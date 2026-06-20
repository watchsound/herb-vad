"""Identity normalization: pinyin, Chinese name, Latin binomial.

Cross-database identity matching collapses to (chinese_norm,
pinyin_norm, latin_norm) — none alone is reliable, the trio together
beats any single criterion. Keep these pure-function helpers small and
zero-dependency so they can be reused everywhere.
"""

from __future__ import annotations

import re
import unicodedata

_PUNCT_RE = re.compile(r"[\s\-_'\"·]+")
_LATIN_AUTHORITY_RE = re.compile(r"\s+(?:[A-Z][A-Za-z.]*\.|[A-Z][A-Za-z]+|et al\.?|ex|var\.).*$")


def _strip_tone_marks(text: str) -> str:
    """Remove combining diacritics; preserve base letters."""
    decomposed = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def normalize_pinyin(s: str | None) -> str:
    if not s:
        return ""
    t = _strip_tone_marks(str(s)).lower()
    t = t.replace("ü", "u").replace("v", "u")
    return _PUNCT_RE.sub("", t)


def normalize_chinese(s: str | None) -> str:
    if not s:
        return ""
    t = unicodedata.normalize("NFKC", str(s))
    return _PUNCT_RE.sub("", t)


def normalize_latin(s: str | None) -> str:
    """Lowercase, collapse whitespace, strip taxonomic authority suffix.

    The authority suffix is everything from the first capitalized
    author-style token onwards (e.g. "C. A. Meyer", "Debx.", "L.").
    We are deliberately conservative — if no authority is detected the
    full string passes through.
    """
    if not s:
        return ""
    t = str(s).strip()
    t = _LATIN_AUTHORITY_RE.sub("", t)
    t = re.sub(r"\s+", " ", t).lower()
    return t
