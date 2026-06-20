"""Parser for the NRC-VAD Lexicon (Mohammad 2018 v1 / 2025 v2.1).

v2.1 uses signed [-1, +1] scores for valence / arousal / dominance; v1
used [0, 1]. This parser preserves whatever the source file uses (no
rescaling). Downstream code is expected to inspect the score range when
combining with other lexicons (e.g. CVAW).
"""

from __future__ import annotations

from pathlib import Path

import polars as pl

EXPECTED_COLUMNS = ("term", "valence", "arousal", "dominance")


def parse_nrc_vad(path: Path) -> pl.DataFrame:
    df = pl.read_csv(path, separator="\t")
    missing = set(EXPECTED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(
            f"NRC-VAD file {path} missing columns: {sorted(missing)}. " f"Found: {df.columns}"
        )
    return df.select(list(EXPECTED_COLUMNS)).with_columns(
        pl.col("valence").cast(pl.Float64),
        pl.col("arousal").cast(pl.Float64),
        pl.col("dominance").cast(pl.Float64),
    )
