"""Fetch & parse ETCM v2.0 herb properties.

ETCM v2.0 (http://www.tcmip.cn/ETCM2/) exposes a per-herb JSON API but
no single bulk download. The expected workflow: a separate
``scripts/01_fetch_etcm_crawl.py`` (TBD, out of scope for this task)
walks the index and produces ``data/raw/etcm/Herb.tsv`` with columns
Herb_ID, Chinese_name, Pinyin_name, Property, Flavor, Meridian,
Toxicity (Chinese labels).

This script then parses that TSV and writes
``data/interim/etcm.parquet``.
"""

from __future__ import annotations

from pathlib import Path

from herb_vad.ingest.etcm import parse_etcm_herbs

RAW = Path("data/raw/etcm/Herb.tsv")
OUT = Path("data/interim/etcm.parquet")


def main() -> None:
    if not RAW.exists():
        raise SystemExit(
            f"Missing {RAW}. See module docstring for the crawl workflow that " "produces this TSV."
        )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df = parse_etcm_herbs(RAW)
    df.write_parquet(OUT)
    axes = sorted(df["axis"].unique().to_list())
    print(f"Wrote {OUT}: {df.height} rows over axes {axes}")


if __name__ == "__main__":
    main()
