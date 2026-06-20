import numpy as np

from herb_vad.embeddings.embedder import LMEmbedder, MockEmbedder


def test_mock_embedder_dim():
    e = MockEmbedder(dim=8)
    out = e.encode(["hello", "world", "human readable text"])
    assert out.shape == (3, 8)


def test_mock_embedder_deterministic():
    e = MockEmbedder(dim=16)
    a = e.encode(["人参"])
    b = e.encode(["人参"])
    assert np.allclose(a, b)


def test_mock_embedder_different_inputs_different_outputs():
    e = MockEmbedder(dim=16)
    a = e.encode(["人参"])
    b = e.encode(["石膏"])
    assert not np.allclose(a, b)


def test_mock_embedder_unit_norm():
    e = MockEmbedder(dim=8)
    out = e.encode(["text 1", "another text"])
    norms = np.linalg.norm(out, axis=1)
    assert np.allclose(norms, 1.0, atol=1e-5)


def test_lm_embedder_construct_does_not_import_st():
    # Constructor must NOT import sentence_transformers — code that uses
    # only the type/name must work without [ml] extras installed.
    e = LMEmbedder("BAAI/bge-m3")
    assert e.name == "BAAI/bge-m3"
    assert e._model is None  # lazy


def test_lm_embedder_raises_clear_error_without_st(monkeypatch):
    # Force ImportError on sentence_transformers
    import builtins

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "sentence_transformers" or name.startswith("sentence_transformers."):
            raise ImportError("sentence_transformers not available in test")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    e = LMEmbedder("BAAI/bge-m3")
    import pytest

    with pytest.raises(ImportError, match=r"\[ml\] extra"):
        e.encode(["hi"])
