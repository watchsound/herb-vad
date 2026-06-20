"""Dump the curated symptom vocab to data/interim/symptom_vocab.txt."""

from __future__ import annotations

from pathlib import Path

from herb_vad.ingest.symptom_vocab import SYMPTOM_TERMS

OUT = Path("data/interim/symptom_vocab.txt")


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(SYMPTOM_TERMS) + "\n", encoding="utf-8")
    print(f"Wrote {OUT}: {len(SYMPTOM_TERMS)} terms.")


if __name__ == "__main__":
    main()
