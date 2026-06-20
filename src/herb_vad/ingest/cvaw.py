"""Parser for CVAW (Chinese Valence-Arousal Words, Yu et al.,
Yuan Ze University; http://nlp.innobic.yzu.edu.tw/resources/cvaw.html).

CVAW reports each word's valence and arousal as Likert means on a
1-9 scale. To interoperate with NRC-VAD v2.1's signed [-1, +1] range
this parser also emits a normalized projection
``signed = (likert - 5.0) / 4.0`` so 5.0 (neutral) maps to 0.0.

CVAW has no Dominance axis; the output's ``dominance`` column is null
so the schema matches ``herb_vad.ingest.nrc_vad`` for trivial concat.
"""

from __future__ import annotations

from pathlib import Path

import polars as pl


def normalize_likert_to_signed(
    score: float, *, midpoint: float = 5.0, half_range: float = 4.0
) -> float:
    """Project a 1-9 Likert score onto [-1, +1] with midpoint at 0."""
    return (score - midpoint) / half_range


def _find_column(df: pl.DataFrame, *candidates: str) -> str:
    by_lower = {c.lower(): c for c in df.columns}
    for cand in candidates:
        actual = by_lower.get(cand.lower())
        if actual is not None:
            return actual
    raise ValueError(f"Required column missing; tried {candidates}; have {df.columns}")


def parse_cvaw(path: Path) -> pl.DataFrame:
    raw = pl.read_csv(path)

    word_col = _find_column(raw, "Word", "word", "term")
    v_col = _find_column(raw, "Valence_Mean", "valence_mean")
    a_col = _find_column(raw, "Arousal_Mean", "arousal_mean")

    df = raw.rename({word_col: "term", v_col: "valence_likert", a_col: "arousal_likert"})
    df = df.with_columns(
        ((pl.col("valence_likert") - 5.0) / 4.0).alias("valence"),
        ((pl.col("arousal_likert") - 5.0) / 4.0).alias("arousal"),
        pl.lit(None, dtype=pl.Float64).alias("dominance"),
    )
    return df.select(
        "term",
        "valence",
        "arousal",
        "dominance",
        "valence_likert",
        "arousal_likert",
    )
