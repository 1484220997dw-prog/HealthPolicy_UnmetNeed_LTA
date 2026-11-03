"""Weighted multinomial and binary logit with cluster-robust standard errors.

Step three of the classify-analyse-adjust ("three-step") LTA workflow.  The
measurement model is estimated first (step 02), respondents are then assigned to
latent statuses, and covariate associations are estimated here.  Both estimators
are written out explicitly rather than taken from a library so that survey
weights, posterior-probability weights and clustering by person can be combined
in one place.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import optimize, stats


# --------------------------------------------------------------------------- #
# Design matrices
# --------------------------------------------------------------------------- #
def design_matrix(df: pd.DataFrame, spec: dict[str, object]):
    """Build an intercept-plus-covariates matrix from a {column: reference} spec.

    A ``None`` reference marks a numeric column, a string marks the reference
    level of a categorical column.
    """
    cols, names = [np.ones(len(df))], ["Intercept"]
    for col, ref in spec.items():
        if ref is None:
            cols.append(df[col].to_numpy(dtype=float))
            names.append(col)
        else:
            levels = [v for v in sorted(df[col].dropna().unique()) if v != ref]
            for lv in levels:
                cols.append((df[col] == lv).to_numpy(dtype=float))
                names.append(f"{col}: {lv}")
    return np.column_stack(cols), names


# --------------------------------------------------------------------------- #
# Weighted multinomial logit
# --------------------------------------------------------------------------- #
@dataclass
class MNLogitResult:
    params: np.ndarray            # (p, K-1)
    se: np.ndarray                # (p, K-1)
    names: list[str]
    outcome_labels: list[str]
    loglik: float
    n: int

    def table(self) -> pd.DataFrame:
        rows = []
        for m, lab in enumerate(self.outcome_labels):
            for i, nm in enumerate(self.names):
                if nm == "Intercept":
                    continue
                b, s = self.params[i, m], self.se[i, m]
                z = b / s
                rows.append({
                    "outcome": lab,
                    "term": nm,
                    "RRR": np.exp(b),
                    "ci_low": np.exp(b - 1.96 * s),
                    "ci_high": np.exp(b + 1.96 * s),
                    "p_value": 2 * stats.norm.sf(abs(z)),
                })
        return pd.DataFrame(rows)


def _mn_negll(beta_flat, X, Yd, w, K):
    p = X.shape[1]
    B = np.concatenate([np.zeros((p, 1)), beta_flat.reshape(p, K - 1)], axis=1)
    eta = X @ B
    eta -= eta.max(axis=1, keepdims=True)
    lse = np.log(np.exp(eta).sum(axis=1))
    ll = (w * ((Yd * eta).sum(axis=1) - lse)).sum()
    P = np.exp(eta - lse[:, None])
    grad = X.T @ (w[:, None] * (Yd - P))
    return -ll, -grad[:, 1:].ravel()


def fit_mnlogit(X, y, w, clusters=None, outcome_labels=None,
                names=None) -> MNLogitResult:
    """y must hold integer codes 0..K-1 with 0 as the reference category."""
    K = int(y.max()) + 1
    p = X.shape[1]
    Yd = np.eye(K)[y]
    w = np.asarray(w, dtype=float)
    res = optimize.minimize(_mn_negll, np.zeros(p * (K - 1)),
                            args=(X, Yd, w, K), jac=True, method="L-BFGS-B",
                            options={"maxiter": 2000, "ftol": 1e-12})
    B1 = res.x.reshape(p, K - 1)
    B = np.concatenate([np.zeros((p, 1)), B1], axis=1)
    eta = X @ B
    eta -= eta.max(axis=1, keepdims=True)
    P = np.exp(eta) / np.exp(eta).sum(axis=1, keepdims=True)

    # observed information (block form) and cluster-robust sandwich
    d = p * (K - 1)
    H = np.zeros((d, d))
    for m in range(1, K):
        for l in range(1, K):
            wk = w * P[:, m] * ((m == l) - P[:, l])
            H[(m - 1) * p:m * p, (l - 1) * p:l * p] = X.T @ (wk[:, None] * X)
    Hinv = np.linalg.pinv(H)

    score = np.concatenate([(w[:, None] * (Yd[:, [m]] - P[:, [m]])) * X
                            for m in range(1, K)], axis=1)
    if clusters is None:
        meat = score.T @ score
    else:
        cl = pd.Series(clusters)
        agg = np.vstack([score[np.asarray(ix)].sum(axis=0)
                         for ix in cl.groupby(cl).indices.values()])
        meat = agg.T @ agg
    V = Hinv @ meat @ Hinv
    se = np.sqrt(np.clip(np.diag(V), 0, None)).reshape(K - 1, p).T
    return MNLogitResult(params=B1, se=se,
                         names=names or [f"x{i}" for i in range(p)],
                         outcome_labels=outcome_labels or
                         [f"status {m + 1}" for m in range(1, K)],
                         loglik=float(-res.fun), n=len(y))


# --------------------------------------------------------------------------- #
# Weighted binary logit
# --------------------------------------------------------------------------- #
@dataclass
class LogitResult:
    params: np.ndarray
    se: np.ndarray
    names: list[str]
    loglik: float
    n: int

    def table(self) -> pd.DataFrame:
        rows = []
        for b, s, nm in zip(self.params, self.se, self.names):
            if nm == "Intercept":
                continue
            rows.append({
                "term": nm,
                "OR": np.exp(b),
                "ci_low": np.exp(b - 1.96 * s),
                "ci_high": np.exp(b + 1.96 * s),
                "p_value": 2 * stats.norm.sf(abs(b / s)),
            })
        return pd.DataFrame(rows)


def _logit_negll(beta, X, y, w):
    eta = X @ beta
    ll = (w * (y * eta - np.logaddexp(0.0, eta))).sum()
    pr = 1 / (1 + np.exp(-eta))
    return -ll, -(X.T @ (w * (y - pr)))


def fit_logit(X, y, w, clusters=None, names=None) -> LogitResult:
    w = np.asarray(w, dtype=float)
    res = optimize.minimize(_logit_negll, np.zeros(X.shape[1]),
                            args=(X, y, w), jac=True, method="L-BFGS-B",
                            options={"maxiter": 2000, "ftol": 1e-12})
    beta = res.x
    pr = 1 / (1 + np.exp(-(X @ beta)))
    H = X.T @ ((w * pr * (1 - pr))[:, None] * X)
    Hinv = np.linalg.pinv(H)
    score = (w * (y - pr))[:, None] * X
    if clusters is None:
        meat = score.T @ score
    else:
        cl = pd.Series(clusters)
        agg = np.vstack([score[np.asarray(ix)].sum(axis=0)
                         for ix in cl.groupby(cl).indices.values()])
        meat = agg.T @ agg
    V = Hinv @ meat @ Hinv
    return LogitResult(params=beta, se=np.sqrt(np.clip(np.diag(V), 0, None)),
                       names=names or [f"x{i}" for i in range(X.shape[1])],
                       loglik=float(-res.fun), n=len(y))
