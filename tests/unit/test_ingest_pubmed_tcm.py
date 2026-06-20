from pathlib import Path

import polars as pl

from herb_vad.ingest.pubmed_tcm import (
    fetch_and_parse,
    parse_pubmed_xml,
)

FIXTURE = Path(__file__).parent.parent / "fixtures" / "pubmed_efetch_sample.xml"


def test_parse_extracts_two_articles():
    df = parse_pubmed_xml(FIXTURE.read_text(encoding="utf-8"))
    assert df.height == 2


def test_parse_pmids():
    df = parse_pubmed_xml(FIXTURE.read_text(encoding="utf-8"))
    assert df["pmid"].to_list() == ["99999991", "99999992"]


def test_parse_language_field():
    df = parse_pubmed_xml(FIXTURE.read_text(encoding="utf-8"))
    assert set(df["language"].to_list()) == {"eng", "chi"}


def test_parse_chinese_abstract_preserved():
    df = parse_pubmed_xml(FIXTURE.read_text(encoding="utf-8"))
    chi_row = df.filter(pl.col("language") == "chi")
    assert "麻黄" in chi_row["abstract"][0]


def test_fetch_and_parse_uses_injected_fetchers():
    xml = FIXTURE.read_text(encoding="utf-8")

    def fake_ids(_query: str, retmax: int = 5000) -> list[str]:
        return ["99999991", "99999992"]

    def fake_xml(_ids: list[str], batch: int = 200) -> list[str]:
        return [xml]

    df = fetch_and_parse(id_fetcher=fake_ids, xml_fetcher=fake_xml)
    assert df.height == 2
    assert set(df["pmid"].to_list()) == {"99999991", "99999992"}


def test_fetch_and_parse_empty_id_list_returns_empty_frame():
    def fake_ids(_query: str, retmax: int = 5000) -> list[str]:
        return []

    def fake_xml(_ids: list[str], batch: int = 200) -> list[str]:
        raise AssertionError("xml_fetcher must not be called when there are no IDs")

    df = fetch_and_parse(id_fetcher=fake_ids, xml_fetcher=fake_xml)
    assert df.height == 0
