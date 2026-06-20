"""Fetch & parse HERB Herb_info.

HERB (http://herb.ac.cn/Download/, Fang et al. 2021, NAR) provides
``Herb_info.tsv`` as a direct download from the public Download page.
Place the file at ``data/raw/herb_db/Herb_info.tsv`` with columns
Herb_ID, Herb_pinyin_name, Herb_cn_name, Herb_en_name, Properties,
Flavors, Meridians, Toxicity.

This script then parses it and writes
``data/interim/herb_db.parquet``.
"""

from __future__ import annotations

from pathlib import Path

from herb_vad.ingest.herb_db import parse_herb_db

RAW = Path("data/raw/herb_db/Herb_info.tsv")
OUT = Path("data/interim/herb_db.parquet")


def main() -> None:
    if not RAW.exists():
        raise SystemExit(f"Missing {RAW}. Download Herb_info.tsv from herb.ac.cn/Download/.")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df = parse_herb_db(RAW)
    df.write_parquet(OUT)
    axes = sorted(df["axis"].unique().to_list())
    print(f"Wrote {OUT}: {df.height} rows over axes {axes}")


if __name__ == "__main__":
    main()
