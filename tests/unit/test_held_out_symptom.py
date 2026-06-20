import numpy as np
import polars as pl
import pytest

from herb_vad.probes.held_out_symptom import (
    HeldOutProbeInputs,
    held_out_probe,
    join_passages_to_labels,
)


def _separable() -> HeldOutProbeInputs:
    rng = np.random.default_rng(0)
    # Two clusters per axis, same generator on train and held-out:
    X_train_0 = rng.normal(loc=+1.0, size=(50, 6))
    X_train_1 = rng.normal(loc=-1.0, size=(50, 6))
    X_train = np.vstack([X_train_0, X_train_1]).astype(np.float32)
    y_train = np.array([0] * 50 + [1] * 50)
    X_held_0 = rng.normal(loc=+1.0, size=(20, 6))
    X_held_1 = rng.normal(loc=-1.0, size=(20, 6))
    X_held = np.vstack([X_held_0, X_held_1]).astype(np.float32)
    y_held = np.array([0] * 20 + [1] * 20)
    return HeldOutProbeInputs(
        X_train=X_train,
        y_train=y_train,
        X_held_out=X_held,
        y_held_out=y_held,
        is_multilabel=False,
    )


def _domain_shift() -> HeldOutProbeInputs:
    # Train clusters at ±1; held-out drawn from totally different distribution
    rng = np.random.default_rng(1)
    X_train_0 = rng.normal(loc=+1.0, size=(50, 6))
    X_train_1 = rng.normal(loc=-1.0, size=(50, 6))
    X_train = np.vstack([X_train_0, X_train_1]).astype(np.float32)
    y_train = np.array([0] * 50 + [1] * 50)
    # Held-out: same labels, but X is pure noise — should drop accuracy
    X_held = rng.normal(loc=0.0, size=(40, 6)).astype(np.float32)
    y_held = rng.integers(0, 2, size=40)
    return HeldOutProbeInputs(
        X_train=X_train,
        y_train=y_train,
        X_held_out=X_held,
        y_held_out=y_held,
        is_multilabel=False,
    )


def test_separable_held_out_high_accuracy():
    r = held_out_probe(_separable(), axis="QI")
    assert r.accuracy > 0.9
    assert r.macro_f1 > 0.9
    assert r.held_out_symptom is True
    assert r.cv_folds == 0


def test_domain_shifted_held_out_drops_accuracy():
    r = held_out_probe(_domain_shift(), axis="QI")
    assert r.accuracy < 0.7  # near chance — the probe can't transfer


def test_empty_train_raises():
    bad = HeldOutProbeInputs(
        X_train=np.zeros((0, 6)),
        y_train=np.zeros(0, dtype=int),
        X_held_out=np.zeros((10, 6)),
        y_held_out=np.zeros(10, dtype=int),
        is_multilabel=False,
    )
    with pytest.raises(ValueError, match="X_train empty"):
        held_out_probe(bad, axis="QI")


def test_dim_mismatch_raises():
    bad = HeldOutProbeInputs(
        X_train=np.zeros((10, 6)),
        y_train=np.zeros(10, dtype=int),
        X_held_out=np.zeros((10, 8)),
        y_held_out=np.zeros(10, dtype=int),
        is_multilabel=False,
    )
    with pytest.raises(ValueError, match="dim mismatch"):
        held_out_probe(bad, axis="QI")


def test_unknown_axis_raises():
    with pytest.raises(ValueError, match="not a recognized property axis"):
        held_out_probe(_separable(), axis="MOOD")


def test_join_passages_to_labels_filters_to_axis():
    passages = pl.DataFrame(
        {
            "canonical_id": ["H00001", "H00002", "H00099"],
            "embedding": ["mock"] * 3,
            "text_variant": ["indication_masked"] * 3,
            "dim": [4] * 3,
            "vector": [[0.1] * 4, [0.2] * 4, [0.3] * 4],
            "is_empty": [False, False, False],
        }
    )
    labels = pl.DataFrame(
        {
            "canonical_id": ["H00001", "H00002"],
            "axis": ["QI"] * 2,
            "consensus_value": ["warm", "cold"],
        }
    )
    out = join_passages_to_labels(passages, labels, axis="QI")
    # H00099 not in labels → dropped by inner join
    assert out.height == 2
    assert set(out["consensus_value"].to_list()) == {"warm", "cold"}


def test_join_passages_drops_is_empty():
    passages = pl.DataFrame(
        {
            "canonical_id": ["H00001", "H00001"],
            "embedding": ["mock"] * 2,
            "text_variant": ["indication_masked"] * 2,
            "dim": [4] * 2,
            "vector": [[0.1] * 4, [0.2] * 4],
            "is_empty": [False, True],
        }
    )
    labels = pl.DataFrame(
        {
            "canonical_id": ["H00001"],
            "axis": ["QI"],
            "consensus_value": ["warm"],
        }
    )
    out = join_passages_to_labels(passages, labels, axis="QI")
    assert out.height == 1
