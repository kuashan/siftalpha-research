"""Frozen statistical primitives for XMA Falsification v2."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np
import pandas as pd
from scipy.stats import t as student_t
from scipy.stats import rankdata
import statsmodels.api as sm


@dataclass(frozen=True)
class BootstrapResult:
    estimate: float
    se: float
    ci_low: float
    ci_high: float
    p_value: float
    valid_replicates: int
    clusters: int


def cluster_bootstrap(
    frame: pd.DataFrame,
    cluster_col: str,
    estimator: Callable[[pd.DataFrame], float],
    seed: int,
    b: int = 10_000,
    direction: str = "two-sided",
    min_valid: int | None = None,
) -> BootstrapResult:
    clusters = pd.Index(frame[cluster_col].dropna().unique())
    k = len(clusters)
    if k < 2:
        raise ValueError("INSUFFICIENT SAMPLE: fewer than 2 clusters")

    t_obs = float(estimator(frame))
    rng = np.random.default_rng(seed)
    reps = []
    for _ in range(b):
        sampled = rng.choice(clusters.to_numpy(), size=k, replace=True)
        pieces = []
        for draw_id, cluster in enumerate(sampled):
            x = frame[frame[cluster_col] == cluster].copy()
            x["_bootstrap_draw"] = draw_id
            pieces.append(x)
        sample = pd.concat(pieces, ignore_index=True)
        try:
            value = float(estimator(sample))
        except Exception:
            continue
        if np.isfinite(value):
            reps.append(value)

    min_valid = b if min_valid is None else min_valid
    if len(reps) < min_valid:
        raise ValueError(f"INSUFFICIENT STATISTIC: {len(reps)}/{b} valid bootstrap estimates")

    reps_arr = np.asarray(reps, dtype=float)
    se = float(reps_arr.std(ddof=1))
    if not np.isfinite(se) or se <= 0:
        raise ValueError("INSUFFICIENT STATISTIC: non-positive bootstrap SE")

    t_obs_std = t_obs / se
    df = k - 1
    cdf = float(student_t.cdf(t_obs_std, df=df))
    if direction == "positive":
        p = 1.0 - cdf
    elif direction == "negative":
        p = cdf
    elif direction == "two-sided":
        p = 2.0 * min(cdf, 1.0 - cdf)
    else:
        raise ValueError("direction must be positive, negative, or two-sided")

    return BootstrapResult(
        estimate=t_obs,
        se=se,
        ci_low=float(np.quantile(reps_arr, 0.025)),
        ci_high=float(np.quantile(reps_arr, 0.975)),
        p_value=float(min(1.0, max(0.0, p))),
        valid_replicates=len(reps),
        clusters=k,
    )


def median_quantile_state_coefficient(
    frame: pd.DataFrame,
    outcome_col: str,
    down_col: str,
    spy_ret_col: str,
    atr_pct_col: str,
) -> float:
    y = frame[outcome_col].astype(float)
    x = frame[[down_col, spy_ret_col, atr_pct_col]].astype(float)
    x = sm.add_constant(x, has_constant="add")
    model = sm.QuantReg(y, x).fit(q=0.5, max_iter=10_000)
    return float(model.params[down_col])


def touch_probability_difference(frame: pd.DataFrame, group_col: str, touch_col: str) -> float:
    a = frame.loc[frame[group_col].astype(bool), touch_col].astype(float)
    b = frame.loc[~frame[group_col].astype(bool), touch_col].astype(float)
    if len(a) == 0 or len(b) == 0:
        raise ValueError("empty H3 arm")
    return float(a.mean() - b.mean())


def km_median_wait(times: np.ndarray, observed: np.ndarray, horizon: int = 20) -> float:
    """Minimal deterministic Kaplan-Meier median for integer waiting times."""
    times = np.asarray(times, dtype=int)
    observed = np.asarray(observed, dtype=bool)
    survival = 1.0
    for t in range(1, horizon + 1):
        at_risk = int(np.sum(times >= t))
        if at_risk == 0:
            break
        d = int(np.sum((times == t) & observed))
        survival *= (1.0 - d / at_risk)
        if survival <= 0.5:
            return float(t)
    raise ValueError("KM median not estimable by horizon")


def km_median_difference(
    frame: pd.DataFrame,
    extreme_col: str,
    time_col: str,
    observed_col: str,
    horizon: int = 20,
) -> float:
    ext = frame[frame[extreme_col].astype(bool)]
    neu = frame[~frame[extreme_col].astype(bool)]
    a = km_median_wait(ext[time_col].to_numpy(), ext[observed_col].to_numpy(), horizon)
    b = km_median_wait(neu[time_col].to_numpy(), neu[observed_col].to_numpy(), horizon)
    return float(a - b)


def residualize(y: np.ndarray, x: np.ndarray) -> np.ndarray:
    y = np.asarray(y, dtype=float)
    x = np.asarray(x, dtype=float)
    design = np.column_stack([np.ones(len(y)), x])
    if np.linalg.matrix_rank(design) < design.shape[1]:
        raise ValueError("CONTROL_MATRIX_RANK_DEFICIENT")
    beta, *_ = np.linalg.lstsq(design, y, rcond=None)
    return y - design @ beta


def rank_biserial_from_binary(group: np.ndarray, outcome: np.ndarray) -> float:
    g = np.asarray(group, dtype=bool)
    y = np.asarray(outcome, dtype=float)
    if g.all() or (~g).all():
        raise ValueError("both groups required")
    ranks = rankdata(y, method="average")
    n1, n0 = int(g.sum()), int((~g).sum())
    u = float(ranks[g].sum() - n1 * (n1 + 1) / 2.0)
    return float(2.0 * u / (n1 * n0) - 1.0)


def partial_spearman(x: np.ndarray, y: np.ndarray, controls: np.ndarray) -> float:
    rx = rankdata(np.asarray(x, dtype=float), method="average")
    ry = rankdata(np.asarray(y, dtype=float), method="average")
    ex = residualize(rx, controls)
    ey = residualize(ry, controls)
    if ex.std(ddof=1) == 0 or ey.std(ddof=1) == 0:
        raise ValueError("zero residual variance")
    return float(np.corrcoef(ex, ey)[0, 1])
