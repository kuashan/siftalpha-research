#!/usr/bin/env python3
"""SLTD V6 Hard Exit Study v1 — 79 frozen-stock comparison."""
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
OUT_JSON = ROOT / "SLTD_V6_HARD_EXIT_STUDY_79_STOCKS_v1.json"
OUT_MD = ROOT / "SLTD_V6_HARD_EXIT_STUDY_79_STOCKS_v1.md"
DECISION = ROOT / "SLTD_V6_POSITION_POLICY_STOCK_VALIDATION_DECISION_v1.json"

VARIANTS = (
    "BASELINE",
    "H1_GREEN_LOWER_FULL_BELOW",
    "H2_GREEN_TWO_CLOSES_BELOW_ZD1",
    "H3_H1_OR_H2",
)


def load_promoted_policy() -> core.Policy:
    doc = json.loads(DECISION.read_text(encoding="utf-8"))
    d = doc["decision"]
    if not d.get("stock_policy_promoted"):
        raise RuntimeError("No promoted stock position policy")
    p = d["policy"]
    policy = core.Policy(
        p["initial"], p["add_mode"], p["sell_reduction"], p["wait_mode"], p["resolution"]
    )
    expected = "I25_AADD_25_TO_CAP_S25_WHOLD_RNO_CHANGE_MIXED"
    if policy.id != expected or d["result"] != expected:
        raise RuntimeError(f"Unexpected promoted policy: {policy.id} / {d['result']}")
    return policy


def read_frame(batch: int, symbol: str) -> pd.DataFrame:
    path = DATA_ROOT / f"batch_{batch:02d}_stocks" / f"{symbol}.csv.gz"
    if not path.exists():
        raise FileNotFoundError(path)
    with gzip.open(path, "rt", encoding="utf-8") as f:
        frame = pd.read_csv(f, parse_dates=["Date"])
    return frame


def read_ledger(batch: int, symbol: str) -> list[dict]:
    path = LEDGER_ROOT / f"BATCH_{batch:02d}_{symbol}_FIRST_OBSERVED.csv.gz"
    if not path.exists():
        raise FileNotFoundError(path)
    with gzip.open(path, "rt", encoding="utf-8") as f:
        df = pd.read_csv(f)
    df["date"] = pd.to_datetime(df["date"])
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


def truthy(v) -> bool:
    if isinstance(v, bool):
        return v
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return False
    return str(v).strip().lower() in {"true", "1", "yes"}


def finite_float(v) -> float | None:
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    return x if np.isfinite(x) else None


def h1(row: dict | None) -> bool:
    if not row:
        return False
    return (
        str(row.get("color", "")).upper() == "GREEN"
        and truthy(row.get("lower"))
        and str(row.get("lower_subtype", "")).upper() == "FULL_BELOW"
    )


def green_close_below(row: dict | None) -> bool:
    if not row or str(row.get("color", "")).upper() != "GREEN":
        return False
    close = finite_float(row.get("close"))
    zd1 = finite_float(row.get("ZD1"))
    return close is not None and zd1 is not None and close < zd1


def build_exit_arrays(prep: dict, ledger: list[dict]) -> tuple[dict[str, np.ndarray], dict[str, int]]:
    dates = [pd.Timestamp(x) for x in prep["dates"]]
    by_date = {pd.Timestamp(x["date"]): x for x in ledger}
    n = len(dates)
    arr_h1 = np.zeros(n, dtype=np.bool_)
    arr_h2 = np.zeros(n, dtype=np.bool_)
    signal_h1 = 0
    signal_h2 = 0

    # Execution bar j uses the signal confirmed on bar j-1.
    for j in range(1, n):
        cur = by_date.get(dates[j - 1])
        h1_now = h1(cur)
        if h1_now:
            arr_h1[j] = True
            signal_h1 += 1

        if j >= 2:
            prev = by_date.get(dates[j - 2])
            h2_now = green_close_below(cur) and green_close_below(prev)
            if h2_now:
                arr_h2[j] = True
                signal_h2 += 1

    return {
        "BASELINE": np.zeros(n, dtype=np.bool_),
        "H1_GREEN_LOWER_FULL_BELOW": arr_h1,
        "H2_GREEN_TWO_CLOSES_BELOW_ZD1": arr_h2,
        "H3_H1_OR_H2": np.logical_or(arr_h1, arr_h2),
    }, {
        "H1_signal_bars": int(signal_h1),
        "H2_signal_bars": int(signal_h2),
        "H3_signal_bars": int(np.logical_or(arr_h1, arr_h2).sum()),
    }


def simulate(prep: dict, policy: core.Policy, friction_bps: float, hard_exit: np.ndarray) -> dict:
    opens = prep["opens"]
    closes = prep["closes"]
    actions = prep["actions"][policy.resolution]
    n = len(opens)
    if len(hard_exit) != n:
        raise RuntimeError("hard-exit array length mismatch")

    cash = 1.0
    shares = 0.0
    turnover = 0.0
    changes = 0
    invested_days = 0
    hard_exit_executions = 0
    curve = np.empty(n, dtype=float)
    cost_rate = friction_bps / 10000.0

    for j in range(n):
        op = float(opens[j])
        cl = float(closes[j])
        pre_equity = cash + shares * op
        if pre_equity <= 0:
            raise RuntimeError("non-positive equity")
        position_value = shares * op
        current_fraction = position_value / pre_equity
        order_value = 0.0

        if bool(hard_exit[j]) and shares > 1e-14:
            order_value = -position_value
            hard_exit_executions += 1
        else:
            action = int(actions[j])
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
            elif action == 4 and shares > 0:  # ordinary SELL
                order_value = -position_value * policy.sell_reduction
            # WAIT is HOLD in the promoted policy, so no order.

        if order_value > 1e-14:
            max_buy = max(0.0, cash / (1.0 + cost_rate))
            order_value = min(order_value, max_buy)
        elif order_value < -1e-14:
            order_value = max(order_value, -position_value)

        if abs(order_value) > 1e-14:
            cost = abs(order_value) * cost_rate
            shares += order_value / op
            cash -= order_value + cost
            turnover += abs(order_value) / pre_equity
            changes += 1
            if shares <= 1e-12:
                shares = 0.0

        curve[j] = cash + shares * cl
        if shares > 1e-12:
            invested_days += 1

    final_equity = float(curve[-1])
    days = max(1, (pd.Timestamp(prep["dates"][-1]) - pd.Timestamp(prep["dates"][0])).days)
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
        "hard_exit_executions": int(hard_exit_executions),
    }


def compact(v: dict) -> dict:
    return {
        k: v[k] for k in (
            "total_return", "cagr", "max_drawdown", "calmar", "turnover",
            "position_changes", "time_in_market", "hard_exit_executions"
        )
    }


def portfolio(per_symbol: dict[str, dict], prepared: dict[str, dict]) -> dict:
    common_dates, common_idx = core.prepare_common_alignment(prepared)
    m = core.portfolio_metrics_fast(per_symbol, common_dates, common_idx)
    m["hard_exit_executions_sum"] = int(sum(v["hard_exit_executions"] for v in per_symbol.values()))
    m["common_start"] = common_dates[0]
    m["common_end"] = common_dates[-1]
    return m


def delta_metrics(candidate: dict, baseline: dict) -> dict:
    return {
        "total_return": candidate["total_return"] - baseline["total_return"],
        "cagr": candidate["cagr"] - baseline["cagr"],
        "max_drawdown": candidate["max_drawdown"] - baseline["max_drawdown"],
        "calmar": candidate["calmar"] - baseline["calmar"],
        "turnover_mean": candidate["turnover_mean"] - baseline["turnover_mean"],
        "time_in_market_mean": candidate["time_in_market_mean"] - baseline["time_in_market_mean"],
    }


def pct(x: float) -> str:
    return f"{100*x:.2f}%"


def num(x: float) -> str:
    return f"{x:.3f}"


def main() -> None:
    policy = load_promoted_policy()

    prepared: dict[str, dict] = {}
    exit_arrays: dict[str, dict[str, np.ndarray]] = {}
    trigger_counts: dict[str, dict] = {}
    symbol_batch: dict[str, int] = {}

    for batch, symbols in core.BATCHES.items():
        for symbol in symbols:
            frame = read_frame(batch, symbol)
            ledger = read_ledger(batch, symbol)
            prep = core.prepare_fast_symbol(frame, ledger)
            arrays, triggers = build_exit_arrays(prep, ledger)
            prepared[symbol] = prep
            exit_arrays[symbol] = arrays
            trigger_counts[symbol] = triggers
            symbol_batch[symbol] = batch

    if len(prepared) != 79:
        raise RuntimeError(f"Expected 79 stocks, got {len(prepared)}")

    simulations: dict[str, dict[str, dict[str, dict]]] = {"5bps": {}, "10bps": {}}
    for friction_name, bps in (("5bps", 5.0), ("10bps", 10.0)):
        for variant in VARIANTS:
            simulations[friction_name][variant] = {
                symbol: simulate(prepared[symbol], policy, bps, exit_arrays[symbol][variant])
                for symbol in prepared
            }

    batch_results: dict[str, dict[str, dict[str, dict]]] = {"5bps": {}, "10bps": {}}
    for friction_name in ("5bps", "10bps"):
        for variant in VARIANTS:
            batch_results[friction_name][variant] = {}
            for batch, symbols in core.BATCHES.items():
                sub_prepared = {s: prepared[s] for s in symbols}
                sub_results = {s: simulations[friction_name][variant][s] for s in symbols}
                batch_results[friction_name][variant][str(batch)] = portfolio(sub_results, sub_prepared)

    all79: dict[str, dict[str, dict]] = {"5bps": {}, "10bps": {}}
    for friction_name in ("5bps", "10bps"):
        for variant in VARIANTS:
            all79[friction_name][variant] = portfolio(
                simulations[friction_name][variant], prepared
            )

    comparisons: dict[str, dict] = {}
    base_batches = batch_results["5bps"]["BASELINE"]
    for variant in VARIANTS[1:]:
        deltas = {}
        improved_calmar = 0
        improved_cagr = 0
        improved_mdd = 0
        for b in map(str, range(1, 9)):
            d = delta_metrics(batch_results["5bps"][variant][b], base_batches[b])
            deltas[b] = d
            improved_calmar += d["calmar"] > 0
            improved_cagr += d["cagr"] > 0
            # MaxDD is negative, so a positive delta means a smaller drawdown magnitude.
            improved_mdd += d["max_drawdown"] > 0
        comparisons[variant] = {
            "batch_deltas_vs_baseline_5bps": deltas,
            "batches_improved_calmar": int(improved_calmar),
            "batches_improved_cagr": int(improved_cagr),
            "batches_improved_max_drawdown": int(improved_mdd),
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

    baseline_summary = {
        "median_batch_calmar": statistics.median(
            batch_results["5bps"]["BASELINE"][str(b)]["calmar"] for b in range(1, 9)
        ),
        "median_batch_cagr": statistics.median(
            batch_results["5bps"]["BASELINE"][str(b)]["cagr"] for b in range(1, 9)
        ),
        "median_batch_max_drawdown": statistics.median(
            batch_results["5bps"]["BASELINE"][str(b)]["max_drawdown"] for b in range(1, 9)
        ),
        "median_batch_10bps_calmar": statistics.median(
            batch_results["10bps"]["BASELINE"][str(b)]["calmar"] for b in range(1, 9)
        ),
    }

    per_symbol = {}
    for symbol in prepared:
        per_symbol[symbol] = {
            "batch": symbol_batch[symbol],
            "trigger_counts": trigger_counts[symbol],
            "5bps": {v: compact(simulations["5bps"][v][symbol]) for v in VARIANTS},
            "10bps": {v: compact(simulations["10bps"][v][symbol]) for v in VARIANTS},
        }

    output = {
        "meta": {
            "study": "SLTD_V6_HARD_EXIT_STUDY_V1",
            "status": "COMPLETE",
            "universe_count": 79,
            "batches": list(range(1, 9)),
            "formal_window": "2020-01-02..2026-09-30",
            "representation": "FIRST_OBSERVED",
            "execution": "SIGNAL_CLOSE_TO_NEXT_AVAILABLE_OPEN",
            "ordinary_position_policy": policy.id,
            "hard_exit_priority": "HARD_EXIT_OVERRIDES_ORDINARY_ACTION",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        },
        "variants": {
            "BASELINE": "No Hard Exit.",
            "H1_GREEN_LOWER_FULL_BELOW": "GREEN + LOWER event + FULL_BELOW -> next open 100% exit.",
            "H2_GREEN_TWO_CLOSES_BELOW_ZD1": "Two consecutive GREEN bars with Close < ZD1 -> next open 100% exit.",
            "H3_H1_OR_H2": "Either H1 or H2 -> next open 100% exit.",
        },
        "baseline_summary": baseline_summary,
        "batch_results": batch_results,
        "all79_equal_weight": all79,
        "comparisons": comparisons,
        "per_symbol": per_symbol,
    }
    OUT_JSON.write_text(json.dumps(output, indent=2), encoding="utf-8")

    lines = [
        "# SLTD V6 Hard Exit Study v1 — 79 Stocks",
        "",
        "Status: **COMPLETE**",
        "",
        f"Ordinary policy held fixed: `{policy.id}`",
        "",
        "Hard Exit executes at the next available open and overrides ordinary actions.",
        "",
        "## 5 bps — all 79 equal-weight portfolio",
        "",
        "| Variant | Return | CAGR | MaxDD | Calmar | Turnover | Time in market | Hard exits |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for v in VARIANTS:
        m = all79["5bps"][v]
        lines.append(
            f"| {v} | {pct(m['total_return'])} | {pct(m['cagr'])} | {pct(m['max_drawdown'])} | "
            f"{num(m['calmar'])} | {m['turnover_mean']:.2f} | {pct(m['time_in_market_mean'])} | "
            f"{m['hard_exit_executions_sum']} |"
        )

    lines += [
        "",
        "## 5 bps — batch Calmar",
        "",
        "| Variant | B1 | B2 | B3 | B4 | B5 | B6 | B7 | B8 | Median |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for v in VARIANTS:
        vals = [batch_results["5bps"][v][str(b)]["calmar"] for b in range(1, 9)]
        lines.append(
            "| " + v + " | " + " | ".join(f"{x:.3f}" for x in vals)
            + f" | {statistics.median(vals):.3f} |"
        )

    lines += [
        "",
        "## 5 bps — batch CAGR",
        "",
        "| Variant | B1 | B2 | B3 | B4 | B5 | B6 | B7 | B8 | Median |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for v in VARIANTS:
        vals = [batch_results["5bps"][v][str(b)]["cagr"] for b in range(1, 9)]
        lines.append(
            "| " + v + " | " + " | ".join(pct(x) for x in vals)
            + f" | {pct(statistics.median(vals))} |"
        )

    lines += [
        "",
        "## 5 bps — batch MaxDD",
        "",
        "| Variant | B1 | B2 | B3 | B4 | B5 | B6 | B7 | B8 | Median |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for v in VARIANTS:
        vals = [batch_results["5bps"][v][str(b)]["max_drawdown"] for b in range(1, 9)]
        lines.append(
            "| " + v + " | " + " | ".join(pct(x) for x in vals)
            + f" | {pct(statistics.median(vals))} |"
        )

    lines += [
        "",
        "## Comparison versus BASELINE",
        "",
        "| Hard Exit | Calmar improved batches | CAGR improved batches | MaxDD improved batches | Median Calmar | Median CAGR | Median MaxDD | Median 10bps Calmar |",
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
        "This is a fixed-hypothesis comparison. No Hard Exit threshold was tuned after seeing results.",
        "",
        "`SLTD_V6_HARD_EXIT_STUDY_V1 = COMPLETE`",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
