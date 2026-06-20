import numpy as np
import polars as pl

from herb_vad.crosswalk.parallel_pairs import (
    build_idf,
    build_parallel_pairs,
    compute_passage_vad,
    tokenize_passage,
)


def test_tokenize_english():
    assert tokenize_passage("Hello World!") == ["hello", "world!"]


def test_tokenize_chinese_char_per_token():
    out = tokenize_passage("怕冷乏力")
    assert out == ["怕", "冷", "乏", "力"]


def test_tokenize_mixed_chinese_english():
    out = tokenize_passage("ren shen 主治 fatigue")
    # Latin runs are lowercased; CJK chars are each one token
    assert "ren" in out
    assert "主" in out
    assert "治" in out
    assert "fatigue" in out


def test_compute_passage_vad_returns_mean():
    lookup = {
        "happy": (0.9, 0.7, 0.8),
        "sad": (-0.5, 0.4, -0.3),
    }
    vec, n = compute_passage_vad("happy sad happy", lookup)
    # 2/3 of the matched mass is "happy" with idf weighting None -> uniform
    expected = np.mean([[0.9, 0.7, 0.8], [-0.5, 0.4, -0.3], [0.9, 0.7, 0.8]], axis=0)
    assert n == 3
    assert np.allclose(vec, expected)


def test_compute_passage_vad_empty_match_returns_zero():
    lookup = {"happy": (0.9, 0.7, 0.8)}
    vec, n = compute_passage_vad("the quick brown fox", lookup)
    assert n == 0
    assert np.allclose(vec, np.zeros(3))


def test_build_idf_log_form():
    passages = ["a b c", "a b", "a"]
    idf = build_idf(passages)
    # n=3, df("a") = 3, df("c") = 1
    # idf("a") = log(4/4) + 1 = 1.0
    # idf("c") = log(4/2) + 1 = log(2) + 1
    assert abs(idf["a"] - 1.0) < 1e-9
    assert abs(idf["c"] - (np.log(2) + 1.0)) < 1e-6


def test_build_parallel_pairs_drops_no_match_rows():
    passages = pl.DataFrame(
        {
            "canonical_id": ["P1", "P2", "P3"],
            "embedding": ["mock"] * 3,
            "text_variant": ["indication_masked"] * 3,
            "dim": [4] * 3,
            "vector": [[0.1, 0.2, 0.3, 0.4], [0.5, 0.6, 0.7, 0.8], [0.0, 0.0, 0.0, 0.0]],
            "is_empty": [False, False, False],
            "text": ["happy sad", "the quick brown fox", "happy"],
        }
    )
    lex = pl.DataFrame(
        {
            "term": ["happy", "sad"],
            "valence": [0.9, -0.5],
            "arousal": [0.7, 0.4],
            "dominance": [0.8, -0.3],
        }
    )
    X, Y, ids = build_parallel_pairs(passages, lex)
    assert ids == ["P1", "P3"]
    assert X.shape == (2, 4)
    assert Y.shape == (2, 3)


def test_build_parallel_pairs_respects_min_matched_tokens():
    passages = pl.DataFrame(
        {
            "canonical_id": ["P1"],
            "embedding": ["mock"],
            "text_variant": ["indication_masked"],
            "dim": [4],
            "vector": [[0.1, 0.2, 0.3, 0.4]],
            "is_empty": [False],
            "text": ["happy"],
        }
    )
    lex = pl.DataFrame(
        {
            "term": ["happy"],
            "valence": [0.9],
            "arousal": [0.7],
            "dominance": [0.8],
        }
    )
    X, Y, ids = build_parallel_pairs(passages, lex, min_matched_tokens=2)
    assert ids == []
    assert X.shape == (0, 0)


def test_build_parallel_pairs_skips_is_empty():
    passages = pl.DataFrame(
        {
            "canonical_id": ["P1", "P2"],
            "embedding": ["mock"] * 2,
            "text_variant": ["indication_masked"] * 2,
            "dim": [4] * 2,
            "vector": [[0.1] * 4, [0.2] * 4],
            "is_empty": [False, True],
            "text": ["happy", "happy"],
        }
    )
    lex = pl.DataFrame(
        {
            "term": ["happy"],
            "valence": [0.9],
            "arousal": [0.7],
            "dominance": [0.8],
        }
    )
    X, Y, ids = build_parallel_pairs(passages, lex)
    assert ids == ["P1"]
