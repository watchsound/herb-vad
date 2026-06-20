"""Run the held-out symptom probe per axis x embedding model.

Reads:
  - data/processed/embeddings_lm.parquet            (herb-level: definition, concat)
  - data/processed/embeddings_passages.parquet      (passage-level: indication_masked)
  - data/interim/property_consensus.parquet

Writes:
  - data/processed/held_out_probe_results.parquet

The passages parquet is produced by an unnamed future task
(``scripts/07_embed_passages.py``) — out of scope for Task 20. This
driver fails clean if it doesn't exist.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import polars as pl

from herb_vad.probes.dataset import SINGLE_VALUED, assemble
from herb_vad.probes.held_out_symptom import (
    HeldOutProbeInputs,
    held_out_probe,
    join_passages_to_labels,
)

EMB_HERB = Path("data/processed/embeddings_lm.parquet")
EMB_PASSAGES = Path("data/processed/embeddings_passages.parquet")
CONSENSUS = Path("data/interim/property_consensus.parquet")
OUT = Path("data/processed/held_out_probe_results.parquet")


def _vectorize(
    passages_with_labels: pl.DataFrame, classes: list[str]
) -> tuple[np.ndarray, np.ndarray]:
    X = np.asarray(passages_with_labels["vector"].to_list(), dtype=np.float32)
    cidx = {c: i for i, c in enumerate(classes)}
    y = np.asarray(
        [cidx[v] for v in passages_with_labels["consensus_value"].to_list()], dtype=np.int64
    )
    return X, y


def main() -> None:
    for p in (EMB_HERB, EMB_PASSAGES, CONSENSUS):
        if not p.exists():
            raise SystemExit(f"Missing {p}. Build embeddings + consensus first.")
    herb_emb = pl.read_parquet(EMB_HERB)
    passage_emb = pl.read_parquet(EMB_PASSAGES)
    labels = pl.read_parquet(CONSENSUS)

    rows: list[dict] = []
    for emb_name in herb_emb["embedding"].unique().to_list():
        for train_variant in ("definition", "concat"):
            for axis in sorted(SINGLE_VALUED):  # symptom probe only over single-label axes
                ds_train = assemble(
                    herb_emb, labels, axis=axis, embedding_name=emb_name, text_variant=train_variant
                )
                if ds_train.X.shape[0] < 20:
                    continue
                joined = join_passages_to_labels(
                    passage_emb.filter(pl.col("embedding") == emb_name).filter(
                        pl.col("text_variant") == "indication_masked"
                    ),
                    labels,
                    axis=axis,
                )
                # Restrict held-out labels to the train-set's class set
                joined = joined.filter(pl.col("consensus_value").is_in(ds_train.classes))
                if joined.height < 20:
                    continue
                X_held, y_held = _vectorize(joined, ds_train.classes)
                result = held_out_probe(
                    HeldOutProbeInputs(
                        X_train=ds_train.X,
                        y_train=ds_train.y,
                        X_held_out=X_held,
                        y_held_out=y_held,
                        is_multilabel=False,
                    ),
                    axis=axis,
                    embedding_name=emb_name,
                )
                rows.append(
                    {
                        "embedding": emb_name,
                        "train_variant": train_variant,
                        "axis": axis,
                        "accuracy": result.accuracy,
                        "macro_f1": result.macro_f1,
                        "n_held_out": result.n,
                    }
                )

    out = pl.DataFrame(rows)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.write_parquet(OUT)
    print(f"Wrote {OUT}: {out.height} (embedding x train_variant x axis) results.")


if __name__ == "__main__":
    main()
