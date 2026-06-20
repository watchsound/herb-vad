from herb_vad.identity.normalize import (
    normalize_chinese,
    normalize_latin,
    normalize_pinyin,
)


# --- pinyin -------------------------------------------------------------


def test_pinyin_strips_tone_marks_and_spaces():
    assert normalize_pinyin("Rén Shēn") == "renshen"
    assert normalize_pinyin("Ren Shen") == "renshen"
    assert normalize_pinyin("rénshēn") == "renshen"


def test_pinyin_strips_hyphen_and_punctuation():
    assert normalize_pinyin("ren-shen") == "renshen"
    assert normalize_pinyin("Ren'Shen") == "renshen"


def test_pinyin_handles_empty_and_none():
    assert normalize_pinyin("") == ""
    assert normalize_pinyin(None) == ""


def test_pinyin_handles_umlaut_u():
    assert normalize_pinyin("nǚzhēnzǐ") == "nuzhenzi"


# --- chinese ------------------------------------------------------------


def test_chinese_strips_whitespace_and_punctuation():
    assert normalize_chinese(" 人 参 ") == "人参"
    assert normalize_chinese("人-参") == "人参"


def test_chinese_traditional_to_simplified_optional():
    # Parser should at least pass simplified through unchanged; if the
    # implementation does t→s conversion, both forms collapse.
    assert normalize_chinese("人参") == "人参"


def test_chinese_empty_and_none():
    assert normalize_chinese("") == ""
    assert normalize_chinese(None) == ""


# --- latin --------------------------------------------------------------


def test_latin_drops_authority_and_lowercases():
    assert normalize_latin("Panax ginseng C. A. Meyer") == "panax ginseng"
    assert normalize_latin("Aconitum carmichaelii Debx.") == "aconitum carmichaelii"


def test_latin_collapses_internal_whitespace():
    assert normalize_latin("  Panax   ginseng  ") == "panax ginseng"


def test_latin_handles_empty_and_none():
    assert normalize_latin("") == ""
    assert normalize_latin(None) == ""
