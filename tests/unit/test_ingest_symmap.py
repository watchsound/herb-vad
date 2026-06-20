from pathlib import Path

import polars as pl

from herb_vad.ingest.symmap import parse_symmap_herbs

FIXTURE = Path(__file__).parent.parent / "fixtures" / "symmap_mini.tsv"


def test_parse_returns_at_least_twelve_rows():
    df = parse_symmap_herbs(FIXTURE)
    # 3 herbs × (1 QI + ≥1 FLAVOR + ≥1 CHANNEL + 1 TOXICITY) = ≥12 rows
    assert df.height >= 12


def test_parse_explodes_multi_value_channels():
    df = parse_symmap_herbs(FIXTURE)
    ren_shen_channels = df.filter((pl.col("chinese") == "人参") & (pl.col("axis") == "CHANNEL"))
    assert ren_shen_channels.height == 3


def test_parse_explodes_multi_value_flavors():
    df = parse_symmap_herbs(FIXTURE)
    fu_zi_flavors = df.filter((pl.col("chinese") == "附子") & (pl.col("axis") == "FLAVOR"))
    assert fu_zi_flavors.height == 2  # pungent; sweet


def test_parse_normalizes_qi_to_canonical_enum():
    df = parse_symmap_herbs(FIXTURE)
    qi_values = set(df.filter(pl.col("axis") == "QI")["value"].to_list())
    assert qi_values <= {"hot", "warm", "neutral", "cool", "cold"}


def test_parse_normalizes_toxicity():
    df = parse_symmap_herbs(FIXTURE)
    tox_values = set(df.filter(pl.col("axis") == "TOXICITY")["value"].to_list())
    assert tox_values <= {"none", "slight", "moderate", "severe"}


def test_source_is_symmap_for_every_row():
    df = parse_symmap_herbs(FIXTURE)
    assert df["source"].unique().to_list() == ["symmap"]


def test_required_columns_present():
    df = parse_symmap_herbs(FIXTURE)
    required = {"smhb_id", "chinese", "pinyin", "latin", "source", "axis", "value"}
    assert required <= set(df.columns)
