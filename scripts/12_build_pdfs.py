"""Build PDFs of the Herb-VAD paper drafts from Markdown.

Pipeline: Markdown -> HTML (pandoc, with academic-paper CSS) -> PDF
(Chrome / Edge --headless --print-to-pdf). This avoids LaTeX font
configuration headaches, particularly for the Chinese version where
xelatex CJK font setup is brittle.

Outputs ``docs/paper/herb_vad_{en,zh}.pdf`` (gitignored as binary).
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PAPER_DIR = REPO / "docs" / "paper"

CHROME_CANDIDATES = [
    Path("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"),
    Path("C:/Program Files/Google/Chrome/Application/chrome.exe"),
    Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"),
    Path("C:/Program Files/Microsoft/Edge/Application/msedge.exe"),
]

CSS_EN = """
@page { size: A4; margin: 0.9in 0.85in; }
body {
  font-family: 'Times New Roman', 'Liberation Serif', serif;
  font-size: 11pt;
  line-height: 1.45;
  text-align: justify;
  color: #111;
  max-width: 7in;
  margin: 0 auto;
}
h1 { font-size: 17pt; text-align: center; margin: 0 0 0.4em 0; line-height: 1.2; }
h2 { font-size: 13pt; margin: 1.4em 0 0.4em 0; border-bottom: 1px solid #999; padding-bottom: 2pt; }
h3 { font-size: 11.5pt; margin: 1em 0 0.3em 0; font-weight: bold; }
p { margin: 0 0 0.5em 0; }
table { border-collapse: collapse; margin: 0.6em 0; font-size: 10pt; width: 100%; }
th, td { border: 1px solid #999; padding: 4pt 6pt; vertical-align: top; }
th { background: #eee; font-weight: bold; }
code { font-family: 'Courier New', monospace; font-size: 10pt; background: #f4f4f4; padding: 1pt 3pt; border-radius: 2pt; }
pre { background: #f4f4f4; padding: 8pt; border-left: 3pt solid #888; font-size: 10pt; overflow-x: auto; }
blockquote { border-left: 3pt solid #888; margin: 0.5em 0; padding-left: 12pt; color: #444; }
hr { border: none; border-top: 1px solid #aaa; margin: 1em 0; }
em { font-style: italic; }
strong { font-weight: bold; }
"""

CSS_ZH = (
    CSS_EN.replace(
        "font-family: 'Times New Roman', 'Liberation Serif', serif;",
        (
            "font-family: 'Source Han Serif SC', 'Noto Serif CJK SC', "
            "'Microsoft YaHei', 'SimSun', 'Songti SC', serif;"
        ),
    )
    + "\n"
    "h1, h2, h3 { "
    "font-family: 'Source Han Sans SC', 'Noto Sans CJK SC', "
    "'Microsoft YaHei', 'SimHei', sans-serif; "
    "}\n"
)


def _find_chrome() -> Path:
    for cand in CHROME_CANDIDATES:
        if cand.exists():
            return cand
    raise SystemExit(
        "No Chrome or Edge found. Install one of them, or expose a chrome.exe / msedge.exe."
    )


def _md_to_html(md_path: Path, html_path: Path, css: str) -> None:
    if shutil.which("pandoc") is None:
        raise SystemExit("pandoc not found on PATH. Install pandoc and retry.")
    css_path = html_path.with_suffix(".css")
    css_path.write_text(css, encoding="utf-8")
    cmd = [
        "pandoc",
        str(md_path),
        "-o",
        str(html_path),
        "--standalone",
        "--toc",
        "--toc-depth=3",
        f"--css={css_path.name}",
    ]
    print(f"$ {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


def _html_to_pdf(html_path: Path, pdf_path: Path) -> None:
    chrome = _find_chrome()
    cmd = [
        str(chrome),
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        f"--print-to-pdf={pdf_path}",
        "--print-to-pdf-no-header",
        f"file:///{html_path.as_posix()}",
    ]
    print(f"$ {chrome.name} --headless --print-to-pdf={pdf_path.name} {html_path.name}")
    subprocess.run(cmd, check=True)


def build(md_path: Path, lang: str, css: str) -> Path:
    stem = md_path.stem
    html_path = md_path.with_suffix(".html")
    pdf_path = md_path.with_suffix(".pdf")
    print(f"\n=== Building {lang}: {stem} ===")
    _md_to_html(md_path, html_path, css)
    _html_to_pdf(html_path, pdf_path)
    print(f"Wrote {pdf_path} ({pdf_path.stat().st_size:,} bytes)")
    return pdf_path


def main() -> None:
    en_md = PAPER_DIR / "herb_vad_en.md"
    zh_md = PAPER_DIR / "herb_vad_zh.md"
    if not en_md.exists() or not zh_md.exists():
        sys.exit(f"Missing paper drafts at {PAPER_DIR}.")
    build(en_md, "English", CSS_EN)
    build(zh_md, "Chinese", CSS_ZH)


if __name__ == "__main__":
    main()
