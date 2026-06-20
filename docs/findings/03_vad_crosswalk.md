# Finding #3 — VAD ↔ TCM cross-walk (pre-registered)

**Status:** pre-registered. Predictions written 2026-06-20, BEFORE any real run.

## Why this matters

If the embodied/interoceptive reading of Herb-VAD is right, classical
TCM syndrome categories (寒证, 阳虚, 肝郁) should sit in **the same
regions** of a shared cognitive-affective space that Western dimensional
affect terms (depression, anger, calmness) occupy. Concrete predictions:

## The five hypotheses

### H1 — 寒证 → low Valence

寒证 (cold-pattern) symptom embeddings, when projected to the V/A/D
sub-space, have **mean Valence < corpus median**. One-sided
Wilcoxon rank-sum, α = 0.01.

### H2 — 阳虚 → low Arousal AND low Dominance

阳虚 (yang-deficiency) shows both low A and low D simultaneously. Pass
requires BOTH one-sided tests to clear α = 0.01.

### H3 — 肝郁 → high Arousal, low Valence

肝郁 (liver-qi stagnation) sits in the irritation/anger quadrant. Pass
requires BOTH directions to clear α = 0.01.

### H4 — CCA partitions axes informatively

CCA top-3 components from the herb-property embedding explain:
- ≥ 50% of NRC-VAD V/A/D variance for **QI** AND **FLAVOR** axes
- ≤ 20% of NRC-VAD V/A/D variance for **CHANNEL** axis

The latter is the strongest single test of the project's "channels are
theoretical, not interoceptive" prediction. A CCA explaining lots of VAD
variance from CHANNEL would falsify the cognitive-substrate thesis for
归经.

### H5 — Distance test (the strongest single signal)

In the shared multilingual space:
```
d(寒证-centroid, depression-cluster centroid)  <  d(寒证-centroid, anger-cluster centroid)
```
No multiple-correction needed for H5 (it's a single deterministic
comparison of three centroids).

## Multiple-comparison correction

H1-H3 are family-wise: Holm-Bonferroni at α = 0.01 across the three
syndrome tests. H4 is descriptive (no per-axis p-value). H5 is a single
non-statistical comparison.

## Confirmatory criteria

Each hypothesis is **confirmed** iff its specific bands (above) are
met. The project's **central** claim is supported only if H1 AND (H2 OR
H3) AND H5 are confirmed — that's the minimum bar for "TCM categories
partition the same interoceptive manifold as Western affect." H4 is the
strongest single confirmatory test of the channel-specific prediction.

## What disconfirmation means

- H1 failing: "寒证 ↔ low V" is the project's most accessible prediction.
  Failure here would weaken the entire embodied-cognition reading.
- H2 or H3 partial-failure: the syndrome-to-quadrant mapping needs
  refinement; suggests the descriptors carve a different geometry than
  Western dimensional affect.
- H4 disconfirmation (CHANNEL > 20%): 归经 turns out to have a felt
  substrate after all. This would be a major surprise and would
  warrant a follow-up paper of its own.
- H5 failing: the shared-multilingual-space mapping doesn't carry the
  cross-cultural signal we expected; either the embedding model isn't
  sufficient, or the categories don't actually align.

## How to populate Actuals (after real run)

After `scripts/09_crosswalk.py` (Task 22) and `scripts/10_crosswalk_hypotheses.py`
produce results, paste the per-hypothesis row from
`data/processed/crosswalk_hypotheses_results.parquet` into the table
below. **Do not edit the prediction column.**

| Hypothesis | Prediction                  | Actual (fill after run) | Holm-corrected | Notes |
|------------|-----------------------------|-------------------------|----------------|-------|
| H1         | 寒证 V < median, p < 0.01   | _TBD_                   | _TBD_          |       |
| H2         | 阳虚 A and D < median, p<0.01 | _TBD_                | _TBD_          |       |
| H3         | 肝郁 A > median AND V < med | _TBD_                   | _TBD_          |       |
| H4         | QI ≥ 0.50, FLAVOR ≥ 0.50, CHANNEL ≤ 0.20 | _TBD_      | n/a            |       |
| H5         | d(寒证, dep) < d(寒证, anger) | _TBD_                 | n/a            |       |

## Interpretation (fill after real run)

_TBD — paste here when Actuals are recorded._
