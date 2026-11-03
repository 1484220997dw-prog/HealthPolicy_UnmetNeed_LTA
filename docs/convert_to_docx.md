# Converting the manuscript files to .docx

Elsevier needs editable Word files; a PDF is not an acceptable source file. The
Markdown files in `manuscript/` are the master copies.

Install Pandoc (<https://pandoc.org/installing.html>), then from the project root:

```bash
for f in manuscript/*.md; do pandoc "$f" -o "${f%.md}.docx"; done
```

On Windows PowerShell:

```powershell
Get-ChildItem manuscript\*.md | ForEach-Object { pandoc $_.FullName -o ($_.FullName -replace '\.md$','.docx') }
```

Then, in Word:

1. Set the layout to a single column and add page numbers.
2. Confirm that the manuscript file carries no author names or affiliations — the
   journal uses double-anonymised review.
3. Check the word count of `05_manuscript.docx` from Background to the end of
   Conclusions, including the research-in-context box but excluding the abstract,
   references, tables and figure. The limit is 4,000.
4. Rename the highlights file so the name still contains the word "highlights".
5. Submit the figure separately: `output/figures/figure1_status_prevalence_and_persistence.tif`
   is the 600 dpi version for production, and the PDF is the vector original.

The tables are in `output/tables/` as CSV. Paste `table1_baseline_characteristics.csv`,
`table2_measurement_model.csv` and `table3_transition_matrices.csv` into the manuscript
file as Word tables, each with its caption from `manuscript/05_manuscript.md`, and put
the appendix tables into the e-component file.
