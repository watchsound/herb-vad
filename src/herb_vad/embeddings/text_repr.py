"""Build the four text representations per canonical herb.

Variants:
  - definition: classical Materia Medica snippet (from
    data/interim/classical_paragraphs.parquet) or a fallback identity
    string when no classical hit is found.
  - indication: passages from the classical corpus and PubMed-zh that
    mention the herb AND >=1 symptom term from the curated vocab.
  - concat: definition + "\\n\\n" + indication.
  - indication_masked: indication with every property-vocab token
    replaced by "[PROP]". This is the substrate for Task 20.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import polars as pl

from herb_vad.embeddings.property_vocab import PROPERTY_REGEX
from herb_vad.ingest.symptom_vocab import SYMPTOM_TERMS
from herb_vad.ingest.symptom_vocab_en import SYMPTOM_TERMS_EN

_BILINGUAL_SYMPTOM_TERMS: tuple[str, ...] = tuple(list(SYMPTOM_TERMS) + list(SYMPTOM_TERMS_EN))

MASK_TOKEN = "[PROP]"


@dataclass(frozen=True)
class HerbTexts:
    canonical_id: str
    definition: str
    indication: str
    concat: str
    indication_masked: str


def mask_property_keywords(text: str) -> str:
    return PROPERTY_REGEX.sub(MASK_TOKEN, text)


def _mentions_herb(passage: str, names: Iterable[str]) -> bool:
    """Return True if any of ``names`` occurs in ``passage``.

    For ASCII names (pinyin / latin) we lowercase both sides AND strip
    internal whitespace so that pinyin like "renshen" matches a passage
    that writes "Ren Shen". For Chinese names we match the raw bytes.
    """
    passage_ascii_norm = "".join(ch for ch in passage.lower() if not ch.isspace())
    for n in names:
        if not n:
            continue
        if all(ord(c) < 128 for c in n):
            n_norm = "".join(ch for ch in n.lower() if not ch.isspace())
            if n_norm and n_norm in passage_ascii_norm:
                return True
        else:
            if n in passage:
                return True
    return False


def _mentions_symptom(passage: str, symptoms: Iterable[str] = _BILINGUAL_SYMPTOM_TERMS) -> bool:
    """Detect a TCM symptom mention in a passage.

    Defaults to the bilingual vocab (ZH terms substring-match raw text;
    EN terms substring-match the lowercased version) so both classical
    Chinese passages and PubMed English abstracts are eligible.
    """
    lower = passage.lower()
    for s in symptoms:
        if any("\u4e00" <= c <= "\u9fff" for c in s):
            if s in passage:
                return True
        else:
            if s in lower:
                return True
    return False


def build_for_herb(
    canonical_id: str,
    *,
    chinese: str,
    pinyin: str,
    latin: str | None,
    corpus: pl.DataFrame,
) -> HerbTexts:
    """Build all four variants for a single canonical herb.

    ``corpus`` is the concatenation of classical_paragraphs.parquet +
    pubmed_tcm.parquet (the caller decides what to feed in). It must
    have ``text`` and ``source`` columns.
    """
    names = (chinese or "", pinyin or "", latin or "")
    # Definition: classical paragraphs that mention the herb (no symptom requirement)
    definition_rows = corpus.filter(pl.col("source") == "ctext").filter(
        pl.col("text").map_elements(
            lambda t, names=names: _mentions_herb(t, names),
            return_dtype=pl.Boolean,
        )
    )
    definition = "\n".join(definition_rows["text"].to_list())
    if not definition:
        definition = f"{chinese} {pinyin} {latin or ''}".strip()

    # Indication: any source, must mention herb AND at least one symptom term
    indication_rows = corpus.filter(
        pl.col("text").map_elements(
            lambda t, names=names: _mentions_herb(t, names) and _mentions_symptom(t),
            return_dtype=pl.Boolean,
        )
    )
    indication = "\n".join(indication_rows["text"].to_list())

    concat = (definition + "\n\n" + indication).strip()
    indication_masked = mask_property_keywords(indication)

    return HerbTexts(
        canonical_id=canonical_id,
        definition=definition,
        indication=indication,
        concat=concat,
        indication_masked=indication_masked,
    )


def build_all(master: pl.DataFrame, corpus: pl.DataFrame) -> pl.DataFrame:
    """Build the 4-variant table for every canonical herb in ``master``."""
    rows: list[dict[str, str]] = []
    for r in master.iter_rows(named=True):
        t = build_for_herb(
            canonical_id=r["canonical_id"],
            chinese=r.get("chinese_norm") or "",
            pinyin=r.get("pinyin_norm") or "",
            latin=r.get("latin_norm") or "",
            corpus=corpus,
        )
        rows.append(
            {
                "canonical_id": t.canonical_id,
                "definition": t.definition,
                "indication": t.indication,
                "concat": t.concat,
                "indication_masked": t.indication_masked,
            }
        )
    return pl.DataFrame(rows)
