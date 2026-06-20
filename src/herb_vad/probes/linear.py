"""Linear probes: L2 logistic regression with stratified CV.

Single-label axes (QI / DIRECTION / TOXICITY) → multinomial LR with
``cross_val_predict``-style accuracy + macro-F1.

Multi-label axes (FLAVOR / CHANNEL) → one-vs-rest LR with macro-F1 +
Jaccard.

All metrics returned through ``herb_vad.schemas.ProbeResult`` for
serialization compatibility with the existing schema.
"""

from __future__ import annotations

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, jaccard_score
from sklearn.model_selection import KFold, StratifiedKFold, cross_val_predict
from sklearn.multiclass import OneVsRestClassifier

from herb_vad.probes.dataset import ProbeDataset
from herb_vad.schemas import ProbeResult, PropertyAxis


def _build_estimator(is_multilabel: bool) -> object:
    # L2 is the default (l1_ratio=0); penalty="l2" / n_jobs=1 are deprecated in
    # sklearn 1.8+, so we rely on defaults rather than spelling them out.
    base = LogisticRegression(
        C=1.0,
        max_iter=2000,
        random_state=42,
    )
    return OneVsRestClassifier(base) if is_multilabel else base


def probe_dataset(
    ds: ProbeDataset,
    *,
    cv_folds: int = 5,
    held_out_symptom: bool = False,
) -> ProbeResult:
    """Cross-validated linear probe on a single (axis, embedding) dataset."""
    if ds.X.shape[0] == 0:
        raise ValueError(f"probe_dataset received empty X for axis {ds.axis}")

    n = ds.X.shape[0]
    folds = min(cv_folds, n)
    if folds < 2:
        raise ValueError(f"need >=2 samples for any CV (got {n})")

    estimator = _build_estimator(ds.is_multilabel)

    if ds.is_multilabel:
        cv = KFold(n_splits=folds, shuffle=True, random_state=42)
        y_pred = cross_val_predict(estimator, ds.X, ds.y, cv=cv)
        accuracy = float(accuracy_score(ds.y, y_pred))  # exact-match
        macro_f1 = float(f1_score(ds.y, y_pred, average="macro", zero_division=0))
    else:
        # Stratified CV needs >=folds samples per class; degrade to KFold if not.
        try:
            cv = StratifiedKFold(n_splits=folds, shuffle=True, random_state=42)
            y_pred = cross_val_predict(estimator, ds.X, ds.y, cv=cv)
        except ValueError:
            cv = KFold(n_splits=folds, shuffle=True, random_state=42)
            y_pred = cross_val_predict(estimator, ds.X, ds.y, cv=cv)
        accuracy = float(accuracy_score(ds.y, y_pred))
        macro_f1 = float(f1_score(ds.y, y_pred, average="macro", zero_division=0))

    embedding_name = "unknown"  # caller fills via report dataframe
    return ProbeResult(
        embedding=embedding_name,
        axis=PropertyAxis(ds.axis),
        accuracy=accuracy,
        macro_f1=macro_f1,
        n=n,
        cv_folds=folds,
        held_out_symptom=held_out_symptom,
    )


def probe_jaccard(ds: ProbeDataset, *, cv_folds: int = 5) -> float:
    """Macro-Jaccard for multilabel datasets; convenience helper."""
    if not ds.is_multilabel:
        raise ValueError("probe_jaccard is for multilabel datasets only")
    folds = min(cv_folds, ds.X.shape[0])
    estimator = _build_estimator(True)
    cv = KFold(n_splits=folds, shuffle=True, random_state=42)
    y_pred = cross_val_predict(estimator, ds.X, ds.y, cv=cv)
    return float(jaccard_score(ds.y, y_pred, average="macro", zero_division=0))
