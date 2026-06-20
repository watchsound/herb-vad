"""Fetch PubMed TCM abstracts → parquet.

Uses NCBI Entrez (no API key needed at the default 3 req/s rate). Writes
data/interim/pubmed_tcm.parquet with (pmid, title, abstract, language).
"""

from __future__ import annotations

from pathlib import Path

from herb_vad.ingest.pubmed_tcm import fetch_and_parse

OUT = Path("data/interim/pubmed_tcm.parquet")


def main() -> None:
    df = fetch_and_parse(retmax=2000)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.write_parquet(OUT)
    print(
        f"Wrote {OUT}: {df.height} abstracts; languages: {sorted(df['language'].unique().to_list())}"
    )


if __name__ == "__main__":
    main()
