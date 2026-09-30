#!/usr/bin/env python3
"""Strict FEB_XMA_v1 historical replay.

Reads <SYMBOL>.csv files with Date/Open/High/Low/Close/Volume columns.
Implements the frozen legacy raw Source-XMA/ADKBY-E mechanics, including
point-in-time first-observed XMA, readiness gating, next-open execution,
and the historical FEB target-accounting convention.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Optional

TRADING_DAYS = 252
INITIAL_CAPITAL = 10_000.0
SLIPPAGE = 0.0005


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


def prefix(values: list[float]) -> list[float]:
    out = [0.0]
    total = 0.0
    for value in values:
        total += value
        out.append(total)
    return out


def range_mean(pref: list[float], left: int, right: int) -> float:
    left = max(0, left)
    right = min(len(pref) - 2, right)
    return (pref[right + 1] - pref[left]) / (right - left + 1)


def point_in_time_double_xma_endpoint(values: list[float], asof: int, period: int = 25) -> float:
    # Source behavior verified against ABT January: centered/truncated XMA.
    # For N=25, radius=12. At the right edge, future samples do not exist.
    radius = (period - 1) // 2
    pref = prefix(values)
    inner = []
    for j in range(max(0, asof - radius), asof + 1):
        inner.append(range_mean(pref, j - radius, min(j + radius, asof)))
    return sum(inner) / len(inner)


def raw_weighted(values: list[float], i: int) -> Optional[float]:
    # Historical raw ADKBY-E: lag 19 and lag 20 are both present, denominator 210.
    if i < 20:
        return None
    total = 0.0
    for k in range(0, 19):  # lag 0..18, weights 20..2
        total += (20 - k) * values[i - k]
    total += values[i - 19]
    total += values[i - 20]
    return total / 210.0


def sample_sharpe(equity: list[float]) -> Optional[float]:
    rets = []
    for a, b in zip(equity, equity[1:]):
        if a > 0:
            rets.append(b / a - 1.0)
    if len(rets) < 2:
        return None
    sd = statistics.stdev(rets)
    if sd == 0:
        return None
    return statistics.mean(rets) / sd * math.sqrt(TRADING_DAYS)


def max_drawdown(equity: list[float]) -> float:
    peak = equity[0]
    worst = 0.0
    for value in equity:
        peak = max(peak, value)
        worst = min(worst, value / peak - 1.0)
    return worst


def annual_returns(dates: list[str], equity: list[float], initial: float) -> dict[str, float]:
    year_end: dict[str, float] = {}
    for d, e in zip(dates, equity):
        year_end[d[:4]] = e
    out: dict[str, float] = {}
    prev = initial
    for y in sorted(year_end):
        out[y] = year_end[y] / prev - 1.0
        prev = year_end[y]
    return out


def cagr(start: str, end: str, initial: float, final: float) -> float:
    days = (date.fromisoformat(end) - date.fromisoformat(start)).days
    years = days / 365.25
    return (final / initial) ** (1.0 / years) - 1.0


@dataclass
class Row:
    d: str
    o: float
    h: float
    l: float
    c: float
    v: float


def load_rows(path: Path, start: str, end: str) -> list[Row]:
    rows: list[Row] = []
    with path.open(newline="", encoding="utf-8") as f:
        for item in csv.DictReader(f):
            d = item["Date"]
            if d < start or d > end:
                continue
            rows.append(Row(
                d=d,
                o=float(item["Open"]),
                h=float(item["High"]),
                l=float(item["Low"]),
                c=float(item["Close"]),
                v=float(item["Volume"]),
            ))
    if not rows:
        raise ValueError(f"no rows in requested window: {path}")
    return rows


def build_features(rows: list[Row]) -> list[dict]:
    n = len(rows)
    H = [r.h for r in rows]
    L = [r.l for r in rows]
    C = [r.c for r in rows]
    V = [r.v for r in rows]

    e3 = ema(C, 3)
    e6 = ema(C, 6)
    e9 = ema(C, 9)
    dea3 = ema([a - b if a is not None and b is not None else None for a, b in zip(e3, e6)], 9)
    d39 = [a - b if a is not None and b is not None else None for a, b in zip(e3, e9)]
    d39e3 = ema(d39, 3)
    d39e9 = ema(d39, 9)
    dea33 = ema([a - b if a is not None and b is not None else None for a, b in zip(d39e3, d39e9)], 9)

    wh = [raw_weighted(H, i) for i in range(n)]
    wl = [raw_weighted(L, i) for i in range(n)]
    d90h = ema(wh, 90)
    d90l = ema(wl, 90)

    feats: list[dict] = []
    for i, row in enumerate(rows):
        vh = point_in_time_double_xma_endpoint(H, i, 25)
        vl = point_in_time_double_xma_endpoint(L, i, 25)
        width = vh - vl
        fast_lower = vl - width
        fast_upper = vh + width
        fast_mid = (vh + vl) / 2.0

        regime = None
        slow_upper = None
        slow_lower = None
        if d90h[i] is not None and d90l[i] is not None:
            slow_width = d90h[i] - d90l[i]
            slow_upper = d90h[i] + 2.0 * slow_width
            slow_lower = d90l[i] - 2.0 * slow_width
            if fast_lower >= slow_lower and fast_upper >= slow_upper:
                regime = "BULL"
            elif fast_upper <= slow_upper and fast_lower <= slow_lower:
                regime = "BEAR"
            elif fast_lower >= slow_lower and fast_upper <= slow_upper:
                regime = "RANGE"
            else:
                regime = "EXPANSION"

        fd = None if i == 0 or dea3[i] is None or dea3[i-1] is None else dea3[i] - dea3[i-1]
        sd = None if i == 0 or dea33[i] is None or dea33[i-1] is None else dea33[i] - dea33[i-1]
        momentum = None
        if fd is not None and sd is not None:
            if fd > 0 and sd > 0:
                momentum = "BOTH_UP"
            elif fd < 0 and sd < 0:
                momentum = "BOTH_DOWN"
            else:
                momentum = "CONFLICT"

        rvol20 = None
        if i >= 19:
            rvol20 = V[i] / (sum(V[i-19:i+1]) / 20.0)

        denom = fast_upper - fast_lower
        pos_l = None if denom <= 0 else (row.l - fast_lower) / denom * 100000.0
        pos_c = None if denom <= 0 else (row.c - fast_lower) / denom * 100000.0
        ready = (
            regime is not None and fd is not None and sd is not None and
            pos_l is not None and pos_c is not None
        )
        feats.append({
            "fast_lower": fast_lower,
            "fast_mid": fast_mid,
            "fast_upper": fast_upper,
            "slow_lower": slow_lower,
            "slow_upper": slow_upper,
            "regime": regime,
            "fast_delta": fd,
            "slow_delta": sd,
            "momentum": momentum,
            "rvol20": rvol20,
            "pos_l": pos_l,
            "pos_c": pos_c,
            "sum_delta": None if fd is None or sd is None else fd + sd,
            "ready": ready,
        })
    return feats


def replay_symbol(symbol: str, rows: list[Row]) -> dict:
    feats = build_features(rows)
    cash = INITIAL_CAPITAL
    shares = 0.0
    target = 0.0
    pending: Optional[dict] = None
    watch_end = -1
    counts = {"probe": 0, "confirm": 0, "breakout": 0, "add": 0, "reduce": 0, "exit": 0}
    events = []
    equity = []
    target_exposure = []
    gross_exposure = []

    def execute(i: int, action: str, new_target: float, signal_date: str) -> None:
        nonlocal cash, shares, target
        old = target
        open_px = rows[i].o
        if new_target > old:
            notional = (new_target - old) * INITIAL_CAPITAL
            px = open_px * (1.0 + SLIPPAGE)
            delta_shares = notional / px
            cash -= notional
            shares += delta_shares
        elif new_target < old:
            px = open_px * (1.0 - SLIPPAGE)
            if new_target <= 0.0:
                delta_shares = -shares
            else:
                sell_fraction = (old - new_target) / old
                delta_shares = -(shares * sell_fraction)
            cash += (-delta_shares) * px
            shares += delta_shares
        else:
            return
        target = new_target
        counts[action] += 1
        events.append({
            "signal_date": signal_date,
            "execution_date": rows[i].d,
            "action": action,
            "old_target": old,
            "new_target": new_target,
            "raw_open": open_px,
            "shares_after": shares,
            "cash_after": cash,
        })

    for i, row in enumerate(rows):
        if pending is not None:
            execute(i, pending["action"], pending["target"], pending["signal_date"])
            pending = None

        eq = cash + shares * row.c
        equity.append(eq)
        target_exposure.append(target)
        gross_exposure.append(0.0 if eq == 0 else shares * row.c / eq)

        if i == len(rows) - 1:
            break

        if i > watch_end:
            watch_end = -1

        f = feats[i]
        if not f["ready"]:
            continue

        action = None
        new_target = target

        if target <= 0.0:
            probe = f["regime"] != "BEAR" and f["pos_l"] < 20000.0
            breakout = (
                f["regime"] != "BEAR" and
                row.c > f["fast_upper"] and
                f["momentum"] == "BOTH_UP" and
                f["rvol20"] is not None and f["rvol20"] >= 1.50
            )
            if probe:
                action = "probe"
                new_target = 0.25
                watch_end = i + 3
            elif breakout:
                action = "breakout"
                new_target = 0.70
        else:
            hard_exit = (
                f["regime"] == "BEAR" or
                (row.c < f["fast_mid"] and f["momentum"] != "BOTH_UP") or
                (f["slow_delta"] < 0 and f["pos_c"] > 80000.0)
            )
            prev_sum = feats[i-1]["sum_delta"] if i > 0 else None
            reduce = (
                f["pos_c"] > 120000.0 and
                prev_sum is not None and
                f["sum_delta"] is not None and
                f["sum_delta"] < prev_sum
            )
            add = (
                row.c > f["fast_upper"] and
                f["momentum"] == "BOTH_UP" and
                f["rvol20"] is not None and f["rvol20"] >= 1.50 and
                target < 1.0
            )
            confirm = (
                watch_end >= i and
                row.c > f["fast_mid"] and
                f["momentum"] == "BOTH_UP" and
                target < 0.65
            )
            if hard_exit:
                action = "exit"
                new_target = 0.0
                watch_end = -1
            elif reduce:
                candidate = max(0.40, target - 0.30)
                if candidate < target:
                    action = "reduce"
                    new_target = candidate
            elif add:
                action = "add"
                new_target = 1.0
            elif confirm:
                action = "confirm"
                new_target = 0.65

        if action is not None and abs(new_target - target) > 1e-12:
            pending = {"action": action, "target": new_target, "signal_date": row.d}

    terminal_liquidation = 0
    if shares > 0.0:
        px = rows[-1].c * (1.0 - SLIPPAGE)
        cash += shares * px
        shares = 0.0
        target = 0.0
        terminal_liquidation = 1
        equity[-1] = cash
        target_exposure[-1] = 0.0
        gross_exposure[-1] = 0.0

    final = equity[-1]
    result = {
        "symbol": symbol,
        "start": rows[0].d,
        "end": rows[-1].d,
        "initial_capital": INITIAL_CAPITAL,
        "final_capital": final,
        "total_return": final / INITIAL_CAPITAL - 1.0,
        "cagr": cagr(rows[0].d, rows[-1].d, INITIAL_CAPITAL, final),
        "max_drawdown": max_drawdown(equity),
        "sharpe_annualized": sample_sharpe(equity),
        "average_target_exposure": statistics.mean(target_exposure),
        "average_gross_exposure": statistics.mean(gross_exposure),
        "counts": counts,
        "terminal_liquidation": terminal_liquidation,
        "executions": sum(counts.values()) + terminal_liquidation,
        "annual_returns": annual_returns([r.d for r in rows], equity, INITIAL_CAPITAL),
        "equity": [[r.d, e] for r, e in zip(rows, equity)],
        "events": events,
    }
    return result


def aggregate(results: list[dict]) -> dict:
    if not results:
        raise ValueError("no symbol results")
    dates = [d for d, _ in results[0]["equity"]]
    for r in results[1:]:
        if [d for d, _ in r["equity"]] != dates:
            raise ValueError("date alignment differs across symbols")
    aggregate_equity = []
    for i, d in enumerate(dates):
        aggregate_equity.append(sum(r["equity"][i][1] for r in results))
    initial = INITIAL_CAPITAL * len(results)
    final = aggregate_equity[-1]
    sleeve_returns = [r["total_return"] for r in results]
    return {
        "symbols": len(results),
        "initial_capital": initial,
        "final_capital": final,
        "total_return": final / initial - 1.0,
        "cagr": cagr(dates[0], dates[-1], initial, final),
        "max_drawdown": max_drawdown(aggregate_equity),
        "sharpe_annualized": sample_sharpe(aggregate_equity),
        "mean_sleeve_return": statistics.mean(sleeve_returns),
        "median_sleeve_return": statistics.median(sleeve_returns),
        "positive_symbols": sum(x > 0 for x in sleeve_returns),
        "annual_returns": annual_returns(dates, aggregate_equity, initial),
        "equity": [[d, e] for d, e in zip(dates, aggregate_equity)],
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True, type=Path)
    ap.add_argument("--symbols", required=True, help="comma-separated symbols")
    ap.add_argument("--start", default="2020-01-02")
    ap.add_argument("--end", default="2025-12-30")
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()

    symbols = [s.strip().upper() for s in args.symbols.split(",") if s.strip()]
    results = []
    for symbol in symbols:
        rows = load_rows(args.data_dir / f"{symbol}.csv", args.start, args.end)
        results.append(replay_symbol(symbol, rows))

    payload = {
        "schema": 1,
        "strategy": "FEB_XMA_v1_STRICT_REPLAY",
        "window": {"start": args.start, "end": args.end},
        "per_symbol": {r["symbol"]: r for r in results},
        "aggregate": aggregate(results),
    }
    args.out.write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
