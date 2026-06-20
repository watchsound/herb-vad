"""Fetch every URN in CTEXT_URNS from ctext.org → cache + parquet.

Hits api.ctext.org once per URN with a 1-second sleep between calls,
caches the raw JSON under data/raw/classical_texts/, and writes
data/interim/classical_paragraphs.parquet.
"""

from __future__ import annotations

from pathlib import Path

from herb_vad.ingest.classical_texts import fetch_all

CACHE = Path("data/raw/classical_texts")
OUT = Path("data/interim/classical_paragraphs.parquet")


def main() -> None:
    df = fetch_all(cache_dir=CACHE)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.write_parquet(OUT)
    print(f"Wrote {OUT}: {df.height} paragraphs from {df['doc_id'].n_unique()} texts.")


if __name__ == "__main__":
    main()
