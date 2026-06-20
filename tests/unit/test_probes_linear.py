import numpy as np

from herb_vad.probes.dataset import ProbeDataset
from herb_vad.probes.linear import probe_dataset, probe_jaccard


def _trivially_separable_single() -> ProbeDataset:
    rng = np.random.default_rng(0)
    X1 = rng.normal(loc=+1.0, size=(40, 6))
    X2 = rng.normal(loc=-1.0, size=(40, 6))
    X = np.vstack([X1, X2]).astype(np.float32)
    y = np.array([0] * 40 + [1] * 40, dtype=np.int64)
    return ProbeDataset(
        X=X,
        y=y,
        classes=["A", "B"],
        canonical_ids=["x"] * 80,
        axis="QI",
        is_multilabel=False,
    )


def _noisy_single() -> ProbeDataset:
    rng = np.random.default_rng(1)
    X = rng.normal(size=(120, 6)).astype(np.float32)
    y = rng.integers(0, 2, size=120, dtype=np.int64)
    return ProbeDataset(
        X=X,
        y=y,
        classes=["A", "B"],
        canonical_ids=["x"] * 120,
        axis="QI",
        is_multilabel=False,
    )


def _multilabel_easy() -> ProbeDataset:
    rng = np.random.default_rng(2)
    # 3 axes of difficulty separation
    X = rng.normal(size=(80, 6)).astype(np.float32)
    # Class 0 = sign of X[:,0]; class 1 = sign of X[:,1]; class 2 = sign of X[:,2]
    Y = np.column_stack(
        [
            (X[:, 0] > 0).astype(int),
            (X[:, 1] > 0).astype(int),
            (X[:, 2] > 0).astype(int),
        ]
    )
    return ProbeDataset(
        X=X,
        y=Y,
        classes=["a", "b", "c"],
        canonical_ids=["x"] * 80,
        axis="FLAVOR",
        is_multilabel=True,
    )


def test_separable_single_label_gives_high_accuracy():
    r = probe_dataset(_trivially_separable_single())
    assert r.accuracy > 0.9
    assert r.macro_f1 > 0.9
    assert r.n == 80
    assert r.cv_folds == 5
    assert r.held_out_symptom is False


def test_noisy_single_label_gives_near_chance_accuracy():
    r = probe_dataset(_noisy_single())
    assert r.accuracy < 0.7  # <= chance bands for binary noise


def test_multilabel_separable_high_macro_f1():
    r = probe_dataset(_multilabel_easy())
    assert r.macro_f1 > 0.85


def test_held_out_symptom_flag_propagates():
    r = probe_dataset(_trivially_separable_single(), held_out_symptom=True)
    assert r.held_out_symptom is True


def test_jaccard_helper_multilabel():
    j = probe_jaccard(_multilabel_easy())
    assert j > 0.7


def test_jaccard_helper_rejects_singlelabel():
    import pytest

    with pytest.raises(ValueError, match="multilabel"):
        probe_jaccard(_trivially_separable_single())
