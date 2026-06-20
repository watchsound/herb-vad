"""Compute per-axis inter-database reliability.

Reads data/interim/property_long.parquet (produced by
scripts/02_harmonize.py), writes data/interim/reliability_per_axis.parquet,
and prints a one-line summary per axis. Pre-registered predictions live in
docs/findings/01_label_reliability.md - DO NOT edit the prediction column
of that document; fill in the actuals next to the predictions instead.

Reports BOTH:
- Raw set-equality agreement (robust to ragged rater coverage; works
  with any number of sources >= 2).
- Fleiss kappa (requires equal raters per subject; degrades gracefully
  to empty rows when the assumption fails).
"""

from __future__ import annotations

from pathlib import Path

import polars as pl

from herb_vad.analysis.reliability import fleiss_per_axis, raw_agreement_per_axis

LONG = Path("data/interim/property_long.parquet")
OUT = Path("data/interim/reliability_per_axis.parquet")


def main() -> None:
    if not LONG.exists():
        raise SystemExit(f"Missing {LONG}. Run scripts/02_harmonize.py first.")
    long = pl.read_parquet(LONG)

    agreement = raw_agreement_per_axis(long)
    kappa = fleiss_per_axis(long)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    agreement.write_parquet(OUT)

    print("Raw set-equality agreement per axis:")
    for row in agreement.iter_rows(named=True):
        pct = row["raw_agreement"] * 100
        print(
            f"  {row['axis']:<10s}  "
            f"{row['n_herbs_agree']:>4d}/{row['n_herbs_eligible']:<4d}  "
            f"{pct:5.1f}%"
        )
    if kappa.height > 0:
        print()
        print("Fleiss kappa (where equal-rater assumption holds):")
        for row in kappa.iter_rows(named=True):
            print(
                f"  {row['axis']:<10s}  k = {row['fleiss_kappa']:+.3f}  "
                f"(n_herbs={row['n_herbs']}, n_classes={row['n_classes']})"
            )


if __name__ == "__main__":
    main()
