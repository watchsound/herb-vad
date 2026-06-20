"""Fetch & parse SymMap herb properties.

SymMap v2.0 (http://www.symmap.org/, Wu et al. 2019) distributes the
herb table as ``SMHB.xlsx`` from the public Download page. This script:

1. Downloads ``SMHB.xlsx`` to ``data/raw/symmap/`` if not already present.
2. Converts it to ``SMHB.tsv`` (needs ``openpyxl``).
3. Runs the canonical parser → ``data/interim/symmap.parquet``.

If you've already placed ``SMHB.tsv`` in ``data/raw/symmap/`` by hand,
steps 1 and 2 are skipped.
"""

from __future__ import annotations

from pathlib import Path
from urllib.request import urlopen

from herb_vad.ingest.symmap import parse_symmap_herbs

XLSX_URL = "http://www.symmap.org/static/download/V2.0/" "SymMap%20v2.0%2C%20SMHB%20file.xlsx"
XLSX = Path("data/raw/symmap/SMHB.xlsx")
TSV = Path("data/raw/symmap/SMHB.tsv")
OUT = Path("data/interim/symmap.parquet")


def _download_xlsx() -> None:
    XLSX.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {XLSX_URL} -> {XLSX} ...")
    with urlopen(XLSX_URL, timeout=120) as resp, XLSX.open("wb") as fh:
        fh.write(resp.read())
    print(f"Wrote {XLSX} ({XLSX.stat().st_size} bytes)")


def _convert_xlsx_to_tsv() -> None:
    try:
        import pandas as pd
    except ImportError as e:
        raise SystemExit("pandas required for XLSX conversion") from e
    print(f"Converting {XLSX} -> {TSV} (requires openpyxl) ...")
    df = pd.read_excel(XLSX)
    df.to_csv(TSV, sep="\t", index=False)
    print(f"Wrote {TSV}: {df.shape[0]} rows x {df.shape[1]} cols")


def main() -> None:
    if not TSV.exists():
        if not XLSX.exists():
            _download_xlsx()
        _convert_xlsx_to_tsv()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df = parse_symmap_herbs(TSV)
    df.write_parquet(OUT)
    axes = sorted(df["axis"].unique().to_list())
    print(f"Wrote {OUT}: {df.height} rows over axes {axes}")


if __name__ == "__main__":
    main()
