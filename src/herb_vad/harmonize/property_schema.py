"""Convenience constants over the canonical property schema enums.

Other modules import these instead of re-listing axis names. The truth
table lives in ``herb_vad.schemas``.
"""

from __future__ import annotations

from herb_vad.schemas import (
    Channel,
    Direction,
    FiveFlavor,
    FourQi,
    PropertyAxis,
    Toxicity,
)

CANONICAL_AXES: tuple[str, ...] = tuple(a.value for a in PropertyAxis)

VALID_VALUES_BY_AXIS: dict[str, frozenset[str]] = {
    PropertyAxis.QI.value: frozenset(q.value for q in FourQi),
    PropertyAxis.FLAVOR.value: frozenset(f.value for f in FiveFlavor),
    PropertyAxis.CHANNEL.value: frozenset(c.value for c in Channel),
    PropertyAxis.DIRECTION.value: frozenset(d.value for d in Direction),
    PropertyAxis.TOXICITY.value: frozenset(t.value for t in Toxicity),
}
