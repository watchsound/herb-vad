import numpy as np

from herb_vad.crosswalk.hypotheses import (
    bonferroni_holm,
    h1_cold_pattern_lower_valence,
    h2_yang_xu_low_AD,
    h3_gan_yu_high_A_low_V,
    h4_axis_explained_variance,
    h5_cold_closer_to_depression_than_anger,
)


# --- H1 ---------------------------------------------------------------


def test_h1_supported_when_cold_well_below_corpus():
    rng = np.random.default_rng(0)
    corpus = rng.normal(loc=0.0, scale=1.0, size=2000)
    cold = rng.normal(loc=-1.5, scale=0.5, size=200)
    r = h1_cold_pattern_lower_valence(cold, corpus)
    assert r.result == "supported"
    assert r.p_value < 0.01
    assert r.n == 200


def test_h1_not_supported_when_cold_matches_corpus():
    rng = np.random.default_rng(1)
    corpus = rng.normal(size=2000)
    cold = rng.normal(size=200)
    r = h1_cold_pattern_lower_valence(cold, corpus)
    assert r.result == "not_supported"


def test_h1_inconclusive_when_cold_empty():
    r = h1_cold_pattern_lower_valence(np.array([]), np.linspace(-1, 1, 100))
    assert r.result == "inconclusive"


# --- H2 ---------------------------------------------------------------


def test_h2_supported_when_both_axes_low():
    rng = np.random.default_rng(2)
    corpus = rng.normal(size=(2000, 2))
    yang_xu = rng.normal(loc=-1.2, size=(200, 2))
    r = h2_yang_xu_low_AD(yang_xu, corpus)
    assert r.result == "supported"


def test_h2_not_supported_when_only_one_axis_low():
    rng = np.random.default_rng(3)
    corpus = rng.normal(size=(2000, 2))
    yang_xu = np.column_stack(
        [
            rng.normal(loc=-1.2, size=200),  # low arousal
            rng.normal(loc=+0.0, size=200),  # neutral dominance
        ]
    )
    r = h2_yang_xu_low_AD(yang_xu, corpus)
    assert r.result == "not_supported"


# --- H3 ---------------------------------------------------------------


def test_h3_supported_when_arousal_high_valence_low():
    rng = np.random.default_rng(4)
    corpus = rng.normal(size=(2000, 2))
    gan_yu = np.column_stack(
        [
            rng.normal(loc=-1.2, size=300),  # low valence
            rng.normal(loc=+1.2, size=300),  # high arousal
        ]
    )
    r = h3_gan_yu_high_A_low_V(gan_yu, corpus)
    assert r.result == "supported"


# --- H4 ---------------------------------------------------------------


def test_h4_supported_when_qi_flavor_high_channel_low():
    r = h4_axis_explained_variance({"QI": 0.62, "FLAVOR": 0.55, "CHANNEL": 0.12})
    assert r.result == "supported"


def test_h4_not_supported_when_channel_too_high():
    r = h4_axis_explained_variance({"QI": 0.62, "FLAVOR": 0.55, "CHANNEL": 0.45})
    assert r.result == "not_supported"


def test_h4_inconclusive_missing_axis():
    r = h4_axis_explained_variance({"QI": 0.5, "FLAVOR": 0.5})
    assert r.result == "inconclusive"


# --- H5 ---------------------------------------------------------------


def test_h5_supported_when_cold_closer_to_depression():
    cold = np.array([0.0, 0.0, 0.0])
    dep = np.array([0.1, 0.0, 0.0])
    anger = np.array([1.0, 0.0, 0.0])
    r = h5_cold_closer_to_depression_than_anger(cold, dep, anger)
    assert r.result == "supported"
    assert r.statistic > 0


def test_h5_not_supported_when_cold_closer_to_anger():
    cold = np.array([0.0, 0.0, 0.0])
    dep = np.array([1.0, 0.0, 0.0])
    anger = np.array([0.1, 0.0, 0.0])
    r = h5_cold_closer_to_depression_than_anger(cold, dep, anger)
    assert r.result == "not_supported"


# --- Bonferroni-Holm --------------------------------------------------


def test_holm_rejects_smallest_when_below_alpha_over_m():
    # 3 p-values, alpha=0.01 -> thresholds 0.0033, 0.005, 0.01
    rej = bonferroni_holm([0.002, 0.5, 0.001])
    assert rej == [True, False, True]


def test_holm_stops_at_first_failure():
    rej = bonferroni_holm([0.001, 0.5, 0.005])
    # sorted: 0.001 (passes 0.0033), then 0.005 (vs threshold 0.005) — passes,
    # then 0.5 (vs 0.01) — fails.
    assert rej[0] is True  # smallest
    # 0.005 against threshold 0.005 — passes
    assert rej[2] is True
    # 0.5 against threshold 0.01 — fails
    assert rej[1] is False


def test_holm_with_none_pvalues_ignored():
    rej = bonferroni_holm([None, 0.002, None, 0.5])
    # Two tested values: 0.002 (smallest threshold 0.005) passes, 0.5 (threshold 0.01) fails
    assert rej[1] is True
    assert rej[3] is False
    assert rej[0] is False  # None entries not rejected
    assert rej[2] is False
