"""Parser for ETCM v2.0 (Zhang et al. 2023, Acta Pharm. Sin. B).

ETCM stores property/flavor/channel/toxicity labels in Chinese
characters; the zh→en canonicalization lives in ``zh_vocab`` and is
shared with the BATMAN-TCM, HERB, and classical-text ingest paths.
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


def parse_etcm_herbs(path: Path) -> pl.DataFrame:
    raw = pl.read_csv(path, separator="\t")
    rows: list[dict[str, object]] = []
    for r in raw.iter_rows(named=True):
        base = {
            "etcm_id": r.get("Herb_ID"),
            "chinese": r.get("Chinese_name"),
            "pinyin": r.get("Pinyin_name"),
            "latin": r.get("Latin_name"),
            "source": "etcm",
        }

        qi = ZH_QI_MAP.get(str(r.get("Property") or "").strip())
        if qi:
            rows.append({**base, "axis": "QI", "value": qi})

        for token in split_zh_multi(r.get("Flavor")):
            mapped = ZH_FLAVOR_MAP.get(token)
            if mapped:
                rows.append({**base, "axis": "FLAVOR", "value": mapped})

        for token in split_zh_multi(r.get("Meridian")):
            mapped = ZH_CHANNEL_MAP.get(token)
            if mapped:
                rows.append({**base, "axis": "CHANNEL", "value": mapped})

        tox = ZH_TOX_MAP.get(str(r.get("Toxicity") or "").strip())
        if tox:
            rows.append({**base, "axis": "TOXICITY", "value": tox})

    return pl.DataFrame(rows)
