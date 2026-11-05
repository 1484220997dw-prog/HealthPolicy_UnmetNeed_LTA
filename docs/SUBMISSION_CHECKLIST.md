# Submission checklist for *Health Policy*

Everything below follows the journal's Guide for Authors as retrieved on
2026-11-03. Items marked **AUTHOR ACTION** need a decision or a fact only the
authors can supply; they are the only things standing between this package and
submission through <https://www.editorialmanager.com/HEAP/>.

## Files to upload, in this order

| # | Submission item | File to upload | Status |
|---|---|---|---|
| 1 | Cover letter | `manuscript/01_cover_letter.docx` | ready |
| 2 | Title page (incl. funding, competing interests) | `manuscript/02_title_page.docx` | ready |
| 3 | CRediT author contribution statement | `manuscript/03_credit_statement.docx` | ready |
| 4 | Highlights (file name must contain "highlights") | `manuscript/04_highlights.docx` | ready |
| 5 | Manuscript, anonymised | `manuscript/05_manuscript.docx` | ready |
| 6 | Appendices, uploaded as "e-component" | `manuscript/06_appendix.docx` | ready |
| 7 | Figure, as a separate file | `output/figures/figure1_...tif` | ready |

The `.docx` files are built from the Markdown masters by `src/08_make_docx.py`; see
`docs/convert_to_docx.md`. Item 7 is required even though Figure 1 is also embedded in
the manuscript: the journal asks for artwork as separate files.

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

## Outstanding items

Neither of these blocks submission. The journal's Guide for Authors does not require an
ethics approval number, and the ethics statement on the title page says only what can be
verified without one: that the microdata are de-identified, that consent was obtained by
the data producers, and that the authors saw nothing identifying. Adding a number later
is an addition to that statement, not a correction of it, so nothing said at submission
becomes wrong.

**1. Ethical review (ask now, add later).** Email the Kyungwoon University IRB to ask
whether secondary analysis of de-identified public-use KHP data needs an exemption
determination. Korean IRBs usually issue one within a week or two for this kind of
study, and some do not require an application at all. Add the number to the title page
when it arrives — at revision if the paper is already under review.

In the submission system, if asked about ethical approval, answer **not applicable** or
**exempt** and say the study analyses de-identified public-use secondary data. Do not
tick "approved by an ethics committee": that would not be true yet.

**2. KHP data-use agreement number (five minutes).** The approval KIHASA issued when the
data were released carries an identifier. Check the approval email and the agreement
terms: if the agreement requires the number to be cited in publications, add it to the
title page before submitting, since that is a contractual obligation rather than a
journal one. If it does not, nothing is needed.

Also note that Kyungwoon University may have its own rule requiring an IRB record for
anything published, independently of what the journal asks. That is worth confirming
even though the journal does not need it.

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
