from pathlib import Path

import polars as pl

from herb_vad.ingest.herb_db import parse_herb_db

FIXTURE = Path(__file__).parent.parent / "fixtures" / "herb_db_mini.tsv"


def test_parse_emits_records():
    df = parse_herb_db(FIXTURE)
    # 5 herbs × (1 QI + ≥1 FLAVOR + ≥1 CHANNEL + 1 TOX) ≥ 20
    assert df.height >= 20


def test_toxicity_four_levels_covered():
    df = parse_herb_db(FIXTURE)
    tox_values = set(df.filter(pl.col("axis") == "TOXICITY")["value"].to_list())
    # Fixture contains 无毒 / 有毒 / 小毒 → none / moderate / slight
    assert tox_values <= {"none", "slight", "moderate", "severe"}
    assert {"none", "moderate", "slight"} <= tox_values


def test_microtemp_qi_normalizes_to_warm():
    # 微温 should canonicalize to "warm" (杏仁 in the fixture)
    df = parse_herb_db(FIXTURE)
    xingren_qi = df.filter((pl.col("chinese") == "杏仁") & (pl.col("axis") == "QI"))[
        "value"
    ].to_list()
    assert xingren_qi == ["warm"]


def test_multi_flavor_split_zh():
    df = parse_herb_db(FIXTURE)
    cangerzi_flavors = sorted(
        df.filter((pl.col("chinese") == "苍耳子") & (pl.col("axis") == "FLAVOR"))["value"].to_list()
    )
    assert cangerzi_flavors == ["bitter", "pungent"]


def test_channel_singleton_works():
    # 苍耳子 has only one channel (肺 → lung)
    df = parse_herb_db(FIXTURE)
    cangerzi_channels = df.filter((pl.col("chinese") == "苍耳子") & (pl.col("axis") == "CHANNEL"))[
        "value"
    ].to_list()
    assert cangerzi_channels == ["lung"]


def test_english_name_preserved():
    df = parse_herb_db(FIXTURE)
    # Verify that the parser carries english name through (used downstream for
    # cross-database identity matching against Latin names)
    assert "english" in df.columns or "herb_en_name" in df.columns


def test_source_is_herb_db():
    df = parse_herb_db(FIXTURE)
    assert df["source"].unique().to_list() == ["herb_db"]
