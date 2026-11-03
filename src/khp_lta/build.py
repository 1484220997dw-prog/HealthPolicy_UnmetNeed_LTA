"""Build the analysis-ready person-wave panel from the KHP annual SPSS files."""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import config as cfg


def _clean(series: pd.Series) -> pd.Series:
    out = series.copy()
    return out.mask(out.isin(cfg.MISSING_CODES))


def _read_wave(wave: int) -> pd.DataFrame:
    import pyreadstat

    year, folder, fname = cfg.WAVES[wave]
    path = cfg.raw_dir() / folder / fname
    if not path.exists():
        raise FileNotFoundError(
            f"KHP file not found: {path}\n"
            "Set KHP_RAW_DIR to the folder that holds the KHP+<year>_spss directories."
        )
    df, _ = pyreadstat.read_sav(str(path), usecols=cfg.RAW_COLUMNS)
    df["wave"] = wave
    df["year"] = year
    return df


def _unmet_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Four binary indicators: physician/dental care by cost/non-financial barrier."""
    out = pd.DataFrame(index=df.index)
    for key, stem in cfg.UNMET_STEMS.items():
        base = _clean(df[stem])
        asked = base.notna()                       # module administered (age 19+)
        any_unmet = base.eq(1)
        for label, reasons in (("cost", cfg.COST_REASONS),
                               ("noncost", cfg.NONCOST_REASONS)):
            cols = [f"{stem}_{i}_D" for i in reasons]
            flag = pd.concat([_clean(df[c]).eq(1) for c in cols], axis=1).any(axis=1)
            ind = (any_unmet & flag).astype(float)
            out[f"{key}_{label}"] = ind.where(asked)
        for i in cfg.COST_REASONS + cfg.NONCOST_REASONS:
            flag = _clean(df[f"{stem}_{i}_D"]).eq(1)
            out[f"{key}_r{i}"] = (any_unmet & flag).astype(float).where(asked)
        out[f"{key}_any"] = any_unmet.astype(float).where(asked)
    out["module_asked"] = (
        out[[f"{k}_any" for k in cfg.UNMET_STEMS]].notna().any(axis=1).astype(int)
    )
    return out


def _covariates(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(index=df.index)
    out["age"] = df["year"] - _clean(df["BIRTH_Y"])
    out["female"] = _clean(df["SEX"]).eq(2).astype(float)

    edu = _clean(df["EDU"])
    out["edu3"] = np.select(
        [edu.isin([1, 2, 3]), edu.eq(4), edu.isin([5, 6])],
        ["Middle school or less", "High school", "Tertiary"],
        default=None,
    )

    marr = _clean(df["MARR"])
    out["partnered"] = marr.eq(1).astype(float).where(marr.notna() & marr.ne(6))

    eco = _clean(df["ECO1"])
    out["employed"] = eco.isin([1, 2, 3, 4, 5]).astype(float).where(eco.notna())

    reg = _clean(df["REGION1"])
    out["region3"] = np.select(
        [reg.isin(cfg.CAPITAL_AREA), reg.isin(cfg.METRO_CITIES), reg.notna()],
        ["Capital area", "Metropolitan city", "Other province"],
        default=None,
    )

    ins = _clean(df["HEALTH_INS"])
    out["insurance3"] = np.select(
        [ins.isin([1, 2]), ins.isin([3, 4]), ins.isin([5, 6])],
        ["NHI employee-based", "NHI self-employed", "Medical Aid"],
        default=None,
    )
    out.loc[ins.isin([7, 8]), "insurance3"] = None

    out["hh_income"] = _clean(df["H_INC_TOT"])          # annual, 10 000 KRW
    out["chronic"] = _clean(df["CD"]).eq(1).astype(float)
    out["disability"] = _clean(df["DISA_YN"]).eq(1).astype(float)
    srh = _clean(df["HS_SRH"])
    out["poor_srh"] = srh.isin([4, 5]).astype(float).where(srh.notna())
    out["usual_source"] = _clean(df["USC1_YN"]).eq(1).astype(float)
    out["private_insurance"] = _clean(df["I_PHI1_YN"]).eq(1).astype(float)
    return out


def build_panel(verbose: bool = True) -> pd.DataFrame:
    frames = []
    for wave in sorted(cfg.WAVES):
        raw = _read_wave(wave)
        size = raw.groupby("HHID")["PIDWON"].transform("size")
        block = pd.concat(
            [
                raw[["PIDWON", "HHID", "wave", "year", "I_WGL", "I_WGC"]].reset_index(drop=True),
                _unmet_indicators(raw).reset_index(drop=True),
                _covariates(raw).reset_index(drop=True),
            ],
            axis=1,
        )
        # Equivalised household income: household total / sqrt(household size).
        block["hh_size"] = size.to_numpy()
        block["eq_income"] = block["hh_income"] / np.sqrt(block["hh_size"])
        if verbose:
            print(f"wave {wave} ({int(raw['year'].iat[0])}): {len(block):6d} rows, "
                  f"module asked for {int(block['module_asked'].sum()):6d}")
        frames.append(block)

    panel = pd.concat(frames, ignore_index=True)
    panel["PIDWON"] = panel["PIDWON"].astype("int64")

    # Income quintiles within wave, among respondents to the unmet-need module.
    panel["income_q5"] = np.nan
    for wave in sorted(cfg.WAVES):
        m = (panel.wave == wave) & panel.eq_income.notna() & panel.module_asked.eq(1)
        if m.sum() > 0:
            panel.loc[m, "income_q5"] = pd.qcut(
                panel.loc[m, "eq_income"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]
            ).astype(float)

    # Baseline-cohort restriction: adults aged 19+ in 2020 who answered the
    # unmet-need module at least once over 2020-2023.
    base = panel[(panel.wave == 1) & (panel.age >= 19) & (panel.module_asked == 1)]
    keep = sorted(set(base.PIDWON))
    panel["in_cohort"] = panel.PIDWON.isin(keep).astype(int)

    # Analysis weight: baseline longitudinal individual weight, rescaled to mean 1.
    w = panel[panel.wave == 1].set_index("PIDWON")["I_WGL"].reindex(keep)
    w = w / w.mean()
    panel["w_lon"] = panel.PIDWON.map(w)

    n_wave_obs = (panel[panel.in_cohort == 1]
                  .groupby("PIDWON")["module_asked"].sum()
                  .rename("n_waves_observed"))
    panel = panel.merge(n_wave_obs, on="PIDWON", how="left")

    if verbose:
        print(f"baseline cohort: {len(keep)} adults; "
              f"complete 4-wave responders: {int((n_wave_obs == cfg.N_WAVES).sum())}")
    return panel


def indicator_array(panel: pd.DataFrame, complete_only: bool = False):
    """Return (Y, weights, ids) with Y of shape (N, T, J) and NaN where missing."""
    coh = panel[panel.in_cohort == 1].copy()
    if complete_only:
        coh = coh[coh.n_waves_observed == cfg.N_WAVES]
    ids = np.sort(coh.PIDWON.unique())
    pos = {p: i for i, p in enumerate(ids)}
    Y = np.full((len(ids), cfg.N_WAVES, len(cfg.INDICATORS)), np.nan)
    idx = coh.PIDWON.map(pos).to_numpy()
    tt = (coh.wave.to_numpy() - 1).astype(int)
    for j, name in enumerate(cfg.INDICATORS):
        Y[idx, tt, j] = coh[name].to_numpy(dtype=float)
    wmap = coh.drop_duplicates("PIDWON").set_index("PIDWON")["w_lon"]
    w = wmap.reindex(ids).to_numpy(dtype=float)
    w = np.where(np.isfinite(w) & (w > 0), w, np.nan)
    w = w / np.nanmean(w)
    return Y, w, ids
