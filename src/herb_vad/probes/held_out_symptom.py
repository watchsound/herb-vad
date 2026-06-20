"""Held-out symptom probe: trains on herb-text embeddings, tests on
symptom-passage embeddings with property keywords masked.

The probe is the load-bearing experiment of Finding #2: it answers
whether TCM property descriptors live in cognitive/interoceptive space
(predictable from symptom narrative) or only in pharmacological-vocabulary
space (predictable only when the property words themselves are present).

Pipeline:
  1. Train embedding rows = (canonical_id, embedding, text_variant) where
     text_variant in {"definition","concat"}. These are per-HERB.
  2. Held-out embedding rows = (passage_id, embedding, text_variant) where
     text_variant == "indication_masked". These are per-PASSAGE; each
     passage carries the canonical_id it mentions (added by the driver
     before passing to the probe).
  3. Train logistic regression on (X_train, y_train); predict
     (X_held_out, y_held_out) where y_held_out is the consensus property
     label of the canonical_id the passage refers to.
  4. Report macro-F1 and accuracy.

Single-label vs multi-label semantics match herb_vad.probes.linear.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import polars as pl
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.multiclass import OneVsRestClassifier

from herb_vad.probes.dataset import MULTI_VALUED, SINGLE_VALUED
from herb_vad.schemas import ProbeResult, PropertyAxis


@dataclass(frozen=True)
class HeldOutProbeInputs:
    """Arrays from the caller. y_* must use the same class indexing."""

    X_train: np.ndarray
    y_train: np.ndarray
    X_held_out: np.ndarray
    y_held_out: np.ndarray
    is_multilabel: bool


def _build_estimator(is_multilabel: bool) -> Any:
    base = LogisticRegression(C=1.0, max_iter=2000, random_state=42)
    return OneVsRestClassifier(base) if is_multilabel else base


def held_out_probe(
    inputs: HeldOutProbeInputs,
    *,
    axis: str,
    embedding_name: str = "unknown",
) -> ProbeResult:
    if inputs.X_train.shape[0] == 0:
        raise ValueError("X_train empty — cannot train probe")
    if inputs.X_held_out.shape[0] == 0:
        raise ValueError("X_held_out empty — nothing to evaluate")
    if inputs.X_train.shape[1] != inputs.X_held_out.shape[1]:
        raise ValueError(
            f"dim mismatch: train {inputs.X_train.shape[1]} vs held_out {inputs.X_held_out.shape[1]}"
        )
    if axis not in SINGLE_VALUED and axis not in MULTI_VALUED:
        raise ValueError(f"axis {axis!r} not a recognized property axis")

    est = _build_estimator(inputs.is_multilabel)
    est.fit(inputs.X_train, inputs.y_train)
    y_pred = est.predict(inputs.X_held_out)
    accuracy = float(accuracy_score(inputs.y_held_out, y_pred))
    macro_f1 = float(f1_score(inputs.y_held_out, y_pred, average="macro", zero_division=0))
    return ProbeResult(
        embedding=embedding_name,
        axis=PropertyAxis(axis),
        accuracy=accuracy,
        macro_f1=macro_f1,
        n=int(inputs.X_held_out.shape[0]),
        cv_folds=0,
        held_out_symptom=True,
    )


def join_passages_to_labels(
    passage_embeddings: pl.DataFrame,
    labels: pl.DataFrame,
    *,
    axis: str,
) -> pl.DataFrame:
    """Attach the property label of each passage's referenced canonical_id.

    ``passage_embeddings`` must have columns canonical_id, vector, dim,
    embedding, text_variant, is_empty. ``labels`` is the consensus frame
    from Task 13.
    """
    label_rows = labels.filter(pl.col("axis") == axis).select(["canonical_id", "consensus_value"])
    return passage_embeddings.join(label_rows, on="canonical_id", how="inner").filter(
        ~pl.col("is_empty")
    )
