"""Step 01 - build the person-wave panel and the data dictionary.

Reads the restricted KHP SPSS files (directory given by KHP_RAW_DIR) and writes
input/derived/khp_unmet_panel_2020_2023.csv.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd

from khp_lta import config as cfg
from khp_lta.build import build_panel

DICTIONARY = [
    ("PIDWON", "Person identifier, stable across KHP waves", "integer"),
    ("HHID", "Household identifier for the wave", "integer"),
    ("wave", "Survey wave, 1 = 2020 ... 4 = 2023", "1-4"),
    ("year", "Calendar year of the survey wave", "2020-2023"),
    ("I_WGL", "KHP longitudinal individual weight (population)", "numeric"),
    ("I_WGC", "KHP cross-sectional individual weight (population)", "numeric"),
    ("w_lon", "Baseline longitudinal weight rescaled to mean 1", "numeric"),
    ("phy_cost", "Forgone physician/hospital care, cost barrier (AH1=1 and AH1_1/2_D=1)", "0/1"),
    ("phy_noncost", "Forgone physician/hospital care, non-financial barrier (AH1=1 and AH1_3-8_D=1)", "0/1"),
    ("den_cost", "Forgone dental care, cost barrier (AH2=1 and AH2_1/2_D=1)", "0/1"),
    ("den_noncost", "Forgone dental care, non-financial barrier (AH2=1 and AH2_3-8_D=1)", "0/1"),
    ("phy_any", "Any forgone physician or hospital care (AH1=1)", "0/1"),
    ("den_any", "Any forgone dental care (AH2=1)", "0/1"),
    ("module_asked", "Unmet-need module administered in this wave", "0/1"),
    ("age", "Age in completed years at the wave", "19 and over"),
    ("female", "Female", "0/1"),
    ("edu3", "Educational attainment, three groups", "categorical"),
    ("partnered", "Living with a spouse or partner", "0/1"),
    ("employed", "In paid work, self-employed or unpaid family worker", "0/1"),
    ("region3", "Capital area / metropolitan city / other province", "categorical"),
    ("insurance3", "NHI employee-based / NHI self-employed / Medical Aid", "categorical"),
    ("hh_income", "Annual household total income, 10 000 KRW", "numeric"),
    ("hh_size", "Number of household members enumerated in the wave", "integer"),
    ("eq_income", "Household income divided by the square root of household size", "numeric"),
    ("income_q5", "Equivalised income quintile within wave, 1 = lowest", "1-5"),
    ("chronic", "At least one of 30 physician-diagnosed chronic conditions", "0/1"),
    ("disability", "Registered disability", "0/1"),
    ("poor_srh", "Self-rated health poor or very poor", "0/1"),
    ("usual_source", "Has a usual source of care", "0/1"),
    ("private_insurance", "Holds private health insurance", "0/1"),
    ("in_cohort", "In the 2020 baseline adult cohort used for analysis", "0/1"),
    ("n_waves_observed", "Number of waves in which the module was answered", "1-4"),
]


def weighted_prevalence(coh: pd.DataFrame) -> pd.DataFrame:
    rows = {}
    for year, g in coh[coh.module_asked == 1].groupby("year"):
        rows[year] = {
            name: 100 * (g[name] * g.w_lon).sum() / g.loc[g[name].notna(), "w_lon"].sum()
            for name in cfg.INDICATORS + ["phy_any", "den_any"]
        }
        rows[year]["n_respondents"] = len(g)
    return pd.DataFrame(rows).T.round(2)


def main() -> None:
    panel = build_panel(verbose=True)
    panel.to_csv(cfg.PANEL_CSV, index=False, encoding="utf-8")
    print(f"wrote {cfg.PANEL_CSV}  ({len(panel):,} person-wave rows)")

    pd.DataFrame(DICTIONARY, columns=["variable", "description", "values"]).to_csv(
        cfg.DICTIONARY_DIR / "data_dictionary.csv", index=False, encoding="utf-8"
    )

    prev = weighted_prevalence(panel[panel.in_cohort == 1])
    print("\nWeighted prevalence (%) in the baseline cohort")
    print(prev.to_string())
    prev.to_csv(cfg.LOGS_DIR / "indicator_prevalence_by_year.csv", encoding="utf-8")


if __name__ == "__main__":
    main()
