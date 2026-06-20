import polars as pl

from herb_vad.analysis.reliability import (
    fleiss_per_axis,
    label_matrix,
)


def test_label_matrix_groups_subjects_by_canonical_id():
    long = pl.DataFrame(
        {
            "canonical_id": ["H00001", "H00001", "H00001", "H00002", "H00002", "H00002"],
            "source": ["symmap", "tcmsp", "etcm", "symmap", "tcmsp", "etcm"],
            "axis": ["QI"] * 6,
            "value": ["warm", "warm", "warm", "cold", "cold", "warm"],
        }
    )
    mat, herb_ids, classes = label_matrix(long, axis="QI")
    # 2 herbs (subjects) x {warm, cold} (classes) - each subject has 3 raters
    assert mat.shape == (2, 2)
    assert sum(mat[0]) == 3
    assert sum(mat[1]) == 3
    assert set(classes) == {"warm", "cold"}


def test_label_matrix_filters_to_axis():
    long = pl.DataFrame(
        {
            "canonical_id": ["H00001", "H00001", "H00001"],
            "source": ["a", "b", "c"],
            "axis": ["QI", "QI", "FLAVOR"],
            "value": ["warm", "warm", "sweet"],
        }
    )
    mat, herb_ids, classes = label_matrix(long, axis="QI")
    assert mat.shape == (1, 1)  # only QI rows; 1 class (warm)
    assert herb_ids == ["H00001"]


def test_fleiss_per_axis_high_for_unanimous():
    long = pl.DataFrame(
        {
            "canonical_id": ["H00001"] * 6 + ["H00002"] * 6,
            "source": ["a", "b", "c", "d", "e", "f"] * 2,
            "axis": ["QI"] * 12,
            "value": ["warm"] * 6 + ["cold"] * 6,
        }
    )
    out = fleiss_per_axis(long)
    qi_row = out.filter(pl.col("axis") == "QI").row(0, named=True)
    assert qi_row["fleiss_kappa"] >= 0.99  # perfect inter-rater agreement
    assert qi_row["n_herbs"] == 2


def test_fleiss_per_axis_low_for_disagreement():
    long = pl.DataFrame(
        {
            "canonical_id": ["H00001"] * 6 + ["H00002"] * 6,
            "source": ["a", "b", "c", "d", "e", "f"] * 2,
            "axis": ["QI"] * 12,
            # Maximum noise within each herb: 3 cold, 3 warm
            "value": ["warm", "warm", "warm", "cold", "cold", "cold"] * 2,
        }
    )
    out = fleiss_per_axis(long)
    qi_row = out.filter(pl.col("axis") == "QI").row(0, named=True)
    # Within-herb disagreement with balanced marginals: P_o=0.4, P_e=0.5,
    # so kappa = (0.4-0.5)/(1-0.5) = -0.2 (well below unanimous 1.0).
    assert -0.25 < qi_row["fleiss_kappa"] < 0.2


def test_fleiss_drops_axes_with_too_few_herbs():
    long = pl.DataFrame(
        {
            "canonical_id": ["H00001", "H00001"],  # only 1 herb with >= 2 raters
            "source": ["a", "b"],
            "axis": ["DIRECTION"] * 2,
            "value": ["ascend", "ascend"],
        }
    )
    out = fleiss_per_axis(long, min_raters=2, min_herbs=2)
    # min_herbs=2 -> DIRECTION (1 herb) is filtered out
    assert out.filter(pl.col("axis") == "DIRECTION").height == 0


def test_fleiss_handles_per_axis_independently():
    long = pl.DataFrame(
        {
            "canonical_id": ["H00001"] * 4 + ["H00002"] * 4,
            "source": ["a", "b", "c", "d"] * 2,
            "axis": ["QI"] * 2 + ["FLAVOR"] * 2 + ["QI"] * 2 + ["FLAVOR"] * 2,
            "value": [
                "warm",
                "warm",  # QI for H00001 - both raters agree
                "sweet",
                "bitter",  # FLAVOR for H00001 - disagree
                "cold",
                "warm",  # QI for H00002 - disagree
                "sweet",
                "sweet",  # FLAVOR for H00002 - agree
            ],
        }
    )
    out = fleiss_per_axis(long, min_raters=2, min_herbs=1)
    axes = set(out["axis"].to_list())
    assert axes == {"QI", "FLAVOR"}
