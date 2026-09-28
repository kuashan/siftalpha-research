"""Executable protocol mechanics for XMA Falsification v2.

Infrastructure/statistics primitives only.
No hypothesis outcome data are loaded here.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import ceil, sqrt
from typing import Iterable, Sequence

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class Episode:
    symbol: str
    arm: str
    anchor_idx: int
    anchor_date: pd.Timestamp
    last_qualifying_idx: int
    episode_id: str


def build_debounced_episodes(
    symbol: str,
    dates: Sequence[pd.Timestamp],
    qualifying: Sequence[bool],
    arm: Sequence[str],
    max_gap: int = 3,
) -> list[Episode]:
    """F2/F4/F5 episode rule.

    Successive qualifying bars with trading-index gap <= max_gap remain one
    episode. Different arm identity always starts a different episode stream.
    """
    by_arm: dict[str, list[tuple[int, pd.Timestamp]]] = {}
    for i, (d, q, a) in enumerate(zip(dates, qualifying, arm)):
        if q:
            by_arm.setdefault(str(a), []).append((i, pd.Timestamp(d)))

    out: list[Episode] = []
    for a, rows in sorted(by_arm.items()):
        start_i = last_i = None
        start_d = None
        seq = 0
        for i, d in rows:
            if start_i is None or i - last_i >= max_gap + 1:
                if start_i is not None:
                    seq += 1
                    out.append(Episode(symbol, a, start_i, start_d, last_i, f"{symbol}:{a}:{seq}"))
                start_i, start_d = i, d
            last_i = i
        if start_i is not None:
            seq += 1
            out.append(Episode(symbol, a, start_i, start_d, last_i, f"{symbol}:{a}:{seq}"))
    return sorted(out, key=lambda e: (e.anchor_date, e.symbol, e.arm))


def build_continuous_state_runs(
    symbol: str,
    dates: Sequence[pd.Timestamp],
    states: Sequence[str],
    allowed: tuple[str, ...] = ("UP_STATE", "DOWN_STATE"),
) -> list[Episode]:
    """F1 maximal consecutive state-run episodes."""
    out: list[Episode] = []
    cur_state = None
    start = None
    seq = 0
    for i, (d, s) in enumerate(zip(dates, states)):
        s = str(s)
        if s not in allowed:
            if cur_state is not None:
                seq += 1
                out.append(Episode(symbol, cur_state, start, pd.Timestamp(dates[start]), i-1, f"{symbol}:{cur_state}:{seq}"))
            cur_state, start = None, None
            continue
        if s != cur_state:
            if cur_state is not None:
                seq += 1
                out.append(Episode(symbol, cur_state, start, pd.Timestamp(dates[start]), i-1, f"{symbol}:{cur_state}:{seq}"))
            cur_state, start = s, i
    if cur_state is not None:
        seq += 1
        out.append(Episode(symbol, cur_state, start, pd.Timestamp(dates[start]), len(states)-1, f"{symbol}:{cur_state}:{seq}"))
    return out


def market_wave_ids(anchor_dates: Sequence[pd.Timestamp], max_gap_days: int = 2) -> np.ndarray:
    """Cluster sorted unique trading dates by <=2 observed trading-date steps.

    Input must already be market trading dates. Difference is measured in the
    ordinal position among unique anchor dates, not calendar days.
    """
    dates = [pd.Timestamp(x) for x in anchor_dates]
    unique = sorted(set(dates))
    pos = {d: i for i, d in enumerate(unique)}
    # Protocol links anchors separated by <=2 trading dates. Since only anchor
    # dates are supplied here, caller must pass a complete trading-calendar
    # ordinal when exact exchange-calendar distance is needed.
    # This helper therefore uses business-day distance as deterministic fallback.
    def bdist(a: pd.Timestamp, b: pd.Timestamp) -> int:
        return int(np.busday_count(a.date(), b.date()))

    wave_by_date = {}
    wave = 0
    prev = None
    for d in unique:
        if prev is None or bdist(prev, d) > max_gap_days:
            wave += 1
        wave_by_date[d] = wave
        prev = d
    return np.array([wave_by_date[d] for d in dates], dtype=int)


def design_effect_ess(values: Sequence[float], cluster_ids: Sequence[int]) -> dict:
    y = np.asarray(values, dtype=float)
    g = np.asarray(cluster_ids)
    mask = np.isfinite(y)
    y, g = y[mask], g[mask]
    n = len(y)
    groups = [y[g == k] for k in np.unique(g)]
    K = len(groups)
    if n < 2 or K < 2 or n <= K:
        return {"n": n, "K": K, "icc": np.nan, "deff": np.nan, "ess": np.nan}
    sizes = np.array([len(x) for x in groups], dtype=float)
    mbar = sizes.mean()
    cvm = sizes.std(ddof=1) / mbar if K > 1 and mbar > 0 else 0.0
    overall = y.mean()
    msb = sum(len(x) * (x.mean() - overall) ** 2 for x in groups) / (K - 1)
    msw = sum(((x - x.mean()) ** 2).sum() for x in groups) / (n - K)
    m0 = (n - (sizes**2).sum()/n) / (K - 1)
    denom = msb + (m0 - 1.0) * msw
    rho_raw = 0.0 if denom == 0 else (msb - msw) / denom
    rho = float(min(1.0, max(0.0, rho_raw)))
    deff = float(max(1.0, 1.0 + ((((1.0 + cvm**2) * mbar) - 1.0) * rho)))
    return {"n": n, "K": K, "icc": rho, "deff": deff, "ess": float(n/deff)}


def benjamini_hochberg(pvalues: Sequence[float]) -> np.ndarray:
    p = np.asarray(pvalues, dtype=float)
    if np.any((p < 0) | (p > 1) | ~np.isfinite(p)):
        raise ValueError("pvalues must be finite in [0,1]")
    m = len(p)
    order = np.argsort(p)
    ranked = p[order]
    q = ranked * m / np.arange(1, m + 1)
    q = np.minimum.accumulate(q[::-1])[::-1]
    q = np.minimum(q, 1.0)
    out = np.empty_like(q)
    out[order] = q
    return out


def standardized_euclidean_distances(event: pd.Series, controls: pd.DataFrame, cols: Sequence[str]) -> pd.Series:
    pool = controls[list(cols)].astype(float)
    mu = pool.mean()
    sd = pool.std(ddof=1)
    if (sd <= 0).any() or sd.isna().any():
        raise ValueError("zero/nonfinite matching-pool std")
    ze = (event[list(cols)].astype(float) - mu) / sd
    zc = (pool - mu) / sd
    return np.sqrt(((zc - ze) ** 2).sum(axis=1))


def select_nearest_controls(event: pd.Series, controls: pd.DataFrame, cols: Sequence[str], n: int = 5) -> pd.DataFrame:
    if len(controls) < n:
        raise ValueError("UNMATCHABLE: fewer than required controls")
    tmp = controls.copy()
    tmp["_distance"] = standardized_euclidean_distances(event, tmp, cols)
    tmp = tmp.sort_values(["_distance", "date", "symbol"], kind="mergesort")
    return tmp.head(n).copy()


def pair_f5_a_to_b(a: pd.DataFrame, b: pd.DataFrame) -> pd.DataFrame:
    """Deterministic same-symbol, same-quarter, one-use B pairing."""
    a = a.copy().sort_values(["date", "symbol", "event_id"], kind="mergesort")
    b = b.copy()
    used: set[str] = set()
    pairs = []
    for _, ar in a.iterrows():
        ad = pd.Timestamp(ar["date"])
        q = ad.to_period("Q")
        cand = b[
            (b["symbol"] == ar["symbol"]) &
            (pd.to_datetime(b["date"]).dt.to_period("Q") == q) &
            (~b["event_id"].isin(used))
        ].copy()
        if cand.empty:
            pairs.append({"a_event_id": ar["event_id"], "b_event_id": None, "status": "UNMATCHABLE_FOR_DID"})
            continue
        cand["_dist"] = (pd.to_datetime(cand["date"]) - ad).abs().dt.days
        cand = cand.sort_values(["_dist", "date", "event_id"], kind="mergesort")
        br = cand.iloc[0]
        used.add(str(br["event_id"]))
        pairs.append({"a_event_id": ar["event_id"], "b_event_id": br["event_id"], "status": "MATCHED"})
    return pd.DataFrame(pairs)


def guard_pass(effect: float, mde_abs: float, sample_ok: bool) -> str:
    if not sample_ok:
        return "INSUFFICIENT"
    return "PASS" if abs(float(effect)) < float(mde_abs) else "FAIL"
