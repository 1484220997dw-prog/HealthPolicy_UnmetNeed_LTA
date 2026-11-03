"""Step 04 - Table 1, Figure 1, the appendix tables and output/logs/numbers.json.

Every number quoted in the manuscript is written to numbers.json by this step, so
the text can be checked against the analysis without re-reading the tables.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

from khp_lta import config as cfg
from khp_lta.threestep import design_matrix, fit_logit

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.linewidth": 0.6,
    "savefig.dpi": 600,
})

PALETTE = ["#4C6E8A", "#C97B4A", "#7A9A6B", "#9B5C7A"]

ROWS = [
    ("age_group", "Age group", ["19-39", "40-64", "65+"]),
    ("sex_label", "Sex", ["Men", "Women"]),
    ("edu3", "Education", ["Middle school or less", "High school", "Tertiary"]),
    ("income_q5_c", "Equivalised household income",
     ["Q1 (lowest)", "Q2", "Q3", "Q4", "Q5 (highest)"]),
    ("insurance3", "Health coverage",
     ["NHI employee-based", "NHI self-employed", "Medical Aid"]),
    ("phi_label", "Private health insurance", ["Yes", "No"]),
    ("region3", "Region of residence",
     ["Capital area", "Metropolitan city", "Other province"]),
    ("work_label", "Economic activity", ["In work", "Not in work"]),
    ("chronic_label", "Chronic condition", ["Yes", "No"]),
    ("disability_label", "Registered disability", ["Yes", "No"]),
    ("srh_label", "Self-rated health", ["Poor or very poor", "Fair or better"]),
    ("usc_label", "Usual source of care", ["Yes", "No"]),
]

Q_LABELS = {1.0: "Q1 (lowest)", 2.0: "Q2", 3.0: "Q3", 4.0: "Q4", 5.0: "Q5 (highest)"}


def label_frame(panel: pd.DataFrame, post: pd.DataFrame, names: list[str]) -> pd.DataFrame:
    df = panel[panel.in_cohort == 1].merge(post, on=["PIDWON", "wave"], how="left")
    df["age_group"] = pd.cut(df.age, [18, 39, 64, 200],
                             labels=["19-39", "40-64", "65+"]).astype(object)
    df["income_q5_c"] = df.income_q5.map(Q_LABELS)
    df["sex_label"] = df.female.map({1.0: "Women", 0.0: "Men"})
    df["phi_label"] = df.private_insurance.map({1.0: "Yes", 0.0: "No"})
    df["work_label"] = df.employed.map({1.0: "In work", 0.0: "Not in work"})
    df["chronic_label"] = df.chronic.map({1.0: "Yes", 0.0: "No"})
    df["disability_label"] = df.disability.map({1.0: "Yes", 0.0: "No"})
    df["srh_label"] = df.poor_srh.map({1.0: "Poor or very poor", 0.0: "Fair or better"})
    df["usc_label"] = df.usual_source.map({1.0: "Yes", 0.0: "No"})
    df["status_label"] = df.modal_status.map({i + 1: n for i, n in enumerate(names)})
    return df


def _wpct(g: pd.DataFrame, col: str, level: str) -> float:
    sub = g[g[col].notna()]
    if sub.w_lon.sum() == 0:
        return np.nan
    return 100 * sub.loc[sub[col] == level, "w_lon"].sum() / sub.w_lon.sum()


def _design_p(base: pd.DataFrame, col: str, levels: list[str], names: list[str]) -> float:
    """Pearson chi-square on weighted shares rescaled to the Kish effective n."""
    sub = base[base[col].notna() & base.status_label.notna()]
    if sub.empty:
        return np.nan
    n_eff = sub.w_lon.sum() ** 2 / (sub.w_lon ** 2).sum()
    tab = np.array([[sub.loc[(sub.status_label == s) & (sub[col] == lv), "w_lon"].sum()
                     for lv in levels] for s in names])
    tab = tab / tab.sum() * n_eff
    tab = tab[:, tab.sum(axis=0) > 0]
    tab = tab[tab.sum(axis=1) > 0, :]
    if min(tab.shape) < 2:
        return np.nan
    return float(stats.chi2_contingency(tab)[1])


def table1(df: pd.DataFrame, names: list[str]) -> pd.DataFrame:
    base = df[df.wave == 1]
    groups = [("All", base)] + [(n, base[base.status_label == n]) for n in names]
    rows = []
    hdr = {"Characteristic": "n (unweighted)"}
    for lab, g in groups:
        hdr[lab] = f"{len(g):,}"
    rows.append(hdr)
    hdr = {"Characteristic": "Weighted share of the cohort (%)"}
    for lab, g in groups:
        hdr[lab] = f"{100 * g.w_lon.sum() / base.w_lon.sum():.1f}"
    rows.append(hdr)
    for col, pretty, levels in ROWS:
        rows.append({"Characteristic": pretty, **{lab: "" for lab, _ in groups},
                     "p": f"{_design_p(base, col, levels, names):.3f}"})
        for lv in levels:
            row = {"Characteristic": f"   {lv}"}
            for lab, g in groups:
                row[lab] = f"{_wpct(g, col, lv):.1f}"
            rows.append(row)
    out = pd.DataFrame(rows)
    return out[["Characteristic"] + [lab for lab, _ in groups] + ["p"]]


def figure1(params: dict, df: pd.DataFrame, names: list[str]) -> dict:
    prev = 100 * np.array(params["status_prevalence"])
    lo = 100 * np.array(params["status_prevalence_ci_low"])
    hi = 100 * np.array(params["status_prevalence_ci_high"])

    tb = pd.read_csv(cfg.TABLES_DIR / "tableA4_model_b_persistence.csv")
    keep = [t for t in tb.term if not t.startswith("interval")]
    tb = tb[tb.term.isin(keep)].copy()
    pretty = {
        "age_group: 40-64": "Age 40-64", "age_group: 65+": "Age 65+",
        "female": "Female", "edu3: High school": "High school",
        "edu3: Middle school or less": "Middle school or less",
        "partnered": "Living with a partner", "employed": "In work",
        "income_q5_c: Q1 (lowest)": "Income Q1 (lowest)",
        "income_q5_c: Q2": "Income Q2", "income_q5_c: Q3": "Income Q3",
        "income_q5_c: Q4": "Income Q4",
        "insurance3: Medical Aid": "Medical Aid",
        "insurance3: NHI self-employed": "NHI self-employed",
        "private_insurance": "Private health insurance",
        "chronic": "Chronic condition", "disability": "Registered disability",
        "poor_srh": "Poor self-rated health", "usual_source": "Usual source of care",
        "region3: Metropolitan city": "Metropolitan city",
        "region3: Other province": "Other province",
    }
    for n in names[2:]:
        pretty[f"status_t: {n}"] = f"Starts: {n.lower()}"
    tb["label"] = tb.term.map(pretty)
    tb = tb.dropna(subset=["label"]).iloc[::-1].reset_index(drop=True)

    fig, axes = plt.subplots(1, 2, figsize=(7.2, 4.6),
                             gridspec_kw={"width_ratios": [1.0, 1.15]})

    # Panel A shows the three unmet-need statuses only. Plotting the
    # "no unmet need" status alongside them would compress the others into the
    # bottom eighth of the axis; its share is printed above each year instead.
    ax = axes[0]
    ks = list(range(1, params["K"]))
    width = 0.26
    x = np.arange(len(cfg.YEARS))
    for i, k in enumerate(ks):
        pos = x + (i - (len(ks) - 1) / 2) * width
        ax.bar(pos, prev[:, k], width, color=PALETTE[k], label=names[k],
               edgecolor="white", linewidth=0.3)
        ax.errorbar(pos, prev[:, k],
                    yerr=[prev[:, k] - lo[:, k], hi[:, k] - prev[:, k]],
                    fmt="none", ecolor="#333333", elinewidth=0.6, capsize=1.5)
    ax.set_xticks(x, [f"{y}\n{prev[t, 0]:.1f}%" for t, y in enumerate(cfg.YEARS)])
    ax.set_xlabel("Year, and the share with no unmet need", fontsize=7)
    ax.set_ylabel("Share of the cohort (%)")
    ax.set_title("A  Prevalence of each unmet-need status", loc="left",
                 fontsize=9, fontweight="bold")
    ax.legend(frameon=False, fontsize=6.5, loc="upper right")
    ax.set_ylim(0, hi[:, ks].max() * 1.22)

    ax = axes[1]
    y = np.arange(len(tb))
    ax.errorbar(tb.OR, y, xerr=[tb.OR - tb.ci_low, tb.ci_high - tb.OR],
                fmt="o", ms=3, color="#2F4858", ecolor="#8C9BA5",
                elinewidth=0.9, capsize=1.5, lw=0)
    ax.axvline(1, color="#999999", lw=0.6, ls="--")
    ax.set_yticks(y, tb.label, fontsize=6.5)
    ax.set_xscale("log")
    ax.set_xticks([0.5, 1, 2, 4])
    ax.set_xticklabels(["0.5", "1", "2", "4"])
    ax.set_xlabel("Adjusted odds ratio (95% CI), log scale")
    ax.set_title("B  Staying in an unmet-need status one year later",
                 loc="left", fontsize=9, fontweight="bold")
    ax.set_ylim(-0.8, len(tb) - 0.2)

    fig.tight_layout()
    stem = cfg.FIGURES_DIR / "figure1_status_prevalence_and_persistence"
    fig.savefig(f"{stem}.pdf", bbox_inches="tight")              # vector original
    fig.savefig(f"{stem}.png", bbox_inches="tight", dpi=300)
    # Elsevier asks for 300-500 dpi for a combination figure; LZW keeps the TIFF
    # from running to tens of megabytes.
    fig.savefig(f"{stem}.tif", bbox_inches="tight", dpi=300,
                pil_kwargs={"compression": "tiff_lzw"})
    plt.close(fig)
    return {"figure1_panelB_terms": int(len(tb))}


def appendix_tables(df: pd.DataFrame, panel: pd.DataFrame, names: list[str]) -> dict:
    out = {}
    # A2: reason-level weighted prevalence among module respondents
    stems = {"phy": "Physician or hospital care", "den": "Dental care"}
    reason_text = {
        1: "Cost of care or transport", 2: "Lost earnings",
        3: "Could not find the time", 4: "Opening hours or no appointment",
        5: "Did not know where to go", 6: "Transport or distance",
        7: "Mobility or health prevented the visit", 8: "Booking too complicated",
    }
    resp = df[df.module_asked == 1]
    rows = []
    for key, dom in stems.items():
        for r, txt in reason_text.items():
            col = f"{key}_r{r}"
            if col not in resp.columns:
                continue
            row = {"Domain": dom, "Reason": txt,
                   "Barrier group": ("Cost" if r in cfg.COST_REASONS
                                     else "Non-financial")}
            for year in cfg.YEARS:
                g = resp[resp.year == year]
                g = g[g[col].notna()]
                row[str(year)] = round(
                    100 * (g[col] * g.w_lon).sum() / g.w_lon.sum(), 2)
                row[f"n {year}"] = int(g[col].sum())
            rows.append(row)
    a2 = pd.DataFrame(rows)
    a2.to_csv(cfg.TABLES_DIR / "tableA2_reason_prevalence.csv", index=False)
    out["reason_table_rows"] = int(len(a2))

    # A6: complete-case sensitivity - prevalence among 4-wave responders.
    # Summed over posterior probabilities, not modal assignments, so that the
    # only difference from the main estimates is the sample.
    pcols = [c for c in df.columns if c.startswith("p_status")]

    def posterior_prevalence(frame: pd.DataFrame, weight: str) -> pd.DataFrame:
        rows = {}
        for year, g in frame.groupby("year"):
            w = g[weight].to_numpy()
            tot = w.sum()
            rows[year] = {names[k]: round(100 * float((g[c].to_numpy() * w).sum() / tot), 1)
                          for k, c in enumerate(pcols)}
        return pd.DataFrame(rows).T.rename_axis("year")

    cc = df[(df.n_waves_observed == cfg.N_WAVES) & df[pcols[0]].notna()]
    posterior_prevalence(cc, "w_lon").to_csv(
        cfg.TABLES_DIR / "tableA6_completecase_prevalence.csv")
    out["complete_case_n"] = int(cc.PIDWON.nunique())

    # A7: attrition - baseline characteristics by number of waves answered
    base = df[df.wave == 1].copy()
    base["responded_all"] = (base.n_waves_observed == cfg.N_WAVES).map(
        {True: "Answered all four waves", False: "Answered fewer waves"})
    rows = []
    for col, pretty, levels in ROWS:
        rows.append({"Characteristic": pretty, "Answered all four waves": "",
                     "Answered fewer waves": ""})
        for lv in levels:
            row = {"Characteristic": f"   {lv}"}
            for grp, g in base.groupby("responded_all"):
                row[grp] = f"{_wpct(g, col, lv):.1f}"
            rows.append(row)
    pd.DataFrame(rows).to_csv(cfg.TABLES_DIR / "tableA7_attrition.csv", index=False)

    # A8: inverse-probability-of-response weighted prevalence
    spec = {"age_group": "19-39", "female": None, "edu3": "Tertiary",
            "income_q5_c": "Q5 (highest)", "insurance3": "NHI employee-based",
            "chronic": None, "disability": None, "poor_srh": None,
            "region3": "Capital area"}
    b = base.dropna(subset=list(spec)).copy()
    X, xn = design_matrix(b, spec)
    resp = (b.n_waves_observed == cfg.N_WAVES).to_numpy(dtype=float)
    fit = fit_logit(X, resp, b.w_lon.to_numpy(), names=xn)
    p = 1 / (1 + np.exp(-(X @ fit.params)))
    b["ipw"] = b.w_lon / np.clip(p, 0.05, 1.0)
    cc2 = cc.copy()
    cc2["ipw"] = cc2.PIDWON.map(b.set_index("PIDWON")["ipw"])
    cc2 = cc2.dropna(subset=["ipw"])
    posterior_prevalence(cc2, "ipw").to_csv(
        cfg.TABLES_DIR / "tableA8_ipw_prevalence.csv")
    out["ipw_model_n"] = int(len(b))

    # How far the two attrition analyses move the headline estimates
    main = pd.DataFrame(100 * np.array(
        json.loads((cfg.LOGS_DIR / "lta_parameters.json").read_text(encoding="utf-8"))
        ["status_prevalence"]), index=cfg.YEARS, columns=names)
    for tag, frame in (("complete_case", posterior_prevalence(cc, "w_lon")),
                       ("ipw", posterior_prevalence(cc2, "ipw"))):
        diff = (frame.to_numpy() - main.to_numpy())
        out[f"max_abs_shift_{tag}_pp"] = round(float(np.abs(diff).max()), 1)
    return out


def main() -> None:
    print(f"writing results to {cfg.TABLES_DIR.parent}")
    params = json.loads((cfg.LOGS_DIR / "lta_parameters.json").read_text(encoding="utf-8"))
    names = params["status_names"]
    panel = pd.read_csv(cfg.PANEL_CSV)
    post = pd.read_csv(cfg.DERIVED_DIR / "posterior_status.csv")
    df = label_frame(panel, post, names)

    t1 = table1(df, names)
    t1.to_csv(cfg.TABLES_DIR / "table1_baseline_characteristics.csv", index=False)
    print(t1.to_string(index=False))

    nums = {}
    nums.update(figure1(params, df, names))
    nums.update(appendix_tables(df, panel, names))

    # ---- headline numbers for the manuscript ------------------------------
    coh = df[df.in_cohort == 1]
    prev = np.array(params["status_prevalence"]) * 100
    tau = np.array(params["tau"])
    cov = json.loads((cfg.LOGS_DIR / "covariate_models.json").read_text(encoding="utf-8"))

    # Persistence counts use the respondents who answered the module in all four
    # waves, so that a count of unmet-need years is never built from a wave the
    # person did not answer.
    modal = df[df.modal_status.notna() & df.module_asked.eq(1)]
    per_person = modal.groupby("PIDWON").agg(
        n_obs=("modal_status", "size"),
        n_unmet=("modal_status", lambda s: int((s > 1).sum())),
        w=("w_lon", "first"))
    comp = per_person[per_person.n_obs == cfg.N_WAVES]
    share = lambda m: float(100 * comp.loc[m, "w"].sum() / comp.w.sum())

    nums.update({
        "n_baseline_cohort": int(coh.PIDWON.nunique()),
        "n_person_waves_module_answered": int(len(modal)),
        "n_answered_all_four_waves": int(len(comp)),
        "status_names": names,
        "prevalence_2020": prev[0].round(1).tolist(),
        "prevalence_2023": prev[-1].round(1).tolist(),
        "any_unmet_2020": float(round(prev[0, 1:].sum(), 1)),
        "any_unmet_2023": float(round(prev[-1, 1:].sum(), 1)),
        "share_never_unmet_4w": round(share(comp.n_unmet == 0), 1),
        "share_once_unmet_4w": round(share(comp.n_unmet == 1), 1),
        "share_two_or_more_4w": round(share(comp.n_unmet >= 2), 1),
        "share_three_or_more_4w": round(share(comp.n_unmet >= 3), 1),
        "share_all_four_4w": round(share(comp.n_unmet == 4), 1),
        "stay_prob_mean": {names[k]: round(float(tau[:, k, k].mean()), 3)
                           for k in range(params["K"])},
        "exit_to_no_unmet_mean": {names[k]: round(float(tau[:, k, 0].mean()), 3)
                                  for k in range(1, params["K"])},
        "entry_from_no_unmet_mean": round(float(1 - tau[:, 0, 0].mean()), 3),
        "entropy_R2": round(params["entropy_R2"], 3),
        "bic_selected": round(params["BIC"], 1),
        "n_bootstrap": params["n_bootstrap"],
        "model_a_n": cov["model_a_n"],
        "model_b_n_pairs": cov["model_b_n_pairs"],
        "model_b_n_individuals": cov["model_b_n_individuals"],
        "model_b_persist_rate": round(100 * cov["model_b_persist_rate"], 1),
    })
    prevyear = pd.read_csv(cfg.LOGS_DIR / "indicator_prevalence_by_year.csv", index_col=0)
    nums["indicator_prevalence_by_year"] = prevyear.round(2).to_dict()

    cfg.NUMBERS_JSON.write_text(json.dumps(nums, indent=2, ensure_ascii=False),
                                encoding="utf-8")
    print("\n" + json.dumps(nums, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
