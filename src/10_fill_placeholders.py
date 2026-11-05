"""Step 10 - fill the submission placeholders and rebuild the Word files.

Three files promise a public repository URL and the cover letter needs a date.
Editing them by hand risks missing one, so this fills all four at once and
reports anything still outstanding.

    python src/10_fill_placeholders.py --url https://github.com/you/repo
    python src/10_fill_placeholders.py --url ... --date "5 November 2026"
    python src/10_fill_placeholders.py --check

With --check it only reports what is still unfilled, changing nothing.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from khp_lta import config as cfg

MANUSCRIPT_DIR = cfg.PROJECT_ROOT / "manuscript"

# A Markdown formatter escapes the brackets, so "[GITHUB URL]" may sit in the
# file as "\[GITHUB URL\]". Both forms have to match, or a placeholder in a
# reformatted file is silently left in the submitted manuscript.
URL_PATTERNS = [
    r"\\?\[GITHUB URL TO BE INSERTED AT SUBMISSION\\?\]",
    r"\\?\[GITHUB URL\\?\]",
]
DATE_PATTERN = r"\\?\[DATE\\?\]"


def outstanding() -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    for md in sorted(MANUSCRIPT_DIR.glob("0*.md")):
        text = md.read_text(encoding="utf-8")
        hits = []
        for pat in URL_PATTERNS + [DATE_PATTERN]:
            hits += re.findall(pat, text)
        if hits:
            found[md.name] = hits
    return found


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", help="public URL of the pushed repository")
    ap.add_argument("--date", help="date for the cover letter "
                                   "(default: today, as '5 November 2026')")
    ap.add_argument("--check", action="store_true",
                    help="only report what is unfilled")
    ap.add_argument("--no-rebuild", action="store_true",
                    help="do not regenerate the .docx files afterwards")
    args = ap.parse_args()

    if args.check or not args.url:
        left = outstanding()
        if not left:
            print("Nothing outstanding: no placeholders remain.")
            return 0
        print("Still to fill:")
        for name, hits in left.items():
            print(f"  {name:<26} {', '.join(sorted(set(hits)))}")
        if not args.url:
            print("\nPass --url https://github.com/<account>/<repo> to fill them.")
        return 0

    if not args.url.startswith("https://"):
        print(f"That does not look like a URL: {args.url}")
        return 1

    when = args.date or f"{date.today().day} {date.today():%B %Y}"
    changed = []
    for md in sorted(MANUSCRIPT_DIR.glob("0*.md")):
        text = original = md.read_text(encoding="utf-8")
        for pat in URL_PATTERNS:
            text = re.sub(pat, args.url, text)
        text = re.sub(DATE_PATTERN, when, text)
        if text != original:
            md.write_text(text, encoding="utf-8")
            changed.append(md.name)

    print(f"url  {args.url}")
    print(f"date {when}")
    print(f"updated: {', '.join(changed) if changed else 'nothing to change'}")

    left = outstanding()
    if left:
        print("\nStill outstanding:")
        for name, hits in left.items():
            print(f"  {name:<26} {', '.join(sorted(set(hits)))}")

    if changed and not args.no_rebuild:
        print("\nrebuilding the Word files")
        subprocess.run([sys.executable, "-I",
                        str(Path(__file__).parent / "08_make_docx.py")], check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
