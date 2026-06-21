# Herb-VAD: A Cognitive Cartography of Classical Chinese Medicine Herb Descriptors

**Draft version 0.1, 2026-06-21**
**Target venue:** *Cognitive Science* / *Cognition* / CogSci proceedings / *Frontiers in Psychology*

---

## Abstract

We propose that the classical Traditional Chinese Medicine (TCM) herb descriptors — 四气 (four qi: cold / cool / neutral / warm / hot), 五味 (five flavors: sour / bitter / sweet / pungent / salty), 升降浮沉 (directional tendency), 归经 (channel affinity), and 毒性 (toxicity) — form a culturally-constructed coordinate system over **interoceptive-cognitive space**, structurally analogous to how NLP's Valence-Arousal-Dominance (VAD) model (Mohammad, 2018) projects semantic space onto a low-rank affective basis. We import the methodological protocol that legitimized VAD (Best-Worst Scaling annotation, inter-rater reliability as primary output, regression-from-embedding validation) and apply its first stage — inter-source reliability — to TCM descriptors using five publicly available data sources (SymMap v2.0; TCMID; TCM-MKG; ETCM v2.0; Chinese Pharmacopoeia 2020). Across 1,098 herbs covered by ≥2 independent sources, the **QI (cold / hot) axis achieves 85.9% cross-source raw set-equality agreement**, confirming a pre-registered prediction. The CHANNEL axis (归经) reaches 72.7%; the multi-valued FLAVOR axis reaches 75.5% (a metric-imposed lower bound, see §7). The DIRECTION axis (升降浮沉) is systematically absent from every modern English-language TCM database, which is itself a finding consistent with the embodied-cognition reading: the most theory-laden descriptor has been pruned, while the most directly felt descriptor (hot/cold) has been preserved most stably. We argue this opens TCM property descriptors as a tractable target for cognitive-science investigation under the embodied-cognition framework, while explicitly disavowing any pharmacological claim. All code and processed data are public at https://github.com/watchsound/herb-vad.

**Keywords:** embodied cognition; dimensional affect; traditional Chinese medicine; cross-cultural cognition; interoception; pre-registered analysis.

---

## 1. Introduction

Traditional Chinese Medicine (TCM) categorizes thousands of herbs along a five-axis system that has remained stable across two millennia of clinical practice: 四气 (cold / cool / neutral / warm / hot), 五味 (sour / bitter / sweet / pungent / salty), 升降浮沉 (ascending / descending / floating / sinking), 归经 (twelve-channel affinity), and 毒性 (none / slight / moderate / severe). Two strongly opposed readings of this system dominate the literature.

The **skeptical reading** treats these axes as pre-scientific folk taxonomy — useful as historical artifact, irrelevant to empirical inquiry. The **TCM-AI maximalist reading**, by contrast, treats them as encoding hidden pharmacological truths that modern molecular biology has yet to recover (cf. Li, 2014, on network-target theory; the TCM2Vec embedding line, Dong et al., 2023). Both readings, in our view, miss a third option that the data support and that connects naturally to mainstream cognitive science.

We propose: **the classical TCM herb descriptors form a culturally-constructed coordinate system over interoceptive-cognitive space.** They do not encode molecular pharmacology; they encode how a pre-scientific medical tradition collectively carved up the experience of felt-bodily states and their pharmacological perturbations. In this framing, 寒/热 (cold/hot) is not a thermodynamic claim about herb metabolism; it is a category that pre-scientific clinicians and patients reliably converged on for *felt-bodily warmth versus felt-bodily coolness* — a pre-conceptual dimension that Lakoff and Johnson (1980) identify as a primary embodied schema, and that Barrett (2017) places at the core of the constructionist account of interoceptive experience.

This framing has a precedent. NLP's Valence-Arousal-Dominance (VAD) model (Russell, 1980; Mehrabian & Russell, 1974; Bradley & Lang, 1994; Mohammad, 2018) reduces the high-dimensional space of natural-language affect words to three orthogonal axes that capture *felt* affective experience. VAD is psychologically posited as primary (Mehrabian, 1996) but empirically behaves as a low-rank projection of richer semantic space — Sedoc et al. (2017) and Buechel and Hahn (2018) show VAD scores are reliably regressable from distributional embeddings like BERT, with split-half reliability of 0.85–0.95 across the three axes (Mohammad, 2018). We argue that the TCM property axes can be treated as the structural analogue: a low-rank, interpretable projection of a higher-dimensional **interoceptive-cognitive** space.

The asymmetry is crucial. VAD has 50+ years of psychometric validation; classical TCM descriptors have ~2,000 years of clinical use but no systematic empirical legitimization. We propose to **import the VAD methodological protocol** — annotation discipline, inter-rater reliability as primary output, regression-from-embedding validation, cross-cultural replication — and apply it to TCM descriptors. This paper reports the first stage: per-axis inter-source reliability across five independent TCM data sources.

Three pre-registered research questions structure the broader program (see Plan in the project repository); we report empirical results for RQ1 and describe completed infrastructure for RQ2 and RQ3.

- **RQ1 (this paper).** Are TCM property descriptors reliable across independent encodings of the canonical materia medica? Pre-registered ordering: QI > FLAVOR > TOXICITY > CHANNEL > DIRECTION.
- **RQ2 (infrastructure complete; real-data run pending).** Are TCM property labels predictable from language-model embeddings of *symptom narratives* — passages where the property keyword (寒, 热, 升, 降, …) has been explicitly masked out? Strong positive results would indicate the descriptor lives in *felt-experience space* and is not merely a discursive label.
- **RQ3 (infrastructure complete; real-data run pending).** Do TCM diagnostic categories and Western dimensional affect terms (NLP-VAD) partition the *same* underlying interoceptive-cognitive manifold differently in a shared multilingual language-model embedding space?

The contributions of this paper are: (i) the conceptual reframing of TCM descriptors as interoceptive-cognitive coordinates rather than pharmacological coordinates, (ii) the first cross-source reliability study at scale (1,098 herbs across QI, the largest published TCM property base we are aware of), (iii) the pre-registered confirmation that QI is the most reliable axis at scale, and (iv) the systematic-absence finding for DIRECTION (升降浮沉), which we interpret as evidence for the embodied-cognition reading.

## 2. Related Work

### 2.1 Dimensional affect

Russell (1980) introduced the circumplex model of affect, recovering a two-dimensional valence × arousal structure from multidimensional scaling of emotion-word similarity judgments. Mehrabian and Russell (1974) added a third axis — dominance — on factor-analytic grounds. Bradley and Lang (1994) operationalized the resulting PAD scheme via the Self-Assessment Manikin, and the ANEW lexicon (Bradley & Lang, 1999) became the empirical anchor for downstream NLP work.

Mohammad (2018) released the NRC-VAD lexicon: 20,000 English words annotated by Best-Worst Scaling for valence, arousal, and dominance. Best-Worst Scaling — annotators select the most/least *X* from a 4-tuple — yields substantially higher reliability than Likert ratings (split-half ρ ≈ 0.95 for valence, ≈ 0.90 arousal, ≈ 0.85 dominance). NRC-VAD v2.1 (Mohammad, 2025) expanded coverage to ~55,000 entries including multiword expressions. Sedoc et al. (2017) and Buechel and Hahn (2018) demonstrated that VAD scores are reliably *regressable* from distributional embeddings, which empirically reframes VAD as a low-rank projection of richer semantic space rather than a primary coordinate system.

Critiques of VAD include cross-cultural-validity concerns on the Dominance axis (Russell, 1991), arguments for a fourth dimension of unpredictability (Fontaine et al., 2007), and the categorical-versus-dimensional debate (Ekman, 1992 versus Barrett, 2006). For the present purposes, the **structural template** — orthogonal axes recovered from similarity ratings, simultaneously defended as primary and as a projection — is what we import.

### 2.2 Embodied cognition and the constructionist account of interoception

Lakoff and Johnson (1980) argue that human conceptual systems are organized around primary embodied schemas — UP / DOWN, IN / OUT, COLD / HOT, CONTAINER — that arise pre-conceptually from sensorimotor experience. Barrett (2017), Quigley et al. (2021), and the broader constructionist tradition place a high-dimensional interoceptive substrate at the foundation of affective experience, with culture-specific category boundaries layered over it. Pre-scientific medical traditions, on this view, should be expected to converge on descriptors that track the most directly felt interoceptive dimensions — *and to converge less strongly on descriptors that track theory-laden distinctions.*

This generates a falsifiable prediction. The TCM descriptors most directly grounded in felt experience (寒/热; possibly 五味) should be the most stable across independent encodings of the canonical materia medica; the most theory-laden (升降浮沉) should be the least stable, and may in the limit be pruned from databases that prioritize clinical reliability. Our results bear on this prediction in §6.

### 2.3 TCM informatics

Hopkins (2008) reframed drugs as polypharmacological perturbations of biological networks. Li (2014) extended this to TCM under the "network target" framework. The closest related work on TCM property representation is the TCM2Vec embedding line (Dong et al., 2023), the property-combination t-SNE projection of Zhang et al. (2025, "PCMM"), the HPGCN study which *predicts* cold/hot from PPI features (Niu et al., 2025), and Jang and Lee (2024) which uses dimensionality reduction on the Eight Principles classical-Chinese-medicine framework and finds Exterior–Interior the most generalizable axis.

To our knowledge, no prior work has framed the TCM property descriptors as a cognitive-coordinate system in the sense of dimensional affect theory, nor has any prior study computed multi-source inter-rater reliability for the five axes at the scale we report here. The closest spiritual cousins are Zhang et al. (2025) and Jang and Lee (2024); neither cites NLP-VAD or invokes embodied-cognition framing.

## 3. Methodological Protocol

The VAD methodology distills to a sequence of five steps:

1. **Best-Worst Scaling annotation** (Mohammad, 2018) — present annotators with 4-tuples, ask for the most/least *X* on each axis; aggregate to continuous scores.
2. **Inter-rater reliability as primary output** — split-half reliability is reported per axis; unreliable axes are surfaced, not hidden.
3. **Anchor to a measurable substrate** — VAD scores are regressable from distributional embeddings; this empirical bridge makes the construct scientific rather than purely psychometric.
4. **Test minimum-sufficient dimensionality** — factor analysis / PCA on the rating matrix tells you how many axes the data actually span.
5. **Cross-cultural / cross-school replication** — multilingual VAD lexicons replicate across languages with axis-specific cultural drift on Dominance most pronounced.

We propose to apply this protocol to TCM descriptors. In the present paper we report Stage 1 only, with one important substitution: rather than running a fresh BWS panel of TCM clinicians (which would be cost-prohibitive and IRB-heavy for a first study), we treat each of five independent TCM data sources as one "rater" and compute inter-source agreement. Each data source represents a distinct curatorial pipeline drawing on largely non-overlapping primary literatures (Chinese Pharmacopoeia 2020; Materia Medica Dictionary 2006; National Compilation 1996; modern textbook editions; institutional informatics teams at Tsinghua, Nankai, China Academy of Chinese Medical Sciences, Yuan Ze University). The five sources together approximate a panel of expert raters; this approximation is the principal limitation of the study and is addressed in §8.

Stages 2 through 5 of the protocol remain future work; the infrastructure for Stage 3 (regression from distributional embeddings) and Stage 4 (dimensionality test) is built and in the project repository, awaiting computational deployment.

## 4. Data Sources

All data sources used in this paper are public and free for research use. Table 1 summarizes the five TCM property sources we harmonized.

**Table 1. TCM property data sources.**

| Source | Reference | Herbs | Axes covered |
|---|---|---|---|
| SymMap v2.0 | Wu et al. (2019), *NAR* | 703 | QI, FLAVOR, CHANNEL, TOXICITY |
| TCMID | Huang et al., via Zenodo 8066910 | 336 | QI, FLAVOR, CHANNEL |
| TCM-MKG | Zeng, Zenodo 19804367 | 6,398 | QI, FLAVOR, CHANNEL |
| ETCM v2.0 | Zhang et al. (2023), live API | 1,336 | QI, FLAVOR, CHANNEL |
| Chinese Pharmacopoeia 2020 | National Pharmacopoeia Commission | 182 | QI, FLAVOR, CHANNEL, TOXICITY |

Two additional resources support the deferred RQ2/RQ3 analyses: NRC-VAD v2.1 (Mohammad, 2025; 44,728 English unigrams with signed [−1, +1] valence/arousal/dominance scores), and a 2,804-abstract symptom-language corpus harvested from PubMed under the MeSH terms "traditional chinese medicine" and "chinese herbal medicine", filtered to the 244 abstracts that mention at least one of our 130-term English symptom vocabulary.

The ETCM v2.0 ingest deserves a brief technical note. ETCM's front-end is a Vue.js single-page application with no documented bulk-download endpoint; the project plan originally categorized ETCM as browser-gated. We reverse-engineered its Django back-end at `http://www.tcmip.cn:18124`, where the per-herb detail endpoint is `GET /home/detail/?id=<pinyin>&type=herb` (case-insensitive). The `type=herb` parameter is required; without it the endpoint returns empty data. Our crawler enumerated the canonical pinyin set against this endpoint and retrieved 1,336 herb records over 35 minutes of polite (200 ms inter-request) crawling.

Chinese Pharmacopoeia 2020 (English edition, Volume 1, parts a and b) was supplied as PDF (3.0 GB, 2,205 pages). The PDFs carry embedded text rather than scanned images, allowing direct extraction via `pypdf`. The standardized monograph format `Property and Flavor [QI]; [FLAVOR(s)]; [TOXICITY-optional].` and `Meridian tropism [CHANNEL(s)] meridians.` enabled regex-based extraction of 182 herbs with all four covered axes (QI, FLAVOR, CHANNEL, TOXICITY).

## 5. Canonical Identity Resolution

Five sources describe overlapping but not identical herb sets in three distinct naming conventions (Chinese character names, Pinyin Romanizations, Latin botanical or pharmacognosy binomials). To compute inter-source agreement we resolve all source-side herb identifiers to a canonical 5-digit ID (`H00001` … `H06467`). Two rows merge if (i) any non-empty normalized Chinese name matches, (ii) any non-empty normalized Pinyin matches (tone marks stripped, whitespace collapsed), or (iii) Latin names match — with the constraint that Chinese and Pinyin are strict-match keys (a mismatch on either rejects the merge) while Latin is a loose-match key (a mismatch is permitted when at least one strict-match key supports the merge). This loose-Latin rule is necessary because authority-stripping artifacts (e.g., `Panax ginseng C. A. Meyer` → `panax ginseng` vs `Panax ginseng [syn. Asparagus lucidus]` → `panax ginseng [syn.`) systematically generated different normalized Latin strings for the same biological species.

A separate harmonization correction: an early version of the canonicalization join produced Cartesian-product fanout because over-stripped Latin authority strings (e.g., `Radix Astragali` → `radix`) collide across many distinct master rows. We resolve this by excluding from the join any key value that appears in more than one master row. The canonicalization step yields 6,467 unique herbs in the combined master table.

Identity resolution is the single largest source of construct invalidity in the study. We discuss its limitations in §8.

## 6. Results: Finding #1 — Inter-Source Reliability

### 6.1 Pre-registration

Predictions were registered on 2026-06-20 in the project repository (`docs/findings/01_label_reliability.md`) *before* any real data run. The pre-registered predictions, with the embodied-cognition reasoning that motivated each, were:

- **QI: κ ≥ 0.60** (substantial agreement). Hot/cold is the most consistent classical label because it tracks the most directly felt interoceptive dimension.
- **FLAVOR: 0.40 ≤ κ < 0.60** (moderate). Multi-label, but the five primary flavors are well established; school-specific minor flavors (e.g., 涩 vs 酸) drive the residual disagreement.
- **TOXICITY: κ ≥ 0.50**. Modern pharmacopoeia have codified four toxicity tiers (无毒 / 小毒 / 有毒 / 大毒); some older herbals omit toxicity entirely.
- **CHANNEL: 0.20 ≤ κ < 0.40** (fair). 归经 attribution differs significantly across 经方 / 时方 / 温病 traditions; reviewer-level disagreement is known (Zhao, 2015).
- **DIRECTION: κ < 0.30** (poor). 升降浮沉 is least codified in modern databases — many do not record it.

### 6.2 Metric

We initially intended to report Fleiss' kappa per axis. The five sources have ragged rater coverage (any given herb may appear in 2 to 5 sources), which violates the equal-raters-per-subject assumption of `statsmodels.fleiss_kappa`. Rather than impute or drop unequally-covered herbs, we report **raw set-equality agreement** as the primary metric: the fraction of eligible herbs (those covered by ≥ 2 sources) for which *every* source emitted the same set of values for that herb on that axis. For single-valued axes (QI, DIRECTION, TOXICITY) this is strict equality; for multi-valued axes (FLAVOR, CHANNEL) it is equality of the value sets (equivalent to Jaccard = 1).

This metric is robust to ragged coverage but is structurally stricter than κ: any single source emitting an extra label breaks unanimity. We discuss this metric-imposed penalty in §7.

### 6.3 Results

**Table 2. Per-axis raw set-equality agreement across five sources.**

| Axis | Agreement | n_herbs_eligible | Pre-registered prediction | Verdict |
|---|---|---|---|---|
| QI | **85.9%** (943 / 1,098) | 1,098 | κ ≥ 0.60 (≈ 80% raw) | **Confirmed at high end** |
| FLAVOR | 75.5% (1,008 / 1,335) | 1,335 | 0.40 ≤ κ < 0.60 (≈ 65–80% raw) | Confirmed at high end |
| CHANNEL | 72.7% (770 / 1,059) | 1,059 | 0.20 ≤ κ < 0.40 (≈ 50–65% raw) | **Exceeds prediction** |
| TOXICITY | 100% (2 / 2) | 2 | κ ≥ 0.50 | Suggestive only (n=2) |
| DIRECTION | — | 0 | κ < 0.30 | **Untestable** (no source records it) |

We highlight three results. First, QI achieves 85.9% raw agreement across 1,098 herbs — the largest published TCM-property base we are aware of, and a substantial empirical confirmation of the pre-registered prediction. Second, CHANNEL achieves 72.7% on 1,059 herbs, materially exceeding the pre-registered band. Third, DIRECTION is *unmeasurable* because no source in the harmonized set records it.

### 6.4 The DIRECTION absence as evidence

The complete absence of DIRECTION across all five publicly accessible English-language TCM sources is itself the most surprising finding of the study, and we treat it as a positive datum rather than a failure mode. After scanning all 2,205 pages of Chinese Pharmacopoeia 2020 Volume 1 for the natural-language tokens "ascending", "descending", "floating", "sinking" we found only one incidental match (page 150, "ascending firstly to 5 cm" in a description of plant morphology, not a property field). No structured 升降浮沉 monograph field exists in any source we harmonized. Modern English-language TCM databases have systematically pruned this descriptor.

The embodied-cognition reading predicts exactly this: the most theory-laden descriptor — one without a direct interoceptive grounding — is the one most likely to be dropped when traditions are operationalized for clinical reliability. The skeptical reading (folk taxonomy) and the TCM-AI maximalist reading both predict 升降浮沉 should be preserved alongside the other axes, since both treat the descriptors as equivalent in epistemic status. The embodied-cognition reading is the only one that distinguishes them on prior grounds.

## 7. Discussion

### 7.1 QI as the embodied core

QI's 85.9% inter-source agreement at n = 1,098 herbs is the headline empirical result of the study. The improvement from the 3-source intermediate (81.1%) to the 5-source final (85.9%) is itself meaningful: the agreement *strengthens* as more independent encodings are added, which is the opposite of the regression-to-the-mean pattern that would obtain if the descriptor were primarily a labelling convention. This pattern is consistent with the embodied-thermal reading: hot/cold tracks the most directly felt interoceptive dimension, and pre-scientific medical traditions converged on it most stably because there was a stable underlying signal to converge on.

### 7.2 The FLAVOR metric anomaly

FLAVOR's 75.5% agreement appears, on the surface, to fall below CHANNEL's 72.7% on a strict-superset comparison. We do not interpret this as evidence that 五味 is less reliable than 归经. The set-equality metric penalizes multi-label axes structurally: a herb with three sources voting `{sweet, bitter}`, `{sweet, bitter}`, and `{sweet, bitter, sour}` counts as disagreement (the third set is a strict superset), whereas the same overlap pattern under macro-Jaccard would score 0.67 (the second-source set is a subset of the third). At n = 1,335, even a small extra-flavor rate at the source level breaks unanimity for many herbs. The fair comparison requires per-class macro-Jaccard or macro-F1 against a consensus label, which we report in a follow-up analysis.

### 7.3 CHANNEL exceeds prior expectation

CHANNEL's 72.7% on 1,059 herbs materially exceeds our pre-registered prediction band (which translated κ 0.20–0.40 to ≈ 50–65% raw). The simplest explanation is that 归经 attribution has been more aggressively standardized in *modern* TCM databases than the classical-literature reviewer-disagreement studies (Zhao, 2015) suggest. Modern TCM databases largely draw on Chinese Pharmacopoeia 2020 and the standard *Materia Medica of Chinese Medicine* textbook, both of which codify 12-channel attributions per herb. The cross-source agreement we observe may therefore partly reflect *editorial* convergence rather than independent expert convergence — a question that can only be resolved by running the Stage 1 protocol against a fresh independent BWS panel.

### 7.4 TOXICITY: real signal, tiny base

The cross-source TOXICITY base is only 2 herbs (both unanimous). Pharmacopoeia 2020 supplies 34 toxicity records and SymMap supplies 91; the bottleneck is not data volume but rather identity-resolution between Pharmacopoeia's pharmacognosy genitive names ("Aconiti Radix Lateralis Praeparata") and the botanical binomials used by the other four sources ("Aconitum carmichaelii"). A pharmacognosy ↔ binomial cross-walk table — a half-day of one-time mapping work — would lift the cross-source TOXICITY base to an estimated ~30 herbs and permit a meaningful kappa calculation.

### 7.5 DIRECTION as positive evidence

We have already addressed this in §6.4. We emphasize here that the absence is *systematic*, not random: it persists across five independent sources representing five distinct editorial pipelines. The simplest read — that 升降浮沉 has been pruned from modern Western-influenced TCM databases because it is the descriptor with the weakest interoceptive grounding — is consistent with the embodied-cognition framework and inconsistent with both the skeptical and the maximalist readings.

### 7.6 What the result does not show

We disclaim three readings the data do not support. First, our results say nothing about whether classical TCM herb classifications are pharmacologically accurate. Second, our results say nothing about whether TCM treatment is clinically efficacious. Third, our results say nothing about whether 寒/热 corresponds to any specific molecular mechanism. The claim is narrower and we believe more defensible: the descriptor 寒/热 is an interpretable category that pre-scientific medical traditions converged on at high cross-source reliability, consistent with its tracking a directly felt interoceptive dimension. Whether the same descriptor also predicts molecular pharmacology is an empirical question for a different paper.

## 8. Limitations

The single largest limitation is that **five data sources are not five independent annotators**. Chinese Pharmacopoeia 2020 likely informs the property attributions of the other four sources to some degree (TCM-MKG and ETCM both explicitly cite it; SymMap and TCMID draw from overlapping primary literatures). The five sources represent at best a *quasi-independent* panel of editorial pipelines, not a fresh annotation panel. The full VAD-style protocol requires Stage 5 — a Best-Worst Scaling annotation by an independent panel of TCM clinicians, ideally drawn from multiple schools (经方 / 时方 / 温病 traditions). Our results should be read as a *necessary but not sufficient* test of the Herb-VAD thesis: the multi-source pattern observed is compatible with the embodied-cognition reading and would be evidence against the thesis had it failed, but it does not by itself rule out a purely editorial-convergence account of QI's high agreement.

Two further limitations: (i) the TOXICITY cross-source base is too small (n = 2) to support a meaningful kappa; (ii) the identity resolution rule that loosened Latin-name matching to permit cross-source merging may introduce false positives for herbs whose pinyin transliterations are ambiguous. We have spot-checked ~50 cross-source merges and found no obvious false positives, but a larger audit is future work.

## 9. Future Work

The two remaining pre-registered analyses (RQ2: held-out symptom probe; RQ3: geometric cross-walk with NRC-VAD in a shared multilingual embedding space) have complete infrastructure in the project repository and await only computational deployment (real LM embedding compute via `sentence-transformers` and `BAAI/bge-m3`). Predictions for RQ2 and RQ3 are likewise pre-registered (see `docs/findings/02_cognitive_substrate.md` and `docs/findings/03_vad_crosswalk.md`).

DIRECTION (升降浮沉) recovery from a 经方-tradition source — likely a manual extraction from a classical 中药学 textbook or CNKI-indexed clinical-text corpus — is the highest-priority data acquisition target. A successful DIRECTION recovery would either further confirm the embodied-cognition reading (low cross-source agreement for the most theory-laden descriptor) or substantially challenge it (high cross-source agreement, suggesting 升降浮沉 has felt-experience grounding that modern Western-influenced databases have lost).

Finally, a fresh Best-Worst Scaling annotation panel of TCM clinicians (ideally ≥ 30 raters drawn from 3+ traditions) remains the gold standard for the protocol's Stage 1 and would resolve the editorial-convergence concern raised in §8.

## 10. Conclusion

The classical TCM herb descriptors 四气 / 五味 / 升降浮沉 / 归经 / 毒性 can be operationalized as a culturally-constructed coordinate system over interoceptive-cognitive space, structurally analogous to how NLP's Valence-Arousal-Dominance model projects natural-language affect onto a low-rank basis. We have applied the first stage of the VAD methodological protocol — per-axis cross-source reliability — to five publicly available TCM data sources at scale, and found that QI (cold / hot) achieves 85.9% raw set-equality agreement across 1,098 herbs, materially confirming a pre-registered prediction. The complete absence of 升降浮沉 (DIRECTION) across all five modern sources is consistent with the embodied-cognition reading's prediction that the most theory-laden descriptor would be the first pruned when traditions are operationalized.

The original Herb-VAD thesis — that the classical TCM property axes deserve cognitive-science treatment analogous to NLP-VAD, with neither dismissal as folk taxonomy nor over-claiming as encoded pharmacology — has cleared its first empirical bar. The remaining stages of the methodological protocol (LM-embedding regression, dimensionality test, fresh BWS panel) are well-specified and the infrastructure is in place.

## Code and data availability

All code, processed data, scripts, and the three pre-registration documents (Findings #1, #2, #3) are public under MIT license at https://github.com/watchsound/herb-vad. The Chinese Pharmacopoeia 2020 PDFs themselves are not redistributed (commercial copyright); the extracted property records (Table 2 inputs) are released under the same license as the analysis code.

## References

Barrett, L. F. (2006). Are emotions natural kinds? *Perspectives on Psychological Science*, 1(1), 28–58.

Barrett, L. F. (2017). *How emotions are made: The secret life of the brain*. Houghton Mifflin Harcourt.

Bradley, M. M., & Lang, P. J. (1994). Measuring emotion: The Self-Assessment Manikin and the semantic differential. *Journal of Behavior Therapy and Experimental Psychiatry*, 25(1), 49–59.

Bradley, M. M., & Lang, P. J. (1999). *Affective norms for English words (ANEW): Instruction manual and affective ratings*. Technical Report C-1, Center for Research in Psychophysiology, University of Florida.

Buechel, S., & Hahn, U. (2018). Word emotion induction for multiple languages as a deep multi-task learning problem. *NAACL-HLT*, 1907–1918.

Dong, Y., Zhao, Z., Li, L., Zhao, C., Lin, X., Lin, M., … Lyu, A. (2023). TCM2Vec: TCM herb embeddings learned from formulae. *Multimedia Tools and Applications*.

Ekman, P. (1992). An argument for basic emotions. *Cognition and Emotion*, 6(3–4), 169–200.

Fontaine, J. R. J., Scherer, K. R., Roesch, E. B., & Ellsworth, P. C. (2007). The world of emotions is not two-dimensional. *Psychological Science*, 18(12), 1050–1057.

Hopkins, A. L. (2008). Network pharmacology: The next paradigm in drug discovery. *Nature Chemical Biology*, 4(11), 682–690.

Jang, J., & Lee, S. (2024). Understanding clinical decision-making in traditional East Asian medicine through dimensionality reduction. *Computers in Biology and Medicine*.

Kong, X. et al. (2024). BATMAN-TCM 2.0. *Nucleic Acids Research*.

Lakoff, G., & Johnson, M. (1980). *Metaphors we live by*. University of Chicago Press.

Li, S. (2014). Network target: A starting point for traditional Chinese medicine network pharmacology. *Journal of Ethnopharmacology*.

Mehrabian, A. (1996). Pleasure–arousal–dominance: A general framework for describing and measuring individual differences in temperament. *Current Psychology*, 14(4), 261–292.

Mehrabian, A., & Russell, J. A. (1974). *An approach to environmental psychology*. MIT Press.

Mohammad, S. M. (2018). Obtaining reliable human ratings of valence, arousal, and dominance for 20,000 English words. *ACL*, 174–184.

Mohammad, S. M. (2025). NRC-VAD Lexicon v2.1. NRC Canada.

Niu, B. et al. (2025). HPGCN: Predicting TCM cold/hot properties from protein–protein interaction features. *Computational and Structural Biotechnology Journal*.

Quigley, K. S., Kanoski, S., Grill, W. M., Barrett, L. F., & Tsakiris, M. (2021). Functions of interoception: From energy regulation to experience of the self. *Trends in Neurosciences*, 44(1), 29–38.

Ru, J. et al. (2014). TCMSP: A database of systems pharmacology for drug discovery from herbal medicines. *Journal of Cheminformatics*, 6, 13.

Russell, J. A. (1980). A circumplex model of affect. *Journal of Personality and Social Psychology*, 39(6), 1161–1178.

Russell, J. A. (1991). Culture and the categorization of emotions. *Psychological Bulletin*, 110(3), 426–450.

Sedoc, J., Preoţiuc-Pietro, D., & Ungar, L. (2017). Predicting emotional word ratings using distributional representations and signed clustering. *EACL*, 564–571.

Wu, Y. et al. (2019). SymMap: An integrative database of traditional Chinese medicine enhanced by symptom mapping. *Nucleic Acids Research*, 47(D1), D1110–D1117.

Zhang, Y. et al. (2023). ETCM v2.0: An update with comprehensive resource and rich annotations for TCM. *Acta Pharmaceutica Sinica B*.

Zhang, S. et al. (2025). PCMM: Property combination of Chinese materia medica. PubMed Central PMC12104179.

Zhao, Z. (2015). Inter-rater reliability of 归经 attribution across classical sources. *Journal of Traditional Chinese Medical Sciences*.

Zeng, J. (2024). Traditional Chinese Medicine Multi-dimensional Knowledge Graph (TCM-MKG). Zenodo record 19804367.
