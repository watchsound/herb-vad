"""Build the 4-variant text representation table for every canonical herb.

Reads:
  - data/interim/herb_master.parquet
  - data/interim/classical_paragraphs.parquet (optional)
  - data/interim/pubmed_tcm.parquet (optional)

Writes:
  - data/interim/herb_texts.parquet
  - data/interim/property_vocab.txt (canonical token list for diagnostics)
"""

from __future__ import annotations

from pathlib import Path

import polars as pl

from herb_vad.embeddings.property_vocab import ALL_PROPERTY_TOKENS
from herb_vad.embeddings.text_repr import build_all

MASTER = Path("data/interim/herb_master.parquet")
CLASSICAL = Path("data/interim/classical_paragraphs.parquet")
PUBMED = Path("data/interim/pubmed_tcm.parquet")
OUT_TEXTS = Path("data/interim/herb_texts.parquet")
OUT_VOCAB = Path("data/interim/property_vocab.txt")


def _load_corpus() -> pl.DataFrame:
    parts: list[pl.DataFrame] = []
    if CLASSICAL.exists():
        parts.append(pl.read_parquet(CLASSICAL).select(["source", "text"]))
    if PUBMED.exists():
        pm = pl.read_parquet(PUBMED).select(
            pl.lit("pubmed").alias("source"),
            (pl.col("title") + " " + pl.col("abstract")).alias("text"),
        )
        parts.append(pm)
    if not parts:
        return pl.DataFrame({"source": [], "text": []}, schema={"source": pl.Utf8, "text": pl.Utf8})
    return pl.concat(parts, how="vertical")


def main() -> None:
    if not MASTER.exists():
        raise SystemExit(f"Missing {MASTER}. Run scripts/02_harmonize.py first.")
    master = pl.read_parquet(MASTER)
    corpus = _load_corpus()
    out = build_all(master, corpus)
    OUT_TEXTS.parent.mkdir(parents=True, exist_ok=True)
    out.write_parquet(OUT_TEXTS)
    OUT_VOCAB.write_text("\n".join(ALL_PROPERTY_TOKENS) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_TEXTS}: {out.height} herbs × 4 variants.")
    print(f"Wrote {OUT_VOCAB}: {len(ALL_PROPERTY_TOKENS)} property tokens.")


if __name__ == "__main__":
    main()
