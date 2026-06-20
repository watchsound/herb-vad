# herb-vad

Cognitive cartography of classical Chinese-medicine herb descriptors. We test whether 四气 / 五味 / 升降浮沉 / 归经 / 毒性 form a recoverable low-dimensional coordinate system over interoceptive-cognitive space — applying the NLP-VAD (Valence / Arousal / Dominance) methodological protocol to TCM, then geometrically cross-walking the recovered space with the NLP affective space. See [`herb-VAD.md`](herb-VAD.md) for the underlying concept and [`docs/plan.md`](docs/plan.md) for the implementation plan.

## Layout

```
src/herb_vad/   # canonical schemas + ingest + identity + harmonize + embeddings + probes + crosswalk + analysis
tests/          # unit + fixture data
scripts/        # 01..11 step-numbered driver scripts (run in order; each fails clean if its inputs are absent)
docs/           # plan.md, paper_outline.md, findings/, decisions/, figures/
data/           # raw / interim / processed (gitignored; .gitkeep sentinels in git)
```

## Reproducing the pipeline

1. `pip install -e ".[dev,ml,viz,data]"` (Tsinghua mirror recommended for `pypi.org`-unreachable networks)
2. Place public source dumps under `data/raw/<source>/` as described in each `scripts/01_fetch_*.py` docstring.
3. Run in order: `scripts/01_*` (ingest) → `scripts/02_harmonize.py` → `scripts/03_reliability.py` → `scripts/04_build_text_repr.py` → `scripts/05_*` (embeddings) → `scripts/06_probe.py` → `scripts/07_held_out_probe.py` → `scripts/08_embed_vad.py` → `scripts/09_crosswalk.py` → `scripts/10_crosswalk_hypotheses.py` → `scripts/11_figures.py`.

## Citation

See `CITATION.cff`.

## License

MIT — see `LICENSE`.
