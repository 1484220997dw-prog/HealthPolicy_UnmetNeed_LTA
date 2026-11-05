"""Step 09 - render the .docx files to PDF so the layout can be looked at.

Checking a Word file by reading its XML catches missing content but not how it
sits on the page. This step converts each submission file with LibreOffice and
reports the page count and orientation, so a broken table or a caption that has
come adrift is visible without opening Word.

Needs LibreOffice. Set SOFFICE to its path if it is not in one of the usual
places. The PDFs are a convenience for the authors, not submission files:
Elsevier wants the .docx.

Writes output/preview/*.pdf.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from khp_lta import config as cfg

MANUSCRIPT_DIR = cfg.PROJECT_ROOT / "manuscript"
PREVIEW_DIR = cfg.OUTPUT_DIR / "preview"

CANDIDATES = [
    r"C:\Program Files\LibreOffice\program\soffice.exe",
    r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    "/Applications/LibreOffice.app/Contents/MacOS/soffice",
    "/usr/bin/soffice",
    "/usr/bin/libreoffice",
]


def find_soffice() -> str | None:
    override = os.environ.get("SOFFICE")
    if override and Path(override).exists():
        return override
    for path in CANDIDATES:
        if Path(path).exists():
            return path
    from shutil import which
    return which("soffice") or which("libreoffice")


def main() -> int:
    soffice = find_soffice()
    if soffice is None:
        print("LibreOffice not found. Install it, or set SOFFICE to its path.")
        print("This step is optional: it only renders the .docx files for review.")
        return 0

    docs = sorted(MANUSCRIPT_DIR.glob("0*.docx"))
    if not docs:
        print("No .docx files yet; run src/08_make_docx.py first.")
        return 1

    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    print(f"rendering {len(docs)} files with {soffice}")
    subprocess.run([soffice, "--headless", "--norestore", "--convert-to", "pdf",
                    "--outdir", str(PREVIEW_DIR)] + [str(d) for d in docs],
                   check=True, capture_output=True, timeout=600)

    try:
        import pymupdf
    except ImportError:
        print(f"\nwrote PDFs to {PREVIEW_DIR}")
        print("install pymupdf for the page-by-page report")
        return 0

    print(f"\n{'file':<28}{'pages':>7}  orientation")
    for doc in docs:
        pdf = PREVIEW_DIR / (doc.stem + ".pdf")
        if not pdf.exists():
            print(f"{doc.name:<28}{'FAILED':>7}")
            continue
        with pymupdf.open(pdf) as rendered:
            shapes = {("landscape" if p.rect.width > p.rect.height else "portrait")
                      for p in rendered}
            print(f"{pdf.name:<28}{rendered.page_count:>7}  "
                  f"{', '.join(sorted(shapes))}")
    print(f"\nwrote {PREVIEW_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
