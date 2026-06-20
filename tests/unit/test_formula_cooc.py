import numpy as np
import polars as pl
import pytest

from herb_vad.embeddings.formula_cooc import (
    MockCoocTrainer,
    W2VCoocTrainer,
    build_formula_sequences,
    vectors_to_frame,
)


def _formula_table() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "formula_id": ["F1", "F1", "F1", "F2", "F2", "F3"],
            "canonical_id": ["H00001", "H00002", "H00003", "H00001", "H00004", "H00005"],
        }
    )


def test_build_sequences_groups_by_formula():
    seqs = build_formula_sequences(_formula_table())
    # F1 has 3 herbs, F2 has 2 herbs, F3 has 1 (dropped)
    assert seqs == [["H00001", "H00002", "H00003"], ["H00001", "H00004"]]


def test_build_sequences_skips_singleton_formulae():
    seqs = build_formula_sequences(_formula_table())
    # No length-1 sequence makes it through
    assert all(len(s) >= 2 for s in seqs)


def test_build_sequences_missing_columns_raises():
    bad = pl.DataFrame({"formula": ["F1"], "herb": ["H00001"]})
    with pytest.raises(KeyError):
        build_formula_sequences(bad)


def test_mock_trainer_emits_unit_norm_vectors():
    seqs = build_formula_sequences(_formula_table())
    vecs = MockCoocTrainer(dim=16).train(seqs)
    # Vocab is 4 distinct herbs (H00001 reused, H00003 only in F1, H00005 dropped)
    assert set(vecs) == {"H00001", "H00002", "H00003", "H00004"}
    for v in vecs.values():
        assert abs(np.linalg.norm(v) - 1.0) < 1e-5


def test_mock_trainer_deterministic():
    seqs = build_formula_sequences(_formula_table())
    a = MockCoocTrainer(dim=8).train(seqs)
    b = MockCoocTrainer(dim=8).train(seqs)
    for k in a:
        assert np.allclose(a[k], b[k])


def test_vectors_to_frame_schema():
    vecs = MockCoocTrainer(dim=4).train(build_formula_sequences(_formula_table()))
    df = vectors_to_frame(vecs, embedding_name="mock-cooc")
    assert df.height == 4
    expected = {"canonical_id", "embedding", "text_variant", "dim", "vector", "is_empty"}
    assert expected == set(df.columns)
    assert df["text_variant"].unique().to_list() == ["formula_cooc"]


def test_vectors_to_frame_empty_input_returns_empty_frame_with_schema():
    df = vectors_to_frame({}, embedding_name="mock-cooc")
    assert df.height == 0
    assert {"canonical_id", "embedding", "text_variant", "dim", "vector", "is_empty"} <= set(
        df.columns
    )


def test_w2v_construct_does_not_import_gensim():
    t = W2VCoocTrainer(dim=64)
    assert t.dim == 64
    assert t.name == "tcm2vec-formula"


def test_w2v_train_raises_when_gensim_missing(monkeypatch):
    import builtins

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "gensim" or name.startswith("gensim."):
            raise ImportError("gensim not installed in this env")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    t = W2VCoocTrainer(dim=8)
    with pytest.raises(ImportError, match=r"\[ml\] extra"):
        t.train([["H00001", "H00002"]])
