import json
from pathlib import Path


from herb_vad.ingest.classical_texts import (
    CTEXT_URNS,
    fetch_all,
    parse_ctext_response,
)

FIXTURE = Path(__file__).parent.parent / "fixtures" / "ctext_paragraphs_sample.json"


def _load_fixture() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_parse_returns_one_row_per_paragraph():
    payload = _load_fixture()
    df = parse_ctext_response("shen-nong-ben-cao-jing", payload)
    assert df.height == 3


def test_parse_preserves_paragraph_order():
    payload = _load_fixture()
    df = parse_ctext_response("shen-nong-ben-cao-jing", payload)
    assert df["paragraph_index"].to_list() == [0, 1, 2]
    assert "人參" in df["text"][0]


def test_parse_source_field():
    payload = _load_fixture()
    df = parse_ctext_response("shen-nong-ben-cao-jing", payload)
    assert df["source"].unique().to_list() == ["ctext"]


def test_parse_handles_contents_shape():
    payload = {
        "urn": "ctp:other",
        "contents": [
            {"text": "段落一"},
            {"text": "段落二"},
        ],
    }
    df = parse_ctext_response("other", payload)
    assert df.height == 2


def test_parse_unknown_shape_returns_empty():
    df = parse_ctext_response("misc", {"urn": "ctp:misc", "something_else": "x"})
    assert df.height == 0


def test_fetch_all_via_injected_fetcher_covers_all_urns():
    calls: list[str] = []

    def fake_fetcher(urn: str) -> dict:
        calls.append(urn)
        return {"urn": urn, "fulltext": [f"text-of-{urn}"]}

    df = fetch_all(fetcher=fake_fetcher)
    assert calls == list(CTEXT_URNS.values())
    assert df.height == len(CTEXT_URNS)
    assert set(df["doc_id"].to_list()) == set(CTEXT_URNS.keys())
