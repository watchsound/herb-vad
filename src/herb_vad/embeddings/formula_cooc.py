"""Formula co-occurrence ("TCM2Vec-style") herb embeddings.

Each TCM formula is treated as a sentence whose tokens are the canonical
ids of its constituent herbs. A skip-gram Word2Vec model trained on
the ~30k formula corpus yields a dense embedding per herb that captures
*compositional* signal (which herbs are paired in clinical practice),
complementing the LM text embedding's *descriptive* signal.

Public API:
  - ``build_formula_sequences(formula_table)`` -> list[list[str]]
  - ``CoocEmbedder`` (Protocol-compatible with herb_vad.embeddings.embedder.Embedder)
  - ``train_w2v(sequences, dim, ...)`` (lazy-imports gensim)
  - ``MockCoocTrainer`` for tests
"""

from __future__ import annotations

import hashlib
from typing import Protocol, Sequence

import numpy as np
import polars as pl


def build_formula_sequences(formula_table: pl.DataFrame) -> list[list[str]]:
    """Turn a long-format ``(formula_id, canonical_id)`` table into a list
    of herb-id "sentences", one per formula. Order within a formula is
    preserved if the input is pre-sorted; otherwise it follows polars'
    iteration order. Single-herb formulae are dropped (skip-gram needs
    at least 2 tokens to define a context window).
    """
    if "formula_id" not in formula_table.columns or "canonical_id" not in formula_table.columns:
        raise KeyError(
            f"formula_table needs columns formula_id + canonical_id; got {formula_table.columns}"
        )
    grouped = formula_table.group_by("formula_id", maintain_order=True).agg(
        pl.col("canonical_id").alias("herbs")
    )
    out: list[list[str]] = []
    for row in grouped.iter_rows(named=True):
        herbs = [h for h in row["herbs"] if h]
        if len(herbs) >= 2:
            out.append(herbs)
    return out


class CoocTrainer(Protocol):
    """Trainer protocol - implementations train and return embeddings."""

    name: str
    dim: int

    def train(self, sequences: Sequence[Sequence[str]]) -> dict[str, np.ndarray]: ...


class MockCoocTrainer:
    """Deterministic hash-based pseudo-trainer for unit tests.

    Each herb id is hashed into a unit-norm vector. Co-occurrence is
    not used (the mock is purely a dictionary lookup); this is enough
    to exercise the data-prep + driver code without depending on
    gensim.
    """

    def __init__(self, dim: int = 8, name: str = "mock-cooc") -> None:
        self.dim = dim
        self.name = name

    def train(self, sequences: Sequence[Sequence[str]]) -> dict[str, np.ndarray]:
        vocab = {tok for seq in sequences for tok in seq}
        out: dict[str, np.ndarray] = {}
        for tok in sorted(vocab):
            digest = hashlib.sha256(tok.encode("utf-8")).digest()
            vec = np.frombuffer(digest[: self.dim], dtype=np.uint8).astype(np.float32)
            vec = (vec / 127.5) - 1.0
            n = np.linalg.norm(vec) or 1.0
            out[tok] = vec / n
        return out


class W2VCoocTrainer:
    """Lazy-importing gensim Word2Vec trainer.

    Hyperparameters chosen from the plan: skip-gram, dim 256,
    window 10, min_count 3, epochs 20. Imports gensim only on
    ``train`` so the module imports cleanly without the [ml] extra.
    """

    def __init__(
        self,
        *,
        dim: int = 256,
        window: int = 10,
        min_count: int = 3,
        epochs: int = 20,
        seed: int = 42,
        name: str = "tcm2vec-formula",
    ) -> None:
        self.dim = dim
        self.window = window
        self.min_count = min_count
        self.epochs = epochs
        self.seed = seed
        self.name = name

    def train(self, sequences: Sequence[Sequence[str]]) -> dict[str, np.ndarray]:
        try:
            from gensim.models import Word2Vec
        except ImportError as e:
            raise ImportError(
                "gensim is not installed. Install the [ml] extra: " 'pip install -e ".[ml]"'
            ) from e
        model = Word2Vec(
            sentences=list(sequences),
            vector_size=self.dim,
            window=self.window,
            min_count=self.min_count,
            sg=1,  # skip-gram
            workers=1,  # determinism > speed
            seed=self.seed,
            epochs=self.epochs,
        )
        return {tok: np.asarray(model.wv[tok], dtype=np.float32) for tok in model.wv.key_to_index}


def vectors_to_frame(vectors: dict[str, np.ndarray], *, embedding_name: str) -> pl.DataFrame:
    """Convert a {canonical_id: vector} dict into the shared embedding-frame schema."""
    if not vectors:
        return pl.DataFrame(
            {
                "canonical_id": [],
                "embedding": [],
                "text_variant": [],
                "dim": [],
                "vector": [],
                "is_empty": [],
            }
        )
    dim = len(next(iter(vectors.values())))
    ids = sorted(vectors)
    return pl.DataFrame(
        {
            "canonical_id": ids,
            "embedding": [embedding_name] * len(ids),
            "text_variant": ["formula_cooc"] * len(ids),
            "dim": [dim] * len(ids),
            "vector": [vectors[i].tolist() for i in ids],
            "is_empty": [False] * len(ids),
        }
    )
