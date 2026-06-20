from herb_vad.embeddings.property_vocab import (
    ALL_PROPERTY_TOKENS,
    PROPERTY_REGEX,
    ZH_QI_TOKENS,
    build_property_regex,
)


def test_all_tokens_nontrivial():
    assert len(ALL_PROPERTY_TOKENS) >= 60


def test_qi_tokens_cover_five_basics():
    assert {"寒", "凉", "平", "温", "热"} <= set(ZH_QI_TOKENS)


def test_regex_matches_zh_qi_token_inside_sentence():
    sample = "本品性温，味甘，归脾经。"
    assert PROPERTY_REGEX.search(sample) is not None


def test_regex_matches_multichar_token_in_priority_order():
    # "性寒" must be picked before just "寒"
    sample = "性寒"
    matched = PROPERTY_REGEX.findall(sample)
    assert "性寒" in matched


def test_regex_english_token_word_boundary():
    # "warm" must match standalone but NOT inside "warmth"
    assert PROPERTY_REGEX.search("This herb is warm.") is not None
    assert PROPERTY_REGEX.search("warmth") is None


def test_regex_misses_unrelated_text():
    assert PROPERTY_REGEX.search("人参为五加科植物") is None


def test_custom_regex_factory():
    rx = build_property_regex(("special",))
    assert rx.search("a special case") is not None
    assert rx.search("specialty") is None
