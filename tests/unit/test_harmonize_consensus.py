import polars as pl

from herb_vad.harmonize.consensus import consensus_labels


def test_unanimous_qi_returns_full_agreement():
    long = pl.DataFrame(
        {
            "canonical_id": ["H00001", "H00001", "H00001"],
            "source": ["symmap", "tcmsp", "etcm"],
            "axis": ["QI", "QI", "QI"],
            "value": ["warm", "warm", "warm"],
        }
    )
    out = consensus_labels(long)
    row = out.filter((pl.col("canonical_id") == "H00001") & (pl.col("axis") == "QI")).row(
        0, named=True
    )
    assert row["consensus_value"] == "warm"
    assert row["agreement"] == 1.0
    assert row["n_sources"] == 3


def test_majority_qi_returns_partial_agreement():
    long = pl.DataFrame(
        {
            "canonical_id": ["H00001"] * 4,
            "source": ["symmap", "tcmsp", "etcm", "batman"],
            "axis": ["QI"] * 4,
            "value": ["warm", "warm", "warm", "hot"],
        }
    )
    out = consensus_labels(long)
    row = out.row(0, named=True)
    assert row["consensus_value"] == "warm"
    assert 0.74 < row["agreement"] < 0.76  # 3/4
    assert row["n_sources"] == 4


def test_tie_breaks_alphabetically_for_determinism():
    long = pl.DataFrame(
        {
            "canonical_id": ["H00001"] * 2,
            "source": ["symmap", "tcmsp"],
            "axis": ["QI"] * 2,
            "value": ["warm", "cool"],
        }
    )
    out = consensus_labels(long)
    row = out.row(0, named=True)
    assert row["consensus_value"] == "cool"  # alphabetical first
    assert row["agreement"] == 0.5
    assert row["n_sources"] == 2


def test_multivalue_axes_handled_per_value():
    # FLAVOR is multi-valued per herb-source. The consensus reports each
    # value separately, with agreement = sources_for_value / sources_for_axis.
    long = pl.DataFrame(
        {
            "canonical_id": ["H00001"] * 5,
            "source": ["symmap", "symmap", "tcmsp", "etcm", "etcm"],
            "axis": ["FLAVOR"] * 5,
            "value": ["sweet", "bitter", "sweet", "sweet", "bitter"],
        }
    )
    out = consensus_labels(long)
    sweet_row = out.filter(pl.col("consensus_value") == "sweet")
    bitter_row = out.filter(pl.col("consensus_value") == "bitter")
    # 3 distinct sources for sweet, 2 for bitter, 3 total sources for FLAVOR axis
    assert sweet_row["agreement"][0] == 1.0  # all 3 sources mention sweet
    assert abs(bitter_row["agreement"][0] - 2 / 3) < 1e-9
    assert sweet_row["n_sources"][0] == 3  # number of sources with the consensus value
    assert bitter_row["n_sources"][0] == 2


def test_output_columns():
    long = pl.DataFrame(
        {
            "canonical_id": ["H00001"],
            "source": ["symmap"],
            "axis": ["QI"],
            "value": ["warm"],
        }
    )
    out = consensus_labels(long)
    assert set(out.columns) >= {"canonical_id", "axis", "consensus_value", "agreement", "n_sources"}
