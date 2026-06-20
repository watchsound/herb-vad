# Finding #2 — Cognitive substrate of TCM property axes (held-out symptom probe)

**Status:** pre-registered. Predictions written 2026-06-20, BEFORE any real run.

## Question

Are the classical TCM property descriptors (寒/热, 酸/苦/甘/辛/咸, 归经, 升降浮沉, 毒性) **predictable from symptom-language alone**, with all property keywords explicitly masked out?

If yes → the descriptors live in *interoceptive-cognitive* space (Lakoff–Johnson, Barrett constructionism applied to TCM).
If no → they're purely vocabulary-discursive labels with no felt-experience grounding.

## Protocol

1. Train an L2 logistic-regression probe on per-herb LM embeddings of `definition` (and separately `concat`) text variants → predict consensus property value.
2. Test (held-out) on per-passage LM embeddings of `indication_masked` (every QI / FLAVOR / CHANNEL / DIRECTION / TOXICITY token in the passage replaced with `[PROP]`).
3. The herb each passage refers to provides the gold label (via `canonical_id`).
4. Score: accuracy + macro-F1.
5. Per-axis bands below are the inference rules.

## Pre-registered predictions

| Axis      | Held-out macro-F1 prediction | Interpretation if confirmed                                       | Actual (fill after run) |
|-----------|------------------------------|-------------------------------------------------------------------|-------------------------|
| QI        | **≥ 0.55**                   | 寒/热 is grounded in felt experience (cold/hot is interoceptive). | _TBD_                   |
| FLAVOR    | **≥ 0.40**                   | Taste is partly experiential (sweet/bitter are felt).             | _TBD_                   |
| TOXICITY  | **≥ 0.50**                   | Toxicity has very salient experiential markers (vomiting etc.).   | _TBD_                   |
| CHANNEL   | **≤ 0.30**                   | 归经 is theoretical, not directly felt — should NOT transfer.     | _TBD_                   |
| DIRECTION | **≤ 0.25**                   | 升降浮沉 is even less felt; weakest expected transfer.            | _TBD_                   |

## Confirmatory criteria

- A prediction is **confirmed** when actual macro-F1 falls on the predicted side of the band.
- The two most informative single results:
  - **QI macro-F1 ≥ 0.55** would strongly support the embodied-cognition reading of the entire project.
  - **CHANNEL macro-F1 ≥ 0.50** would FALSIFY the "归经 is purely theoretical" claim, with major implications (channels may have a felt-experience substrate after all).

## What disconfirmation means

- If QI fails (< 0.40), the "interoceptive 寒/热" hypothesis loses; the descriptor may be a purely linguistic label.
- If CHANNEL succeeds (≥ 0.50), Lakoff-Johnson embodied-cognition framing extends further than expected — channels are felt in some way the modern reductive read denies.

## Surprise predictions (small bets)

- TOXICITY may UNDER-perform if the symptom corpus lacks acute-toxicity narratives (most clinical case records describe chronic conditions).
- DIRECTION may modestly out-perform if 升 (up-going) clusters with head/upper-body symptoms (dizziness, headache) — the spatial-cognition reading.

## How to populate the Actual column

After Task 16 (LM embeddings) and a sibling `scripts/07_embed_passages.py` produce
`data/processed/embeddings_passages.parquet`:

```bash
.venv/Scripts/python scripts/07_held_out_probe.py
```

Open `data/processed/held_out_probe_results.parquet`, find the row with the best
`train_variant` per axis, paste the macro-F1 into the Actual column. **Never** edit
the Prediction column.

## Interpretation (fill after run)

_TBD — paste here when Actuals are recorded._
