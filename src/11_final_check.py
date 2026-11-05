"""Step 11 - one pass over the whole package before submitting.

The other checks each look at one thing: step 07 at the manuscript's numbers and
limits, step 08 at the Word conversion, step 09 at the rendered layout. This
one looks for the problems that fall between them — a file the submission needs
that was never built, a name that was changed in one place and not another, a
placeholder still in the text, restricted data staged for a public repository.

It reports and exits non-zero on anything that would matter at submission.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from khp_lta import config as cfg

ROOT = cfg.PROJECT_ROOT
MS_DIR = ROOT / "manuscript"

UPLOAD_FILES = [
    "manuscript/01_cover_letter.docx",
    "manuscript/02_title_page.docx",
    "manuscript/03_credit_statement.docx",
    "manuscript/04_highlights.docx",
    "manuscript/05_manuscript.docx",
    "manuscript/06_appendix.docx",
    "output/figures/figure1_status_prevalence_and_persistence.tif",
]

# A name dropped from the author list must not survive anywhere in the package.
REMOVED_NAMES = ["HUO Ning", "Huo Ning", "0009-0002-6606-6726", "h1521378158"]

PLACEHOLDERS = [r"\[GITHUB URL", r"\[DATE\]", r"<your-account>", r"3,9xx",
                r"TO BE INSERTED", r"TODO", r"FIXME", r"XXX"]

results: list[tuple[bool, str, str]] = []


def check(ok: bool, label: str, detail: str = "") -> None:
    results.append((ok, label, detail))


def unescape(text: str) -> str:
    return re.sub(r"\\(.)", r"\1", text)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8", errors="replace")


def docx_text(path: str) -> str:
    from docx import Document
    doc = Document(ROOT / path)
    out = [p.text for p in doc.paragraphs]
    for table in doc.tables:
        for row in table.rows:
            out += [c.text for c in row.cells]
    return "\n".join(out)


def main() -> int:
    # ---- the files the submission needs ----------------------------------
    missing = [f for f in UPLOAD_FILES if not (ROOT / f).exists()]
    check(not missing, "all seven upload files exist", ", ".join(missing))

    stale = [f for f in UPLOAD_FILES if f.endswith(".docx")
             and (ROOT / f).stat().st_mtime
             < (MS_DIR / (Path(f).stem + ".md")).stat().st_mtime]
    check(not stale, "no .docx is older than its Markdown source",
          ", ".join(stale) + (" — rerun src/08_make_docx.py" if stale else ""))

    # ---- placeholders, in the Word files that actually get uploaded ------
    found = []
    for f in UPLOAD_FILES:
        if not f.endswith(".docx"):
            continue
        text = docx_text(f)
        for pat in PLACEHOLDERS:
            if re.search(pat, text):
                found.append(f"{Path(f).name}:{pat}")
    check(not found, "no placeholders left in the uploaded files",
          ", ".join(found))

    # ---- the removed author ----------------------------------------------
    hits = []
    for path in list(ROOT.rglob("*.md")) + list(ROOT.rglob("*.cff")) + [ROOT / "LICENSE"]:
        if ".git" in path.parts or "output" in path.parts:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for name in REMOVED_NAMES:
            if name in text:
                hits.append(f"{path.relative_to(ROOT)}:{name}")
    check(not hits, "the removed author appears nowhere", ", ".join(hits))

    # ---- anonymity of the reviewed files ---------------------------------
    # The repository URL belongs on the title page only: the account name
    # encodes the corresponding author's email identifier, and the repository
    # names both authors in its LICENSE and CITATION.cff, so a link in the
    # anonymised manuscript would undo the double-anonymised review.
    identifying = ["DU Haichao", "Wansuk Choi", "Kyungwoon", "1484220997",
                   "wschoi", "0009-0006-0839", "0000-0003-1324",
                   "github.com", "orcid.org"]
    leaks = [f"{name}:{w}" for name in ("05_manuscript.docx", "06_appendix.docx")
             for w in identifying if w in docx_text("manuscript/" + name)]
    check(not leaks, "the anonymised files carry nothing identifying",
          ", ".join(leaks))

    # ---- the authors who should be there ---------------------------------
    title_page = docx_text("manuscript/02_title_page.docx")
    credit = docx_text("manuscript/03_credit_statement.docx")
    check(all(n in title_page for n in ("DU Haichao", "Wansuk Choi")),
          "both authors on the title page")
    check(all(n in credit for n in ("DU Haichao", "Wansuk Choi")),
          "both authors in the CRediT statement")
    check("0009-0006-0839-1888" in title_page and "0000-0003-1324-6723" in title_page,
          "both ORCIDs on the title page")

    # ---- references -------------------------------------------------------
    md = unescape(read("manuscript/05_manuscript.md"))
    body, reflist = md.split("## References", 1)
    listed = [int(m.group(1)) for m in re.finditer(r"(?m)^\[(\d+)\]", reflist)]
    cited: list[int] = []
    for m in re.finditer(r"\[([0-9]+(?:\s*[,–-]\s*[0-9]+)*)\]", body):
        for part in m.group(1).split(","):
            part = part.strip()
            if part.isdigit():
                cited.append(int(part))
            else:
                a, b = re.split(r"[–-]", part)
                cited.extend(range(int(a), int(b) + 1))
    first = list(dict.fromkeys(cited))
    check(listed == list(range(1, len(listed) + 1)),
          f"reference list numbered 1-{len(listed)} without gaps")
    check(not set(listed) - set(cited), "every listed reference is cited",
          str(sorted(set(listed) - set(cited))))
    check(not set(cited) - set(listed), "every citation is listed",
          str(sorted(set(cited) - set(listed))))
    check(first == sorted(first), "references cited in order of first appearance")

    pdfs = sorted(p.name for p in (ROOT / "references").glob("*.pdf"))
    check(len(pdfs) == len(listed),
          f"one reference PDF per entry ({len(pdfs)} files, {len(listed)} entries)")

    # ---- the numbers ------------------------------------------------------
    audit = cfg.LOGS_DIR / "manuscript_audit.txt"
    check(audit.exists() and "MISS" not in audit.read_text(encoding="utf-8"),
          "no quoted number disagrees with the analysis output")

    counts = (cfg.LOGS_DIR / "word_count.txt").read_text(encoding="utf-8")
    over = [l for l in counts.splitlines() if l.startswith("OVER")]
    # the line reads "TOTAL (limit 4,000)   3,649" — take the last number on it,
    # not the first, which is the limit itself
    total_line = next(l for l in counts.splitlines() if l.startswith("TOTAL"))
    total = int(re.findall(r"[\d,]+", total_line)[-1].replace(",", ""))
    check(total <= 4000, f"manuscript text within the 4,000-word limit ({total:,})")
    check(not over, "every other journal limit met", "; ".join(over))

    # ---- the repository ---------------------------------------------------
    def git(*args: str) -> str:
        return subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                              text=True).stdout.strip()

    tracked = git("ls-files")
    restricted = [l for l in tracked.splitlines()
                  if l.startswith("input/derived") or l.endswith(".sav")]
    check(not restricted, "no restricted microdata tracked by git",
          ", ".join(restricted))
    check(not git("status", "--porcelain"), "working tree clean",
          git("status", "--porcelain")[:200])
    local, remote = git("rev-parse", "HEAD"), git("rev-parse", "@{u}")
    check(bool(remote) and local == remote, "pushed to the remote",
          f"local {local[:7]} vs remote {remote[:7]}" if local != remote else "")

    # ---- the notebook ------------------------------------------------------
    nb_path = ROOT / "notebooks" / "KHP_UnmetNeed_LTA_Colab.ipynb"
    try:
        nb = json.loads(nb_path.read_text(encoding="utf-8"))
        nb_src = "".join("".join(c.get("source", [])) for c in nb["cells"])
        check(True, "Colab notebook is valid JSON")
        check("<your-account>" not in nb_src,
              "notebook points at the real repository")
    except Exception as exc:                       # noqa: BLE001
        check(False, "Colab notebook is valid JSON", str(exc))

    # ---- report ------------------------------------------------------------
    width = max(len(label) for _, label, _ in results)
    bad = 0
    for ok, label, detail in results:
        bad += not ok
        print(f"{'ok  ' if ok else 'FAIL'} {label:<{width}}"
              f"{'  ' + detail if detail and not ok else ''}")
    print()
    if bad:
        print(f"{bad} problem(s) to fix before submitting.")
        return 1
    print(f"All {len(results)} checks pass. The package is ready to submit.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
