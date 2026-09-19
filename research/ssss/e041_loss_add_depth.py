#!/usr/bin/env python3
"""E041 BTC 15m Loss-Pullback Ladder Depth & Drawdown Attribution.

Discovery-only research runner governed by:
research/ssss/preregistrations/E041.md

This script MUST NOT query any OOS or cross-asset holdout.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

from e035_dynamic_engine import (  # noqa: E402
    BASE_FRICTION,
    STRESS_FRICTION,
    CONFIGS,
    compute_indicators,
    lifecycle_return,
)

RAW_DIR = HERE / "checkpoints" / "e035" / "raw"
E037_CHECKPOINT = HERE / "checkpoints" / "e037" / "E037_DYNAMIC_MAP.json"
E040_CHECKPOINT = HERE / "checkpoints" / "e040" / "E040_REPEATED_PULLBACK.json"

STARTER = 0.30
ADD_DELTA = 0.10
PULLBACK = 0.01
COOLDOWN_BARS = 4


def load_bars() -> pd.DataFrame:
    pages = sorted(RAW_DIR.glob("page_*.csv"))
    if len(pages) != 10:
        raise RuntimeError(f"expected 10 frozen pages, got {len(pages)}")

    frames = [pd.read_csv(p) for p in pages]
    raw = pd.concat(frames, ignore_index=True)
    raw = raw.rename(
        columns={
            "t": "timestamp",
            "o": "open",
            "h": "high",
            "l": "low",
            "c": "close",
            "v": "volume",
        }
    )
    keep = ["timestamp", "open", "high", "low", "close", "volume"]
    raw = raw[keep].copy()
    raw["timestamp"] = pd.to_datetime(raw["timestamp"], unit="ms", utc=True)
    raw = raw.sort_values("timestamp").reset_index(drop=True)

    # Frozen pre-result E035 sanitation.
    raw["high"] = raw[["high", "open", "close"]].max(axis=1)
    raw["low"] = raw[["low", "open", "close"]].min(axis=1)

    if len(raw) != 33312:
        raise RuntimeError(f"unexpected frozen bar count {len(raw)}")
    if raw["timestamp"].duplicated().any():
        raise RuntimeError("duplicate timestamp in frozen snapshot")
    return raw


def pf(values: list[float]) -> float | None:
    pos = sum(x for x in values if x > 0)
    neg = -sum(x for x in values if x < 0)
    if neg <= 0:
        return None if pos <= 0 else float("inf")
    return pos / neg


def top3_share(values: list[float]) -> float | None:
    pos = sorted((x for x in values if x > 0), reverse=True)
    if not pos:
        return None
    den = sum(pos)
    return sum(pos[:3]) / den if den else None


def describe_events(events: list[dict]) -> dict:
    if not events:
        return {
            "n": 0,
            "mean": None,
            "median": None,
            "pf": None,
            "stress_median": None,
            "q25": None,
            "positive_rate": None,
            "top3": None,
        }
    base = [float(e["base_unit_return"]) for e in events]
    stress = [float(e["stress_unit_return"]) for e in events]
    return {
        "n": len(events),
        "mean": float(np.mean(base)),
        "median": float(np.median(base)),
        "pf": pf(base),
        "stress_median": float(np.median(stress)),
        "q25": float(np.quantile(base, 0.25)),
        "positive_rate": float(np.mean(np.array(base) > 0)),
        "top3": top3_share(base),
    }


def max_drawdown_from_returns(per: list[float]) -> tuple[float, list[int], list[float]]:
    equity = [1.0]
    for r in per:
        equity.append(equity[-1] * (1.0 + r))

    peak_val = equity[0]
    peak_idx = 0
    best_dd = 0.0
    best_peak = 0
    best_trough = 0

    for idx, value in enumerate(equity):
        if value > peak_val:
            peak_val = value
            peak_idx = idx
        dd = 1.0 - value / peak_val
        if dd > best_dd:
            best_dd = dd
            best_peak = peak_idx
            best_trough = idx

    # equity index k means after lifecycle k; drawdown-causing lifecycle IDs
    # are best_peak+1 ... best_trough.
    ids = list(range(best_peak + 1, best_trough + 1))
    return float(best_dd), ids, equity


def build_green_transition_lifecycles(df: pd.DataFrame, cfg) -> list[dict]:
    rows: list[dict] = []
    in_position = False
    seen_red = False
    trade = None

    for i in range(len(df)):
        state = str(df.at[i, "effective_state"])

        if not in_position:
            if (
                i >= cfg.warmup_bars
                and bool(df.at[i, "green_transition"])
                and i + 1 < len(df)
            ):
                in_position = True
                seen_red = False
                trade = {
                    "signal_i": i,
                    "entry_i": i + 1,
                    "entry_open": float(df.at[i + 1, "open"]),
                    "first_red_i": None,
                }
        else:
            assert trade is not None
            if seen_red:
                if bool(df.at[i, "red_to_gray"]) and i + 1 < len(df):
                    trade["close_signal_i"] = i
                    trade["exit_i"] = i + 1
                    trade["exit_open"] = float(df.at[i + 1, "open"])
                    trade["path"] = "MATURE"
                    rows.append(trade)
                    trade = None
                    in_position = False
                    seen_red = False
            else:
                if state == "red":
                    seen_red = True
                    trade["first_red_i"] = i
                elif bool(df.at[i, "gray_to_green"]) and i + 1 < len(df):
                    trade["close_signal_i"] = i
                    trade["exit_i"] = i + 1
                    trade["exit_open"] = float(df.at[i + 1, "open"])
                    trade["path"] = "FAILURE"
                    rows.append(trade)
                    trade = None
                    in_position = False

    for n, t in enumerate(rows, start=1):
        t["id"] = n
        t["base_unit_return"] = lifecycle_return(
            t["entry_open"], t["exit_open"], BASE_FRICTION
        )
        t["stress_unit_return"] = lifecycle_return(
            t["entry_open"], t["exit_open"], STRESS_FRICTION
        )
    return rows


def weighted_cost(lots: list[dict]) -> float:
    total = sum(float(x["weight"]) for x in lots)
    return sum(float(x["weight"]) * float(x["entry_open"]) for x in lots) / total


def evaluate_lots_to_exit(
    lots: list[dict],
    realized_base: float,
    realized_stress: float,
    exit_open: float,
) -> tuple[float, float]:
    b = realized_base
    s = realized_stress
    for lot in lots:
        w = float(lot["weight"])
        px = float(lot["entry_open"])
        b += w * lifecycle_return(px, exit_open, BASE_FRICTION)
        s += w * lifecycle_return(px, exit_open, STRESS_FRICTION)
    return float(b), float(s)


def simulate_loss_only(
    df: pd.DataFrame,
    trade: dict,
    max_adds: int,
) -> dict:
    lots = [{"weight": STARTER, "entry_open": float(trade["entry_open"])}]
    events: list[dict] = []
    add_count = 0
    anchor = float(trade["entry_open"])
    validity_active = True
    cooldown_until = -1

    # Reference CLOSE signal bar is excluded: CLOSE overrides pending ADD.
    for i in range(int(trade["entry_i"]), int(trade["close_signal_i"])):
        close = float(df.at[i, "close"])
        high = float(df.at[i, "high"])
        fast_lower = float(df.at[i, "fast_lower"])
        floor_ok = close >= fast_lower

        if not floor_ok:
            validity_active = False
            continue

        if not validity_active:
            # Causal FastLower reclaim: restart local anchor, no ADD on reclaim bar.
            validity_active = True
            anchor = high
            continue

        anchor = max(anchor, high)

        if i < cooldown_until:
            continue
        if add_count >= max_adds:
            continue

        pb = close / anchor - 1.0
        if pb > -PULLBACK:
            continue

        state = str(df.at[i, "effective_state"])
        continuation = state in {"green", "red"} and float(df.at[i, "dsep"]) > 0
        if not continuation:
            continue

        position_return = close / weighted_cost(lots) - 1.0
        if position_return >= 0:
            continue

        exec_i = i + 1
        if exec_i >= int(trade["exit_i"]):
            continue
        exec_open = float(df.at[exec_i, "open"])

        add_count += 1
        event = {
            "lifecycle_id": int(trade["id"]),
            "path": trade["path"],
            "ordinal": add_count,
            "signal_i": i,
            "exec_i": exec_i,
            "exec_open": exec_open,
            "signal_close": close,
            "anchor": anchor,
            "pb": pb,
            "position_return_at_signal": position_return,
            "base_unit_return": lifecycle_return(
                exec_open, float(trade["exit_open"]), BASE_FRICTION
            ),
            "stress_unit_return": lifecycle_return(
                exec_open, float(trade["exit_open"]), STRESS_FRICTION
            ),
        }
        events.append(event)

        lots.append({"weight": ADD_DELTA, "entry_open": exec_open})
        anchor = exec_open
        # Four complete 15m bars after the action execution are in cooldown.
        cooldown_until = exec_i + COOLDOWN_BARS

    base_ret, stress_ret = evaluate_lots_to_exit(
        lots, 0.0, 0.0, float(trade["exit_open"])
    )

    # Time-weighted mark-to-market nominal exposure diagnostic.
    mtm = []
    for i in range(int(trade["entry_i"]), int(trade["exit_i"])):
        active_lots = [
            {"weight": STARTER, "entry_open": float(trade["entry_open"])}
        ]
        for e in events:
            if int(e["exec_i"]) <= i:
                active_lots.append({"weight": ADD_DELTA, "entry_open": float(e["exec_open"])})
        close = float(df.at[i, "close"])
        val = sum(
            float(x["weight"]) * close / float(x["entry_open"])
            for x in active_lots
        )
        mtm.append(val)

    # Turnover relative to lifecycle-start equity: buys + final net liquidation.
    buy_turnover = STARTER + ADD_DELTA * len(events)
    final_value = sum(
        float(x["weight"])
        * (float(trade["exit_open"]) * (1.0 - BASE_FRICTION))
        / (float(x["entry_open"]) * (1.0 + BASE_FRICTION))
        for x in lots
    )

    return {
        "id": int(trade["id"]),
        "path": trade["path"],
        "base_ret": base_ret,
        "stress_ret": stress_ret,
        "events": events,
        "avg_exposure": float(np.mean(mtm)) if mtm else STARTER,
        "turnover": float(buy_turnover + final_value),
    }


def simulate_e040_reproduction(df: pd.DataFrame, trade: dict) -> dict:
    """Diagnostic reproduction of E040 D=1%, V1_FASTLOWER.

    This is NOT used to select E041. It exists only to verify continuity
    with the already-viewed E040 implementation as closely as possible.
    """
    lots = [{"weight": STARTER, "entry_open": float(trade["entry_open"])}]
    realized_base = 0.0
    realized_stress = 0.0
    anchor = float(trade["entry_open"])
    validity_active = True
    cooldown_until = -1
    events = []
    add_ordinal = 0

    for i in range(int(trade["entry_i"]), int(trade["close_signal_i"])):
        close = float(df.at[i, "close"])
        high = float(df.at[i, "high"])
        floor_ok = close >= float(df.at[i, "fast_lower"])

        if not floor_ok:
            validity_active = False
            continue
        if not validity_active:
            validity_active = True
            anchor = high
            continue

        anchor = max(anchor, high)
        if i < cooldown_until:
            continue

        pb = close / anchor - 1.0
        if pb > -PULLBACK:
            continue

        state = str(df.at[i, "effective_state"])
        strong = state in {"green", "red"} and float(df.at[i, "dsep"]) > 0
        exposure = sum(float(x["weight"]) for x in lots)
        pos_ret = close / weighted_cost(lots) - 1.0
        exec_i = i + 1
        if exec_i >= int(trade["exit_i"]):
            continue
        exec_open = float(df.at[exec_i, "open"])

        action = None
        if strong and exposure < 0.50 - 1e-12:
            add_w = min(ADD_DELTA, 0.50 - exposure)
            if add_w > 1e-12:
                add_ordinal += 1
                cls = "TREND" if pos_ret >= 0 else "LOSS"
                lots.append({"weight": add_w, "entry_open": exec_open})
                action = {
                    "type": "ADD",
                    "class": cls,
                    "ordinal": add_ordinal,
                    "weight": add_w,
                    "exec_i": exec_i,
                    "exec_open": exec_open,
                }
        elif (not strong) and pos_ret > 0 and exposure > 0.30 + 1e-12:
            target = max(0.30, exposure * 0.85)
            scale = target / exposure
            sold_parts = []
            new_lots = []
            for lot in lots:
                old_w = float(lot["weight"])
                keep_w = old_w * scale
                sold_w = old_w - keep_w
                if sold_w > 0:
                    realized_base += sold_w * lifecycle_return(
                        float(lot["entry_open"]), exec_open, BASE_FRICTION
                    )
                    realized_stress += sold_w * lifecycle_return(
                        float(lot["entry_open"]), exec_open, STRESS_FRICTION
                    )
                    sold_parts.append(sold_w)
                new_lots.append(
                    {"weight": keep_w, "entry_open": float(lot["entry_open"])}
                )
            lots = new_lots
            action = {
                "type": "REDUCE",
                "weight": sum(sold_parts),
                "exec_i": exec_i,
                "exec_open": exec_open,
            }

        if action is not None:
            events.append(action)
            anchor = exec_open
            cooldown_until = exec_i + COOLDOWN_BARS

    base_ret, stress_ret = evaluate_lots_to_exit(
        lots, realized_base, realized_stress, float(trade["exit_open"])
    )
    return {
        "base_ret": base_ret,
        "stress_ret": stress_ret,
        "events": events,
    }


def portfolio_summary(results: list[dict], benchmark_b: dict) -> dict:
    per = [float(x["base_ret"]) for x in results]
    stress_per = [float(x["stress_ret"]) for x in results]
    final = float(np.prod([1.0 + x for x in per]))
    stress_final = float(np.prod([1.0 + x for x in stress_per]))
    maxdd, dd_ids, _ = max_drawdown_from_returns(per)

    b_per = {int(x["id"]): float(x["ret"]) for x in benchmark_b["per"]}
    incremental = [
        float(x["base_ret"]) - b_per[int(x["id"])]
        for x in results
    ]
    pos_inc = [x for x in incremental if x > 0]
    top_inc_share = (
        max(pos_inc) / sum(pos_inc) if pos_inc and sum(pos_inc) > 0 else None
    )

    mature = sum(float(x["base_ret"]) for x in results if x["path"] == "MATURE")
    failure = sum(float(x["base_ret"]) for x in results if x["path"] == "FAILURE")

    all_events = [e for x in results for e in x["events"]]

    return {
        "final": final,
        "ret": final - 1.0,
        "stress_final": stress_final,
        "stress_ret": stress_final - 1.0,
        "maxDD": maxdd,
        "maxDD_lifecycle_ids": dd_ids,
        "avgExposure": float(np.mean([x["avg_exposure"] for x in results])),
        "turnover": float(sum(x["turnover"] for x in results)),
        "mature_total": float(mature),
        "failure_total": float(failure),
        "incremental_vs_B": float((final - 1.0) - float(benchmark_b["ret"])),
        "top_incremental_share": top_inc_share,
        "add_count": len(all_events),
    }


def main() -> dict:
    bars = load_bars()
    cfg = next(x for x in CONFIGS if x.name == "B2_NATIVE_24H")
    df = compute_indicators(bars, cfg)
    lifecycles = build_green_transition_lifecycles(df, cfg)

    with E037_CHECKPOINT.open("r", encoding="utf-8") as f:
        e037 = json.load(f)
    with E040_CHECKPOINT.open("r", encoding="utf-8") as f:
        e040 = json.load(f)

    # Hard continuity checks that do not inspect any new holdout.
    ref = e037["summary"]["reference"]
    base_unit = [float(t["base_unit_return"]) for t in lifecycles]
    lifecycle_check = {
        "resolved": len(lifecycles),
        "mature": sum(t["path"] == "MATURE" for t in lifecycles),
        "failure": sum(t["path"] == "FAILURE" for t in lifecycles),
        "base_mean": float(np.mean(base_unit)),
        "base_median": float(np.median(base_unit)),
        "base_pf": pf(base_unit),
    }

    expected_tuple = (48, 33, 15)
    got_tuple = (
        lifecycle_check["resolved"],
        lifecycle_check["mature"],
        lifecycle_check["failure"],
    )
    if got_tuple != expected_tuple:
        raise RuntimeError(
            f"GREEN_TRANSITION lifecycle mismatch: got {got_tuple}, expected {expected_tuple}"
        )
    for key in ("base_mean", "base_median", "base_pf"):
        if not math.isclose(
            float(lifecycle_check[key]), float(ref[key]), rel_tol=0, abs_tol=1e-12
        ):
            raise RuntimeError(
                f"E037 reference mismatch {key}: {lifecycle_check[key]} vs {ref[key]}"
            )

    benchmark_a_per = [
        {
            "id": int(t["id"]),
            "path": t["path"],
            "ret": STARTER * float(t["base_unit_return"]),
        }
        for t in lifecycles
    ]
    a_per = [x["ret"] for x in benchmark_a_per]
    a_final = float(np.prod([1 + x for x in a_per]))
    a_dd, _, _ = max_drawdown_from_returns(a_per)
    a_expected = e040["benchmark_A"]
    benchmark_a_check = {
        "final": a_final,
        "maxDD": a_dd,
        "max_abs_per_diff": max(
            abs(x["ret"] - float(y["ret"]))
            for x, y in zip(benchmark_a_per, a_expected["per"])
        ),
    }
    if not math.isclose(a_final, float(a_expected["final"]), rel_tol=0, abs_tol=1e-12):
        raise RuntimeError(
            f"E040 Benchmark A final mismatch: {a_final} vs {a_expected['final']}"
        )
    if benchmark_a_check["max_abs_per_diff"] > 1e-12:
        raise RuntimeError(
            f"E040 Benchmark A per-lifecycle mismatch {benchmark_a_check['max_abs_per_diff']}"
        )

    # Diagnostic E040 D=1/V1 reproduction; not a selection input.
    repro = [simulate_e040_reproduction(df, t) for t in lifecycles]
    repro_per = [x["base_ret"] for x in repro]
    repro_final = float(np.prod([1 + x for x in repro_per]))
    repro_dd, _, _ = max_drawdown_from_returns(repro_per)
    repro_events = [e for x in repro for e in x["events"]]
    e040_reproduction = {
        "final": repro_final,
        "ret": repro_final - 1.0,
        "maxDD": repro_dd,
        "counts": {
            "add": sum(e["type"] == "ADD" for e in repro_events),
            "reduce": sum(e["type"] == "REDUCE" for e in repro_events),
            "trend_add": sum(
                e["type"] == "ADD" and e.get("class") == "TREND"
                for e in repro_events
            ),
            "loss_add": sum(
                e["type"] == "ADD" and e.get("class") == "LOSS"
                for e in repro_events
            ),
            "first_add": sum(
                e["type"] == "ADD" and e.get("ordinal") == 1
                for e in repro_events
            ),
            "second_add": sum(
                e["type"] == "ADD" and e.get("ordinal") == 2
                for e in repro_events
            ),
        },
        "expected": {
            "final": e040["best_by_D"][0]["final"],
            "ret": e040["best_by_D"][0]["ret"],
            "maxDD": e040["best_by_D"][0]["maxDD"],
            "counts": e040["best_by_D"][0]["counts"],
        },
    }

    b = e040["benchmark_B"]
    bs = e040["benchmark_B_stress"]

    l1_results = [simulate_loss_only(df, t, 1) for t in lifecycles]
    l2_results = [simulate_loss_only(df, t, 2) for t in lifecycles]

    l1_events = [e for x in l1_results for e in x["events"]]
    l2_events = [e for x in l2_results for e in x["events"]]
    l2_first = [e for e in l2_events if int(e["ordinal"]) == 1]
    l2_second = [e for e in l2_events if int(e["ordinal"]) == 2]

    l1_port = portfolio_summary(l1_results, b)
    l2_port = portfolio_summary(l2_results, b)

    l1_event = describe_events(l1_events)
    l2_event = describe_events(l2_events)
    first_event = describe_events(l2_first)
    second_event = describe_events(l2_second)

    def l1_event_gate(s: dict) -> bool:
        return (
            s["n"] >= 15
            and s["mean"] is not None and s["mean"] > 0
            and s["median"] is not None and s["median"] > 0
            and s["pf"] is not None and s["pf"] > 1.25
            and s["stress_median"] is not None and s["stress_median"] >= 0
            and s["q25"] is not None and s["q25"] > -0.025
            and s["top3"] is not None and s["top3"] <= 0.60
        )

    l1eg = l1_event_gate(l1_event)
    l2eg = (
        l1_event_gate(l2_event)
        and second_event["n"] >= 8
        and second_event["mean"] is not None and second_event["mean"] > 0
        and second_event["median"] is not None and second_event["median"] > 0
        and second_event["stress_median"] is not None
        and second_event["stress_median"] >= 0
    )

    benchmark_mature = float(e040["best_by_D"][0]["benchmark_mature_total"])

    def portfolio_gate(p: dict) -> bool:
        return (
            p["ret"] > float(b["ret"])
            and p["stress_ret"] >= float(bs["ret"])
            and p["maxDD"] <= 1.10 * float(b["maxDD"])
            and p["mature_total"] >= 0.90 * benchmark_mature
            and p["top_incremental_share"] is not None
            and p["top_incremental_share"] <= 0.35
        )

    l1pg = portfolio_gate(l1_port)
    l2pg = portfolio_gate(l2_port)
    l1_eligible = l1eg and l1pg
    l2_eligible = l2eg and l2pg

    selected = None
    status = "NO_LOSS_ADD_DEPTH_CANDIDATE"
    eligible = []
    if l1_eligible:
        eligible.append(("L1_ONE_LOSS_ADD", l1_port))
    if l2_eligible:
        eligible.append(("L2_TWO_LOSS_ADDS", l2_port))
    if eligible:
        eligible.sort(
            key=lambda x: (
                x[1]["stress_ret"] - float(bs["ret"]),
                -x[1]["maxDD"],
                -x[1]["turnover"],
                -x[1]["add_count"],
            ),
            reverse=True,
        )
        selected = eligible[0][0]
        status = (
            "ONE_STEP_LOSS_ADD_CANDIDATE"
            if selected == "L1_ONE_LOSS_ADD"
            else "TWO_STEP_LOSS_ADD_CANDIDATE"
        )

    drawdown_attribution = {
        "benchmark_B_maxDD": float(b["maxDD"]),
        "allowed_maxDD": 1.10 * float(b["maxDD"]),
        "L1_maxDD": l1_port["maxDD"],
        "L2_maxDD": l2_port["maxDD"],
        "first_step_incremental_DD": l1_port["maxDD"] - float(b["maxDD"]),
        "second_step_incremental_DD": l2_port["maxDD"] - l1_port["maxDD"],
        "L1_relative_vs_B": l1_port["maxDD"] / float(b["maxDD"]) - 1.0,
        "L2_relative_vs_B": l2_port["maxDD"] / float(b["maxDD"]) - 1.0,
    }

    return {
        "experiment": "E041",
        "data": {
            "bars": len(df),
            "resolved_lifecycles": len(lifecycles),
            "mature": lifecycle_check["mature"],
            "failure": lifecycle_check["failure"],
        },
        "continuity_checks": {
            "e037_reference": lifecycle_check,
            "e040_benchmark_A": benchmark_a_check,
            "e040_1pct_v1_reproduction": e040_reproduction,
        },
        "benchmark_A": e040["benchmark_A"],
        "benchmark_B": b,
        "benchmark_B_stress": bs,
        "variants": {
            "L1_ONE_LOSS_ADD": {
                "event_gate": l1eg,
                "portfolio_gate": l1pg,
                "eligible": l1_eligible,
                "events": l1_event,
                "first_add": l1_event,
                "portfolio": l1_port,
            },
            "L2_TWO_LOSS_ADDS": {
                "event_gate": l2eg,
                "portfolio_gate": l2pg,
                "eligible": l2_eligible,
                "events": l2_event,
                "first_add": first_event,
                "second_add": second_event,
                "portfolio": l2_port,
            },
        },
        "drawdown_attribution": drawdown_attribution,
        "selected": selected,
        "final_status": status,
        "holdouts_opened": False,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", default="")
    args = parser.parse_args()
    result = main()
    payload = json.dumps(result, ensure_ascii=False, separators=(",", ":"))
    if args.json:
        Path(args.json).write_text(
            json.dumps(result, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    print("E041_RESULT_JSON=" + payload)
