# input/

## derived/ — not redistributed

`khp_unmet_panel_2020_2023.csv` is built by `src/01_build_panel.py` from the
restricted Korea Health Panel SPSS files. It holds one row per person-wave for
every household member enumerated in 2020-2023, with the four unmet-need
indicators, the reason-level dummies and the covariates listed in
`dictionary/data_dictionary.csv`.

It is a person-level derivative of microdata released under a data-use agreement
that forbids redistribution, so it is excluded by `.gitignore` and must be
rebuilt locally from an approved copy of the KHP files.

`posterior_status.csv` (written by `src/02_fit_lta.py`) holds the posterior
latent-status probabilities and the modal status for each person-wave. It is
excluded for the same reason.

## synthetic/ — committed

`synthetic_unmet_panel.csv` is drawn from the fitted latent transition model and
from the observed marginal distributions of the covariates. It has the same
columns, the same four waves and a comparable amount of attrition, and it
contains no real respondent. Its purpose is to let anyone run the pipeline:

```bash
python src/run_all.py --synthetic
```

Estimates from the synthetic panel are close to the published ones but not
identical, and the manuscript reports only estimates from the real KHP files.

## dictionary/ — committed

`data_dictionary.csv` describes every variable in the derived panel, including
the KHP source items each indicator is built from.

## Getting the KHP data

Apply at <https://www.khp.re.kr>. The analysis needs the second-phase annual
data for 2020-2023:

| Year | Folder | File |
| --- | --- | --- |
| 2020 | `KHP+2020_spss` | `b_ind.sav` |
| 2021 | `KHP+2021_spss` | `c_ind.sav` |
| 2022 | `KHP+2022_spss` | `d_ind.sav` |
| 2023 | `KHP+2023_spss` | `e_ind.sav` |

Point `KHP_RAW_DIR` at the folder that contains those four subdirectories.
