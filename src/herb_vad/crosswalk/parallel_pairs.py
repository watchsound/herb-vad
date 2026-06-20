"""Build row-aligned (passage_embedding, vad_score_vector) parallel pairs.

For each symptom-corpus passage:
  * passage_embedding = the LM embedding of the passage (e.g. from
    indication_masked variant), dim = embedder.dim.
  * vad_score_vector  = aggregate VAD score derived from the passage by
    looking up each token in the NRC-VAD/CVAW lexicon and computing an
    idf-weighted mean. Shape (3,) for V/A/D.

These pairs are the supervision for Procrustes / CCA in Task 22.
"""

from __future__ import annotations

import math
import re

import numpy as np
import polars as pl

_CJK_RE = re.compile(r"[\u4e00-\u9fff]")


def tokenize_passage(text: str) -> list[str]:
    """Naive multilingual tokenizer.

    English: split on whitespace + lowercase.
    Chinese: each CJK character is its own token (good enough for the
    NRC-VAD-zh lexicon, which is single-character heavy; full segmentation
    can be swapped in later).
    """
    if not text:
        return []
    if _CJK_RE.search(text):
        # Mostly Chinese — emit each CJK char + lowercase Latin runs
        tokens: list[str] = []
        latin_buf: list[str] = []
        for ch in text:
            if _CJK_RE.match(ch):
                if latin_buf:
                    tokens.append("".join(latin_buf).lower())
                    latin_buf = []
                tokens.append(ch)
            elif ch.isalpha():
                latin_buf.append(ch)
            else:
                if latin_buf:
                    tokens.append("".join(latin_buf).lower())
                    latin_buf = []
        if latin_buf:
            tokens.append("".join(latin_buf).lower())
        return tokens
    return [w.lower() for w in text.split()]


def compute_passage_vad(
    text: str,
    vad_lookup: dict[str, tuple[float, float, float]],
    idf: dict[str, float] | None = None,
) -> tuple[np.ndarray, int]:
    """Aggregate VAD score for a passage by averaging matched tokens.

    Returns (vad_vector, n_tokens_matched). ``vad_vector`` is shape (3,);
    if no tokens matched, returns zeros and n=0.
    """
    tokens = tokenize_passage(text)
    matched = [(t, vad_lookup[t]) for t in tokens if t in vad_lookup]
    if not matched:
        return np.zeros(3, dtype=np.float64), 0
    weights = np.asarray([(idf or {}).get(t, 1.0) for t, _ in matched], dtype=np.float64)
    scores = np.asarray([v for _, v in matched], dtype=np.float64)
    weighted = (scores.T * weights).T
    total = weights.sum()
    return weighted.sum(axis=0) / max(total, 1e-12), len(matched)


def build_idf(passages: list[str]) -> dict[str, float]:
    """Standard inverse-document-frequency over the passage corpus."""
    n = len(passages)
    df: dict[str, int] = {}
    for p in passages:
        for tok in set(tokenize_passage(p)):
            df[tok] = df.get(tok, 0) + 1
    return {t: math.log((n + 1) / (k + 1)) + 1.0 for t, k in df.items()}


def build_parallel_pairs(
    passage_embeddings: pl.DataFrame,
    vad_lexicon: pl.DataFrame,
    *,
    min_matched_tokens: int = 1,
) -> tuple[np.ndarray, np.ndarray, list[str]]:
    """Return (X, Y, passage_ids) where X is the LM-embedding matrix and
    Y is the (3,) VAD score matrix, both row-aligned.

    Passages with fewer than ``min_matched_tokens`` matches are dropped
    (their VAD aggregate is uninformative).

    ``passage_embeddings`` must have columns canonical_id, vector,
    is_empty, text (the raw passage). ``vad_lexicon`` must have term,
    valence, arousal, dominance.
    """
    lookup = {
        row["term"]: (
            float(row["valence"] or 0.0),
            float(row["arousal"] or 0.0),
            float(row["dominance"] or 0.0),
        )
        for row in vad_lexicon.iter_rows(named=True)
    }
    rows = passage_embeddings.filter(~pl.col("is_empty")).to_dicts()
    if not rows:
        return np.zeros((0, 0), dtype=np.float32), np.zeros((0, 3), dtype=np.float64), []

    passages = [r["text"] for r in rows]
    idf = build_idf(passages)

    keep_X: list[list[float]] = []
    keep_Y: list[np.ndarray] = []
    keep_ids: list[str] = []
    for r in rows:
        vad, n_matched = compute_passage_vad(r["text"], lookup, idf=idf)
        if n_matched < min_matched_tokens:
            continue
        keep_X.append(r["vector"])
        keep_Y.append(vad)
        keep_ids.append(r["canonical_id"])

    X = np.asarray(keep_X, dtype=np.float32) if keep_X else np.zeros((0, 0), dtype=np.float32)
    Y = np.vstack(keep_Y) if keep_Y else np.zeros((0, 3), dtype=np.float64)
    return X, Y, keep_ids
