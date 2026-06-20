import numpy as np
import polars as pl
import pytest

from herb_vad.crosswalk.vad_embed import combine_vad_corpora, embed_vad_lexicon
from herb_vad.embeddings.embedder import MockEmbedder


def _en_lexicon() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "term": ["happy", "sad", "calm"],
            "valence": [0.96, -0.09, 0.74],
            "arousal": [0.73, 0.45, -0.08],
            "dominance": [0.85, -0.25, 0.53],
        }
    )


def _zh_lexicon_no_dominance() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "term": ["快樂", "悲傷", "平靜"],
            "valence": [0.875, -0.8, 0.525],
            "arousal": [0.55, -0.125, -0.675],
            "dominance": [None, None, None],
        }
    )


def test_embed_assigns_synthetic_canonical_ids():
    out = embed_vad_lexicon(_en_lexicon(), MockEmbedder(dim=8), lang="en")
    ids = out["canonical_id"].to_list()
    assert all(i.startswith("VAD::en::") for i in ids)
    assert ids == ["VAD::en::happy", "VAD::en::sad", "VAD::en::calm"]


def test_embed_vector_dim_matches_embedder():
    e = MockEmbedder(dim=16)
    out = embed_vad_lexicon(_en_lexicon(), e, lang="en")
    assert all(len(v) == 16 for v in out["vector"].to_list())
    assert out["dim"].unique().to_list() == [16]


def test_embed_passes_through_vad_scores():
    out = embed_vad_lexicon(_en_lexicon(), MockEmbedder(dim=8), lang="en")
    happy = out.filter(pl.col("term") == "happy").row(0, named=True)
    assert abs(happy["valence"] - 0.96) < 1e-9
    assert abs(happy["arousal"] - 0.73) < 1e-9
    assert abs(happy["dominance"] - 0.85) < 1e-9


def test_embed_handles_null_dominance():
    out = embed_vad_lexicon(_zh_lexicon_no_dominance(), MockEmbedder(dim=8), lang="zh")
    assert out["dominance"].null_count() == 3
    # Valence/arousal still populated
    assert out["valence"].null_count() == 0


def test_embed_drops_empty_terms():
    lex = pl.DataFrame(
        {
            "term": ["x", "", None, "y"],
            "valence": [0.1, 0.2, 0.3, 0.4],
            "arousal": [0.1, 0.2, 0.3, 0.4],
            "dominance": [0.1, 0.2, 0.3, 0.4],
        }
    )
    out = embed_vad_lexicon(lex, MockEmbedder(dim=4), lang="en")
    assert out["term"].to_list() == ["x", "y"]


def test_embed_missing_required_column_raises():
    bad = pl.DataFrame({"term": ["x"], "valence": [0.1]})  # missing arousal, dominance
    with pytest.raises(KeyError):
        embed_vad_lexicon(bad, MockEmbedder(dim=4), lang="en")


def test_combine_returns_empty_frame_for_no_inputs():
    out = combine_vad_corpora([])
    assert out.height == 0
    assert "canonical_id" in out.columns


def test_combine_vertical_concat():
    en = embed_vad_lexicon(_en_lexicon(), MockEmbedder(dim=4), lang="en")
    zh = embed_vad_lexicon(_zh_lexicon_no_dominance(), MockEmbedder(dim=4), lang="zh")
    combined = combine_vad_corpora([en, zh])
    assert combined.height == 6
    assert set(combined["lang"].to_list()) == {"en", "zh"}


def test_mock_embedder_deterministic_per_term():
    e = MockEmbedder(dim=8)
    out_a = embed_vad_lexicon(_en_lexicon(), e, lang="en")
    out_b = embed_vad_lexicon(_en_lexicon(), e, lang="en")
    for va, vb in zip(out_a["vector"].to_list(), out_b["vector"].to_list()):
        assert np.allclose(va, vb)
