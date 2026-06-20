"""Embed per-herb texts into row-stacked LM vectors.

Public entrypoint: ``embed_herbs(texts_df, embedder, *, variant)``.
Returns a polars frame with one row per herb and one ``vector`` column
of fixed dimension. The frame's ``embedding`` and ``text_variant``
columns identify which (model, variant) combo produced the row, so
downstream code can stack multiple (model x variant) tables.
"""

from __future__ import annotations

from typing import Iterable

import numpy as np
import polars as pl

from herb_vad.embeddings.embedder import Embedder

VALID_VARIANTS: tuple[str, ...] = ("definition", "indication", "concat", "indication_masked")


def embed_herbs(
    texts_df: pl.DataFrame,
    embedder: Embedder,
    *,
    variant: str,
    batch_size: int = 32,
) -> pl.DataFrame:
    """Embed the ``variant`` column of ``texts_df`` row-by-row.

    ``texts_df`` must have at least ``canonical_id`` and the requested
    ``variant`` column. Empty strings are embedded as zero vectors and
    flagged via the ``is_empty`` column so downstream code can drop them.
    """
    if variant not in VALID_VARIANTS:
        raise ValueError(f"variant must be one of {VALID_VARIANTS}, got {variant!r}")
    if variant not in texts_df.columns:
        raise KeyError(f"texts_df has no column {variant!r}; columns={texts_df.columns}")

    ids: list[str] = texts_df["canonical_id"].to_list()
    raw_texts: list[str] = [t or "" for t in texts_df[variant].to_list()]

    nonempty_index = [i for i, t in enumerate(raw_texts) if t.strip()]
    nonempty_texts = [raw_texts[i] for i in nonempty_index]

    vectors = np.zeros((len(raw_texts), embedder.dim), dtype=np.float32)
    if nonempty_texts:
        # Batch through embedder in chunks
        encoded_chunks: list[np.ndarray] = []
        for start in range(0, len(nonempty_texts), batch_size):
            chunk = nonempty_texts[start : start + batch_size]
            encoded_chunks.append(embedder.encode(chunk))
        encoded = np.vstack(encoded_chunks)
        for src_idx, dst_idx in enumerate(nonempty_index):
            vectors[dst_idx] = encoded[src_idx]

    is_empty = [not t.strip() for t in raw_texts]
    return pl.DataFrame(
        {
            "canonical_id": ids,
            "embedding": [embedder.name] * len(ids),
            "text_variant": [variant] * len(ids),
            "dim": [embedder.dim] * len(ids),
            "vector": [v.tolist() for v in vectors],
            "is_empty": is_empty,
        }
    )


def embed_all_variants(
    texts_df: pl.DataFrame,
    embedder: Embedder,
    *,
    variants: Iterable[str] = VALID_VARIANTS,
    batch_size: int = 32,
) -> pl.DataFrame:
    frames: list[pl.DataFrame] = []
    for v in variants:
        frames.append(embed_herbs(texts_df, embedder, variant=v, batch_size=batch_size))
    return pl.concat(frames, how="vertical")
