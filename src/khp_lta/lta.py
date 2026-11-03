"""Latent transition analysis for binary indicators, fitted by weighted EM.

Model
-----
For person *i* observed at waves t = 1..T with J binary indicators:

    S_i1 ~ Categorical(delta)                       (initial status)
    S_i,t+1 | S_it = k ~ Categorical(tau[t][k, .])  (wave-specific transitions)
    Y_itj | S_it = k ~ Bernoulli(rho[j, k])         (measurement, time-invariant)

Time-invariant ``rho`` imposes full measurement invariance across waves, which is
what makes the transition probabilities interpretable as movement between the
same statuses rather than as drift in what the statuses mean.

Missing indicator values are handled by full-information maximum likelihood: the
measurement likelihood is taken over the observed indicators only, so a wave a
respondent did not answer contributes nothing to the measurement part while the
person is still retained in the transition part of the likelihood (missing at
random given the observed responses).

Survey weights enter as frequency weights, rescaled to mean 1 so that the
information criteria use the number of sampled individuals.

Fitting follows the two-stage random-start strategy that is standard for mixture
models: many short runs locate the basin of the global maximum, then the best
few are iterated to convergence.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

EPS = 1e-10
RHO_FLOOR = 1e-6


# --------------------------------------------------------------------------- #
# Parameter container
# --------------------------------------------------------------------------- #
@dataclass
class LTAFit:
    K: int
    delta: np.ndarray                 # (K,)
    tau: np.ndarray                   # (T-1, K, K)
    rho: np.ndarray                   # (J, K)
    loglik: float
    n_iter: int
    n_obs: int
    gamma: np.ndarray = field(repr=False, default=None)   # (N, T, K) posteriors
    prevalence: np.ndarray = field(repr=False, default=None)   # (T, K)
    homogeneous: bool = False

    @property
    def n_params(self) -> int:
        K, J = self.K, self.rho.shape[0]
        n_trans = (1 if self.homogeneous else self.tau.shape[0]) * K * (K - 1)
        return (K - 1) + n_trans + J * K

    @property
    def aic(self) -> float:
        return -2 * self.loglik + 2 * self.n_params

    @property
    def bic(self) -> float:
        return -2 * self.loglik + self.n_params * np.log(self.n_obs)

    @property
    def status_prevalence(self) -> np.ndarray:
        """Weighted share in each status, by wave: shape (T, K)."""
        return self.prevalence

    def entropy_r2(self) -> float:
        if self.K == 1:
            return float("nan")
        g = np.clip(self.gamma, EPS, 1.0)
        ent = -(g * np.log(g)).sum()
        return float(1 - ent / (g.shape[0] * g.shape[1] * np.log(self.K)))

    def avg_posterior(self) -> np.ndarray:
        """Mean posterior probability of the assigned status, per status."""
        modal = self.gamma.argmax(axis=2)
        out = np.full(self.K, np.nan)
        for k in range(self.K):
            m = modal == k
            if m.any():
                out[k] = self.gamma[:, :, k][m].mean()
        return out

    def modal_counts(self) -> np.ndarray:
        modal = self.gamma.argmax(axis=2)
        return np.array([int((modal == k).sum()) for k in range(self.K)])


# --------------------------------------------------------------------------- #
# E step
# --------------------------------------------------------------------------- #
def _emission(YM: np.ndarray, NM: np.ndarray, rho: np.ndarray, shape) -> np.ndarray:
    """P(observed indicators | status) for every person-wave: (N, T, K).

    ``YM`` and ``NM`` are the flattened (N*T, J) arrays of y*observed and
    (1-y)*observed, so the whole measurement step is one BLAS call.
    """
    r = np.clip(rho, RHO_FLOOR, 1 - RHO_FLOOR)
    log_b = YM @ np.log(r) + NM @ np.log1p(-r)
    np.exp(log_b, out=log_b)
    return log_b.reshape(shape)


def _estep(b: np.ndarray, delta: np.ndarray, tau: np.ndarray, wn: np.ndarray):
    """Scaled forward-backward.

    Returns the posterior status probabilities ``gamma`` (N, T, K), the
    weight-summed pairwise posteriors ``xi_sum`` (T-1, K, K) that the M step
    needs, and the per-person log-likelihood.  The pairwise posteriors are
    accumulated with two matrix products instead of being materialised for
    every person, which is what makes thousands of EM iterations affordable.
    """
    N, T, K = b.shape
    alpha = np.empty((N, T, K))
    scale = np.empty((N, T))

    a = delta[None, :] * b[:, 0, :]
    scale[:, 0] = a.sum(axis=1)
    alpha[:, 0, :] = a / np.maximum(scale[:, 0], EPS)[:, None]
    for t in range(1, T):
        a = (alpha[:, t - 1, :] @ tau[t - 1]) * b[:, t, :]
        scale[:, t] = a.sum(axis=1)
        alpha[:, t, :] = a / np.maximum(scale[:, t], EPS)[:, None]

    beta = np.ones((N, T, K))
    xi_sum = np.empty((T - 1, K, K))
    for t in range(T - 2, -1, -1):
        nxt = (b[:, t + 1, :] * beta[:, t + 1, :]
               / np.maximum(scale[:, t + 1], EPS)[:, None])
        beta[:, t, :] = nxt @ tau[t].T
        xi_sum[t] = tau[t] * ((wn[:, None] * alpha[:, t, :]).T @ nxt)

    gamma = alpha * beta
    gamma /= np.maximum(gamma.sum(axis=2, keepdims=True), EPS)
    ll_i = np.log(np.maximum(scale, EPS)).sum(axis=1)
    return gamma, xi_sum, ll_i


# --------------------------------------------------------------------------- #
# Single EM run
# --------------------------------------------------------------------------- #
def _random_start(Y, J, K, T, rng):
    delta = rng.dirichlet(np.ones(K) * 5)
    tau = np.stack([rng.dirichlet(np.ones(K) + 4 * np.eye(K)[k])
                    for _ in range(T - 1) for k in range(K)]).reshape(T - 1, K, K)
    base = np.nanmean(Y.reshape(-1, J), axis=0)
    rho = np.clip(base[:, None] * rng.uniform(0.05, 3.0, size=(J, K)), 0.001, 0.98)
    return delta, tau, rho


def _pack(delta, tau, rho):
    return np.concatenate([delta.ravel(), tau.ravel(), rho.ravel()])


def _unpack(v, K, T, J):
    n_tau = (T - 1) * K * K
    delta = v[:K]
    tau = v[K:K + n_tau].reshape(T - 1, K, K)
    rho = v[K + n_tau:].reshape(J, K)
    return delta, tau, rho


def _project(delta, tau, rho):
    """Pull an extrapolated point back into the parameter space."""
    delta = np.clip(delta, EPS, None)
    delta = delta / delta.sum()
    tau = np.clip(tau, EPS, None)
    tau = tau / tau.sum(axis=2, keepdims=True)
    rho = np.clip(rho, RHO_FLOOR, 1 - RHO_FLOOR)
    return delta, tau, rho


def fit_once(Y: np.ndarray, w: np.ndarray, K: int, rng: np.random.Generator,
             homogeneous: bool = False, max_iter: int = 5000,
             tol: float = 1e-7, start=None) -> LTAFit:
    """One EM run.  ``tol`` is an absolute tolerance on the log-likelihood."""
    N, T, J = Y.shape
    M = (~np.isnan(Y)).astype(float)
    Yf = np.nan_to_num(Y)
    YM = (Yf * M).reshape(N * T, J)
    NM = ((1 - Yf) * M).reshape(N * T, J)
    wn = w / w.mean()
    W = wn[:, None]
    Wflat = np.repeat(wn, T)[:, None]

    delta, tau, rho = (_random_start(Y, J, K, T, rng) if start is None
                       else tuple(a.copy() for a in start))

    def em_step(params):
        """One EM update; returns the new parameters and the log-likelihood at
        the parameters that went in."""
        d, tt, rr = params
        b = _emission(YM, NM, rr, (N, T, K))
        gamma, xi_sum, ll_i = _estep(b, d, tt, wn)
        ll = float((wn * ll_i).sum())

        d_new = (W * gamma[:, 0, :]).sum(axis=0)
        d_new = d_new / d_new.sum()

        if homogeneous:
            pooled = xi_sum.sum(axis=0)
            t_new = pooled / np.maximum(pooled.sum(axis=1, keepdims=True), EPS)
            t_new = np.repeat(t_new[None, :, :], T - 1, axis=0)
        else:
            t_new = xi_sum / np.maximum(xi_sum.sum(axis=2, keepdims=True), EPS)

        gw = gamma.reshape(N * T, K) * Wflat
        num_rho = (gw.T @ YM).T
        den_rho = (gw.T @ (YM + NM)).T
        r_new = np.clip(num_rho / np.maximum(den_rho, EPS), RHO_FLOOR, 1 - RHO_FLOOR)
        return (d_new, t_new, r_new), ll

    # --- SQUAREM-accelerated EM (Varadhan & Roland 2008) -------------------- #
    # Plain EM creeps along the likelihood ridge of a latent transition model;
    # squared extrapolation of two successive EM steps reaches the same maximum
    # in roughly a fifth of the iterations, with a stabilising EM step and a
    # fall-back to ordinary EM whenever the extrapolation does not improve the
    # likelihood.
    params = (delta, tau, rho)
    prev_ll, n_iter = -np.inf, 0
    while n_iter < max_iter:
        p1, ll0 = em_step(params)
        p2, ll1 = em_step(p1)
        n_iter += 2
        v0, v1, v2 = _pack(*params), _pack(*p1), _pack(*p2)
        r = v1 - v0
        u = v2 - v1 - r
        nu = np.linalg.norm(u)
        params, cur_ll = p2, ll1
        if nu > 1e-12 and n_iter < max_iter:
            alpha = float(np.clip(-np.linalg.norm(r) / nu, -8.0, -1.0))
            cand = _project(*_unpack(v0 - 2 * alpha * r + alpha * alpha * u,
                                     K, T, J))
            p3, ll2 = em_step(cand)
            n_iter += 1
            if np.isfinite(ll2) and ll2 >= ll1:
                params, cur_ll = p3, ll2
        if cur_ll - prev_ll < tol and n_iter > 20:
            prev_ll = cur_ll
            break
        prev_ll = cur_ll
    delta, tau, rho = params

    b = _emission(YM, NM, rho, (N, T, K))
    gamma, _, ll_i = _estep(b, delta, tau, wn)
    ll = float((wn * ll_i).sum())
    prevalence = (gamma * W[:, :, None]).sum(axis=0) / wn.sum()
    return LTAFit(K=K, delta=delta, tau=tau, rho=rho, loglik=ll, n_iter=n_iter,
                  n_obs=N, gamma=gamma, prevalence=prevalence,
                  homogeneous=homogeneous)


def _permute(fit: LTAFit, order: np.ndarray) -> LTAFit:
    fit.delta = fit.delta[order]
    fit.tau = fit.tau[:, order, :][:, :, order]
    fit.rho = fit.rho[:, order]
    fit.gamma = fit.gamma[:, :, order]
    fit.prevalence = fit.prevalence[:, order]
    return fit


def _order_statuses(fit: LTAFit) -> LTAFit:
    """Order statuses by overall unmet-need burden, lowest first."""
    return _permute(fit, np.argsort(fit.rho.sum(axis=0)))


def _align_to(fit: LTAFit, ref_rho: np.ndarray) -> LTAFit:
    """Relabel a bootstrap solution to match the point estimate's statuses.

    Two of the four statuses have almost the same total barrier load, so a rule
    that orders statuses by that load flips their labels in some replicates and
    produces confidence intervals that straddle both statuses. Matching each
    replicate's item-response profile to the point estimate's profiles, by the
    assignment that minimises total squared distance, removes that artefact.
    """
    from scipy.optimize import linear_sum_assignment

    cost = ((fit.rho[:, :, None] - ref_rho[:, None, :]) ** 2).sum(axis=0)
    _, order = linear_sum_assignment(cost.T)
    return _permute(fit, np.asarray(order))


def fit_lta(Y: np.ndarray, w: np.ndarray, K: int, n_starts: int = 60,
            seed: int = 0, homogeneous: bool = False, max_iter: int = 20000,
            tol: float = 1e-7, n_polish: int = 4, screen_iter: int = 150,
            verbose: bool = False) -> LTAFit:
    """Two-stage multiple-start fit; returns the best-likelihood solution."""
    rng = np.random.default_rng(seed)
    screened = []
    for s in range(n_starts):
        cand = fit_once(Y, w, K, rng, homogeneous=homogeneous,
                        max_iter=screen_iter, tol=1e-4)
        screened.append((cand.loglik, (cand.delta, cand.tau, cand.rho)))
        if verbose:
            print(f"  screen {s + 1:3d}/{n_starts}: ll = {cand.loglik:,.2f}")
    screened.sort(key=lambda x: -x[0])

    best = None
    for rank, (_, start) in enumerate(screened[:n_polish], start=1):
        cand = fit_once(Y, w, K, rng, homogeneous=homogeneous,
                        max_iter=max_iter, tol=tol, start=start)
        if best is None or cand.loglik > best.loglik + 1e-6:
            best = cand
        if verbose:
            print(f"  polish {rank}/{n_polish}: ll = {cand.loglik:,.3f} "
                  f"({cand.n_iter} iterations)")
    return _order_statuses(best)


# --------------------------------------------------------------------------- #
# Bootstrap
# --------------------------------------------------------------------------- #
def bootstrap(Y: np.ndarray, w: np.ndarray, fit: LTAFit, n_boot: int = 400,
              seed: int = 0, max_iter: int = 600, tol: float = 1e-6,
              verbose: bool = True) -> dict[str, np.ndarray]:
    """Non-parametric bootstrap over individuals, started from the point estimate.

    Each replicate's statuses are matched to the point estimate's statuses by
    their item-response profiles, which keeps the labels comparable across
    replicates.
    """
    rng = np.random.default_rng(seed)
    N = Y.shape[0]
    start = (fit.delta, fit.tau, fit.rho)
    draws = {"delta": [], "tau": [], "rho": [], "prev": []}
    for bidx in range(n_boot):
        idx = rng.integers(0, N, size=N)
        cand = _align_to(
            fit_once(Y[idx], w[idx], fit.K, rng, homogeneous=fit.homogeneous,
                     max_iter=max_iter, tol=tol, start=start), fit.rho)
        draws["delta"].append(cand.delta)
        draws["tau"].append(cand.tau)
        draws["rho"].append(cand.rho)
        draws["prev"].append(cand.prevalence)
        if verbose and (bidx + 1) % 25 == 0:
            print(f"  bootstrap {bidx + 1}/{n_boot}", flush=True)
    return {k: np.array(v) for k, v in draws.items()}


def ci(draws: np.ndarray, lo: float = 2.5, hi: float = 97.5):
    return np.percentile(draws, lo, axis=0), np.percentile(draws, hi, axis=0)
