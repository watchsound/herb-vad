"""Compute per-axis inter-database reliability.

Reads data/interim/property_long.parquet (produced by
scripts/02_harmonize.py), writes data/interim/reliability_per_axis.parquet,
and prints a one-line summary per axis. Pre-registered predictions live in
docs/findings/01_label_reliability.md - DO NOT edit the prediction column
of that document; fill in the actuals next to the predictions instead.
"""

from __future__ import annotations

from pathlib import Path

import polars as pl

from herb_vad.analysis.reliability import fleiss_per_axis

LONG = Path("data/interim/property_long.parquet")
OUT = Path("data/interim/reliability_per_axis.parquet")


def main() -> None:
    if not LONG.exists():
        raise SystemExit(f"Missing {LONG}. Run scripts/02_harmonize.py first.")
    long = pl.read_parquet(LONG)
    out = fleiss_per_axis(long)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.write_parquet(OUT)
    print("Per-axis Fleiss' kappa:")
    for row in out.iter_rows(named=True):
        print(
            f"  {row['axis']:<10s}  k = {row['fleiss_kappa']:+.3f}  "
            f"(n_herbs={row['n_herbs']}, n_classes={row['n_classes']})"
        )


if __name__ == "__main__":
    main()
