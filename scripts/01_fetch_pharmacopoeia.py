"""Extract & parse Chinese Pharmacopoeia 2020 (English edition) PDFs.

Expects ``PHARMACOPOEIA-1a.pdf`` and ``PHARMACOPOEIA-1b.pdf`` at the
repo root (large; gitignored). The script:

1. Extracts each PDF's text via ``pypdf`` (~2 min total for ~3 GB
   across 2,200 pages) into ``data/raw/pharmacopoeia/{1a,1b}.txt``,
   skipping the extraction step if the text files already exist.
2. Runs ``parse_pharmacopoeia_files`` to identify Property and Flavor
   + Meridian tropism blocks, emit canonical property records, and
   write ``data/interim/pharmacopoeia.parquet``.

ChP 2020 carries QI / FLAVOR / CHANNEL / TOXICITY but NOT direction.
"""

from __future__ import annotations

from pathlib import Path

from herb_vad.ingest.pharmacopoeia import parse_pharmacopoeia_files

PDFS = {
    Path("PHARMACOPOEIA-1a.pdf"): Path("data/raw/pharmacopoeia/1a.txt"),
    Path("PHARMACOPOEIA-1b.pdf"): Path("data/raw/pharmacopoeia/1b.txt"),
}
OUT = Path("data/interim/pharmacopoeia.parquet")


def _extract_pdf(pdf_path: Path, text_path: Path) -> None:
    import pypdf

    text_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"Extracting {pdf_path} -> {text_path} ...")
    with pdf_path.open("rb") as fh:
        r = pypdf.PdfReader(fh)
        chunks: list[str] = []
        for page in r.pages:
            try:
                chunks.append(page.extract_text() or "")
            except Exception:  # noqa: BLE001 — pypdf raises a zoo on dirty PDFs
                chunks.append("")
    text_path.write_text("\n".join(chunks), encoding="utf-8")
    print(f"  wrote {text_path.stat().st_size} bytes")


def main() -> None:
    for pdf_path, text_path in PDFS.items():
        if text_path.exists():
            continue
        if not pdf_path.exists():
            raise SystemExit(
                f"Missing {pdf_path}. Place Chinese Pharmacopoeia 2020 English "
                f"edition PDFs at {list(PDFS.keys())}."
            )
        _extract_pdf(pdf_path, text_path)

    df = parse_pharmacopoeia_files(list(PDFS.values()))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.write_parquet(OUT)
    if df.height:
        axes = sorted(df["axis"].unique().to_list())
        n_herbs = df["latin"].n_unique()
        print(f"Wrote {OUT}: {df.height} rows, {n_herbs} herbs, axes {axes}")
    else:
        print(f"Wrote {OUT}: empty.")


if __name__ == "__main__":
    main()
