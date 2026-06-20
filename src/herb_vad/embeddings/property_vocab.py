"""Property-keyword vocabulary that MUST be masked in indication_masked.

Defines the regex used by ``text_repr.mask_property_keywords``. Any
token here would leak the answer for Task 20's held-out probe, so we
err on the side of over-masking (e.g. we mask both 寒 and 性寒).

The list combines zh single-character property markers, common multi-
character forms, and the canonical English forms used in the schemas.
"""

from __future__ import annotations

import re

ZH_QI_TOKENS: tuple[str, ...] = (
    "寒",
    "凉",
    "微寒",
    "微凉",
    "平",
    "温",
    "微温",
    "热",
    "大寒",
    "大热",
    "性寒",
    "性凉",
    "性平",
    "性温",
    "性热",
)
ZH_FLAVOR_TOKENS: tuple[str, ...] = (
    "酸",
    "苦",
    "甘",
    "辛",
    "咸",
    "淡",
    "涩",
    "微甘",
    "微苦",
    "微辛",
    "微酸",
    "味甘",
    "味苦",
    "味辛",
    "味酸",
    "味咸",
)
ZH_CHANNEL_TOKENS: tuple[str, ...] = (
    "归经",
    "入肺",
    "入大肠",
    "入胃",
    "入脾",
    "入心",
    "入小肠",
    "入膀胱",
    "入肾",
    "入心包",
    "入三焦",
    "入胆",
    "入肝",
    "肺经",
    "大肠经",
    "胃经",
    "脾经",
    "心经",
    "小肠经",
    "膀胱经",
    "肾经",
    "心包经",
    "三焦经",
    "胆经",
    "肝经",
)
ZH_DIRECTION_TOKENS: tuple[str, ...] = (
    "升",
    "降",
    "浮",
    "沉",
    "升浮",
    "沉降",
)
ZH_TOX_TOKENS: tuple[str, ...] = (
    "无毒",
    "小毒",
    "有毒",
    "大毒",
)

EN_TOKENS: tuple[str, ...] = (
    "cold",
    "cool",
    "neutral",
    "warm",
    "hot",
    "sour",
    "bitter",
    "sweet",
    "pungent",
    "salty",
    "bland",
    "ascend",
    "ascending",
    "descend",
    "descending",
    "float",
    "floating",
    "sink",
    "sinking",
    "non-toxic",
    "slightly toxic",
    "toxic",
    "highly toxic",
    "lung meridian",
    "heart meridian",
    "spleen meridian",
    "kidney meridian",
    "liver meridian",
    "stomach meridian",
    "bladder meridian",
)

ALL_PROPERTY_TOKENS: tuple[str, ...] = (
    ZH_QI_TOKENS
    + ZH_FLAVOR_TOKENS
    + ZH_CHANNEL_TOKENS
    + ZH_DIRECTION_TOKENS
    + ZH_TOX_TOKENS
    + EN_TOKENS
)


def build_property_regex(tokens: tuple[str, ...] = ALL_PROPERTY_TOKENS) -> re.Pattern[str]:
    """Compile an alternation regex that matches the longest token first.

    Sorting by length descending ensures multi-character tokens (e.g.
    "性寒") win over their substrings ("寒"). Word boundaries are not
    used because Chinese text has no whitespace word boundaries; for
    English tokens we add ``\\b`` on either side to avoid matching
    inside words like "warmth".
    """
    parts: list[str] = []
    for tok in sorted(tokens, key=len, reverse=True):
        if all(ord(c) < 128 for c in tok):
            parts.append(rf"\b{re.escape(tok)}\b")
        else:
            parts.append(re.escape(tok))
    return re.compile("|".join(parts), flags=re.IGNORECASE)


PROPERTY_REGEX: re.Pattern[str] = build_property_regex()
