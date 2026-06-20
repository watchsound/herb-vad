from pathlib import Path

import polars as pl

from herb_vad.ingest.tcm_mkg import parse_tcm_mkg_herbs

HERBS = Path(__file__).parent.parent / "fixtures" / "tcm_mkg_herbs_mini.tsv"
PROPS = Path(__file__).parent.parent / "fixtures" / "tcm_mkg_props_mini.tsv"


def test_parser_returns_property_records():
    df = parse_tcm_mkg_herbs(HERBS, PROPS)
    # 3 herbs × (1 QI + ≥1 FLAVOR + ≥1 CHANNEL) ≥ 9 rows
    assert df.height >= 12


def test_qi_normalizes_from_therapeutic():
    df = parse_tcm_mkg_herbs(HERBS, PROPS)
    qi_values = set(df.filter(pl.col("axis") == "QI")["value"].to_list())
    assert qi_values == {"warm", "hot", "cold"}


def test_flavor_normalizes_from_medicinal():
    df = parse_tcm_mkg_herbs(HERBS, PROPS)
    flavors = set(df.filter(pl.col("axis") == "FLAVOR")["value"].to_list())
    assert flavors <= {"sour", "bitter", "sweet", "pungent", "salty", "bland"}


def test_channel_normalizes_from_meridian():
    df = parse_tcm_mkg_herbs(HERBS, PROPS)
    ren_shen_channels = sorted(
        df.filter((pl.col("chinese") == "人参") & (pl.col("axis") == "CHANNEL"))["value"].to_list()
    )
    assert ren_shen_channels == ["heart", "lung", "spleen"]


def test_no_toxicity_or_direction():
    df = parse_tcm_mkg_herbs(HERBS, PROPS)
    assert df.filter(pl.col("axis").is_in(["TOXICITY", "DIRECTION"])).height == 0


def test_source_label():
    df = parse_tcm_mkg_herbs(HERBS, PROPS)
    assert df["source"].unique().to_list() == ["tcm_mkg"]
