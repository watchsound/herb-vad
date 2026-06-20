from herb_vad.ingest.zh_vocab import (
    ZH_CHANNEL_MAP,
    ZH_DIRECTION_MAP,
    ZH_QI_MAP,
    ZH_TOX_MAP,
    split_zh_multi,
)


def test_qi_covers_five_basic_categories():
    assert set(ZH_QI_MAP.values()) == {"hot", "warm", "neutral", "cool", "cold"}


def test_channel_covers_twelve_meridians():
    assert len(set(ZH_CHANNEL_MAP.values())) == 12


def test_direction_covers_four_directions():
    assert set(ZH_DIRECTION_MAP.values()) == {"ascend", "float", "descend", "sink"}


def test_tox_covers_four_levels():
    assert set(ZH_TOX_MAP.values()) == {"none", "slight", "moderate", "severe"}


def test_split_handles_enumeration_comma():
    assert split_zh_multi("脾、肺、心") == ["脾", "肺", "心"]


def test_split_handles_fullwidth_comma():
    assert split_zh_multi("酸，苦") == ["酸", "苦"]


def test_split_handles_mixed_separators():
    assert split_zh_multi("甘、苦; 辛，咸") == ["甘", "苦", "辛", "咸"]


def test_split_drops_empties_and_strips():
    assert split_zh_multi(" ;; 寒；; ") == ["寒"]


def test_split_handles_none_and_empty():
    assert split_zh_multi(None) == []
    assert split_zh_multi("") == []
