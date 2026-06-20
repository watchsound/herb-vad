from herb_vad.ingest.symptom_vocab import SYMPTOM_GROUPS
from herb_vad.ingest.symptom_vocab_en import (
    SYMPTOM_GROUPS_EN,
    SYMPTOM_TERMS_EN,
    all_terms_en,
)


def test_at_least_hundred_terms_en():
    assert len(SYMPTOM_TERMS_EN) >= 100


def test_no_duplicates():
    assert len(SYMPTOM_TERMS_EN) == len(set(SYMPTOM_TERMS_EN))


def test_terms_are_lowercase():
    for term in SYMPTOM_TERMS_EN:
        assert term == term.lower(), term


def test_keys_align_with_zh_vocab():
    # EN and ZH tables must share top-level keys for cross-lingual probes
    assert set(SYMPTOM_GROUPS_EN) == set(SYMPTOM_GROUPS)


def test_each_group_nontrivial():
    for key, terms in SYMPTOM_GROUPS_EN.items():
        assert len(terms) >= 5, f"group {key} too small: {len(terms)}"


def test_all_terms_function_returns_dedup_flat():
    flat = all_terms_en()
    assert flat == SYMPTOM_TERMS_EN
    assert len(flat) == len(set(flat))


def test_thermal_group_covers_obvious_phrasings():
    # At least one explicit "cold" and one "fever/hot" phrasing each
    assert any(t in SYMPTOM_GROUPS_EN["thermal"] for t in ("cold intolerance", "feels cold"))
    assert any("fever" in t for t in SYMPTOM_GROUPS_EN["thermal"])


def test_no_single_high_collision_word():
    # Single common words like "cold", "warm", "pain", "hot" should not
    # appear bare — they'd match too much. Multi-word phrases preferred.
    forbidden = {"cold", "warm", "hot", "pain", "fever"}
    for term in SYMPTOM_TERMS_EN:
        assert term not in forbidden, f"{term!r} is too generic"
