#!/usr/bin/env python3
"""SLTD V7 Sell Intensity & Full Exit Study v1 — Round 1 / frozen Daily-79.

Research only. This file does not modify V6 or the frozen V7 candidate taxonomy.
"""
from __future__ import annotations

import json
import math
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import sltd_v7_combination_ablation_v1 as parent  # noqa: E402

core = parent.core

OUT_JSON = ROOT / "SLTD_V7_SELL_INTENSITY_FULL_EXIT_ROUND1_RESULT_v1.json"
OUT_MD = ROOT / "SLTD_V7_SELL_INTENSITY_FULL_EXIT_ROUND1_RESULT_v1.md"
FROZEN_V7_RESULT = ROOT / "SLTD_V7_79_STOCK_ROBUSTNESS_RESULT_v1.json"

FORMAL_START = pd.Timestamp("2020-01-02")
FORMAL_END = pd.Timestamp("2026-09-30")
FRICTIONS = (5.0, 10.0)

V7_DROPS = frozenset({
    "BUY_RECENT_BLUE_GRAY_LIGHT_SUPPORT",
    "SELL_RECENT_BLUE_GRAY_LIGHT_RESIST",
    "NEW_V5_D_GREEN_11_20_UPPER_WICK_ONLY",
})

S1 = "S1_MATURE_BLUE_UPPER_WICK"
S2 = "S2_MATURE_BLUE_UPPER_ANY"
S3 = "S3_MATURE_BLUE_WICK_CONFIRM_DOWN"

MODES = ("CUR25", "CUR50", "TARGET50", "TARGET25", "FULL")

VARIANTS: dict[str, dict] = {
    "BASELINE_V7": {"sell_modes": {}, "direct_c2": False, "candidate_zd1_full": False},
}
for event in (S1, S2, S3):
    for mode in MODES:
        VARIANTS[f"{event}__{mode}"] = {
            "sell_modes": {event: mode},
            "direct_c2": False,
            "candidate_zd1_full": False,
        }

VARIANTS.update({
    "LAYER_S1_CUR25_S3_CUR50": {
        "sell_modes": {S1: "CUR25", S3: "CUR50"},
        "direct_c2": False,
        "candidate_zd1_full": False,
    },
    "LAYER_S1_CUR25_S3_TARGET25": {
        "sell_modes": {S1: "CUR25", S3: "TARGET25"},
        "direct_c2": False,
        "candidate_zd1_full": False,
    },
    "LAYER_S1_CUR25_S3_FULL": {
        "sell_modes": {S1: "CUR25", S3: "FULL"},
        "direct_c2": False,
        "candidate_zd1_full": False,
    },
    "LAYER_S1_CUR25_S3_TARGET25_ZD1_FULL": {
        "sell_modes": {S1: "CUR25", S3: "TARGET25"},
        "direct_c2": False,
        "candidate_zd1_full": True,
    },
    "LAYER_S1_CUR25_S3_TARGET25_DIRECT_C2": {
        "sell_modes": {S1: "CUR25", S3: "TARGET25"},
        "direct_c2": True,
        "candidate_zd1_full": False,
    },
    "LAYER_S1_CUR25_S3_FULL_DIRECT_C2": {
        "sell_modes": {S1: "CUR25", S3: "FULL"},
        "direct_c2": True,
        "candidate_zd1_full": False,
    },
    "DIRECT_C2_FULL": {
        "sell_modes": {},
        "direct_c2": True,
        "candidate_zd1_full": False,
    },
    "S1_CUR25_ZD1_FULL": {
        "sell_modes": {S1: "CUR25"},
        "direct_c2": False,
        "candidate_zd1_full": True,
    },
    "S2_CUR25_ZD1_FULL": {
        "sell_modes": {S2: "CUR25"},
        "direct_c2": False,
        "candidate_zd1_full": True,
    },
})


def valid_num(x) -> bool:
    try:
        return math.isfinite(float(x))
    except (TypeError, ValueError):
        return False


def atomic_hits(i: int, ledger: list[dict]) -> tuple[str, ...]:
    row = ledger[i]
    prev = ledger[i - 1] if i > 0 else None
    out: list[str] = []
    if (
        str(row.get("color")) == "BLUE"
        and int(row.get("run_age") or 0) >= 21
        and bool(row.get("upper"))
        and row.get("upper_subtype") == "WICK_ONLY"
    ):
        out.append(S1)
    if (
        str(row.get("color")) == "BLUE"
        and int(row.get("run_age") or 0) >= 21
        and bool(row.get("upper"))
    ):
        out.append(S2)
    if (
        prev is not None
        and str(prev.get("color")) == "BLUE"
        and int(prev.get("run_age") or 0) >= 21
        and bool(prev.get("upper"))
        and prev.get("upper_subtype") == "WICK_ONLY"
        and float(row["close"]) < float(prev["close"])
    ):
        out.append(S3)
    return tuple(out)


def v7_classes(row: dict | None, extra_sell: bool) -> tuple[str, ...]:
    if not row:
        return ()
    classes: list[str] = []
    for cls in ("BUY", "HOLD", "WAIT", "SELL"):
        ids = [x for x in row.get(cls, []) if x not in V7_DROPS]
        if ids or (cls == "SELL" and extra_sell):
            classes.append(cls)
    return tuple(classes)


def resolve(classes: tuple[str, ...]) -> str | None:
    if len(classes) == 1:
        return classes[0]
    return None


def c2_condition(row: dict | None) -> bool:
    if not row or str(row.get("color") or "").upper() != "GREEN":
        return False
    return valid_num(row.get("high")) and valid_num(row.get("GZB4")) and float(row["high"]) < float(row["GZB4"])


def close_below_zd1(row: dict | None) -> bool:
    return bool(
        row
        and valid_num(row.get("close"))
        and valid_num(row.get("ZD1"))
        and float(row["close"]) < float(row["ZD1"])
    )


def read_prepare(batch: int, symbol: str) -> dict:
    frame = parent.read_frame(batch, symbol)
    ledger = parent.read_ledger(batch, symbol)
    hit_by_date = {
        pd.Timestamp(row["date"]): atomic_hits(i, ledger)
        for i, row in enumerate(ledger)
    }
    row_by_date = {pd.Timestamp(row["date"]): row for row in ledger}

    dates = pd.to_datetime(frame["Date"]).dt.tz_localize(None)
    mask = (dates >= FORMAL_START) & (dates <= FORMAL_END)
    idx = np.flatnonzero(mask.to_numpy())
    if len(idx) < 2:
        raise RuntimeError(f"{symbol}: insufficient formal bars")
    formal_dates = [pd.Timestamp(dates.iloc[i]) for i in idx]
    rows = [row_by_date[d] for d in formal_dates]
    hits = [hit_by_date[d] for d in formal_dates]

    return {
        "dates": [d.strftime("%Y-%m-%d") for d in formal_dates],
        "opens": frame["Open"].astype(float).to_numpy()[idx],
        "highs": frame["High"].astype(float).to_numpy()[idx],
        "lows": frame["Low"].astype(float).to_numpy()[idx],
        "closes": frame["Close"].astype(float).to_numpy()[idx],
        "rows": rows,
        "hits": hits,
    }


def desired_position_value(mode: str, position_value: float, pre_equity: float) -> float:
    if mode == "CUR25":
        return position_value * 0.75
    if mode == "CUR50":
        return position_value * 0.50
    if mode == "TARGET50":
        return min(position_value, pre_equity * 0.50)
    if mode == "TARGET25":
        return min(position_value, pre_equity * 0.25)
    if mode == "FULL":
        return 0.0
    raise ValueError(mode)


def q(values: list[float], p: float) -> float | None:
    return float(np.quantile(np.asarray(values, dtype=float), p)) if values else None


def mean(values: list[float]) -> float | None:
    return float(statistics.fmean(values)) if values else None


def median(values: list[float]) -> float | None:
    return float(statistics.median(values)) if values else None


def simulate(prep: dict, cfg: dict, friction_bps: float) -> dict:
    opens = prep["opens"]
    highs = prep["highs"]
    lows = prep["lows"]
    closes = prep["closes"]
    rows = prep["rows"]
    hits = prep["hits"]
    n = len(opens)

    cash = 1.0
    shares = 0.0
    risk_armed = False
    candidate_armed = False
    turnover = 0.0
    changes = 0
    invested = 0
    full_exits = 0
    candidate_sell_exec = 0
    strong_sell_exec = 0
    curve = np.empty(n, dtype=float)
    cost_rate = float(friction_bps) / 10000.0
    markers: list[dict] = []

    cycle_start_equity: float | None = None
    trade_returns: list[float] = []

    for j in range(n):
        op = float(opens[j])
        cl = float(closes[j])
        pre = cash + shares * op
        if pre <= 0:
            raise RuntimeError("non-positive equity")
        pos = shares * op
        frac = pos / pre
        signal = rows[j - 1] if j > 0 else None
        signal_hits = hits[j - 1] if j > 0 else ()
        configured_hits = [h for h in signal_hits if h in cfg["sell_modes"]]
        extra_sell = bool(configured_hits)

        hard_reason = None
        if shares > 1e-14 and signal is not None:
            if cfg.get("direct_c2") and c2_condition(signal):
                hard_reason = "DIRECT_C2_FULL"
            elif risk_armed and c2_condition(signal):
                hard_reason = "ARMED_C2_FULL"
            elif cfg.get("candidate_zd1_full") and candidate_armed and close_below_zd1(signal):
                hard_reason = "CANDIDATE_ARMED_CLOSE_BELOW_ZD1_FULL"

        classes = v7_classes(signal, extra_sell)
        action = resolve(classes)
        order = 0.0
        ordinary_action = None
        sell_mode = None

        if hard_reason:
            order = -pos
        else:
            ordinary_action = action
            if action == "BUY":
                target = 0.25 if shares <= 1e-14 else min(1.0, frac + 0.25)
                order = max(frac, target) * pre - pos
            elif action == "SELL" and shares > 1e-14:
                if configured_hits:
                    desired = pos
                    chosen = []
                    for h in configured_hits:
                        mode = cfg["sell_modes"][h]
                        chosen.append(mode)
                        desired = min(desired, desired_position_value(mode, pos, pre))
                    sell_mode = "+".join(sorted(set(chosen)))
                    order = desired - pos
                else:
                    sell_mode = "BASELINE_CUR25"
                    order = -pos * 0.25

        if order > 1e-14:
            order = min(order, max(0.0, cash / (1.0 + cost_rate)))
        elif order < -1e-14:
            order = max(order, -pos)

        executed = abs(order) > 1e-14
        before_shares = shares
        if executed:
            cost = abs(order) * cost_rate
            shares += order / op
            cash -= order + cost
            turnover += abs(order) / pre
            changes += 1
            if shares <= 1e-12:
                shares = 0.0

            if cycle_start_equity is None and order > 0 and shares > 1e-14:
                cycle_start_equity = pre

        became_flat = before_shares > 1e-14 and shares <= 1e-14

        if hard_reason and executed:
            full_exits += 1
            risk_armed = False
            candidate_armed = False
        elif executed and ordinary_action == "SELL" and order < 0:
            risk_armed = True
            if configured_hits:
                candidate_armed = True
                candidate_sell_exec += 1
                if sell_mode and sell_mode not in ("CUR25", "BASELINE_CUR25"):
                    strong_sell_exec += 1
            if became_flat:
                full_exits += 1
                risk_armed = False
                candidate_armed = False
        elif executed and ordinary_action == "BUY" and order > 0:
            risk_armed = False
            candidate_armed = False

        close_eq = cash + shares * cl
        curve[j] = close_eq
        if shares > 1e-12:
            invested += 1

        if became_flat and cycle_start_equity is not None:
            trade_returns.append(cash / cycle_start_equity - 1.0)
            cycle_start_equity = None

        if executed:
            after_frac = (shares * cl / close_eq) if close_eq > 0 else 0.0
            markers.append({
                "index": j,
                "execution_date": prep["dates"][j],
                "price": op,
                "side": "X" if hard_reason else ("B" if order > 0 else "S"),
                "action": "HARD_EXIT" if hard_reason else ordinary_action,
                "hard_reason": hard_reason,
                "configured_hits": configured_hits,
                "sell_mode": sell_mode,
                "position_after": float(max(0.0, min(1.0, after_frac))),
                "full_exit": bool(became_flat),
            })

    if cycle_start_equity is not None:
        trade_returns.append(float(curve[-1]) / cycle_start_equity - 1.0)

    full_markers = [m for m in markers if m["full_exit"]]
    buy_markers = [m for m in markers if m["side"] == "B"]
    post = {h: [] for h in (1, 3, 5, 10)}
    avoided_drop_10: list[float] = []
    lost_upside_10: list[float] = []
    wrong_10 = 0
    eligible_10 = 0
    rebuy5 = 0
    reentry_any = 0

    for fm in full_markers:
        j = int(fm["index"])
        px = float(fm["price"])
        later_buys = [b for b in buy_markers if int(b["index"]) > j]
        if later_buys:
            reentry_any += 1
            if int(later_buys[0]["index"]) <= j + 5:
                rebuy5 += 1
        for h in (1, 3, 5, 10):
            if j + h < n:
                post[h].append(float(closes[j + h]) / px - 1.0)
        if j + 10 < n:
            eligible_10 += 1
            r10 = float(closes[j + 10]) / px - 1.0
            wrong_10 += int(r10 > 0)
            window_lows = [float(x) for x in lows[j + 1:j + 11]]
            window_highs = [float(x) for x in highs[j + 1:j + 11]]
            avoided_drop_10.append(max(0.0, 1.0 - min(window_lows) / px))
            lost_upside_10.append(max(0.0, max(window_highs) / px - 1.0))

    final = float(curve[-1])
    days = max(1, (pd.Timestamp(prep["dates"][-1]) - pd.Timestamp(prep["dates"][0])).days)
    total_return = final - 1.0
    cagr = final ** (365.25 / days) - 1.0 if final > 0 else -1.0
    mdd = core.max_drawdown(curve)
    calmar = cagr / abs(mdd) if mdd < -1e-12 else (999.0 if cagr > 0 else 0.0)

    tail_cut = q(trade_returns, 0.05)
    tail = [x for x in trade_returns if tail_cut is not None and x <= tail_cut]

    return {
        "curve": curve,
        "total_return": float(total_return),
        "cagr": float(cagr),
        "max_drawdown": float(mdd),
        "calmar": float(calmar),
        "turnover": float(turnover),
        "position_changes": int(changes),
        "time_in_market": float(invested / n),
        "hard_exit_count": int(full_exits),
        "full_exit_count": int(full_exits),
        "candidate_sell_executed": int(candidate_sell_exec),
        "strong_sell_executed": int(strong_sell_exec),
        "reentry_after_full_exit": int(reentry_any),
        "quick_rebuy_5bars": int(rebuy5),
        "wrong_full_exit_10bar_count": int(wrong_10),
        "eligible_full_exit_10bar_count": int(eligible_10),
        "post_full_returns": {str(h): post[h] for h in post},
        "avoided_drop_10": avoided_drop_10,
        "lost_upside_10": lost_upside_10,
        "trade_count": len(trade_returns),
        "p5_trade_return": tail_cut,
        "cvar5_trade_return": mean(tail),
    }


def compact(v: dict) -> dict:
    return {k: v[k] for k in (
        "total_return", "cagr", "max_drawdown", "calmar", "turnover",
        "position_changes", "time_in_market", "full_exit_count",
        "candidate_sell_executed", "strong_sell_executed",
        "reentry_after_full_exit", "quick_rebuy_5bars",
        "wrong_full_exit_10bar_count", "eligible_full_exit_10bar_count",
        "trade_count", "p5_trade_return", "cvar5_trade_return",
    )}


def merge_event_stats(per_symbol: dict[str, dict]) -> dict:
    post = {h: [] for h in (1, 3, 5, 10)}
    avoided: list[float] = []
    upside: list[float] = []
    full = reentry = rebuy = wrong = eligible = cand = strong = 0
    for v in per_symbol.values():
        full += v["full_exit_count"]
        reentry += v["reentry_after_full_exit"]
        rebuy += v["quick_rebuy_5bars"]
        wrong += v["wrong_full_exit_10bar_count"]
        eligible += v["eligible_full_exit_10bar_count"]
        cand += v["candidate_sell_executed"]
        strong += v["strong_sell_executed"]
        for h in post:
            post[h].extend(v["post_full_returns"][str(h)])
        avoided.extend(v["avoided_drop_10"])
        upside.extend(v["lost_upside_10"])
    return {
        "full_exit_count": full,
        "candidate_sell_executed": cand,
        "strong_sell_executed": strong,
        "reentry_after_full_exit": reentry,
        "quick_rebuy_5bars": rebuy,
        "quick_rebuy_rate": rebuy / full if full else 0.0,
        "wrong_full_exit_10bar_count": wrong,
        "eligible_full_exit_10bar_count": eligible,
        "wrong_full_exit_10bar_rate": wrong / eligible if eligible else 0.0,
        "post_full_return_mean": {str(h): mean(post[h]) for h in post},
        "post_full_return_median": {str(h): median(post[h]) for h in post},
        "median_avoided_drop_10": median(avoided),
        "mean_avoided_drop_10": mean(avoided),
        "median_lost_upside_10": median(upside),
        "mean_lost_upside_10": mean(upside),
    }


def status_for(delta: dict, better_calmar: int) -> str:
    if (
        better_calmar >= 44
        and delta["calmar"] > 0
        and delta["max_drawdown"] >= 0
        and delta["cagr"] >= -0.005
    ):
        return "ADVANCE_TO_ROUND2"
    if better_calmar <= 31 and delta["calmar"] < 0 and delta["cagr"] < 0:
        return "REJECTED_NOT_ADMITTED"
    return "WATCH"


def pct(x: float | None) -> str:
    return "NA" if x is None else f"{100.0 * x:+.2f}%"


def num(x: float | None) -> str:
    return "NA" if x is None else f"{x:+.3f}"


def main() -> None:
    prepared = {}
    batch_of = {}
    for batch, symbols in core.BATCHES.items():
        print(f"BATCH_{batch:02d}_PREPARE", flush=True)
        for symbol in symbols:
            prepared[symbol] = read_prepare(batch, symbol)
            batch_of[symbol] = batch
    if len(prepared) != 79:
        raise RuntimeError(f"expected 79 symbols, got {len(prepared)}")

    sims: dict[str, dict[str, dict[str, dict]]] = {}
    portfolio: dict[str, dict[str, dict]] = {}
    for bps in FRICTIONS:
        key = f"{int(bps)}bps"
        sims[key] = {}
        portfolio[key] = {}
        for name, cfg in VARIANTS.items():
            print(f"RUN {key} {name}", flush=True)
            per = {s: simulate(prepared[s], cfg, bps) for s in prepared}
            sims[key][name] = per
            portfolio[key][name] = parent.portfolio(per, prepared)

    frozen = json.loads(FROZEN_V7_RESULT.read_text(encoding="utf-8"))
    expected = frozen["all79"]["5bps"]["CANDIDATE_B_DROP_B3_S1_S3"]
    actual = portfolio["5bps"]["BASELINE_V7"]
    baseline_diffs = {k: float(actual[k] - expected[k]) for k in ("total_return", "cagr", "max_drawdown", "calmar")}
    if any(abs(v) > 1e-10 for v in baseline_diffs.values()):
        raise RuntimeError(f"V7 baseline reproduction failed: {baseline_diffs}")

    summary = {}
    base_per = sims["5bps"]["BASELINE_V7"]
    base_port = portfolio["5bps"]["BASELINE_V7"]

    for name in VARIANTS:
        per = sims["5bps"][name]
        p = portfolio["5bps"][name]
        delta = {k: float(p[k] - base_port[k]) for k in ("total_return", "cagr", "max_drawdown", "calmar")}
        better_return = sum(per[s]["total_return"] > base_per[s]["total_return"] for s in prepared)
        better_mdd = sum(per[s]["max_drawdown"] > base_per[s]["max_drawdown"] for s in prepared)
        better_calmar = sum(per[s]["calmar"] > base_per[s]["calmar"] for s in prepared)
        dr = [per[s]["total_return"] - base_per[s]["total_return"] for s in prepared]
        dc = [per[s]["calmar"] - base_per[s]["calmar"] for s in prepared]
        dm = [per[s]["max_drawdown"] - base_per[s]["max_drawdown"] for s in prepared]
        cvars = [per[s]["cvar5_trade_return"] for s in prepared if per[s]["cvar5_trade_return"] is not None]
        ev = merge_event_stats(per)
        summary[name] = {
            "status": "BASELINE" if name == "BASELINE_V7" else status_for(delta, better_calmar),
            "portfolio_5bps": p,
            "portfolio_10bps": portfolio["10bps"][name],
            "delta_vs_baseline_5bps": delta,
            "better_return_symbols": int(better_return),
            "better_max_drawdown_symbols": int(better_mdd),
            "better_calmar_symbols": int(better_calmar),
            "median_symbol_delta_return": median(dr),
            "p10_symbol_delta_return": q(dr, 0.10),
            "median_symbol_delta_max_drawdown": median(dm),
            "median_symbol_delta_calmar": median(dc),
            "p10_symbol_total_return": q([per[s]["total_return"] for s in prepared], 0.10),
            "median_symbol_cvar5_trade_return": median(cvars),
            "events": ev,
        }

    per_symbol = {
        s: {
            "batch": batch_of[s],
            "5bps": {name: compact(sims["5bps"][name][s]) for name in VARIANTS},
            "10bps": {name: compact(sims["10bps"][name][s]) for name in VARIANTS},
        }
        for s in prepared
    }

    payload = {
        "meta": {
            "study": "SLTD_V7_SELL_INTENSITY_FULL_EXIT_STUDY_V1_ROUND1",
            "status": "IMPLEMENTED_AND_VERIFIED",
            "round": 1,
            "research_type": "REUSED_FROZEN_79_STOCK_DAILY_LONG_HISTORY",
            "source_candidate_branch": "candidate/sltd-v7-12rules-position-v1",
            "source_candidate_commit": "5f9ea4d8fa434b54afdbf32a1cb21ef2f3cb4042",
            "rollback_v6_commit": "05be43e350d9193ba01a2748ef4c0267438a84b1",
            "formal_window": "2020-01-02..2026-09-30",
            "representation": "FIRST_OBSERVED",
            "execution": "SIGNAL_CLOSE_TO_NEXT_AVAILABLE_OPEN",
            "frictions_bps": list(FRICTIONS),
            "wrong_full_exit_definition": "10-bar close return from exit open > 0",
            "avoided_drop_definition": "max(0, 1 - min(next 10 lows)/exit open)",
            "lost_upside_definition": "max(0, max(next 10 highs)/exit open - 1)",
            "status_gate": {
                "advance": "better_calmar>=44/79 AND delta_calmar>0 AND delta_max_drawdown>=0 AND delta_cagr>=-0.005",
                "reject": "better_calmar<=31/79 AND delta_calmar<0 AND delta_cagr<0",
                "otherwise": "WATCH",
            },
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        },
        "baseline_reproduction": {"status": "PASS", "diffs": baseline_diffs},
        "variants": VARIANTS,
        "summary": summary,
        "per_symbol": per_symbol,
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# SLTD V7 Sell Intensity & Full Exit Study v1 — Round 1",
        "",
        "状态：**IMPLEMENTED_AND_VERIFIED**",
        "",
        "- Universe：冻结 79 股票",
        "- 周期：1d",
        "- 正式窗口：2020-01-02 ~ 2026-09-30",
        "- 执行：信号 K 线收盘确认 → 下一根同周期 K 线开盘执行",
        "- V7 baseline reproduction：PASS",
        "",
        "## 核心结果（5 bps）",
        "",
        "| Variant | Status | Return | CAGR | MaxDD | Calmar | ΔCAGR | ΔMDD | ΔCalmar | Better Calmar | Full exits | 5-bar rebuy | Wrong exit 10b | Median post10 | Avoided drop10 | Lost upside10 |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name, s in summary.items():
        p = s["portfolio_5bps"]
        d = s["delta_vs_baseline_5bps"]
        e = s["events"]
        lines.append(
            f"| {name} | {s['status']} | {pct(p['total_return'])} | {pct(p['cagr'])} | "
            f"{pct(p['max_drawdown'])} | {p['calmar']:.3f} | {pct(d['cagr'])} | "
            f"{pct(d['max_drawdown'])} | {num(d['calmar'])} | {s['better_calmar_symbols']}/79 | "
            f"{e['full_exit_count']} | {e['quick_rebuy_5bars']}/{e['full_exit_count']} | "
            f"{e['wrong_full_exit_10bar_count']}/{e['eligible_full_exit_10bar_count']} | "
            f"{pct(e['post_full_return_median']['10'])} | {pct(e['median_avoided_drop_10'])} | "
            f"{pct(e['median_lost_upside_10'])} |"
        )

    lines += [
        "",
        "## 强度定义",
        "",
        "- `CUR25`：卖当前持仓的 25%。",
        "- `CUR50`：卖当前持仓的 50%。",
        "- `TARGET50`：把仓位降到不高于 50%。",
        "- `TARGET25`：把仓位降到不高于 25%。",
        "- `FULL`：全部清仓。",
        "- `DIRECT_C2_FULL`：不要求先有普通 SELL；若 GREEN 且 High < GZB4，下一根开盘直接清仓。",
        "- `ZD1_FULL`：仅在新增候选 SELL 已实际执行后警戒；后续收盘跌破彩色带下轨 ZD1，下一根开盘清仓。",
        "",
        "## 解释边界",
        "",
        "- 本轮只负责长期 1d 强度筛选，不修改正式 V7。",
        "- 中轨公式未在当前冻结事实源中确认，所以本轮没有凭感觉构造“跌破中轨”规则。",
        "- `错误清仓率` 定义为清仓后第 10 根收盘高于清仓执行价；同时保留 10 根内最大避免下跌与损失上涨，避免只用单一标签。",
        "- 只有 `ADVANCE_TO_ROUND2` 才进入 1h / 4h 跨周期验证；Round 1 不直接录取正式规则。",
        "",
        "`SLTD_V7_SELL_INTENSITY_FULL_EXIT_ROUND1 = IMPLEMENTED_AND_VERIFIED`",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(OUT_MD.read_text(encoding="utf-8"), flush=True)


if __name__ == "__main__":
    main()
