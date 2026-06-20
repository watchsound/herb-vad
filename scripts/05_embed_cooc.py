"""Train a formula co-occurrence Word2Vec embedding over the TCM formula corpus.

Requires the ``[ml]`` extra (gensim):
    pip install -e ".[ml]"

Reads data/interim/formulae.parquet (formula_id, canonical_id pairs;
produced by an upstream join of TCMSP + ETCM formula tables - out of
scope for this task) and writes data/processed/embeddings_cooc.parquet.
"""

from __future__ import annotations

from pathlib import Path

import polars as pl

from herb_vad.embeddings.formula_cooc import (
    W2VCoocTrainer,
    build_formula_sequences,
    vectors_to_frame,
)

FORMULAE = Path("data/interim/formulae.parquet")
OUT = Path("data/processed/embeddings_cooc.parquet")


def main() -> None:
    if not FORMULAE.exists():
        raise SystemExit(
            f"Missing {FORMULAE}. Build the formula->canonical_id table "
            "from TCMSP / ETCM formula tables first."
        )
    formulae = pl.read_parquet(FORMULAE)
    sequences = build_formula_sequences(formulae)
    print(f"Training W2V on {len(sequences)} formulae...")
    trainer = W2VCoocTrainer(dim=256, window=10, min_count=3, epochs=20)
    vectors = trainer.train(sequences)
    df = vectors_to_frame(vectors, embedding_name=trainer.name)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.write_parquet(OUT)
    print(f"Wrote {OUT}: {df.height} herbs at dim {trainer.dim}.")


if __name__ == "__main__":
    main()
