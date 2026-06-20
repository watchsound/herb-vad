# Release procedure

## Cutting a tagged release

1. Ensure CI is green (`pytest -v` passes locally and on GitHub Actions).
2. Update the version in `pyproject.toml`, `CITATION.cff`, and `src/herb_vad/__init__.py`.
3. Tag and push:
   ```bash
   git tag -a vX.Y.Z -m "vX.Y.Z"
   git push origin vX.Y.Z
   ```
4. GitHub Actions (if configured) builds a sdist + wheel from the tag and attaches them to the GitHub Release.

## Documentation site (GitHub Pages)

The three pre-registration documents under `docs/findings/` are the
primary public-facing artifacts. To serve them as a GitHub Pages site:

1. In the repository settings, enable GitHub Pages from the `docs/`
   directory on `main`.
2. Add a top-level `docs/index.md` linking to:
   - `findings/01_label_reliability.md`
   - `findings/02_cognitive_substrate.md`
   - `findings/03_vad_crosswalk.md`
   - `plan.md`
   - `paper_outline.md`
3. The default Jekyll theme renders Markdown directly; no further
   config is needed.

## Data release

Raw TCM database dumps are not redistributable in their original form;
the project releases parsing scripts only. The NRC-VAD lexicon is
redistributable for research; CVAW is redistributable upon attribution.
Processed derived parquet artifacts (canonical_id mappings, embeddings)
can be released under MIT alongside the code.
