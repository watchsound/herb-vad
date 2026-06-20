import numpy as np
import pytest

from herb_vad.crosswalk.align import (
    cca_align,
    procrustes_align,
)


def test_procrustes_recovers_rotation():
    rng = np.random.default_rng(0)
    X = rng.normal(size=(40, 6))
    # Apply a known rotation
    Q, _ = np.linalg.qr(rng.normal(size=(6, 6)))
    Y = X @ Q
    res = procrustes_align(X, Y)
    assert res.residual < 1e-6


def test_procrustes_zero_residual_on_identity():
    rng = np.random.default_rng(1)
    X = rng.normal(size=(30, 4))
    res = procrustes_align(X, X)
    assert res.residual < 1e-9


def test_procrustes_rejects_shape_mismatch():
    with pytest.raises(ValueError, match="matching shapes"):
        procrustes_align(np.zeros((4, 3)), np.zeros((5, 3)))


def test_procrustes_rejects_empty():
    with pytest.raises(ValueError, match="empty"):
        procrustes_align(np.zeros((0, 4)), np.zeros((0, 4)))


def test_cca_perfect_correlation_when_linear():
    rng = np.random.default_rng(2)
    X = rng.normal(size=(80, 6))
    A = rng.normal(size=(6, 3))
    Y = X @ A  # Linear projection of X
    res = cca_align(X, Y, n_components=3)
    # Each component's sample correlation should be close to 1
    assert np.all(np.abs(res.correlations) > 0.95)


def test_cca_low_correlation_on_noise():
    rng = np.random.default_rng(3)
    X = rng.normal(size=(80, 6))
    Y = rng.normal(size=(80, 3))  # independent
    res = cca_align(X, Y, n_components=3)
    # Even random data fits something; sample sizes mean we may see
    # noticeable apparent correlation, but it should be markedly below
    # the linear-projection case above.
    assert np.all(np.abs(res.correlations) < 0.7)


def test_cca_rejects_insufficient_samples():
    with pytest.raises(ValueError):
        cca_align(np.zeros((2, 6)), np.zeros((2, 3)), n_components=3)


def test_cca_components_capped_at_min_dim():
    rng = np.random.default_rng(4)
    X = rng.normal(size=(20, 4))
    Y = rng.normal(size=(20, 2))  # Y has only 2 dims
    res = cca_align(X, Y, n_components=5)  # request more than possible
    assert res.X_c.shape[1] == 2  # capped at min(4, 2, 5)
