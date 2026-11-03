"""Step 03 - who starts in, and who stays in, an unmet-need status.

Two covariate models on top of the fitted measurement model (three-step LTA):

  Model A  weighted multinomial logit for the 2020 baseline latent status
  Model B  weighted logit for remaining in any unmet-need status one year later,
           among person-waves that start in an unmet-need status

Writes the two full regression tables as appendix files, a combined view of
both (Table A10), and a sensitivity version that weights every respondent by
the posterior probability of each status instead of using modal assignment.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import pandas as pd

from khp_lta import config as cfg
from khp_lta.threestep import design_matrix, fit_logit, fit_mnlogit

# column -> reference level (None marks a numeric covariate)
SPEC: dict[str, object] = {
    "age_group": "19-39",
    "female": None,
    "edu3": "Tertiary",
    "partnered": None,
    "employed": None,
    "income_q5_c": "Q5 (highest)",
    "insurance3": "NHI employee-based",
    "private_insurance": None,
    "chronic": None,
    "disability": None,
    "poor_srh": None,
    "usual_source": None,
    "region3": "Capital area",
}

PRETTY = {
    "age_group: 40-64": "Age 40-64 (ref 19-39)",
    "age_group: 65+": "Age 65 or over (ref 19-39)",
    "female": "Female",
    "edu3: High school": "High school (ref tertiary)",
    "edu3: Middle school or less": "Middle school or less (ref tertiary)",
    "partnered": "Living with a partner",
    "employed": "In work",
    "income_q5_c: Q1 (lowest)": "Income quintile 1, lowest (ref Q5)",
    "income_q5_c: Q2": "Income quintile 2 (ref Q5)",
    "income_q5_c: Q3": "Income quintile 3 (ref Q5)",
    "income_q5_c: Q4": "Income quintile 4 (ref Q5)",
    "insurance3: Medical Aid": "Medical Aid (ref NHI employee-based)",
    "insurance3: NHI self-employed": "NHI self-employed (ref NHI employee-based)",
    "private_insurance": "Holds private health insurance",
    "chronic": "Chronic condition",
    "disability": "Registered disability",
    "poor_srh": "Poor or very poor self-rated health",
    "usual_source": "Has a usual source of care",
    "region3: Metropolitan city": "Metropolitan city (ref capital area)",
    "region3: Other province": "Other province (ref capital area)",
    "interval: 2021-2022": "Interval 2021-2022 (ref 2020-2021)",
    "interval: 2022-2023": "Interval 2022-2023 (ref 2020-2021)",
}


def add_status_labels(names: list[str]) -> None:
    """Label the status-at-t terms from the fitted status names, not by hand."""
    for n in names[2:]:
        PRETTY[f"status_t: {n}"] = f"Starts in the {n.lower()} status (ref {names[1].lower()})"

Q_LABELS = {1.0: "Q1 (lowest)", 2.0: "Q2", 3.0: "Q3", 4.0: "Q4", 5.0: "Q5 (highest)"}


def prepare(panel: pd.DataFrame, post: pd.DataFrame, names: list[str]) -> pd.DataFrame:
    df = panel[panel.in_cohort == 1].merge(post, on=["PIDWON", "wave"], how="left")
    df["age_group"] = pd.cut(df.age, [18, 39, 64, 200],
                             labels=["19-39", "40-64", "65+"]).astype(object)
    df["income_q5_c"] = df.income_q5.map(Q_LABELS)
    df["status_label"] = df.modal_status.map(
        {i + 1: n for i, n in enumerate(names)})
    df["unmet_any"] = (df.modal_status > 1).astype(float)
    return df


def model_a(df: pd.DataFrame, names: list[str]):
    base = df[(df.wave == 1) & df.modal_status.notna()].copy()
    need = list(SPEC) + ["w_lon", "modal_status"]
    base = base.dropna(subset=need)
    X, xn = design_matrix(base, SPEC)
    y = (base.modal_status.to_numpy(dtype=int) - 1)
    res = fit_mnlogit(X, y, base.w_lon.to_numpy(), clusters=base.HHID.to_numpy(),
                      outcome_labels=names[1:], names=xn)
    return res, len(base)


def model_b(df: pd.DataFrame, names: list[str]):
    nxt = df[["PIDWON", "wave", "modal_status"]].copy()
    nxt["wave"] -= 1
    nxt = nxt.rename(columns={"modal_status": "status_next"})
    pairs = df.merge(nxt, on=["PIDWON", "wave"], how="inner")
    pairs = pairs[(pairs.modal_status > 1) & pairs.status_next.notna()].copy()
    pairs["persist"] = (pairs.status_next > 1).astype(float)
    pairs["status_t"] = pairs.modal_status.map({i + 1: n for i, n in enumerate(names)})
    pairs["interval"] = pairs.wave.map({1: "2020-2021", 2: "2021-2022", 3: "2022-2023"})

    spec = dict(SPEC)
    spec["status_t"] = names[1]
    spec["interval"] = "2020-2021"
    need = [c for c in spec] + ["w_lon", "persist"]
    pairs = pairs.dropna(subset=need)
    X, xn = design_matrix(pairs, spec)
    res = fit_logit(X, pairs.persist.to_numpy(dtype=float), pairs.w_lon.to_numpy(),
                    clusters=pairs.PIDWON.to_numpy(), names=xn)
    return res, len(pairs), pairs


def model_b_posterior(df: pd.DataFrame, names: list[str]):
    """Sensitivity: weight each person-wave by its posterior status probabilities."""
    pcols = [c for c in df.columns if c.startswith("p_status")]
    nxt = df[["PIDWON", "wave"] + pcols].copy()
    nxt["wave"] -= 1
    nxt = nxt.rename(columns={c: f"{c}_next" for c in pcols})
    pairs = df.merge(nxt, on=["PIDWON", "wave"], how="inner").copy()
    pairs["p_unmet_t"] = pairs[pcols[1:]].sum(axis=1)
    pairs["p_unmet_next"] = pairs[[f"{c}_next" for c in pcols[1:]]].sum(axis=1)
    pairs = pairs[pairs.p_unmet_t > 0.01].copy()
    pairs["interval"] = pairs.wave.map({1: "2020-2021", 2: "2021-2022", 3: "2022-2023"})

    spec = {k: v for k, v in SPEC.items()}
    spec["interval"] = "2020-2021"
    long = []
    for outcome in (1.0, 0.0):
        g = pairs.copy()
        g["persist"] = outcome
        g["wt"] = g.w_lon * g.p_unmet_t * (g.p_unmet_next if outcome == 1.0
                                           else 1 - g.p_unmet_next)
        long.append(g)
    long = pd.concat(long, ignore_index=True)
    long = long[long.wt > 1e-8].dropna(subset=list(spec) + ["wt"])
    X, xn = design_matrix(long, spec)
    return fit_logit(X, long.persist.to_numpy(dtype=float), long.wt.to_numpy(),
                     clusters=long.PIDWON.to_numpy(), names=xn)


def fmt(row, col: str = "OR") -> str:
    """Point estimate with its 95% interval and a significance marker."""
    stars = ("***" if row.p_value < 0.001 else "**" if row.p_value < 0.01
             else "*" if row.p_value < 0.05 else "")
    return f"{row[col]:.2f} ({row.ci_low:.2f}-{row.ci_high:.2f}){stars}"


def main() -> None:
    print(f"writing results to {cfg.TABLES_DIR.parent}")
    params = json.loads((cfg.LOGS_DIR / "lta_parameters.json").read_text(encoding="utf-8"))
    names = params["status_names"]
    panel = pd.read_csv(cfg.PANEL_CSV)
    post = pd.read_csv(cfg.DERIVED_DIR / "posterior_status.csv")
    add_status_labels(names)
    df = prepare(panel, post, names)

    res_a, n_a = model_a(df, names)
    ta = res_a.table()
    ta["estimate"] = ta.apply(fmt, axis=1, col="RRR")
    ta.to_csv(cfg.TABLES_DIR / "tableA3_model_a_baseline_status.csv", index=False)
    print(f"Model A: multinomial logit, n = {n_a:,}")
    print(ta[["outcome", "term", "estimate"]].to_string(index=False))

    res_b, n_b, pairs = model_b(df, names)
    tb = res_b.table()
    tb["estimate"] = tb.apply(fmt, axis=1, col="OR")
    tb.to_csv(cfg.TABLES_DIR / "tableA4_model_b_persistence.csv", index=False)
    print(f"\nModel B: persistence logit, n = {n_b:,} person-wave pairs "
          f"({pairs.PIDWON.nunique():,} individuals)")
    print(tb[["term", "estimate"]].to_string(index=False))

    res_b2 = model_b_posterior(df, names)
    tb2 = res_b2.table()
    tb2["estimate"] = tb2.apply(fmt, axis=1, col="OR")
    tb2.to_csv(cfg.TABLES_DIR / "tableA5_model_b_posterior_weighted.csv", index=False)

    # ---- Table A10: the two models side by side, in reading order ---------
    rows = []
    order = [t for t in PRETTY if t in set(ta.term) | set(tb.term)]
    for term in order:
        row = {"Characteristic": PRETTY[term]}
        for lab in names[1:]:
            sub = ta[(ta.outcome == lab) & (ta.term == term)]
            row[f"RRR: {lab}"] = fmt(sub.iloc[0], "RRR") if len(sub) else ""
        sub = tb[tb.term == term]
        row["OR: stays unmet next year"] = (fmt(sub.iloc[0], "OR")
                                            if len(sub) else "")
        rows.append(row)
    combined = pd.DataFrame(rows)
    combined.to_csv(cfg.TABLES_DIR / "tableA10_covariates_combined.csv", index=False)
    print("\n" + combined.to_string(index=False))

    summary = {
        "model_a_n": int(n_a),
        "model_b_n_pairs": int(n_b),
        "model_b_n_individuals": int(pairs.PIDWON.nunique()),
        "model_b_persist_rate": float(np.average(pairs.persist, weights=pairs.w_lon)),
        "model_a_loglik": res_a.loglik,
        "model_b_loglik": res_b.loglik,
    }
    (cfg.LOGS_DIR / "covariate_models.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8")
    print("\n" + json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
