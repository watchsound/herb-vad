"""Run the linear-probe matrix over every (embedding x text_variant x axis).

Reads:
  - data/processed/embeddings_lm.parquet (and/or embeddings_cooc.parquet)
  - data/interim/property_consensus.parquet

Writes:
  - data/processed/probe_results.parquet (one row per probe)

Skips combinations where the embedding x variant rows don't exist.
"""

from __future__ import annotations

from pathlib import Path

import polars as pl

from herb_vad.probes.dataset import MULTI_VALUED, SINGLE_VALUED, assemble
from herb_vad.probes.linear import probe_dataset

EMB_LM = Path("data/processed/embeddings_lm.parquet")
EMB_COOC = Path("data/processed/embeddings_cooc.parquet")
CONSENSUS = Path("data/interim/property_consensus.parquet")
OUT = Path("data/processed/probe_results.parquet")


def _load_embeddings() -> pl.DataFrame | None:
    parts: list[pl.DataFrame] = []
    if EMB_LM.exists():
        parts.append(pl.read_parquet(EMB_LM))
    if EMB_COOC.exists():
        parts.append(pl.read_parquet(EMB_COOC))
    return pl.concat(parts, how="vertical") if parts else None


def main() -> None:
    embeddings = _load_embeddings()
    if embeddings is None:
        raise SystemExit("No embeddings found. Run scripts/05_embed_*.py first.")
    if not CONSENSUS.exists():
        raise SystemExit(f"Missing {CONSENSUS}. Run scripts/02_harmonize.py first.")
    labels = pl.read_parquet(CONSENSUS)

    rows: list[dict] = []
    for emb_name in embeddings["embedding"].unique().to_list():
        variants = (
            embeddings.filter(pl.col("embedding") == emb_name)["text_variant"].unique().to_list()
        )
        for variant in variants:
            for axis in sorted(SINGLE_VALUED | MULTI_VALUED):
                try:
                    ds = assemble(
                        embeddings,
                        labels,
                        axis=axis,
                        embedding_name=emb_name,
                        text_variant=variant,
                    )
                    if ds.X.shape[0] < 10:
                        continue
                    result = probe_dataset(ds)
                    rows.append(
                        {
                            "embedding": emb_name,
                            "text_variant": variant,
                            "axis": axis,
                            "accuracy": result.accuracy,
                            "macro_f1": result.macro_f1,
                            "n": result.n,
                            "cv_folds": result.cv_folds,
                            "held_out_symptom": result.held_out_symptom,
                        }
                    )
                except ValueError as e:
                    print(f"skipping ({emb_name}, {variant}, {axis}): {e}")

    out = pl.DataFrame(rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.write_parquet(OUT)
    print(f"Wrote {OUT}: {out.height} probe results.")


if __name__ == "__main__":
    main()
