import polars as pl

from herb_vad.harmonize.canonicalize import join_to_canonical


def _master() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "canonical_id": ["H00001", "H00002"],
            "chinese_norm": ["人参", "石膏"],
            "pinyin_norm": ["renshen", "shigao"],
            "latin_norm": ["panax ginseng", "gypsum fibrosum"],
            "sources": [["symmap", "tcmsp"], ["symmap"]],
        }
    )


def _long_one_source() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "chinese": ["人参", "石膏"],
            "pinyin": ["Ren Shen", "shigao"],
            "latin": ["Panax ginseng", "Gypsum Fibrosum"],
            "source": ["symmap", "symmap"],
            "axis": ["QI", "QI"],
            "value": ["warm", "cold"],
        }
    )


def test_join_assigns_canonical_ids():
    out = join_to_canonical(_long_one_source(), _master())
    assert out.height == 2
    assert set(out["canonical_id"].to_list()) == {"H00001", "H00002"}


def test_join_preserves_source_axis_value():
    out = join_to_canonical(_long_one_source(), _master())
    h00001 = out.filter(pl.col("canonical_id") == "H00001").row(0, named=True)
    assert h00001["source"] == "symmap"
    assert h00001["axis"] == "QI"
    assert h00001["value"] == "warm"


def test_unmapped_herbs_are_dropped_not_silently_kept():
    long = pl.DataFrame(
        {
            "chinese": ["黑芝麻"],  # not in master
            "pinyin": ["heizhima"],
            "latin": ["Sesamum indicum"],
            "source": ["symmap"],
            "axis": ["FLAVOR"],
            "value": ["sweet"],
        }
    )
    out = join_to_canonical(long, _master())
    assert out.height == 0


def test_normalization_applied_before_join():
    # Tone marks + capitalization differences must NOT block the join.
    long = pl.DataFrame(
        {
            "chinese": ["人参"],
            "pinyin": ["Rén Shēn"],  # tones
            "latin": ["Panax ginseng C. A. Meyer"],  # authority
            "source": ["tcmsp"],
            "axis": ["FLAVOR"],
            "value": ["sweet"],
        }
    )
    out = join_to_canonical(long, _master())
    assert out["canonical_id"].to_list() == ["H00001"]


def test_only_long_format_columns_in_output():
    out = join_to_canonical(_long_one_source(), _master())
    expected = {"canonical_id", "source", "axis", "value"}
    assert expected <= set(out.columns)
