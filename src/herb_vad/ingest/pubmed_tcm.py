"""NCBI Entrez fetcher + parser for PubMed TCM abstracts.

ESearch finds PMIDs matching a query; EFetch returns XML with metadata
+ abstract bodies. Used by Task 11 to assemble the symptom-corpus that
Task 20's held-out probe regresses against.
"""

from __future__ import annotations

import time
import xml.etree.ElementTree as ET
from typing import Callable

import polars as pl
import requests  # type: ignore[import-untyped]

ESEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
EFETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

DEFAULT_QUERY = (
    '("traditional chinese medicine"[MeSH Terms] OR "chinese herbal medicine"[Title/Abstract])'
)


def fetch_pubmed_ids(
    query: str = DEFAULT_QUERY,
    *,
    retmax: int = 5000,
    session: requests.Session | None = None,
) -> list[str]:
    sess = session or requests.Session()
    resp = sess.get(
        ESEARCH,
        params={"db": "pubmed", "term": query, "retmax": retmax, "retmode": "json"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["esearchresult"]["idlist"]


def fetch_pubmed_xml(
    ids: list[str],
    *,
    batch: int = 200,
    session: requests.Session | None = None,
    sleep: float = 0.4,
) -> list[str]:
    """Fetch EFetch XML for batches of IDs; return a list of XML payload strings."""
    sess = session or requests.Session()
    out: list[str] = []
    for i in range(0, len(ids), batch):
        chunk = ids[i : i + batch]
        resp = sess.get(
            EFETCH,
            params={"db": "pubmed", "id": ",".join(chunk), "retmode": "xml"},
            timeout=60,
        )
        resp.raise_for_status()
        out.append(resp.text)
        time.sleep(sleep)
    return out


def parse_pubmed_xml(xml_text: str) -> pl.DataFrame:
    """Parse a PubMed EFetch XML payload into (pmid, title, abstract, language)."""
    root = ET.fromstring(xml_text)
    rows: list[dict[str, str]] = []
    for art in root.iter("PubmedArticle"):
        pmid_el = art.find(".//PMID")
        title_el = art.find(".//ArticleTitle")
        abstract_el = art.find(".//Abstract/AbstractText")
        lang_el = art.find(".//Language")
        rows.append(
            {
                "pmid": pmid_el.text if pmid_el is not None and pmid_el.text else "",
                "title": title_el.text if title_el is not None and title_el.text else "",
                "abstract": abstract_el.text
                if abstract_el is not None and abstract_el.text
                else "",
                "language": lang_el.text if lang_el is not None and lang_el.text else "",
            }
        )
    return pl.DataFrame(rows)


def fetch_and_parse(
    query: str = DEFAULT_QUERY,
    *,
    retmax: int = 200,
    id_fetcher: Callable[..., list[str]] = fetch_pubmed_ids,
    xml_fetcher: Callable[..., list[str]] = fetch_pubmed_xml,
) -> pl.DataFrame:
    ids = id_fetcher(query, retmax=retmax)
    if not ids:
        return pl.DataFrame(
            schema={"pmid": pl.Utf8, "title": pl.Utf8, "abstract": pl.Utf8, "language": pl.Utf8}
        )
    xml_blobs = xml_fetcher(ids)
    frames = [parse_pubmed_xml(blob) for blob in xml_blobs]
    return pl.concat(frames, how="vertical")
