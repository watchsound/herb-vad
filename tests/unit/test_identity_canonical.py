import polars as pl

from herb_vad.identity.canonical import build_canonical_table


def _make_source(name: str, rows: list[dict]) -> pl.DataFrame:
    base = pl.DataFrame(rows)
    return base.with_columns(pl.lit(name).alias("source"))


def test_same_herb_across_two_sources_resolves_to_one_canonical_id():
    sources = {
        "symmap": _make_source(
            "symmap",
            [{"chinese": "人参", "pinyin": "Ren Shen", "latin": "Panax ginseng"}],
        ),
        "tcmsp": _make_source(
            "tcmsp",
            [{"chinese": "人参", "pinyin": "renshen", "latin": "Panax ginseng C.A.Meyer"}],
        ),
    }
    master = build_canonical_table(sources)
    rensheng = master.filter(pl.col("chinese_norm") == "人参")
    assert rensheng.height == 1


def test_canonical_ids_are_five_digit_h_prefixed():
    sources = {
        "symmap": _make_source(
            "symmap",
            [{"chinese": "人参", "pinyin": "Ren Shen", "latin": "Panax ginseng"}],
        ),
    }
    master = build_canonical_table(sources)
    assert master.height == 1
    cid = master["canonical_id"][0]
    assert cid.startswith("H")
    assert len(cid) == 6
    assert cid[1:].isdigit()


def test_different_chinese_names_get_different_canonical_ids():
    sources = {
        "symmap": _make_source(
            "symmap",
            [
                {"chinese": "人参", "pinyin": "renshen", "latin": "Panax ginseng"},
                {"chinese": "石膏", "pinyin": "shigao", "latin": "Gypsum Fibrosum"},
            ],
        ),
    }
    master = build_canonical_table(sources)
    assert master["canonical_id"].n_unique() == 2


def test_pinyin_only_match_collapses_when_chinese_missing():
    # If one source omits chinese but pinyin + latin match, they should still merge.
    sources = {
        "symmap": _make_source(
            "symmap",
            [{"chinese": "人参", "pinyin": "Ren Shen", "latin": "Panax ginseng"}],
        ),
        "pubmed": _make_source(
            "pubmed",
            [{"chinese": None, "pinyin": "renshen", "latin": "Panax ginseng"}],
        ),
    }
    master = build_canonical_table(sources)
    panax = master.filter(pl.col("latin_norm") == "panax ginseng")
    assert panax.height == 1


def test_master_contains_source_provenance_list():
    sources = {
        "symmap": _make_source(
            "symmap",
            [{"chinese": "人参", "pinyin": "renshen", "latin": "Panax ginseng"}],
        ),
        "tcmsp": _make_source(
            "tcmsp",
            [{"chinese": "人参", "pinyin": "renshen", "latin": "Panax ginseng"}],
        ),
    }
    master = build_canonical_table(sources)
    sources_for_renshen = set(master["sources"][0])
    assert sources_for_renshen == {"symmap", "tcmsp"}


def test_normalized_keys_present_in_output():
    sources = {
        "symmap": _make_source(
            "symmap",
            [{"chinese": "人参", "pinyin": "Ren Shen", "latin": "Panax ginseng"}],
        ),
    }
    master = build_canonical_table(sources)
    expected = {"canonical_id", "chinese_norm", "pinyin_norm", "latin_norm", "sources"}
    assert expected <= set(master.columns)
