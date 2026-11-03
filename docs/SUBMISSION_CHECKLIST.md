# Submission checklist for *Health Policy*

Everything below follows the journal's Guide for Authors as retrieved on
2026-11-03. Items marked **AUTHOR ACTION** need a decision or a fact only the
authors can supply; they are the only things standing between this package and
submission through <https://www.editorialmanager.com/HEAP/>.

## Files to upload, in this order

| # | Submission item | File in this package | Status |
|---|---|---|---|
| 1 | Cover letter | `manuscript/01_cover_letter.md` | date and GitHub URL to insert |
| 2 | Title page (incl. funding, competing interests) | `manuscript/02_title_page.md` | GitHub URL to insert |
| 3 | CRediT author contribution statement | `manuscript/03_credit_statement.md` | ready |
| 4 | Highlights (file name must contain "highlights") | `manuscript/04_highlights.md` | ready |
| 5 | Manuscript, anonymised | `manuscript/05_manuscript.md` | ready |
| 6 | Appendices, uploaded as "e-component" | `manuscript/06_appendix.md` | ready |

Convert items 1–6 to `.docx` before uploading — Elsevier does not accept a PDF as the
source file, and the journal asks for single-column Word files. The Markdown sources
are the editable master copies; `docs/convert_to_docx.md` gives the one-line Pandoc
command.

## Journal requirements, item by item

| Requirement | Limit | This submission |
|---|---|---|
| Article type | Full-length article | yes |
| Word count (text + boxes, excluding abstract, references, tables, figures) | 4,000 | see `output/logs/word_count.txt` |
| Tables + figures, combined | 4 | 3 tables + 1 figure = 4 |
| Title | ≤ 20 words, states country and study type | 17 words; "South Korea", "latent transition analysis" |
| Abstract | ≤ 250 words, structured Background / Objective / Methods / Results / Conclusions | 248 words, structured |
| Highlights | 3–5 bullets, ≤ 85 characters each; first states the problem; ≥ 1 on findings; ≥ 1 on policy implications | 5 bullets, all ≤ 85 characters |
| Research in context box | ≤ 200 words under three set headings | 196 words |
| Headings | Background, Methods, Results, Discussion, Conclusion | yes |
| Footnotes | none permitted | none |
| Equations | ≤ 3 in the main text | 1 in the main text; the full likelihood is in the appendix |
| References | numbered in square brackets, in order of appearance | 29 references, `references/reference_list_vancouver.txt` |
| Anonymisation | manuscript must carry no author details | `05_manuscript.md` contains no names, affiliations or self-identifying citations |
| Appendix numbering | Table A1, Figure A1 … | Tables A1–A9 |
| Data statement | encouraged | on the title page and in the Methods |
| Generative AI disclosure | required where used | on the title page |

## Checking the manuscript against the analysis

```bash
python src/07_check_manuscript.py
```

This reports the word counts against every limit in the table above, and then searches
the manuscript for each quantity in `output/logs/numbers.json` and for each regression
estimate quoted in section 3.4. A line marked `MISS` means the analysis produces a value
the prose does not contain — that is, the text has drifted from the output and must be
corrected before submission. The report is saved to
`output/logs/manuscript_audit.txt`.

## AUTHOR ACTION before submission

1. **GitHub URL.** Push the repository (see `docs/GITHUB_PUSH.md`) and insert the
   public URL in three places: the cover letter, the title page data-availability
   statement, and the Methods paragraph headed "Data and code availability".
2. **Ethical review.** Confirm with the Kyungwoon University IRB whether an exemption
   determination is needed for secondary analysis of de-identified KHP public-use
   data, and add the determination number to the title page if one is issued. The
   current wording states only what is verifiable: that the data are de-identified
   secondary microdata obtained under a data-use agreement and that consent was
   obtained by the data producers.
3. **KHP data-use agreement number.** Insert the approval identifier issued with the
   data release, if your agreement requires it to be cited.
4. **Date** on the cover letter.
5. **Confirm the author order and the corresponding author.** The package puts
   DU Haichao first and as corresponding author, with HUO Ning second, following the
   author list supplied for this study.
6. **Check the word count** after converting to .docx, since Word counts differently
   from the script. `output/logs/word_count.txt` records the Markdown count.

## Suggested reviewers

The journal does not require these, but Editorial Manager offers the field. Candidates
whose published work is closest to this manuscript, and who are not collaborators of
the authors, can be drawn from `references/references.csv` — the authors of references
[12], [13] and [14] work directly on unmet need in Korea.

## If the paper is rejected

The strategy note for this study lists *Social Science & Medicine* and
*SSM – Population Health* as the next destinations. Both accept the same structure with
modest reformatting; the main change needed is a longer Methods section, since neither
imposes the 4,000-word limit.
