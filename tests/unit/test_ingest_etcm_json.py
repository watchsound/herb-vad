from pathlib import Path

import polars as pl

from herb_vad.ingest.etcm import parse_etcm_json_responses

FIXTURE_DIR = Path(__file__).parent.parent / "fixtures" / "etcm_json"


def test_parse_returns_qi_flavor_channel():
    df = parse_etcm_json_responses(FIXTURE_DIR)
    # 2 herbs × (1 QI + ≥1 FLAVOR + ≥1 CHANNEL) ≥ 9
    assert df.height >= 9


def test_great_hot_normalizes_to_hot():
    df = parse_etcm_json_responses(FIXTURE_DIR)
    fuzi_qi = df.filter((pl.col("pinyin") == "FuZi") & (pl.col("axis") == "QI"))["value"].to_list()
    assert fuzi_qi == ["hot"]


def test_mildly_warm_normalizes_to_warm():
    df = parse_etcm_json_responses(FIXTURE_DIR)
    renshen_qi = df.filter((pl.col("pinyin") == "RenShen") & (pl.col("axis") == "QI"))[
        "value"
    ].to_list()
    assert renshen_qi == ["warm"]


def test_mildly_bitter_normalizes_to_bitter():
    df = parse_etcm_json_responses(FIXTURE_DIR)
    flavors = sorted(
        df.filter((pl.col("pinyin") == "RenShen") & (pl.col("axis") == "FLAVOR"))["value"].to_list()
    )
    assert flavors == ["bitter", "sweet"]


def test_meridian_suffix_stripped():
    df = parse_etcm_json_responses(FIXTURE_DIR)
    channels = sorted(
        df.filter((pl.col("pinyin") == "RenShen") & (pl.col("axis") == "CHANNEL"))[
            "value"
        ].to_list()
    )
    assert channels == ["heart", "kidney", "lung", "spleen"]


def test_html_tags_stripped_from_latin():
    df = parse_etcm_json_responses(FIXTURE_DIR)
    latins = df["latin"].unique().to_list()
    assert all("<" not in str(latin) for latin in latins)


def test_source_is_etcm():
    df = parse_etcm_json_responses(FIXTURE_DIR)
    assert df["source"].unique().to_list() == ["etcm"]
