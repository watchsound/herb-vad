import polars as pl
import pytest

from herb_vad.embeddings.embedder import MockEmbedder
from herb_vad.embeddings.text_lm import VALID_VARIANTS, embed_all_variants, embed_herbs


def _texts() -> pl.DataFrame:
    return pl.DataFrame(
        {
            "canonical_id": ["H00001", "H00002", "H00003"],
            "definition": ["renshen definition", "shigao definition", ""],
            "indication": ["renshen indication", "", "mahuang indication"],
            "concat": ["full ren shen", "", "full ma huang"],
            "indication_masked": ["renshen [PROP] indication", "", "mahuang [PROP]"],
        }
    )


def test_embed_herbs_one_row_per_input():
    df = embed_herbs(_texts(), MockEmbedder(dim=8), variant="definition")
    assert df.height == 3


def test_embed_herbs_dim_matches_embedder():
    df = embed_herbs(_texts(), MockEmbedder(dim=16), variant="concat")
    assert df["dim"].unique().to_list() == [16]
    assert all(len(v) == 16 for v in df["vector"].to_list())


def test_embed_herbs_emits_zero_vector_for_empty_text():
    df = embed_herbs(_texts(), MockEmbedder(dim=8), variant="definition")
    h3_row = df.filter(pl.col("canonical_id") == "H00003").row(0, named=True)
    assert h3_row["is_empty"] is True
    assert all(x == 0.0 for x in h3_row["vector"])


def test_embed_herbs_invalid_variant_raises():
    with pytest.raises(ValueError, match="variant must be"):
        embed_herbs(_texts(), MockEmbedder(dim=4), variant="bogus")


def test_embed_herbs_missing_column_raises():
    bad = _texts().drop("indication")
    with pytest.raises(KeyError):
        embed_herbs(bad, MockEmbedder(dim=4), variant="indication")


def test_embed_herbs_metadata_columns():
    e = MockEmbedder(dim=8, name="mock-test")
    df = embed_herbs(_texts(), e, variant="indication")
    assert df["embedding"].unique().to_list() == ["mock-test"]
    assert df["text_variant"].unique().to_list() == ["indication"]


def test_embed_all_variants_returns_stacked_frame():
    df = embed_all_variants(_texts(), MockEmbedder(dim=4))
    assert df.height == 3 * len(VALID_VARIANTS)
    assert set(df["text_variant"].unique().to_list()) == set(VALID_VARIANTS)
