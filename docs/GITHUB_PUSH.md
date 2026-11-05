# Pushing this package to GitHub

The repository root is `HealthPolicy_UnmetNeed_LTA/`. It is already laid out as a
publishable repository: `.gitignore` excludes the restricted microdata and every
person-level derivative of it, and keeps the synthetic replica, the data dictionary and
all results.

## What will and will not be published

Committed:

* all code in `src/`, the Colab notebook, the manuscript sources, `references/`
* `input/synthetic/` and `input/dictionary/`
* every table, figure and log in `output/`

Never committed (enforced by `.gitignore`):

* `input/derived/` — the person-wave panel and the posterior status file
* any `*.sav`, `*.sas7bdat`, `*.dta` file

Before the first push, check that nothing restricted is staged:

```bash
git status --short
```

```bash
git ls-files | grep -E "input/derived|\.sav$" || echo "clean: no restricted files staged"
```

## First push

```bash
cd "HealthPolicy_UnmetNeed_LTA"
```

```bash
git init -b main
```

```bash
git add . && git status --short | head -50
```

```bash
git commit -m "Replication package for the KHP unmet-need latent transition analysis"
```

Create an empty repository on GitHub named `HealthPolicy_UnmetNeed_LTA` — without a
README, licence or .gitignore, since this package supplies all three — and then:

```bash
git remote add origin https://github.com/1484220997dw-prog/HealthPolicy_UnmetNeed_LTA.git
```

```bash
git push -u origin main
```

## After pushing

1. Copy the repository URL into the three places listed in
   `docs/SUBMISSION_CHECKLIST.md`.
2. Set `REPO_URL` in `notebooks/KHP_UnmetNeed_LTA_Colab.ipynb` to the same URL, and
   add the Colab badge link to the README if you want reviewers to open it in one
   click:
   `https://colab.research.google.com/github/1484220997dw-prog/HealthPolicy_UnmetNeed_LTA/blob/main/notebooks/KHP_UnmetNeed_LTA_Colab.ipynb`
3. For a citable snapshot, link the repository to Zenodo and tag a release; the DOI can
   then replace the bare URL in the data-availability statement, which reviewers
   generally prefer.

## Keeping the repository in step with the manuscript

Re-running `python src/run_all.py` rewrites everything in `output/`, so a commit after
each run keeps the published results identical to the submitted numbers. The run log
records the commit hash it ran at, which makes the link verifiable in both directions.
