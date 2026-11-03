"""Step 08 - turn the Markdown manuscript files into the .docx files to upload.

Elsevier does not accept a PDF as the source file and asks for single-column
Word files, so the Markdown sources in manuscript/ are the editable masters and
this script produces the submission copies from them.

It is a small converter rather than a general Markdown engine: it handles the
constructs these six files actually use - ATX headings, paragraphs, bullet
lists, pipe tables, blockquotes, horizontal rules, and inline bold, italic,
code and links - and it raises on anything it does not recognise rather than
dropping it silently.

For the manuscript it does one thing a generic converter cannot: it drops the
three main tables in as real Word tables, read from output/tables/, and places
Figure 1 as an image, so the file that goes to the journal is complete.

Writes manuscript/*.docx.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd
from docx import Document
from docx.enum.section import WD_ORIENT, WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

from khp_lta import config as cfg

MANUSCRIPT_DIR = cfg.PROJECT_ROOT / "manuscript"
BODY_FONT = "Times New Roman"
BODY_SIZE = Pt(12)

# Tables and the figure are inserted into 05_manuscript.docx at these markers.
TABLE_FILES = {
    "Table 1.": "table1_baseline_characteristics.csv",
    "Table 2.": "table2_measurement_model.csv",
    "Table 3.": "table3_transition_matrices.csv",
}
FIGURE_FILE = "figure1_status_prevalence_and_persistence.png"

# Appendix tables, in order: (number, caption, file, rename, drop).
#
# ``rename`` only relabels columns for the reader; ``drop`` is the one way a
# column leaves the table. Keeping the two separate matters — an earlier version
# used a single "keep" mapping for both jobs and silently reduced three of these
# tables to their first column.
#
# The regression tables carry both the raw bounds and a formatted "estimate"
# column; printing both would double the width for no added information.
APPENDIX_TABLES: list[tuple[str, str, str, dict[str, str] | None, list[str] | None]] = [
    ("Table A1", "Model selection: one to six latent statuses, with wave-specific "
     "and with time-homogeneous transitions",
     "tableA1_model_selection.csv",
     {"K": "Statuses", "transitions": "Transitions", "n_parameters": "Parameters",
      "log_likelihood": "Log-likelihood", "entropy_R2": "Entropy R2",
      "smallest_status_pct": "Smallest status (%)"}, None),
    ("Table A2", "Weighted prevalence of each stated reason, by domain and year "
     "(%, with unweighted counts)",
     "tableA2_reason_prevalence.csv", None, None),
    ("Table A3", "Model A in full: multinomial logit for latent status in 2020, "
     "relative risk ratios against having no unmet need",
     "tableA3_model_a_baseline_status.csv",
     {"outcome": "Status", "term": "Characteristic", "estimate": "RRR (95% CI)"},
     ["RRR", "ci_low", "ci_high", "p_value"]),
    ("Table A4", "Model B in full: logit for being in an unmet-need status one "
     "year later, among person-waves that begin in one",
     "tableA4_model_b_persistence.csv",
     {"term": "Characteristic", "estimate": "OR (95% CI)"},
     ["OR", "ci_low", "ci_high", "p_value"]),
    ("Table A5", "Model B re-estimated with posterior-probability weights instead "
     "of modal assignment",
     "tableA5_model_b_posterior_weighted.csv",
     {"term": "Characteristic", "estimate": "OR (95% CI)"},
     ["OR", "ci_low", "ci_high", "p_value"]),
    ("Table A6", "Latent status prevalence among the 7,905 adults who answered all "
     "four waves (%)",
     "tableA6_completecase_prevalence.csv", {"year": "Year"}, None),
    ("Table A7", "Baseline characteristics by number of waves answered (weighted %)",
     "tableA7_attrition.csv", None, None),
    ("Table A8", "Latent status prevalence with inverse probability of response "
     "weighting (%)",
     "tableA8_ipw_prevalence.csv", {"year": "Year"}, None),
    ("Table A9", "The five-status solution, for comparison with the selected "
     "four-status model",
     "tableA9_five_status_solution.csv",
     {"transitions": "Transitions", "quantity": "Quantity"}, None),
    ("Table A10", "Models A and B side by side, one row per characteristic",
     "tableA10_covariates_combined.csv", None, None),
]


# --------------------------------------------------------------------------- #
# Document setup
# --------------------------------------------------------------------------- #
def new_document(line_spacing: float = 1.5) -> Document:
    doc = Document()
    for section in doc.sections:
        section.left_margin = section.right_margin = Inches(1)
        section.top_margin = section.bottom_margin = Inches(1)

    normal = doc.styles["Normal"]
    normal.font.name = BODY_FONT
    normal.font.size = BODY_SIZE
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), BODY_FONT)
    normal.paragraph_format.line_spacing = line_spacing
    normal.paragraph_format.space_after = Pt(6)

    for level, size, bold, italic in (("Title", 14, True, False),
                                      ("Heading 1", 13, True, False),
                                      ("Heading 2", 12, True, False),
                                      ("Heading 3", 12, False, True)):
        st = doc.styles[level]
        st.font.name = BODY_FONT
        st.font.size = Pt(size)
        st.font.bold = bold
        st.font.italic = italic
        st.font.color.rgb = RGBColor(0, 0, 0)
        st.paragraph_format.space_before = Pt(12)
        st.paragraph_format.space_after = Pt(6)
        st.paragraph_format.keep_with_next = True
    return doc


def add_page_numbers(doc: Document) -> None:
    """A PAGE field in the footer; the journal asks for numbered pages."""
    for section in doc.sections:
        p = section.footer.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run()
        for kind, text in (("begin", None), (None, "PAGE"), ("end", None)):
            if kind:
                el = OxmlElement("w:fldChar")
                el.set(qn("w:fldCharType"), kind)
            else:
                el = OxmlElement("w:instrText")
                el.set(qn("xml:space"), "preserve")
                el.text = text
            run._r.append(el)
        run.font.name = BODY_FONT
        run.font.size = Pt(10)


# --------------------------------------------------------------------------- #
# Inline formatting
# --------------------------------------------------------------------------- #
INLINE = re.compile(
    r"(\*\*.+?\*\*)"        # bold
    r"|(\*[^*\n]+?\*)"      # italic
    r"|(`[^`]+?`)"          # code
    r"|(\[[^\]]+?\]\([^)]+?\))"   # link
)


def unescape(text: str) -> str:
    return re.sub(r"\\([.\[\]|*_<>~`#+=-])", r"\1", text)


def add_runs(paragraph, text: str) -> None:
    """Write text into a paragraph, honouring bold, italic, code and links."""
    for piece in filter(None, INLINE.split(unescape(text))):
        if piece.startswith("**") and piece.endswith("**"):
            paragraph.add_run(piece[2:-2]).bold = True
        elif piece.startswith("*") and piece.endswith("*") and len(piece) > 2:
            paragraph.add_run(piece[1:-1]).italic = True
        elif piece.startswith("`") and piece.endswith("`"):
            run = paragraph.add_run(piece[1:-1])
            run.font.name = "Consolas"
            run.font.size = Pt(10)
        elif piece.startswith("[") and "](" in piece:
            label, url = piece[1:-1].split("](", 1)
            paragraph.add_run(label)
            if url not in label:
                paragraph.add_run(f" ({url})").font.size = Pt(10)
        else:
            paragraph.add_run(piece)


# --------------------------------------------------------------------------- #
# Block parsing
# --------------------------------------------------------------------------- #
def is_block_start(line: str) -> bool:
    """True for a line that opens a new block rather than continuing a paragraph.

    The space after the bullet marker matters: a line beginning "*Health Policy*"
    is an italic run, not a list item.
    """
    s = line.strip()
    return (s.startswith(("#", ">", "|"))
            or s.startswith(("* ", "- "))
            or s in ("---", "***", "___"))


def split_row(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def is_separator(line: str) -> bool:
    return bool(re.fullmatch(r"\|?[\s:|-]+\|?", line.strip())) and "-" in line


def add_markdown_table(doc: Document, rows: list[list[str]]) -> None:
    table = doc.add_table(rows=len(rows), cols=max(len(r) for r in rows))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, row in enumerate(rows):
        for j, cell in enumerate(row):
            para = table.cell(i, j).paragraphs[0]
            para.paragraph_format.line_spacing = 1.0
            para.paragraph_format.space_after = Pt(2)
            add_runs(para, cell)
            for run in para.runs:
                run.font.size = Pt(9)
                if i == 0:
                    run.bold = True


def add_dataframe(doc: Document, df: pd.DataFrame, font_size: Pt = Pt(8)) -> None:
    df = df.fillna("")
    table = doc.add_table(rows=len(df) + 1, cols=len(df.columns))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for j, name in enumerate(df.columns):
        para = table.cell(0, j).paragraphs[0]
        para.paragraph_format.line_spacing = 1.0
        run = para.add_run(str(name))
        run.bold = True
        run.font.size = font_size
    for i, (_, row) in enumerate(df.iterrows(), start=1):
        for j, value in enumerate(row):
            para = table.cell(i, j).paragraphs[0]
            para.paragraph_format.line_spacing = 1.0
            para.paragraph_format.space_after = Pt(0)
            run = para.add_run("" if pd.isna(value) else str(value))
            run.font.size = font_size


# Anything after this marker in a Markdown file is a working note for the
# authors and is left out of the file that goes to the journal.
STOP_MARKER = "<!-- not for submission -->"


def convert(md_path: Path, out_path: Path, with_tables: bool = False) -> int:
    text = md_path.read_text(encoding="utf-8")
    if STOP_MARKER in text:
        text = text.split(STOP_MARKER, 1)[0]
    lines = text.splitlines()
    doc = new_document()
    add_page_numbers(doc)

    i, n_blocks = 0, 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        if stripped in ("---", "***", "___"):
            i += 1
            continue

        m = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if m:
            level, text = len(m.group(1)), m.group(2)
            style = "Title" if level == 1 else f"Heading {min(level - 1, 3)}"
            add_runs(doc.add_paragraph(style=style), text)
            n_blocks += 1
            if with_tables:
                insert_object(doc, unescape(text))
            i += 1
            continue

        if stripped.startswith("|") and i + 1 < len(lines) and is_separator(lines[i + 1]):
            rows = [split_row(stripped)]
            i += 2
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(split_row(lines[i]))
                i += 1
            add_markdown_table(doc, rows)
            doc.add_paragraph()
            n_blocks += 1
            continue

        if stripped.startswith(("* ", "- ")):
            while i < len(lines) and lines[i].strip().startswith(("* ", "- ")):
                para = doc.add_paragraph(style="List Bullet")
                body = lines[i].strip()[2:]
                i += 1
                while i < len(lines) and lines[i].startswith(("  ", "\t")) \
                        and lines[i].strip() and not lines[i].strip().startswith(("* ", "- ")):
                    body += " " + lines[i].strip()
                    i += 1
                add_runs(para, body)
            n_blocks += 1
            continue

        if stripped.startswith("> "):
            body = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                body.append(lines[i].strip().lstrip(">").strip())
                i += 1
            para = doc.add_paragraph()
            para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            para.paragraph_format.space_before = Pt(10)
            para.paragraph_format.space_after = Pt(10)
            add_runs(para, " ".join(body))
            n_blocks += 1
            continue

        # ordinary paragraph: join until a blank line
        body = []
        while i < len(lines) and lines[i].strip() and not is_block_start(lines[i]):
            body.append(lines[i].strip())
            i += 1
        if body:
            add_runs(doc.add_paragraph(), " ".join(body))
            n_blocks += 1
        else:
            raise ValueError(f"{md_path.name}:{i + 1}: unhandled line {lines[i]!r}")

    doc.save(out_path)
    return n_blocks


def insert_object(doc: Document, heading: str) -> None:
    """Nothing to do at headings; tables and the figure go in at the end."""
    return None


def append_tables_and_figure(out_path: Path) -> None:
    """Add the three tables and Figure 1 after the caption list."""
    doc = Document(out_path)
    doc.add_page_break()
    for caption, fname in TABLE_FILES.items():
        df = pd.read_csv(cfg.TABLES_DIR / fname)
        para = doc.add_paragraph()
        add_runs(para, f"**{caption}**")
        add_dataframe(doc, df)
        doc.add_paragraph()
    para = doc.add_paragraph()
    add_runs(para, "**Figure 1.**")
    doc.add_picture(str(cfg.FIGURES_DIR / FIGURE_FILE), width=Inches(6.4))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.save(out_path)


# Markup that must not survive conversion.
#
# Paragraphs are checked for everything, because the converter parses all of it
# there. Table cells are checked only for markup that is never legitimate data:
# a cell may hold "#" as a column name, a pipe as part of its text, or the
# asterisks that mark statistical significance, and flagging those as unparsed
# bold would be a false alarm.
PARAGRAPH_LEFTOVERS = {
    "HTML tag": r"<su[bp]>",
    "bold marker": r"\*\*[^*\n]+\*\*",
    "escape backslash": r"\\[.\[\]|*_]",
    "heading marker": r"(?m)^#{1,4} ",
    "pipe-table row": r"(?m)^\|",
}
CELL_LEFTOVERS = {
    "HTML tag": r"<su[bp]>",
    "escape backslash": r"\\[.\[\]|*_]",
}


def verify(path: Path) -> tuple[int, int, dict[str, int]]:
    """Read the .docx back and look for markup the converter should have consumed."""
    doc = Document(path)
    paragraphs = "\n".join(p.text for p in doc.paragraphs)
    cells = "\n".join(" ".join(c.text for c in row.cells)
                      for table in doc.tables for row in table.rows)

    found: dict[str, int] = {}
    for name, pat in PARAGRAPH_LEFTOVERS.items():
        found[name] = len(re.findall(pat, paragraphs))
    for name, pat in CELL_LEFTOVERS.items():
        found[name] = found.get(name, 0) + len(re.findall(pat, cells))
    return len(doc.paragraphs), len(doc.tables), {k: v for k, v in found.items() if v}


def append_appendix_tables(out_path: Path) -> int:
    """Add Tables A1-A10 in full, on landscape pages so the wide ones fit."""
    doc = Document(out_path)

    section = doc.add_section(WD_SECTION.NEW_PAGE)
    section.orientation = WD_ORIENT.LANDSCAPE
    section.page_width, section.page_height = section.page_height, section.page_width
    section.left_margin = section.right_margin = Inches(0.7)
    section.top_margin = section.bottom_margin = Inches(0.7)

    add_runs(doc.add_paragraph(style="Heading 1"), "E. Appendix tables in full")
    add_runs(doc.add_paragraph(),
             "The same tables are in `output/tables/` of the replication "
             "repository as CSV files.")

    n_added = 0
    for number, caption, fname, rename, drop in APPENDIX_TABLES:
        df = pd.read_csv(cfg.TABLES_DIR / fname)
        if drop:
            df = df.drop(columns=[c for c in drop if c in df.columns])
        if rename:
            df = df.rename(columns=rename)
        para = doc.add_paragraph()
        para.paragraph_format.space_before = Pt(14)
        para.paragraph_format.keep_with_next = True
        add_runs(para, f"**{number}.** {caption}.")
        add_dataframe(doc, df, font_size=Pt(7.5))
        n_added += 1
    doc.save(out_path)
    return n_added


def main() -> None:
    print(f"writing results to {MANUSCRIPT_DIR}")
    made = []
    for md in sorted(MANUSCRIPT_DIR.glob("0*.md")):
        out = md.with_suffix(".docx")
        n = convert(md, out, with_tables=md.name.startswith("05_"))
        if md.name.startswith("05_"):
            append_tables_and_figure(out)
        if md.name.startswith("06_"):
            n += append_appendix_tables(out)
        made.append((out.name, n, out.stat().st_size))

    print(f"{'file':<28}{'paras':>7}{'tables':>8}{'size':>12}  leftover markup")
    problems = 0
    for name, _, size in made:
        n_par, n_tab, found = verify(MANUSCRIPT_DIR / name)
        problems += len(found)
        print(f"{name:<28}{n_par:>7}{n_tab:>8}{size:>10,} B  "
              f"{found if found else 'none'}")

    n_img = len([r for r in Document(MANUSCRIPT_DIR / "05_manuscript.docx")
                 .part.rels.values() if "image" in r.reltype])
    print(f"\nfigures embedded in 05_manuscript.docx: {n_img}")

    print("\nupload order for Editorial Manager:")
    for i, (name, _, _) in enumerate(made, start=1):
        print(f"  {i}. {name}")

    if problems:
        print(f"\n{problems} kind(s) of unconverted markup remain; fix the converter.")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
