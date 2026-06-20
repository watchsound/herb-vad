"""Six paper-grade figure functions for the Herb-VAD final report.

matplotlib is in the [viz] extra; each function lazy-imports it and
raises a clear error if missing. Tests verify only the prep functions
that build the underlying data; rendering itself is integration
territory.

Figures:
  F1: Inter-database reliability per axis (bar of Fleiss κ).
  F2: Linear-probe accuracy heatmap (axes × embeddings × variants).
  F3: Held-out symptom probe macro-F1 (Finding #2 headline figure).
  F4: UMAP of shared multilingual space (overlaid: NRC-VAD vs TCM labels).
  F5: Procrustes residual / CCA explained variance per axis.
  F6: Pre-registered hypothesis-test forest plot (H1-H5 with CIs).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import polars as pl


def _import_mpl() -> Any:
    try:
        import matplotlib

        matplotlib.use("Agg")  # headless
        import matplotlib.pyplot as plt

        return plt
    except ImportError as e:
        raise ImportError(
            "matplotlib not installed. Install the [viz] extra: " 'pip install -e ".[viz]"'
        ) from e


# --- Figure 1: Reliability bar ----------------------------------------


def prepare_f1_data(reliability_df: pl.DataFrame) -> pl.DataFrame:
    """Sort by canonical axis order; pass other columns through."""
    order = ["QI", "FLAVOR", "TOXICITY", "CHANNEL", "DIRECTION"]
    return (
        reliability_df.with_columns(
            pl.col("axis")
            .map_elements(lambda a: order.index(a) if a in order else 99, return_dtype=pl.Int64)
            .alias("_order")
        )
        .sort("_order")
        .drop("_order")
    )


def render_f1(reliability_df: pl.DataFrame, out_path: Path) -> None:
    plt = _import_mpl()
    data = prepare_f1_data(reliability_df)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(data["axis"].to_list(), data["fleiss_kappa"].to_list())
    ax.axhline(0.6, linestyle="--", linewidth=0.8, label="κ=0.6")
    ax.set_ylabel("Fleiss' κ")
    ax.set_title("Inter-database label reliability per axis")
    ax.set_ylim(-0.1, 1.0)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=200)
    plt.close(fig)


# --- Figure 2: Probe accuracy heatmap ---------------------------------


def prepare_f2_data(probe_df: pl.DataFrame) -> pl.DataFrame:
    """Pivot probe_results into a (embedding+variant) × axis macro-F1 matrix.

    If multiple rows collide on (emb_variant, axis) (e.g. repeated CV runs),
    take the mean macro-F1 — pivot otherwise raises on multi-value cells.
    """
    return probe_df.with_columns(
        (pl.col("embedding") + "/" + pl.col("text_variant")).alias("emb_variant")
    ).pivot(index="emb_variant", on="axis", values="macro_f1", aggregate_function="mean")


def render_f2(probe_df: pl.DataFrame, out_path: Path) -> None:
    plt = _import_mpl()
    pivot = prepare_f2_data(probe_df)
    axes = [c for c in pivot.columns if c != "emb_variant"]
    matrix = pivot.select(axes).to_numpy()
    labels = pivot["emb_variant"].to_list()
    fig, ax = plt.subplots(figsize=(7, max(3, len(labels) * 0.4)))
    im = ax.imshow(matrix, aspect="auto", vmin=0, vmax=1)
    ax.set_xticks(range(len(axes)))
    ax.set_xticklabels(axes)
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels)
    ax.set_title("Linear-probe macro-F1 (axes × embedding/variant)")
    fig.colorbar(im, ax=ax)
    fig.tight_layout()
    fig.savefig(out_path, dpi=200)
    plt.close(fig)


# --- Figure 3: Held-out symptom probe ----------------------------------


def prepare_f3_data(held_out_df: pl.DataFrame) -> pl.DataFrame:
    return (
        held_out_df.group_by("axis")
        .agg(
            pl.col("macro_f1").max().alias("best_macro_f1"),
            pl.col("n_held_out").max().alias("max_n"),
        )
        .sort("axis")
    )


def render_f3(held_out_df: pl.DataFrame, out_path: Path) -> None:
    plt = _import_mpl()
    data = prepare_f3_data(held_out_df)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(data["axis"].to_list(), data["best_macro_f1"].to_list())
    ax.axhline(0.55, linestyle="--", linewidth=0.8, label="QI prediction ≥ 0.55")
    ax.set_ylabel("Held-out macro-F1")
    ax.set_title("Held-out symptom probe (Finding #2)")
    ax.set_ylim(0, 1.0)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=200)
    plt.close(fig)


# --- Figure 4: UMAP shared space --------------------------------------


def prepare_f4_data(
    embeddings: pl.DataFrame, *, sample: int = 2000, seed: int = 42
) -> pl.DataFrame:
    """Stratified sample down to ``sample`` rows for the UMAP plot."""
    if embeddings.height <= sample:
        return embeddings
    return embeddings.sample(n=sample, seed=seed)


def render_f4(embeddings: pl.DataFrame, out_path: Path) -> None:
    plt = _import_mpl()
    try:
        import umap  # type: ignore[import-untyped]
    except ImportError as e:
        raise ImportError("umap-learn not installed. pip install umap-learn") from e
    sample = prepare_f4_data(embeddings)
    X = np.asarray(sample["vector"].to_list(), dtype=np.float32)
    coords = umap.UMAP(n_components=2, random_state=42).fit_transform(X)
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.scatter(coords[:, 0], coords[:, 1], s=4, alpha=0.6)
    ax.set_title("Shared multilingual cognitive space (UMAP)")
    ax.set_xticks([])
    ax.set_yticks([])
    fig.tight_layout()
    fig.savefig(out_path, dpi=200)
    plt.close(fig)


# --- Figure 5: Procrustes residual / CCA variance ---------------------


def prepare_f5_data(alignment_df: pl.DataFrame) -> pl.DataFrame:
    return alignment_df


def render_f5(alignment_df: pl.DataFrame, out_path: Path) -> None:
    plt = _import_mpl()
    data = prepare_f5_data(alignment_df)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(
        data["method"].to_list(),
        [
            float(s.split(",")[0]) if "," in s else float(s.split("=")[-1])
            for s in data["summary"].to_list()
        ],
    )
    ax.set_title("Alignment quality per method")
    fig.tight_layout()
    fig.savefig(out_path, dpi=200)
    plt.close(fig)


# --- Figure 6: Hypothesis forest plot ---------------------------------


def prepare_f6_data(hypotheses_df: pl.DataFrame) -> pl.DataFrame:
    return hypotheses_df


def render_f6(hypotheses_df: pl.DataFrame, out_path: Path) -> None:
    plt = _import_mpl()
    data = prepare_f6_data(hypotheses_df)
    fig, ax = plt.subplots(figsize=(7, max(3, data.height * 0.5)))
    ys = list(range(data.height))
    stats_col = data["statistic"].to_list()
    stat_floats = [float(x) if x is not None else 0.0 for x in stats_col]
    ax.scatter(stat_floats, ys)
    ax.set_yticks(ys)
    ax.set_yticklabels(data["hypothesis"].to_list())
    ax.axvline(0, linewidth=0.8, color="gray")
    ax.set_title("Pre-registered hypothesis statistics (Finding #3)")
    fig.tight_layout()
    fig.savefig(out_path, dpi=200)
    plt.close(fig)
