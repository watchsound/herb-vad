"""Parser for Chinese Pharmacopoeia 2020 English edition (Volume 1).

Each herb monograph in ChP 2020 has structured fields:

  [Herb Latin name] (e.g. "Aconiti Radix Lateralis Praeparata")
  (Chinese characters, Pinyin)

  Property and Flavor [QI]; [FLAVOR(s)]; [TOXICITY (optional)].
  Meridian tropism [CHANNEL(s)] meridians.

This module turns extracted PDF text from
``data/raw/pharmacopoeia/*.txt`` into canonical property records over
QI / FLAVOR / CHANNEL / TOXICITY. (The Pharmacopoeia does NOT publish
升降浮沉 / direction as a structured field, so DIRECTION remains
gapped.)

The fetch script extracts the PDF text via pypdf; this module assumes
the text is already on disk. Extraction is deliberately a separate
step because pypdf walks the 1.7 GB PDF in ~2 minutes — we cache once.
"""

from __future__ import annotations

import re
from pathlib import Path

import polars as pl

from herb_vad.ingest.symmap import CHANNEL_MAP, FLAVOR_MAP, QI_MAP, TOX_MAP

# Regexes
_PROP_FLAVOR_RE = re.compile(r"Property\s+and\s+Flavor[s]?\s+([^.\n]+?)\.", re.IGNORECASE)
_MERIDIAN_RE = re.compile(
    r"Meridian\s+[tT]ropism\s+([^.\n]+?)(?:\s+meridian[s]?)?\.", re.IGNORECASE
)
# A herb name is typically 2-4 capitalized Latin words just before
# Property/Source/Description. Allow some noise inside (e.g. ", ", ",
# ", or page wrap). Greedy backward match.
_HERB_NAME_RE = re.compile(r"([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){1,4})\s*(?:\([^)]{1,100}\))?")


def _parse_property_flavor(value: str) -> tuple[str | None, list[str], str | None]:
    """Split the ``Property and Flavor`` line into qi / flavors / toxicity.

    Format: ``[qi]; [flavor1, flavor2, ...]; [toxicity-clause].``
    Toxicity clause is present only when the trailing ``;``-segment
    contains the word ``toxic``.
    """
    segs = [seg.strip() for seg in re.split(r"[;]\s*", value) if seg.strip()]
    if not segs:
        return None, [], None

    qi_token = segs[0].lower().strip(" ·,")
    qi = QI_MAP.get(qi_token)

    flavors: list[str] = []
    toxicity: str | None = None

    for seg in segs[1:]:
        seg_l = seg.lower()
        if "toxic" in seg_l:
            tox = TOX_MAP.get(seg_l.strip().rstrip(",.").strip())
            if not tox:
                if "non-toxic" in seg_l or "nontoxic" in seg_l:
                    tox = "none"
                elif "highly toxic" in seg_l or "very toxic" in seg_l:
                    tox = "severe"
                elif "slightly toxic" in seg_l or "mild" in seg_l:
                    tox = "slight"
                elif "toxic" in seg_l:
                    tox = "moderate"
            toxicity = tox
            continue
        # FLAVOR list — split on commas and "and"
        for tok in re.split(r",\s*|\s+and\s+", seg):
            tok = tok.strip().lower().strip(" ·,")
            if not tok:
                continue
            mapped = FLAVOR_MAP.get(tok)
            if mapped:
                flavors.append(mapped)
    return qi, flavors, toxicity


def _parse_meridian(value: str) -> list[str]:
    """Split ``Meridian tropism`` value into canonical channels."""
    value = re.sub(r"\s+", " ", value).strip()
    # Remove trailing "meridian(s)" if present
    value = re.sub(r"\s+meridian[s]?\s*$", "", value, flags=re.IGNORECASE)
    channels: list[str] = []
    for tok in re.split(r",\s*|\s+and\s+", value):
        tok = tok.strip().lower().rstrip(",.")
        if not tok:
            continue
        # Sometimes the token still has " meridian" appended
        tok = re.sub(r"\s+meridian[s]?\s*$", "", tok)
        mapped = CHANNEL_MAP.get(tok)
        if mapped:
            channels.append(mapped)
    return channels


def _herb_name_before(text: str, pos: int, window: int = 600) -> str | None:
    """Find the closest Latin-binomial-like heading before ``pos``."""
    start = max(0, pos - window)
    chunk = text[start:pos]
    candidates = list(_HERB_NAME_RE.finditer(chunk))
    if not candidates:
        return None
    # Take the last (closest) match; skip generic field names.
    for m in reversed(candidates):
        name = re.sub(r"\s+", " ", m.group(1)).strip()
        upper = name.lower()
        if any(
            upper.startswith(skip)
            for skip in (
                "property and",
                "meridian tropism",
                "actions",
                "indications",
                "administration",
                "precautions",
                "description",
                "identification",
                "storage",
                "assay",
                "water",
                "total ash",
                "extractives",
                "source",
                "preparation",
                "the drug",
            )
        ):
            continue
        return name
    return None


def parse_pharmacopoeia_text(text: str) -> pl.DataFrame:
    """Extract property records from concatenated Pharmacopoeia text.

    Each match of ``Property and Flavor ...`` becomes one or more rows
    keyed on the closest preceding herb-name candidate.
    """
    rows: list[dict[str, object]] = []
    seen_herbs: set[str] = set()

    for m in _PROP_FLAVOR_RE.finditer(text):
        prop_value = m.group(1)
        herb = _herb_name_before(text, m.start())
        if not herb:
            continue
        # De-duplicate per herb — Pharmacopoeia often has multiple
        # processed-form sub-entries per parent herb.
        if herb in seen_herbs:
            continue
        seen_herbs.add(herb)

        qi, flavors, toxicity = _parse_property_flavor(prop_value)
        base = {
            "chinese": None,
            "pinyin": None,
            "latin": herb,
            "source": "pharmacopoeia",
        }
        if qi:
            rows.append({**base, "axis": "QI", "value": qi})
        for f in flavors:
            rows.append({**base, "axis": "FLAVOR", "value": f})
        if toxicity:
            rows.append({**base, "axis": "TOXICITY", "value": toxicity})

        # Find the Meridian tropism within the next ~600 chars
        tail = text[m.end() : m.end() + 600]
        m2 = _MERIDIAN_RE.search(tail)
        if m2:
            for ch in _parse_meridian(m2.group(1)):
                rows.append({**base, "axis": "CHANNEL", "value": ch})

    return pl.DataFrame(rows)


def parse_pharmacopoeia_files(text_paths: list[Path]) -> pl.DataFrame:
    """Concatenate multiple cached PDF-text files and parse."""
    chunks = [p.read_text(encoding="utf-8") for p in text_paths if p.exists()]
    return parse_pharmacopoeia_text("\n".join(chunks))
