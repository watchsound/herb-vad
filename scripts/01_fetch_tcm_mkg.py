"""Fetch & parse TCM-MKG (Traditional Chinese Medicine Multi-dimensional
Knowledge Graph) herb properties.

Source: Zeng J., Zenodo record 19804367. Downloads the two TSVs we
need (D6 herb identity + D7 properties) and writes
``data/interim/tcm_mkg.parquet``.
"""

from __future__ import annotations

from pathlib import Path
from urllib.request import urlopen

from herb_vad.ingest.tcm_mkg import parse_tcm_mkg_herbs

ZENODO_BASE = "https://zenodo.org/api/records/19804367/files"
FILES = {
    "D6_Chinese_herbal_pieces.tsv": "data/raw/tcm_mkg/D6_Chinese_herbal_pieces.tsv",
    "D7_CHP_Medicinal_properties.tsv": "data/raw/tcm_mkg/D7_CHP_Medicinal_properties.tsv",
}
OUT = Path("data/interim/tcm_mkg.parquet")


def _download(name: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    url = f"{ZENODO_BASE}/{name}/content"
    print(f"Downloading {url} -> {dest} ...")
    with urlopen(url, timeout=300) as resp, dest.open("wb") as fh:
        fh.write(resp.read())
    print(f"Wrote {dest} ({dest.stat().st_size} bytes)")


def main() -> None:
    for name, path_str in FILES.items():
        path = Path(path_str)
        if not path.exists():
            _download(name, path)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df = parse_tcm_mkg_herbs(
        Path("data/raw/tcm_mkg/D6_Chinese_herbal_pieces.tsv"),
        Path("data/raw/tcm_mkg/D7_CHP_Medicinal_properties.tsv"),
    )
    df.write_parquet(OUT)
    axes = sorted(df["axis"].unique().to_list())
    print(f"Wrote {OUT}: {df.height} rows over axes {axes}")


if __name__ == "__main__":
    main()
