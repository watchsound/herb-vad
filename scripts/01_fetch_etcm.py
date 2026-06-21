"""Fetch & parse ETCM v2.0 herb properties.

The ETCM front-end is a Vue SPA with no bulk download; the Django
back-end at ``http://www.tcmip.cn:18124`` exposes a per-herb detail
endpoint:

  GET /home/detail/?id=<pinyin>&type=herb

where ``<pinyin>`` is the herb's Pinyin name (case-insensitive, no
spaces). This script reads the canonical pinyin set from the harmonized
master table (``data/interim/herb_master.parquet``), hits the detail
endpoint for each pinyin, caches the JSON to
``data/raw/etcm/json/<pinyin>.json``, and writes
``data/interim/etcm.parquet``.

Rate-limited at 200 ms between calls. Resumable: re-running the script
skips pinyins already cached on disk.
"""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from pathlib import Path

import polars as pl

from herb_vad.ingest.etcm import parse_etcm_json_responses

MASTER = Path("data/interim/herb_master.parquet")
CACHE = Path("data/raw/etcm/json")
OUT = Path("data/interim/etcm.parquet")
BASE = "http://www.tcmip.cn:18124/home/detail/?id={pinyin}&type=herb"
SLEEP_SECONDS = 0.2


def _fetch_one(pinyin: str) -> dict | None:
    url = BASE.format(pinyin=pinyin)
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError):
        return None


def _enumerate_pinyins() -> list[str]:
    if not MASTER.exists():
        raise SystemExit(f"Missing {MASTER}. Run scripts/02_harmonize.py first.")
    m = pl.read_parquet(MASTER)
    return sorted(set(m["pinyin_norm"].drop_nulls().to_list()) - {""})


def main() -> None:
    CACHE.mkdir(parents=True, exist_ok=True)
    pinyins = _enumerate_pinyins()
    print(f"Enumerating ETCM for {len(pinyins)} candidate pinyins...")

    hit, miss, skipped = 0, 0, 0
    for i, p in enumerate(pinyins, start=1):
        out_path = CACHE / f"{p}.json"
        if out_path.exists():
            skipped += 1
            continue
        payload = _fetch_one(p)
        time.sleep(SLEEP_SECONDS)
        if payload is None:
            miss += 1
            continue
        if payload.get("code") == 1:
            out_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            hit += 1
        else:
            miss += 1
        if i % 200 == 0:
            print(f"  [{i}/{len(pinyins)}] hit={hit} miss={miss} skipped={skipped}")

    print(f"Crawl done. hit={hit} miss={miss} skipped={skipped}")

    df = parse_etcm_json_responses(CACHE)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.write_parquet(OUT)
    if df.height:
        axes = sorted(df["axis"].unique().to_list())
        print(f"Wrote {OUT}: {df.height} rows over axes {axes}")
    else:
        print(f"Wrote {OUT}: empty.")


if __name__ == "__main__":
    main()
