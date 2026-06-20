"""Parser for the HERB database (Fang et al. 2021, Nucleic Acids Research;
http://herb.ac.cn).

HERB's bulk Herb_info table carries Chinese values for Properties /
Flavors / Meridians / Toxicity, plus a Latin-script common-name column
(``Herb_en_name``) that complements pinyin and is preserved as
``english`` in the output for downstream identity matching.
"""

from __future__ import annotations

from pathlib import Path

import polars as pl

from herb_vad.ingest.zh_vocab import (
    ZH_CHANNEL_MAP,
    ZH_FLAVOR_MAP,
    ZH_QI_MAP,
    ZH_TOX_MAP,
    split_zh_multi,
)


def parse_herb_db(path: Path) -> pl.DataFrame:
    raw = pl.read_csv(path, separator="\t")
    rows: list[dict[str, object]] = []
    for r in raw.iter_rows(named=True):
        base = {
            "herb_db_id": r.get("Herb_ID"),
            "chinese": r.get("Herb_cn_name"),
            "pinyin": r.get("Herb_pinyin_name"),
            "english": r.get("Herb_en_name"),
            "source": "herb_db",
        }

        qi = ZH_QI_MAP.get(str(r.get("Properties") or "").strip())
        if qi:
            rows.append({**base, "axis": "QI", "value": qi})

        for token in split_zh_multi(r.get("Flavors")):
            mapped = ZH_FLAVOR_MAP.get(token)
            if mapped:
                rows.append({**base, "axis": "FLAVOR", "value": mapped})

        for token in split_zh_multi(r.get("Meridians")):
            mapped = ZH_CHANNEL_MAP.get(token)
            if mapped:
                rows.append({**base, "axis": "CHANNEL", "value": mapped})

        tox = ZH_TOX_MAP.get(str(r.get("Toxicity") or "").strip())
        if tox:
            rows.append({**base, "axis": "TOXICITY", "value": tox})

    return pl.DataFrame(rows)
