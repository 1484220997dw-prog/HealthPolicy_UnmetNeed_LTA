"""Checks that the latent transition estimator does what it claims to do.

The model in src/khp_lta/lta.py is written here rather than taken from a
package, so a reviewer has no library reputation to rely on. These tests
simulate data from known parameters and check that the estimator recovers them,
that missing waves are handled by the likelihood rather than by dropping people,
and that a reloaded fit reproduces the stored solution exactly.

Run:  python -m pytest src/tests -q
  or: python src/tests/test_lta_recovery.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np

from khp_lta import lta

K, T, J, N = 3, 4, 4, 8000
DELTA = np.array([0.60, 0.25, 0.15])
TAU = np.stack([np.array([[0.85, 0.10, 0.05],
                          [0.30, 0.60, 0.10],
                          [0.20, 0.15, 0.65]])] * (T - 1))
RHO = np.array([[0.02, 0.55, 0.10],
                [0.03, 0.10, 0.60],
                [0.01, 0.50, 0.08],
                [0.02, 0.08, 0.55]])


def simulate(seed: int = 7):
    rng = np.random.default_rng(seed)
    S = np.empty((N, T), dtype=int)
    S[:, 0] = rng.choice(K, N, p=DELTA)
    for t in range(1, T):
        for k in range(K):
            m = S[:, t - 1] == k
            if m.any():
                S[m, t] = rng.choice(K, int(m.sum()), p=TAU[t - 1, k])
    Y = (rng.random((N, T, J)) < RHO.T[S]).astype(float)
    return Y, np.ones(N), S


def fit(Y, w):
    return lta.fit_lta(Y, w, K, n_starts=12, seed=1, screen_iter=200,
                       n_polish=2, max_iter=8000, tol=1e-7)


def test_recovers_known_parameters():
    Y, w, _ = simulate()
    f = fit(Y, w)
    assert np.abs(f.rho - RHO).max() < 0.05, f.rho
    assert np.abs(f.tau - TAU).max() < 0.08, f.tau
    assert np.abs(f.prevalence[0] - DELTA).max() < 0.05, f.prevalence[0]


def test_missing_waves_do_not_drop_people():
    """A person whose later waves are missing still contributes to the fit."""
    Y, w, _ = simulate()
    Y_missing = Y.copy()
    rng = np.random.default_rng(11)
    gone = rng.random(N) < 0.35
    Y_missing[gone, 2:, :] = np.nan
    f = fit(Y_missing, w)
    assert f.gamma.shape[0] == N, "individuals were dropped from the likelihood"
    assert np.isfinite(f.loglik)
    # the estimates should degrade, but not break
    assert np.abs(f.rho - RHO).max() < 0.08, f.rho


def test_reloading_a_fit_is_exact():
    """lta.evaluate must return the stored solution, not a nearby one."""
    Y, w, _ = simulate()
    f = fit(Y, w)
    again = lta.evaluate(Y, w, f.delta, f.tau, f.rho)
    assert np.allclose(again.gamma, f.gamma, atol=1e-12)
    assert abs(again.loglik - f.loglik) < 1e-8


def test_label_alignment_survives_relabelling():
    """A permuted solution is matched back to the reference ordering."""
    Y, w, _ = simulate()
    f = fit(Y, w)
    perm = np.array([2, 0, 1])
    shuffled = lta.evaluate(Y, w, f.delta[perm], f.tau[:, perm][:, :, perm],
                            f.rho[:, perm])
    aligned = lta._align_to(shuffled, f.rho)
    assert np.allclose(aligned.rho, f.rho, atol=1e-10)


def test_weights_change_the_estimates_in_the_expected_direction():
    """Up-weighting one latent group raises its estimated prevalence."""
    Y, w, S = simulate()
    heavy = np.where(S[:, 0] == 1, 5.0, 1.0)
    base = fit(Y, w)
    tilted = fit(Y, heavy)
    assert tilted.prevalence[0, 1] > base.prevalence[0, 1] + 0.05


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"{name}: ok")
    print("all checks passed")
