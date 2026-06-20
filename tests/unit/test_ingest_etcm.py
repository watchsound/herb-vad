from pathlib import Path

import polars as pl

from herb_vad.ingest.etcm import parse_etcm_herbs

FIXTURE = Path(__file__).parent.parent / "fixtures" / "etcm_mini.tsv"


def test_parse_returns_property_records():
    df = parse_etcm_herbs(FIXTURE)
    # 4 herbs × (1 QI + ≥1 FLAVOR + ≥1 CHANNEL + 1 TOX) ≥ 16
    assert df.height >= 16


def test_zh_property_normalizes_to_english_canonical():
    df = parse_etcm_herbs(FIXTURE)
    qi_values = set(df.filter(pl.col("axis") == "QI")["value"].to_list())
    assert qi_values <= {"hot", "warm", "neutral", "cool", "cold"}
    # 大热 should map to hot, 大寒 to cold, 凉 to cool, 温 to warm
    assert "hot" in qi_values
    assert "cold" in qi_values
    assert "cool" in qi_values
    assert "warm" in qi_values


def test_zh_channel_normalizes_to_english_canonical():
    df = parse_etcm_herbs(FIXTURE)
    channels = set(df.filter(pl.col("axis") == "CHANNEL")["value"].to_list())
    assert channels <= {
        "lung",
        "large_intestine",
        "stomach",
        "spleen",
        "heart",
        "small_intestine",
        "bladder",
        "kidney",
        "pericardium",
        "san_jiao",
        "gallbladder",
        "liver",
    }


def test_ren_shen_has_three_channels():
    df = parse_etcm_herbs(FIXTURE)
    ren_shen_channels = df.filter((pl.col("chinese") == "人参") & (pl.col("axis") == "CHANNEL"))
    assert ren_shen_channels.height == 3


def test_zh_toxicity_mapped():
    df = parse_etcm_herbs(FIXTURE)
    tox_for_fuzi = df.filter((pl.col("chinese") == "附子") & (pl.col("axis") == "TOXICITY"))[
        "value"
    ].to_list()
    assert tox_for_fuzi == ["severe"]


def test_source_is_etcm():
    df = parse_etcm_herbs(FIXTURE)
    assert df["source"].unique().to_list() == ["etcm"]
