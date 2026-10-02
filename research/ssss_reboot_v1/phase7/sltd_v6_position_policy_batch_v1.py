#!/usr/bin/env python3
"""SLTD V6 Position Policy Study v1.

Batch-oriented causal backtest for the official SLTD V6 15-rule taxonomy.

Important:
- XMA is reconstructed point-in-time (FIRST_OBSERVED).
- Signal at close t executes at next available open.
- This file does not modify the 15-rule taxonomy.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import itertools
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import yfinance as yf


ROOT = Path(__file__).resolve().parent
DATA_ROOT = ROOT / "data_snapshot"
BATCH_ROOT = ROOT / "batches"
LEDGER_ROOT = ROOT / "signal_ledgers"

FORMAL_START = pd.Timestamp("2020-01-02")
FORMAL_END = pd.Timestamp("2026-09-30")
FETCH_START = "2010-01-04"
FETCH_END_EXCLUSIVE = "2026-10-01"

BATCHES = {
    1: ["AAPL","MSFT","NVDA","AMD","AVGO","ORCL","INTC","QCOM","MU","GOOGL"],
    2: ["META","NFLX","AMZN","TSLA","HD","MCD","WMT","COST","PG","KO"],
    3: ["PEP","ABT","LLY","UNH","JNJ","TMO","JPM","BAC","GS","V"],
    4: ["MA","CAT","BA","GE","XOM","CVX","LIN","NEE","PLD"],
    5: ["IBM","CSCO","CRM","ADBE","TXN","DIS","NKE","SBUX","TGT","LOW"],
    6: ["MRK","PFE","ABBV","AMGN","GILD","C","MS","BLK","COP","UPS"],
    7: ["ACN","NOW","INTU","AMAT","LRCX","BKNG","TJX","CMG","ROST","MAR"],
    8: ["DHR","SYK","MDT","BMY","ISRG","SCHW","SPGI","DE","HON","RTX"],
}

INITIALS = (0.25, 0.40, 0.50, 0.60, 0.70, 1.00)
ADD_MODES = ("IGNORE", "ADD_25_TO_CAP", "ADD_ENTRY_TO_CAP", "TOPUP_TO_100")
SELL_REDUCTIONS = (0.25, 0.50, 0.75, 1.00)
WAIT_MODES = ("HOLD", "TRIM_25", "TRIM_50", "EXIT_100")
RESOLUTIONS = ("SELL_FIRST", "WAIT_FIRST", "NO_CHANGE_MIXED")

RULE_IDS = {
    "BUY_1":"BUY_BLUE_21P_LOWER",
    "BUY_2":"BUY_GRAY_4_10_LIGHT_SUPPORT",
    "BUY_3":"BUY_RECENT_BLUE_GRAY_LIGHT_SUPPORT",
    "BUY_4":"BLUE_11_20_LOWER_WICK_ONLY",
    "BUY_5":"NEW_V5_C_GRAY_4_10_LOWER_WICK_ONLY",
    "HOLD_1":"CONT_BLUE_11_20_UPPER",
    "HOLD_2":"CONT_BLUE_4_10_UPPER",
    "HOLD_3":"CONT_RECENT_GRAY_BLUE_UPPER",
    "HOLD_4":"NEW_V5_B_BLUE_21P_UPPER_CLOSE_ABOVE",
    "WAIT_1":"AVOID_GREEN_11_20_LOWER",
    "WAIT_2":"GREEN_11_20_LOWER_CLOSE_BELOW",
    "SELL_1":"SELL_RECENT_BLUE_GRAY_LIGHT_RESIST",
    "SELL_2":"GREEN_4_10_UPPER",
    "SELL_3":"NEW_V5_D_GREEN_11_20_UPPER_WICK_ONLY",
    "SELL_4":"NEW_V5_E_GREEN_11_20_LIGHT_RESIST",
}


@dataclass(frozen=True)
class Policy:
    initial: float
    add_mode: str
    sell_reduction: float
    wait_mode: str
    resolution: str

    @property
    def id(self) -> str:
        i = int(round(self.initial * 100))
        s = int(round(self.sell_reduction * 100))
        return f"I{i}_A{self.add_mode}_S{s}_W{self.wait_mode}_R{self.resolution}"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--batch", type=int, required=True, choices=range(1, 9))
    p.add_argument("--force-fetch", action="store_true")
    return p.parse_args()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def flatten_yf(frame: pd.DataFrame, ticker: str) -> pd.DataFrame:
    if isinstance(frame.columns, pd.MultiIndex):
        if ticker in frame.columns.get_level_values(0):
            frame = frame[ticker].copy()
        else:
            frame = frame.copy()
            frame.columns = frame.columns.get_level_values(-1)
    frame = frame.reset_index()
    date_col = "Date" if "Date" in frame.columns else frame.columns[0]
    frame = frame.rename(columns={date_col: "Date"})
    required = ["Date","Open","High","Low","Close","Volume"]
    missing = [c for c in required if c not in frame.columns]
    if missing:
        raise RuntimeError(f"{ticker}: missing columns {missing}")
    out = frame[required].copy()
    out["Date"] = pd.to_datetime(out["Date"], utc=True, errors="coerce").dt.tz_convert(None)
    for c in ["Open","High","Low","Close","Volume"]:
        out[c] = pd.to_numeric(out[c], errors="coerce")
    out = out.dropna(subset=["Date","Open","High","Low","Close"]).sort_values("Date")
    out = out.drop_duplicates("Date", keep="last")
    return out


def fetch_stock(ticker: str, path: Path, force: bool) -> pd.DataFrame:
    if path.exists() and not force:
        with gzip.open(path, "rt", encoding="utf-8") as f:
            return pd.read_csv(f, parse_dates=["Date"])
    frame = yf.download(
        ticker,
        start=FETCH_START,
        end=FETCH_END_EXCLUSIVE,
        interval="1d",
        auto_adjust=False,
        actions=False,
        repair=False,
        progress=False,
        threads=False,
        multi_level_index=True,
    )
    if frame is None or frame.empty:
        raise RuntimeError(f"{ticker}: no yfinance data")
    out = flatten_yf(frame, ticker)
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", encoding="utf-8", newline="") as f:
        out.to_csv(f, index=False)
    return out


def ema_optional(values: list[float | None], period: int) -> list[float | None]:
    alpha = 2.0 / (period + 1.0)
    out: list[float | None] = [None] * len(values)
    prev: float | None = None
    for i, value in enumerate(values):
        if value is None or not math.isfinite(value):
            continue
        prev = value if prev is None else alpha * value + (1.0 - alpha) * prev
        out[i] = prev
    return out


def weighted_20(values: np.ndarray) -> list[float | None]:
    weights = np.arange(20, 0, -1, dtype=float)
    out: list[float | None] = [None] * len(values)
    for i in range(19, len(values)):
        window = values[i-19:i+1][::-1]
        out[i] = float(np.dot(weights, window) / 210.0)
    return out


def double_xma_right(values: np.ndarray, t: int, period: int) -> float:
    """Exact right-edge value of XMA(XMA(values,n),n) at finite as-of t."""
    p = int((period - 2) / 2)
    outer_left = max(0, t - p - 1)
    prefix = np.concatenate(([0.0], np.cumsum(values[:t+1], dtype=float)))
    inners: list[float] = []
    for j in range(outer_left, t + 1):
        left = max(0, j - p - 1)
        right = min(t + 1, j + (period - p) - 1)
        if right <= left:
            raise RuntimeError("invalid XMA window")
        inners.append(float((prefix[right] - prefix[left]) / (right - left)))
    return float(sum(inners) / len(inners))


def age_bucket(age: int) -> str:
    if age <= 3:
        return "1_3"
    if age <= 10:
        return "4_10"
    if age <= 20:
        return "11_20"
    return "21_PLUS"


def build_ledger(frame: pd.DataFrame, symbol: str) -> list[dict]:
    dates = pd.to_datetime(frame["Date"]).tolist()
    O = frame["Open"].astype(float).to_numpy()
    H = frame["High"].astype(float).to_numpy()
    L = frame["Low"].astype(float).to_numpy()
    C = frame["Close"].astype(float).to_numpy()

    wh = weighted_20(H)
    wl = weighted_20(L)
    gzb3 = ema_optional(wh, 90)
    gzb4 = ema_optional(wl, 90)

    rows: list[dict] = []
    prev_state: str | None = None
    current_origin: str | None = None
    run_age = 0
    prev_support_contact = False
    prev_resist_contact = False

    for t in range(len(frame)):
        vl25 = double_xma_right(L, t, 25)
        vh25 = double_xma_right(H, t, 25)
        w25 = vh25 - vl25
        zd1 = vl25 - w25
        zk1 = vh25 + w25

        vl60 = double_xma_right(L, t, 60)
        vh60 = double_xma_right(H, t, 60)
        w60 = vh60 - vl60
        bs = vh60 + 2.2 * w60
        bd = vl60 - 2.8 * w60

        state = "OTHER"
        slow_top = gzb3[t]
        slow_bottom = gzb4[t]
        gzb8 = None
        gzb9 = None
        if slow_top is not None and slow_bottom is not None:
            sw = slow_top - slow_bottom
            gzb8 = slow_top + 2.0 * sw
            gzb9 = slow_bottom - 2.0 * sw
            if zd1 >= gzb9 and zk1 >= gzb8:
                state = "BLUE"
            elif zk1 <= gzb8 and zd1 <= gzb9:
                state = "GREEN"
            elif zd1 >= gzb9 and zk1 <= gzb8:
                state = "GRAY"
            else:
                state = "OTHER"

        if state == prev_state:
            run_age += 1
        else:
            current_origin = prev_state
            run_age = 1
        bucket = age_bucket(run_age)

        lower = False
        upper = False
        lower_subtype = None
        upper_subtype = None
        if t > 0 and rows:
            prev = rows[-1]
            lower = bool(L[t] < zd1 and not (L[t-1] < float(prev["ZD1"])))
            upper = bool(H[t] > zk1 and not (H[t-1] > float(prev["ZK1"])))
        if lower:
            if C[t] >= zd1:
                lower_subtype = "WICK_ONLY"
            elif H[t] >= zd1:
                lower_subtype = "CLOSE_BELOW"
            else:
                lower_subtype = "FULL_BELOW"
        if upper:
            if C[t] <= zk1:
                upper_subtype = "WICK_ONLY"
            elif L[t] <= zk1:
                upper_subtype = "CLOSE_ABOVE"
            else:
                upper_subtype = "FULL_ABOVE"

        support_contact = False
        resist_contact = False
        light_support = False
        light_resist = False
        if t > 0 and slow_top is not None and slow_bottom is not None:
            prev_top = gzb3[t-1]
            prev_bottom = gzb4[t-1]
            if prev_top is not None and prev_bottom is not None:
                intersects = H[t] >= slow_bottom and L[t] <= slow_top
                support_contact = bool(C[t-1] > prev_top and intersects)
                resist_contact = bool(C[t-1] < prev_bottom and intersects)
                light_support = support_contact and not prev_support_contact
                light_resist = resist_contact and not prev_resist_contact

        recent = current_origin in ("BLUE","GRAY","GREEN") and run_age <= 5
        transition = f"{current_origin}->{state}" if recent and current_origin != state else None

        actions: dict[str, list[str]] = {"BUY":[],"HOLD":[],"WAIT":[],"SELL":[]}
        if state == "BLUE" and run_age >= 21 and lower:
            actions["BUY"].append(RULE_IDS["BUY_1"])
        if state == "GRAY" and 4 <= run_age <= 10 and light_support:
            actions["BUY"].append(RULE_IDS["BUY_2"])
        if state == "GRAY" and current_origin == "BLUE" and run_age <= 5 and light_support:
            actions["BUY"].append(RULE_IDS["BUY_3"])
        if state == "BLUE" and 11 <= run_age <= 20 and lower and lower_subtype == "WICK_ONLY":
            actions["BUY"].append(RULE_IDS["BUY_4"])
        if state == "GRAY" and 4 <= run_age <= 10 and lower and lower_subtype == "WICK_ONLY":
            actions["BUY"].append(RULE_IDS["BUY_5"])

        if state == "BLUE" and 11 <= run_age <= 20 and upper:
            actions["HOLD"].append(RULE_IDS["HOLD_1"])
        if state == "BLUE" and 4 <= run_age <= 10 and upper:
            actions["HOLD"].append(RULE_IDS["HOLD_2"])
        if state == "BLUE" and current_origin == "GRAY" and run_age <= 5 and upper:
            actions["HOLD"].append(RULE_IDS["HOLD_3"])
        if state == "BLUE" and run_age >= 21 and upper and upper_subtype == "CLOSE_ABOVE":
            actions["HOLD"].append(RULE_IDS["HOLD_4"])

        if state == "GREEN" and 11 <= run_age <= 20 and lower:
            actions["WAIT"].append(RULE_IDS["WAIT_1"])
        if state == "GREEN" and 11 <= run_age <= 20 and lower and lower_subtype == "CLOSE_BELOW":
            actions["WAIT"].append(RULE_IDS["WAIT_2"])

        if state == "GRAY" and current_origin == "BLUE" and run_age <= 5 and light_resist:
            actions["SELL"].append(RULE_IDS["SELL_1"])
        if state == "GREEN" and 4 <= run_age <= 10 and upper:
            actions["SELL"].append(RULE_IDS["SELL_2"])
        if state == "GREEN" and 11 <= run_age <= 20 and upper and upper_subtype == "WICK_ONLY":
            actions["SELL"].append(RULE_IDS["SELL_3"])
        if state == "GREEN" and 11 <= run_age <= 20 and light_resist:
            actions["SELL"].append(RULE_IDS["SELL_4"])

        rows.append({
            "symbol": symbol,
            "date": dates[t].strftime("%Y-%m-%d"),
            "open": float(O[t]),
            "high": float(H[t]),
            "low": float(L[t]),
            "close": float(C[t]),
            "ZD1": zd1,
            "ZK1": zk1,
            "GZB3": slow_top,
            "GZB4": slow_bottom,
            "GZB8": gzb8,
            "GZB9": gzb9,
            "BS": bs,
            "BD": bd,
            "color": state,
            "run_age": run_age,
            "age": bucket,
            "origin": current_origin,
            "recent": recent,
            "transition": transition,
            "lower": lower,
            "lower_subtype": lower_subtype,
            "upper": upper,
            "upper_subtype": upper_subtype,
            "light_support": light_support,
            "light_resist": light_resist,
            "BUY": actions["BUY"],
            "HOLD": actions["HOLD"],
            "WAIT": actions["WAIT"],
            "SELL": actions["SELL"],
        })
        prev_state = state
        prev_support_contact = support_contact
        prev_resist_contact = resist_contact

    return rows


def action_classes(row: dict) -> tuple[str, ...]:
    return tuple(k for k in ("BUY","HOLD","WAIT","SELL") if row.get(k))


def resolve_action(classes: tuple[str, ...], resolution: str) -> str | None:
    if not classes:
        return None
    if len(classes) == 1:
        return classes[0]
    if resolution == "NO_CHANGE_MIXED":
        return None
    if resolution == "SELL_FIRST":
        order = ("SELL","WAIT","BUY","HOLD")
    elif resolution == "WAIT_FIRST":
        order = ("WAIT","SELL","BUY","HOLD")
    else:
        raise ValueError(resolution)
    for x in order:
        if x in classes:
            return x
    return None


def max_drawdown(curve: np.ndarray) -> float:
    peak = np.maximum.accumulate(curve)
    dd = curve / peak - 1.0
    return float(np.min(dd)) if len(dd) else 0.0


def cvar5(values: list[float]) -> float | None:
    if not values:
        return None
    a = np.asarray(values, dtype=float)
    cutoff = np.quantile(a, 0.05)
    tail = a[a <= cutoff]
    return float(np.mean(tail)) if len(tail) else float(cutoff)


def simulate_symbol(
    frame: pd.DataFrame,
    ledger: list[dict],
    policy: Policy,
    friction_bps: float,
) -> dict:
    dates = pd.to_datetime(frame["Date"]).dt.tz_localize(None)
    mask = (dates >= FORMAL_START) & (dates <= FORMAL_END)
    idx = np.flatnonzero(mask.to_numpy())
    if len(idx) < 2:
        raise RuntimeError("insufficient formal-window bars")

    ledger_by_date = {pd.Timestamp(x["date"]): x for x in ledger}
    cash = 1.0
    shares = 0.0
    turnover = 0.0
    changes = 0
    invested_days = 0
    equity_curve: list[float] = []
    curve_dates: list[str] = []
    cycle_start_equity: float | None = None
    cycle_start_date: pd.Timestamp | None = None
    trade_returns: list[float] = []
    holding_days: list[int] = []
    cost_rate = friction_bps / 10000.0

    for j, i in enumerate(idx):
        date = pd.Timestamp(dates.iloc[i])
        op = float(frame.iloc[i]["Open"])
        cl = float(frame.iloc[i]["Close"])
        pre_equity = cash + shares * op
        if pre_equity <= 0:
            raise RuntimeError("non-positive equity")

        if j > 0:
            prev_i = idx[j-1]
            prev_date = pd.Timestamp(dates.iloc[prev_i])
            signal = ledger_by_date.get(prev_date)
            classes = action_classes(signal) if signal else ()
            action = resolve_action(classes, policy.resolution)
        else:
            action = None

        position_value = shares * op
        current_fraction = position_value / pre_equity if pre_equity > 0 else 0.0
        order_value = 0.0

        if action == "BUY":
            if shares <= 1e-14:
                desired_fraction = policy.initial
            elif policy.add_mode == "IGNORE":
                desired_fraction = current_fraction
            elif policy.add_mode == "ADD_25_TO_CAP":
                desired_fraction = min(1.0, current_fraction + 0.25)
            elif policy.add_mode == "ADD_ENTRY_TO_CAP":
                desired_fraction = min(1.0, current_fraction + policy.initial)
            elif policy.add_mode == "TOPUP_TO_100":
                desired_fraction = 1.0
            else:
                raise ValueError(policy.add_mode)
            desired_fraction = max(current_fraction, desired_fraction)
            order_value = desired_fraction * pre_equity - position_value

        elif action == "SELL" and shares > 0:
            order_value = -position_value * policy.sell_reduction

        elif action == "WAIT" and shares > 0:
            trim = {"HOLD":0.0,"TRIM_25":0.25,"TRIM_50":0.50,"EXIT_100":1.0}[policy.wait_mode]
            order_value = -position_value * trim

        if abs(order_value) > 1e-14:
            max_buy = max(0.0, cash / (1.0 + cost_rate))
            if order_value > 0:
                order_value = min(order_value, max_buy)
            if order_value < 0:
                order_value = max(order_value, -position_value)
            cost = abs(order_value) * cost_rate
            shares += order_value / op
            cash -= order_value
            cash -= cost
            turnover += abs(order_value) / pre_equity
            changes += 1

            if cycle_start_equity is None and order_value > 0 and shares > 1e-14:
                cycle_start_equity = pre_equity
                cycle_start_date = date

            if shares <= 1e-12:
                shares = 0.0
                if cycle_start_equity is not None and cycle_start_equity > 0:
                    exit_equity = cash
                    trade_returns.append(exit_equity / cycle_start_equity - 1.0)
                    if cycle_start_date is not None:
                        holding_days.append((date - cycle_start_date).days)
                cycle_start_equity = None
                cycle_start_date = None

        close_equity = cash + shares * cl
        equity_curve.append(float(close_equity))
        curve_dates.append(date.strftime("%Y-%m-%d"))
        if shares > 1e-12:
            invested_days += 1

    final_equity = equity_curve[-1]
    if shares > 1e-12 and cycle_start_equity is not None:
        trade_returns.append(final_equity / cycle_start_equity - 1.0)
        if cycle_start_date is not None:
            holding_days.append((pd.Timestamp(curve_dates[-1]) - cycle_start_date).days)

    days = max(1, (pd.Timestamp(curve_dates[-1]) - pd.Timestamp(curve_dates[0])).days)
    total_return = final_equity - 1.0
    cagr = final_equity ** (365.25 / days) - 1.0 if final_equity > 0 else -1.0
    mdd = max_drawdown(np.asarray(equity_curve, dtype=float))
    calmar = cagr / abs(mdd) if mdd < -1e-12 else (999.0 if cagr > 0 else 0.0)
    wins = sum(1 for x in trade_returns if x > 0)

    return {
        "dates": curve_dates,
        "curve": equity_curve,
        "total_return": float(total_return),
        "cagr": float(cagr),
        "max_drawdown": float(mdd),
        "calmar": float(calmar),
        "turnover": float(turnover),
        "position_changes": int(changes),
        "time_in_market": float(invested_days / len(idx)),
        "trade_count": len(trade_returns),
        "win_rate": float(wins / len(trade_returns)) if trade_returns else None,
        "median_trade_return": float(np.median(trade_returns)) if trade_returns else None,
        "p5_trade_return": float(np.quantile(trade_returns, 0.05)) if trade_returns else None,
        "cvar5_trade_return": cvar5(trade_returns),
        "average_holding_days": float(np.mean(holding_days)) if holding_days else None,
    }


def portfolio_metrics(per_symbol: dict[str, dict]) -> dict:
    date_sets = [set(v["dates"]) for v in per_symbol.values()]
    common = sorted(set.intersection(*date_sets))
    if len(common) < 2:
        raise RuntimeError("no common portfolio dates")
    curves = []
    for v in per_symbol.values():
        mapping = dict(zip(v["dates"], v["curve"]))
        curves.append([mapping[d] for d in common])
    curve = np.mean(np.asarray(curves, dtype=float), axis=0)
    days = max(1, (pd.Timestamp(common[-1]) - pd.Timestamp(common[0])).days)
    total = float(curve[-1] - 1.0)
    cagr = float(curve[-1] ** (365.25 / days) - 1.0) if curve[-1] > 0 else -1.0
    mdd = max_drawdown(curve)
    calmar = cagr / abs(mdd) if mdd < -1e-12 else (999.0 if cagr > 0 else 0.0)
    return {
        "total_return": total,
        "cagr": cagr,
        "max_drawdown": float(mdd),
        "calmar": float(calmar),
        "turnover_mean": float(np.mean([v["turnover"] for v in per_symbol.values()])),
        "position_changes_sum": int(sum(v["position_changes"] for v in per_symbol.values())),
        "time_in_market_mean": float(np.mean([v["time_in_market"] for v in per_symbol.values()])),
    }


def policies() -> Iterable[Policy]:
    for values in itertools.product(INITIALS, ADD_MODES, SELL_REDUCTIONS, WAIT_MODES, RESOLUTIONS):
        yield Policy(*values)


def compact_symbol_metrics(v: dict) -> dict:
    return {k:v[k] for k in (
        "total_return","cagr","max_drawdown","calmar","turnover",
        "position_changes","time_in_market","trade_count","win_rate",
        "median_trade_return","p5_trade_return","cvar5_trade_return",
        "average_holding_days"
    )}


def fmt_pct(x: float | None) -> str:
    return "NA" if x is None else f"{100*x:.2f}%"


def fmt_num(x: float | None) -> str:
    return "NA" if x is None else f"{x:.3f}"


def main() -> None:
    args = parse_args()
    batch = args.batch
    symbols = BATCHES[batch]
    data_dir = DATA_ROOT / f"batch_{batch:02d}_stocks"
    data_dir.mkdir(parents=True, exist_ok=True)
    LEDGER_ROOT.mkdir(parents=True, exist_ok=True)
    BATCH_ROOT.mkdir(parents=True, exist_ok=True)

    frames: dict[str, pd.DataFrame] = {}
    ledgers: dict[str, list[dict]] = {}
    manifest = {
        "study":"SLTD_V6_POSITION_POLICY_STUDY_V1",
        "batch":batch,
        "asset_class":"STOCK",
        "symbols":symbols,
        "provider":"Yahoo Finance via yfinance",
        "auto_adjust":False,
        "repair":False,
        "fetch_start":FETCH_START,
        "fetch_end_exclusive":FETCH_END_EXCLUSIVE,
        "formal_start":FORMAL_START.strftime("%Y-%m-%d"),
        "formal_end":FORMAL_END.strftime("%Y-%m-%d"),
        "generated_at_utc":datetime.now(timezone.utc).isoformat(),
        "files":{},
    }

    for symbol in symbols:
        path = data_dir / f"{symbol}.csv.gz"
        frame = fetch_stock(symbol, path, args.force_fetch)
        if frame.empty:
            raise RuntimeError(f"{symbol}: empty frame")
        if frame["Date"].max() < FORMAL_END:
            raise RuntimeError(f"{symbol}: data ends before formal end: {frame['Date'].max()}")
        frames[symbol] = frame
        manifest["files"][symbol] = {
            "path":str(path.relative_to(ROOT)),
            "sha256":sha256_file(path),
            "rows":len(frame),
            "first":pd.Timestamp(frame["Date"].min()).strftime("%Y-%m-%d"),
            "last":pd.Timestamp(frame["Date"].max()).strftime("%Y-%m-%d"),
        }

        ledger = build_ledger(frame, symbol)
        ledgers[symbol] = ledger
        ledger_path = LEDGER_ROOT / f"BATCH_{batch:02d}_{symbol}_FIRST_OBSERVED.csv.gz"
        fieldnames = [
            "symbol","date","open","high","low","close","ZD1","ZK1","GZB3","GZB4",
            "GZB8","GZB9","BS","BD","color","run_age","age","origin","recent",
            "transition","lower","lower_subtype","upper","upper_subtype",
            "light_support","light_resist","BUY","HOLD","WAIT","SELL"
        ]
        with gzip.open(ledger_path, "wt", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for row in ledger:
                out = dict(row)
                for k in ("BUY","HOLD","WAIT","SELL"):
                    out[k] = "|".join(out[k])
                w.writerow(out)

    manifest_path = data_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

    all_results = []
    for policy in policies():
        per5 = {}
        per10 = {}
        for symbol in symbols:
            per5[symbol] = simulate_symbol(frames[symbol], ledgers[symbol], policy, 5.0)
            per10[symbol] = simulate_symbol(frames[symbol], ledgers[symbol], policy, 10.0)
        p5 = portfolio_metrics(per5)
        p10 = portfolio_metrics(per10)
        all_results.append({
            "policy_id":policy.id,
            "policy":{
                "initial":policy.initial,
                "add_mode":policy.add_mode,
                "sell_reduction":policy.sell_reduction,
                "wait_mode":policy.wait_mode,
                "resolution":policy.resolution,
            },
            "baseline_5bps":p5,
            "stress_10bps":p10,
        })

    all_results.sort(key=lambda x: (
        -x["baseline_5bps"]["calmar"],
        -x["baseline_5bps"]["cagr"],
        x["baseline_5bps"]["max_drawdown"],
        x["baseline_5bps"]["turnover_mean"],
        x["policy_id"],
    ))

    detailed = []
    for rank, item in enumerate(all_results[:20], start=1):
        p = item["policy"]
        policy = Policy(p["initial"],p["add_mode"],p["sell_reduction"],p["wait_mode"],p["resolution"])
        syms5 = {s:simulate_symbol(frames[s], ledgers[s], policy, 5.0) for s in symbols}
        detailed.append({
            "rank":rank,
            "policy_id":policy.id,
            "per_symbol_5bps":{s:compact_symbol_metrics(v) for s,v in syms5.items()},
        })

    event_counts = {}
    for symbol, ledger in ledgers.items():
        counts = {a:0 for a in ("BUY","HOLD","WAIT","SELL")}
        rule_counts = {rid:0 for rid in RULE_IDS.values()}
        for row in ledger:
            d = pd.Timestamp(row["date"])
            if d < FORMAL_START or d > FORMAL_END:
                continue
            for a in counts:
                if row[a]:
                    counts[a] += 1
                    for rid in row[a]:
                        rule_counts[rid] += 1
        event_counts[symbol] = {"action_class_bars":counts,"rule_hits":rule_counts}

    output = {
        "meta":{
            "study":"SLTD_V6_POSITION_POLICY_STUDY_V1",
            "status":"BATCH_COMPLETE",
            "batch":batch,
            "asset_class":"STOCK",
            "symbols":symbols,
            "formal_window":"2020-01-02..2026-09-30",
            "representation":"FIRST_OBSERVED",
            "execution":"CLOSE_CONFIRMED_NEXT_AVAILABLE_OPEN",
            "candidate_count":len(all_results),
            "friction_baseline_bps":5,
            "friction_stress_bps":10,
            "generated_at_utc":datetime.now(timezone.utc).isoformat(),
            "data_manifest":str(manifest_path.relative_to(ROOT)),
        },
        "event_counts":event_counts,
        "policies":all_results,
        "top20_detail":detailed,
    }
    json_path = BATCH_ROOT / f"BATCH_{batch:02d}_STOCK_POSITION_POLICY.json"
    json_path.write_text(json.dumps(output, indent=2), encoding="utf-8")

    lines = [
        f"# SLTD V6 Position Policy v1 — Stock Batch {batch}",
        "",
        "Status: **COMPLETE**",
        "",
        f"Symbols: {', '.join(symbols)}",
        "",
        "Window: 2020-01-02 through 2026-09-30",
        "",
        "Representation: FIRST_OBSERVED",
        "",
        "Execution: signal close -> next available open",
        "",
        f"Candidates evaluated: {len(all_results)}",
        "",
        "## Top 20 — 5 bps baseline",
        "",
        "| Rank | Policy | Calmar | CAGR | Max DD | Return | 10bps Calmar | Turnover |",
        "|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    for rank, item in enumerate(all_results[:20], start=1):
        b = item["baseline_5bps"]
        s = item["stress_10bps"]
        lines.append(
            f"| {rank} | `{item['policy_id']}` | {fmt_num(b['calmar'])} | "
            f"{fmt_pct(b['cagr'])} | {fmt_pct(b['max_drawdown'])} | "
            f"{fmt_pct(b['total_return'])} | {fmt_num(s['calmar'])} | "
            f"{b['turnover_mean']:.2f} |"
        )
    lines += [
        "",
        "## Batch rule",
        "",
        "This batch is recorded independently. No parameter is changed from its",
        "results before the next batch. Discovery ranking across Batches 1-4 is",
        "performed only after Batch 4 is complete.",
        "",
        f"`SLTD_V6_POSITION_POLICY_BATCH_{batch:02d} = COMPLETE`",
        "",
    ]
    md_path = BATCH_ROOT / f"BATCH_{batch:02d}_STOCK_POSITION_POLICY.md"
    md_path.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps({
        "batch":batch,
        "symbols":symbols,
        "candidate_count":len(all_results),
        "top_policy":all_results[0]["policy_id"],
        "top_5bps":all_results[0]["baseline_5bps"],
        "top_10bps":all_results[0]["stress_10bps"],
        "json":str(json_path),
        "md":str(md_path),
    }, indent=2))


if __name__ == "__main__":
    main()
