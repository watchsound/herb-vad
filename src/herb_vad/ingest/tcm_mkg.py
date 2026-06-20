"""Parser for the Traditional Chinese Medicine Multi-dimensional
Knowledge Graph (TCM-MKG; Zeng, Zenodo record 19804367).

TCM-MKG ships two TSVs that we join:

* ``D6_Chinese_herbal_pieces.tsv`` — herb identity: ``CHP_ID``,
  ``Chinese_herbal_pieces`` (Chinese name), ``Pinyin_term``,
  ``English_term`` (Latin binomial).
* ``D7_CHP_Medicinal_properties.tsv`` — long-format properties keyed
  on CHP_ID with a ``Class`` field that distinguishes three axes:

  - ``Therapeutic nature`` → QI (Cold / Cool / Neutral / Warm / Hot)
  - ``Medicinal flavor`` → FLAVOR (Astringent / Bitter / Pungent /
    Salty / Sour / Sweet — astringent folds into sour)
  - ``Meridian tropism`` → CHANNEL (12 meridians)

The ``Medicinal_properties`` values follow a ``"<token> <suffix>"``
pattern (e.g. ``"Sweet medicinal"``, ``"Cool therapeutic"``,
``"Lung meridian"``). The parser strips the suffix and routes the
leading token through the canonical SymMap vocab maps.
"""

from __future__ import annotations

from pathlib import Path

import polars as pl

from herb_vad.ingest.symmap import CHANNEL_MAP, FLAVOR_MAP, QI_MAP

_CLASS_TO_AXIS: dict[str, str] = {
    "Therapeutic nature": "QI",
    "Medicinal flavor": "FLAVOR",
    "Meridian tropism": "CHANNEL",
}


def _strip_suffix(value: str, suffix: str) -> str:
    v = (value or "").strip().lower()
    s = suffix.lower()
    if v.endswith(" " + s):
        v = v[: -(len(s) + 1)].strip()
    return v


def parse_tcm_mkg_herbs(herbs_path: Path, properties_path: Path) -> pl.DataFrame:
    herbs = pl.read_csv(herbs_path, separator="\t")
    props = pl.read_csv(properties_path, separator="\t")

    # First column of D6 may be BOM-prefixed (excel-style export); normalize.
    if herbs.columns[0] != "CHP_ID":
        herbs = herbs.rename({herbs.columns[0]: "CHP_ID"})

    id_to_meta = {
        r["CHP_ID"]: (r.get("Chinese_herbal_pieces"), r.get("Pinyin_term"), r.get("English_term"))
        for r in herbs.iter_rows(named=True)
    }

    rows: list[dict[str, object]] = []
    for r in props.iter_rows(named=True):
        cid = r.get("CHP_ID")
        cls = r.get("Class")
        axis = _CLASS_TO_AXIS.get(cls or "")
        if axis is None or cid not in id_to_meta:
            continue
        chinese, pinyin, latin = id_to_meta[cid]
        base = {
            "chp_id": cid,
            "chinese": chinese,
            "pinyin": pinyin,
            "latin": latin,
            "source": "tcm_mkg",
        }
        raw_value = r.get("Medicinal_properties") or ""

        if axis == "QI":
            token = _strip_suffix(raw_value, "therapeutic")
            mapped = QI_MAP.get(token)
            if mapped:
                rows.append({**base, "axis": "QI", "value": mapped})
        elif axis == "FLAVOR":
            token = _strip_suffix(raw_value, "medicinal")
            mapped = FLAVOR_MAP.get(token)
            if mapped:
                rows.append({**base, "axis": "FLAVOR", "value": mapped})
        elif axis == "CHANNEL":
            token = _strip_suffix(raw_value, "meridian")
            mapped = CHANNEL_MAP.get(token)
            if mapped:
                rows.append({**base, "axis": "CHANNEL", "value": mapped})

    return pl.DataFrame(rows)
