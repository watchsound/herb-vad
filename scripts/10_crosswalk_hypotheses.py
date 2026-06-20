"""Run the five pre-registered cross-walk hypotheses.

Reads:
  - data/processed/embeddings_passages.parquet (with VAD aggregates)
  - data/processed/vad_embeddings.parquet
  - data/processed/crosswalk_alignment.parquet (CCA correlations per axis)

Writes:
  - data/processed/crosswalk_hypotheses_results.parquet
  - prints a multi-comparison-corrected summary

This is intentionally a thin script: the heavy lifting is in
``herb_vad.crosswalk.hypotheses``. The driver only assembles the
matrices and dispatches.
"""

from __future__ import annotations

from pathlib import Path

import polars as pl

from herb_vad.crosswalk.hypotheses import bonferroni_holm  # noqa: F401  (used post-real-run)

REQUIRED = [
    Path("data/processed/embeddings_passages.parquet"),
    Path("data/processed/vad_embeddings.parquet"),
    Path("data/processed/crosswalk_alignment.parquet"),
]
OUT = Path("data/processed/crosswalk_hypotheses_results.parquet")


def main() -> None:
    missing = [p for p in REQUIRED if not p.exists()]
    if missing:
        raise SystemExit(f"Missing inputs: {missing}. Build them first.")
    # Real assembly is non-trivial; this driver is a placeholder
    # for the actual data-shaping that lands once Tasks 16, 21, 22 produce
    # real artifacts. We export a stub schema so downstream reporting
    # (Task 24's figures) can pin against it.
    pl.DataFrame(
        {
            "hypothesis": ["H1", "H2", "H3", "H4", "H5"],
            "result": ["pending"] * 5,
            "statistic": [None] * 5,
            "p_value": [None] * 5,
            "n": [None] * 5,
        }
    ).write_parquet(OUT)
    print(f"Wrote {OUT} (stub; populate after Tasks 16/21/22 land real artifacts).")
    print("After real run:")
    print("  rej = bonferroni_holm([p1, p2, p3, p4, p5], alpha=0.01)")


if __name__ == "__main__":
    main()
