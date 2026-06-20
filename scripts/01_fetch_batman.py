"""Fetch & parse BATMAN-TCM 2.0 Herb_info.

BATMAN-TCM 2.0 (http://bionet.ncpsb.org.cn/batman-tcm/) distributes the
herb table as a SQL dump from the bulk-download page. Convert the
``Herb_info`` table to TSV (mysqldump → sed, or one-shot via the project's
"Download" panel) and place it at ``data/raw/batman_tcm/Herb_info.tsv``
with columns batman_id, chinese_name, pinyin_name, latin_name, nature,
taste, meridian.

This script then parses it and writes
``data/interim/batman.parquet``.
"""

from __future__ import annotations

from pathlib import Path

from herb_vad.ingest.batman import parse_batman_herbs

RAW = Path("data/raw/batman_tcm/Herb_info.tsv")
OUT = Path("data/interim/batman.parquet")


def main() -> None:
    if not RAW.exists():
        raise SystemExit(f"Missing {RAW}. See module docstring for the SQL→TSV workflow.")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df = parse_batman_herbs(RAW)
    df.write_parquet(OUT)
    axes = sorted(df["axis"].unique().to_list())
    print(f"Wrote {OUT}: {df.height} rows over axes {axes}")


if __name__ == "__main__":
    main()
