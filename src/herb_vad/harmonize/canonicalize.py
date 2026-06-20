"""Project per-source long-format property records onto canonical IDs."""

from __future__ import annotations

import polars as pl

from herb_vad.identity.normalize import (
    normalize_chinese,
    normalize_latin,
    normalize_pinyin,
)


def join_to_canonical(long: pl.DataFrame, master: pl.DataFrame) -> pl.DataFrame:
    """Add a ``canonical_id`` column to each long-format property row.

    Rows that do not match any master herb are dropped. The match is
    on (chinese_norm OR pinyin_norm OR latin_norm) — any single normalized
    field is enough, but only one canonical row may match (master is
    already deduplicated by Task 12).
    """
    enriched = long.with_columns(
        pl.col("chinese")
        .map_elements(normalize_chinese, return_dtype=pl.Utf8)
        .alias("chinese_norm"),
        pl.col("pinyin").map_elements(normalize_pinyin, return_dtype=pl.Utf8).alias("pinyin_norm"),
        pl.col("latin").map_elements(normalize_latin, return_dtype=pl.Utf8).alias("latin_norm"),
    )

    by_chinese = master.select(["canonical_id", "chinese_norm"]).filter(
        pl.col("chinese_norm") != ""
    )
    by_pinyin = master.select(["canonical_id", "pinyin_norm"]).filter(pl.col("pinyin_norm") != "")
    by_latin = master.select(["canonical_id", "latin_norm"]).filter(pl.col("latin_norm") != "")

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
