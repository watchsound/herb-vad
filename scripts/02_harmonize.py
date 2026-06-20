"""End-to-end harmonization driver: ingest → canonical master → property_long → consensus.

Reads each source's interim parquet (skipping any that don't exist), builds the
canonical master table, joins, and writes:
  - data/interim/herb_master.parquet
  - data/interim/property_long.parquet
  - data/interim/property_consensus.parquet
"""

from __future__ import annotations

from pathlib import Path

import polars as pl

from herb_vad.harmonize.canonicalize import join_to_canonical
from herb_vad.harmonize.consensus import consensus_labels
from herb_vad.identity.canonical import build_canonical_table

INTERIM = Path("data/interim")
SOURCES = ["symmap", "tcmsp", "etcm", "batman", "herb_db"]


def _load_long() -> dict[str, pl.DataFrame]:
    out: dict[str, pl.DataFrame] = {}
    for src in SOURCES:
        path = INTERIM / f"{src}.parquet"
        if path.exists():
            out[src] = pl.read_parquet(path)
    return out


def main() -> None:
    longs = _load_long()
    if not longs:
        raise SystemExit(
            "No source parquets found in data/interim/. " "Run scripts/01_fetch_*.py first."
        )

    # Master canonical table: one row per unique herb.
    id_sources = {
        name: df.select(["chinese", "pinyin", "latin"]).unique() for name, df in longs.items()
    }
    master = build_canonical_table(id_sources)

    # Long-format property records keyed on canonical_id.
    property_long = pl.concat(
        [join_to_canonical(df, master) for df in longs.values()],
        how="vertical",
    )

    # Inter-source consensus.
    consensus = consensus_labels(property_long)

    INTERIM.mkdir(parents=True, exist_ok=True)
    master.write_parquet(INTERIM / "herb_master.parquet")
    property_long.write_parquet(INTERIM / "property_long.parquet")
    consensus.write_parquet(INTERIM / "property_consensus.parquet")
    print(
        f"herb_master: {master.height} canonical herbs\n"
        f"property_long: {property_long.height} (canonical_id, axis, value) rows\n"
        f"property_consensus: {consensus.height} consensus rows"
    )


if __name__ == "__main__":
    main()
