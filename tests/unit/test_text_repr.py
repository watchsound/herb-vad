import polars as pl

from herb_vad.embeddings.text_repr import (
    MASK_TOKEN,
    build_all,
    build_for_herb,
    mask_property_keywords,
)


def _corpus() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "source": ["ctext", "ctext", "pubmed", "pubmed"],
            "text": [
                "人參，味甘微寒。主補五藏，安精神。",  # classical, no symptom term
                "人參主治怕冷、乏力、心悸。",  # classical + symptom
                "Ren Shen is used in patients with 怕冷 and 乏力.",  # pubmed + symptom
                "石膏 cools 烦热 in febrile illness.",  # unrelated to ren shen
            ],
        }
    )


def _master() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "canonical_id": ["H00001"],
            "chinese_norm": ["人參"],
            "pinyin_norm": ["renshen"],
            "latin_norm": ["panax ginseng"],
        }
    )


def test_definition_pulls_classical_passages_only():
    out = build_for_herb(
        canonical_id="H00001",
        chinese="人參",
        pinyin="renshen",
        latin="panax ginseng",
        corpus=_corpus(),
    )
    # Both ctext rows mention 人參; pubmed row also does but should not be in definition
    assert "人參，味甘微寒" in out.definition
    assert "人參主治" in out.definition
    assert "Ren Shen is used" not in out.definition


def test_indication_requires_symptom_term():
    out = build_for_herb(
        canonical_id="H00001",
        chinese="人參",
        pinyin="renshen",
        latin="panax ginseng",
        corpus=_corpus(),
    )
    # First ctext row has no symptom term → excluded
    assert "人參，味甘微寒" not in out.indication
    # Second ctext row has 怕冷, 乏力, 心悸 → included
    assert "人參主治怕冷" in out.indication
    # PubMed row has 怕冷, 乏力 → included
    assert "Ren Shen is used in patients" in out.indication


def test_indication_masked_hides_property_keywords():
    out = build_for_herb(
        canonical_id="H00001",
        chinese="人參",
        pinyin="renshen",
        latin="panax ginseng",
        corpus=_corpus(),
    )
    # 怕冷 IS a symptom term; the masker must NOT remove it.
    # 寒/温 etc. ARE property tokens; if present they'd be masked.
    assert "怕冷" in out.indication_masked  # symptom term preserved
    # Plant the assertion via a synthetic line that contains a property token
    syn = "性温 味甘 人參主治怕冷"
    assert mask_property_keywords(syn) == f"{MASK_TOKEN} {MASK_TOKEN} 人參主治怕冷"


def test_concat_is_definition_plus_indication():
    out = build_for_herb(
        canonical_id="H00001",
        chinese="人參",
        pinyin="renshen",
        latin="panax ginseng",
        corpus=_corpus(),
    )
    assert out.concat.startswith(out.definition)
    assert out.indication in out.concat


def test_build_all_returns_one_row_per_master_herb():
    out = build_all(_master(), _corpus())
    assert out.height == 1
    assert set(out.columns) == {
        "canonical_id",
        "definition",
        "indication",
        "concat",
        "indication_masked",
    }


def test_fallback_definition_when_no_classical_hit():
    empty_corpus = pl.DataFrame(
        {"source": [], "text": []}, schema={"source": pl.Utf8, "text": pl.Utf8}
    )
    out = build_for_herb(
        canonical_id="H99999",
        chinese="xxx",
        pinyin="xxx",
        latin="xxx",
        corpus=empty_corpus,
    )
    assert out.definition == "xxx xxx xxx"
