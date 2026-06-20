"""Assemble (X, y) tensors from embedding frame + consensus label frame.

Inputs (long-format):
  - embeddings: canonical_id, embedding, text_variant, dim, vector
  - labels: canonical_id, axis, consensus_value (single-valued axes)
            OR canonical_id, axis, consensus_value (multi-valued: many rows per herb-axis)

Output:
  - X: ndarray[float32], shape (n_herbs, dim)
  - y_single: ndarray[int], shape (n_herbs,) for single-valued axes
  - y_multi: ndarray[int], shape (n_herbs, n_classes) for multi-valued axes
  - classes: list[str], ordered by index
  - canonical_ids: list[str], row-aligned with X
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import polars as pl

SINGLE_VALUED = {"QI", "DIRECTION", "TOXICITY"}
MULTI_VALUED = {"FLAVOR", "CHANNEL"}


@dataclass(frozen=True)
class ProbeDataset:
    X: np.ndarray
    y: np.ndarray
    classes: list[str]
    canonical_ids: list[str]
    axis: str
    is_multilabel: bool


def _stack_vectors(embedding_rows: pl.DataFrame) -> tuple[np.ndarray, list[str]]:
    if embedding_rows.height == 0:
        return np.zeros((0, 0), dtype=np.float32), []
    ids = embedding_rows["canonical_id"].to_list()
    vectors = embedding_rows["vector"].to_list()
    return np.asarray(vectors, dtype=np.float32), ids


def assemble(
    embeddings: pl.DataFrame,
    labels: pl.DataFrame,
    *,
    axis: str,
    embedding_name: str,
    text_variant: str,
) -> ProbeDataset:
    if axis not in SINGLE_VALUED and axis not in MULTI_VALUED:
        raise ValueError(f"axis {axis!r} not recognized")

    emb = embeddings.filter(
        (pl.col("embedding") == embedding_name)
        & (pl.col("text_variant") == text_variant)
        & (~pl.col("is_empty"))
    )
    X, emb_ids = _stack_vectors(emb)

    label_rows = labels.filter(pl.col("axis") == axis)
    if axis in SINGLE_VALUED:
        # Take first consensus_value per herb (deduped upstream by Task 13)
        wide = label_rows.group_by("canonical_id", maintain_order=True).agg(
            pl.col("consensus_value").first().alias("label")
        )
        herb_labels = dict(zip(wide["canonical_id"].to_list(), wide["label"].to_list()))
        keep_idx = [i for i, h in enumerate(emb_ids) if h in herb_labels]
        X_kept = X[keep_idx]
        ids_kept = [emb_ids[i] for i in keep_idx]
        classes = sorted({herb_labels[h] for h in ids_kept})
        class_to_idx = {c: j for j, c in enumerate(classes)}
        y = np.asarray([class_to_idx[herb_labels[h]] for h in ids_kept], dtype=np.int64)
        return ProbeDataset(
            X=X_kept,
            y=y,
            classes=classes,
            canonical_ids=ids_kept,
            axis=axis,
            is_multilabel=False,
        )
    else:
        # Multi-valued: aggregate every consensus_value per herb into a set
        wide = label_rows.group_by("canonical_id", maintain_order=True).agg(
            pl.col("consensus_value").alias("labels")
        )
        herb_labels = {
            row["canonical_id"]: set(row["labels"]) for row in wide.iter_rows(named=True)
        }
        keep_idx = [i for i, h in enumerate(emb_ids) if h in herb_labels]
        X_kept = X[keep_idx]
        ids_kept = [emb_ids[i] for i in keep_idx]
        classes = sorted({c for h in ids_kept for c in herb_labels[h]})
        Y = np.zeros((len(ids_kept), len(classes)), dtype=np.int64)
        cidx = {c: j for j, c in enumerate(classes)}
        for i, h in enumerate(ids_kept):
            for c in herb_labels[h]:
                Y[i, cidx[c]] = 1
        return ProbeDataset(
            X=X_kept,
            y=Y,
            classes=classes,
            canonical_ids=ids_kept,
            axis=axis,
            is_multilabel=True,
        )
