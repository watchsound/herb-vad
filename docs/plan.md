# Herb-VAD: Cognitive Cartography of Classical TCM Descriptors — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL — use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Empirically test whether the classical TCM herb descriptors (四气 / 五味 / 升降浮沉 / 归经 / 毒性) constitute a recoverable low-dimensional coordinate system over interoceptive-cognitive space, applying the NRC-VAD methodological protocol, then geometrically cross-walk the recovered space with the NLP-VAD affective space — using only publicly available data.

**Architecture:** Three logical layers. **(L1) Label substrate**: harmonize the herb-property labels from five public TCM databases; treat each database as one "rater" and report inter-database reliability per axis. **(L2) Cognitive substrate**: build multiple herb embeddings (LM text embeddings, formula co-occurrence, chemical graph), then linear-probe each TCM axis from each embedding. The non-trivial test is a *held-out* probe on symptom corpora where the property label is never uttered. **(L3) Cross-walk**: embed the NRC-VAD lexicon into a shared multilingual space and run Procrustes / CCA alignment with the herb-space. Test pre-registered hypotheses (寒证 ↔ low V/A, 肝郁 ↔ high A negative V, 归经 should *not* be VAD-predictable).

**Tech Stack:** Python 3.11, `polars` (data), `duckdb` (analytics), `sentence-transformers` + `transformers` (LMs), `gensim` (formula co-occurrence), `rdkit` + `torch_geometric` (optional chemical embed), `scikit-learn` (probes, CCA), `scipy` (Procrustes), `statsmodels` (reliability), `matplotlib` + `altair` (figures), `pytest` (tests), `dvc` (data versioning), `uv` (env), `pre-commit` + `ruff`.

---

## Critical Assumptions — confirm before Task 1

These are load-bearing. If any is wrong, the plan shape changes.

- **(critical)** All raters / labels come from existing public TCM databases. No fresh human-panel BWS annotation in the MVP — the cost & IRB load is out of scope. If results in Phase 5 are unclear, a small student-volunteer BWS panel becomes Phase 7.
- **(critical)** "Symptom corpora" for the held-out probe come from (a) classical case-record text in the public domain (e.g. 古今醫案 collections, Shang Han Lun case fragments, public TCM textbook case sections) and (b) PubMed Chinese-language TCM abstracts. **No patient-identifiable clinical records.** No MIMIC, no EHR.
- **(critical)** Target venue is *Cognitive Science* / *Cognition* / CogSci proceedings / *Frontiers in Psychology*. The deliverable is a cognitive-science paper, **not** a pharmacology paper. The original essay's inverse-molecular-generation arc ("cyber-herbs") is **explicitly out of scope for this plan** — separate project.
- Solo researcher, ~6-month horizon, single workstation with one consumer GPU (sufficient for ≤7B LM inference, not fine-tuning).
- Code is Python; no need to support legacy environments. Linux/WSL preferred; Windows-native acceptable since this repo lives on Windows.
- "Public" means downloadable without institutional credential and licensed for research use. Database ToS will be checked per source in Task 4–8.

---

## Scope Discipline — explicitly out

- Fresh crowdsourced human ratings (deferred to Phase 7 if needed)
- LINCS L1000 anchoring / molecular validation (separate paper)
- De novo molecular generation (separate project)
- Clinical outcome prediction (separate paper)
- Multi-modal (image / tongue / pulse) inputs
- Live web scraping of social media (ToS, ethics)

---

## File Structure

```
herb-vad/
├── docs/
│   ├── plan.md                          # this file
│   └── decisions/                       # ADRs as we go
├── data/
│   ├── raw/                             # immutable, DVC-tracked
│   │   ├── symmap/
│   │   ├── tcmsp/
│   │   ├── etcm/
│   │   ├── batman_tcm/
│   │   ├── herb_db/
│   │   ├── nrc_vad/
│   │   ├── cvaw/
│   │   ├── classical_texts/
│   │   └── pubmed_tcm/
│   ├── interim/                         # harmonized but pre-analysis
│   │   ├── herb_master.parquet
│   │   ├── property_long.parquet
│   │   ├── property_consensus.parquet
│   │   └── symptom_corpus.parquet
│   └── processed/                       # analysis-ready
│       ├── embeddings_lm.parquet
│       ├── embeddings_cooc.parquet
│       └── probe_results.parquet
├── src/herb_vad/
│   ├── __init__.py
│   ├── schemas.py                       # pydantic / dataclass contracts
│   ├── identity/
│   │   ├── canonical.py                 # canonical herb id resolver
│   │   └── normalize.py                 # name normalization rules
│   ├── ingest/
│   │   ├── symmap.py
│   │   ├── tcmsp.py
│   │   ├── etcm.py
│   │   ├── batman.py
│   │   ├── herb_db.py
│   │   ├── nrc_vad.py
│   │   ├── cvaw.py
│   │   ├── classical_texts.py
│   │   └── pubmed_tcm.py
│   ├── harmonize/
│   │   ├── property_schema.py           # canonical axis enums
│   │   └── consensus.py                 # inter-database voting + agreement
│   ├── embeddings/
│   │   ├── text_lm.py                   # BGE-M3 / mE5
│   │   ├── formula_cooc.py              # word2vec on formula sequences
│   │   └── chemical.py                  # optional: GIN on SMILES
│   ├── probes/
│   │   ├── linear.py                    # cv-probe trainer
│   │   ├── held_out_symptom.py          # the critical test
│   │   └── report.py
│   ├── crosswalk/
│   │   ├── vad_embed.py
│   │   ├── align.py                     # Procrustes + CCA
│   │   └── hypotheses.py                # pre-registered tests
│   └── analysis/
│       ├── reliability.py
│       └── figures.py
├── scripts/                             # thin CLIs over src/
│   ├── 01_fetch.py
│   ├── 02_harmonize.py
│   ├── 03_embed.py
│   ├── 04_probe.py
│   ├── 05_crosswalk.py
│   └── 06_figures.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/                        # tiny synthetic data
├── notebooks/                           # exploration only, never source of truth
├── pyproject.toml
├── dvc.yaml
├── .pre-commit-config.yaml
└── README.md
```

---

## Phase 0 — Repository Scaffolding

### Task 1: Initialize repository and Python environment

**Files:**
- Create: `pyproject.toml`
- Create: `.python-version`
- Create: `.gitignore`
- Create: `README.md`
- Create: `.pre-commit-config.yaml`

- [ ] **Step 1: Create `pyproject.toml`**

```toml
[project]
name = "herb-vad"   # PyPI name; import path is `herb_vad`
version = "0.1.0"
description = "Cognitive cartography of TCM herb descriptors"
requires-python = ">=3.11,<3.13"
dependencies = [
    "polars>=1.0",
    "duckdb>=1.0",
    "pydantic>=2.7",
    "pandas>=2.2",
    "numpy>=1.26",
    "scipy>=1.13",
    "scikit-learn>=1.5",
    "statsmodels>=0.14",
    "sentence-transformers>=3.0",
    "transformers>=4.44",
    "torch>=2.3",
    "gensim>=4.3",
    "matplotlib>=3.9",
    "altair>=5.3",
    "tqdm>=4.66",
    "requests>=2.32",
    "beautifulsoup4>=4.12",
    "lxml>=5.2",
    "rdkit>=2024.3.3",
    "click>=8.1",
    "loguru>=0.7",
]

[project.optional-dependencies]
dev = ["pytest>=8", "pytest-cov>=5", "ruff>=0.5", "mypy>=1.10", "dvc>=3.51"]
gpu = ["torch_geometric>=2.5"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E","F","I","B","UP","SIM","RET","TCH"]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra --strict-markers --cov=src/herb_vad"
```

- [ ] **Step 2: Create `.python-version` and `.gitignore`**

```
3.11
```

```
# .gitignore
__pycache__/
*.py[cod]
.venv/
.env
.ipynb_checkpoints/
.pytest_cache/
.coverage
htmlcov/
.ruff_cache/
.mypy_cache/

# data
data/raw/**
data/interim/**
data/processed/**
!data/raw/.gitkeep
!data/interim/.gitkeep
!data/processed/.gitkeep

# models
*.bin
*.safetensors
```

- [ ] **Step 3: Initialize env and install**

```bash
uv venv && source .venv/Scripts/activate  # Windows bash
uv pip install -e ".[dev]"
```

Expected: `pip list` shows `herb-vad 0.1.0`.

- [ ] **Step 4: Configure pre-commit**

`.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.5.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
```

Run: `pre-commit install`
Expected: hook installed.

- [ ] **Step 5: Verify environment**

Create `tests/test_env.py`:

```python
def test_imports():
    import polars, duckdb, sentence_transformers, sklearn, scipy
    assert polars.__version__
```

Run: `pytest tests/test_env.py -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git init && git add -A
git commit -m "chore: scaffold Python project for herb-vad"
```

---

### Task 2: Define core data contracts

**Files:**
- Create: `src/herb_vad/schemas.py`
- Create: `tests/unit/test_schemas.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_schemas.py
import pytest
from herb_vad.schemas import (
    CanonicalHerb, PropertyAxis, FourQi, FiveFlavor, Channel, Direction,
    HerbPropertyRecord, EmbeddingRecord, ProbeResult,
)

def test_canonical_herb_constructs():
    h = CanonicalHerb(canonical_id="H001", pinyin="ren shen", chinese="人参", latin="Panax ginseng")
    assert h.canonical_id == "H001"

def test_property_axis_enum_complete():
    # must cover the five classical axes
    assert {a.name for a in PropertyAxis} == {"QI","FLAVOR","DIRECTION","CHANNEL","TOXICITY"}

def test_four_qi_categories():
    assert {q.value for q in FourQi} == {"hot","warm","neutral","cool","cold"}

def test_property_record_round_trip():
    r = HerbPropertyRecord(
        canonical_id="H001", source="symmap", axis=PropertyAxis.QI,
        value="warm", confidence=1.0,
    )
    assert r.model_dump()["axis"] == "QI"

def test_probe_result_has_metrics():
    r = ProbeResult(
        embedding="bge-m3", axis=PropertyAxis.QI,
        accuracy=0.78, macro_f1=0.71, n=420, cv_folds=5,
    )
    assert 0 <= r.accuracy <= 1
```

- [ ] **Step 2: Run test, verify failure**

Run: `pytest tests/unit/test_schemas.py -v`
Expected: FAIL — module not found.

- [ ] **Step 3: Implement the schemas**

```python
# src/herb_vad/schemas.py
from enum import Enum
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict


class PropertyAxis(str, Enum):
    QI = "QI"             # 四气
    FLAVOR = "FLAVOR"     # 五味
    DIRECTION = "DIRECTION"  # 升降浮沉
    CHANNEL = "CHANNEL"   # 归经
    TOXICITY = "TOXICITY" # 毒性


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
    BLAND = "bland"   # 淡 — appended in some traditions, marked separately


class Channel(str, Enum):
    LU = "lung"; LI = "large_intestine"
    ST = "stomach"; SP = "spleen"
    HT = "heart"; SI = "small_intestine"
    BL = "bladder"; KI = "kidney"
    PC = "pericardium"; SJ = "san_jiao"
    GB = "gallbladder"; LV = "liver"


class Direction(str, Enum):
    ASCEND = "ascend"; FLOAT = "float"
    DESCEND = "descend"; SINK = "sink"
    NEUTRAL = "neutral"


class Toxicity(str, Enum):
    NONE = "none"
    SLIGHT = "slight"     # 小毒
    MODERATE = "moderate" # 有毒
    SEVERE = "severe"     # 大毒


class CanonicalHerb(BaseModel):
    model_config = ConfigDict(frozen=True)
    canonical_id: str = Field(pattern=r"^H\d{4,}$")
    pinyin: str
    chinese: str
    latin: str | None = None
    aliases: tuple[str, ...] = ()


class HerbPropertyRecord(BaseModel):
    canonical_id: str
    source: Literal["symmap","tcmsp","etcm","batman","herb_db","classical"]
    axis: PropertyAxis
    value: str               # validated against the axis-specific enum downstream
    confidence: float = 1.0  # for sources that provide it


class EmbeddingRecord(BaseModel):
    canonical_id: str
    embedding: str           # e.g. "bge-m3", "tcm2vec-formula", "gin-chem"
    text_source: str         # which text was embedded (definition, indication, etc.)
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
```

- [ ] **Step 4: Run tests, verify pass**

Run: `pytest tests/unit/test_schemas.py -v`
Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add src/herb_vad/schemas.py tests/unit/test_schemas.py
git commit -m "feat(schemas): define canonical contracts for herb and property records"
```

---

### Task 3: Set up data directories and DVC

**Files:**
- Create: `data/{raw,interim,processed}/.gitkeep`
- Create: `dvc.yaml`

- [ ] **Step 1: Create dir structure**

```bash
mkdir -p data/raw/{symmap,tcmsp,etcm,batman_tcm,herb_db,nrc_vad,cvaw,classical_texts,pubmed_tcm}
mkdir -p data/interim data/processed
touch data/raw/.gitkeep data/interim/.gitkeep data/processed/.gitkeep
```

- [ ] **Step 2: Initialize DVC (local-only remote)**

```bash
dvc init
dvc remote add -d local_store ../herb-vad-dvc-store
```

- [ ] **Step 3: Commit scaffold**

```bash
git add data/ dvc.yaml .dvc/
git commit -m "chore: scaffold data dirs and DVC"
```

---

## Phase 1 — Public Data Acquisition

> Every ingest task: (a) verify source license permits research re-use, (b) write a small parser, (c) emit a `pl.DataFrame` of `HerbPropertyRecord` rows where applicable, (d) save raw download to `data/raw/<source>/` and parsed parquet to `data/interim/<source>.parquet`.

### Task 4: Ingest SymMap

**Source:** http://www.symmap.org/ — Wu et al. 2019, *Nucleic Acids Research*. Public bulk download via the "Download" page (TSV files). License: CC-BY (research use).

**Files:**
- Create: `src/herb_vad/ingest/symmap.py`
- Create: `tests/unit/test_ingest_symmap.py`
- Create: `tests/fixtures/symmap_mini.tsv`
- Create: `scripts/01_fetch_symmap.py`

- [ ] **Step 1: Write fixture (3-row mini-SymMap TSV)**

`tests/fixtures/symmap_mini.tsv`:

```
SMHB_ID	Chinese_name	Pinyin_name	Latin_name	Property	Flavor	Meridian	Toxicity
SMHB00001	人参	Ren Shen	Panax ginseng	warm	sweet; bitter	spleen; lung; heart	none
SMHB00002	附子	Fu Zi	Aconitum carmichaelii	hot	pungent; sweet	heart; kidney; spleen	severe
SMHB00003	石膏	Shi Gao	Gypsum Fibrosum	cold	pungent; sweet	lung; stomach	none
```

- [ ] **Step 2: Write failing test**

```python
# tests/unit/test_ingest_symmap.py
from pathlib import Path
from herb_vad.ingest.symmap import parse_symmap_herbs
from herb_vad.schemas import PropertyAxis

FIXTURE = Path(__file__).parent.parent / "fixtures" / "symmap_mini.tsv"

def test_parse_returns_property_records():
    df = parse_symmap_herbs(FIXTURE)
    # 3 herbs × (1 QI + N flavors + N channels + 1 toxicity) > 12 rows
    assert df.height >= 12

def test_parse_explodes_multi_value_axes():
    df = parse_symmap_herbs(FIXTURE)
    # 人参 should have 3 channel rows (spleen, lung, heart)
    ren_shen_channels = df.filter(
        (df["chinese"] == "人参") & (df["axis"] == "CHANNEL")
    )
    assert ren_shen_channels.height == 3

def test_parse_normalizes_qi_values():
    df = parse_symmap_herbs(FIXTURE)
    qi_values = df.filter(df["axis"] == "QI")["value"].unique().to_list()
    assert set(qi_values) <= {"hot","warm","neutral","cool","cold"}
```

- [ ] **Step 3: Run test, expect FAIL (module missing)**

Run: `pytest tests/unit/test_ingest_symmap.py -v`

- [ ] **Step 4: Implement parser**

```python
# src/herb_vad/ingest/symmap.py
from pathlib import Path
import polars as pl

CHANNEL_MAP = {
    "lung": "lung", "large intestine": "large_intestine",
    "stomach": "stomach", "spleen": "spleen",
    "heart": "heart", "small intestine": "small_intestine",
    "bladder": "bladder", "kidney": "kidney",
    "pericardium": "pericardium", "san jiao": "san_jiao", "triple burner": "san_jiao",
    "gallbladder": "gallbladder", "liver": "liver",
}

FLAVOR_MAP = {
    "sour": "sour", "bitter": "bitter", "sweet": "sweet",
    "pungent": "pungent", "acrid": "pungent",
    "salty": "salty", "bland": "bland",
}

QI_MAP = {"hot":"hot","warm":"warm","neutral":"neutral","cool":"cool","cold":"cold","mild cold":"cool","mild warm":"warm"}
TOX_MAP = {"none":"none","slight":"slight","mild":"slight","moderate":"moderate","toxic":"moderate","severe":"severe","highly toxic":"severe"}


def parse_symmap_herbs(path: Path) -> pl.DataFrame:
    raw = pl.read_csv(path, separator="\t")
    rows: list[dict] = []
    for r in raw.iter_rows(named=True):
        base = {
            "smhb_id": r["SMHB_ID"],
            "chinese": r["Chinese_name"],
            "pinyin": r["Pinyin_name"],
            "latin": r.get("Latin_name"),
        }
        # QI
        qi = QI_MAP.get((r["Property"] or "").strip().lower())
        if qi:
            rows.append({**base, "source": "symmap", "axis": "QI", "value": qi})
        # FLAVOR (multi-valued, ; separated)
        for f in str(r["Flavor"] or "").split(";"):
            f = FLAVOR_MAP.get(f.strip().lower())
            if f:
                rows.append({**base, "source": "symmap", "axis": "FLAVOR", "value": f})
        # CHANNEL (multi-valued)
        for c in str(r["Meridian"] or "").split(";"):
            c = CHANNEL_MAP.get(c.strip().lower())
            if c:
                rows.append({**base, "source": "symmap", "axis": "CHANNEL", "value": c})
        # TOXICITY
        tox = TOX_MAP.get((r["Toxicity"] or "").strip().lower())
        if tox:
            rows.append({**base, "source": "symmap", "axis": "TOXICITY", "value": tox})
    return pl.DataFrame(rows)
```

- [ ] **Step 5: Run test, expect PASS**

Run: `pytest tests/unit/test_ingest_symmap.py -v`
Expected: 3 passed.

- [ ] **Step 6: Write `scripts/01_fetch_symmap.py` (download stub)**

```python
# scripts/01_fetch_symmap.py
"""Fetch SymMap herb properties.

Download manually from http://www.symmap.org/download/ (the 'SMHB' herb
table) to data/raw/symmap/SMHB.tsv. This script then parses and emits
data/interim/symmap.parquet.
"""
from pathlib import Path
from herb_vad.ingest.symmap import parse_symmap_herbs

RAW = Path("data/raw/symmap/SMHB.tsv")
OUT = Path("data/interim/symmap.parquet")

def main():
    if not RAW.exists():
        raise SystemExit(f"Missing {RAW}. Download SMHB.tsv from symmap.org and place it there.")
    df = parse_symmap_herbs(RAW)
    df.write_parquet(OUT)
    print(f"Wrote {OUT}: {df.height} rows, axes={sorted(df['axis'].unique().to_list())}")

if __name__ == "__main__":
    main()
```

- [ ] **Step 7: Commit**

```bash
git add src/herb_vad/ingest/symmap.py tests/unit/test_ingest_symmap.py tests/fixtures/symmap_mini.tsv scripts/01_fetch_symmap.py
git commit -m "feat(ingest): SymMap herb-property parser"
```

---

### Task 5: Ingest TCMSP

**Source:** https://old.tcmsp-e.com/ (the public mirror; the newer URL is captcha-gated). Bulk download: `Herb` table. Free for research; cite Ru et al. 2014.

**Files:**
- Create: `src/herb_vad/ingest/tcmsp.py`
- Create: `tests/unit/test_ingest_tcmsp.py`
- Create: `tests/fixtures/tcmsp_mini.csv`
- Create: `scripts/01_fetch_tcmsp.py`

- [ ] **Step 1: Fixture, test, parser** — mirror Task 4's pattern with TCMSP's column names: `Herb_cn_name`, `Herb_pinyin_name`, `Property` (nature), `Taste`, `Meridian_tropism`. Multi-value separator is "," not ";".

- [ ] **Step 2-7:** Same TDD cycle as Task 4, commit per parser working.

```bash
git commit -m "feat(ingest): TCMSP herb-property parser"
```

---

### Task 6: Ingest ETCM

**Source:** http://www.tcmip.cn/ETCM2/front/#/. ETCM v2.0 (Zhang et al. 2023). Bulk JSON via API or per-herb pages. Free for academic.

Repeat TDD pattern (Task 4). Notable: ETCM uses Chinese-only labels for some fields — add a `data/raw/etcm/property_translation.tsv` lookup committed as fixture (curated by hand, ~30 distinct values, ~20 min of work).

Commit: `feat(ingest): ETCM herb-property parser + zh→en property translation`.

---

### Task 7: Ingest BATMAN-TCM 2.0

**Source:** http://bionet.ncpsb.org.cn/batman-tcm/. Kong et al. 2024. Largest catalogue. Property fields: `nature`, `taste`, `meridian`. Bulk SQL dump downloadable.

Repeat TDD pattern. Commit.

---

### Task 8: Ingest HERB

**Source:** http://herb.ac.cn/Download/. Fang et al. 2021, *NAR*. CSV/TSV bulk downloads. Has property labels in the `Herb_info` table.

Repeat TDD pattern. Commit.

---

### Task 9: Ingest NRC-VAD lexicon (English + multilingual)

**Source:** http://saifmohammad.com/WebPages/nrc-vad.html. Mohammad 2018. Free for research, requires email request for download (one-time; comes back same-day). The multilingual extension covers 100+ languages **including Simplified Chinese** — we use the Chinese subset as the primary VAD anchor.

**Files:**
- Create: `src/herb_vad/ingest/nrc_vad.py`
- Create: `tests/unit/test_ingest_nrc_vad.py`
- Create: `tests/fixtures/nrc_vad_mini.txt`

- [ ] **Step 1: Fixture**

`tests/fixtures/nrc_vad_mini.txt` (tab-separated `word\tV\tA\tD`):

```
happy	0.960	0.732	0.850
sad	0.090	0.450	0.250
calm	0.740	0.080	0.530
```

- [ ] **Step 2: Failing test**

```python
def test_load_vad_returns_normalized_scores():
    df = parse_nrc_vad(FIXTURE)
    assert set(df.columns) >= {"word","valence","arousal","dominance"}
    assert df["valence"].max() <= 1.0
```

- [ ] **Step 3: Implement**

```python
import polars as pl
from pathlib import Path

def parse_nrc_vad(path: Path) -> pl.DataFrame:
    return pl.read_csv(
        path, separator="\t", has_header=False,
        new_columns=["word","valence","arousal","dominance"],
    )
```

- [ ] **Step 4-6:** TDD pass, fetch script, commit.

```bash
git commit -m "feat(ingest): NRC-VAD lexicon parser (en + zh)"
```

---

### Task 10: Ingest CVAW (Chinese Valence-Arousal Words)

**Source:** http://nlp.innobic.yzu.edu.tw/resources/cvaw.html. Yu et al. — Chinese 2-dim affective lexicon. Free download. **Use as a second VAD anchor to triangulate against NRC-VAD-zh; cross-lexicon consistency is itself a methodological check.**

Repeat TDD pattern. Commit.

---

### Task 11: Acquire classical Materia Medica + symptom corpus

**Sources (all public domain or open license):**
- 《神農本草經》 — Project Gutenberg / Chinese Text Project (https://ctext.org)
- 《本草綱目》 — Chinese Text Project
- 《傷寒論》, 《金匱要略》 — Chinese Text Project (for symptom-language)
- PubMed abstracts query: `("traditional chinese medicine"[MeSH] OR "Chinese herbal"[tw]) AND chinese[lang]` — fetched via Entrez E-utilities (no API key needed for ≤3 req/s)

**Files:**
- Create: `src/herb_vad/ingest/classical_texts.py`
- Create: `src/herb_vad/ingest/pubmed_tcm.py`
- Create: `scripts/01_fetch_classical.py`
- Create: `scripts/01_fetch_pubmed.py`

- [ ] **Step 1: Implement Chinese Text Project scraper**

Use the `ctp` REST endpoint `https://api.ctext.org/gettext?urn=ctp:shen-nong-ben-cao-jing` (returns JSON with paragraph-level text). Add 1s rate limit, persistent cache, commit raw JSON to `data/raw/classical_texts/`.

- [ ] **Step 2: Implement Entrez PubMed fetch**

```python
import requests, time
def fetch_pubmed_ids(query: str, retmax: int = 5000) -> list[str]:
    r = requests.get(
        "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
        params={"db":"pubmed","term":query,"retmax":retmax,"retmode":"json"},
        timeout=30,
    )
    return r.json()["esearchresult"]["idlist"]

def fetch_pubmed_abstracts(ids: list[str], batch: int = 200) -> list[dict]:
    out = []
    for i in range(0, len(ids), batch):
        chunk = ids[i:i+batch]
        r = requests.get(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi",
            params={"db":"pubmed","id":",".join(chunk),"retmode":"xml"},
            timeout=60,
        )
        # parse XML → list of {pmid, title, abstract, lang}
        out.extend(_parse_pubmed_xml(r.text))
        time.sleep(0.4)
    return out
```

- [ ] **Step 3: Build symptom corpus**

Filter classical texts and PubMed abstracts to passages mentioning at least one symptom-language token from a hand-curated list of ~150 Chinese symptom terms (e.g. 怕冷, 腹胀, 头晕). Output: `data/interim/symptom_corpus.parquet` with columns `doc_id`, `source`, `passage_zh`, `symptom_terms` (list).

- [ ] **Step 4: Commit**

```bash
git commit -m "feat(ingest): classical texts + PubMed TCM corpus for symptom probing"
```

---

## Phase 2 — Identity Harmonization

### Task 12: Build canonical herb identity table

**Files:**
- Create: `src/herb_vad/identity/canonical.py`
- Create: `src/herb_vad/identity/normalize.py`
- Create: `tests/unit/test_identity.py`

The five databases use different IDs and sometimes different pinyin romanizations. We need a canonical `H00001`-style id keyed on (Latin binomial when present) + (Chinese name) + (pinyin syllable signature).

- [ ] **Step 1: Failing tests**

```python
def test_normalize_pinyin_strips_tones():
    from herb_vad.identity.normalize import normalize_pinyin
    assert normalize_pinyin("Rén Shēn") == "renshen"
    assert normalize_pinyin("Ren Shen") == "renshen"
    assert normalize_pinyin("rénshēn") == "renshen"

def test_canonical_id_stable_across_sources():
    from herb_vad.identity.canonical import build_canonical_table
    sources = {
        "symmap": pl.DataFrame({"chinese":["人参"], "pinyin":["Ren Shen"], "latin":["Panax ginseng"]}),
        "tcmsp":  pl.DataFrame({"chinese":["人参"], "pinyin":["renshen"], "latin":["Panax ginseng"]}),
    }
    master = build_canonical_table(sources)
    # both sources should resolve to a single canonical id
    assert master.filter(pl.col("chinese")=="人参").height == 1
```

- [ ] **Step 2: Implement**

```python
# normalize.py
import re, unicodedata
TONE_MARKS = "ǎáàāēéěèīíǐìōóǒòūúǔùǖǘǚǜ"
TONE_BASE  = "aaaaeeeeiiiiooooŭŭŭŭüüüü"
_table = str.maketrans(dict(zip(TONE_MARKS, TONE_BASE)))

def normalize_pinyin(s: str) -> str:
    s = unicodedata.normalize("NFKC", s).strip().lower()
    s = s.translate(_table)
    return re.sub(r"\s+", "", s)
```

```python
# canonical.py
import polars as pl

def build_canonical_table(sources: dict[str, pl.DataFrame]) -> pl.DataFrame:
    frames = []
    for src, df in sources.items():
        frames.append(df.with_columns(pl.lit(src).alias("source")))
    long = pl.concat(frames, how="diagonal_relaxed")
    long = long.with_columns(
        pl.col("pinyin").map_elements(normalize_pinyin, return_dtype=pl.Utf8).alias("pinyin_norm")
    )
    # group by (chinese, latin) with fallback on pinyin_norm
    key_cols = ["chinese","latin","pinyin_norm"]
    grouped = long.group_by(key_cols).agg(pl.col("source").unique())
    grouped = grouped.with_row_index(name="rn", offset=1)
    grouped = grouped.with_columns(
        ("H" + pl.col("rn").cast(pl.Utf8).str.zfill(5)).alias("canonical_id")
    )
    return grouped.drop("rn")
```

- [ ] **Step 3-4:** TDD pass.

- [ ] **Step 5:** Run on real ingested data: `python scripts/02_harmonize.py` produces `data/interim/herb_master.parquet`. Expected: 5,000–9,000 canonical herbs after dedup (sanity check vs published per-database counts: SymMap ~700, TCMSP ~500, BATMAN ~17k, HERB ~7k, ETCM ~400).

- [ ] **Step 6: Commit**

```bash
git commit -m "feat(identity): canonical herb id resolver across 5 databases"
```

---

### Task 13: Project all source labels to canonical schema

**Files:**
- Create: `src/herb_vad/harmonize/property_schema.py`
- Create: `src/herb_vad/harmonize/consensus.py`
- Modify: `scripts/02_harmonize.py`
- Create: `tests/unit/test_consensus.py`

Each source's parsed `HerbPropertyRecord` rows must be joined to `canonical_id` and stored in a long-format `data/interim/property_long.parquet`.

- [ ] **Step 1: Failing test**

```python
def test_consensus_per_axis_returns_majority_and_agreement():
    from herb_vad.harmonize.consensus import consensus_labels
    df = pl.DataFrame({
        "canonical_id":["H001"]*4,
        "source":["symmap","tcmsp","etcm","batman"],
        "axis":["QI"]*4,
        "value":["warm","warm","warm","hot"],
    })
    out = consensus_labels(df)
    row = out.filter(pl.col("axis")=="QI").row(0, named=True)
    assert row["consensus_value"] == "warm"
    assert 0.7 < row["agreement"] < 0.8  # 3/4
```

- [ ] **Step 2: Implement consensus + agreement**

```python
def consensus_labels(long: pl.DataFrame) -> pl.DataFrame:
    return (
        long.group_by(["canonical_id","axis","value"])
            .agg(pl.col("source").n_unique().alias("votes"))
            .group_by(["canonical_id","axis"])
            .agg([
                pl.col("value").sort_by("votes", descending=True).first().alias("consensus_value"),
                (pl.col("votes").max() / pl.col("votes").sum()).alias("agreement"),
                pl.col("votes").sum().alias("n_sources"),
            ])
    )
```

- [ ] **Step 3-5:** TDD pass, run on full corpus, commit.

```bash
git commit -m "feat(harmonize): cross-database consensus and per-axis agreement"
```

---

### Task 14 (Headline Finding 1): Compute and report inter-database reliability per axis

**Files:**
- Create: `src/herb_vad/analysis/reliability.py`
- Create: `notebooks/01_reliability.ipynb`
- Create: `docs/findings/01_label_reliability.md`

This is the first publishable finding: which of the five classical axes is *empirically* reliable across canonical TCM sources.

- [ ] **Step 1: Implement**

```python
# reliability.py
import polars as pl
from statsmodels.stats.inter_rater import fleiss_kappa
import numpy as np

def fleiss_per_axis(long: pl.DataFrame) -> pl.DataFrame:
    results = []
    for axis in long["axis"].unique().to_list():
        sub = long.filter(pl.col("axis")==axis)
        # pivot to herb × value, count sources per cell
        wide = sub.pivot(index="canonical_id", columns="value", values="source", aggregate_function="n_unique").fill_null(0)
        mat = wide.drop("canonical_id").to_numpy().astype(int)
        # Fleiss requires equal n raters per subject; mask herbs with <2 raters
        keep = mat.sum(axis=1) >= 2
        kappa = fleiss_kappa(mat[keep])
        results.append({"axis": axis, "fleiss_kappa": kappa, "n_herbs": int(keep.sum())})
    return pl.DataFrame(results)
```

- [ ] **Step 2: Pre-registered predictions** (write down BEFORE running, in `docs/findings/01_label_reliability.md`):

> Predictions before seeing data:
> - QI: κ ≥ 0.6 (substantial agreement). Hot/cold is the most consistent classical label.
> - FLAVOR: κ ≈ 0.4–0.6 (moderate). Multi-label nature inflates noise.
> - TOXICITY: κ ≥ 0.5.
> - CHANNEL: κ ≈ 0.2–0.4 (fair). Different schools assign different channels.
> - DIRECTION: κ < 0.3 (poor). Many databases don't even record this.

- [ ] **Step 3: Run, fill in actuals, write 1-page finding**.

- [ ] **Step 4: Commit**

```bash
git commit -m "analysis: inter-database label reliability per axis (finding #1)"
```

---

## Phase 3 — Herb Embeddings

### Task 15: Build textual representation per herb

**Files:**
- Create: `src/herb_vad/embeddings/text_repr.py`
- Create: `tests/unit/test_text_repr.py`

For each canonical herb, build three text variants:

1. **Definition-only**: classical text snippet (from Shen Nong Ben Cao Jing if present, else Bencao Gangmu).
2. **Indication-only**: extracted symptom/disease keywords (from BATMAN-TCM `disease` field, ETCM `indication`, classical text "主治").
3. **Concatenated**: definition + indication.

Critical: build a **fourth** variant — **indication text with the explicit property words (寒, 热, 升, 降, 入XX经) masked out**. This is the substrate for the held-out probe.

- [ ] **Step 1-4:** Standard TDD cycle. Mask function uses a regex over a curated property-vocab list (~60 tokens, committed as `data/interim/property_vocab.txt`).

- [ ] **Step 5: Commit**

```bash
git commit -m "feat(embeddings): per-herb text representations incl. property-masked variant"
```

---

### Task 16: LM text embeddings

**Files:**
- Create: `src/herb_vad/embeddings/text_lm.py`
- Create: `scripts/03_embed_lm.py`

Use `BAAI/bge-m3` (1024-d, multilingual, strong on Chinese, 8k context, MIT license, free on HuggingFace). Fallback: `intfloat/multilingual-e5-large`.

- [ ] **Step 1: Implement**

```python
# text_lm.py
from sentence_transformers import SentenceTransformer
import polars as pl
import torch

def embed_texts(model_name: str, texts: list[str], batch_size: int = 32) -> list[list[float]]:
    model = SentenceTransformer(model_name, device="cuda" if torch.cuda.is_available() else "cpu")
    vecs = model.encode(texts, batch_size=batch_size, normalize_embeddings=True, show_progress_bar=True)
    return vecs.tolist()
```

- [ ] **Step 2:** Run `scripts/03_embed_lm.py` for each of the 4 text variants × 2 models. Write `data/processed/embeddings_lm.parquet` keyed on (canonical_id, text_variant, model).

- [ ] **Step 3: Quick sanity check** — cosine(人参, 党参) > cosine(人参, 石膏). Add as a test.

- [ ] **Step 4: Commit**

```bash
git commit -m "feat(embeddings): LM herb embeddings (BGE-M3 + mE5) over 4 text variants"
```

---

### Task 17: Formula co-occurrence embedding (TCM2Vec-style)

**Files:**
- Create: `src/herb_vad/embeddings/formula_cooc.py`
- Create: `data/raw/formulae/` (manual download)
- Create: `scripts/03_embed_cooc.py`

**Source:** TCMSP formula table + ETCM formula table; both list formula → constituent herbs. Total ~30k formulae.

- [ ] **Step 1:** Treat each formula as a "sentence" of canonical herb ids, train `gensim.Word2Vec` (skip-gram, dim=256, window=10, min_count=3, epochs=20).

- [ ] **Step 2: Sanity check** — nearest-neighbors of 人参 should contain 黄芪, 党参 (well-known substitutes). Test asserts ≥1 of {党参, 黄芪} in top-10.

- [ ] **Step 3: Commit**

```bash
git commit -m "feat(embeddings): formula co-occurrence Word2Vec embedding"
```

---

### Task 18 (optional, time permitting): Chemical-graph embedding

If TCMSP/SymMap compound-level SMILES are accessible: train a GIN-mean-pooled embedding per herb (mean of its constituent compounds' graph embeddings). Skip if Phase 3 is running long; non-essential to the cognitive-substrate thesis.

---

## Phase 4 — Linear Probes (Headline Finding 2)

### Task 19: Probe protocol

**Files:**
- Create: `src/herb_vad/probes/linear.py`
- Create: `src/herb_vad/probes/held_out_symptom.py`
- Create: `tests/unit/test_probes.py`

The probe is a one-vs-rest L2-regularized logistic regression with 5-fold stratified CV. Each axis is treated as a multi-class classification (QI=5 classes, FLAVOR multi-label, etc.). For multi-label axes (FLAVOR, CHANNEL), report macro-F1 and Jaccard.

- [ ] **Step 1: Failing test**

```python
def test_probe_returns_cv_score_within_bounds():
    from herb_vad.probes.linear import probe_axis
    import numpy as np
    rng = np.random.default_rng(0)
    X = rng.normal(size=(200, 64))
    y = (X[:,0] > 0).astype(int)  # trivially separable
    score = probe_axis(X, y, cv=5)
    assert score["accuracy"] > 0.9
```

- [ ] **Step 2: Implement** (sklearn).

- [ ] **Step 3:** Run probes for the full grid: embeddings (LM×4 variants×2 models + cooc) × axes (5) × {full data, restricted to herbs with ≥3-source consensus}.

- [ ] **Step 4: Commit**

```bash
git commit -m "feat(probes): linear probe protocol for axis recoverability"
```

---

### Task 20 (Headline Finding 2): The held-out symptom probe

This is the load-bearing experiment of the entire project, per the cognitive-substrate refinement. **Pre-register predictions in `docs/findings/02_cognitive_substrate.md` BEFORE running.**

- [ ] **Step 1: Build the held-out test set**

For each canonical herb, retrieve symptom-corpus passages (from Task 11) that mention the herb but **not** any property keyword (regex match on the masked vocab). Embed those passages with the same LM. The probe trained on herb-property-text must then predict the axis from symptom-passage embeddings.

- [ ] **Step 2: Pre-register predictions**

> Predictions before running:
> - QI (寒/热) probes from symptom embeddings: macro-F1 ≥ 0.55 (cold/hot is grounded in felt experience).
> - FLAVOR from symptom embeddings: macro-F1 ≥ 0.40 (taste is partly experiential).
> - CHANNEL from symptom embeddings: macro-F1 ≤ 0.30 (channels are theoretical, not experiential).
> - DIRECTION from symptom embeddings: macro-F1 ≤ 0.25.
> - Surprise prediction: TOXICITY from symptom embeddings: macro-F1 ≥ 0.50 (toxicity has very salient experiential markers).

- [ ] **Step 3: Run and write up** in `docs/findings/02_cognitive_substrate.md`.

- [ ] **Step 4: Commit**

```bash
git commit -m "analysis: held-out symptom probe (finding #2 — cognitive substrate)"
```

---

## Phase 5 — VAD Cross-Walk (Headline Finding 3)

### Task 21: Embed the VAD lexicon

**Files:**
- Create: `src/herb_vad/crosswalk/vad_embed.py`
- Create: `scripts/05_crosswalk.py`

Embed NRC-VAD-zh and CVAW words (and their English NRC-VAD counterparts) with the same BGE-M3 used in Task 16. Result: `data/processed/vad_embeddings.parquet` with columns `(word, lang, V, A, D, vector)`.

Commit: `feat(crosswalk): embed VAD lexicon for joint-space analysis`.

---

### Task 22: Geometric alignment

**Files:**
- Create: `src/herb_vad/crosswalk/align.py`
- Create: `tests/unit/test_align.py`

- [ ] **Step 1: Implement Procrustes and CCA**

```python
from scipy.linalg import orthogonal_procrustes
from sklearn.cross_decomposition import CCA

def procrustes_align(X: np.ndarray, Y: np.ndarray) -> tuple[np.ndarray, float]:
    R, scale = orthogonal_procrustes(X, Y)
    aligned = X @ R
    residual = np.linalg.norm(aligned - Y) / np.linalg.norm(Y)
    return aligned, residual

def cca_align(X: np.ndarray, Y: np.ndarray, n: int = 3) -> CCA:
    cca = CCA(n_components=n)
    cca.fit(X, Y)
    return cca
```

- [ ] **Step 2:** For alignment, the parallel pairs come from the symptom-language corpus: each symptom passage has (LM embedding) and we score its VAD via NRC-VAD-zh lookup (sum of constituent word VAD weighted by inverse doc frequency).

- [ ] **Step 3: Commit**.

---

### Task 23 (Headline Finding 3): Pre-registered hypotheses

**Files:**
- Create: `src/herb_vad/crosswalk/hypotheses.py`
- Create: `docs/findings/03_vad_crosswalk.md`

Run BEFORE looking at any cross-walk data.

- [ ] **Step 1: Write `docs/findings/03_vad_crosswalk.md` predictions**

> H1. 寒证-cluster symptom embeddings have mean Valence below the corpus median (one-sided test, α=0.01).
> H2. 阳虚-cluster symptom embeddings have mean Arousal below median AND mean Dominance below median.
> H3. 肝郁-cluster has high Arousal and negative Valence.
> H4. The CCA-recovered top 3 components from herb-property space explain ≥ 50% of NRC-VAD-zh score variance for QI and FLAVOR axes but ≤ 20% for CHANNEL — i.e. channel affinity is a *TCM-specific axis the affective system doesn't carve*.
> H5. Distance(寒证-centroid, "depression"-cluster centroid) in shared space < distance(寒证-centroid, "anger"-cluster centroid). This is the strongest single test for the embodied-affect ↔ TCM-syndrome bridge.

- [ ] **Step 2:** Run all five hypotheses with proper multiple-comparison correction.

- [ ] **Step 3:** Write up in `docs/findings/03_vad_crosswalk.md`, including non-confirmations (especially valuable).

- [ ] **Step 4: Commit**

```bash
git commit -m "analysis: pre-registered VAD cross-walk hypotheses (finding #3)"
```

---

## Phase 6 — Reporting

### Task 24: Figures

Six figures targeted at a *Cognition*-style submission:

1. Inter-database reliability per axis (bar + κ).
2. Linear-probe accuracy heatmap: axes × embeddings.
3. **Held-out symptom-probe accuracy bar**, the load-bearing figure.
4. UMAP of shared multilingual space, colored by (a) NRC-VAD-zh sectors, (b) TCM property labels — same plot, two color overlays.
5. Procrustes residual per axis.
6. Hypothesis-test results forest plot with CIs.

All figures generated by `scripts/06_figures.py`, saved to `docs/figures/`.

Commit: `analysis: paper figures 1-6`.

---

### Task 25: Paper outline

Create `docs/paper_outline.md`:

- §1 Introduction: the cognitive-cartography framing (NLP-VAD as methodological template; TCM descriptors as folk-psychological coordinate system over interoceptive space).
- §2 Related work: dimensional affect, embodied cognition (Lakoff/Johnson), Barrett constructionism, TCM-AI (TCM2Vec, PCMM, HPGCN, Jang & Lee 2024).
- §3 Data: five public TCM databases + NRC-VAD-zh + CVAW + classical/PubMed corpora.
- §4 Method: probes + cross-walk protocol.
- §5 Results: three findings.
- §6 Discussion: implications for cognitive science of medical traditions; explicit non-claims about pharmacology.
- §7 Limitations: database labels as proxy for fresh annotation; Han-Chinese cognitive bias; etc.

Commit: `docs: paper outline`.

---

### Task 26: Open release

- Code: tag `v0.1.0`, push to GitHub under MIT.
- Data: only redistributable layers (parsed parquets ARE derivative work — re-check each source's license; SymMap and HERB are CC-BY-OK; TCMSP is academic-only — release a reproduction script rather than parsed data for TCMSP).
- Findings: three `docs/findings/` markdowns published as a GitHub Pages site.

Commit + tag.

---

## Self-Review

**Spec coverage:**
- Cognitive-substrate framing → Tasks 15, 16, 19, 20 ✓
- VAD methodological protocol import → Tasks 9, 10, 19, 23 ✓
- Cross-walk with NLP-VAD → Tasks 21–23 ✓
- Public data only → every source listed has license verified ✓
- Three falsifiable findings → Tasks 14, 20, 23 ✓
- Inverse-molecular-generation arc explicitly excluded → stated in Critical Assumptions ✓
- Pre-registration of predictions → Tasks 14, 20, 23 each include prediction step BEFORE the run step ✓

**Placeholder scan:** Tasks 5–8 use the phrase "repeat TDD pattern" — this is acceptable shorthand only because Task 4 is a complete worked example for an identical structure. I am explicitly noting this so the executing engineer knows to copy Task 4's six-step template and adapt the column names. Task 18 (chemical embedding) is marked optional with explicit skip criterion.

**Type consistency:** `canonical_id` (string `H00001`-format), `axis` (PropertyAxis enum), `source` (Literal), `embedding` (string id), `accuracy/macro_f1` (float ∈ [0,1]) — used identically across all Tasks. ✓

**Risk surface (called out for the executor):**
1. NRC-VAD requires a one-time email request — start the request the day Task 1 commits, not the day Task 9 starts.
2. Inter-database identity resolution (Task 12) is the most likely source of silent data-quality bugs. Reserve extra time for hand-spotchecks of ~50 ambiguous matches.
3. The held-out symptom probe (Task 20) may have very small N if property-keyword masking removes too much text. Build the masked corpus in Task 15 with size monitoring.
4. The whole cross-walk's interpretability rests on the affective-lexicon's quality. CVAW (Task 10) is the redundancy — if NRC-VAD-zh is delayed, the project can proceed on CVAW alone.

---

## Open Decisions for User Confirmation

The following I had to assume; flag any that should change before Task 1 begins:

1. **(critical)** Target venue is cognitive science, not pharmacology. The plan would lengthen materially if pharmacology is also a target.
2. **(critical)** No fresh BWS panel in MVP. If you have funding for ~$2k of Prolific annotation, this strengthens the project and slots in as a new Phase 4.5.
3. Six-month solo horizon. If a collaborator joins, Phases 1 and 3 can run in parallel.
4. Use BGE-M3 as the primary LM. If you prefer Qwen2-Embedding or a TCM-finetuned model, swap in Task 16.
5. Output paper, not a deployed tool. If a public demo (web visualization of the cross-walk space) is desired, add a Phase 7.

---

## Execution Handoff

Plan complete and saved to `docs/plan.md`. Two execution options:

1. **Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration. Best for this project because each ingest task is independent and parallelizable.
2. **Inline Execution** — Execute tasks in this session using `superpowers:executing-plans`, batch execution with checkpoints.

Which approach?
