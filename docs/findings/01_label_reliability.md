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

| Axis       | κ prediction         | Reasoning                                                                                                  | Actual (fill after real run) |
|------------|----------------------|------------------------------------------------------------------------------------------------------------|------------------------------|
| QI         | **κ ≥ 0.60**         | Hot/cold is the most consistent classical label — every modern textbook agrees on 寒/熱 for major herbs.   | _TBD_                        |
| FLAVOR     | **0.40 ≤ κ < 0.60**  | Multi-label, schools differ on minor flavors (e.g. 涩 vs. 酸), but 甘/苦/辛 are well established.           | _TBD_                        |
| TOXICITY   | **κ ≥ 0.50**         | Modern pharmacopoeia have codified 无毒/小毒/有毒/大毒; some old herbals omit toxicity entirely.            | _TBD_                        |
| CHANNEL    | **0.20 ≤ κ < 0.40**  | 归经 attribution differs significantly across 经方 / 时方 / 温病 traditions; reviewer-level disagreement.  | _TBD_                        |
| DIRECTION  | **κ < 0.30**         | 升降浮沉 is least codified in modern databases — many don't even record it.                                | _TBD_                        |

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

## Interpretation (fill after real run)

_TBD — paste here when Actuals are recorded._
