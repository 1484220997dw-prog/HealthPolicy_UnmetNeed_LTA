"""Step 05 - write a synthetic replica of the analysis panel.

The Korea Health Panel may not be redistributed, so the repository ships a
synthetic panel instead.  It is drawn from the *fitted* latent transition model
and from the observed marginal distributions of the covariates, which means it
reproduces the structure a reader needs in order to run every script end to end
(four waves, four indicators, the same column names, a comparable amount of
attrition) without containing a single real respondent.

Numbers obtained from the synthetic panel are close to, but not identical with,
the published estimates; the manuscript reports the estimates from the real KHP
files.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import pandas as pd

from khp_lta import config as cfg

N_SYNTH = 10_000

CATEGORICAL = ["edu3", "insurance3", "region3"]
BINARY = ["female", "partnered", "employed", "chronic", "disability",
          "poor_srh", "usual_source", "private_insurance"]


def main() -> None:
    params = json.loads((cfg.LOGS_DIR / "lta_parameters.json").read_text(encoding="utf-8"))
    panel = pd.read_csv(cfg.PANEL_CSV)
    coh = panel[panel.in_cohort == 1]
    base = coh[coh.wave == 1]

    rng = np.random.default_rng(cfg.RANDOM_SEED)
    K, T = params["K"], cfg.N_WAVES
    delta = np.array(params["delta"])
    tau = np.array(params["tau"])
    rho = np.array(params["rho"])

    # latent status trajectories
    status = np.empty((N_SYNTH, T), dtype=int)
    status[:, 0] = rng.choice(K, size=N_SYNTH, p=delta / delta.sum())
    for t in range(1, T):
        for k in range(K):
            m = status[:, t - 1] == k
            if m.any():
                p = tau[t - 1, k] / tau[t - 1, k].sum()
                status[m, t] = rng.choice(K, size=int(m.sum()), p=p)

    # indicators given status
    Y = rng.random((N_SYNTH, T, len(cfg.INDICATORS))) < rho.T[status]

    # attrition: same per-wave response rates as the real cohort
    resp_rate = [float(coh.loc[coh.wave == w, "module_asked"].mean())
                 for w in range(1, T + 1)]
    observed = np.ones((N_SYNTH, T), dtype=bool)
    for t in range(1, T):
        # response at t requires response at t-1 (monotone attrition)
        p_stay = resp_rate[t] / resp_rate[t - 1]
        observed[:, t] = observed[:, t - 1] & (rng.random(N_SYNTH) < p_stay)

    # covariates, drawn from the observed baseline marginals, time-invariant
    cov = {}
    for col in CATEGORICAL:
        vals = base[col].dropna()
        cov[col] = rng.choice(vals.unique(),
                              p=vals.value_counts(normalize=True)[vals.unique()].to_numpy(),
                              size=N_SYNTH)
    for col in BINARY:
        cov[col] = (rng.random(N_SYNTH) < float(base[col].mean())).astype(float)
    cov["age"] = rng.choice(base.age.dropna().to_numpy(), size=N_SYNTH)
    cov["income_q5"] = rng.choice([1.0, 2.0, 3.0, 4.0, 5.0], size=N_SYNTH)
    w_lon = rng.choice(base.w_lon.dropna().to_numpy(), size=N_SYNTH)

    rows = []
    for t in range(T):
        block = pd.DataFrame({
            "PIDWON": np.arange(1, N_SYNTH + 1),
            "HHID": np.arange(1, N_SYNTH + 1),
            "wave": t + 1,
            "year": cfg.YEARS[t],
            "w_lon": w_lon,
            "I_WGL": w_lon,
            "I_WGC": w_lon,
            "module_asked": observed[:, t].astype(int),
            "true_status": status[:, t] + 1,
        })
        for j, name in enumerate(cfg.INDICATORS):
            block[name] = np.where(observed[:, t], Y[:, t, j].astype(float), np.nan)
        block["phy_any"] = np.where(observed[:, t],
                                    (Y[:, t, 0] | Y[:, t, 1]).astype(float), np.nan)
        block["den_any"] = np.where(observed[:, t],
                                    (Y[:, t, 2] | Y[:, t, 3]).astype(float), np.nan)
        for col, v in cov.items():
            block[col] = v
        block["age"] = block["age"] + t
        block["in_cohort"] = 1
        rows.append(block)

    synth = pd.concat(rows, ignore_index=True)
    synth["n_waves_observed"] = synth.groupby("PIDWON")["module_asked"].transform("sum")
    synth["hh_size"] = 1
    synth["hh_income"] = np.nan
    synth["eq_income"] = np.nan
    synth.to_csv(cfg.SYNTHETIC_CSV, index=False, encoding="utf-8")

    print(f"wrote {cfg.SYNTHETIC_CSV}  ({len(synth):,} person-wave rows, "
          f"{N_SYNTH:,} synthetic adults)")
    chk = synth[synth.module_asked == 1]
    print("\nsynthetic indicator prevalence (%), unweighted")
    print((100 * chk.groupby("year")[cfg.INDICATORS].mean()).round(2).to_string())
    print("\nreal-data indicator prevalence (%), unweighted, for comparison")
    real = coh[coh.module_asked == 1]
    print((100 * real.groupby("year")[cfg.INDICATORS].mean()).round(2).to_string())


if __name__ == "__main__":
    main()
