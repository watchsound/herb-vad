# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Nature

This is **not a software project**. The directory contains a single Markdown essay, [herb-VAD.md](herb-VAD.md), exploring a conceptual mapping from Traditional Chinese Medicine (TCM) herb pharmacology to NLP/ML representation theory.

There is no source code, no build system, no package manifest, no tests, and no git history. Do not invent commands, scripts, or architecture. If asked to "run," "build," "test," or "lint" anything, surface that no such tooling exists before suggesting next steps.

## Core Concept: Herb-VAD

The essay proposes that the classical TCM herb descriptors (四气, 五味, 升降浮沉, 归经, 毒性) are a hand-crafted, interpretable low-dimensional projection of a high-dimensional **physiological homeostatic phase space** — analogous to how NLP's **VAD (Valence, Arousal, Dominance)** is a projection of semantic embedding space.

The central mapping the document develops:

| TCM dimension | NLP/ML analogue | Proposed mathematical role |
| --- | --- | --- |
| 四气 (cold/hot) | Valence | Thermodynamic gradient on metabolic rate |
| 毒性 (toxicity) | Arousal | Gain / learning rate of the state-transition step |
| 升降浮沉 (direction) | Dominance | Vector field direction over the physiological manifold |
| 归经 (channel affinity) | Attention mask | Topological addressing into a subgraph of organ networks |
| 五味 (five flavors) | Activation function | Operator type (辛≈ReLU, 酸≈Sigmoid, 甘≈smoothing) |

A prescription (方剂) is then framed as a weighted tensor sum  T_prescription = Σ w_i · T_herb_i, with the classical 君臣佐使 roles mapped to principal vector, correction vector, anti-overfit reverse perturbation, and pure attention-mask routing respectively.

The essay closes by extrapolating to **inverse molecular generation** — using the Herb-VAD coordinate system as a prompt to a generative model that synthesizes de novo "cyber-herb" compound clusters.

## Working Style for This Repo

- Treat the file as a living thesis. When asked to edit, preserve the author's voice and the bilingual (Chinese-dominant, English technical terms) register.
- The technical analogies are deliberately aggressive ("认知核爆", "降维打击"). Do not soften them unless asked.
- Mathematical notation is LaTeX-in-Markdown (`$...$`, `$$...$$`); keep that convention.
- The table column "数学与物理本质 (AI 架构解释)" is the load-bearing axis of the argument — edits there ripple through the rest of the essay's logic.
