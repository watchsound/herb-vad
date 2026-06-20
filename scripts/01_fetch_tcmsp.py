"""Fetch & parse TCMSP herb properties.

TCMSP (https://old.tcmsp-e.com/, Ru et al. 2014) requires manual export
of the Herb table from the bulk-download page; an automated scrape would
trip the captcha on the v2 site. Place the exported CSV at
``data/raw/tcmsp/Herb.csv`` and ensure it has at least the columns
Herb_cn_name, Herb_pinyin_name, Herb_latin_name, Property, Taste,
Meridian_tropism.

This script then parses it and writes ``data/interim/tcmsp.parquet``.
"""

from __future__ import annotations

from pathlib import Path

from herb_vad.ingest.tcmsp import parse_tcmsp_herbs

RAW = Path("data/raw/tcmsp/Herb.csv")
OUT = Path("data/interim/tcmsp.parquet")


def main() -> None:
    if not RAW.exists():
        raise SystemExit(
            f"Missing {RAW}. Export the Herb table from old.tcmsp-e.com "
            "and place it there before running this script."
        )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df = parse_tcmsp_herbs(RAW)
    df.write_parquet(OUT)
    axes = sorted(df["axis"].unique().to_list())
    print(f"Wrote {OUT}: {df.height} rows over axes {axes}")


if __name__ == "__main__":
    main()
