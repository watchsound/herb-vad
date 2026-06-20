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
    "slightly sour": "sour",
    "bitter": "bitter",
    "slightly bitter": "bitter",
    "sweet": "sweet",
    "slightly sweet": "sweet",
    "pungent": "pungent",
    "slightly pungent": "pungent",
    "acrid": "pungent",
    "spicy": "pungent",
    "salty": "salty",
    "slightly salty": "salty",
    "bland": "bland",
    "tasteless": "bland",
    "astringent": "sour",  # 涩 folded into sour, matching zh_vocab
}

QI_MAP: dict[str, str] = {
    "hot": "hot",
    "extreme hot": "hot",
    "extremely hot": "hot",
    "warm": "warm",
    "mild warm": "warm",
    "slightly warm": "warm",
    "neutral": "neutral",
    "mild": "neutral",
    "plain": "neutral",
    "calm": "neutral",
    "cool": "cool",
    "slightly cool": "cool",
    "mild cool": "cool",
    "mild cold": "cool",
    "slightly cold": "cool",
    "cold": "cold",
    "extreme cold": "cold",
    "extremely cold": "cold",
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
    """Parse SymMap herb-property table.

    Handles two column layouts:
      * **Plan layout** (the test fixture): separate ``Property`` /
        ``Flavor`` / ``Meridian`` / ``Toxicity`` columns. Required ID
        column: ``SMHB_ID``.
      * **Actual v2.0 bulk file** (``SMHB.xlsx`` → ``SMHB.tsv``): a single
        ``Properties_English`` column packing qi + flavor + toxicity
        tokens comma-separated; channels in ``Meridians_English``;
        ID column ``Herb_id``. Each token is routed by lookup —
        whichever of {QI_MAP, FLAVOR_MAP, TOX_MAP} matches wins for its
        axis. This is how SymMap v2.0 actually ships.
    """
    raw = pl.read_csv(path, separator="\t", infer_schema_length=2000)
    cols = set(raw.columns)
    actual_layout = "Properties_English" in cols and "Meridians_English" in cols

    rows: list[dict[str, object]] = []
    for r in raw.iter_rows(named=True):
        base = {
            "smhb_id": r.get("SMHB_ID") or r.get("Herb_id"),
            "chinese": r.get("Chinese_name"),
            "pinyin": r.get("Pinyin_name"),
            "latin": r.get("Latin_name"),
            "source": "symmap",
        }

        if actual_layout:
            # Single column packs qi + flavor + (sometimes) toxicity tokens.
            for token in _split_multi(r.get("Properties_English")):
                qi = QI_MAP.get(token)
                if qi:
                    rows.append({**base, "axis": "QI", "value": qi})
                    continue
                fl = FLAVOR_MAP.get(token)
                if fl:
                    rows.append({**base, "axis": "FLAVOR", "value": fl})
                    continue
                tox = TOX_MAP.get(token)
                if tox:
                    rows.append({**base, "axis": "TOXICITY", "value": tox})
            for token in _split_multi(r.get("Meridians_English")):
                ch = CHANNEL_MAP.get(token)
                if ch:
                    rows.append({**base, "axis": "CHANNEL", "value": ch})
        else:
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
