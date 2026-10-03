#!/usr/bin/env python3
"""SLTD V7 Profit Protection Study v1.

Finite, pre-frozen candidates:
- V7_BASELINE
- P1_STRUCT_TREND_FAILURE
- P2_CHANDELIER_22_3_PROFIT
- P3_BS_SCALEOUT_25
- P4_BS25_PLUS_CHANDELIER

The frozen V7 12-rule candidate, ordinary SELL and C2 remain unchanged.
All historical SLTD/XMA inputs are FIRST_OBSERVED.
"""
from __future__ import annotations

import json
import math
import statistics
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
PHASE8 = ROOT / "research" / "ssss_reboot_v1" / "phase8"
PHASE9 = ROOT / "research" / "ssss_reboot_v1" / "phase9"
sys.path.insert(0, str(PHASE8))

import sltd_e7b_89_stock_validation_v1 as base89  # noqa: E402

combo = base89.combo

OUT_JSON = PHASE9 / "SLTD_V7_PROFIT_PROTECTION_RESULT_v1.json"
OUT_MD = PHASE9 / "SLTD_V7_PROFIT_PROTECTION_RESULT_v1.md"
FROZEN_E7B_RESULT = PHASE8 / "SLTD_E7B_89_STOCK_VALIDATION_RESULT_v1.json"

FORMAL_START = base89.FORMAL_START
FORMAL_END = base89.FORMAL_END
PRIOR79 = base89.PRIOR79
OOS10 = base89.OOS10
ALL89 = base89.ALL89
CANDIDATE = "DROP_B3_S1_S3"

VARIANTS = (
    "V7_BASELINE",
    "P1_STRUCT_TREND_FAILURE",
    "P2_CHANDELIER_22_3_PROFIT",
    "P3_BS_SCALEOUT_25",
    "P4_BS25_PLUS_CHANDELIER",
)

YEARS = list(range(2020, 2027))
ERAS = {
    "EARLY_2020_2021": ("2020-01-02", "2021-12-31"),
    "MIDDLE_2022_2023": ("2022-01-01", "2023-12-31"),
    "LATE_2024_2026Q3": ("2024-01-01", "2026-09-30"),
}


def _finite(x) -> bool:
    try:
        return math.isfinite(float(x))
    except (TypeError, ValueError):
        return False


def wilder_atr(high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int = 22) -> np.ndarray:
    n = len(close)
    tr = np.empty(n, dtype=float)
    tr[0] = float(high[0] - low[0])
    for i in range(1, n):
        tr[i] = max(
            float(high[i] - low[i]),
            abs(float(high[i] - close[i - 1])),
            abs(float(low[i] - close[i - 1])),
        )
    out = np.full(n, np.nan, dtype=float)
    if n < period:
        return out
    out[period - 1] = float(np.mean(tr[:period]))
    for i in range(period, n):
        out[i] = ((period - 1) * out[i - 1] + tr[i]) / period
    return out


def rolling_high(values: np.ndarray, period: int = 22) -> np.ndarray:
    out = np.full(len(values), np.nan, dtype=float)
    for i in range(period - 1, len(values)):
        out[i] = float(np.max(values[i - period + 1:i + 1]))
    return out


def bs_new_cross(ledger: list[dict], i: int) -> bool:
    if i <= 0:
        return False
    cur, prev = ledger[i], ledger[i - 1]
    if not all(_finite(cur.get(k)) for k in ("high", "BS")):
        return False
    if not all(_finite(prev.get(k)) for k in ("high", "BS")):
        return False
    return float(cur["high"]) >= float(cur["BS"]) and float(prev["high"]) < float(prev["BS"])


def prepare_symbol(frame: pd.DataFrame, ledger: list[dict]) -> dict:
    v7 = combo.prepare_symbol(frame, ledger)
    dates_all = pd.to_datetime(frame["Date"]).dt.tz_localize(None)
    mask = (dates_all >= FORMAL_START) & (dates_all <= FORMAL_END)
    idx = np.flatnonzero(mask.to_numpy())
    if len(idx) < 2:
        raise RuntimeError("insufficient formal bars")

    formal_dates = [pd.Timestamp(dates_all.iloc[i]).strftime("%Y-%m-%d") for i in idx]
    if formal_dates != list(v7["dates"]):
        raise RuntimeError("formal date alignment mismatch")

    high_all = frame["High"].astype(float).to_numpy()
    low_all = frame["Low"].astype(float).to_numpy()
    close_all = frame["Close"].astype(float).to_numpy()
    atr_all = wilder_atr(high_all, low_all, close_all, 22)
    hh_all = rolling_high(high_all, 22)

    rows = [ledger[i] for i in idx]
    bs_cross = np.asarray([bs_new_cross(ledger, i) for i in idx], dtype=np.bool_)

    return {
        "dates": formal_dates,
        "opens": frame["Open"].astype(float).to_numpy()[idx],
        "highs": high_all[idx],
        "lows": low_all[idx],
        "closes": close_all[idx],
        "rows": rows,
        "actions": v7["actions"][CANDIDATE],
        "c2": v7["c2"],
        "atr22": atr_all[idx],
        "hh22": hh_all[idx],
        "chandelier": hh_all[idx] - 3.0 * atr_all[idx],
        "bs_cross": bs_cross,
    }


def cycle_summary(cycles: list[dict]) -> dict:
    positive = [c for c in cycles if c["peak_gain"] > 1e-12]
    captures = [c["capture_ratio"] for c in positive]
    givebacks = [c["giveback"] for c in positive]
    giveback_ratios = [c["giveback_ratio"] for c in positive]
    return {
        "completed_cycles": len(cycles),
        "positive_peak_cycles": len(positive),
        "median_capture_ratio": float(statistics.median(captures)) if captures else None,
        "median_giveback": float(statistics.median(givebacks)) if givebacks else None,
        "median_giveback_ratio": float(statistics.median(giveback_ratios)) if giveback_ratios else None,
        "mean_giveback_ratio": float(np.mean(giveback_ratios)) if giveback_ratios else None,
    }


def simulate(prep: dict, variant: str, friction_bps: float) -> dict:
    if variant not in VARIANTS:
        raise ValueError(variant)

    opens = prep["opens"]
    highs = prep["highs"]
    closes = prep["closes"]
    rows = prep["rows"]
    actions = prep["actions"]
    c2 = prep["c2"]
    chandelier = prep["chandelier"]
    bs_cross = prep["bs_cross"]
    n = len(opens)

    cash = 1.0
    shares = 0.0
    avg_cost: float | None = None
    v7_armed = False
    trend_armed = False
    pending_overlay: dict | None = None

    turnover = 0.0
    changes = 0
    invested = 0
    curve = np.empty(n, dtype=float)
    counts = Counter()
    cost_rate = float(friction_bps) / 10000.0

    cycle_start_equity: float | None = None
    cycle_peak_equity: float | None = None
    cycle_start_date: str | None = None
    cycles: list[dict] = []

    for j in range(n):
        op = float(opens[j])
        hi = float(highs[j])
        cl = float(closes[j])
        pre = cash + shares * op
        if pre <= 0:
            raise RuntimeError("non-positive equity")

        shares_before = shares
        pos = shares * op
        frac = pos / pre if pre > 0 else 0.0

        hard_c2 = bool(shares > 1e-14 and v7_armed and bool(c2[j]))
        ordinary = int(actions[j])
        source = "NONE"
        order = 0.0
        overlay = pending_overlay
        pending_overlay = None

        # Risk priority is intentionally frozen before the run.
        if hard_c2:
            source = "V7_C2"
            order = -pos
        elif overlay is not None and shares > 1e-14:
            if overlay["kind"] == "EXIT":
                source = overlay["reason"]
                order = -pos
            elif overlay["kind"] == "SCALE_25":
                source = overlay["reason"]
                order = -0.25 * pos
            else:
                raise RuntimeError(f"unknown overlay kind {overlay['kind']}")
        else:
            if ordinary == 1:
                source = "V7_BUY"
                target = 0.25 if shares <= 1e-14 else min(1.0, frac + 0.25)
                order = max(0.0, target * pre - pos)
            elif ordinary == 4 and shares > 1e-14:
                source = "V7_SELL"
                order = -0.25 * pos

        if order > 1e-14:
            order = min(order, max(0.0, cash / (1.0 + cost_rate)))
        elif order < -1e-14:
            order = max(order, -pos)

        executed = abs(order) > 1e-14
        buy_executed = False
        full_exit_executed = False

        if executed:
            fee = abs(order) * cost_rate
            if order > 0:
                old_shares = shares
                new_shares = order / op
                old_basis = 0.0 if avg_cost is None else avg_cost * old_shares
                new_basis = order + fee
                shares += new_shares
                avg_cost = (old_basis + new_basis) / shares
                buy_executed = True
            else:
                shares += order / op

            cash -= order + fee
            turnover += abs(order) / pre
            changes += 1
            counts[source + "_EXEC"] += 1

            if shares <= 1e-12:
                shares = 0.0
                avg_cost = None
                full_exit_executed = shares_before > 1e-12

        # Exact frozen V7 C2 state semantics.
        if source == "V7_C2" and executed:
            v7_armed = False
        elif source == "V7_SELL" and executed:
            v7_armed = True
        elif source == "V7_BUY" and executed:
            v7_armed = False
        elif full_exit_executed:
            v7_armed = False

        if buy_executed:
            trend_armed = False
        if full_exit_executed:
            trend_armed = False

        # Start/finish completed-position cycles.
        if shares_before <= 1e-14 and shares > 1e-12 and buy_executed:
            cycle_start_equity = pre
            cycle_peak_equity = cash + shares * hi
            cycle_start_date = prep["dates"][j]

        if full_exit_executed and cycle_start_equity is not None:
            exit_equity = cash
            peak_equity = max(cycle_peak_equity or cycle_start_equity, cycle_start_equity)
            peak_gain = peak_equity / cycle_start_equity - 1.0
            exit_gain = exit_equity / cycle_start_equity - 1.0
            giveback = max(0.0, peak_gain - exit_gain)
            cycles.append({
                "start": cycle_start_date,
                "end": prep["dates"][j],
                "peak_gain": float(peak_gain),
                "exit_gain": float(exit_gain),
                "giveback": float(giveback),
                "capture_ratio": float(exit_gain / peak_gain) if peak_gain > 1e-12 else None,
                "giveback_ratio": float(giveback / peak_gain) if peak_gain > 1e-12 else None,
                "exit_source": source,
            })
            cycle_start_equity = None
            cycle_peak_equity = None
            cycle_start_date = None

        if shares > 1e-12 and cycle_start_equity is not None:
            mark_high = cash + shares * hi
            if cycle_peak_equity is None or mark_high > cycle_peak_equity:
                cycle_peak_equity = mark_high

        curve[j] = cash + shares * cl
        if shares > 1e-12:
            invested += 1

        # Build next-open overlay from the currently completed bar.
        if shares <= 1e-12 or avg_cost is None:
            continue

        row = rows[j]
        close_profit = cl > avg_cost
        p1 = variant == "P1_STRUCT_TREND_FAILURE"
        p2 = variant in ("P2_CHANDELIER_22_3_PROFIT", "P4_BS25_PLUS_CHANDELIER")
        p3 = variant in ("P3_BS_SCALEOUT_25", "P4_BS25_PLUS_CHANDELIER")

        # Full-exit overlays take priority over scale-out.
        if p1:
            was_armed = trend_armed
            if (
                was_armed
                and _finite(row.get("ZK1"))
                and float(row["close"]) < float(row["ZK1"])
                and close_profit
            ):
                pending_overlay = {"kind": "EXIT", "reason": "P1_TREND_FAILURE"}
                counts["P1_TREND_FAILURE_SIGNAL"] += 1
            elif (
                not was_armed
                and str(row.get("color") or "").upper() == "BLUE"
                and bool(row.get("upper"))
                and close_profit
            ):
                trend_armed = True
                counts["P1_ARM"] += 1

        if pending_overlay is None and p2:
            stop = float(chandelier[j]) if math.isfinite(float(chandelier[j])) else math.nan
            if math.isfinite(stop) and stop > avg_cost and cl < stop:
                pending_overlay = {"kind": "EXIT", "reason": "P2_CHANDELIER_EXIT"}
                counts["P2_CHANDELIER_SIGNAL"] += 1

        if pending_overlay is None and p3:
            bs = row.get("BS")
            if bool(bs_cross[j]) and _finite(bs) and float(bs) > avg_cost:
                pending_overlay = {"kind": "SCALE_25", "reason": "P3_BS_SCALE25"}
                counts["P3_BS_SCALE25_SIGNAL"] += 1

    out = base89.metric_block(list(prep["dates"]), curve)
    out.update({
        "dates": list(prep["dates"]),
        "curve": curve,
        "turnover": float(turnover),
        "position_changes": int(changes),
        "time_in_market": float(invested / n),
        "trigger_counts": dict(counts),
        "cycle_summary": cycle_summary(cycles),
        "_cycles": cycles,
    })
    return out


def subset(per: dict[str, dict], symbols: list[str]) -> dict[str, dict]:
    return {s: per[s] for s in symbols}


def aggregate_cycle_metrics(per: dict[str, dict]) -> dict:
    cycles = []
    for r in per.values():
        cycles.extend(r.get("_cycles") or [])
    return cycle_summary(cycles)


def portfolio_with_cycles(per: dict[str, dict]) -> dict:
    out = base89.portfolio(per)
    out["cycle_summary"] = aggregate_cycle_metrics(per)
    return out


def compare_with_cycles(candidate: dict[str, dict], baseline: dict[str, dict]) -> dict:
    out = base89.compare(candidate, baseline)
    eligible = 0
    better = 0
    for s in candidate:
        a = candidate[s]["cycle_summary"].get("median_giveback_ratio")
        b = baseline[s]["cycle_summary"].get("median_giveback_ratio")
        if a is None or b is None:
            continue
        eligible += 1
        if a < b:
            better += 1
    out["giveback_ratio_better"] = better
    out["giveback_ratio_eligible"] = eligible
    return out


def compact(r: dict) -> dict:
    keys = (
        "total_return", "cagr", "max_drawdown", "calmar",
        "turnover", "position_changes", "time_in_market",
    )
    return {k: r[k] for k in keys} | {
        "trigger_counts": r["trigger_counts"],
        "cycle_summary": r["cycle_summary"],
    }


def pct(x: float) -> str:
    return f"{100.0 * float(x):.2f}%"


def ratio_text(x) -> str:
    return "NA" if x is None else f"{100.0 * float(x):.1f}%"


def classify(candidate: dict, baseline: dict, oos_candidate: dict, oos_baseline: dict) -> dict:
    ccy = candidate["cycle_summary"]
    bcy = baseline["cycle_summary"]
    ocy = oos_candidate["cycle_summary"]
    obcy = oos_baseline["cycle_summary"]

    return_retention = (
        candidate["total_return"] / baseline["total_return"]
        if baseline["total_return"] > 1e-12 else math.nan
    )
    gates = {
        "all89_calmar_improves": candidate["calmar"] > baseline["calmar"],
        "all89_maxdd_improves": candidate["max_drawdown"] > baseline["max_drawdown"],
        "all89_return_retention_ge_90pct": return_retention >= 0.90,
        "all89_giveback_ratio_improves": (
            ccy["median_giveback_ratio"] is not None
            and bcy["median_giveback_ratio"] is not None
            and ccy["median_giveback_ratio"] < bcy["median_giveback_ratio"]
        ),
        "oos10_maxdd_not_worse": oos_candidate["max_drawdown"] >= oos_baseline["max_drawdown"],
        "oos10_giveback_ratio_improves": (
            ocy["median_giveback_ratio"] is not None
            and obcy["median_giveback_ratio"] is not None
            and ocy["median_giveback_ratio"] < obcy["median_giveback_ratio"]
        ),
    }
    if all(gates.values()):
        label = "ADMIT_CANDIDATE"
    elif gates["all89_maxdd_improves"] and gates["all89_giveback_ratio_improves"]:
        label = "MIXED_NOT_ADMITTED"
    else:
        label = "REJECTED_NOT_ADMITTED"
    return {
        "classification": label,
        "return_retention": float(return_retention),
        "gates": gates,
    }


def main() -> None:
    frames, ledgers, groups = base89.load_universe()
    prepared = {s: prepare_symbol(frames[s], ledgers[s]) for s in ALL89}

    sims = {
        friction: {variant: {} for variant in VARIANTS}
        for friction in ("5bps", "10bps")
    }
    for friction, bps in (("5bps", 5.0), ("10bps", 10.0)):
        for n, s in enumerate(ALL89, 1):
            for variant in VARIANTS:
                sims[friction][variant][s] = simulate(prepared[s], variant, bps)
            print("SIM_PASS", friction, n, 89, s, flush=True)

    # Exact baseline parity against the already frozen 89-stock V7 validation.
    frozen = json.loads(FROZEN_E7B_RESULT.read_text(encoding="utf-8"))
    parity_errors = []
    for friction in ("5bps", "10bps"):
        for s in ALL89:
            expected = frozen["per_symbol"][s][friction]["V7"]
            actual = sims[friction]["V7_BASELINE"][s]
            for k in ("total_return", "cagr", "max_drawdown", "calmar"):
                if not math.isclose(float(actual[k]), float(expected[k]), rel_tol=1e-10, abs_tol=1e-10):
                    parity_errors.append((friction, s, k, actual[k], expected[k]))
    if parity_errors:
        raise RuntimeError(f"V7 baseline parity failed: {parity_errors[:10]}")
    print("V7_89_PARITY_PASS", flush=True)

    aggregates: dict = {}
    comparisons: dict = {}
    classifications: dict = {}
    yearly: dict = {}
    eras: dict = {}
    trigger_totals: dict = {}

    for friction in ("5bps", "10bps"):
        aggregates[friction] = {}
        yearly[friction] = {}
        eras[friction] = {}
        for variant in VARIANTS:
            per = sims[friction][variant]
            aggregates[friction][variant] = {
                "all89": portfolio_with_cycles(per),
                "prior79": portfolio_with_cycles(subset(per, PRIOR79)),
                "oos10": portfolio_with_cycles(subset(per, OOS10)),
            }
            yearly[friction][variant] = {
                str(y): base89.slice_portfolio(per, f"{y}-01-01", f"{y}-12-31")
                for y in YEARS
            }
            eras[friction][variant] = {
                era: base89.slice_portfolio(per, a, b)
                for era, (a, b) in ERAS.items()
            }
            total = Counter()
            for r in per.values():
                total.update(r["trigger_counts"])
            trigger_totals.setdefault(friction, {})[variant] = dict(total)

        base = sims[friction]["V7_BASELINE"]
        comparisons[friction] = {}
        for variant in VARIANTS[1:]:
            comparisons[friction][variant] = {
                "all89": compare_with_cycles(sims[friction][variant], base),
                "prior79": compare_with_cycles(
                    subset(sims[friction][variant], PRIOR79),
                    subset(base, PRIOR79),
                ),
                "oos10": compare_with_cycles(
                    subset(sims[friction][variant], OOS10),
                    subset(base, OOS10),
                ),
            }

    for variant in VARIANTS[1:]:
        classifications[variant] = classify(
            aggregates["5bps"][variant]["all89"],
            aggregates["5bps"]["V7_BASELINE"]["all89"],
            aggregates["5bps"][variant]["oos10"],
            aggregates["5bps"]["V7_BASELINE"]["oos10"],
        )

    per_symbol = {
        s: {
            "group": groups[s],
            friction: {
                variant: compact(sims[friction][variant][s])
                for variant in VARIANTS
            }
            for friction in ("5bps", "10bps")
        }
        for s in ALL89
    }

    aapl = {
        friction: {
            variant: compact(sims[friction][variant]["AAPL"])
            for variant in VARIANTS
        }
        for friction in ("5bps", "10bps")
    }

    output = {
        "meta": {
            "study": "SLTD_V7_PROFIT_PROTECTION_STUDY_V1",
            "status": "COMPLETE",
            "protocol_status": "FROZEN_BEFORE_RUN",
            "universe_count": 89,
            "prior79_count": 79,
            "oos10_count": 10,
            "formal_window": "2020-01-02..2026-09-30",
            "timeframe": "1d",
            "representation": "FIRST_OBSERVED",
            "execution": "SIGNAL_CLOSE_TO_NEXT_AVAILABLE_OPEN",
            "frictions_bps": [5.0, 10.0],
            "v7_frozen_commit": "5f9ea4d8fa434b54afdbf32a1cb21ef2f3cb4042",
            "candidate": CANDIDATE,
            "variants": list(VARIANTS),
            "v7_89_parity": "PASS",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        },
        "aggregates": aggregates,
        "comparisons": comparisons,
        "classifications": classifications,
        "yearly": yearly,
        "eras": eras,
        "trigger_totals": trigger_totals,
        "aapl": aapl,
        "per_symbol": per_symbol,
    }
    OUT_JSON.write_text(json.dumps(output, indent=2), encoding="utf-8")

    base = aggregates["5bps"]["V7_BASELINE"]["all89"]
    lines = [
        "# SLTD V7 Profit Protection Study v1",
        "",
        "Status: **COMPLETE**",
        "",
        "Frozen V7 BUY/HOLD/WAIT / ordinary SELL / C2: **UNCHANGED**.",
        "",
        "Representation: **FIRST_OBSERVED**.  Window: **2020-01-02..2026-09-30**.",
        "",
        "Universe: **89 stocks = prior79 + OOS10**. Primary friction: **5 bps**; stress: **10 bps**.",
        "",
        "Frozen V7 89-stock parity: **PASS**.",
        "",
        "## All-89 equal-weight portfolio — 5 bps",
        "",
        "| Variant | Return | CAGR | MaxDD | Calmar | Time | Capture | Giveback ratio | Classification |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for variant in VARIANTS:
        m = aggregates["5bps"][variant]["all89"]
        cy = m["cycle_summary"]
        label = "FROZEN_BASELINE" if variant == "V7_BASELINE" else classifications[variant]["classification"]
        lines.append(
            f"| {variant} | {pct(m['total_return'])} | {pct(m['cagr'])} | "
            f"{pct(m['max_drawdown'])} | {m['calmar']:.3f} | "
            f"{pct(m['time_in_market_mean'])} | {ratio_text(cy['median_capture_ratio'])} | "
            f"{ratio_text(cy['median_giveback_ratio'])} | {label} |"
        )

    lines += [
        "",
        "## OOS10 — 5 bps",
        "",
        "| Variant | Return | MaxDD | Calmar | Capture | Giveback ratio |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for variant in VARIANTS:
        m = aggregates["5bps"][variant]["oos10"]
        cy = m["cycle_summary"]
        lines.append(
            f"| {variant} | {pct(m['total_return'])} | {pct(m['max_drawdown'])} | "
            f"{m['calmar']:.3f} | {ratio_text(cy['median_capture_ratio'])} | "
            f"{ratio_text(cy['median_giveback_ratio'])} |"
        )

    lines += [
        "",
        "## Breadth vs V7 — 5 bps",
        "",
        "| Variant | Better Return | Better MaxDD | Better Calmar | Better giveback / eligible |",
        "|---|---:|---:|---:|---:|",
    ]
    for variant in VARIANTS[1:]:
        x = comparisons["5bps"][variant]["all89"]
        lines.append(
            f"| {variant} | {x['better_return']}/89 | {x['better_maxdd']}/89 | "
            f"{x['better_calmar']}/89 | {x['giveback_ratio_better']}/{x['giveback_ratio_eligible']} |"
        )

    lines += [
        "",
        "## Admission gates",
        "",
    ]
    for variant in VARIANTS[1:]:
        x = classifications[variant]
        lines.append(f"### {variant} — **{x['classification']}**")
        lines.append(f"- Return retention vs V7: **{100*x['return_retention']:.1f}%**")
        for k, v in x["gates"].items():
            lines.append(f"- {k}: **{'PASS' if v else 'FAIL'}**")
        lines.append("")

    lines += [
        "## AAPL diagnostic — 5 bps",
        "",
        "| Variant | Return | MaxDD | Calmar | Capture | Giveback ratio |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for variant in VARIANTS:
        r = sims["5bps"][variant]["AAPL"]
        cy = r["cycle_summary"]
        lines.append(
            f"| {variant} | {pct(r['total_return'])} | {pct(r['max_drawdown'])} | "
            f"{r['calmar']:.3f} | {ratio_text(cy['median_capture_ratio'])} | "
            f"{ratio_text(cy['median_giveback_ratio'])} |"
        )

    lines += [
        "",
        "## Closure",
        "",
        "No additional SELL hypothesis is generated from this run.",
        "",
        "`SLTD_V7_PROFIT_PROTECTION_STUDY_V1 = COMPLETE`",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
