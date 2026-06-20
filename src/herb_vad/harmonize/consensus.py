"""Per-axis consensus voting + agreement scoring.

For single-valued axes (QI, TOXICITY, DIRECTION) ``consensus_value`` is
the modal value; ``agreement`` is votes_for_consensus / total_sources_voting.

For multi-valued axes (FLAVOR, CHANNEL) every distinct value is emitted
as its own row; ``agreement`` is sources_that_used_value /
sources_that_voted_on_axis. (This treats each value as an independent
"yes/no" annotation rather than forcing a single winning value.)
"""

from __future__ import annotations

import polars as pl


def consensus_labels(long: pl.DataFrame) -> pl.DataFrame:
    # sources_per_axis = how many distinct sources gave any opinion on this axis
    sources_per_axis = long.group_by(["canonical_id", "axis"]).agg(
        pl.col("source").n_unique().alias("axis_n_sources")
    )

    votes = long.group_by(["canonical_id", "axis", "value"]).agg(
        pl.col("source").n_unique().alias("votes")
    )

    joined = votes.join(sources_per_axis, on=["canonical_id", "axis"], how="left")
    joined = joined.with_columns((pl.col("votes") / pl.col("axis_n_sources")).alias("agreement"))

    # Single-valued axes collapse to one row per (canonical_id, axis); take the modal value,
    # ties broken alphabetically for determinism.
    # Multi-valued axes (FLAVOR, CHANNEL) keep one row per value.
    single = {"QI", "TOXICITY", "DIRECTION"}

    def _modal_picker(group: pl.DataFrame) -> pl.DataFrame:
        return group.sort(["votes", "value"], descending=[True, False]).head(1)

    single_subset = joined.filter(pl.col("axis").is_in(single))
    if single_subset.height == 0:
        # Polars' group_by + map_groups raises ComputeError on an empty frame;
        # keep an empty-but-correctly-shaped placeholder so concat survives.
        single_picked = single_subset
    else:
        single_picked = single_subset.group_by(
            ["canonical_id", "axis"], maintain_order=True
        ).map_groups(_modal_picker)

    # For single-valued axes, n_sources reports the total voters on the axis
    # (so the reader sees how many sources weighed in, not just how many agreed).
    single_rows = single_picked.select(
        [
            "canonical_id",
            "axis",
            pl.col("value").alias("consensus_value"),
            "agreement",
            pl.col("axis_n_sources").alias("n_sources"),
        ]
    )

    # For multi-valued axes, each distinct value is its own row and n_sources
    # is the count of sources that asserted that value.
    multi_rows = joined.filter(~pl.col("axis").is_in(single)).select(
        [
            "canonical_id",
            "axis",
            pl.col("value").alias("consensus_value"),
            "agreement",
            pl.col("votes").alias("n_sources"),
        ]
    )

    return pl.concat([single_rows, multi_rows], how="vertical")
