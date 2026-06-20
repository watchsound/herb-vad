from pathlib import Path

import polars as pl

from herb_vad.ingest.nrc_vad import parse_nrc_vad

FIXTURE = Path(__file__).parent.parent / "fixtures" / "nrc_vad_mini.tsv"


def test_returns_expected_columns():
    df = parse_nrc_vad(FIXTURE)
    assert set(df.columns) == {"term", "valence", "arousal", "dominance"}


def test_row_count_matches_fixture():
    df = parse_nrc_vad(FIXTURE)
    assert df.height == 5


def test_scores_in_signed_range():
    df = parse_nrc_vad(FIXTURE)
    for col in ("valence", "arousal", "dominance"):
        assert df[col].min() >= -1.0
        assert df[col].max() <= 1.0


def test_negative_valence_preserved():
    df = parse_nrc_vad(FIXTURE)
    sad_v = df.filter(pl.col("term") == "sad")["valence"][0]
    assert sad_v < 0  # v2.1 uses signed scores; "sad" must stay negative


def test_term_is_unique_index():
    df = parse_nrc_vad(FIXTURE)
    assert df["term"].n_unique() == df.height


def test_dtype_is_float():
    df = parse_nrc_vad(FIXTURE)
    for col in ("valence", "arousal", "dominance"):
        assert df.schema[col] in (pl.Float64, pl.Float32)
