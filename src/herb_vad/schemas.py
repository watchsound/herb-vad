"""Canonical data contracts for Herb-VAD.

Shared by every ingest source, every embedding pipeline, and every
analysis script. Source-specific code maps into these types; downstream
code never sees a SymMap or TCMSP shape directly.
"""

from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class PropertyAxis(str, Enum):
    QI = "QI"  # 四气
    FLAVOR = "FLAVOR"  # 五味
    DIRECTION = "DIRECTION"  # 升降浮沉
    CHANNEL = "CHANNEL"  # 归经
    TOXICITY = "TOXICITY"  # 毒性


class FourQi(str, Enum):
    HOT = "hot"
    WARM = "warm"
    NEUTRAL = "neutral"
    COOL = "cool"
    COLD = "cold"


class FiveFlavor(str, Enum):
    SOUR = "sour"
    BITTER = "bitter"
    SWEET = "sweet"
    PUNGENT = "pungent"
    SALTY = "salty"
    BLAND = "bland"  # 淡 — appended in some traditions, surfaced separately


class Channel(str, Enum):
    LU = "lung"
    LI = "large_intestine"
    ST = "stomach"
    SP = "spleen"
    HT = "heart"
    SI = "small_intestine"
    BL = "bladder"
    KI = "kidney"
    PC = "pericardium"
    SJ = "san_jiao"
    GB = "gallbladder"
    LV = "liver"


class Direction(str, Enum):
    ASCEND = "ascend"
    FLOAT = "float"
    DESCEND = "descend"
    SINK = "sink"
    NEUTRAL = "neutral"


class Toxicity(str, Enum):
    NONE = "none"
    SLIGHT = "slight"  # 小毒
    MODERATE = "moderate"  # 有毒
    SEVERE = "severe"  # 大毒


class CanonicalHerb(BaseModel):
    model_config = ConfigDict(frozen=True)

    canonical_id: str = Field(pattern=r"^H\d{5}$")
    pinyin: str
    chinese: str
    latin: str | None = None
    aliases: tuple[str, ...] = ()


class HerbPropertyRecord(BaseModel):
    canonical_id: str
    source: Literal["symmap", "tcmsp", "etcm", "batman", "herb_db", "tcmid", "tcm_mkg", "classical"]
    axis: PropertyAxis
    value: str  # validated against the axis-specific enum downstream
    confidence: float = 1.0


class EmbeddingRecord(BaseModel):
    canonical_id: str
    embedding: str  # e.g. "bge-m3", "tcm2vec-formula", "gin-chem"
    text_source: str  # which text was embedded (definition, indication, …)
    dim: int
    vector: list[float]


class ProbeResult(BaseModel):
    embedding: str
    axis: PropertyAxis
    accuracy: float
    macro_f1: float
    n: int
    cv_folds: int
    held_out_symptom: bool = False
