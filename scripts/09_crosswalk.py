"""Run Procrustes and CCA alignment between passage embeddings and the
NRC-VAD-derived score vectors.

Reads:
  - data/processed/embeddings_passages.parquet
  - data/interim/nrc_vad_en.parquet (also data/interim/cvaw.parquet if present)

Writes:
  - data/processed/crosswalk_alignment.parquet (per-method, per-axis-pair stats)
"""

from __future__ import annotations

from pathlib import Path

import polars as pl

from herb_vad.crosswalk.align import cca_align, procrustes_align
from herb_vad.crosswalk.parallel_pairs import build_parallel_pairs

EMB_PASSAGES = Path("data/processed/embeddings_passages.parquet")
NRC_VAD = Path("data/interim/nrc_vad_en.parquet")
CVAW = Path("data/interim/cvaw.parquet")
OUT = Path("data/processed/crosswalk_alignment.parquet")


def main() -> None:
    if not EMB_PASSAGES.exists():
        raise SystemExit(f"Missing {EMB_PASSAGES}. Build passage embeddings first.")
    passages = pl.read_parquet(EMB_PASSAGES)

    if not NRC_VAD.exists():
        raise SystemExit(f"Missing {NRC_VAD}. Run scripts/01_parse_nrc_vad.py first.")
    nrc = pl.read_parquet(NRC_VAD)
    lex = nrc
    if CVAW.exists():
        cvaw = pl.read_parquet(CVAW).select(["term", "valence", "arousal", "dominance"])
        lex = pl.concat(
            [nrc.select(["term", "valence", "arousal", "dominance"]), cvaw], how="vertical"
        )

    X, Y, ids = build_parallel_pairs(passages, lex)
    print(f"Parallel pairs: {len(ids)}; X shape {X.shape}; Y shape {Y.shape}")
    if X.shape[0] < 20:
        raise SystemExit("Too few parallel pairs (< 20) for stable alignment.")

    # CCA: project both sides into the shared 3-dim VAD space
    cca = cca_align(X, Y, n_components=3)
    print(f"CCA component correlations: {cca.correlations.round(3).tolist()}")

    # Procrustes: only meaningful if X and Y are the same dim. We project
    # X down to 3 dims via the CCA's X side first.
    proc = procrustes_align(cca.X_c, cca.Y_c)
    print(f"Procrustes residual on CCA-projected space: {proc.residual:.4f}")

    pl.DataFrame(
        {
            "method": ["cca", "procrustes"],
            "n_pairs": [len(ids), len(ids)],
            "summary": [
                ",".join(f"{c:.3f}" for c in cca.correlations),
                f"residual={proc.residual:.4f}",
            ],
        }
    ).write_parquet(OUT)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
