#!/usr/bin/env python3
"""Standalone SLTD score-regime mode v2.

Independent architecture:
SLTD state -> frozen Phase12 score -> hysteretic LONG/CASH state machine.
V7 is comparator only.
"""
from __future__ import annotations

import json
import math
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

ROOT = Path(__file__).resolve().parent
PHASE7 = ROOT.parent / "phase7"
PHASE11 = ROOT.parent / "phase11"
PHASE12 = ROOT.parent / "phase12"

sys.path.insert(0, str(PHASE12))
sys.path.insert(0, str(PHASE11))
sys.path.insert(0, str(PHASE7))

import pure_sltd_state_score_exposure_map_v1 as px
import pure_sltd_v8_probability_map_r2_v1 as r2

PROJECT = ROOT.parents[2] / "integrations" / "sltd_v7_siftalpha_v1"
sys.path.insert(0, str(PROJECT))
import strategy as sltd

import sltd_v6_position_policy_batch_v1 as core

FORMAL_START = pd.Timestamp("2020-01-02")
FORMAL_END = pd.Timestamp("2026-09-30")
FETCH_START = "2010-01-04"
FETCH_END_EXCLUSIVE = "2026-10-01"

UNIVERSE = [
    ("TFC", "Financial"), ("AON", "Financial"), ("MET", "Financial"),
    ("ANET", "Technology"), ("MSI", "Technology"), ("NXPI", "Technology"),
    ("ELV", "Healthcare"), ("MCK", "Healthcare"), ("RMD", "Healthcare"),
    ("GWW", "Industrials"), ("CMI", "Industrials"), ("NSC", "Industrials"),
    ("STLD", "Materials"), ("CF", "Materials"), ("LYB", "Materials"),
    ("RCL", "ConsumerDiscretionary"), ("DHI", "ConsumerDiscretionary"), ("NVR", "ConsumerDiscretionary"),
    ("CPB", "ConsumerStaples"), ("TSN", "ConsumerStaples"), ("ADM", "ConsumerStaples"),
    ("PEG", "Utilities"), ("ES", "Utilities"), ("ETR", "Utilities"),
    ("HAL", "Energy"), ("DVN", "Energy"), ("FANG", "Energy"),
    ("VICI", "RealEstate"), ("SPG", "RealEstate"), ("DLR", "RealEstate"),
]
SYMBOLS = [s for s, _ in UNIVERSE]

DATA_DIR = ROOT / "fresh30_score_regime_v2_data"
OUT_JSON = ROOT / "SLTD_STATE_SCORE_REGIME_MODE_V2_RESULT.json"
OUT_MD = ROOT / "SLTD_STATE_SCORE_REGIME_MODE_V2_RESULT.md"


def pct(x):
    return "—" if x is None else f"{100*x:.2f}%"


def compact(x):
    return {k: v for k, v in x.items() if k not in {"dates", "curve"}}


def fetch_stock(ticker: str) -> pd.DataFrame:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / f"{ticker}.csv.gz"
    if path.exists():
        return pd.read_csv(path, parse_dates=["Date"])

    last = None
    for attempt in range(4):
        try:
            f = yf.download(
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
            if f is not None and not f.empty:
                out = r2.flatten_yf(f, ticker)
                out.to_csv(path, index=False, compression="gzip")
                return out
            last = RuntimeError("empty download")
        except Exception as exc:
            last = exc
        time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"{ticker}: download failed: {last}")


def simulate_regime(bars, ledger, weights, cal, bps):
    formal_index = next(
        (i for i, b in enumerate(bars) if b["date"] >= FORMAL_START.strftime("%Y-%m-%d")),
        0,
    )
    start = max(formal_index, min(sltd.MIN_WARMUP_BARS, len(bars) - 1))
    end = max(i for i, b in enumerate(bars) if b["date"] <= FORMAL_END.strftime("%Y-%m-%d"))
    if end <= start:
        raise RuntimeError("insufficient formal window")

    cash = 1.0
    shares = 0.0
    cost_rate = bps / 10000.0
    curve = []
    dates = []
    turnover = 0.0
    changes = 0
    invested = 0
    entries = 0
    exits = 0
    holding_lengths = []
    current_hold = 0
    bucket_counts = defaultdict(int)

    for j in range(start, end + 1):
        op = float(bars[j]["open"])
        cl = float(bars[j]["close"])
        pre = cash + shares * op
        pos = shares * op
        long_now = shares > 1e-12

        if j > 0:
            score, _, _ = px.score_bar(ledger, j - 1, weights)
            bucket = px.target_from_score(score, cal["pos_scale"], cal["neg_scale"])
        else:
            score = 0.0
            bucket = 0.75
        bucket_counts[str(bucket)] += 1

        order = 0.0
        if (not long_now) and abs(bucket - 1.0) < 1e-12:
            order = pre
        elif long_now and abs(bucket - 0.25) < 1e-12:
            order = -pos

        if order > 1e-14:
            order = min(order, max(0.0, cash / (1.0 + cost_rate)))
        elif order < -1e-14:
            order = max(order, -pos)

        executed = abs(order) > 1e-14
        if executed:
            was_long = shares > 1e-12
            cost = abs(order) * cost_rate
            shares += order / op
            cash -= order + cost
            if shares <= 1e-12:
                shares = 0.0
            now_long = shares > 1e-12
            changes += 1
            turnover += abs(order) / pre

            if (not was_long) and now_long:
                entries += 1
                current_hold = 0
            elif was_long and (not now_long):
                exits += 1
                if current_hold > 0:
                    holding_lengths.append(current_hold)
                current_hold = 0

        eq = cash + shares * cl
        curve.append(eq)
        dates.append(bars[j]["date"])

        if shares > 1e-12:
            invested += 1
            current_hold += 1

    if shares > 1e-12 and current_hold > 0:
        holding_lengths.append(current_hold)

    arr = np.asarray(curve, dtype=float)
    days = max(1, (pd.Timestamp(dates[-1]) - pd.Timestamp(dates[0])).days)
    total = float(arr[-1] - 1.0)
    cagr = float(arr[-1] ** (365.25 / days) - 1.0) if arr[-1] > 0 else -1.0
    mdd = r2.max_drawdown(arr)
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
        "entries": int(entries),
        "exits": int(exits),
        "average_holding_bars": float(np.mean(holding_lengths)) if holding_lengths else 0.0,
        "median_holding_bars": float(np.median(holding_lengths)) if holding_lengths else 0.0,
        "target_bucket_counts": dict(bucket_counts),
    }


def trigger_diagnostic(bars_by, ledger_by, weights, cal):
    base = defaultdict(lambda: defaultdict(list))
    trigger = {
        "ENTRY_100": defaultdict(lambda: defaultdict(list)),
        "EXIT_25": defaultdict(lambda: defaultdict(list)),
    }
    counts = {"ENTRY_100": 0, "EXIT_25": 0}
    symbols_by = {"ENTRY_100": set(), "EXIT_25": set()}

    for s in SYMBOLS:
        bars = bars_by[s]
        ledger = ledger_by[s]
        for t, row in enumerate(ledger):
            dt = pd.Timestamp(row["date"])
            if not (FORMAL_START <= dt <= FORMAL_END):
                continue
            if t + 20 >= len(bars):
                continue
            entry = float(bars[t + 1]["open"])
            if entry <= 0:
                continue

            score, _, _ = px.score_bar(ledger, t, weights)
            bucket = px.target_from_score(score, cal["pos_scale"], cal["neg_scale"])

            for h in (10, 20):
                ret = float(bars[t + h]["close"]) / entry - 1.0
                base[s][h].append(ret)

            key = None
            if abs(bucket - 1.0) < 1e-12:
                key = "ENTRY_100"
            elif abs(bucket - 0.25) < 1e-12:
                key = "EXIT_25"

            if key:
                counts[key] += 1
                symbols_by[key].add(s)
                for h in (10, 20):
                    ret = float(bars[t + h]["close"]) / entry - 1.0
                    trigger[key][s][h].append(ret)

    out = {}
    for key in ("ENTRY_100", "EXIT_25"):
        out[key] = {
            "count": counts[key],
            "symbol_count": len(symbols_by[key]),
            "horizons": {},
        }
        for h in (10, 20):
            effects = []
            abs_meds = []
            for s in SYMBOLS:
                vals = trigger[key][s][h]
                if vals and base[s][h]:
                    med = float(np.median(vals))
                    effects.append(med - float(np.median(base[s][h])))
                    abs_meds.append(med)
            out[key]["horizons"][str(h)] = {
                "cross_symbol_median_excess": float(np.median(effects)) if effects else None,
                "cross_symbol_median_absolute_return": float(np.median(abs_meds)) if abs_meds else None,
                "positive_breadth": float(np.mean(np.asarray(effects) > 0)) if effects else None,
                "negative_breadth": float(np.mean(np.asarray(effects) < 0)) if effects else None,
                "symbol_effect_count": len(effects),
            }
    return out


def main():
    prior79 = {s for xs in core.BATCHES.values() for s in xs}
    prior24 = {s for s, _ in px.UNIVERSE}
    prior = prior79 | set(px.PRIOR_OOS10) | set(px.PRIOR_R2) | set(px.PRIOR_R3) | prior24
    overlap = sorted(set(SYMBOLS) & prior)
    if overlap:
        raise RuntimeError(f"Fresh30 v2 overlap with prior research: {overlap}")
    if len(SYMBOLS) != 30 or len(set(SYMBOLS)) != 30:
        raise RuntimeError("Fresh30 v2 must contain 30 unique symbols")

    weights, weight_meta = px.load_confirmed_weights()
    calibration = px.calibrate(weights)

    bars_by = {}
    ledger_by = {}
    manifest = {
        "study": "SLTD_STATE_SCORE_REGIME_MODE_V2",
        "symbols": SYMBOLS,
        "industries": dict(UNIVERSE),
        "prior_overlap": overlap,
        "provider": "Yahoo Finance via yfinance",
        "auto_adjust": False,
        "fetch_start": FETCH_START,
        "fetch_end_exclusive": FETCH_END_EXCLUSIVE,
        "formal_window": ["2020-01-02", "2026-09-30"],
        "frozen_score_source": "research/sltd-state-score-exposure-map-v1@29ceeeb73328e0f1b1108f01ab14179e858c7e5e",
        "calibration": calibration,
        "files": {},
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for s, industry in UNIVERSE:
        frame = fetch_stock(s)
        if pd.Timestamp(frame["Date"].min()) >= FORMAL_START:
            raise RuntimeError(f"{s}: no pre-2020 warmup")
        if pd.Timestamp(frame["Date"].max()) < FORMAL_END:
            raise RuntimeError(f"{s}: data ends early at {frame['Date'].max()}")

        bars = r2.candles_from_frame(frame)
        ledger = sltd.build_ledger(bars, s)
        bars_by[s] = bars
        ledger_by[s] = ledger

        p = DATA_DIR / f"{s}.csv.gz"
        manifest["files"][s] = {
            "industry": industry,
            "rows": len(frame),
            "first": pd.Timestamp(frame["Date"].min()).strftime("%Y-%m-%d"),
            "last": pd.Timestamp(frame["Date"].max()).strftime("%Y-%m-%d"),
            "sha256": r2.sha256_file(p),
        }

    (DATA_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    systems = {}
    for flabel, bps in (("5bps", 5.0), ("10bps", 10.0), ("20bps", 20.0)):
        systems[flabel] = {
            "SCORE_REGIME_V2": {},
            "SCORE_EXPOSURE_V1": {},
            "V7_BASE": {},
            "BUY_HOLD": {},
            "SMA200_TREND": {},
        }
        for s in SYMBOLS:
            bars = bars_by[s]
            ledger = ledger_by[s]

            systems[flabel]["SCORE_REGIME_V2"][s] = simulate_regime(
                bars, ledger, weights, calibration, bps
            )
            systems[flabel]["SCORE_EXPOSURE_V1"][s] = px.simulate_score_exposure(
                bars, ledger, weights, calibration, bps
            )
            systems[flabel]["V7_BASE"][s] = r2.simulate_sltd(
                bars, ledger, bps, False
            )
            systems[flabel]["BUY_HOLD"][s] = r2.simulate_buy_hold(bars, bps)
            systems[flabel]["SMA200_TREND"][s] = r2.simulate_sma200(bars, bps)

    portfolio = {
        flabel: {label: r2.portfolio_metrics(vals) for label, vals in systems[flabel].items()}
        for flabel in systems
    }

    per_symbol = {
        s: {
            flabel: {label: compact(systems[flabel][label][s]) for label in systems[flabel]}
            for flabel in systems
        }
        for s in SYMBOLS
    }

    diag = trigger_diagnostic(bars_by, ledger_by, weights, calibration)

    p5 = portfolio["5bps"]
    p10 = portfolio["10bps"]
    p20 = portfolio["20bps"]

    breadth = {
        "return_gt_v7": sum(
            per_symbol[s]["5bps"]["SCORE_REGIME_V2"]["total_return"] >
            per_symbol[s]["5bps"]["V7_BASE"]["total_return"]
            for s in SYMBOLS
        ),
        "return_gt_buyhold": sum(
            per_symbol[s]["5bps"]["SCORE_REGIME_V2"]["total_return"] >
            per_symbol[s]["5bps"]["BUY_HOLD"]["total_return"]
            for s in SYMBOLS
        ),
        "calmar_gt_v7": sum(
            per_symbol[s]["5bps"]["SCORE_REGIME_V2"]["calmar"] >
            per_symbol[s]["5bps"]["V7_BASE"]["calmar"]
            for s in SYMBOLS
        ),
    }

    entry10 = diag["ENTRY_100"]["horizons"]["10"]["cross_symbol_median_excess"]
    entry20 = diag["ENTRY_100"]["horizons"]["20"]["cross_symbol_median_excess"]
    exit10 = diag["EXIT_25"]["horizons"]["10"]["cross_symbol_median_excess"]
    exit20 = diag["EXIT_25"]["horizons"]["20"]["cross_symbol_median_excess"]

    gates = {
        "return_gt_score_exposure_v1_5bps":
            p5["SCORE_REGIME_V2"]["total_return"] > p5["SCORE_EXPOSURE_V1"]["total_return"],
        "calmar_gt_score_exposure_v1_5bps":
            p5["SCORE_REGIME_V2"]["calmar"] > p5["SCORE_EXPOSURE_V1"]["calmar"],
        "turnover_lt_score_exposure_v1_5bps":
            p5["SCORE_REGIME_V2"]["turnover_mean"] < p5["SCORE_EXPOSURE_V1"]["turnover_mean"],
        "return_gt_v7_5bps":
            p5["SCORE_REGIME_V2"]["total_return"] > p5["V7_BASE"]["total_return"],
        "calmar_gt_v7_5bps":
            p5["SCORE_REGIME_V2"]["calmar"] > p5["V7_BASE"]["calmar"],
        "return_ge_buyhold_5bps":
            p5["SCORE_REGIME_V2"]["total_return"] >= p5["BUY_HOLD"]["total_return"],
        "calmar_gt_buyhold_5bps":
            p5["SCORE_REGIME_V2"]["calmar"] > p5["BUY_HOLD"]["calmar"],
        "maxdd_better_than_buyhold":
            p5["SCORE_REGIME_V2"]["max_drawdown"] > p5["BUY_HOLD"]["max_drawdown"],
        "symbol_return_gt_v7_ge_16": breadth["return_gt_v7"] >= 16,
        "symbol_return_gt_buyhold_ge_16": breadth["return_gt_buyhold"] >= 16,
        "entry_100_excess_10_positive": entry10 is not None and entry10 > 0,
        "entry_100_excess_20_positive": entry20 is not None and entry20 > 0,
        "exit_25_excess_10_negative": exit10 is not None and exit10 < 0,
        "exit_25_excess_20_negative": exit20 is not None and exit20 < 0,
        "return_gt_v7_10bps":
            p10["SCORE_REGIME_V2"]["total_return"] > p10["V7_BASE"]["total_return"],
        "calmar_gt_v7_20bps":
            p20["SCORE_REGIME_V2"]["calmar"] > p20["V7_BASE"]["calmar"],
    }

    if all(gates.values()):
        decision = "PROMOTE_STANDALONE_SCORE_REGIME_TO_ENGINEERING_CANDIDATE"
    elif (
        gates["return_gt_score_exposure_v1_5bps"]
        and gates["calmar_gt_score_exposure_v1_5bps"]
        and gates["return_gt_v7_5bps"]
        and gates["calmar_gt_v7_5bps"]
    ):
        decision = "RESEARCH_ONLY_SCORE_REGIME_HAS_VALUE"
    else:
        decision = "REJECTED_SCORE_REGIME_V2"

    out = {
        "meta": {
            "study": "SLTD_STATE_SCORE_REGIME_MODE_V2",
            "status": "COMPLETE",
            "protocol": "SLTD_STATE_SCORE_REGIME_MODE_V2_PROTOCOL.md",
            "standalone_mode": True,
            "uses_v7_rules": False,
            "uses_v7_c2": False,
            "chan_used": False,
            "fresh30": UNIVERSE,
            "prior_overlap": overlap,
            "formal_window": "2020-01-02..2026-09-30",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        },
        "frozen_score": {
            "confirmed_state_count": len(weights),
            "positive_scale": calibration["pos_scale"],
            "negative_scale": calibration["neg_scale"],
        },
        "portfolio": portfolio,
        "breadth_5bps": breadth,
        "trigger_diagnostic": diag,
        "gates": gates,
        "decision": decision,
        "per_symbol": per_symbol,
    }
    OUT_JSON.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# SLTD State Score Regime Mode v2 — Result",
        "",
        "Status: **COMPLETE**",
        "",
        f"Decision: **{decision}**",
        "",
        "Standalone mode: **YES**",
        "Uses V7 trade rules: **NO**",
        "Uses V7 C2: **NO**",
        "Uses Chan/缠论: **NO**",
        "",
        "## Equal-weight Fresh30 portfolio — 5 bps",
        "",
        "| System | Return | CAGR | MaxDD | Calmar | Turnover | Exposure |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for label in ("SCORE_REGIME_V2", "SCORE_EXPOSURE_V1", "V7_BASE", "BUY_HOLD", "SMA200_TREND"):
        m = p5[label]
        lines.append(
            f"| {label} | {pct(m['total_return'])} | {pct(m['cagr'])} | {pct(m['max_drawdown'])} | "
            f"{m['calmar']:.3f} | {m['turnover_mean']:.2f} | {pct(m['time_in_market_mean'])} |"
        )

    lines += [
        "",
        "## Fresh30 breadth — 5 bps",
        "",
        f"- Return > V7: **{breadth['return_gt_v7']}/30**",
        f"- Calmar > V7: **{breadth['calmar_gt_v7']}/30**",
        f"- Return > Buy & Hold: **{breadth['return_gt_buyhold']}/30**",
        "",
        "## Trigger diagnostics",
        "",
        f"- ENTRY_100: 10d excess {pct(entry10)}, 20d excess {pct(entry20)}",
        f"- EXIT_25: 10d excess {pct(exit10)}, 20d excess {pct(exit20)}",
        "",
        "## Admission gates",
        "",
    ]
    for k, v in gates.items():
        lines.append(f"- {k}: **{'PASS' if v else 'FAIL'}**")

    lines += [
        "",
        "This result governs only the standalone score-regime mode. Production V7 is unchanged.",
        "",
        f"SLTD_STATE_SCORE_REGIME_MODE_V2 = {decision}",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps({
        "decision": decision,
        "portfolio_5bps": {k: compact(v) for k, v in p5.items()},
        "portfolio_10bps": {k: compact(v) for k, v in p10.items()},
        "portfolio_20bps": {k: compact(v) for k, v in p20.items()},
        "breadth_5bps": breadth,
        "trigger_diagnostic": diag,
        "gates": gates,
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
