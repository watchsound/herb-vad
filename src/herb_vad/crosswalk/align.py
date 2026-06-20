"""Geometric alignment between two embedding spaces.

Two complementary methods:

  * ``procrustes_align(X, Y)`` — find orthogonal R s.t. ``X @ R`` best
    matches ``Y``. Returns rotation, scale, and a residual error.
    Used when the two spaces are believed to differ by a rigid rotation +
    uniform scale (the common assumption for two LM embeddings of
    different but conceptually-parallel corpora).

  * ``cca_align(X, Y, n_components)`` — Canonical Correlation Analysis.
    Finds linear projections of X and Y into a shared latent space that
    maximize correlation per component. Returns the fitted CCA object
    along with X' and Y' transformed coordinates.

Both expect ``X`` and ``Y`` to be already row-aligned: the i-th row of
``X`` is the "same thing" (e.g. a passage) as the i-th row of ``Y``
(its VAD-weighted score vector or its lexicon-embedded counterpart).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.linalg import orthogonal_procrustes
from sklearn.cross_decomposition import CCA


@dataclass(frozen=True)
class ProcrustesResult:
    rotation: np.ndarray  # (d, d) orthogonal matrix
    scale: float  # sum of singular values of X.T @ Y (scipy convention)
    residual: float  # ||X @ R - Y|| / ||Y||


def procrustes_align(X: np.ndarray, Y: np.ndarray) -> ProcrustesResult:
    if X.shape != Y.shape:
        raise ValueError(f"Procrustes requires matching shapes, got {X.shape} vs {Y.shape}")
    if X.size == 0:
        raise ValueError("empty matrix")
    # scipy's ``orthogonal_procrustes`` finds R minimizing ||X @ R - Y||;
    # the returned ``scale`` is sum of singular values of X.T @ Y, NOT a
    # multiplier to apply to ``X @ R``.
    R, scale = orthogonal_procrustes(X, Y)
    aligned = X @ R
    residual = float(np.linalg.norm(aligned - Y) / max(np.linalg.norm(Y), 1e-12))
    return ProcrustesResult(rotation=R, scale=float(scale), residual=residual)


@dataclass(frozen=True)
class CCAResult:
    model: CCA
    X_c: np.ndarray
    Y_c: np.ndarray
    correlations: np.ndarray  # per-component sample correlations


def cca_align(X: np.ndarray, Y: np.ndarray, *, n_components: int = 3) -> CCAResult:
    if X.shape[0] != Y.shape[0]:
        raise ValueError(f"row count mismatch: {X.shape[0]} vs {Y.shape[0]}")
    if X.shape[0] < n_components:
        raise ValueError(f"need >={n_components} samples; got {X.shape[0]}")
    max_components = min(n_components, X.shape[1], Y.shape[1])
    model = CCA(n_components=max_components, max_iter=1000)
    model.fit(X, Y)
    X_c, Y_c = model.transform(X, Y)
    corrs = np.asarray(
        [float(np.corrcoef(X_c[:, i], Y_c[:, i])[0, 1]) for i in range(max_components)],
        dtype=np.float64,
    )
    return CCAResult(model=model, X_c=X_c, Y_c=Y_c, correlations=corrs)


def variance_explained_by_cca(result: CCAResult) -> float:
    """Approximate fraction of Y's variance recovered through CCA components.

    Rough indicator computed in the shared CCA latent space:
    ``1 - ||Y_c - X_c||^2 / ||Y_c||^2``. When the alignment is good, the
    transformed X and Y land near each other in the latent space and the
    ratio approaches 1.0. This is NOT the rigorous CCA variance
    decomposition; it's a quick scalar for monitoring.
    """
    num = float(np.linalg.norm(result.Y_c - result.X_c) ** 2)
    den = float(np.linalg.norm(result.Y_c) ** 2) + 1e-12
    return 1.0 - (num / den)
