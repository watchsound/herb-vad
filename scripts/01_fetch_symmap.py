"""Fetch & parse SymMap herb properties.

SymMap (http://www.symmap.org/) requires a manual download of the SMHB
table from the public Download page; an automated scrape is brittle and
the data is small (~1 MB). Place the downloaded TSV at
``data/raw/symmap/SMHB.tsv`` (the column header must contain at least
SMHB_ID, Chinese_name, Pinyin_name, Latin_name, Property, Flavor,
Meridian, Toxicity).

This script then parses it and writes ``data/interim/symmap.parquet``.
"""

from __future__ import annotations

from pathlib import Path

from herb_vad.ingest.symmap import parse_symmap_herbs

RAW = Path("data/raw/symmap/SMHB.tsv")
OUT = Path("data/interim/symmap.parquet")


def main() -> None:
    if not RAW.exists():
        raise SystemExit(
            f"Missing {RAW}. Download SMHB.tsv from http://www.symmap.org/download/ "
            "and place it there before running this script."
        )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df = parse_symmap_herbs(RAW)
    df.write_parquet(OUT)
    axes = sorted(df["axis"].unique().to_list())
    print(f"Wrote {OUT}: {df.height} rows over axes {axes}")


if __name__ == "__main__":
    main()
