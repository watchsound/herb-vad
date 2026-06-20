"""Embed a VAD lexicon (NRC-VAD or CVAW) into the shared embedding-space
schema used by herb_vad.embeddings.text_lm.

Input lexicons all have a ``term`` column. Score columns vary:
  - NRC-VAD v2.1: valence / arousal / dominance (signed [-1, +1])
  - CVAW:        valence / arousal / dominance (dominance is null)

Output frame:
  - canonical_id   = "VAD::{lang}::{term}"   (synthetic id so the row joins
                                              into herb tables without collision)
  - embedding      = embedder.name
  - text_variant   = "vad_term"
  - dim            = embedder.dim
  - vector         = float32 list
  - is_empty       = False (we always embed the term itself)
  - valence / arousal / dominance = pass-through scores

The last three columns are NOT in the herb-embedding schema; downstream
code that wants a strict herb-shaped frame should ``.drop(["valence",
"arousal", "dominance"])`` after the join.
"""

from __future__ import annotations

from typing import Iterable

import polars as pl

from herb_vad.embeddings.embedder import Embedder


def embed_vad_lexicon(
    lexicon: pl.DataFrame,
    embedder: Embedder,
    *,
    lang: str,
    batch_size: int = 64,
) -> pl.DataFrame:
    """Embed the ``term`` column; pass V/A/D scores through.

    ``lexicon`` must have at least ``term``, ``valence``, ``arousal`` and
    ``dominance`` columns. Empty terms are dropped.
    """
    required = {"term", "valence", "arousal", "dominance"}
    missing = required - set(lexicon.columns)
    if missing:
        raise KeyError(f"lexicon missing required columns: {sorted(missing)}")

    lex = lexicon.filter(pl.col("term").is_not_null() & (pl.col("term").str.len_chars() > 0))
    terms: list[str] = lex["term"].to_list()
    if not terms:
        return _empty_frame(embedder.dim, embedder.name)

    chunks = []
    for start in range(0, len(terms), batch_size):
        chunks.append(embedder.encode(terms[start : start + batch_size]))
    import numpy as np

    vectors = np.vstack(chunks)
    canonical_ids = [f"VAD::{lang}::{t}" for t in terms]

    return pl.DataFrame(
        {
            "canonical_id": canonical_ids,
            "embedding": [embedder.name] * len(terms),
            "text_variant": ["vad_term"] * len(terms),
            "dim": [embedder.dim] * len(terms),
            "vector": [v.tolist() for v in vectors],
            "is_empty": [False] * len(terms),
            "term": terms,
            "lang": [lang] * len(terms),
            "valence": lex["valence"].to_list(),
            "arousal": lex["arousal"].to_list(),
            "dominance": lex["dominance"].to_list(),
        }
    )


def _empty_frame(dim: int, embedding_name: str) -> pl.DataFrame:
    return pl.DataFrame(
        {
            "canonical_id": [],
            "embedding": [],
            "text_variant": [],
            "dim": [],
            "vector": [],
            "is_empty": [],
            "term": [],
            "lang": [],
            "valence": [],
            "arousal": [],
            "dominance": [],
        }
    )


def combine_vad_corpora(frames: Iterable[pl.DataFrame]) -> pl.DataFrame:
    """Vertically concat multiple VAD lexicon embedding frames."""
    frames = [f for f in frames if f.height > 0]
    if not frames:
        return _empty_frame(0, "none")
    return pl.concat(frames, how="vertical")
