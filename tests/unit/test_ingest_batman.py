from pathlib import Path

import polars as pl

from herb_vad.ingest.batman import parse_batman_herbs

FIXTURE = Path(__file__).parent.parent / "fixtures" / "batman_mini.tsv"


def test_parse_returns_property_records():
    df = parse_batman_herbs(FIXTURE)
    # 4 herbs × (1 QI + ≥1 FLAVOR + ≥1 CHANNEL) ≥ 12 (no TOX)
    assert df.height >= 12


def test_qi_normalizes_zh_extremes():
    df = parse_batman_herbs(FIXTURE)
    qi = df.filter(pl.col("axis") == "QI")["value"].to_list()
    # 大热 -> hot, 寒 -> cold (twice), 温 -> warm
    assert qi.count("hot") >= 1
    assert qi.count("cold") >= 2
    assert qi.count("warm") >= 1


def test_huang_lian_has_six_channels():
    df = parse_batman_herbs(FIXTURE)
    channels = df.filter((pl.col("chinese") == "黄连") & (pl.col("axis") == "CHANNEL"))[
        "value"
    ].to_list()
    assert sorted(channels) == sorted(
        ["heart", "spleen", "stomach", "liver", "gallbladder", "large_intestine"]
    )


def test_da_huang_has_pericardium_channel():
    # 心包 → pericardium — verify that specific zh→en mapping is exercised
    df = parse_batman_herbs(FIXTURE)
    channels = df.filter((pl.col("chinese") == "大黄") & (pl.col("axis") == "CHANNEL"))[
        "value"
    ].to_list()
    assert "pericardium" in channels


def test_no_toxicity_rows_emitted():
    df = parse_batman_herbs(FIXTURE)
    assert df.filter(pl.col("axis") == "TOXICITY").height == 0


def test_source_is_batman():
    df = parse_batman_herbs(FIXTURE)
    assert df["source"].unique().to_list() == ["batman"]
