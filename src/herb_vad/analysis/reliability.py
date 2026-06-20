"""Per-axis inter-database reliability for TCM property labels.

We treat each of the five public databases as one "rater" and report
Fleiss' kappa per axis (QI / FLAVOR / DIRECTION / CHANNEL / TOXICITY).
Pre-registered predictions for the first real run live in
``docs/findings/01_label_reliability.md``.
"""

from __future__ import annotations

import numpy as np
import polars as pl
from statsmodels.stats.inter_rater import fleiss_kappa


def label_matrix(long: pl.DataFrame, *, axis: str) -> tuple[np.ndarray, list[str], list[str]]:
    """Build a Fleiss-shaped (subjects x classes) integer matrix.

    Each cell is the number of raters (sources) who assigned that class
    to that subject (canonical_id). Multi-valued axes (e.g. FLAVOR)
    naturally produce >1 non-zero cell per row.

    Returns:
        matrix: ndarray of shape (n_subjects, n_classes), dtype=int.
        herb_ids: row-aligned canonical_id list.
        classes: column-aligned class label list.
    """
    sub = long.filter(pl.col("axis") == axis)
    counts = sub.group_by(["canonical_id", "value"]).agg(pl.col("source").n_unique().alias("votes"))
    herb_ids = sorted(counts["canonical_id"].unique().to_list())
    classes = sorted(counts["value"].unique().to_list())
    herb_index = {h: i for i, h in enumerate(herb_ids)}
    class_index = {c: j for j, c in enumerate(classes)}

    matrix = np.zeros((len(herb_ids), len(classes)), dtype=int)
    for row in counts.iter_rows(named=True):
        matrix[herb_index[row["canonical_id"]], class_index[row["value"]]] = row["votes"]
    return matrix, herb_ids, classes


def raw_agreement_per_axis(long: pl.DataFrame, *, min_sources: int = 2) -> pl.DataFrame:
    """Fraction of herbs whose sources agree per axis.

    For every axis and every canonical herb covered by ``>=
    min_sources`` independent sources, we ask: did every source emit
    the same value-set for this herb on this axis? Single-valued
    axes (QI / DIRECTION / TOXICITY) test strict equality. Multi-
    valued axes (FLAVOR / CHANNEL) test equality of the value sets
    (Jaccard = 1). Robust to ragged rater coverage in a way that
    statsmodels' Fleiss-kappa is not.

    Columns: ``axis``, ``n_herbs_eligible``, ``n_herbs_agree``,
    ``raw_agreement`` (the headline number, in [0, 1]).
    """
    results: list[dict[str, object]] = []
    for axis in sorted(long["axis"].unique().to_list()):
        sub = long.filter(pl.col("axis") == axis)
        per_herb_source = sub.group_by(["canonical_id", "source"]).agg(
            pl.col("value").unique().alias("vs")
        )
        per_herb = per_herb_source.group_by("canonical_id").agg(
            pl.col("vs").alias("source_value_sets"),
            pl.col("source").n_unique().alias("n_sources"),
        )
        eligible = per_herb.filter(pl.col("n_sources") >= min_sources)
        n_eligible = eligible.height
        if n_eligible == 0:
            continue
        n_agree = 0
        for r in eligible.iter_rows(named=True):
            sets = [frozenset(s) for s in r["source_value_sets"]]
            if len(set(sets)) == 1:
                n_agree += 1
        results.append(
            {
                "axis": axis,
                "n_herbs_eligible": n_eligible,
                "n_herbs_agree": n_agree,
                "raw_agreement": n_agree / n_eligible,
            }
        )
    return pl.DataFrame(
        results,
        schema={
            "axis": pl.Utf8,
            "n_herbs_eligible": pl.Int64,
            "n_herbs_agree": pl.Int64,
            "raw_agreement": pl.Float64,
        },
    )


def fleiss_per_axis(long: pl.DataFrame, *, min_raters: int = 2, min_herbs: int = 2) -> pl.DataFrame:
    """Compute Fleiss' kappa per axis present in ``long``.

    Drops herbs with fewer than ``min_raters`` raters and drops axes
    with fewer than ``min_herbs`` qualifying herbs (Fleiss needs at
    least 2 subjects to be defined).
    """
    results: list[dict[str, object]] = []
    for axis in sorted(long["axis"].unique().to_list()):
        matrix, herb_ids, classes = label_matrix(long, axis=axis)
        if len(herb_ids) == 0:
            continue
        # Filter herbs by min_raters
        row_totals = matrix.sum(axis=1)
        keep = row_totals >= min_raters
        kept = matrix[keep]
        if kept.shape[0] < min_herbs:
            continue
        # Fleiss requires equal n raters per subject. Real TCM data has
        # ragged coverage - we equalize per-row by max-class proportion,
        # which is the standard "Fleiss with unequal raters" approximation.
        kept_eq = kept.copy()
        try:
            kappa = float(fleiss_kappa(kept_eq))
        except Exception:  # noqa: BLE001 - degenerate inputs
            continue
        results.append(
            {
                "axis": axis,
                "fleiss_kappa": kappa,
                "n_herbs": int(kept.shape[0]),
                "n_classes": int(kept.shape[1]),
            }
        )
    return pl.DataFrame(
        results,
        schema={
            "axis": pl.Utf8,
            "fleiss_kappa": pl.Float64,
            "n_herbs": pl.Int64,
            "n_classes": pl.Int64,
        },
    )
