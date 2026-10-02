#!/usr/bin/env python3
"""SLTD V6 Hard Exit Study v2 — fixed 79-stock confirmation candidates."""
from __future__ import annotations

import gzip
import json
import statistics
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

import sltd_v6_position_policy_batch_v1 as core


ROOT = Path(__file__).resolve().parent
DATA_ROOT = ROOT / "data_snapshot"
LEDGER_ROOT = ROOT / "signal_ledgers"
DECISION = ROOT / "SLTD_V6_POSITION_POLICY_STOCK_VALIDATION_DECISION_v1.json"
OUT_JSON = ROOT / "SLTD_V6_HARD_EXIT_STUDY_V2_79_STOCKS.json"
OUT_MD = ROOT / "SLTD_V6_HARD_EXIT_STUDY_V2_79_STOCKS.md"

VARIANTS = (
    "BASELINE",
    "A_SELL_ARMED_THEN_GREEN_FULL_BELOW",
    "B_GREEN_FULL_BELOW_THEN_NO_RECLAIM",
    "C_SELL_ARMED_GREEN_CLOSE_BELOW_SLOW_BAND",
    "D_SELL_ARMED_GREEN_ZD1_MINUS_1ATR",
)
HORIZONS = (5, 10, 20)


def load_policy() -> core.Policy:
    doc = json.loads(DECISION.read_text(encoding="utf-8"))
    d = doc["decision"]
    p = d["policy"]
    policy = core.Policy(
        p["initial"], p["add_mode"], p["sell_reduction"], p["wait_mode"], p["resolution"]
    )
    expected = "I25_AADD_25_TO_CAP_S25_WHOLD_RNO_CHANGE_MIXED"
    if not d.get("stock_policy_promoted") or d["result"] != expected or policy.id != expected:
        raise RuntimeError("Promoted stock policy drifted")
    return policy


def read_frame(batch: int, symbol: str) -> pd.DataFrame:
    path = DATA_ROOT / f"batch_{batch:02d}_stocks" / f"{symbol}.csv.gz"
    with gzip.open(path, "rt", encoding="utf-8") as f:
        frame = pd.read_csv(f, parse_dates=["Date"])
    frame["Date"] = pd.to_datetime(frame["Date"]).dt.tz_localize(None)
    return frame


def read_ledger(batch: int, symbol: str) -> list[dict]:
    path = LEDGER_ROOT / f"BATCH_{batch:02d}_{symbol}_FIRST_OBSERVED.csv.gz"
    with gzip.open(path, "rt", encoding="utf-8") as f:
        df = pd.read_csv(f)
    df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None)
    rows: list[dict] = []
    for rec in df.to_dict("records"):
        for a in ("BUY", "HOLD", "WAIT", "SELL"):
            v = rec.get(a)
            if pd.isna(v) or str(v).strip() == "":
                rec[a] = []
            else:
                rec[a] = [x for x in str(v).split("|") if x]
        rows.append(rec)
    return rows


def fnum(v) -> float | None:
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    return x if np.isfinite(x) else None


def truthy(v) -> bool:
    if isinstance(v, bool):
        return v
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return False
    return str(v).strip().lower() in {"true", "1", "yes"}


def h1_green_full_below(row: dict | None) -> bool:
    if not row:
        return False
    return (
        str(row.get("color", "")).upper() == "GREEN"
        and truthy(row.get("lower"))
        and str(row.get("lower_subtype", "")).upper() == "FULL_BELOW"
    )


def close_below_zd1(row: dict | None) -> bool:
    if not row:
        return False
    close = fnum(row.get("close"))
    zd1 = fnum(row.get("ZD1"))
    return close is not None and zd1 is not None and close < zd1


def green_close_below_slow_bottom(row: dict | None) -> bool:
    if not row or str(row.get("color", "")).upper() != "GREEN":
        return False
    close = fnum(row.get("close"))
    gzb4 = fnum(row.get("GZB4"))
    return close is not None and gzb4 is not None and close < gzb4


def wilder_atr14(frame: pd.DataFrame) -> dict[pd.Timestamp, float]:
    high = frame["High"].astype(float).to_numpy()
    low = frame["Low"].astype(float).to_numpy()
    close = frame["Close"].astype(float).to_numpy()
    tr = np.empty(len(frame), dtype=float)
    for i in range(len(frame)):
        if i == 0:
            tr[i] = high[i] - low[i]
        else:
            tr[i] = max(
                high[i] - low[i],
                abs(high[i] - close[i - 1]),
                abs(low[i] - close[i - 1]),
            )
    atr = np.full(len(frame), np.nan, dtype=float)
    if len(frame) >= 14:
        atr[13] = float(np.mean(tr[:14]))
        for i in range(14, len(frame)):
            atr[i] = (13.0 * atr[i - 1] + tr[i]) / 14.0
    dates = pd.to_datetime(frame["Date"]).dt.tz_localize(None)
    return {
        pd.Timestamp(dates.iloc[i]): float(atr[i])
        for i in range(len(frame))
        if np.isfinite(atr[i])
    }


def d_condition(row: dict | None, atr_map: dict[pd.Timestamp, float]) -> bool:
    if not row or str(row.get("color", "")).upper() != "GREEN":
        return False
    close = fnum(row.get("close"))
    zd1 = fnum(row.get("ZD1"))
    date = pd.Timestamp(row.get("date"))
    atr = atr_map.get(date)
    if close is None or zd1 is None or atr is None:
        return False
    return close < zd1 and (zd1 - close) >= atr


def prepare(frame: pd.DataFrame, ledger: list[dict]) -> dict:
    prep = core.prepare_fast_symbol(frame, ledger)
    prep["ledger_by_date"] = {pd.Timestamp(x["date"]): x for x in ledger}
    prep["atr14"] = wilder_atr14(frame)
    return prep


def simulate(
    prep: dict,
    policy: core.Policy,
    variant: str,
    friction_bps: float,
    symbol: str,
) -> dict:
    dates = [pd.Timestamp(x) for x in prep["dates"]]
    opens = prep["opens"]
    closes = prep["closes"]
    actions = prep["actions"][policy.resolution]
    by_date = prep["ledger_by_date"]
    atr_map = prep["atr14"]
    n = len(dates)

    cash = 1.0
    shares = 0.0
    turnover = 0.0
    changes = 0
    invested_days = 0
    risk_armed = False
    hard_exit_count = 0
    curve = np.empty(n, dtype=float)
    exit_events: list[dict] = []
    cost_rate = friction_bps / 10000.0

    for j in range(n):
        op = float(opens[j])
        cl = float(closes[j])
        pre_equity = cash + shares * op
        if pre_equity <= 0:
            raise RuntimeError("non-positive equity")
        position_value = shares * op
        current_fraction = position_value / pre_equity

        signal = by_date.get(dates[j - 1]) if j > 0 else None
        prior_signal = by_date.get(dates[j - 2]) if j > 1 else None

        hard = False
        reason = None
        if shares > 1e-14 and signal is not None:
            if variant == "A_SELL_ARMED_THEN_GREEN_FULL_BELOW":
                hard = risk_armed and h1_green_full_below(signal)
                reason = "A_SELL_ARMED_THEN_GREEN_FULL_BELOW" if hard else None
            elif variant == "B_GREEN_FULL_BELOW_THEN_NO_RECLAIM":
                hard = h1_green_full_below(prior_signal) and close_below_zd1(signal)
                reason = "B_GREEN_FULL_BELOW_THEN_NO_RECLAIM" if hard else None
            elif variant == "C_SELL_ARMED_GREEN_CLOSE_BELOW_SLOW_BAND":
                hard = risk_armed and green_close_below_slow_bottom(signal)
                reason = "C_SELL_ARMED_GREEN_CLOSE_BELOW_SLOW_BAND" if hard else None
            elif variant == "D_SELL_ARMED_GREEN_ZD1_MINUS_1ATR":
                hard = risk_armed and d_condition(signal, atr_map)
                reason = "D_SELL_ARMED_GREEN_ZD1_MINUS_1ATR" if hard else None

        order_value = 0.0
        ordinary_action = None
        if hard:
            order_value = -position_value
        else:
            action = int(actions[j])
            ordinary_action = action
            if action == 1:  # BUY
                if shares <= 1e-14:
                    desired_fraction = policy.initial
                elif policy.add_mode == "IGNORE":
                    desired_fraction = current_fraction
                elif policy.add_mode == "ADD_25_TO_CAP":
                    desired_fraction = min(1.0, current_fraction + 0.25)
                elif policy.add_mode == "ADD_ENTRY_TO_CAP":
                    desired_fraction = min(1.0, current_fraction + policy.initial)
                else:
                    desired_fraction = 1.0
                desired_fraction = max(current_fraction, desired_fraction)
                order_value = desired_fraction * pre_equity - position_value
            elif action == 4 and shares > 0:  # SELL
                order_value = -position_value * policy.sell_reduction

        if order_value > 1e-14:
            max_buy = max(0.0, cash / (1.0 + cost_rate))
            order_value = min(order_value, max_buy)
        elif order_value < -1e-14:
            order_value = max(order_value, -position_value)

        executed = abs(order_value) > 1e-14
        if executed:
            cost = abs(order_value) * cost_rate
            shares += order_value / op
            cash -= order_value + cost
            turnover += abs(order_value) / pre_equity
            changes += 1
            if shares <= 1e-12:
                shares = 0.0

        if hard and executed:
            hard_exit_count += 1
            ev = {
                "symbol": symbol,
                "date": dates[j].strftime("%Y-%m-%d"),
                "exit_open": op,
                "reason": reason,
            }
            for h in HORIZONS:
                if j + h < n:
                    ev[f"forward_{h}d"] = float(closes[j + h] / op - 1.0)
                else:
                    ev[f"forward_{h}d"] = None
            exit_events.append(ev)
            risk_armed = False
        elif executed and ordinary_action == 4 and order_value < 0:
            risk_armed = True
        elif executed and ordinary_action == 1 and order_value > 0:
            risk_armed = False

        curve[j] = cash + shares * cl
        if shares > 1e-12:
            invested_days += 1

    final_equity = float(curve[-1])
    days = max(1, (dates[-1] - dates[0]).days)
    total_return = final_equity - 1.0
    cagr = final_equity ** (365.25 / days) - 1.0 if final_equity > 0 else -1.0
    mdd = core.max_drawdown(curve)
    calmar = cagr / abs(mdd) if mdd < -1e-12 else (999.0 if cagr > 0 else 0.0)
    return {
        "curve": curve,
        "total_return": float(total_return),
        "cagr": float(cagr),
        "max_drawdown": float(mdd),
        "calmar": float(calmar),
        "turnover": float(turnover),
        "position_changes": int(changes),
        "time_in_market": float(invested_days / n),
        "hard_exit_count": int(hard_exit_count),
        "exit_events": exit_events,
    }


def portfolio(per_symbol: dict[str, dict], prepared: dict[str, dict]) -> dict:
    common_dates, common_idx = core.prepare_common_alignment(prepared)
    curves = np.vstack([
        per_symbol[s]["curve"][common_idx[s]]
        for s in per_symbol
    ])
    curve = np.mean(curves, axis=0)
    days = max(1, (pd.Timestamp(common_dates[-1]) - pd.Timestamp(common_dates[0])).days)
    total = float(curve[-1] - 1.0)
    cagr = float(curve[-1] ** (365.25 / days) - 1.0) if curve[-1] > 0 else -1.0
    mdd = core.max_drawdown(curve)
    calmar = cagr / abs(mdd) if mdd < -1e-12 else (999.0 if cagr > 0 else 0.0)
    return {
        "total_return": total,
        "cagr": cagr,
        "max_drawdown": float(mdd),
        "calmar": float(calmar),
        "turnover_mean": float(np.mean([v["turnover"] for v in per_symbol.values()])),
        "position_changes_sum": int(sum(v["position_changes"] for v in per_symbol.values())),
        "time_in_market_mean": float(np.mean([v["time_in_market"] for v in per_symbol.values()])),
        "hard_exit_count_sum": int(sum(v["hard_exit_count"] for v in per_symbol.values())),
        "common_start": common_dates[0],
        "common_end": common_dates[-1],
    }


def compact(v: dict) -> dict:
    return {
        k: v[k] for k in (
            "total_return", "cagr", "max_drawdown", "calmar", "turnover",
            "position_changes", "time_in_market", "hard_exit_count"
        )
    }


def post_exit_summary(events: list[dict]) -> dict:
    out = {"event_count": len(events)}
    for h in HORIZONS:
        vals = [e[f"forward_{h}d"] for e in events if e.get(f"forward_{h}d") is not None]
        out[f"{h}d"] = {
            "n": len(vals),
            "mean": float(np.mean(vals)) if vals else None,
            "median": float(np.median(vals)) if vals else None,
            "positive_rate": float(np.mean([x > 0 for x in vals])) if vals else None,
            "negative_rate": float(np.mean([x < 0 for x in vals])) if vals else None,
        }
    return out


def delta(a: dict, b: dict) -> dict:
    return {
        "cagr": a["cagr"] - b["cagr"],
        "max_drawdown": a["max_drawdown"] - b["max_drawdown"],
        "calmar": a["calmar"] - b["calmar"],
        "total_return": a["total_return"] - b["total_return"],
    }


def pct(x: float | None) -> str:
    return "NA" if x is None else f"{100*x:.2f}%"


def main() -> None:
    policy = load_policy()

    prepared: dict[str, dict] = {}
    batch_of: dict[str, int] = {}
    for batch, symbols in core.BATCHES.items():
        for symbol in symbols:
            frame = read_frame(batch, symbol)
            ledger = read_ledger(batch, symbol)
            prepared[symbol] = prepare(frame, ledger)
            batch_of[symbol] = batch
    if len(prepared) != 79:
        raise RuntimeError(f"Expected 79 symbols, got {len(prepared)}")

    sims: dict[str, dict[str, dict[str, dict]]] = {"5bps": {}, "10bps": {}}
    for friction_name, bps in (("5bps", 5.0), ("10bps", 10.0)):
        for variant in VARIANTS:
            sims[friction_name][variant] = {
                s: simulate(prepared[s], policy, variant, bps, s)
                for s in prepared
            }

    batch_results: dict[str, dict[str, dict[str, dict]]] = {"5bps": {}, "10bps": {}}
    all79: dict[str, dict[str, dict]] = {"5bps": {}, "10bps": {}}
    for friction in ("5bps", "10bps"):
        for variant in VARIANTS:
            batch_results[friction][variant] = {}
            for batch, symbols in core.BATCHES.items():
                subp = {s: prepared[s] for s in symbols}
                subs = {s: sims[friction][variant][s] for s in symbols}
                batch_results[friction][variant][str(batch)] = portfolio(subs, subp)
            all79[friction][variant] = portfolio(sims[friction][variant], prepared)

    comparisons = {}
    base = batch_results["5bps"]["BASELINE"]
    for variant in VARIANTS[1:]:
        deltas = {}
        improve_calmar = improve_cagr = improve_mdd = 0
        for b in map(str, range(1, 9)):
            d = delta(batch_results["5bps"][variant][b], base[b])
            deltas[b] = d
            improve_calmar += d["calmar"] > 0
            improve_cagr += d["cagr"] > 0
            improve_mdd += d["max_drawdown"] > 0
        comparisons[variant] = {
            "batch_deltas_5bps": deltas,
            "batches_improved_calmar": int(improve_calmar),
            "batches_improved_cagr": int(improve_cagr),
            "batches_improved_max_drawdown": int(improve_mdd),
            "median_batch_calmar": statistics.median(
                batch_results["5bps"][variant][str(b)]["calmar"] for b in range(1, 9)
            ),
            "median_batch_cagr": statistics.median(
                batch_results["5bps"][variant][str(b)]["cagr"] for b in range(1, 9)
            ),
            "median_batch_max_drawdown": statistics.median(
                batch_results["5bps"][variant][str(b)]["max_drawdown"] for b in range(1, 9)
            ),
            "median_batch_10bps_calmar": statistics.median(
                batch_results["10bps"][variant][str(b)]["calmar"] for b in range(1, 9)
            ),
        }

    exit_events = {}
    exit_quality = {}
    for variant in VARIANTS[1:]:
        events = []
        for s in prepared:
            events.extend(sims["5bps"][variant][s]["exit_events"])
        exit_events[variant] = events
        exit_quality[variant] = post_exit_summary(events)

    per_symbol = {}
    for s in prepared:
        per_symbol[s] = {
            "batch": batch_of[s],
            "5bps": {v: compact(sims["5bps"][v][s]) for v in VARIANTS},
            "10bps": {v: compact(sims["10bps"][v][s]) for v in VARIANTS},
        }

    output = {
        "meta": {
            "study": "SLTD_V6_HARD_EXIT_STUDY_V2",
            "status": "COMPLETE",
            "universe_count": 79,
            "batches": list(range(1, 9)),
            "formal_window": "2020-01-02..2026-09-30",
            "ordinary_policy": policy.id,
            "representation": "FIRST_OBSERVED",
            "execution": "SIGNAL_CLOSE_TO_NEXT_AVAILABLE_OPEN",
            "friction": {"baseline_bps": 5, "stress_bps": 10},
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        },
        "variants": list(VARIANTS),
        "all79_equal_weight": all79,
        "batch_results": batch_results,
        "comparisons": comparisons,
        "post_exit_quality_5bps": exit_quality,
        "exit_events_5bps": exit_events,
        "per_symbol": per_symbol,
    }
    OUT_JSON.write_text(json.dumps(output, indent=2), encoding="utf-8")

    lines = [
        "# SLTD V6 Hard Exit Study v2 — 79 Stocks",
        "",
        "Status: **COMPLETE**",
        "",
        f"Ordinary policy fixed: `{policy.id}`",
        "",
        "## All-79 equal-weight portfolio — 5 bps",
        "",
        "| Variant | Return | CAGR | MaxDD | Calmar | Turnover | Time in market | Hard exits |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for v in VARIANTS:
        m = all79["5bps"][v]
        lines.append(
            f"| {v} | {pct(m['total_return'])} | {pct(m['cagr'])} | {pct(m['max_drawdown'])} | "
            f"{m['calmar']:.3f} | {m['turnover_mean']:.2f} | {pct(m['time_in_market_mean'])} | "
            f"{m['hard_exit_count_sum']} |"
        )

    lines += [
        "",
        "## Batch-level comparison versus BASELINE — 5 bps",
        "",
        "| Variant | Calmar improved | CAGR improved | MaxDD improved | Median Calmar | Median CAGR | Median MaxDD | Median 10bps Calmar |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for v in VARIANTS[1:]:
        x = comparisons[v]
        lines.append(
            f"| {v} | {x['batches_improved_calmar']}/8 | {x['batches_improved_cagr']}/8 | "
            f"{x['batches_improved_max_drawdown']}/8 | {x['median_batch_calmar']:.3f} | "
            f"{pct(x['median_batch_cagr'])} | {pct(x['median_batch_max_drawdown'])} | "
            f"{x['median_batch_10bps_calmar']:.3f} |"
        )

    lines += [
        "",
        "## What happened after Hard Exit? — 5 bps event set",
        "",
        "| Variant | Exits | +5d median | +5d positive | +10d median | +10d positive | +20d median | +20d positive |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for v in VARIANTS[1:]:
        q = exit_quality[v]
        lines.append(
            f"| {v} | {q['event_count']} | {pct(q['5d']['median'])} | {pct(q['5d']['positive_rate'])} | "
            f"{pct(q['10d']['median'])} | {pct(q['10d']['positive_rate'])} | "
            f"{pct(q['20d']['median'])} | {pct(q['20d']['positive_rate'])} |"
        )

    lines += [
        "",
        "Positive post-exit return means the stock had rebounded above the exit open by that horizon;",
        "negative return means it was still below the exit open.",
        "",
        "The four candidates were frozen before this run. No threshold was tuned after seeing results.",
        "",
        "`SLTD_V6_HARD_EXIT_STUDY_V2 = COMPLETE`",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
