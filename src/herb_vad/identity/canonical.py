"""Canonical herb identity resolver.

Consumes the per-source (chinese, pinyin, latin) tables and emits a
master frame with stable ``H#####`` ids. Identity rule: collapse on
(chinese_norm, pinyin_norm, latin_norm) where missing fields are
treated as wildcards — two rows merge if every co-present normalized
field matches and at least one normalized field is non-empty.
"""

from __future__ import annotations

import polars as pl

from herb_vad.identity.normalize import (
    normalize_chinese,
    normalize_latin,
    normalize_pinyin,
)


def _normalize_frame(name: str, df: pl.DataFrame) -> pl.DataFrame:
    return df.with_columns(
        pl.col("chinese")
        .map_elements(normalize_chinese, return_dtype=pl.Utf8)
        .alias("chinese_norm"),
        pl.col("pinyin").map_elements(normalize_pinyin, return_dtype=pl.Utf8).alias("pinyin_norm"),
        pl.col("latin").map_elements(normalize_latin, return_dtype=pl.Utf8).alias("latin_norm"),
        pl.lit(name).alias("source"),
    )


def _merge_clusters(rows: list[dict]) -> list[dict]:
    """Greedy merge: two rows belong to the same cluster if every
    non-empty normalized field they share matches and at least one of
    the (chinese, pinyin, latin) triplets has a non-empty common value.

    O(n²) — fine for the ~5k–10k unique herbs across the 5 sources.
    """
    clusters: list[dict] = []
    for row in rows:
        for cluster in clusters:
            if _can_merge(cluster, row):
                _absorb(cluster, row)
                break
        else:
            clusters.append(
                {
                    "chinese_norm": {row["chinese_norm"]} if row["chinese_norm"] else set(),
                    "pinyin_norm": {row["pinyin_norm"]} if row["pinyin_norm"] else set(),
                    "latin_norm": {row["latin_norm"]} if row["latin_norm"] else set(),
                    "sources": {row["source"]},
                }
            )
    return clusters


_STRICT_AXES = ("chinese_norm", "pinyin_norm")


def _can_merge(cluster: dict, row: dict) -> bool:
    """Greedy cluster merge with a strict/loose axis split.

    Strict axes (chinese_norm, pinyin_norm): a non-empty value on both
    sides MUST match. Mismatches reject the merge.

    Loose axes (latin_norm): mismatches are tolerated because Latin
    binomials in TCM sources are notoriously noisy (pharmacognosy
    prefixes "Radix"/"Folium"/"Fructus", citations with brackets,
    multi-form comma lists). A Latin match counts as positive overlap
    but a Latin mismatch alone never blocks a merge that pinyin or
    chinese already supports.

    A merge succeeds iff (a) no strict-axis mismatch AND (b) at least
    one axis (strict or loose) has a non-empty shared value.
    """
    overlap = False
    for axis in _STRICT_AXES:
        if row[axis] and cluster[axis]:
            if row[axis] in cluster[axis]:
                overlap = True
            else:
                return False
    if row["latin_norm"] and cluster["latin_norm"]:
        if row["latin_norm"] in cluster["latin_norm"]:
            overlap = True
    return overlap


def _absorb(cluster: dict, row: dict) -> None:
    for axis in ("chinese_norm", "pinyin_norm", "latin_norm"):
        if row[axis]:
            cluster[axis].add(row[axis])
    cluster["sources"].add(row["source"])


def build_canonical_table(sources: dict[str, pl.DataFrame]) -> pl.DataFrame:
    frames: list[pl.DataFrame] = []
    for name, df in sources.items():
        frames.append(_normalize_frame(name, df.select(["chinese", "pinyin", "latin"])))
    long = pl.concat(frames, how="vertical")

    rows = long.select(["chinese_norm", "pinyin_norm", "latin_norm", "source"]).to_dicts()
    # Drop fully-empty rows
    rows = [r for r in rows if r["chinese_norm"] or r["pinyin_norm"] or r["latin_norm"]]

    clusters = _merge_clusters(rows)
    out_rows: list[dict] = []
    for i, cluster in enumerate(clusters, start=1):
        out_rows.append(
            {
                "canonical_id": f"H{i:05d}",
                "chinese_norm": next(iter(cluster["chinese_norm"]), ""),
                "pinyin_norm": next(iter(cluster["pinyin_norm"]), ""),
                "latin_norm": next(iter(cluster["latin_norm"]), ""),
                "sources": sorted(cluster["sources"]),
            }
        )
    return pl.DataFrame(out_rows)
