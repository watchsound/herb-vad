"""Chinese Text Project (https://ctext.org) bulk paragraph fetcher.

ctext exposes a public JSON endpoint at https://api.ctext.org/gettext
that returns paragraph-level text for a given URN. This module is a
thin client around that endpoint plus a parser that turns the JSON
into a polars frame of (doc_id, source, urn, paragraph_index, text).

Network use is opt-in: ``fetch_text`` is called only by the
``scripts/01_fetch_classical.py`` driver and is mocked out in unit
tests via dependency injection.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Callable

import polars as pl
import requests  # type: ignore[import-untyped]

CTEXT_API = "https://api.ctext.org/gettext"

# URN registry: classical texts whose passages we want indexed.
# Extend this list when new corpora are added — keep keys stable so
# downstream artifacts can pin to a known set.
CTEXT_URNS: dict[str, str] = {
    "shen-nong-ben-cao-jing": "ctp:shen-nong-ben-cao-jing",
    "ben-cao-gang-mu": "ctp:ben-cao-gang-mu",
    "shang-han-lun": "ctp:shang-han-lun",
    "jin-gui-yao-lue": "ctp:jin-gui-yao-lue",
}


def fetch_text(urn: str, *, session: requests.Session | None = None, sleep: float = 1.0) -> dict:
    """Hit the ctext gettext endpoint for a URN; return the parsed JSON."""
    sess = session or requests.Session()
    resp = sess.get(CTEXT_API, params={"urn": urn}, timeout=30)
    resp.raise_for_status()
    time.sleep(sleep)  # be polite to ctext.org
    return resp.json()


def parse_ctext_response(doc_id: str, payload: dict) -> pl.DataFrame:
    """Turn a ctext JSON payload into a (doc_id, urn, paragraph_index, text) frame.

    The payload's exact shape varies; we accept either a top-level
    ``fulltext`` list-of-paragraphs (string elements) or a ``contents``
    list of ``{text: ...}`` dicts. Anything else is treated as no
    paragraphs (and returns an empty frame), which keeps the caller
    defensive without raising.
    """
    paragraphs: list[str] = []
    if isinstance(payload.get("fulltext"), list):
        for el in payload["fulltext"]:
            if isinstance(el, str) and el.strip():
                paragraphs.append(el.strip())
    elif isinstance(payload.get("contents"), list):
        for el in payload["contents"]:
            if isinstance(el, dict) and isinstance(el.get("text"), str) and el["text"].strip():
                paragraphs.append(el["text"].strip())

    return pl.DataFrame(
        {
            "doc_id": [doc_id] * len(paragraphs),
            "source": ["ctext"] * len(paragraphs),
            "urn": [payload.get("urn", "")] * len(paragraphs),
            "paragraph_index": list(range(len(paragraphs))),
            "text": paragraphs,
        }
    )


def fetch_all(
    fetcher: Callable[[str], dict] = fetch_text,
    cache_dir: Path | None = None,
) -> pl.DataFrame:
    """Fetch every URN in CTEXT_URNS and concatenate into one frame.

    ``fetcher`` is injected for testability. If ``cache_dir`` is set the
    raw JSON payloads are written under it (``<doc_id>.json``) so a
    second run is offline.
    """
    frames: list[pl.DataFrame] = []
    for doc_id, urn in CTEXT_URNS.items():
        payload = fetcher(urn)
        if cache_dir is not None:
            cache_dir.mkdir(parents=True, exist_ok=True)
            (cache_dir / f"{doc_id}.json").write_text(
                json.dumps(payload, ensure_ascii=False), encoding="utf-8"
            )
        frames.append(parse_ctext_response(doc_id, payload))
    if not frames:
        return pl.DataFrame(
            schema={
                "doc_id": pl.Utf8,
                "source": pl.Utf8,
                "urn": pl.Utf8,
                "paragraph_index": pl.Int64,
                "text": pl.Utf8,
            }
        )
    return pl.concat(frames, how="vertical")
