from pathlib import Path

import polars as pl

from herb_vad.ingest.tcmid import parse_tcmid_herbs

FIXTURE = Path(__file__).parent.parent / "fixtures" / "tcmid_mini.csv"


def test_parse_returns_records():
    df = parse_tcmid_herbs(FIXTURE)
    # 4 herbs × (≥1 QI + ≥1 FLAVOR + ≥1 CHANNEL) ≥ 12
    assert df.height >= 12


def test_extreme_temperatures_normalize():
    df = parse_tcmid_herbs(FIXTURE)
    qi = df.filter(pl.col("axis") == "QI")["value"].to_list()
    # "Extremely cold" → cold, "Extreme Hot" → hot, "slightly warm" → warm, "Mild" → neutral
    assert "cold" in qi
    assert "hot" in qi
    assert "warm" in qi
    assert "neutral" in qi


def test_attributes_split_qi_and_flavor():
    df = parse_tcmid_herbs(FIXTURE)
    fu_zi = df.filter(pl.col("pinyin") == "FU ZI")
    qi = fu_zi.filter(pl.col("axis") == "QI")["value"].to_list()
    flavors = sorted(fu_zi.filter(pl.col("axis") == "FLAVOR")["value"].to_list())
    assert qi == ["hot"]
    assert flavors == ["pungent", "sweet"]


def test_meridians_split():
    df = parse_tcmid_herbs(FIXTURE)
    gan_cao = df.filter(pl.col("pinyin") == "GAN CAO")
    channels = sorted(gan_cao.filter(pl.col("axis") == "CHANNEL")["value"].to_list())
    assert channels == ["heart", "lung", "spleen", "stomach"]


def test_source_is_tcmid():
    df = parse_tcmid_herbs(FIXTURE)
    assert df["source"].unique().to_list() == ["tcmid"]


def test_no_toxicity_rows():
    df = parse_tcmid_herbs(FIXTURE)
    assert df.filter(pl.col("axis") == "TOXICITY").height == 0


def test_english_name_preserved():
    df = parse_tcmid_herbs(FIXTURE)
    assert "english" in df.columns
