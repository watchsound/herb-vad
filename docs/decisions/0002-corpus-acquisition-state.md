# ADR-0002: Public-data acquisition — what worked, what didn't

**Date:** 2026-06-20
**Status:** Accepted (snapshot of state after auto-fetch attempts)

## Context

The plan assumed five TCM databases + two affective lexicons + classical
texts + PubMed would all be fetchable. Initial assumption was that the
user would download data manually per script docstring; later authorized
auto-fetch attempts revealed which sources are actually scrape-friendly
without browser interaction.

## Decisions

### ✅ Working sources (auto-fetched)

| Source | Path | Volume | How |
|---|---|---|---|
| **SymMap v2.0** | `data/raw/symmap/SMHB.{xlsx,tsv}` | 703 herbs, 3,414 property records over QI/FLAVOR/CHANNEL/TOXICITY | `scripts/01_fetch_symmap.py` (auto-downloads + converts xlsx → tsv via openpyxl) |
| **NRC-VAD v2.1** | `data/raw/nrc_vad/` | 44,728 English unigrams + V/A/D scores in [-1, +1] | User downloaded manually; `scripts/01_parse_nrc_vad.py` parses |
| **PubMed TCM (English)** | `data/interim/pubmed_tcm.parquet` | 1,998 abstracts (1,958 English / 40 Chinese-labeled) | `scripts/01_fetch_pubmed.py` (NCBI Entrez) |
| **PubMed TCM (Chinese-language)** | `data/interim/pubmed_tcm_zh.parquet` | 806 abstracts labeled `chi` | `scripts/01_fetch_pubmed.py` with `AND chinese[lang]` query |

### ❌ Browser-gated (need manual export)

| Source | Why blocked | Workaround |
|---|---|---|
| **HERB** | herb.ac.cn serves a JS SPA; download buttons require browser context | Open in browser, click "Herb Info" download, drop file at `data/raw/herb_db/Herb_info.tsv` |
| **BATMAN-TCM 2.0** | Vue.js SPA + separate downloadApi at `batman2.cloudna.cn`; AJAX-only | Same workflow as HERB |
| **TCMSP** | v2 has captcha; old mirror requires session export | Browser export from old.tcmsp-e.com |
| **ETCM v2.0** | Per-herb JSON API, no bulk download | Needs a custom crawler (~30 min of work) |
| **CVAW** | Page renders data into JS scatter plots; CSV not in static files | Email-to-author per academic norm |
| **ctext.org classical texts** | URN slugs like `ctp:shen-nong-ben-cao-jing` return ERR_INVALID_URN; canonical TCM corpus appears to live under `wiki.pl?chapter=...` IDs not the slug pattern documented in the plan | Needs URN discovery work (~30 min) |

### ⚠️ Data quality findings

- **PubMed Chinese-labeled abstracts only contain English text.** PubMed records the article's source-language as `chi` but stores the English-translated abstract. Our 90-term Chinese symptom vocabulary (`SYMPTOM_TERMS`) matched **0 of 1,998** English abstracts and **0 of 806** Chinese-labeled-but-English-text abstracts. Task 20's held-out symptom probe needs one of:
  1. An English-language symptom vocabulary (`怕冷` → "cold intolerance", "feels cold", etc.) — easy ~1 day of work.
  2. A native Chinese clinical corpus (CNKI is paywalled; ctext-once-fixed; or a TCM-specific symptom dataset).
- **SymMap v2.0 column structure differs from the plan's stub fixture.** Actual layout packs qi+flavor+toxicity tokens into a single `Properties_English` cell; parser updated to handle both layouts.

## Consequences

- Finding #1 (inter-database reliability) is **partially runnable now** with SymMap alone (one rater). For meaningful κ we still need ≥2 more sources, so HERB + TCMSP browser exports remain the unblocking step.
- Finding #2 (cognitive-substrate held-out symptom probe) is **blocked on the symptom-corpus language gap.** The infrastructure works; the corpus needs either an EN vocab table or a native ZH clinical text source.
- Finding #3 (VAD cross-walk) is **unblocked for the English side** (NRC-VAD is in hand) but the Chinese side still needs CVAW.
- All ML-deps (sentence-transformers, torch, gensim) remain unblocked because the user's network throttles big wheels; install requires browser-grade bandwidth.

## Next concrete actions (in priority order)

1. Open https://herb.ac.cn/Download/ in a browser, click the herb-info download once, save to `data/raw/herb_db/Herb_info.tsv` (~5 min).
2. Same for http://bionet.ncpsb.org.cn/batman-tcm/ → Download → Herb_info (~5 min).
3. Build the EN symptom vocabulary translation (`怕冷` → cold-intolerance synonyms, etc.) so PubMed corpus becomes usable (~1 day).
4. Discover the correct ctext URN format for the four classical TCM works (`wiki.pl?chapter=N` reverse lookup) (~30 min).
5. Build an ETCM crawler against their per-herb API (~30 min).
