"""Parser for ETCM v2.0 (Zhang et al. 2023, Acta Pharm. Sin. B).

Two ingest paths share this module:

* **Bulk-TSV** path (the original fixture): a TSV with the documented
  ETCM v2.0 column shape (Chinese values in ``Property`` / ``Flavor`` /
  ``Meridian`` / ``Toxicity``) goes through ``parse_etcm_herbs``, which
  routes each row through the shared ``zh_vocab`` zh→en maps.

* **JSON-per-herb** path (the live API): hitting the ETCM Django backend
  at ``http://www.tcmip.cn:18124/home/detail/?id=<pinyin>&type=herb``
  yields one JSON per herb with an English-labeled Basic Information
  section carrying ``Property`` (qi), ``Flavor``, ``Meridian Tropism``.
  ``parse_etcm_json_responses`` walks a directory of those cached
  JSONs and emits canonical (chinese, pinyin, latin, source, axis,
  value) records.

ETCM v2.0 does NOT publish TOXICITY or DIRECTION at the API level —
only QI / FLAVOR / CHANNEL come through. The bulk-TSV path preserves
TOXICITY when the input carries it.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import polars as pl

from herb_vad.ingest.symmap import CHANNEL_MAP, FLAVOR_MAP, QI_MAP
from herb_vad.ingest.zh_vocab import (
    ZH_CHANNEL_MAP,
    ZH_FLAVOR_MAP,
    ZH_QI_MAP,
    ZH_TOX_MAP,
    split_zh_multi,
)

_HTML_TAG_RE = re.compile(r"<[^>]+>")


def _strip_html(s: str) -> str:
    return _HTML_TAG_RE.sub("", s or "").strip()


def parse_etcm_herbs(path: Path) -> pl.DataFrame:
    """Parse the bulk-TSV layout of ETCM (Chinese-language values).

    Expected columns: ``Herb_ID``, ``Chinese_name``, ``Pinyin_name``,
    ``Property``, ``Flavor``, ``Meridian``, ``Toxicity``.
    """
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


def _extract_basic_info(payload: dict) -> dict[str, str]:
    """Pull a flat (key → value) dict from ETCM's Basic Information section."""
    flat: dict[str, str] = {}
    for section in payload.get("data", []):
        if section.get("id") != "base_information":
            continue
        for kv in section.get("value", []):
            if isinstance(kv, dict):
                k = (kv.get("key") or "").strip()
                v = kv.get("value")
                if isinstance(v, str):
                    flat[k] = _strip_html(v)
        break
    return flat


def _split_en_multi(raw: str | None) -> list[str]:
    if not raw:
        return []
    parts: list[str] = []
    for token in str(raw).replace(";", ",").split(","):
        token = token.strip().lower()
        if token:
            parts.append(token)
    return parts


_MERIDIAN_SUFFIX = " meridian"


def _strip_meridian_suffix(token: str) -> str:
    if token.endswith(_MERIDIAN_SUFFIX):
        return token[: -len(_MERIDIAN_SUFFIX)].strip()
    return token


def _parse_one_etcm_json(payload: dict) -> list[dict[str, object]]:
    info = _extract_basic_info(payload)
    if not info:
        return []
    base = {
        "chinese": None,
        "pinyin": info.get("Herb Name in Pinyin"),
        "latin": info.get("Herb Name in Latin"),
        "source": "etcm",
    }
    rows: list[dict[str, object]] = []

    qi = QI_MAP.get((info.get("Property") or "").strip().lower())
    if qi:
        rows.append({**base, "axis": "QI", "value": qi})

    for token in _split_en_multi(info.get("Flavor")):
        mapped = FLAVOR_MAP.get(token)
        if mapped:
            rows.append({**base, "axis": "FLAVOR", "value": mapped})

    for raw_token in _split_en_multi(info.get("Meridian Tropism")):
        token = _strip_meridian_suffix(raw_token)
        mapped = CHANNEL_MAP.get(token)
        if mapped:
            rows.append({**base, "axis": "CHANNEL", "value": mapped})

    return rows


def parse_etcm_json_responses(cache_dir: Path) -> pl.DataFrame:
    """Walk a directory of cached ``<pinyin>.json`` ETCM detail responses
    and emit a long-format property frame.
    """
    rows: list[dict[str, object]] = []
    for json_path in sorted(cache_dir.glob("*.json")):
        try:
            payload = json.loads(json_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if payload.get("code") != 1:
            continue
        rows.extend(_parse_one_etcm_json(payload))
    return pl.DataFrame(rows)
