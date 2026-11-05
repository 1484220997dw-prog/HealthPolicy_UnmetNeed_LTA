"""Step 02 - select the number of latent statuses, fit the LTA, bootstrap it.

Writes:
  output/tables/tableA1_model_selection.csv
  output/tables/table2_measurement_model.csv
  output/tables/table3_transition_matrices.csv
  output/logs/lta_parameters.json
  input/derived/posterior_status.csv        (person-wave posteriors, for step 03)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import pandas as pd

from khp_lta import config as cfg
from khp_lta import lta
from khp_lta.build import indicator_array

# Status names describe what the fitted item-response probabilities actually
# show: the second status is driven by cost in both domains but mostly dental,
# the third by time and appointment availability rather than by geography or
# supply (see output/tables/tableA2_reason_prevalence.csv), and the fourth by
# both kinds of barrier in both domains at once.
STATUS_NAMES = {
    4: [
        "No unmet need",
        "Cost barrier",
        "Time and availability barrier",
        "Compound barrier",
    ]
}


def model_selection(Y, w) -> pd.DataFrame:
    rows = []
    for K in cfg.K_RANGE:
        for homo in (False, True):
            if K == 1 and homo:
                continue
            fit = lta.fit_lta(Y, w, K, n_starts=cfg.N_STARTS_SELECT,
                              seed=cfg.RANDOM_SEED + K, homogeneous=homo,
                              n_polish=cfg.N_POLISH_SELECT,
                              screen_iter=cfg.SCREEN_ITER,
                              max_iter=cfg.MAX_ITER_SELECT, tol=cfg.TOL_SELECT)
            rows.append({
                "K": K,
                "transitions": "time-homogeneous" if homo else "wave-specific",
                "n_parameters": fit.n_params,
                "log_likelihood": round(fit.loglik, 2),
                "AIC": round(fit.aic, 1),
                "BIC": round(fit.bic, 1),
                "entropy_R2": round(fit.entropy_r2(), 3) if K > 1 else np.nan,
                "smallest_status_pct": round(100 * fit.status_prevalence.mean(axis=0).min(), 2),
            })
            print(f"K={K:2d} {rows[-1]['transitions']:>17s}  "
                  f"BIC={rows[-1]['BIC']:>12,.1f}  "
                  f"entropy R2={rows[-1]['entropy_R2']}")
    return pd.DataFrame(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reuse-fit", action="store_true",
                    help="skip the model-selection sweep and start the final fit "
                         "from the parameters already in output/logs, then "
                         "re-estimate the bootstrap")
    ap.add_argument("--reuse-bootstrap", action="store_true",
                    help="also reuse the stored bootstrap draws, rebuilding the "
                         "tables without refitting anything")
    args, _ = ap.parse_known_args()

    panel = pd.read_csv(cfg.PANEL_CSV)
    print(f"writing results to {cfg.TABLES_DIR.parent}")
    Y, w, ids = indicator_array(panel, complete_only=False)
    print(f"analysis sample: {Y.shape[0]:,} adults x {Y.shape[1]} waves "
          f"x {Y.shape[2]} indicators")
    print(f"person-waves with the module answered: "
          f"{int((~np.isnan(Y)).any(axis=2).sum()):,}")

    K = cfg.K_SELECTED
    names = STATUS_NAMES.get(K, [f"Status {k + 1}" for k in range(K)])

    saved = cfg.LOGS_DIR / "lta_parameters.json"
    if args.reuse_fit and saved.exists():
        prev = json.loads(saved.read_text(encoding="utf-8"))
        print("reusing the stored point estimate exactly, without re-estimating")
        fit = lta.evaluate(Y, w, np.array(prev["delta"]), np.array(prev["tau"]),
                           np.array(prev["rho"]))
    else:
        sel = model_selection(Y, w)
        sel.to_csv(cfg.TABLES_DIR / "tableA1_model_selection.csv", index=False)
        fit = lta.fit_lta(Y, w, K, n_starts=cfg.N_STARTS, seed=cfg.RANDOM_SEED,
                          homogeneous=False, n_polish=cfg.N_POLISH,
                          screen_iter=cfg.SCREEN_ITER, max_iter=cfg.MAX_ITER,
                          tol=cfg.TOL, verbose=True)
    print(f"\nselected model: K={K}, log-likelihood {fit.loglik:,.2f}, "
          f"entropy R2 {fit.entropy_r2():.3f}, {fit.n_iter} EM iterations")

    boot_file = cfg.LOGS_DIR / "bootstrap_draws.npz"
    if args.reuse_bootstrap and boot_file.exists():
        print(f"reusing the stored bootstrap draws in {boot_file.name}")
        draws = {k: v for k, v in np.load(boot_file).items()}
    else:
        draws = lta.bootstrap(Y, w, fit, n_boot=cfg.N_BOOTSTRAP,
                              seed=cfg.RANDOM_SEED + 1,
                              max_iter=cfg.BOOT_MAX_ITER, tol=cfg.BOOT_TOL)
        np.savez_compressed(boot_file, **draws)

    # ---- Table 2: item-response probabilities and status prevalence --------
    rho_lo, rho_hi = lta.ci(draws["rho"])
    rows = []
    for j, ind in enumerate(cfg.INDICATORS):
        row = {"Indicator": cfg.INDICATOR_LABELS[ind]}
        for k in range(K):
            row[names[k]] = (f"{fit.rho[j, k]:.3f} "
                             f"({rho_lo[j, k]:.3f}-{rho_hi[j, k]:.3f})")
        rows.append(row)
    prev_lo, prev_hi = lta.ci(draws["prev"])
    for t, year in enumerate(cfg.YEARS):
        row = {"Indicator": f"Status prevalence, {year} (%)"}
        for k in range(K):
            row[names[k]] = (f"{100 * fit.status_prevalence[t, k]:.1f} "
                             f"({100 * prev_lo[t, k]:.1f}-{100 * prev_hi[t, k]:.1f})")
        rows.append(row)
    row = {"Indicator": "Mean posterior probability of assigned status"}
    for k, v in enumerate(fit.avg_posterior()):
        row[names[k]] = f"{v:.3f}"
    rows.append(row)
    table2 = pd.DataFrame(rows)
    table2.to_csv(cfg.TABLES_DIR / "table2_measurement_model.csv", index=False)
    print("\n" + table2.to_string(index=False))

    # ---- Table 3: transition matrices -------------------------------------
    tau_lo, tau_hi = lta.ci(draws["tau"])
    rows = []
    for t in range(cfg.N_WAVES - 1):
        for k in range(K):
            row = {"Interval": f"{cfg.YEARS[t]} to {cfg.YEARS[t + 1]}",
                   "Status at year t": names[k]}
            for l in range(K):
                row[names[l]] = (f"{fit.tau[t, k, l]:.3f} "
                                 f"({tau_lo[t, k, l]:.3f}-{tau_hi[t, k, l]:.3f})")
            rows.append(row)
    table3 = pd.DataFrame(rows)
    table3.to_csv(cfg.TABLES_DIR / "table3_transition_matrices.csv", index=False)
    print("\n" + table3.to_string(index=False))

    # ---- posteriors for step 03 ------------------------------------------
    modal = fit.gamma.argmax(axis=2)
    post = pd.DataFrame({
        "PIDWON": np.repeat(ids, cfg.N_WAVES),
        "wave": np.tile(np.arange(1, cfg.N_WAVES + 1), len(ids)),
        "modal_status": modal.reshape(-1) + 1,
    })
    for k in range(K):
        post[f"p_status{k + 1}"] = fit.gamma[:, :, k].reshape(-1)
    post.to_csv(cfg.DERIVED_DIR / "posterior_status.csv", index=False)

    params = {
        "K": K,
        "status_names": names,
        "indicators": cfg.INDICATORS,
        "years": cfg.YEARS,
        "log_likelihood": fit.loglik,
        "n_parameters": fit.n_params,
        "BIC": fit.bic,
        "AIC": fit.aic,
        "entropy_R2": fit.entropy_r2(),
        "n_individuals": int(Y.shape[0]),
        "delta": fit.delta.tolist(),
        "rho": fit.rho.tolist(),
        "tau": fit.tau.tolist(),
        "status_prevalence": fit.status_prevalence.tolist(),
        "status_prevalence_ci_low": prev_lo.tolist(),
        "status_prevalence_ci_high": prev_hi.tolist(),
        "rho_ci_low": rho_lo.tolist(),
        "rho_ci_high": rho_hi.tolist(),
        "tau_ci_low": tau_lo.tolist(),
        "tau_ci_high": tau_hi.tolist(),
        "mean_posterior": fit.avg_posterior().tolist(),
        "n_bootstrap": cfg.N_BOOTSTRAP,
        "seed": cfg.RANDOM_SEED,
    }
    (cfg.LOGS_DIR / "lta_parameters.json").write_text(
        json.dumps(params, indent=2), encoding="utf-8")
    print(f"\nwrote {cfg.LOGS_DIR / 'lta_parameters.json'}")


if __name__ == "__main__":
    main()
