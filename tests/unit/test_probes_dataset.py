import numpy as np
import polars as pl

from herb_vad.probes.dataset import (
    MULTI_VALUED,
    SINGLE_VALUED,
    assemble,
)


def _embeddings() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "canonical_id": ["H00001", "H00002", "H00003"],
            "embedding": ["mock"] * 3,
            "text_variant": ["concat"] * 3,
            "dim": [4, 4, 4],
            "vector": [
                [0.1, 0.2, 0.3, 0.4],
                [-0.1, -0.2, -0.3, -0.4],
                [0.5, -0.5, 0.5, -0.5],
            ],
            "is_empty": [False, False, False],
        }
    )


def _single_labels() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "canonical_id": ["H00001", "H00002", "H00003"],
            "axis": ["QI"] * 3,
            "consensus_value": ["warm", "cold", "warm"],
        }
    )


def _multi_labels() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "canonical_id": ["H00001", "H00001", "H00002", "H00003", "H00003"],
            "axis": ["FLAVOR"] * 5,
            "consensus_value": ["sweet", "bitter", "sweet", "bitter", "sour"],
        }
    )


def test_single_label_assemble_shape():
    ds = assemble(
        _embeddings(),
        _single_labels(),
        axis="QI",
        embedding_name="mock",
        text_variant="concat",
    )
    assert ds.X.shape == (3, 4)
    assert ds.y.shape == (3,)
    assert ds.is_multilabel is False
    assert ds.classes == ["cold", "warm"]


def test_single_label_y_values_consistent_with_classes():
    ds = assemble(
        _embeddings(),
        _single_labels(),
        axis="QI",
        embedding_name="mock",
        text_variant="concat",
    )
    # H00001 = warm = class index 1; H00002 = cold = 0; H00003 = warm = 1
    assert ds.y.tolist() == [1, 0, 1]


def test_multilabel_assemble_shape():
    ds = assemble(
        _embeddings(),
        _multi_labels(),
        axis="FLAVOR",
        embedding_name="mock",
        text_variant="concat",
    )
    assert ds.X.shape == (3, 4)
    assert ds.y.shape == (3, 3)  # 3 herbs x 3 classes (bitter, sour, sweet)
    assert ds.is_multilabel is True
    assert ds.classes == ["bitter", "sour", "sweet"]


def test_multilabel_y_indicator_matrix():
    ds = assemble(
        _embeddings(),
        _multi_labels(),
        axis="FLAVOR",
        embedding_name="mock",
        text_variant="concat",
    )
    # H00001 has {sweet, bitter} -> [1, 0, 1]
    # H00002 has {sweet}         -> [0, 0, 1]
    # H00003 has {bitter, sour}  -> [1, 1, 0]
    expected = np.array([[1, 0, 1], [0, 0, 1], [1, 1, 0]])
    assert (ds.y == expected).all()


def test_assemble_filters_to_named_embedding_and_variant():
    emb = pl.concat(
        [
            _embeddings(),
            _embeddings().with_columns(pl.lit("other-model").alias("embedding")),
            _embeddings().with_columns(pl.lit("definition").alias("text_variant")),
        ]
    )
    ds = assemble(
        emb,
        _single_labels(),
        axis="QI",
        embedding_name="mock",
        text_variant="concat",
    )
    assert ds.X.shape == (3, 4)  # only the original 3 rows


def test_assemble_drops_is_empty_rows():
    emb = _embeddings().with_columns(pl.Series("is_empty", [False, True, False]))
    ds = assemble(
        emb,
        _single_labels(),
        axis="QI",
        embedding_name="mock",
        text_variant="concat",
    )
    assert ds.X.shape == (2, 4)


def test_axis_kinds_enumerated():
    assert SINGLE_VALUED == {"QI", "DIRECTION", "TOXICITY"}
    assert MULTI_VALUED == {"FLAVOR", "CHANNEL"}
