"""Embed NRC-VAD (+ CVAW if available) with the BGE-M3 sentence encoder.

Requires the ``[ml]`` extra:
    pip install -e ".[ml]"

Reads:
  - data/interim/nrc_vad_en.parquet (produced by scripts/01_parse_nrc_vad.py)
  - data/interim/cvaw.parquet       (optional; produced by scripts/01_parse_cvaw.py)

Writes:
  - data/processed/vad_embeddings.parquet
"""

from __future__ import annotations

from pathlib import Path

import polars as pl

from herb_vad.crosswalk.vad_embed import combine_vad_corpora, embed_vad_lexicon
from herb_vad.embeddings.embedder import LMEmbedder

NRC_VAD = Path("data/interim/nrc_vad_en.parquet")
CVAW = Path("data/interim/cvaw.parquet")
OUT = Path("data/processed/vad_embeddings.parquet")


def main() -> None:
    if not NRC_VAD.exists():
        raise SystemExit(f"Missing {NRC_VAD}. Run scripts/01_parse_nrc_vad.py first.")
    embedder = LMEmbedder("BAAI/bge-m3")

    frames: list[pl.DataFrame] = []
    nrc = pl.read_parquet(NRC_VAD)
    print(f"Embedding NRC-VAD-en ({nrc.height} terms)…")
    frames.append(embed_vad_lexicon(nrc, embedder, lang="en"))

    if CVAW.exists():
        cvaw = pl.read_parquet(CVAW)
        print(f"Embedding CVAW-zh ({cvaw.height} terms)…")
        frames.append(embed_vad_lexicon(cvaw, embedder, lang="zh"))
    else:
        print(f"(skipping CVAW: {CVAW} not present)")

    out = combine_vad_corpora(frames)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.write_parquet(OUT)
    langs = sorted(out["lang"].unique().to_list())
    print(f"Wrote {OUT}: {out.height} term embeddings ({langs}).")


if __name__ == "__main__":
    main()
