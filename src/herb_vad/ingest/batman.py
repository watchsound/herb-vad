"""Parser for BATMAN-TCM 2.0 (Kong et al. 2024, NAR).

BATMAN's bulk Herb_info dump stores nature / taste / meridian in Chinese
and omits toxicity. The zh→en canonicalization comes from
``herb_vad.ingest.zh_vocab``.
"""

from __future__ import annotations

from pathlib import Path

import polars as pl

from herb_vad.ingest.zh_vocab import (
    ZH_CHANNEL_MAP,
    ZH_FLAVOR_MAP,
    ZH_QI_MAP,
    split_zh_multi,
)


def parse_batman_herbs(path: Path) -> pl.DataFrame:
    raw = pl.read_csv(path, separator="\t")
    rows: list[dict[str, object]] = []
    for r in raw.iter_rows(named=True):
        base = {
            "batman_id": r.get("batman_id"),
            "chinese": r.get("chinese_name"),
            "pinyin": r.get("pinyin_name"),
            "latin": r.get("latin_name"),
            "source": "batman",
        }

        qi = ZH_QI_MAP.get(str(r.get("nature") or "").strip())
        if qi:
            rows.append({**base, "axis": "QI", "value": qi})

        for token in split_zh_multi(r.get("taste")):
            mapped = ZH_FLAVOR_MAP.get(token)
            if mapped:
                rows.append({**base, "axis": "FLAVOR", "value": mapped})

        for token in split_zh_multi(r.get("meridian")):
            mapped = ZH_CHANNEL_MAP.get(token)
            if mapped:
                rows.append({**base, "axis": "CHANNEL", "value": mapped})

    return pl.DataFrame(rows)
