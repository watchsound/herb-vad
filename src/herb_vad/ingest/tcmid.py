"""Parser for TCMID (Traditional Chinese Medicines Integrated Database;
Huang et al. / Zenodo record 8066910).

TCMID's distribution shape (``Updated_Herb`` CSV from the Zenodo zip):
columns ``Pinyin Name``, ``English Name``, ``Latin Name``,
``Attributes``, ``Meridians/Energy_channels``, ``Use Part``,
``Effect``, ``Indication``.

The ``Attributes`` column packs qi + flavor tokens comma-separated
(e.g. ``"Sweet, bitter,Extremely cold"``). We route each token through
the ``QI_MAP`` / ``FLAVOR_MAP`` from ``symmap`` — same vocabulary, same
canonicalization. TCMID does NOT carry an explicit toxicity column
(toxicity may be embedded in the indication/effect free text but we
don't try to extract it here).
"""

from __future__ import annotations

from pathlib import Path

import polars as pl

from herb_vad.ingest.symmap import (
    CHANNEL_MAP,
    FLAVOR_MAP,
    QI_MAP,
    _split_multi,
)


def parse_tcmid_herbs(path: Path) -> pl.DataFrame:
    raw = pl.read_csv(path, infer_schema_length=2000)

    rows: list[dict[str, object]] = []
    for r in raw.iter_rows(named=True):
        base = {
            "chinese": None,
            "pinyin": r.get("Pinyin Name"),
            "latin": r.get("Latin Name"),
            "english": r.get("English Name"),
            "source": "tcmid",
        }

        # Attributes column packs qi + flavor tokens; route each through both maps.
        for token in _split_multi(r.get("Attributes")):
            qi = QI_MAP.get(token)
            if qi:
                rows.append({**base, "axis": "QI", "value": qi})
                continue
            fl = FLAVOR_MAP.get(token)
            if fl:
                rows.append({**base, "axis": "FLAVOR", "value": fl})

        for token in _split_multi(r.get("Meridians/Energy_channels")):
            mapped = CHANNEL_MAP.get(token)
            if mapped:
                rows.append({**base, "axis": "CHANNEL", "value": mapped})

    return pl.DataFrame(rows)
