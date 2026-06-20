"""Fetch & parse TCMID herb properties from Zenodo.

TCMID (Huang et al., Nucleic Acids Research; Zenodo record 8066910) ships
``Updated_Herb`` (a CSV) inside a small zip. Auto-downloads + extracts +
parses → ``data/interim/tcmid.parquet``.
"""

from __future__ import annotations

import zipfile
from pathlib import Path
from urllib.request import urlopen

from herb_vad.ingest.tcmid import parse_tcmid_herbs

ZIP_URL = "https://zenodo.org/api/records/8066910/files/TCMID.zip/content"
ZIP = Path("data/raw/tcmid/TCMID.zip")
CSV = Path("data/raw/tcmid/Updated_Herb")
OUT = Path("data/interim/tcmid.parquet")


def _download_zip() -> None:
    ZIP.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {ZIP_URL} -> {ZIP} ...")
    with urlopen(ZIP_URL, timeout=120) as resp, ZIP.open("wb") as fh:
        fh.write(resp.read())
    print(f"Wrote {ZIP} ({ZIP.stat().st_size} bytes)")


def _extract_zip() -> None:
    print(f"Extracting {ZIP} ...")
    with zipfile.ZipFile(ZIP) as zf:
        zf.extractall(ZIP.parent)


def main() -> None:
    if not CSV.exists():
        if not ZIP.exists():
            _download_zip()
        _extract_zip()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df = parse_tcmid_herbs(CSV)
    df.write_parquet(OUT)
    axes = sorted(df["axis"].unique().to_list())
    print(f"Wrote {OUT}: {df.height} rows over axes {axes}")


if __name__ == "__main__":
    main()
