from pathlib import Path

import polars as pl

from herb_vad.ingest.cvaw import parse_cvaw

FIXTURE = Path(__file__).parent.parent / "fixtures" / "cvaw_mini.csv"


def test_columns_present():
    df = parse_cvaw(FIXTURE)
    assert {
        "term",
        "valence",
        "arousal",
        "dominance",
        "valence_likert",
        "arousal_likert",
    } <= set(df.columns)


def test_likert_preserved():
    df = parse_cvaw(FIXTURE)
    kuai_le = df.filter(pl.col("term") == "快樂")
    assert kuai_le["valence_likert"][0] == 8.5
    assert kuai_le["arousal_likert"][0] == 7.2


def test_normalization_to_signed_unit_interval():
    df = parse_cvaw(FIXTURE)
    # 8.5 -> (8.5 - 5)/4 = 0.875
    kuai_le_v = df.filter(pl.col("term") == "快樂")["valence"][0]
    assert abs(kuai_le_v - 0.875) < 1e-9
    # 1.5 -> (1.5 - 5)/4 = -0.875
    fennu_v = df.filter(pl.col("term") == "憤怒")["valence"][0]
    assert abs(fennu_v - (-0.875)) < 1e-9


def test_neutral_maps_to_zero():
    # Score of 5.0 should map exactly to 0.0
    from herb_vad.ingest.cvaw import normalize_likert_to_signed

    assert normalize_likert_to_signed(5.0) == 0.0


def test_dominance_is_null():
    df = parse_cvaw(FIXTURE)
    assert df["dominance"].null_count() == df.height


def test_normalized_in_signed_range():
    df = parse_cvaw(FIXTURE)
    for col in ("valence", "arousal"):
        assert df[col].min() >= -1.0
        assert df[col].max() <= 1.0


def test_case_insensitive_column_lookup():
    # Build a tiny in-memory fixture with lowercase headers
    import io

    csv = io.StringIO("No.,Word,valence_mean,arousal_mean\n1,快樂,8.5,7.2\n")
    df = pl.read_csv(csv)
    tmp = Path("tests/fixtures/_cvaw_lowercase.csv")
    tmp.parent.mkdir(parents=True, exist_ok=True)
    df.write_csv(tmp)
    try:
        out = parse_cvaw(tmp)
        assert out.height == 1
        assert abs(out["valence_likert"][0] - 8.5) < 1e-9
    finally:
        tmp.unlink(missing_ok=True)
