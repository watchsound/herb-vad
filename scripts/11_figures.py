"""Render all six figures to docs/figures/.

Requires the [viz] extra:
    pip install -e ".[viz]"

Each figure-renderer fails clean if its input parquet doesn't exist.
"""

from __future__ import annotations

from pathlib import Path

import polars as pl

from herb_vad.analysis.figures import (
    render_f1,
    render_f2,
    render_f3,
    render_f4,
    render_f5,
    render_f6,
)

INPUTS = {
    "f1_reliability": Path("data/interim/reliability_per_axis.parquet"),
    "f2_probes": Path("data/processed/probe_results.parquet"),
    "f3_held_out": Path("data/processed/held_out_probe_results.parquet"),
    "f4_embeddings": Path("data/processed/embeddings_lm.parquet"),
    "f5_alignment": Path("data/processed/crosswalk_alignment.parquet"),
    "f6_hypotheses": Path("data/processed/crosswalk_hypotheses_results.parquet"),
}
OUT_DIR = Path("docs/figures")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    missing = [name for name, path in INPUTS.items() if not path.exists()]
    if missing:
        print(f"Skipping figures with missing inputs: {missing}")
    if INPUTS["f1_reliability"].exists():
        render_f1(pl.read_parquet(INPUTS["f1_reliability"]), OUT_DIR / "f1_reliability.png")
    if INPUTS["f2_probes"].exists():
        render_f2(pl.read_parquet(INPUTS["f2_probes"]), OUT_DIR / "f2_probe_heatmap.png")
    if INPUTS["f3_held_out"].exists():
        render_f3(pl.read_parquet(INPUTS["f3_held_out"]), OUT_DIR / "f3_held_out.png")
    if INPUTS["f4_embeddings"].exists():
        render_f4(pl.read_parquet(INPUTS["f4_embeddings"]), OUT_DIR / "f4_umap.png")
    if INPUTS["f5_alignment"].exists():
        render_f5(pl.read_parquet(INPUTS["f5_alignment"]), OUT_DIR / "f5_alignment.png")
    if INPUTS["f6_hypotheses"].exists():
        render_f6(pl.read_parquet(INPUTS["f6_hypotheses"]), OUT_DIR / "f6_hypotheses.png")
    print(f"Wrote figures to {OUT_DIR}")


if __name__ == "__main__":
    main()
