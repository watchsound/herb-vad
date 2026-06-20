"""Shared zh→en (and ambiguous-en→canonical-en) property vocab.

Used by ETCM, BATMAN-TCM, HERB, and classical-text ingest. The canonical
target values match the enums in ``herb_vad.schemas``.

Note: 涩 (astringent) is folded into ``sour`` because the canonical
5-flavor schema does not carry "astringent" as a separate axis value.
"""

from __future__ import annotations

ZH_QI_MAP: dict[str, str] = {
    "热": "hot",
    "大热": "hot",
    "温": "warm",
    "微温": "warm",
    "平": "neutral",
    "凉": "cool",
    "微凉": "cool",
    "微寒": "cool",
    "寒": "cold",
    "大寒": "cold",
}

ZH_FLAVOR_MAP: dict[str, str] = {
    "酸": "sour",
    "苦": "bitter",
    "甘": "sweet",
    "微甘": "sweet",
    "辛": "pungent",
    "微辛": "pungent",
    "咸": "salty",
    "淡": "bland",
    "涩": "sour",  # 涩 (astringent) folded into sour for the 5-flavor schema
}

ZH_CHANNEL_MAP: dict[str, str] = {
    "肺": "lung",
    "大肠": "large_intestine",
    "胃": "stomach",
    "脾": "spleen",
    "心": "heart",
    "小肠": "small_intestine",
    "膀胱": "bladder",
    "肾": "kidney",
    "心包": "pericardium",
    "三焦": "san_jiao",
    "胆": "gallbladder",
    "肝": "liver",
}

ZH_DIRECTION_MAP: dict[str, str] = {
    "升": "ascend",
    "浮": "float",
    "降": "descend",
    "沉": "sink",
}

ZH_TOX_MAP: dict[str, str] = {
    "无毒": "none",
    "小毒": "slight",
    "有毒": "moderate",
    "大毒": "severe",
}


def split_zh_multi(raw: str | None) -> list[str]:
    """Split a Chinese multi-value cell on common separators.

    Accepts U+3001 (、), U+FF0C (，), ASCII comma/semicolon, and full-width
    semicolon (；). Whitespace stripped; empty tokens dropped.
    """
    if not raw:
        return []
    text = str(raw)
    for sep in ["、", "，", "；", ";", ","]:
        text = text.replace(sep, "|")
    return [t.strip() for t in text.split("|") if t.strip()]
