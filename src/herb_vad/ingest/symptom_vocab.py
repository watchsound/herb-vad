"""Curated Chinese symptom-language vocabulary.

Used by Task 11 to filter classical text + PubMed passages and by
Task 20's held-out probe to identify which passages must be evaluated
for embedded cold/hot/etc. signal. Roughly grouped by classical TCM
symptom category. NOT exhaustive — extend as the corpus grows.
"""

from __future__ import annotations

SYMPTOM_GROUPS: dict[str, list[str]] = {
    "thermal": [
        "怕冷",
        "畏寒",
        "恶寒",
        "肢冷",
        "手足冰冷",
        "发热",
        "潮热",
        "烦热",
        "口渴",
        "口干",
        "咽干",
        "盗汗",
        "自汗",
        "面赤",
        "五心烦热",
        "身热",
    ],
    "energy": [
        "乏力",
        "倦怠",
        "气短",
        "懒言",
        "精神不振",
        "嗜睡",
        "失眠",
        "神疲",
        "多梦",
    ],
    "digestive": [
        "腹胀",
        "腹痛",
        "纳呆",
        "食欲不振",
        "恶心",
        "呕吐",
        "便溏",
        "便秘",
        "泄泻",
        "嗳气",
        "反酸",
        "胃脘痛",
        "口苦",
        "口臭",
    ],
    "respiratory": [
        "咳嗽",
        "气喘",
        "喘息",
        "痰多",
        "胸闷",
        "胸痛",
        "鼻塞",
        "流涕",
        "咽痒",
        "声嘶",
    ],
    "head_sensory": [
        "头痛",
        "头晕",
        "眩晕",
        "目眩",
        "耳鸣",
        "目赤",
        "咽痛",
        "目涩",
        "耳聋",
    ],
    "musculoskeletal": [
        "腰痛",
        "关节痛",
        "肢体酸痛",
        "麻木",
        "拘挛",
        "腰膝酸软",
        "肩痛",
    ],
    "psychoaffective": [
        "心悸",
        "怔忡",
        "烦躁",
        "易怒",
        "抑郁",
        "悲伤",
        "恐惧",
        "健忘",
        "心烦",
    ],
    "urogenital": [
        "尿频",
        "尿急",
        "小便不利",
        "夜尿多",
        "遗精",
        "阳痿",
        "月经不调",
        "痛经",
        "带下",
    ],
    "skin_circulation": [
        "瘙痒",
        "皮疹",
        "肿胀",
        "瘀斑",
        "肌肤甲错",
        "面色苍白",
        "面色萎黄",
    ],
}


def all_terms() -> list[str]:
    """Flat list of every symptom term across all groups, deduplicated."""
    seen: set[str] = set()
    out: list[str] = []
    for group in SYMPTOM_GROUPS.values():
        for term in group:
            if term not in seen:
                seen.add(term)
                out.append(term)
    return out


SYMPTOM_TERMS: list[str] = all_terms()
