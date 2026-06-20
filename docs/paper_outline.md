# Paper outline — Herb-VAD: cognitive cartography of classical Chinese-medicine herb descriptors

**Target venue:** *Cognitive Science* / *Cognition* / CogSci proceedings / *Frontiers in Psychology*.

## §1. Introduction

- Open with the framing: classical TCM herb descriptors (四气/五味/升降浮沉/归经/毒性)
  are a culturally constructed coordinate system over **interoceptive-cognitive
  space**, not over molecular pharmacology.
- Position NLP's VAD (Valence/Arousal/Dominance; Mohammad 2018) as the
  methodological template for empirically validating any low-D affective
  taxonomy.
- Headline claim: 性味归经 can be *cross-walked* with NLP-VAD in a shared
  multilingual embedding space, partitioning the same underlying
  folk-psychological manifold differently.

## §2. Related work

- Dimensional affect: Russell 1980, Mehrabian & Russell 1974, Bradley & Lang
  1999 ANEW, Mohammad 2018 NRC-VAD, Buechel & Hahn 2017 EmoBank.
- Embodied cognition: Lakoff & Johnson 1980 *Metaphors We Live By*; Barrett
  2017 *How Emotions Are Made* (constructionist account).
- TCM informatics: Shao Li's network-target theory (Li 2014); TCM2Vec
  (Dong 2023); HPGCN (Niu 2025); PCMM (Zhang 2025); Jang & Lee 2024
  Eight-Principles dim reduction.
- Cross-cultural emotion: Cowen & Keltner 2017 (27 categories of affect);
  Wierzbicka NSM; Fontaine 2007.

## §3. Data (all public)

- TCM property labels: SymMap, TCMSP, ETCM v2.0, BATMAN-TCM 2.0, HERB.
- Affective lexicons: NRC-VAD v2.1 (Mohammad 2025), CVAW (Yu et al.).
- Corpora: Chinese Text Project (Shen Nong Ben Cao Jing, Bencao Gangmu, Shang Han Lun, Jin Gui Yao Lue); PubMed Chinese TCM abstracts.

## §4. Method

- §4.1 Canonical-id resolution across the five TCM databases.
- §4.2 Consensus voting + Fleiss κ for per-axis reliability.
- §4.3 Per-herb text representations (definition / indication / concat / indication-masked).
- §4.4 LM embeddings (BGE-M3 primary, multilingual-e5-large fallback) + formula-cooc embedding (skip-gram W2V).
- §4.5 Linear-probe protocol (5-fold stratified CV; one-vs-rest for multi-label axes).
- §4.6 Held-out symptom probe (train on herb-text, test on property-masked symptom passages).
- §4.7 Cross-walk: Procrustes + CCA alignment between herb-embedding space and VAD-embedding space.

## §5. Results

- **Finding 1 (Task 14)** — Inter-database reliability per axis.
- **Finding 2 (Task 20)** — Cognitive substrate of 性味归经 (held-out symptom probe macro-F1).
- **Finding 3 (Task 23)** — VAD ↔ TCM cross-walk: five pre-registered hypotheses, Holm-corrected.

## §6. Discussion

- TCM categories and Western dimensional affect carve the same interoceptive manifold differently — not isomorphically.
- Implications for cognitive science of medical traditions; not a pharmacology claim.
- Specific limitations: SymMap-class label noise, Han-Chinese cognitive bias of source materia medica, batch variability of herb chemistry (out of scope — addressed by anchoring everything in the cognitive/discursive layer, not the molecular layer).

## §7. Limitations

- Database labels as proxy for fresh BWS annotation.
- Chinese affective coverage (CVAW alone is small; NRC-VAD-zh helps).
- No causal claim about TCM efficacy.
- Single-language LMs may carry cultural bias.

## §8. Conclusion

- 性味归经 are a recoverable, partially-falsifiable cognitive coordinate system.
- Cross-walking with VAD opens cognitive science of medical traditions to systematic empirical work.

## Appendix

- Reproducibility: every figure has a generating script and a deterministic seed; the entire pipeline runs from public data with `[ml,viz]` extras installed.
- Code + processed data: https://github.com/watchsound/herb-vad
