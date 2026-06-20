# ADR-0001: Task 1 scaffolding deviations

**Date:** 2026-06-20
**Status:** Accepted

## Context

`docs/plan.md` Task 1 specified `requires-python = ">=3.11,<3.13"`. The host workstation has Python 3.10 and 3.13 installed but no 3.11 or 3.12, and no `uv`. The implementer subagent stopped (correctly) and escalated.

## Decision

1. **Python version cap raised to `<3.14`** so the system Python 3.13 qualifies. The `<3.13` cap in the original plan was a conservative choice made when 3.13 was newer; all stack components in scope (polars, scikit-learn, statsmodels, transformers, sentence-transformers, torch ≥ 2.4) have stable 3.13 wheels as of the date of this ADR.

2. **Heavy ML dependencies moved to optional extras** (`ml`, `viz`, `chem`, `gpu`). The default install installs the analytics core only. Phases that need them install `pip install -e ".[ml,viz]"` etc. when they begin. Rationale: keeps Task 1's install fast and avoids Windows wheel-build failures (rdkit, torch_geometric) blocking unrelated tasks.

3. **Package name follows PyPI convention** — distribution name `herb-vad`, import name `herb_vad`. The plan's `herbvad` (no separator) was non-idiomatic; the plan's Task 2+ code references have been updated to `from herb_vad.…` to match.

4. **`pre-commit` added to `[dev]` extras** — the plan's `.pre-commit-config.yaml` step assumed it was installed; the original dev-extras list omitted it.

   **`dvc` and `duckdb` moved from defaults to a `[data]` extra.** Initial installs hung on PyPI from a Chinese ISP — first dvc's heavy transitive tree (celery, scmrepo, gto, sqltrie), then duckdb's 13 MB Windows wheel stalled even from the Tsinghua mirror. Neither dep is needed for Task 1 or Task 2. Splitting them off keeps per-task installs lean: `pip install -e ".[dev]"` for schemas/ingest code, `pip install -e ".[dev,data]"` when Task 3 initializes DVC and the analytics layer needs DuckDB. Polars covers the parquet I/O for Tasks 4–11.

   **Tsinghua mirror used by default for installs.** `-i https://pypi.tuna.tsinghua.edu.cn/simple` on the install command (no global config change). PyPI.org direct was unresponsive from this network; Tsinghua resolved metadata and downloaded successfully (except for the duckdb 13 MB wheel, which is why duckdb moved to `[data]`).

5. **README rewritten** — the first scaffolding pass produced a README with a hallucinated meaning for "VAD" ("Vector-Anchor Decomposition for herbal medicine analytics"). The actual project is cognitive cartography of TCM descriptors using NLP-VAD (Valence-Arousal-Dominance) as a methodological template. Fixed in the same commit as the scaffolding.

## Consequences

- Future tasks that need ML deps must run `pip install -e ".[ml]"` (and `.[viz]` for figures) as their first step. The plan documents this implicitly via task ordering but does not state it as an explicit step. Subsequent task prompts will include the install line where needed.
- `docs/plan.md` has been edited to reflect points 3 above. Other deviations (1, 2, 4, 5) are recorded only here, because they don't affect any subsequent task's interface or expected output.
