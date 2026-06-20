from herb_vad.schemas import (
    CanonicalHerb,
    Channel,
    Direction,
    EmbeddingRecord,
    FiveFlavor,
    FourQi,
    HerbPropertyRecord,
    ProbeResult,
    PropertyAxis,
)


def test_canonical_herb_constructs():
    h = CanonicalHerb(
        canonical_id="H00001", pinyin="ren shen", chinese="人参", latin="Panax ginseng"
    )
    assert h.canonical_id == "H00001"


def test_property_axis_enum_complete():
    assert {a.name for a in PropertyAxis} == {"QI", "FLAVOR", "DIRECTION", "CHANNEL", "TOXICITY"}


def test_four_qi_categories():
    assert {q.value for q in FourQi} == {"hot", "warm", "neutral", "cool", "cold"}


def test_five_flavor_categories():
    assert {f.value for f in FiveFlavor} >= {"sour", "bitter", "sweet", "pungent", "salty"}


def test_channel_has_twelve_meridians():
    assert len(set(Channel)) == 12


def test_direction_enum_has_neutral():
    assert Direction.NEUTRAL.value == "neutral"


def test_property_record_round_trip():
    r = HerbPropertyRecord(
        canonical_id="H00001",
        source="symmap",
        axis=PropertyAxis.QI,
        value="warm",
        confidence=1.0,
    )
    assert r.model_dump()["axis"] == "QI"


def test_embedding_record_dim_matches_vector():
    e = EmbeddingRecord(
        canonical_id="H00001",
        embedding="bge-m3",
        text_source="definition",
        dim=3,
        vector=[0.1, 0.2, 0.3],
    )
    assert len(e.vector) == e.dim


def test_probe_result_has_metrics():
    r = ProbeResult(
        embedding="bge-m3",
        axis=PropertyAxis.QI,
        accuracy=0.78,
        macro_f1=0.71,
        n=420,
        cv_folds=5,
    )
    assert 0 <= r.accuracy <= 1
