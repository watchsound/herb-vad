"""Parser for SymMap (Wu et al. 2019, NAR) herb-property TSV.

Maps SymMap's vocabulary to the canonical Herb-VAD schema:
- Property  -> QI axis (hot / warm / neutral / cool / cold)
- Flavor    -> FLAVOR axis (multi-valued, "; "-separated)
- Meridian  -> CHANNEL axis (multi-valued, "; "-separated)
- Toxicity  -> TOXICITY axis (none / slight / moderate / severe)
"""

from pathlib import Path

import polars as pl

CHANNEL_MAP: dict[str, str] = {
    "lung": "lung",
    "large intestine": "large_intestine",
    "stomach": "stomach",
    "spleen": "spleen",
    "heart": "heart",
    "small intestine": "small_intestine",
    "bladder": "bladder",
    "kidney": "kidney",
    "pericardium": "pericardium",
    "san jiao": "san_jiao",
    "triple burner": "san_jiao",
    "triple energizer": "san_jiao",
    "gallbladder": "gallbladder",
    "liver": "liver",
}

FLAVOR_MAP: dict[str, str] = {
    "sour": "sour",
    "bitter": "bitter",
    "sweet": "sweet",
    "pungent": "pungent",
    "acrid": "pungent",
    "spicy": "pungent",
    "salty": "salty",
    "bland": "bland",
    "tasteless": "bland",
}

QI_MAP: dict[str, str] = {
    "hot": "hot",
    "warm": "warm",
    "mild warm": "warm",
    "slightly warm": "warm",
    "neutral": "neutral",
    "mild": "neutral",
    "plain": "neutral",
    "cool": "cool",
    "slightly cool": "cool",
    "mild cool": "cool",
    "mild cold": "cool",
    "cold": "cold",
}

TOX_MAP: dict[str, str] = {
    "none": "none",
    "non-toxic": "none",
    "nontoxic": "none",
    "slight": "slight",
    "mild": "slight",
    "slightly toxic": "slight",
    "moderate": "moderate",
    "toxic": "moderate",
    "severe": "severe",
    "highly toxic": "severe",
    "very toxic": "severe",
}


def _split_multi(raw: str | None) -> list[str]:
    if not raw:
        return []
    parts: list[str] = []
    for token in str(raw).replace(",", ";").split(";"):
        token = token.strip().lower()
        if token:
            parts.append(token)
    return parts


def parse_symmap_herbs(path: Path) -> pl.DataFrame:
    raw = pl.read_csv(path, separator="\t")
    rows: list[dict[str, object]] = []
    for r in raw.iter_rows(named=True):
        base = {
            "smhb_id": r["SMHB_ID"],
            "chinese": r["Chinese_name"],
            "pinyin": r["Pinyin_name"],
            "latin": r.get("Latin_name"),
            "source": "symmap",
        }

        qi = QI_MAP.get(str(r.get("Property") or "").strip().lower())
        if qi:
            rows.append({**base, "axis": "QI", "value": qi})

        for token in _split_multi(r.get("Flavor")):
            mapped = FLAVOR_MAP.get(token)
            if mapped:
                rows.append({**base, "axis": "FLAVOR", "value": mapped})

        for token in _split_multi(r.get("Meridian")):
            mapped = CHANNEL_MAP.get(token)
            if mapped:
                rows.append({**base, "axis": "CHANNEL", "value": mapped})

        tox = TOX_MAP.get(str(r.get("Toxicity") or "").strip().lower())
        if tox:
            rows.append({**base, "axis": "TOXICITY", "value": tox})

    return pl.DataFrame(rows)
