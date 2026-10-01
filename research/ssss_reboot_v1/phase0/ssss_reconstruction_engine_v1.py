#!/usr/bin/env python3
"""SSSS Reboot v1 canonical reconstruction engine.

No trading policy is implemented here.

Two modes are intentionally separated:

1) render_snapshot:
   Reproduces how the centered/repainting XMA formula renders a historical chart
   when evaluated with data available through one chosen as-of bar.

2) first_observed_ledger:
   Re-evaluates the formula independently at every historical bar t using only
   data <= t, then persists only the state/event visible at that time.

The distinction is mandatory for all later research.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import math


@dataclass(frozen=True)
class Bar:
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0


def ema(values: list[Optional[float]], period: int) -> list[Optional[float]]:
    alpha = 2.0 / (period + 1.0)
    out: list[Optional[float]] = [None] * len(values)
    prev: Optional[float] = None
    for i, value in enumerate(values):
        if value is None or not math.isfinite(value):
            continue
        prev = value if prev is None else alpha * value + (1.0 - alpha) * prev
        out[i] = prev
    return out


def canonical_weighted_20_210(values: list[float]) -> list[Optional[float]]:
    """Author-corrected 20..1 weighted series over lags 0..19."""
    out: list[Optional[float]] = [None] * len(values)
    for i in range(19, len(values)):
        total = 0.0
        for lag in range(20):
            total += (20 - lag) * values[i - lag]
        out[i] = total / 210.0
    return out


def xma_snapshot(values: list[float], asof: int, period: int) -> list[float]:
    """Centered/truncated XMA for the finite history [0..asof].

    Historical values near the right edge may revise when asof advances.
    """
    if period % 2 != 1:
        raise ValueError("SSSS reboot expects odd XMA periods")
    if asof < 0 or asof >= len(values):
        raise IndexError(asof)
    radius = (period - 1) // 2
    src = values[: asof + 1]
    pref = [0.0]
    total = 0.0
    for value in src:
        total += value
        pref.append(total)

    def mean(left: int, right: int) -> float:
        left = max(0, left)
        right = min(len(src) - 1, right)
        return (pref[right + 1] - pref[left]) / (right - left + 1)

    return [mean(i - radius, i + radius) for i in range(len(src))]


def double_xma_snapshot(values: list[float], asof: int, period: int) -> list[float]:
    inner = xma_snapshot(values, asof, period)
    return xma_snapshot(inner, asof, period)


def _cross(a: list[Optional[float]], b: list[Optional[float]], i: int) -> bool:
    if i <= 0 or a[i] is None or b[i] is None or a[i - 1] is None or b[i - 1] is None:
        return False
    return bool(a[i] > b[i] and a[i - 1] <= b[i - 1])


def _state(
    fast_lower: Optional[float],
    fast_upper: Optional[float],
    slow_lower: Optional[float],
    slow_upper: Optional[float],
) -> Optional[str]:
    if None in (fast_lower, fast_upper, slow_lower, slow_upper):
        return None
    assert fast_lower is not None and fast_upper is not None
    assert slow_lower is not None and slow_upper is not None
    if fast_lower >= slow_lower and fast_upper >= slow_upper:
        return "UP"
    if fast_upper <= slow_upper and fast_lower <= slow_lower:
        return "DOWN"
    if fast_lower >= slow_lower and fast_upper <= slow_upper:
        return "RANGE"
    return "EXPANSION"


def render_snapshot(bars: list[Bar], asof: Optional[int] = None) -> list[dict]:
    """Render formula history exactly as evaluated at one finite as-of bar."""
    if not bars:
        return []
    if asof is None:
        asof = len(bars) - 1
    bars = bars[: asof + 1]

    O = [x.open for x in bars]
    H = [x.high for x in bars]
    L = [x.low for x in bars]
    C = [x.close for x in bars]

    # Repainting centered XMA structures.
    vh25 = double_xma_snapshot(H, len(bars) - 1, 25)
    vl25 = double_xma_snapshot(L, len(bars) - 1, 25)
    vh60 = double_xma_snapshot(H, len(bars) - 1, 60 if False else 59)
    vl60 = double_xma_snapshot(L, len(bars) - 1, 60 if False else 59)

    # IMPORTANT:
    # The source formula specifies XMA(...,60). Public TDX-like references
    # normalize XMA to an odd centered window. Phase 0 keeps period-60 behavior
    # explicitly unresolved until Futu values are independently calibrated.
    # Therefore BS/BD below are left None rather than silently assuming period 59.

    wh = canonical_weighted_20_210(H)
    wl = canonical_weighted_20_210(L)
    d90h = ema(wh, 90)
    d90l = ema(wl, 90)

    e3 = ema([float(x) for x in C], 3)
    e6 = ema([float(x) for x in C], 6)
    e9 = ema([float(x) for x in C], 9)
    dea3 = ema([
        None if a is None or b is None else a - b
        for a, b in zip(e3, e6)
    ], 9)
    d39 = [
        None if a is None or b is None else a - b
        for a, b in zip(e3, e9)
    ]
    d39e3 = ema(d39, 3)
    d39e9 = ema(d39, 9)
    dea33 = ema([
        None if a is None or b is None else a - b
        for a, b in zip(d39e3, d39e9)
    ], 9)

    fast_lower: list[Optional[float]] = []
    fast_mid: list[Optional[float]] = []
    fast_upper: list[Optional[float]] = []
    slow_lower: list[Optional[float]] = []
    slow_upper: list[Optional[float]] = []

    for i in range(len(bars)):
        width25 = vh25[i] - vl25[i]
        fast_lower.append(vl25[i] - width25)  # ZD1
        fast_mid.append((vh25[i] + vl25[i]) / 2.0)  # GZB18
        fast_upper.append(vh25[i] + width25)  # ZK1

        if d90h[i] is None or d90l[i] is None:
            slow_lower.append(None)
            slow_upper.append(None)
        else:
            sw = d90h[i] - d90l[i]
            slow_lower.append(d90l[i] - 2.0 * sw)  # GZB9
            slow_upper.append(d90h[i] + 2.0 * sw)  # GZB8

    high_series: list[Optional[float]] = [float(x) for x in H]
    low_series: list[Optional[float]] = [float(x) for x in L]

    rows: list[dict] = []
    for i, bar in enumerate(bars):
        state = _state(fast_lower[i], fast_upper[i], slow_lower[i], slow_upper[i])

        lower_cross = _cross(fast_lower, low_series, i)  # CROSS(ZD1,L)
        upper_cross = _cross(high_series, fast_upper, i)  # CROSS(H,ZK1)

        isred: Optional[bool] = None
        rising = False
        falling = False
        if i > 0 and dea3[i] is not None and dea3[i - 1] is not None and dea33[i] is not None and dea33[i - 1] is not None:
            rising = bool(dea3[i - 1] < dea3[i] or dea33[i - 1] < dea33[i])
            falling = bool(dea3[i - 1] > dea3[i] or dea33[i - 1] > dea33[i])
            isred = rising

        width = fast_upper[i] - fast_lower[i]
        short_bottom = vl25[i] - 2.0 * (vh25[i] - vl25[i])
        short_top = vh25[i] + 2.0 * (vh25[i] - vl25[i])
        denom = short_top - short_bottom
        norm_o = (O[i] - short_bottom) / denom * 100000.0
        norm_h = (H[i] - short_bottom) / denom * 100000.0
        norm_l = (L[i] - short_bottom) / denom * 100000.0
        norm_c = (C[i] - short_bottom) / denom * 100000.0

        adkby_labels: list[str] = []
        if state == "UP" and lower_cross:
            adkby_labels.append("多")
        if state == "UP" and upper_cross:
            adkby_labels.append("平")
        if state == "DOWN" and upper_cross:
            adkby_labels.append("空")
        if state == "DOWN" and lower_cross:
            adkby_labels.append("平")
        if state == "RANGE" and lower_cross:
            adkby_labels.append("多")
        if state == "RANGE" and upper_cross:
            adkby_labels.append("空")

        buy_white = (norm_l < 20000.0 and norm_h > 20000.0) or norm_h < 20000.0
        sell_white = (norm_h > 80000.0 and norm_l < 80000.0) or norm_l > 80000.0
        warning = bool(isred is not None and C[i] > O[i] and not isred and sell_white)
        star = bool(isred is not None and C[i] < O[i] and isred and buy_white)

        rows.append({
            "date": bar.date,
            "ZD1": fast_lower[i],
            "MID": fast_mid[i],
            "ZK1": fast_upper[i],
            "slow_lower": slow_lower[i],
            "slow_upper": slow_upper[i],
            "state": state,
            "color": {
                "UP": "BLUE",
                "DOWN": "GREEN",
                "RANGE": "GRAY",
                "EXPANSION": "EXPANSION",
            }.get(state),
            "lower_cross": lower_cross,
            "upper_cross": upper_cross,
            "ssss_money_bag": lower_cross,
            "ssss_person": upper_cross,
            "momentum_rising": rising,
            "momentum_falling": falling,
            "adkby_isred": isred,
            "adkby_norm_open": norm_o,
            "adkby_norm_high": norm_h,
            "adkby_norm_low": norm_l,
            "adkby_norm_close": norm_c,
            "adkby_labels": adkby_labels,
            "adkby_warning": warning,
            "adkby_star": star,
            "BS": None,
            "BD": None,
        })
    return rows


def first_observed_ledger(bars: list[Bar]) -> list[dict]:
    """Persist only what was observable at each bar t using history <= t."""
    out: list[dict] = []
    for t in range(len(bars)):
        snapshot = render_snapshot(bars, asof=t)
        row = dict(snapshot[-1])
        row["asof_index"] = t
        row["mode"] = "FIRST_OBSERVED"
        out.append(row)
    return out
