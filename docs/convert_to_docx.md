# Producing the Word files

Elsevier needs editable Word files; a PDF is not an acceptable source file. The
Markdown files in `manuscript/` are the masters, and `src/08_make_docx.py` produces the
`.docx` copies from them.

```bash
python src/08_make_docx.py
```

This writes one `.docx` beside each `.md`, then reads each one back and reports any
Markdown or HTML markup that survived the conversion. It exits non-zero if anything
did, so a silent formatting failure cannot reach the journal.

What the script does beyond a plain conversion:

* **Page setup** — single column, 1-inch margins, Times New Roman 12 pt, 1.5 line
  spacing, page numbers centred in the footer.
* **Tables** — Tables 1, 2 and 3 are read from `output/tables/` and inserted into
  `05_manuscript.docx` as real Word tables after the caption list, so the file is
  complete as submitted.
* **Figure 1** — embedded as a 300 dpi PNG, 6.4 inches wide.
* **Working notes** — anything after a `<!-- not for submission -->` marker in a
  Markdown file is left out of the `.docx`. The highlights file uses this to keep its
  character-count table out of the submission copy.

## Checking the layout

```bash
python src/09_preview_pdf.py
```

Reading a .docx as XML shows that the content is there but not how it sits on the page.
This step renders each file to PDF with LibreOffice into `output/preview/` and reports
the page count and orientation. The PDFs are for review only — Elsevier wants the .docx.

## After generating

1. Open `05_manuscript.docx` and confirm the word count in Word's own counter. The
   script counts about 3,690 words from Background to Conclusion; Word counts slightly
   differently, and the limit is 4,000.
2. Confirm the manuscript file carries no author names or affiliations — the journal
   uses double-anonymised review. `src/07_check_manuscript.py` checks the Markdown
   source for this.
3. Submit the figure separately as well:
   `output/figures/figure1_status_prevalence_and_persistence.tif` is the 300 dpi
   version for production and the `.pdf` is the vector original.
4. Move the appendix tables (A1–A10, in `output/tables/`) into the e-component file if
   you want them as Word tables rather than as the CSVs the repository ships.

## Upload order in Editorial Manager

| # | File |
|---|---|
| 1 | `01_cover_letter.docx` |
| 2 | `02_title_page.docx` |
| 3 | `03_credit_statement.docx` |
| 4 | `04_highlights.docx` |
| 5 | `05_manuscript.docx` |
| 6 | `06_appendix.docx` (upload as "e-component") |

## If you would rather use Pandoc

Pandoc is not installed on this machine, which is why the conversion is a script. If
you install it, `pandoc manuscript/05_manuscript.md -o out.docx` gives a plainer file —
but it will not insert the tables or the figure, so the script above is the better
route.
