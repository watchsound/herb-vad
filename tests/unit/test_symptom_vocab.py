from herb_vad.ingest.symptom_vocab import SYMPTOM_GROUPS, SYMPTOM_TERMS, all_terms


def test_at_least_eighty_terms():
    assert len(SYMPTOM_TERMS) >= 80


def test_no_duplicates():
    assert len(SYMPTOM_TERMS) == len(set(SYMPTOM_TERMS))


def test_terms_are_chinese():
    # Every term must contain at least one CJK character
    for term in SYMPTOM_TERMS:
        assert any("\u4e00" <= c <= "\u9fff" for c in term), term


def test_expected_groups_present():
    expected = {
        "thermal",
        "energy",
        "digestive",
        "respiratory",
        "head_sensory",
        "musculoskeletal",
        "psychoaffective",
        "urogenital",
        "skin_circulation",
    }
    assert expected <= set(SYMPTOM_GROUPS)


def test_all_terms_returns_flat_dedup_list():
    flat = all_terms()
    assert flat == SYMPTOM_TERMS  # SYMPTOM_TERMS is itself derived from all_terms()
