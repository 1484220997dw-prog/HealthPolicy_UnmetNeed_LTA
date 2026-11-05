# Submitting to Health Policy through Editorial Manager

Work through this at the computer. Everything the submission needs is already in this
package; the only judgement calls are flagged.

Submission site: <https://www.editorialmanager.com/HEAP/>

Editorial Manager's screens are configured per journal, so the names below may differ
slightly from what you see. The order is the standard one and the content is what this
journal asks for.

---

## Before you start

Have these open:

* this package's `manuscript/` folder (six `.docx` files)
* `output/figures/figure1_status_prevalence_and_persistence.tif`
* the abstract, to paste: it is in `manuscript/05_manuscript.docx` under **Abstract**
* the KHP data-use approval email, if you have the agreement number

One decision to make in advance: **the corresponding author is DU Haichao**
(1484220997@qq.com). Editorial Manager sends every notice to that address, so it must be
one that is checked. Wansuk Choi's institutional address (wschoi@ikw.ac.kr) is the
alternative if you would rather the journal corresponded with the institution.

---

## 1. Account

Register as an author, or log in if you already have an Elsevier Editorial Manager
account. The same login works across Elsevier journals, but the *registration* is
per journal: an existing account elsewhere may still need to be registered for
Health Policy the first time.

Use the corresponding author's email. That address receives the decision letters.

## 2. Start the submission

**Submit New Manuscript**, then choose the article type:

> **Full-length article**

This matters. The article type sets the limits the editorial office checks against:
4,000 words, 4 tables and figures combined, 250-word abstract. The other types
(Health Reform Monitor, Review, Cross-country comparison, Policy comment, Letter) have
different limits and this manuscript is built to the Full-length ones.

## 3. Attach the files, in this order

Editorial Manager asks for an *item type* for each file. Upload in this order; the order
is what the journal's Guide for Authors specifies.

| # | Item type | File |
|---|---|---|
| 1 | Cover Letter | `manuscript/01_cover_letter.docx` |
| 2 | Title Page | `manuscript/02_title_page.docx` |
| 3 | Author Statement / CRediT | `manuscript/03_credit_statement.docx` |
| 4 | Highlights | `manuscript/04_highlights.docx` |
| 5 | Manuscript | `manuscript/05_manuscript.docx` |
| 6 | e-component | `manuscript/06_appendix.docx` |
| 7 | Figure | `output/figures/figure1_status_prevalence_and_persistence.tif` |

Three things to get right here:

* **Item 4's file name must contain the word "highlights."** It does. Do not rename it.
* **Item 6 must be uploaded as "e-component"**, not as part of the manuscript. That is
  how the appendix becomes online supplementary material if the paper is accepted.
* **Item 7 is required even though Figure 1 is already inside the manuscript.** The
  journal asks for artwork as separate files. The `.tif` is 300 dpi for production; the
  `.pdf` in the same folder is the vector original if they ask for one instead.

Do not upload a PDF of the manuscript. Elsevier needs the editable `.docx`.

## 4. Manuscript data

**Title** — paste exactly:

> Cost and non-financial barriers to healthcare in South Korea, 2020–2023: a four-wave
> latent transition analysis

**Abstract** — paste the structured abstract from the manuscript, keeping the
Background / Objective / Methods / Results / Conclusions labels. If the box strips
formatting, the labels can stay as plain text.

**Keywords** — six, entered one at a time:

```
unmet healthcare need
universal coverage
latent transition analysis
financial protection
dental care
Korea
```

**Authors** — add both, in this order:

| Order | Name | ORCID | Email | Role |
|---|---|---|---|---|
| 1 | DU Haichao | 0009-0006-0839-1888 | 1484220997@qq.com | corresponding |
| 2 | Wansuk Choi | 0000-0003-1324-6723 | wschoi@ikw.ac.kr | |

Affiliation for both: Department of Physical Therapy, College of Health Sciences,
Kyungwoon University, 730 Gangdong-ro, Sandong-eup, Gumi-si, Gyeongsangbuk-do,
Republic of Korea.

Linking the ORCIDs is worth the extra click: it attaches the publication to the authors'
records automatically.

## 5. The questionnaire

Editorial Manager asks a series of yes/no and free-text questions. The answers for this
submission:

**Has this work been published before, or is it under consideration elsewhere?**
No. (A preprint would not count against you, but there is none.)

**Ethical approval.** Answer **not applicable** or **exempt**, and if there is a text
box, say: *the study is a secondary analysis of de-identified public-use microdata from
the Korea Health Panel, released on application under a data-use agreement; informed
consent was obtained by the data producers at the time of collection.*

Do not tick "approved by an ethics committee" unless and until Kyungwoon University's IRB
has issued a determination. See `SUBMISSION_CHECKLIST.md`.

**Declaration of competing interests.** None. The title page carries the statement.

**Funding.** None. The title page carries the statement.

**Declaration of generative AI.** Answer **yes**, AI was used, and paste the statement
from the title page:

> During the preparation of this work the authors used Claude (Anthropic) to assist with
> developing the analysis code and with language editing. The authors reviewed and
> edited the output as needed and take full responsibility for the content of the
> publication.

This disclosure is required by Elsevier where generative AI was used in preparing the
manuscript. It does not count against the submission; omitting it would be a problem.

**Data statement / data availability.** The data are from a third party and available on
application:

> The Korea Health Panel microdata are available to researchers on application to the
> Korea Institute for Health and Social Affairs at https://www.khp.re.kr and may not be
> redistributed by the authors. All analysis code, the data dictionary, a synthetic
> replica of the analysis panel, and every table, figure and quoted number are openly
> available at https://github.com/1484220997dw-prog/HealthPolicy_UnmetNeed_LTA

**Suggested reviewers.** Optional. If you want to name any, the authors of references
[12], [13] and [14] work directly on unmet healthcare need in Korea and are not
collaborators:

* Hansoo Ko — unmet healthcare needs and health status, published in this journal
* Jongnam Hwang — reasons for unmet need in Korea
* Woojin Chung — financial and non-financial barriers in the Korea Health Panel

**Opposed reviewers.** Leave blank unless you have a reason.

## 6. Build and approve the PDF

Editorial Manager assembles a PDF from the uploaded files for the editors and reviewers.
Open it and check:

* the **manuscript PDF carries no author names or affiliations** — the review is
  double-anonymised, and the names belong only on the separate title page
* Figure 1 is legible at the size it appears
* the three tables are intact and not split oddly
* the reference list is numbered 1–29, one entry per line

Then **Approve Submission**. Nothing reaches the editors until you do: a submission left
un-approved sits in "Submissions Waiting for Author's Approval" indefinitely. This is the
single most common way a submission silently fails to happen.

## 7. After submitting

You will get a confirmation email with a manuscript number (something like
`HEAP-D-26-00123`). Keep it: every later message about the paper uses it.

Typical timeline for this journal: editorial screening within a couple of weeks, first
decision in two to three months. The status in Editorial Manager moves through
"Submitted to Journal" → "With Editor" → "Under Review" → "Decision in Process".

If the paper is sent back for revision, the Markdown files in `manuscript/` are the
masters: edit those, run `python src/08_make_docx.py` to rebuild the Word files, and
`python src/07_check_manuscript.py` to confirm the numbers and limits still hold.

## If it is rejected

The strategy note for this study lists *Social Science & Medicine* and
*SSM – Population Health* as the next destinations. Both take the same structure with
modest reformatting; the main change is a longer Methods section, since neither imposes
the 4,000-word limit.
