"""Project per-source long-format property records onto canonical IDs."""

from __future__ import annotations

import polars as pl

from herb_vad.identity.normalize import (
    normalize_chinese,
    normalize_latin,
    normalize_pinyin,
)


def _unique_key_table(master: pl.DataFrame, key: str) -> pl.DataFrame:
    """Build a join table that maps a normalized key to a canonical_id.

    Only keeps key values that appear in EXACTLY ONE master row — keys
    that collide across multiple canonical_ids (e.g. ``latin_norm
    = "radix"`` after over-aggressive authority stripping) would
    otherwise multiply property rows by the collision count when used
    as a join key.
    """
    counts = master.group_by(key).agg(pl.len().alias("_n"))
    unique_keys = counts.filter((pl.col("_n") == 1) & (pl.col(key) != "")).drop("_n")
    return master.join(unique_keys, on=key, how="inner").select(["canonical_id", key])


def join_to_canonical(long: pl.DataFrame, master: pl.DataFrame) -> pl.DataFrame:
    """Add a ``canonical_id`` column to each long-format property row.

    Rows that do not match any master herb are dropped. The match is
    on (chinese_norm OR pinyin_norm OR latin_norm) — any single
    UNIQUE-IN-MASTER normalized field is enough. Keys that collide
    across multiple master rows (e.g. ``"radix"`` from over-stripped
    Latin authorities) are excluded from join consideration to prevent
    Cartesian fanout; the source row will fall back to whichever of the
    other two keys is unique.
    """
    enriched = long.with_columns(
        pl.col("chinese")
        .map_elements(normalize_chinese, return_dtype=pl.Utf8)
        .alias("chinese_norm"),
        pl.col("pinyin").map_elements(normalize_pinyin, return_dtype=pl.Utf8).alias("pinyin_norm"),
        pl.col("latin").map_elements(normalize_latin, return_dtype=pl.Utf8).alias("latin_norm"),
    )

    by_chinese = _unique_key_table(master, "chinese_norm")
    by_pinyin = _unique_key_table(master, "pinyin_norm")
    by_latin = _unique_key_table(master, "latin_norm")

    joined = enriched
    for keys, table in (
        ("chinese_norm", by_chinese),
        ("pinyin_norm", by_pinyin),
        ("latin_norm", by_latin),
    ):
        joined = joined.join(table.rename({"canonical_id": f"cid_{keys}"}), on=keys, how="left")

    # Coalesce the three candidate canonical_ids; first non-null wins.
    joined = joined.with_columns(
        pl.coalesce(["cid_chinese_norm", "cid_pinyin_norm", "cid_latin_norm"]).alias("canonical_id")
    )
    joined = joined.filter(pl.col("canonical_id").is_not_null())

    return joined.select(["canonical_id", "source", "axis", "value"])
