#!/usr/bin/env python3
"""Pure SLTD V8 probability-map candidate R2 on fresh 20 US stocks."""
from __future__ import annotations

import hashlib
import json
import math
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
PROJECT = REPO / "integrations" / "sltd_v7_siftalpha_v1"
sys.path.insert(0, str(PROJECT))
import strategy as sltd  # noqa: E402

FORMAL_START = pd.Timestamp("2020-01-02")
FORMAL_END = pd.Timestamp("2026-09-30")
FETCH_START = "2010-01-04"
FETCH_END_EXCLUSIVE = "2026-10-01"

UNIVERSE = [
    ("AXP", "Financial"), ("PGR", "Financial"), ("CB", "Financial"), ("ICE", "Financial"),
    ("T", "Communication"), ("TMUS", "Communication"), ("CMCSA", "Communication"),
    ("CL", "ConsumerStaples"), ("MDLZ", "ConsumerStaples"), ("GIS", "ConsumerStaples"),
    ("MMM", "Industrials"), ("FDX", "Industrials"), ("EMR", "Industrials"),
    ("DUK", "Utilities"), ("D", "Utilities"), ("EXC", "Utilities"),
    ("SLB", "Energy"), ("EOG", "Energy"),
    ("F", "Auto"), ("GM", "Auto"),
]
SYMBOLS = [x[0] for x in UNIVERSE]

DATA_DIR = ROOT / "fresh20_probability_map_data"
MANIFEST = DATA_DIR / "manifest.json"
OUT_JSON = ROOT / "PURE_SLTD_V8_PROBABILITY_MAP_R2_RESULT_v1.json"
OUT_MD = ROOT / "PURE_SLTD_V8_PROBABILITY_MAP_R2_RESULT_v1.md"

PM_BUY_ID = "PM_BUY_1_GREEN_21P_LOWER_CLOSE_BELOW"
PM_SELL_ID = "PM_SELL_1_BLUE_21P_UPPER_WICK_ONLY"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def flatten_yf(frame: pd.DataFrame, ticker: str) -> pd.DataFrame:
    if isinstance(frame.columns, pd.MultiIndex):
        frame = frame.copy()
        for level in range(frame.columns.nlevels):
            vals = {str(x) for x in frame.columns.get_level_values(level)}
            if ticker in vals:
                frame = frame.xs(ticker, axis=1, level=level, drop_level=True)
                break
        if isinstance(frame.columns, pd.MultiIndex):
            frame.columns = frame.columns.get_level_values(0)
    frame = frame.reset_index()
    date_col = "Date" if "Date" in frame.columns else frame.columns[0]
    frame = frame.rename(columns={date_col: "Date"})
    req = ["Date", "Open", "High", "Low", "Close", "Volume"]
    missing = [c for c in req if c not in frame.columns]
    if missing:
        raise RuntimeError(f"{ticker}: missing columns {missing}")
    out = frame[req].copy()
    out["Date"] = pd.to_datetime(out["Date"], utc=True, errors="coerce").dt.tz_convert(None)
    for c in req[1:]:
        out[c] = pd.to_numeric(out[c], errors="coerce")
    out = out.dropna(subset=["Date", "Open", "High", "Low", "Close"]).sort_values("Date")
    return out.drop_duplicates("Date", keep="last").reset_index(drop=True)


def fetch_stock(ticker: str) -> pd.DataFrame:
    path = DATA_DIR / f"{ticker}.csv.gz"
    if path.exists():
        return pd.read_csv(path, parse_dates=["Date"])
    last = None
    for attempt in range(4):
        try:
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
            if frame is not None and not frame.empty:
                out = flatten_yf(frame, ticker)
                DATA_DIR.mkdir(parents=True, exist_ok=True)
                out.to_csv(path, index=False, compression="gzip")
                return out
            last = RuntimeError("empty download")
        except Exception as exc:
            last = exc
        time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"{ticker}: download failed: {last}")


def candles_from_frame(frame: pd.DataFrame) -> list[dict]:
    return [
        {
            "date": pd.Timestamp(r.Date).strftime("%Y-%m-%d"),
            "open": float(r.Open),
            "high": float(r.High),
            "low": float(r.Low),
            "close": float(r.Close),
            "volume": 0.0 if pd.isna(r.Volume) else float(r.Volume),
        }
        for r in frame.itertuples(index=False)
    ]


def pm_buy(row: dict | None) -> bool:
    return bool(
        row
        and str(row.get("color") or "").upper() == "GREEN"
        and int(row.get("run_age") or 0) >= 21
        and bool(row.get("lower"))
        and str(row.get("lower_subtype") or "").upper() == "CLOSE_BELOW"
    )


def pm_sell(row: dict | None) -> bool:
    return bool(
        row
        and str(row.get("color") or "").upper() == "BLUE"
        and int(row.get("run_age") or 0) >= 21
        and bool(row.get("upper"))
        and str(row.get("upper_subtype") or "").upper() == "WICK_ONLY"
    )


def resolve_candidate_action(row: dict | None, enabled: bool) -> tuple[str | None, list[str]]:
    if not row:
        return None, []
    classes = set(sltd.action_classes(row))
    extras = []
    if enabled and pm_buy(row):
        classes.add("BUY")
        extras.append(PM_BUY_ID)
    if enabled and pm_sell(row):
        classes.add("SELL")
        extras.append(PM_SELL_ID)
    if len(classes) != 1:
        return None, extras
    return next(iter(classes)), extras


def max_drawdown(curve: np.ndarray) -> float:
    peak = np.maximum.accumulate(curve)
    return float(np.min(curve / peak - 1.0))


def simulate_sltd(
    bars: list[dict],
    ledger: list[dict],
    friction_bps: float,
    candidate_enabled: bool,
) -> dict:
    formal_index = next((i for i, b in enumerate(bars) if b["date"] >= sltd.POLICY_START_DATE), 0)
    warmup_index = min(sltd.MIN_WARMUP_BARS, len(bars) - 1)
    start = max(formal_index, warmup_index)
    end = max(i for i, b in enumerate(bars) if b["date"] <= FORMAL_END.strftime("%Y-%m-%d"))
    if end <= start:
        raise RuntimeError("insufficient formal window")

    cash = 1.0
    shares = 0.0
    armed = False
    cost_rate = friction_bps / 10000.0
    curve = []
    dates = []
    changes = 0
    turnover = 0.0
    hard_exits = 0
    buy_exec = 0
    sell_exec = 0
    pm_buy_exec = 0
    pm_sell_exec = 0
    invested = 0

    for j in range(start, end + 1):
        bar = bars[j]
        op = float(bar["open"])
        cl = float(bar["close"])
        pre = cash + shares * op
        pos = shares * op
        frac = pos / pre if pre > 0 else 0.0
        signal = ledger[j - 1] if j > start else None

        hard = bool(shares > 1e-14 and armed and sltd.c2_condition(signal))
        action, extras = resolve_candidate_action(signal, candidate_enabled)
        ordinary = None
        order = 0.0
        side = None

        if hard:
            order = -pos
            side = "X"
        else:
            ordinary = action
            if action == "BUY":
                target = 0.25 if shares <= 1e-14 else min(1.0, frac + 0.25)
                target = max(frac, target)
                order = target * pre - pos
                side = "B"
            elif action == "SELL" and shares > 0:
                order = -pos * 0.25
                side = "S"

        if order > 1e-14:
            order = min(order, max(0.0, cash / (1.0 + cost_rate)))
        elif order < -1e-14:
            order = max(order, -pos)

        executed = abs(order) > 1e-14
        if executed:
            cost = abs(order) * cost_rate
            shares += order / op
            cash -= order + cost
            if shares <= 1e-12:
                shares = 0.0
            changes += 1
            turnover += abs(order) / pre
            if side == "B":
                buy_exec += 1
                if PM_BUY_ID in extras:
                    pm_buy_exec += 1
            elif side == "S":
                sell_exec += 1
                if PM_SELL_ID in extras:
                    pm_sell_exec += 1
            elif side == "X":
                hard_exits += 1

        if hard and executed:
            armed = False
        elif executed and ordinary == "SELL" and order < 0:
            armed = True
        elif executed and ordinary == "BUY" and order > 0:
            armed = False

        eq = cash + shares * cl
        curve.append(eq)
        dates.append(bar["date"])
        if shares > 1e-12:
            invested += 1

    arr = np.asarray(curve, dtype=float)
    days = max(1, (pd.Timestamp(dates[-1]) - pd.Timestamp(dates[0])).days)
    total = float(arr[-1] - 1.0)
    cagr = float(arr[-1] ** (365.25 / days) - 1.0) if arr[-1] > 0 else -1.0
    mdd = max_drawdown(arr)
    calmar = cagr / abs(mdd) if mdd < -1e-12 else (999.0 if cagr > 0 else 0.0)
    return {
        "dates": dates,
        "curve": arr,
        "total_return": total,
        "cagr": cagr,
        "max_drawdown": mdd,
        "calmar": float(calmar),
        "turnover": float(turnover),
        "position_changes": int(changes),
        "time_in_market": float(invested / len(arr)),
        "hard_exit_count": int(hard_exits),
        "buy_exec_count": int(buy_exec),
        "sell_exec_count": int(sell_exec),
        "pm_buy_exec_count": int(pm_buy_exec),
        "pm_sell_exec_count": int(pm_sell_exec),
    }


def simulate_buy_hold(bars: list[dict], friction_bps: float) -> dict:
    idx = [i for i, b in enumerate(bars) if FORMAL_START.strftime("%Y-%m-%d") <= b["date"] <= FORMAL_END.strftime("%Y-%m-%d")]
    start, end = idx[0], idx[-1]
    cost = friction_bps / 10000.0
    first_open = float(bars[start]["open"])
    shares = 1.0 / (first_open * (1.0 + cost))
    curve = np.asarray([shares * float(bars[i]["close"]) for i in range(start, end + 1)], dtype=float)
    dates = [bars[i]["date"] for i in range(start, end + 1)]
    days = max(1, (pd.Timestamp(dates[-1]) - pd.Timestamp(dates[0])).days)
    total = float(curve[-1] - 1.0)
    cagr = float(curve[-1] ** (365.25 / days) - 1.0)
    mdd = max_drawdown(curve)
    return {
        "dates": dates, "curve": curve, "total_return": total, "cagr": cagr,
        "max_drawdown": mdd, "calmar": float(cagr / abs(mdd) if mdd < -1e-12 else 999.0),
        "turnover": 1.0, "position_changes": 1, "time_in_market": 1.0,
    }


def simulate_sma200(bars: list[dict], friction_bps: float) -> dict:
    closes = np.asarray([float(b["close"]) for b in bars], dtype=float)
    sma = pd.Series(closes).rolling(200, min_periods=200).mean().to_numpy()
    idx = [i for i, b in enumerate(bars) if FORMAL_START.strftime("%Y-%m-%d") <= b["date"] <= FORMAL_END.strftime("%Y-%m-%d")]
    start, end = idx[0], idx[-1]
    cash = 1.0
    shares = 0.0
    cost_rate = friction_bps / 10000.0
    curve = []
    dates = []
    changes = 0
    turnover = 0.0
    invested = 0

    for j in range(start, end + 1):
        op = float(bars[j]["open"])
        cl = float(bars[j]["close"])
        pre = cash + shares * op
        desired = 0.0
        if j > 0 and math.isfinite(sma[j - 1]) and closes[j - 1] > sma[j - 1]:
            desired = 1.0
        pos = shares * op
        target_value = desired * pre
        order = target_value - pos
        if order > 1e-14:
            order = min(order, max(0.0, cash / (1.0 + cost_rate)))
        elif order < -1e-14:
            order = max(order, -pos)
        if abs(order) > 1e-14:
            cost = abs(order) * cost_rate
            shares += order / op
            cash -= order + cost
            if shares <= 1e-12:
                shares = 0.0
            changes += 1
            turnover += abs(order) / pre
        eq = cash + shares * cl
        curve.append(eq)
        dates.append(bars[j]["date"])
        if shares > 1e-12:
            invested += 1

    arr = np.asarray(curve, dtype=float)
    days = max(1, (pd.Timestamp(dates[-1]) - pd.Timestamp(dates[0])).days)
    total = float(arr[-1] - 1.0)
    cagr = float(arr[-1] ** (365.25 / days) - 1.0) if arr[-1] > 0 else -1.0
    mdd = max_drawdown(arr)
    return {
        "dates": dates, "curve": arr, "total_return": total, "cagr": cagr,
        "max_drawdown": mdd, "calmar": float(cagr / abs(mdd) if mdd < -1e-12 else 999.0),
        "turnover": float(turnover), "position_changes": int(changes),
        "time_in_market": float(invested / len(arr)),
    }


def event_forward(bars: list[dict], ledger: list[dict], predicate, horizons=(10, 20)) -> dict:
    vals = {h: [] for h in horizons}
    symbol_vals = {h: [] for h in horizons}
    by_h = {h: [] for h in horizons}
    for t, row in enumerate(ledger):
        if row["date"] < FORMAL_START.strftime("%Y-%m-%d") or row["date"] > FORMAL_END.strftime("%Y-%m-%d"):
            continue
        if not predicate(row):
            continue
        if t + max(horizons) >= len(bars):
            continue
        entry = float(bars[t + 1]["open"])
        if entry <= 0:
            continue
        for h in horizons:
            by_h[h].append(float(bars[t + h]["close"]) / entry - 1.0)
    return {
        str(h): {
            "n": len(by_h[h]),
            "median": float(np.median(by_h[h])) if by_h[h] else None,
            "mean": float(np.mean(by_h[h])) if by_h[h] else None,
            "win_rate": float(np.mean(np.asarray(by_h[h]) > 0)) if by_h[h] else None,
        }
        for h in horizons
    }


def portfolio_metrics(results: dict[str, dict]) -> dict:
    common = set.intersection(*(set(v["dates"]) for v in results.values()))
    dates = sorted(common)
    if len(dates) < 2:
        raise RuntimeError("no common dates")
    curves = []
    for s, r in results.items():
        pos = {d: i for i, d in enumerate(r["dates"])}
        arr = np.asarray([r["curve"][pos[d]] for d in dates], dtype=float)
        arr = arr / arr[0]
        curves.append(arr)
    curve = np.mean(np.vstack(curves), axis=0)
    days = max(1, (pd.Timestamp(dates[-1]) - pd.Timestamp(dates[0])).days)
    total = float(curve[-1] - 1.0)
    cagr = float(curve[-1] ** (365.25 / days) - 1.0)
    mdd = max_drawdown(curve)
    return {
        "start": dates[0], "end": dates[-1],
        "total_return": total, "cagr": cagr, "max_drawdown": mdd,
        "calmar": float(cagr / abs(mdd) if mdd < -1e-12 else 999.0),
        "turnover_mean": float(np.mean([v["turnover"] for v in results.values()])),
        "time_in_market_mean": float(np.mean([v["time_in_market"] for v in results.values()])),
    }


def compact(r: dict) -> dict:
    return {k: r[k] for k in r if k not in {"curve", "dates"}}


def pct(x: float | None) -> str:
    return "—" if x is None else f"{100*x:.2f}%"


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    manifest = {
        "study": "PURE_SLTD_V8_PROBABILITY_MAP_R2",
        "provider": "Yahoo Finance via yfinance",
        "auto_adjust": False,
        "fetch_start": FETCH_START,
        "fetch_end_exclusive": FETCH_END_EXCLUSIVE,
        "formal_window": [FORMAL_START.strftime("%Y-%m-%d"), FORMAL_END.strftime("%Y-%m-%d")],
        "symbols": SYMBOLS,
        "files": {},
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }

    frames = {}
    bars_by_symbol = {}
    ledger_by_symbol = {}

    for ticker, industry in UNIVERSE:
        frame = fetch_stock(ticker)
        if pd.Timestamp(frame["Date"].min()) >= FORMAL_START:
            raise RuntimeError(f"{ticker}: no pre-2020 warmup")
        if pd.Timestamp(frame["Date"].max()) < FORMAL_END:
            raise RuntimeError(f"{ticker}: data ends early {frame['Date'].max()}")
        frames[ticker] = frame
        bars = candles_from_frame(frame)
        ledger = sltd.build_ledger(bars, ticker)
        bars_by_symbol[ticker] = bars
        ledger_by_symbol[ticker] = ledger
        p = DATA_DIR / f"{ticker}.csv.gz"
        manifest["files"][ticker] = {
            "industry": industry,
            "rows": len(frame),
            "first": pd.Timestamp(frame["Date"].min()).strftime("%Y-%m-%d"),
            "last": pd.Timestamp(frame["Date"].max()).strftime("%Y-%m-%d"),
            "sha256": sha256_file(p),
        }

    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    systems = {}
    per_symbol = {}
    event_buy_all = {10: [], 20: []}
    event_sell_all = {10: [], 20: []}

    for friction_label, bps in (("5bps", 5.0), ("10bps", 10.0)):
        systems[friction_label] = {"V7_BASE": {}, "PMAP_14": {}, "BUY_HOLD": {}, "SMA200_TREND": {}}
        for s in SYMBOLS:
            bars = bars_by_symbol[s]
            ledger = ledger_by_symbol[s]
            base = simulate_sltd(bars, ledger, bps, False)
            cand = simulate_sltd(bars, ledger, bps, True)
            official = sltd.simulate_policy(bars, ledger, friction_bps=bps)
            if abs(float(official["final_equity"]) - (1.0 + base["total_return"])) > 1e-9:
                raise RuntimeError(f"{s}: baseline parity mismatch at {bps}bps")
            systems[friction_label]["V7_BASE"][s] = base
            systems[friction_label]["PMAP_14"][s] = cand
            systems[friction_label]["BUY_HOLD"][s] = simulate_buy_hold(bars, bps)
            systems[friction_label]["SMA200_TREND"][s] = simulate_sma200(bars, bps)

    # Event sanity is price-only and friction-independent.
    for s in SYMBOLS:
        bars = bars_by_symbol[s]
        ledger = ledger_by_symbol[s]
        for t, row in enumerate(ledger):
            if row["date"] < FORMAL_START.strftime("%Y-%m-%d") or row["date"] > FORMAL_END.strftime("%Y-%m-%d"):
                continue
            if t + 20 >= len(bars):
                continue
            entry = float(bars[t + 1]["open"])
            if entry <= 0:
                continue
            if pm_buy(row):
                event_buy_all[10].append(float(bars[t + 10]["close"]) / entry - 1.0)
                event_buy_all[20].append(float(bars[t + 20]["close"]) / entry - 1.0)
            if pm_sell(row):
                event_sell_all[10].append(float(bars[t + 10]["close"]) / entry - 1.0)
                event_sell_all[20].append(float(bars[t + 20]["close"]) / entry - 1.0)

    portfolio = {}
    for flabel in systems:
        portfolio[flabel] = {
            label: portfolio_metrics(systems[flabel][label])
            for label in systems[flabel]
        }

    per_symbol = {
        s: {
            flabel: {label: compact(systems[flabel][label][s]) for label in systems[flabel]}
            for flabel in systems
        }
        for s in SYMBOLS
    }

    base = portfolio["5bps"]["V7_BASE"]
    cand = portfolio["5bps"]["PMAP_14"]
    trend = portfolio["5bps"]["SMA200_TREND"]

    better_return = sum(
        per_symbol[s]["5bps"]["PMAP_14"]["total_return"] > per_symbol[s]["5bps"]["V7_BASE"]["total_return"]
        for s in SYMBOLS
    )
    better_calmar = sum(
        per_symbol[s]["5bps"]["PMAP_14"]["calmar"] > per_symbol[s]["5bps"]["V7_BASE"]["calmar"]
        for s in SYMBOLS
    )

    buy10 = float(np.median(event_buy_all[10])) if event_buy_all[10] else None
    buy20 = float(np.median(event_buy_all[20])) if event_buy_all[20] else None
    sell10 = float(np.median(event_sell_all[10])) if event_sell_all[10] else None
    sell20 = float(np.median(event_sell_all[20])) if event_sell_all[20] else None

    gates = {
        "portfolio_return_improves_vs_v7": cand["total_return"] > base["total_return"],
        "portfolio_calmar_improves_vs_v7": cand["calmar"] > base["calmar"],
        "portfolio_maxdd_not_worse_by_gt_1pp": cand["max_drawdown"] >= base["max_drawdown"] - 0.01,
        "symbol_return_breadth_ge_11": better_return >= 11,
        "symbol_calmar_breadth_ge_11": better_calmar >= 11,
        "pm_buy_10d_positive": buy10 is not None and buy10 > 0,
        "pm_buy_20d_positive": buy20 is not None and buy20 > 0,
        "pm_sell_10d_nonpositive": sell10 is not None and sell10 <= 0,
        "pm_sell_20d_nonpositive": sell20 is not None and sell20 <= 0,
        "simple_baseline_guard": (
            cand["calmar"] > trend["calmar"]
            or (cand["total_return"] > trend["total_return"] and cand["max_drawdown"] >= trend["max_drawdown"])
        ),
    }

    if all(gates.values()):
        decision = "PROMOTE_TO_ENGINEERING_CANDIDATE"
    elif (not gates["portfolio_return_improves_vs_v7"]) or (not gates["portfolio_calmar_improves_vs_v7"]):
        decision = "REJECTED_NOT_ADMITTED"
    else:
        decision = "RESEARCH_ONLY_NOT_PROMOTED"

    event_sanity = {
        "PM_BUY_1": {
            "count": len(event_buy_all[10]),
            "ret10_median": buy10,
            "ret20_median": buy20,
            "ret10_win_rate": float(np.mean(np.asarray(event_buy_all[10]) > 0)) if event_buy_all[10] else None,
            "ret20_win_rate": float(np.mean(np.asarray(event_buy_all[20]) > 0)) if event_buy_all[20] else None,
        },
        "PM_SELL_1": {
            "count": len(event_sell_all[10]),
            "ret10_median": sell10,
            "ret20_median": sell20,
            "ret10_win_rate": float(np.mean(np.asarray(event_sell_all[10]) > 0)) if event_sell_all[10] else None,
            "ret20_win_rate": float(np.mean(np.asarray(event_sell_all[20]) > 0)) if event_sell_all[20] else None,
        },
    }

    out = {
        "meta": {
            "study": "PURE_SLTD_V8_PROBABILITY_MAP_R2",
            "status": "COMPLETE",
            "protocol": "PURE_SLTD_V8_PROBABILITY_MAP_R2_PROTOCOL_v1.md",
            "source_probability_result": "PURE_SLTD_STATE_PROBABILITY_RESULT_v1.json",
            "chan_used": False,
            "candidate_rules": [PM_BUY_ID, PM_SELL_ID],
            "fresh_universe": UNIVERSE,
            "universe_count": len(SYMBOLS),
            "formal_window": "2020-01-02..2026-09-30",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        },
        "portfolio": portfolio,
        "breadth_5bps": {
            "return_better_vs_v7": better_return,
            "calmar_better_vs_v7": better_calmar,
        },
        "event_sanity": event_sanity,
        "gates": gates,
        "decision": decision,
        "per_symbol": per_symbol,
    }
    OUT_JSON.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# Pure SLTD V8 Probability-Map Candidate R2 — Result",
        "",
        "Status: **COMPLETE**",
        "",
        f"Decision: **{decision}**",
        "",
        "Fresh universe: **20 previously unused US stocks**.",
        "",
        "## Equal-weight portfolio — 5 bps",
        "",
        "| System | Return | CAGR | MaxDD | Calmar | Turnover mean | Exposure mean |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for label in ("V7_BASE", "PMAP_14", "BUY_HOLD", "SMA200_TREND"):
        m = portfolio["5bps"][label]
        lines.append(
            f"| {label} | {pct(m['total_return'])} | {pct(m['cagr'])} | {pct(m['max_drawdown'])} | "
            f"{m['calmar']:.3f} | {m['turnover_mean']:.2f} | {pct(m['time_in_market_mean'])} |"
        )

    lines += [
        "",
        "## Breadth vs current V7 — 5 bps",
        "",
        f"- Better Total Return: **{better_return}/20**",
        f"- Better Calmar: **{better_calmar}/20**",
        "",
        "## Fresh20 event sanity",
        "",
        f"- PM_BUY_1 events: **{event_sanity['PM_BUY_1']['count']}**; 10d median {pct(buy10)}; 20d median {pct(buy20)}",
        f"- PM_SELL_1 events: **{event_sanity['PM_SELL_1']['count']}**; 10d median {pct(sell10)}; 20d median {pct(sell20)}",
        "",
        "## Admission gates",
        "",
    ]
    for k, v in gates.items():
        lines.append(f"- {k}: **{'PASS' if v else 'FAIL'}**")

    lines += [
        "",
        "## Per-symbol 5 bps return",
        "",
        "| Symbol | V7 | PMAP_14 | Delta | PM buy exec | PM sell exec |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for s in SYMBOLS:
        b = per_symbol[s]["5bps"]["V7_BASE"]
        c = per_symbol[s]["5bps"]["PMAP_14"]
        lines.append(
            f"| {s} | {pct(b['total_return'])} | {pct(c['total_return'])} | "
            f"{pct(c['total_return'] - b['total_return'])} | "
            f"{c['pm_buy_exec_count']} | {c['pm_sell_exec_count']} |"
        )

    lines += [
        "",
        "The existing V7 remains unchanged unless this result is explicitly promoted into engineering.",
        "",
        f"`PURE_SLTD_V8_PROBABILITY_MAP_R2 = {decision}`",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps({
        "decision": decision,
        "portfolio_5bps": {k: compact(v) for k, v in portfolio["5bps"].items()},
        "breadth_5bps": out["breadth_5bps"],
        "event_sanity": event_sanity,
        "gates": gates,
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
