"""Parse CVAW3 -> parquet, once downloaded.

CVAW3 is distributed from http://nlp.innobic.yzu.edu.tw/resources/cvaw.html
(Yu et al.). Download the CSV and place it at
``data/raw/cvaw/CVAW.csv`` (column headers include Word / Valence_Mean /
Arousal_Mean - casing may vary). Writes ``data/interim/cvaw.parquet``.
"""

from __future__ import annotations

from pathlib import Path

from herb_vad.ingest.cvaw import parse_cvaw

RAW = Path("data/raw/cvaw/CVAW.csv")
OUT = Path("data/interim/cvaw.parquet")


def main() -> None:
    if not RAW.exists():
        raise SystemExit(
            f"Missing {RAW}. Download CVAW3 from "
            "http://nlp.innobic.yzu.edu.tw/resources/cvaw.html and place it there."
        )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df = parse_cvaw(RAW)
    df.write_parquet(OUT)
    print(
        f"Wrote {OUT}: {df.height} terms; "
        f"V range [{df['valence'].min():.3f}, {df['valence'].max():.3f}]; "
        f"A range [{df['arousal'].min():.3f}, {df['arousal'].max():.3f}]; "
        "D = null (CVAW has no dominance)."
    )


if __name__ == "__main__":
    main()
