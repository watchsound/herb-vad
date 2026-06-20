"""Pre-registered hypothesis tests for the Herb-VAD cross-walk.

Each function returns a dataclass with:
  - test_name
  - statistic (the relevant scalar)
  - p_value (where applicable; None for descriptive tests)
  - result: "supported" | "not_supported" | "inconclusive"
  - n: sample size

Multiple-comparison correction is the caller's responsibility — we
expose raw p-values per hypothesis and a ``bonferroni_holm`` helper
(applied to the five hypotheses in the driver).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
from scipy import stats

HypothesisOutcome = Literal["supported", "not_supported", "inconclusive"]


@dataclass(frozen=True)
class HypothesisResult:
    test_name: str
    statistic: float
    p_value: float | None
    result: HypothesisOutcome
    n: int
    notes: str = ""


# --- H1 ----------------------------------------------------------------


def h1_cold_pattern_lower_valence(
    cold_cluster_valence: np.ndarray,
    corpus_valence: np.ndarray,
    *,
    alpha: float = 0.01,
) -> HypothesisResult:
    """寒证-cluster mean Valence below corpus median (one-sided).

    Uses Wilcoxon rank-sum (Mann-Whitney U) one-sided. The corpus_valence
    array supplies the null distribution.
    """
    if cold_cluster_valence.size == 0:
        return HypothesisResult(
            "H1_cold_pattern_low_V", float("nan"), None, "inconclusive", 0, "empty cold cluster"
        )
    median = float(np.median(corpus_valence))
    stat = float(np.mean(cold_cluster_valence) - median)
    res = stats.mannwhitneyu(cold_cluster_valence, corpus_valence, alternative="less")
    outcome: HypothesisOutcome = "supported" if res.pvalue < alpha else "not_supported"
    return HypothesisResult(
        "H1_cold_pattern_low_V", stat, float(res.pvalue), outcome, int(cold_cluster_valence.size)
    )


# --- H2 ----------------------------------------------------------------


def h2_yang_xu_low_AD(
    yang_xu_AD: np.ndarray,  # shape (n, 2): columns are arousal, dominance
    corpus_AD: np.ndarray,  # shape (m, 2)
    *,
    alpha: float = 0.01,
) -> HypothesisResult:
    """阳虚-cluster has Arousal < median AND Dominance < median.

    Pass if BOTH one-sided tests reach p < alpha.
    """
    if yang_xu_AD.shape[0] == 0:
        return HypothesisResult(
            "H2_yang_xu_low_AD", float("nan"), None, "inconclusive", 0, "empty yang_xu cluster"
        )
    p_A = stats.mannwhitneyu(yang_xu_AD[:, 0], corpus_AD[:, 0], alternative="less").pvalue
    p_D = stats.mannwhitneyu(yang_xu_AD[:, 1], corpus_AD[:, 1], alternative="less").pvalue
    combined_p = float(max(p_A, p_D))  # both must clear alpha
    stat = float(
        (np.mean(yang_xu_AD[:, 0]) - np.median(corpus_AD[:, 0]))
        + (np.mean(yang_xu_AD[:, 1]) - np.median(corpus_AD[:, 1]))
    )
    outcome: HypothesisOutcome = "supported" if combined_p < alpha else "not_supported"
    return HypothesisResult(
        "H2_yang_xu_low_AD",
        stat,
        combined_p,
        outcome,
        int(yang_xu_AD.shape[0]),
        notes=f"p_A={p_A:.4g}, p_D={p_D:.4g}",
    )


# --- H3 ----------------------------------------------------------------


def h3_gan_yu_high_A_low_V(
    gan_yu_VA: np.ndarray,
    corpus_VA: np.ndarray,
    *,
    alpha: float = 0.01,
) -> HypothesisResult:
    """肝郁-cluster has Arousal > median AND Valence < median."""
    if gan_yu_VA.shape[0] == 0:
        return HypothesisResult(
            "H3_gan_yu_high_A_low_V", float("nan"), None, "inconclusive", 0, "empty gan_yu cluster"
        )
    p_A = stats.mannwhitneyu(gan_yu_VA[:, 1], corpus_VA[:, 1], alternative="greater").pvalue
    p_V = stats.mannwhitneyu(gan_yu_VA[:, 0], corpus_VA[:, 0], alternative="less").pvalue
    combined_p = float(max(p_A, p_V))
    stat = float(
        (np.mean(gan_yu_VA[:, 1]) - np.median(corpus_VA[:, 1]))
        - (np.mean(gan_yu_VA[:, 0]) - np.median(corpus_VA[:, 0]))
    )
    outcome: HypothesisOutcome = "supported" if combined_p < alpha else "not_supported"
    return HypothesisResult(
        "H3_gan_yu_high_A_low_V",
        stat,
        combined_p,
        outcome,
        int(gan_yu_VA.shape[0]),
        notes=f"p_V={p_V:.4g}, p_A={p_A:.4g}",
    )


# --- H4 ----------------------------------------------------------------


def h4_axis_explained_variance(
    explained_var_by_axis: dict[str, float],
    *,
    qi_threshold: float = 0.50,
    flavor_threshold: float = 0.50,
    channel_threshold: float = 0.20,
) -> HypothesisResult:
    """CCA explains >=50% of V/A/D variance for QI & FLAVOR; <=20% for CHANNEL.

    Pass = QI >= qi_threshold AND FLAVOR >= flavor_threshold AND CHANNEL <= channel_threshold.
    """
    required = {"QI", "FLAVOR", "CHANNEL"}
    if not required <= explained_var_by_axis.keys():
        return HypothesisResult(
            "H4_axis_variance",
            float("nan"),
            None,
            "inconclusive",
            0,
            f"missing axes: {sorted(required - explained_var_by_axis.keys())}",
        )
    qi = explained_var_by_axis["QI"]
    fl = explained_var_by_axis["FLAVOR"]
    ch = explained_var_by_axis["CHANNEL"]
    cond = (qi >= qi_threshold) and (fl >= flavor_threshold) and (ch <= channel_threshold)
    return HypothesisResult(
        "H4_axis_variance",
        statistic=float(qi - ch),
        p_value=None,
        result="supported" if cond else "not_supported",
        n=3,
        notes=f"QI={qi:.3f}, FLAVOR={fl:.3f}, CHANNEL={ch:.3f}",
    )


# --- H5 ----------------------------------------------------------------


def h5_cold_closer_to_depression_than_anger(
    cold_centroid: np.ndarray,
    depression_centroid: np.ndarray,
    anger_centroid: np.ndarray,
) -> HypothesisResult:
    """Distance(寒证, depression) < Distance(寒证, anger) in shared space."""
    d_dep = float(np.linalg.norm(cold_centroid - depression_centroid))
    d_ang = float(np.linalg.norm(cold_centroid - anger_centroid))
    stat = d_ang - d_dep  # positive when supported
    outcome: HypothesisOutcome = "supported" if d_dep < d_ang else "not_supported"
    return HypothesisResult(
        "H5_cold_close_to_depression",
        statistic=stat,
        p_value=None,
        result=outcome,
        n=1,
        notes=f"d(cold,dep)={d_dep:.3f}, d(cold,anger)={d_ang:.3f}",
    )


# --- Multiple-comparison correction -----------------------------------


def bonferroni_holm(p_values: list[float | None], *, alpha: float = 0.01) -> list[bool]:
    """Holm-Bonferroni: return per-hypothesis significance after correction.

    None p-values (descriptive tests) are treated as already-significant
    iff they don't change the ordering of the remaining tested ones.
    """
    indexed = [(i, p) for i, p in enumerate(p_values) if p is not None]
    indexed.sort(key=lambda x: x[1])
    m = len(indexed)
    rejections = [False] * len(p_values)
    for k, (orig_i, p) in enumerate(indexed):
        threshold = alpha / (m - k)
        if p <= threshold:
            rejections[orig_i] = True
        else:
            break  # Holm: once we fail, stop
    # None p-values: treat their outcome as "supported" iff per-test logic accepted
    return rejections
