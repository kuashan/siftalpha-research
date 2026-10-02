#!/usr/bin/env python3
"""SLTD V7 Rule Ablation + Redundancy Study v1.

Exploratory 79-stock contribution study. Frozen V6 rollback baseline is never modified.
"""
from __future__ import annotations

import gzip
import json
import math
import statistics
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
PHASE7 = ROOT.parent / "phase7"
sys.path.insert(0, str(PHASE7))

import sltd_v6_position_policy_batch_v1 as core  # noqa: E402


DATA_ROOT = PHASE7 / "data_snapshot"
LEDGER_ROOT = PHASE7 / "signal_ledgers"
FROZEN_C2_RESULT = PHASE7 / "SLTD_V6_HARD_EXIT_STUDY_V3_79_STOCKS.json"
OUT_JSON = ROOT / "SLTD_V7_RULE_ABLATION_REDUNDANCY_RESULT_v1.json"
OUT_MD = ROOT / "SLTD_V7_RULE_ABLATION_REDUNDANCY_RESULT_v1.md"

FORMAL_START = pd.Timestamp("2020-01-02")
FORMAL_END = pd.Timestamp("2026-09-30")

RULES = (
    ("BUY_BLUE_21P_LOWER", "BUY"),
    ("BUY_GRAY_4_10_LIGHT_SUPPORT", "BUY"),
    ("BUY_RECENT_BLUE_GRAY_LIGHT_SUPPORT", "BUY"),
    ("BLUE_11_20_LOWER_WICK_ONLY", "BUY"),
    ("NEW_V5_C_GRAY_4_10_LOWER_WICK_ONLY", "BUY"),
    ("CONT_BLUE_11_20_UPPER", "HOLD"),
    ("CONT_BLUE_4_10_UPPER", "HOLD"),
    ("CONT_RECENT_GRAY_BLUE_UPPER", "HOLD"),
    ("NEW_V5_B_BLUE_21P_UPPER_CLOSE_ABOVE", "HOLD"),
    ("AVOID_GREEN_11_20_LOWER", "WAIT"),
    ("GREEN_11_20_LOWER_CLOSE_BELOW", "WAIT"),
    ("SELL_RECENT_BLUE_GRAY_LIGHT_RESIST", "SELL"),
    ("GREEN_4_10_UPPER", "SELL"),
    ("NEW_V5_D_GREEN_11_20_UPPER_WICK_ONLY", "SELL"),
    ("NEW_V5_E_GREEN_11_20_LIGHT_RESIST", "SELL"),
)
RULE_IDS = tuple(x[0] for x in RULES)
RULE_TO_CLASS = dict(RULES)
RULE_SET = set(RULE_IDS)

VARIANTS = ("BASELINE_ALL_15",) + tuple(f"DROP__{r}" for r in RULE_IDS)
DROP_BY_VARIANT = {"BASELINE_ALL_15": None}
DROP_BY_VARIANT.update({f"DROP__{r}": r for r in RULE_IDS})

ACTION_CODE = {None: 0, "BUY": 1, "HOLD": 2, "WAIT": 3, "SELL": 4}
HARD_EXIT_ID = "C2_FULL_CANDLE_BELOW_SLOW_BAND"
ORDINARY_POLICY_ID = "I25_AADD_25_TO_CAP_S25_WHOLD_RNO_CHANGE_MIXED"


def read_frame(batch: int, symbol: str) -> pd.DataFrame:
    path = DATA_ROOT / f"batch_{batch:02d}_stocks" / f"{symbol}.csv.gz"
    if not path.exists():
        raise FileNotFoundError(path)
    with gzip.open(path, "rt", encoding="utf-8") as f:
        frame = pd.read_csv(f, parse_dates=["Date"])
    frame["Date"] = pd.to_datetime(frame["Date"]).dt.tz_localize(None)
    return frame


def read_ledger(batch: int, symbol: str) -> list[dict]:
    path = LEDGER_ROOT / f"BATCH_{batch:02d}_{symbol}_FIRST_OBSERVED.csv.gz"
    if not path.exists():
        raise FileNotFoundError(path)
    with gzip.open(path, "rt", encoding="utf-8") as f:
        df = pd.read_csv(f)
    df["date"] = pd.to_datetime(df["date"]).dt.tz_localize(None)
    rows: list[dict] = []
    for rec in df.to_dict("records"):
        for cls in ("BUY", "HOLD", "WAIT", "SELL"):
            v = rec.get(cls)
            if pd.isna(v) or str(v).strip() == "":
                rec[cls] = []
            else:
                rec[cls] = [x for x in str(v).split("|") if x]
        rows.append(rec)
    return rows


def row_rules(row: dict | None) -> dict[str, list[str]]:
    if not row:
        return {k: [] for k in ("BUY", "HOLD", "WAIT", "SELL")}
    out: dict[str, list[str]] = {}
    for cls in ("BUY", "HOLD", "WAIT", "SELL"):
        out[cls] = [r for r in row.get(cls, []) if r in RULE_SET]
    return out


def resolve_row(row: dict | None, drop_rule: str | None) -> str | None:
    rr = row_rules(row)
    classes = []
    for cls in ("BUY", "HOLD", "WAIT", "SELL"):
        ids = rr[cls]
        if drop_rule is not None:
            ids = [r for r in ids if r != drop_rule]
        if ids:
            classes.append(cls)
    return core.resolve_action(tuple(classes), "NO_CHANGE_MIXED")


def c2_condition(row: dict | None) -> bool:
    if not row or str(row.get("color", "")).upper() != "GREEN":
        return False
    try:
        high = float(row.get("high"))
        gzb4 = float(row.get("GZB4"))
    except (TypeError, ValueError):
        return False
    return math.isfinite(high) and math.isfinite(gzb4) and high < gzb4


def prepare_symbol(frame: pd.DataFrame, ledger: list[dict]) -> dict:
    dates = pd.to_datetime(frame["Date"]).dt.tz_localize(None)
    mask = (dates >= FORMAL_START) & (dates <= FORMAL_END)
    idx = np.flatnonzero(mask.to_numpy())
    if len(idx) < 2:
        raise RuntimeError("insufficient formal-window bars")

    formal_dates = [pd.Timestamp(dates.iloc[i]) for i in idx]
    opens = frame["Open"].astype(float).to_numpy()[idx]
    closes = frame["Close"].astype(float).to_numpy()[idx]
    ledger_by_date = {pd.Timestamp(x["date"]): x for x in ledger}

    action_arrays: dict[str, np.ndarray] = {}
    for variant in VARIANTS:
        drop_rule = DROP_BY_VARIANT[variant]
        arr = np.zeros(len(idx), dtype=np.int8)
        for j in range(1, len(idx)):
            signal = ledger_by_date.get(formal_dates[j - 1])
            arr[j] = ACTION_CODE[resolve_row(signal, drop_rule)]
        action_arrays[variant] = arr

    c2 = np.zeros(len(idx), dtype=np.bool_)
    for j in range(1, len(idx)):
        c2[j] = c2_condition(ledger_by_date.get(formal_dates[j - 1]))

    return {
        "dates": [d.strftime("%Y-%m-%d") for d in formal_dates],
        "date_ts": formal_dates,
        "opens": opens,
        "closes": closes,
        "actions": action_arrays,
        "c2": c2,
        "ledger_by_date": ledger_by_date,
    }


def simulate(prep: dict, variant: str, friction_bps: float) -> dict:
    opens = prep["opens"]
    closes = prep["closes"]
    actions = prep["actions"][variant]
    c2 = prep["c2"]
    n = len(opens)

    cash = 1.0
    shares = 0.0
    turnover = 0.0
    changes = 0
    invested_days = 0
    hard_exit_count = 0
    risk_armed = False
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

        hard = bool(shares > 1e-14 and risk_armed and c2[j])
        action = int(actions[j])
        order_value = 0.0
        ordinary_action = None

        if hard:
            order_value = -position_value
        else:
            ordinary_action = action
            if action == 1:  # BUY
                if shares <= 1e-14:
                    desired_fraction = 0.25
                else:
                    desired_fraction = min(1.0, current_fraction + 0.25)
                desired_fraction = max(current_fraction, desired_fraction)
                order_value = desired_fraction * pre_equity - position_value
            elif action == 4 and shares > 0:  # SELL
                order_value = -position_value * 0.25
            # HOLD / WAIT / none are no-order in the frozen policy.

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
            risk_armed = False
        elif executed and ordinary_action == 4 and order_value < 0:
            risk_armed = True
        elif executed and ordinary_action == 1 and order_value > 0:
            risk_armed = False

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
        "hard_exit_count": int(hard_exit_count),
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


def metric_delta(candidate: dict, baseline: dict) -> dict:
    return {
        "total_return": candidate["total_return"] - baseline["total_return"],
        "cagr": candidate["cagr"] - baseline["cagr"],
        "max_drawdown": candidate["max_drawdown"] - baseline["max_drawdown"],
        "calmar": candidate["calmar"] - baseline["calmar"],
        "turnover_mean": candidate["turnover_mean"] - baseline["turnover_mean"],
        "time_in_market_mean": candidate["time_in_market_mean"] - baseline["time_in_market_mean"],
        "hard_exit_count_sum": candidate["hard_exit_count_sum"] - baseline["hard_exit_count_sum"],
    }


def overlap_analysis(prepared: dict[str, dict]) -> dict:
    occurrence = Counter()
    sole = Counter()
    same_class_overlap = Counter()
    cross_class_overlap = Counter()
    pair = Counter()
    changed_resolved = Counter()
    total_signal_bars = 0
    any_rule_bars = 0
    mixed_action_bars = 0
    multi_same_class_bars = 0

    for prep in prepared.values():
        for d in prep["date_ts"]:
            row = prep["ledger_by_date"].get(d)
            if not row:
                continue
            total_signal_bars += 1
            rr = row_rules(row)
            present = []
            for cls in ("BUY", "HOLD", "WAIT", "SELL"):
                present.extend(rr[cls])
            present = sorted(set(present))
            if not present:
                continue
            any_rule_bars += 1

            classes_present = [cls for cls in ("BUY", "HOLD", "WAIT", "SELL") if rr[cls]]
            if len(classes_present) > 1:
                mixed_action_bars += 1
            if any(len(rr[cls]) > 1 for cls in ("BUY", "HOLD", "WAIT", "SELL")):
                multi_same_class_bars += 1

            for r in present:
                occurrence[r] += 1
                if len(present) == 1:
                    sole[r] += 1
                cls = RULE_TO_CLASS[r]
                others = [x for x in present if x != r]
                if any(RULE_TO_CLASS[x] == cls for x in others):
                    same_class_overlap[r] += 1
                if any(RULE_TO_CLASS[x] != cls for x in others):
                    cross_class_overlap[r] += 1

            for i in range(len(present)):
                for j in range(i + 1, len(present)):
                    pair[(present[i], present[j])] += 1

            base_resolved = resolve_row(row, None)
            for r in present:
                if resolve_row(row, r) != base_resolved:
                    changed_resolved[r] += 1

    per_rule = {}
    for r in RULE_IDS:
        n = occurrence[r]
        per_rule[r] = {
            "action_class": RULE_TO_CLASS[r],
            "occurrences": int(n),
            "sole_rule_bars": int(sole[r]),
            "same_class_overlap_bars": int(same_class_overlap[r]),
            "cross_class_overlap_bars": int(cross_class_overlap[r]),
            "resolved_action_changed_if_dropped": int(changed_resolved[r]),
            "sole_fraction": float(sole[r] / n) if n else None,
            "same_class_overlap_fraction": float(same_class_overlap[r] / n) if n else None,
            "cross_class_overlap_fraction": float(cross_class_overlap[r] / n) if n else None,
        }

    pairwise = []
    subset_relationships = []
    for (a, b), co in sorted(pair.items(), key=lambda kv: (-kv[1], kv[0])):
        na = occurrence[a]
        nb = occurrence[b]
        union = na + nb - co
        jaccard = co / union if union else 0.0
        p_b_given_a = co / na if na else 0.0
        p_a_given_b = co / nb if nb else 0.0
        item = {
            "rule_a": a,
            "class_a": RULE_TO_CLASS[a],
            "rule_b": b,
            "class_b": RULE_TO_CLASS[b],
            "same_action_class": RULE_TO_CLASS[a] == RULE_TO_CLASS[b],
            "cooccurrence": int(co),
            "jaccard": float(jaccard),
            "p_b_given_a": float(p_b_given_a),
            "p_a_given_b": float(p_a_given_b),
        }
        pairwise.append(item)
        if co >= 5 and (p_b_given_a >= 0.90 or p_a_given_b >= 0.90):
            relation = None
            if p_b_given_a == 1.0 and p_a_given_b == 1.0:
                relation = "EXACT_COINCIDENT"
            elif p_b_given_a == 1.0:
                relation = f"{a}_SUBSET_OF_{b}"
            elif p_a_given_b == 1.0:
                relation = f"{b}_SUBSET_OF_{a}"
            else:
                relation = "NEAR_SUBSET"
            subset_relationships.append({**item, "relationship": relation})

    return {
        "total_formal_signal_rows_examined": int(total_signal_bars),
        "bars_with_any_of_15_rules": int(any_rule_bars),
        "mixed_action_class_bars": int(mixed_action_bars),
        "multi_rule_same_action_class_bars": int(multi_same_class_bars),
        "per_rule": per_rule,
        "pairwise": pairwise,
        "subset_relationships": subset_relationships,
    }


def validate_frozen_baseline(all79: dict) -> dict:
    frozen = json.loads(FROZEN_C2_RESULT.read_text(encoding="utf-8"))
    ref5 = frozen["all79_equal_weight"]["5bps"]["C2_FULL_CANDLE_BELOW_SLOW_BAND"]
    ref10 = frozen["all79_equal_weight"]["10bps"]["C2_FULL_CANDLE_BELOW_SLOW_BAND"]
    checks = {}
    for name, actual, expected in (
        ("5bps", all79["5bps"]["BASELINE_ALL_15"], ref5),
        ("10bps", all79["10bps"]["BASELINE_ALL_15"], ref10),
    ):
        diffs = {}
        for key in ("total_return", "cagr", "max_drawdown", "calmar"):
            diff = float(actual[key] - expected[key])
            diffs[key] = diff
            if abs(diff) > 1e-10:
                raise RuntimeError(
                    f"Frozen baseline mismatch {name} {key}: actual={actual[key]} expected={expected[key]}"
                )
        checks[name] = {"status": "PASS", "diffs": diffs}
    return checks


def pct(x: float) -> str:
    return f"{100*x:.2f}%"


def fmt_signed(x: float, digits: int = 3) -> str:
    return f"{x:+.{digits}f}"


def main() -> None:
    prepared: dict[str, dict] = {}
    batch_of: dict[str, int] = {}
    for batch, symbols in core.BATCHES.items():
        for symbol in symbols:
            frame = read_frame(batch, symbol)
            ledger = read_ledger(batch, symbol)
            prepared[symbol] = prepare_symbol(frame, ledger)
            batch_of[symbol] = batch

    if len(prepared) != 79:
        raise RuntimeError(f"Expected 79 stocks, got {len(prepared)}")

    overlap = overlap_analysis(prepared)

    sims: dict[str, dict[str, dict[str, dict]]] = {"5bps": {}, "10bps": {}}
    for friction_name, bps in (("5bps", 5.0), ("10bps", 10.0)):
        for variant in VARIANTS:
            sims[friction_name][variant] = {
                s: simulate(prepared[s], variant, bps)
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

    baseline_check = validate_frozen_baseline(all79)

    comparisons = {}
    for rule in RULE_IDS:
        variant = f"DROP__{rule}"
        by_friction = {}
        for friction in ("5bps", "10bps"):
            base = all79[friction]["BASELINE_ALL_15"]
            cand = all79[friction][variant]
            by_friction[friction] = metric_delta(cand, base)

        batch_deltas = {}
        counts = {
            "calmar_improved": 0, "calmar_worsened": 0,
            "cagr_improved": 0, "cagr_worsened": 0,
            "maxdd_improved": 0, "maxdd_worsened": 0,
        }
        for b in map(str, range(1, 9)):
            d = metric_delta(
                batch_results["5bps"][variant][b],
                batch_results["5bps"]["BASELINE_ALL_15"][b],
            )
            batch_deltas[b] = d
            if d["calmar"] > 1e-12:
                counts["calmar_improved"] += 1
            elif d["calmar"] < -1e-12:
                counts["calmar_worsened"] += 1
            if d["cagr"] > 1e-12:
                counts["cagr_improved"] += 1
            elif d["cagr"] < -1e-12:
                counts["cagr_worsened"] += 1
            # MaxDD is negative. Positive delta = less severe drawdown.
            if d["max_drawdown"] > 1e-12:
                counts["maxdd_improved"] += 1
            elif d["max_drawdown"] < -1e-12:
                counts["maxdd_worsened"] += 1

        comparisons[rule] = {
            "action_class": RULE_TO_CLASS[rule],
            "variant": variant,
            "all79_delta": by_friction,
            "batch_counts_5bps": counts,
            "median_batch_delta_5bps": {
                "cagr": float(statistics.median(batch_deltas[b]["cagr"] for b in batch_deltas)),
                "max_drawdown": float(statistics.median(batch_deltas[b]["max_drawdown"] for b in batch_deltas)),
                "calmar": float(statistics.median(batch_deltas[b]["calmar"] for b in batch_deltas)),
                "turnover_mean": float(statistics.median(batch_deltas[b]["turnover_mean"] for b in batch_deltas)),
            },
            "batch_deltas_5bps": batch_deltas,
            "overlap": overlap["per_rule"][rule],
        }

    per_symbol = {}
    for s in prepared:
        per_symbol[s] = {
            "batch": batch_of[s],
            "5bps": {v: compact(sims["5bps"][v][s]) for v in VARIANTS},
            "10bps": {v: compact(sims["10bps"][v][s]) for v in VARIANTS},
        }

    output = {
        "meta": {
            "study": "SLTD_V7_RULE_ABLATION_REDUNDANCY_STUDY_V1",
            "status": "COMPLETE",
            "research_type": "EXPLORATORY_REUSED_79_STOCK_UNIVERSE",
            "baseline_branch": "baseline/sltd-v6-15rules-position-v1",
            "baseline_commit": "05be43e350d9193ba01a2748ef4c0267438a84b1",
            "universe_count": 79,
            "batches": list(range(1, 9)),
            "formal_window": "2020-01-02..2026-09-30",
            "representation": "FIRST_OBSERVED",
            "execution": "SIGNAL_CLOSE_TO_NEXT_AVAILABLE_OPEN",
            "ordinary_policy": ORDINARY_POLICY_ID,
            "hard_exit": HARD_EXIT_ID,
            "friction": {"baseline_bps": 5, "stress_bps": 10},
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        },
        "rules": [{"rule_id": r, "action_class": cls} for r, cls in RULES],
        "variants": list(VARIANTS),
        "frozen_baseline_reproduction": baseline_check,
        "overlap_redundancy": overlap,
        "all79_equal_weight": all79,
        "batch_results": batch_results,
        "comparisons": comparisons,
        "per_symbol": per_symbol,
    }
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(output, indent=2), encoding="utf-8")

    base = all79["5bps"]["BASELINE_ALL_15"]
    lines = [
        "# SLTD V7 Rule Ablation + Redundancy Study v1",
        "",
        "Status: **COMPLETE**",
        "",
        "Research status: **EXPLORATORY — reused 79-stock universe**",
        "",
        f"Frozen baseline: `baseline/sltd-v6-15rules-position-v1` @ `05be43e350d9193ba01a2748ef4c0267438a84b1`",
        "",
        "Frozen position / exit policy:",
        f"- `{ORDINARY_POLICY_ID}`",
        f"- Hard Exit `{HARD_EXIT_ID}`",
        "",
        "Baseline reproduction against the previously frozen C2 study: **PASS (5 bps and 10 bps)**.",
        "",
        "## Frozen baseline — all 79 stocks, 5 bps",
        "",
        f"- Total return: **{pct(base['total_return'])}**",
        f"- CAGR: **{pct(base['cagr'])}**",
        f"- MaxDD: **{pct(base['max_drawdown'])}**",
        f"- Calmar: **{base['calmar']:.3f}**",
        f"- C2 Hard Exits: **{base['hard_exit_count_sum']}**",
        "",
        "## 15-rule one-at-a-time ablation — all-79 delta vs baseline, 5 bps",
        "",
        "| Rule removed | Class | ΔCAGR | ΔMaxDD | ΔCalmar | ΔTurnover | Calmar better batches | Calmar worse batches | Resolved bars changed |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]

    for rule in RULE_IDS:
        x = comparisons[rule]
        d = x["all79_delta"]["5bps"]
        bc = x["batch_counts_5bps"]
        ov = x["overlap"]
        lines.append(
            f"| {rule} | {x['action_class']} | {pct(d['cagr'])} | {pct(d['max_drawdown'])} | "
            f"{fmt_signed(d['calmar'])} | {fmt_signed(d['turnover_mean'], 2)} | "
            f"{bc['calmar_improved']}/8 | {bc['calmar_worsened']}/8 | "
            f"{ov['resolved_action_changed_if_dropped']} |"
        )

    lines += [
        "",
        "Interpretation of ΔMaxDD: positive means drawdown became less severe after removing the rule; negative means worse.",
        "",
        "## Rule overlap / redundancy",
        "",
        "| Rule | Class | Occurrences | Sole bars | Same-class overlap | Cross-class overlap | Resolved bars changed if dropped |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for rule in RULE_IDS:
        x = overlap["per_rule"][rule]
        lines.append(
            f"| {rule} | {x['action_class']} | {x['occurrences']} | {x['sole_rule_bars']} | "
            f"{x['same_class_overlap_bars']} | {x['cross_class_overlap_bars']} | "
            f"{x['resolved_action_changed_if_dropped']} |"
        )

    lines += [
        "",
        f"Bars with any formal rule: **{overlap['bars_with_any_of_15_rules']}**",
        f"Mixed action-class bars: **{overlap['mixed_action_class_bars']}**",
        f"Multi-rule same-class bars: **{overlap['multi_rule_same_action_class_bars']}**",
        "",
        "## Subset / near-subset relationships",
        "",
    ]
    if overlap["subset_relationships"]:
        lines += [
            "| Relationship | Rule A | Rule B | Co-occurrence | Jaccard | P(B|A) | P(A|B) |",
            "|---|---|---|---:|---:|---:|---:|",
        ]
        for x in overlap["subset_relationships"]:
            lines.append(
                f"| {x['relationship']} | {x['rule_a']} | {x['rule_b']} | {x['cooccurrence']} | "
                f"{x['jaccard']:.3f} | {x['p_b_given_a']:.3f} | {x['p_a_given_b']:.3f} |"
            )
    else:
        lines.append("No >=90% subset-like pair with at least 5 co-occurrences.")

    lines += [
        "",
        "## Governance",
        "",
        "This run measures contribution and redundancy only. It does **not** change the frozen V6 baseline.",
        "Any rule deletion / merge / weakening / strengthening must be frozen separately and validated on fresh OOS data.",
        "",
        "`SLTD_V7_RULE_ABLATION_REDUNDANCY_STUDY_V1 = COMPLETE`",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
