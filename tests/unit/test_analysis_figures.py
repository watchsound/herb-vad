import polars as pl
import pytest

from herb_vad.analysis.figures import (
    prepare_f1_data,
    prepare_f2_data,
    prepare_f3_data,
    prepare_f4_data,
    prepare_f5_data,
    prepare_f6_data,
    render_f1,
)


def test_f1_orders_axes_canonically():
    df = pl.DataFrame(
        {
            "axis": ["CHANNEL", "QI", "FLAVOR"],
            "fleiss_kappa": [0.3, 0.7, 0.5],
            "n_herbs": [100, 100, 100],
            "n_classes": [12, 5, 6],
        }
    )
    out = prepare_f1_data(df)
    assert out["axis"].to_list() == ["QI", "FLAVOR", "CHANNEL"]


def test_f2_pivots_emb_variant_x_axis():
    df = pl.DataFrame(
        {
            "embedding": ["mock"] * 4,
            "text_variant": ["concat"] * 4,
            "axis": ["QI", "FLAVOR", "QI", "FLAVOR"],
            "macro_f1": [0.7, 0.5, 0.6, 0.4],
            "accuracy": [0.7, 0.5, 0.6, 0.4],
            "n": [100] * 4,
            "cv_folds": [5] * 4,
        }
    )
    out = prepare_f2_data(df)
    assert "emb_variant" in out.columns
    assert {"QI", "FLAVOR"} <= set(out.columns)


def test_f3_aggregates_per_axis():
    df = pl.DataFrame(
        {
            "embedding": ["a", "a", "b"],
            "train_variant": ["concat"] * 3,
            "axis": ["QI", "QI", "FLAVOR"],
            "macro_f1": [0.5, 0.7, 0.4],
            "accuracy": [0.5, 0.7, 0.4],
            "n_held_out": [200, 150, 100],
        }
    )
    out = prepare_f3_data(df)
    qi_row = out.filter(pl.col("axis") == "QI").row(0, named=True)
    assert abs(qi_row["best_macro_f1"] - 0.7) < 1e-9


def test_f4_stratified_sampling_respects_max():
    df = pl.DataFrame(
        {
            "canonical_id": [f"H{i:05d}" for i in range(5000)],
            "vector": [[0.0] * 4] * 5000,
            "embedding": ["mock"] * 5000,
            "text_variant": ["concat"] * 5000,
            "dim": [4] * 5000,
            "is_empty": [False] * 5000,
        }
    )
    out = prepare_f4_data(df, sample=1000)
    assert out.height == 1000


def test_f4_no_sample_when_small():
    df = pl.DataFrame({"canonical_id": ["H00001"], "vector": [[0.1] * 4]})
    out = prepare_f4_data(df, sample=1000)
    assert out.height == 1


def test_f5_passthrough():
    df = pl.DataFrame({"method": ["cca"], "n_pairs": [100], "summary": ["0.7,0.5,0.3"]})
    assert prepare_f5_data(df).height == 1


def test_f6_passthrough():
    df = pl.DataFrame(
        {
            "hypothesis": ["H1", "H2"],
            "result": ["supported", "not_supported"],
            "statistic": [-0.5, 0.1],
            "p_value": [0.002, 0.5],
            "n": [200, 150],
        }
    )
    assert prepare_f6_data(df).height == 2


def test_render_f1_raises_without_mpl(monkeypatch):
    import builtins

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name.startswith("matplotlib"):
            raise ImportError("matplotlib not available in test")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    df = pl.DataFrame({"axis": ["QI"], "fleiss_kappa": [0.7], "n_herbs": [100], "n_classes": [5]})
    from pathlib import Path

    with pytest.raises(ImportError, match=r"\[viz\] extra"):
        render_f1(df, Path("/tmp/whatever.png"))
