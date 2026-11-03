# Cost and non-financial barriers behind unmet healthcare needs in South Korea, 2020–2023

Replication package for a manuscript submitted to *Health Policy* (Elsevier, ISSN 0168-8510).

The study follows a nationally representative cohort of Korean adults through four
annual waves of the Korea Health Panel (KHP), 2020–2023, and asks a question that
cross-sectional prevalence figures cannot answer: **when someone goes without care
they believe they need, does that state pass, or does it persist?** Four binary
indicators — physician/hospital care and dental care, each forgone for a cost reason
or for a non-financial reason — are combined in a **latent transition analysis (LTA)**
with full measurement invariance across waves, so that the estimated year-to-year
transitions describe movement between the same statuses rather than drift in what the
statuses mean.

---

## What is in this repository

```
HealthPolicy_UnmetNeed_LTA/
├── input/
│   ├── derived/         analysis panel built from the KHP files  (NOT redistributed)
│   ├── synthetic/       synthetic replica of that panel          (committed)
│   └── dictionary/      data dictionary for every derived variable
├── output/
│   ├── tables/          Tables 1–4 and appendix Tables A1–A8, as CSV
│   ├── figures/         Figure 1 in PDF, PNG and TIFF
│   └── logs/            fitted parameters, numbers.json, run log
├── src/
│   ├── khp_lta/         importable modules: config, build, lta, threestep
│   ├── 00_check_environment.py
│   ├── 01_build_panel.py        KHP SPSS files  -> person-wave panel
│   ├── 02_fit_lta.py            model selection, LTA fit, bootstrap
│   ├── 03_covariates.py         three-step covariate models
│   ├── 04_tables_figures.py     tables, figure, numbers.json
│   ├── 05_make_synthetic.py     synthetic replica for people without KHP access
│   ├── 06_sensitivity_k5.py     the five-status solution, for comparison
│   ├── 07_check_manuscript.py   word counts and audit of the numbers in the text
│   └── run_all.py               the whole pipeline, in order
├── notebooks/
│   └── KHP_UnmetNeed_LTA_Colab.ipynb    runs end to end in Google Colab
├── manuscript/          cover letter, title page, highlights, manuscript, appendix
├── references/          one PDF per reference, plus references.bib and .csv
└── requirements.txt
```

## Data access

The analysis uses the **second-phase Korea Health Panel annual data, waves 2020–2023**
(`b_ind.sav`, `c_ind.sav`, `d_ind.sav`, `e_ind.sav`; user guide and codebook version 2.4).
KHP microdata are released by the Korea Institute for Health and Social Affairs and the
National Health Insurance Service to named applicants under a data-use agreement that
**forbids redistribution**, so neither the SPSS files nor the person-level panel derived
from them is included here. Both are excluded by `.gitignore`.

Apply for the data at <https://www.khp.re.kr> (English pages available). Approval is
normally granted for research use within a few weeks and is free of charge.

Two paths are therefore available:

| You have | What to run | What you get |
| --- | --- | --- |
| The KHP files | `python src/run_all.py` after setting `KHP_RAW_DIR` | every number in the manuscript |
| No KHP access | `python src/run_all.py --synthetic` | the same pipeline on `input/synthetic/`, written to `output/synthetic/`, with estimates close to but not identical to the published ones |

```bash
# Windows PowerShell
$env:KHP_RAW_DIR = "D:\data\medical_pannel"
```

```bash
# macOS / Linux
export KHP_RAW_DIR=/data/medical_pannel
```

`KHP_RAW_DIR` must be the folder that contains the `KHP+2020_spss` … `KHP+2023_spss`
subdirectories.

## Reproducing the results

```bash
python -m pip install -r requirements.txt
```

```bash
python src/run_all.py
```

The pipeline is deterministic: every stochastic step draws from a generator seeded with
`RANDOM_SEED = 20260720` in `src/khp_lta/config.py`, so repeated runs on the same data
return identical estimates. A full run takes roughly 50–70 minutes on a laptop, almost
all of it in the 400 bootstrap replications of step 02; `--quick` cuts the bootstrap to
40 replications for a smoke test and leaves everything else unchanged. A synthetic run
reads `input/synthetic/` in place and writes to `output/synthetic/`, so it can never
overwrite the panel built from the real data or the results reported in the paper.

Each step writes its own outputs and can be re-run on its own:

```bash
python src/01_build_panel.py
```

```bash
python src/02_fit_lta.py
```

```bash
python src/03_covariates.py
```

```bash
python src/04_tables_figures.py
```

Step 02 accepts `--reuse-fit`, which skips the model-selection sweep and starts from the
stored point estimate, and `--reuse-bootstrap`, which rebuilds the tables from the stored
bootstrap draws without refitting anything. Step 07 reports the manuscript's word counts
against the journal's limits and checks every number quoted in the text against
`output/logs/numbers.json`; its report is `output/logs/manuscript_audit.txt`.

## Google Colab

`notebooks/KHP_UnmetNeed_LTA_Colab.ipynb` installs the dependencies, clones this
repository and runs the whole pipeline. It defaults to the synthetic panel so that it
completes without the restricted data; one cell mounts Google Drive and points
`KHP_RAW_DIR` at your own approved copy of the KHP files if you have one.

## Method in brief

* **Sample.** Adults aged 19 or over who answered the unmet-need module in the 2020
  wave and were followed to 2023. The module is administered to household members aged
  19 and over; respondents are retained in the likelihood for every wave, with missing
  waves handled by full-information maximum likelihood rather than by dropping cases.
* **Indicators.** `AH1` (physician or hospital care) and `AH2` (dental care) identify
  care that was needed but not obtained; the accompanying reason dummies split each
  domain into a cost barrier (cost of care or transport, forgone earnings) and a
  non-financial barrier (no time, opening hours or no appointment available, did not
  know where to go, transport or distance, mobility or health, booking too
  complicated). "No unmet need" and "no care was needed" are coded alike, which makes
  the indicators immune to the 2020–2023 drift in how often the "no care needed"
  option was chosen.
* **Model.** Latent transition analysis with wave-specific transition matrices and
  time-invariant item-response probabilities, estimated by weighted EM accelerated with
  SQUAREM, with 60 random starts screened and the best four iterated to convergence.
  Confidence intervals come from 400 non-parametric bootstrap replications over
  individuals.
* **Covariates.** A three-step approach: statuses are estimated first, respondents are
  then assigned, and associations are estimated with weighted multinomial and binary
  logit models with cluster-robust standard errors. A posterior-probability-weighted
  version is reported as a sensitivity analysis.
* **Weights.** The KHP longitudinal individual weight from the baseline wave, rescaled
  to mean 1 so that information criteria use the number of sampled individuals.

Full methodological detail, including the likelihood, is in `manuscript/04_appendix.md`.

## Checking the manuscript against the code

`output/logs/numbers.json` holds every quantity quoted in the manuscript text, written
by `src/04_tables_figures.py`. Any number in the paper can be traced to a key in that
file, and from there to the script that produced it.

## Citation

See `CITATION.cff`. The manuscript is under review; please cite the repository until a
journal reference is available.

## Licence

Code is released under the MIT licence (`LICENSE`). The KHP microdata are not covered
by that licence and are not distributed here. Reference PDFs in `references/` remain
under their publishers' terms; items without an open licence are represented by a
citation record rather than the full text.
