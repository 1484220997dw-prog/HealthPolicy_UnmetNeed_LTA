"""Step 06 - the five-status solution, reported as a sensitivity analysis.

BIC keeps falling as statuses are added to a time-homogeneous model, so the
four-status choice has to be checked against the next solution up rather than
asserted. This step fits five statuses with wave-specific and with
time-homogeneous transitions and writes their measurement models, so a reader
can see what the extra status is and whether it changes the substantive picture.

Writes output/tables/tableA9_five_status_solution.csv.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import pandas as pd

from khp_lta import config as cfg
from khp_lta import lta
from khp_lta.build import indicator_array


def main() -> None:
    print(f"writing results to {cfg.TABLES_DIR.parent}")
    panel = pd.read_csv(cfg.PANEL_CSV)
    Y, w, _ = indicator_array(panel)

    rows, summary = [], {}
    for homo in (False, True):
        label = "time-homogeneous" if homo else "wave-specific"
        # A sensitivity check does not need the full search budget of the main
        # model: the five-status likelihood surface was already explored in the
        # model-selection sweep, and the point of this step is to show what the
        # extra status looks like, not to report its parameters to four decimals.
        fit = lta.fit_lta(Y, w, 5, n_starts=cfg.N_STARTS_SELECT * 2,
                          seed=cfg.RANDOM_SEED, homogeneous=homo,
                          n_polish=2, screen_iter=250,
                          max_iter=8000, tol=1e-5, verbose=True)
        names = [f"Status {k + 1}" for k in range(5)]
        for j, ind in enumerate(cfg.INDICATORS):
            row = {"transitions": label, "quantity": cfg.INDICATOR_LABELS[ind]}
            for k in range(5):
                row[names[k]] = round(float(fit.rho[j, k]), 3)
            rows.append(row)
        for t, year in enumerate(cfg.YEARS):
            row = {"transitions": label, "quantity": f"Prevalence, {year} (%)"}
            for k in range(5):
                row[names[k]] = round(100 * float(fit.prevalence[t, k]), 1)
            rows.append(row)
        row = {"transitions": label, "quantity": "Mean posterior probability"}
        for k, v in enumerate(fit.avg_posterior()):
            row[names[k]] = round(float(v), 3)
        rows.append(row)
        # share of the diagonal that stays put, averaged over intervals
        row = {"transitions": label, "quantity": "Mean probability of staying"}
        for k in range(5):
            row[names[k]] = round(float(fit.tau[:, k, k].mean()), 3)
        rows.append(row)
        summary[label] = {"log_likelihood": fit.loglik, "BIC": fit.bic,
                          "entropy_R2": fit.entropy_r2(),
                          "n_parameters": fit.n_params,
                          "smallest_status_pct":
                              round(100 * float(fit.prevalence.mean(axis=0).min()), 2)}
        print(f"K=5 {label}: BIC {fit.bic:,.1f}, entropy R2 "
              f"{fit.entropy_r2():.3f}, smallest status "
              f"{summary[label]['smallest_status_pct']}%")

    out = pd.DataFrame(rows)
    out.to_csv(cfg.TABLES_DIR / "tableA9_five_status_solution.csv", index=False)
    print("\n" + out.to_string(index=False))
    (cfg.LOGS_DIR / "sensitivity_k5.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
