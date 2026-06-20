"""Embed per-herb text representations with sentence-transformers.

Requires the ``[ml]`` extra:
    pip install -e ".[ml]"

Reads data/interim/herb_texts.parquet (produced by
scripts/04_build_text_repr.py), embeds the four text variants with
BAAI/bge-m3 (primary) and intfloat/multilingual-e5-large (fallback),
and writes data/processed/embeddings_lm.parquet (long-format).
"""

from __future__ import annotations

from pathlib import Path

import polars as pl

from herb_vad.embeddings.embedder import LMEmbedder
from herb_vad.embeddings.text_lm import embed_all_variants

TEXTS = Path("data/interim/herb_texts.parquet")
OUT = Path("data/processed/embeddings_lm.parquet")

MODELS = ("BAAI/bge-m3",)  # Add "intfloat/multilingual-e5-large" once primary lands.


def main() -> None:
    if not TEXTS.exists():
        raise SystemExit(f"Missing {TEXTS}. Run scripts/04_build_text_repr.py first.")
    texts = pl.read_parquet(TEXTS)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    frames: list[pl.DataFrame] = []
    for model_name in MODELS:
        embedder = LMEmbedder(model_name)
        print(
            f"Embedding {texts.height} herbs x 4 variants with {model_name} (dim {embedder.dim})..."
        )
        frames.append(embed_all_variants(texts, embedder))
    out = pl.concat(frames, how="vertical")
    out.write_parquet(OUT)
    print(f"Wrote {OUT}: {out.height} rows over {out['embedding'].n_unique()} models.")


if __name__ == "__main__":
    main()
