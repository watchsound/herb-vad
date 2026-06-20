"""Parse the downloaded NRC-VAD v2.1 unigrams file → parquet.

Expects ``data/raw/nrc_vad/NRC-VAD-Lexicon-v2.1/Unigrams/unigrams-NRC-VAD-Lexicon-v2.1.txt``
to exist (the v2.1 zip released April 2025 places the English unigrams
there). Writes ``data/interim/nrc_vad_en.parquet``.
"""

from __future__ import annotations

from pathlib import Path

from herb_vad.ingest.nrc_vad import parse_nrc_vad

RAW = Path("data/raw/nrc_vad/NRC-VAD-Lexicon-v2.1/Unigrams/" "unigrams-NRC-VAD-Lexicon-v2.1.txt")
OUT = Path("data/interim/nrc_vad_en.parquet")


def main() -> None:
    if not RAW.exists():
        raise SystemExit(f"Missing {RAW}. See data/raw/nrc_vad/ for layout.")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df = parse_nrc_vad(RAW)
    df.write_parquet(OUT)
    print(
        f"Wrote {OUT}: {df.height} terms; "
        f"V range [{df['valence'].min():.3f}, {df['valence'].max():.3f}]; "
        f"A range [{df['arousal'].min():.3f}, {df['arousal'].max():.3f}]; "
        f"D range [{df['dominance'].min():.3f}, {df['dominance'].max():.3f}]."
    )


if __name__ == "__main__":
    main()
