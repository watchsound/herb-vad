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
| **TCMID** | `data/raw/tcmid/Updated_Herb` | 336 herbs, 1,607 records over QI/FLAVOR/CHANNEL | `scripts/01_fetch_tcmid.py` (Zenodo 8066910) |
| **TCM-MKG** | `data/raw/tcm_mkg/D{6,7}*.tsv` | **6,398 herbs, 23,517 records over QI/FLAVOR/CHANNEL** | `scripts/01_fetch_tcm_mkg.py` (Zenodo 19804367, Zeng) |
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

1. **TOXICITY data gap.** Only SymMap among the three live sources carries
   toxicity (91 records). HERB and BATMAN-TCM both carry it but are
   browser-gated. ETCM has it via per-herb API. Most accessible path:
   5-minute browser export from herb.ac.cn/Download/.
2. **DIRECTION (升降浮沉) gap.** None of SymMap / TCMID / TCM-MKG
   carry direction. The descriptor is largely absent from
   English-language Western-influenced TCM databases. Path forward
   needs a 经方-tradition Chinese source — likely manual extraction from
   Chinese Pharmacopoeia 2020 (PDF, paid) or a CNKI-indexed clinical
   text corpus.
3. **A fourth independent rater for proper Fleiss-κ.** Statsmodels'
   Fleiss-κ requires equal raters per subject, which our 3-source data
   already lacks. Adding a 4th source widens the eligible-herbs base
   and lets us drop the "raw agreement" stand-in metric. HERB or
   BATMAN-TCM each accomplish this.
4. Build an ETCM crawler against their per-herb API (~30 min).
5. Discover the correct ctext URN format for the four classical TCM
   works — and register for an API key at ctext.org/tools/subscribe
   to unlock `gettext` (free but auth-gated).

## ✅ Completed since first revision

- EN symptom vocabulary translation built (`symptom_vocab_en.py`, 130
  phrasings, 12.2% hit rate on PubMed corpus).
- Third independent TCM property source via Zenodo (TCM-MKG, 6,398
  herbs).
- Canonical-resolver fanout bug fixed (Latin-collision keys excluded
  from joins).
- _can_merge loosened to tolerate Latin disagreement when pinyin or
  chinese matches — necessary for SymMap×TCMID Ren Shen merge.
- `raw_agreement_per_axis` added as a robust headline metric for
  ragged-rater data.
- **First real Finding #1 numbers landed** (`docs/findings/01_label_reliability.md`).

## TOXICITY + DIRECTION re-hunt (2026-06-20, post-Finding-#1)

Targeted hunt for the two missing axes:

- **TCM-MKG D1 terminology**: lists 毒性 ("Herbal toxicity") and qi/flavor/channel
  as recognized property categories. But the D-tables themselves only encode
  qi/flavor/channel as property rows. 升降浮沉 isn't even listed in the TCM-MKG
  glossary — Western-influenced English-language TCM databases largely drop it.
- **ETCM Django API reverse-engineered**: discovered `/home/` endpoint registry
  on `http://www.tcmip.cn:18124/`. `/home/herb_get_level/` and `/home/browse/`
  return taxonomic/tree data. `/home/detail/` accepts GET but my param guesses
  ("data=人参&index_name=etcm_herb" etc.) all return `{"code":2,"msg":"No Data for !"}`.
  The required parameter shape is in a chunked JS file I didn't fully unpack.
  Doable with another ~1-2 hours of JS spelunking.
- **BATMAN downloadApi traced**: separate host `http://batman2.cloudna.cn/`.
  The JS pattern is `/downloadApiFile/${result_id}` — per-query result downloads,
  NOT bulk Herb_info. Bulk export requires going through the SPA UI to first
  execute a search, then download that result. No simple direct URL.
- **HERB direct endpoint**: confirmed via JS bundle the path is
  `/download/file/?file_path=static/download_data/HERB_herb_info.txt` — the
  endpoint validates the path-shape (accepts it) but reports
  `"Sorry, file_path dose not exists"`. The server-side file is missing.
- **Zenodo broad search** for "TCM toxic", "TCM ascending/descending",
  "Chinese pharmacopoeia property": only Zeng's TCM-MKG carries TCM property
  data. CMAUP is molecular-only. MTCMB is LLM Q&A.
- **GitHub search** for HERB/BATMAN/SymMap mirrors: only scrapers, no pre-scraped
  data. Best hit: TCMSP-Spider (44 stars) which is a Python scraper, not data.
- **Wikidata SPARQL** for TCM herbs with property labels: TCM herb-property
  axes aren't modeled in Wikidata.

**Net result for TOXICITY**: 91 records in SymMap remain the only live data.
The 268-herb 2-source eligible base for FLAVOR/CHANNEL drops to single-source
(91 herbs) for TOXICITY, which doesn't support inter-rater computation.

**Net result for DIRECTION**: still zero records across the live sources.
The three Zenodo-accessible TCM databases (SymMap, TCMID, TCM-MKG) all drop
升降浮沉 entirely. No public English-language TCM database covers this axis.

**Realistic paths forward** for each:
- TOXICITY: browser export from HERB or BATMAN-TCM (5 min user action each).
  ETCM via `/home/detail/` once the param shape is figured out.
- DIRECTION: requires a 经方-tradition source. Best candidates: Chinese
  Pharmacopoeia 2020 (paid PDF, manual extraction), CNKI clinical-text corpus
  (institutional access), or a sourced extraction from 《中药学》 standard textbook.
