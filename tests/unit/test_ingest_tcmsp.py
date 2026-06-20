from pathlib import Path

import polars as pl

from herb_vad.ingest.tcmsp import parse_tcmsp_herbs

FIXTURE = Path(__file__).parent.parent / "fixtures" / "tcmsp_mini.csv"


def test_parse_returns_at_least_sixteen_rows():
    df = parse_tcmsp_herbs(FIXTURE)
    # 4 herbs x (1 QI + >=1 FLAVOR + >=1 CHANNEL) >= 16 (toxicity absent here)
    assert df.height >= 16


def test_parse_handles_quoted_multi_value_channel():
    df = parse_tcmsp_herbs(FIXTURE)
    gan_cao_channels = df.filter((pl.col("chinese") == "甘草") & (pl.col("axis") == "CHANNEL"))
    assert gan_cao_channels.height == 4


def test_parse_handles_quoted_multi_value_flavor():
    df = parse_tcmsp_herbs(FIXTURE)
    fu_zi_flavors = df.filter((pl.col("chinese") == "附子") & (pl.col("axis") == "FLAVOR"))
    assert fu_zi_flavors.height == 2


def test_single_value_flavor_still_works():
    df = parse_tcmsp_herbs(FIXTURE)
    gan_cao_flavors = df.filter((pl.col("chinese") == "甘草") & (pl.col("axis") == "FLAVOR"))
    assert gan_cao_flavors.height == 1
    assert gan_cao_flavors["value"][0] == "sweet"


def test_qi_values_in_canonical_set():
    df = parse_tcmsp_herbs(FIXTURE)
    qi_values = set(df.filter(pl.col("axis") == "QI")["value"].to_list())
    assert qi_values <= {"hot", "warm", "neutral", "cool", "cold"}


def test_source_is_tcmsp():
    df = parse_tcmsp_herbs(FIXTURE)
    assert df["source"].unique().to_list() == ["tcmsp"]
