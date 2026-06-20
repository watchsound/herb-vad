"""Parser for TCMSP (Ru et al. 2014, J. Cheminform.) herb-property CSV.

TCMSP uses comma-separated values with quoted multi-value cells, e.g.
``"sweet,bitter"`` inside the Taste column. The vocabulary maps to the
same canonical Herb-VAD schema as SymMap, so the value-normalization
dictionaries are imported from the SymMap parser.
"""

from __future__ import annotations

from pathlib import Path

import polars as pl

from herb_vad.ingest.symmap import (
    CHANNEL_MAP,
    FLAVOR_MAP,
    QI_MAP,
    TOX_MAP,
    _split_multi,
)


def parse_tcmsp_herbs(path: Path) -> pl.DataFrame:
    raw = pl.read_csv(path)
    rows: list[dict[str, object]] = []
    for r in raw.iter_rows(named=True):
        base = {
            "chinese": r.get("Herb_cn_name"),
            "pinyin": r.get("Herb_pinyin_name"),
            "latin": r.get("Herb_latin_name"),
            "source": "tcmsp",
        }

        qi = QI_MAP.get(str(r.get("Property") or "").strip().lower())
        if qi:
            rows.append({**base, "axis": "QI", "value": qi})

        for token in _split_multi(r.get("Taste")):
            mapped = FLAVOR_MAP.get(token)
            if mapped:
                rows.append({**base, "axis": "FLAVOR", "value": mapped})

        for token in _split_multi(r.get("Meridian_tropism")):
            mapped = CHANNEL_MAP.get(token)
            if mapped:
                rows.append({**base, "axis": "CHANNEL", "value": mapped})

        # TCMSP omits toxicity from its public bulk Herb table; parser
        # tolerates the missing column rather than emitting a TOX row.
        tox_raw = r.get("Toxicity")
        if tox_raw is not None:
            tox = TOX_MAP.get(str(tox_raw).strip().lower())
            if tox:
                rows.append({**base, "axis": "TOXICITY", "value": tox})

    return pl.DataFrame(rows)
