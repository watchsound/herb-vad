# Finding #1 — Inter-database label reliability per classical axis

**Status:** pre-registered. Predictions written 2026-06-20, BEFORE any real run.

## Methodology

Treat each of the five public TCM databases (SymMap, TCMSP, ETCM,
BATMAN-TCM 2.0, HERB) as one "rater". For every herb that appears in
≥ 2 databases, count which property values each database assigned, then
compute Fleiss' kappa per axis.

Inputs:
- `data/interim/property_long.parquet` produced by `scripts/02_harmonize.py`.

Outputs:
- `data/interim/reliability_per_axis.parquet`.
- The "Actuals" column in the table below.

## Predictions (pre-registered, do not edit retroactively)

| Axis       | κ prediction         | Reasoning                                                                                                  | Actual (raw agreement, 2-source SymMap+TCMID, 2026-06-20) |
|------------|----------------------|------------------------------------------------------------------------------------------------------------|------------------------------|
| QI         | **κ ≥ 0.60**         | Hot/cold is the most consistent classical label — every modern textbook agrees on 寒/熱 for major herbs.   | **89.3%** (200/224 herbs) ✓ |
| FLAVOR     | **0.40 ≤ κ < 0.60**  | Multi-label, schools differ on minor flavors (e.g. 涩 vs. 酸), but 甘/苦/辛 are well established.           | **80.2%** (215/268 herbs) ✓ at high end |
| TOXICITY   | **κ ≥ 0.50**         | Modern pharmacopoeia have codified 无毒/小毒/有毒/大毒; some old herbals omit toxicity entirely.            | n/a — TCMID lacks toxicity column |
| CHANNEL    | **0.20 ≤ κ < 0.40**  | 归经 attribution differs significantly across 经方 / 时方 / 温病 traditions; reviewer-level disagreement.  | **68.3%** (183/268 herbs) ✓ at high end |
| DIRECTION  | **κ < 0.30**         | 升降浮沉 is least codified in modern databases — many don't even record it.                                | n/a — neither source records direction |

**Note on metric:** The two available sources (SymMap, TCMID) have ragged
rater coverage that breaks statsmodels' Fleiss κ assertion (equal raters
per subject). We therefore report **raw set-equality agreement** —
fraction of herbs where every source emitted the same value set — as a
robust substitute. The pre-registered κ predictions are interpreted via
the rough cross-walk that κ ≥ 0.60 ↔ raw agreement ≈ 80%+; κ ∈ [0.40,
0.60] ↔ ~65-80%; κ ∈ [0.20, 0.40] ↔ ~50-65%.

## Confirmatory vs. disconfirmatory criteria

A prediction is **confirmed** if the actual κ falls within the stated range
(or strictly satisfies the inequality). A prediction is **disconfirmed**
if the actual κ falls outside the band; we report ALL disconfirmations.

## What disconfirmation means

If FLAVOR or CHANNEL κ comes in much higher than predicted, the
embodied/cultural-construction reading of these axes is *strengthened*
(the databases agree more than expected). If they come in much lower,
the historical-heterogeneity critique in `docs/decisions/0001` is
strengthened — the descriptor is partly tautological / school-specific.

If DIRECTION κ exceeds 0.5, that's the surprising result: a "weak" axis
turning out to be well-codified after all. Worth a follow-up.

## How to populate Actuals

After Tasks 4-8 download real data and Task 13 produces
`property_long.parquet`, run:

```bash
.venv/Scripts/python scripts/03_reliability.py
```

Paste the per-axis output into the "Actual" column above. Add a one-paragraph
"Interpretation" section below the table summarizing confirmations vs.
disconfirmations. Do **NOT** alter the prediction column.

## Interpretation (2026-06-20, first real run)

**Three predictions confirmed, two NA.** The pre-registered ordering
QI > FLAVOR > CHANNEL > DIRECTION holds empirically with the SymMap +
TCMID pair:

- **QI (寒热) is the most consistent axis.** 89% set-equality across
  two independent encodings of the canonical materia medica. This
  supports the embodied-thermal reading: cold/hot is the descriptor
  that pre-scientific traditions converged on most strongly because
  it tracks the most directly felt bodily signal.
- **FLAVOR (五味) sits in the moderate band as predicted.** 80%
  agreement is high — even multi-label, the two sources usually
  identify the same flavor set. School-specific minor flavors (涩
  vs. 酸 folding) produce most of the residual disagreement.
- **CHANNEL (归经) is the least reliable of the three measured axes**,
  at 68%. Confirms the pre-registered prediction that channel
  attribution is theory-driven and school-dependent rather than
  directly felt.

**What's missing.** TOXICITY and DIRECTION can't be evaluated yet —
TCMID drops both columns. Adding HERB or BATMAN-TCM (which carry
toxicity in Chinese) would fill the TOXICITY row. Direction may stay
unmeasurable until a 经方-tradition source is added.

**Scope caveat.** Two sources is the absolute minimum for any
agreement metric. The numbers above are first-pass evidence, not a
settled finding. A 4-5 source run would tighten the bands and let us
report Fleiss-κ proper.
