#!/usr/bin/env python3
"""SLTD Rank -> Long-Hold Allocation v1 — Stage A."""
from __future__ import annotations

import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
PHASE11 = ROOT.parent / "phase11"
PHASE14 = ROOT.parent / "phase14"
sys.path.insert(0, str(PHASE14))
sys.path.insert(0, str(PHASE11))

import sltd_state_score_momentum_stage_b_v3 as b  # noqa: E402
import pure_sltd_state_probability_v1 as p11  # noqa: E402

OUT_JSON = ROOT / "SLTD_RANK_LONG_HOLD_ALLOCATION_V1_STAGE_A_RESULT.json"
OUT_MD = ROOT / "SLTD_RANK_LONG_HOLD_ALLOCATION_V1_STAGE_A_RESULT.md"

FORMAL_START = pd.Timestamp("2020-01-02")
FORMAL_END = pd.Timestamp("2026-09-30")
EARLY_END = pd.Timestamp("2023-12-31")
HORIZONS = (126, 252, 504)
FRICTIONS = (5.0, 20.0)
EXPECTED_SYMBOLS = 79


def max_drawdown_from_open(curve: np.ndarray) -> float:
    arr = np.concatenate([[1.0], np.asarray(curve, dtype=float)])
    peak = np.maximum.accumulate(arr)
    return float(np.min(arr / peak - 1.0))


def static_metrics(opens: np.ndarray, closes: np.ndarray, weights: np.ndarray, bps: float, dates: list[pd.Timestamp]) -> dict:
    rate = bps / 10000.0
    post = 1.0 - rate
    shares = weights * post / opens
    curve = np.asarray(closes @ shares, dtype=float)
    total = float(curve[-1] - 1.0)
    days = max(1, (pd.Timestamp(dates[-1]) - pd.Timestamp(dates[0])).days)
    cagr = float(curve[-1] ** (365.25 / days) - 1.0) if curve[-1] > 0 else -1.0
    mdd = max_drawdown_from_open(curve)
    calmar = float(cagr / abs(mdd)) if mdd < -1e-12 else (999.0 if cagr > 0 else 0.0)
    return {
        "total_return": total,
        "cagr": cagr,
        "max_drawdown": mdd,
        "calmar": calmar,
    }


def build_panel(stable: dict[str, float]) -> pd.DataFrame:
    chunks = []
    for batch, symbols in p11.core.BATCHES.items():
        for symbol in symbols:
            frame, ledger = p11.load_79_symbol(batch, symbol)
            rows = p11.build_symbol_rows(symbol, frame, ledger).copy()
            levels = []
            for rr in rows.itertuples(index=False):
                lvl, _ = b.level_for_row(rr, stable)
                levels.append(float(lvl))
            rows["level"] = np.asarray(levels, dtype=float)

            px = frame[["Date", "Open", "Close"]].copy()
            px["Date"] = pd.to_datetime(px["Date"]).dt.tz_localize(None)
            m = rows[["symbol", "date", "level"]].merge(
                px, left_on="date", right_on="Date", how="inner"
            ).drop(columns=["Date"])
            chunks.append(m)

    panel = pd.concat(chunks, ignore_index=True)
    panel["date"] = pd.to_datetime(panel["date"]).dt.tz_localize(None)
    if panel["symbol"].nunique() != EXPECTED_SYMBOLS:
        raise RuntimeError(f"expected {EXPECTED_SYMBOLS} symbols, got {panel['symbol'].nunique()}")
    return panel


def common_matrices(panel: pd.DataFrame):
    symbols = sorted(panel["symbol"].unique())
    opens = panel.pivot(index="date", columns="symbol", values="Open").sort_index().reindex(columns=symbols)
    closes = panel.pivot(index="date", columns="symbol", values="Close").sort_index().reindex(columns=symbols)
    levels = panel.pivot(index="date", columns="symbol", values="level").sort_index().reindex(columns=symbols)

    valid = (
        np.isfinite(opens.to_numpy(float)).all(axis=1)
        & np.isfinite(closes.to_numpy(float)).all(axis=1)
        & np.isfinite(levels.to_numpy(float)).all(axis=1)
    )
    opens = opens.loc[valid]
    closes = closes.loc[valid]
    levels = levels.loc[valid]

    dates = list(opens.index)
    if len(dates) < 1000:
        raise RuntimeError(f"insufficient common dates: {len(dates)}")
    return symbols, opens, closes, levels, dates


def rank_weights(level_row: np.ndarray) -> np.ndarray:
    s = pd.Series(np.asarray(level_row, dtype=float))
    avg_rank = s.rank(method="average", ascending=True).to_numpy(float)
    n = len(avg_rank)
    rank = (avg_rank - 1.0) / (n - 1.0)
    raw = np.clip(rank, 0.0, 1.0)
    z = float(np.sum(raw))
    if z <= 1e-15:
        return np.full(n, 1.0 / n)
    return raw / z


def formation_pairs(dates: list[pd.Timestamp]) -> list[tuple[pd.Timestamp, pd.Timestamp, int]]:
    pairs = []
    for i in range(1, len(dates)):
        d = pd.Timestamp(dates[i])
        prev = pd.Timestamp(dates[i - 1])
        if d < FORMAL_START or d > FORMAL_END:
            continue
        if (d.year, d.month) != (prev.year, prev.month):
            pairs.append((prev, d, i))
    return pairs


def cohort_result(
    rank_date: pd.Timestamp,
    buy_date: pd.Timestamp,
    buy_idx: int,
    horizon: int,
    bps: float,
    opens: pd.DataFrame,
    closes: pd.DataFrame,
    levels: pd.DataFrame,
    dates: list[pd.Timestamp],
) -> dict | None:
    end_idx = buy_idx + horizon - 1
    if end_idx >= len(dates):
        return None
    end_date = pd.Timestamp(dates[end_idx])
    if end_date > FORMAL_END:
        return None

    op = opens.loc[buy_date].to_numpy(float)
    rank_w = rank_weights(levels.loc[rank_date].to_numpy(float))
    equal_w = np.full(len(op), 1.0 / len(op))

    hold_dates = [pd.Timestamp(x) for x in dates[buy_idx:end_idx + 1]]
    cl = closes.loc[hold_dates].to_numpy(float)

    rank_m = static_metrics(op, cl, rank_w, bps, hold_dates)
    eq_m = static_metrics(op, cl, equal_w, bps, hold_dates)

    return {
        "rank_date": rank_date.strftime("%Y-%m-%d"),
        "buy_date": buy_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "formation_segment": "EARLY" if buy_date <= EARLY_END else "LATE",
        "horizon_bars": int(horizon),
        "friction_bps": float(bps),
        "rank_static": rank_m,
        "equal_static": eq_m,
        "excess_return": float(rank_m["total_return"] - eq_m["total_return"]),
        "maxdd_difference": float(rank_m["max_drawdown"] - eq_m["max_drawdown"]),
        "calmar_difference": float(rank_m["calmar"] - eq_m["calmar"]),
    }


def aggregate(items: list[dict]) -> dict:
    if not items:
        return {
            "cohort_count": 0,
            "median_excess_return": None,
            "mean_excess_return": None,
            "positive_fraction": None,
            "p25_excess_return": None,
            "p50_excess_return": None,
            "p75_excess_return": None,
            "median_maxdd_difference": None,
            "median_calmar_difference": None,
        }
    ex = np.asarray([x["excess_return"] for x in items], dtype=float)
    dd = np.asarray([x["maxdd_difference"] for x in items], dtype=float)
    ca = np.asarray([x["calmar_difference"] for x in items], dtype=float)
    return {
        "cohort_count": int(len(items)),
        "median_excess_return": float(np.median(ex)),
        "mean_excess_return": float(np.mean(ex)),
        "positive_fraction": float(np.mean(ex > 0)),
        "p25_excess_return": float(np.quantile(ex, 0.25)),
        "p50_excess_return": float(np.quantile(ex, 0.50)),
        "p75_excess_return": float(np.quantile(ex, 0.75)),
        "median_maxdd_difference": float(np.median(dd)),
        "median_calmar_difference": float(np.median(ca)),
    }


def full_window_diagnostic(opens, closes, levels, dates, bps: float) -> dict:
    buy_candidates = [i for i, d in enumerate(dates) if pd.Timestamp(d) >= FORMAL_START]
    if not buy_candidates:
        raise RuntimeError("no formal buy date")
    buy_idx = buy_candidates[0]
    if buy_idx <= 0:
        raise RuntimeError("no rank date before formal start")
    buy_date = pd.Timestamp(dates[buy_idx])
    rank_date = pd.Timestamp(dates[buy_idx - 1])

    end_candidates = [i for i, d in enumerate(dates) if pd.Timestamp(d) <= FORMAL_END]
    end_idx = end_candidates[-1]

    op = opens.loc[buy_date].to_numpy(float)
    rank_w = rank_weights(levels.loc[rank_date].to_numpy(float))
    equal_w = np.full(len(op), 1.0 / len(op))

    hold_dates = [pd.Timestamp(x) for x in dates[buy_idx:end_idx + 1]]
    cl = closes.loc[hold_dates].to_numpy(float)

    rank_m = static_metrics(op, cl, rank_w, bps, hold_dates)
    eq_m = static_metrics(op, cl, equal_w, bps, hold_dates)
    return {
        "rank_date": rank_date.strftime("%Y-%m-%d"),
        "buy_date": buy_date.strftime("%Y-%m-%d"),
        "end_date": pd.Timestamp(dates[end_idx]).strftime("%Y-%m-%d"),
        "rank_static": rank_m,
        "equal_static": eq_m,
        "excess_return": float(rank_m["total_return"] - eq_m["total_return"]),
        "maxdd_difference": float(rank_m["max_drawdown"] - eq_m["max_drawdown"]),
        "calmar_difference": float(rank_m["calmar"] - eq_m["calmar"]),
    }


def main():
    stable = b.load_stable_utilities()
    if len(stable) != 82:
        raise RuntimeError(f"expected 82 frozen states, got {len(stable)}")

    panel = build_panel(stable)
    symbols, opens, closes, levels, dates = common_matrices(panel)
    if len(symbols) != EXPECTED_SYMBOLS:
        raise RuntimeError("symbol count mismatch")

    pairs = formation_pairs(dates)
    if not pairs:
        raise RuntimeError("no monthly formation pairs")

    cohorts = []
    for bps in FRICTIONS:
        for horizon in HORIZONS:
            for rank_date, buy_date, buy_idx in pairs:
                row = cohort_result(
                    rank_date, buy_date, buy_idx, horizon, bps,
                    opens, closes, levels, dates
                )
                if row is not None:
                    cohorts.append(row)

    summaries = {}
    for bps in FRICTIONS:
        fk = f"{int(bps)}bps"
        summaries[fk] = {}
        for horizon in HORIZONS:
            hk = str(horizon)
            summaries[fk][hk] = {}
            base = [x for x in cohorts if x["friction_bps"] == bps and x["horizon_bars"] == horizon]
            for segment in ("EARLY", "LATE", "ALL"):
                items = base if segment == "ALL" else [x for x in base if x["formation_segment"] == segment]
                summaries[fk][hk][segment] = aggregate(items)

    s5_126_late = summaries["5bps"]["126"]["LATE"]
    s5_252_early = summaries["5bps"]["252"]["EARLY"]
    s5_252_late = summaries["5bps"]["252"]["LATE"]
    s20_252_late = summaries["20bps"]["252"]["LATE"]

    gates = {
        "early_252_median_excess_positive":
            s5_252_early["median_excess_return"] is not None and s5_252_early["median_excess_return"] > 0,
        "late_252_median_excess_positive":
            s5_252_late["median_excess_return"] is not None and s5_252_late["median_excess_return"] > 0,
        "early_252_positive_fraction_gt_50":
            s5_252_early["positive_fraction"] is not None and s5_252_early["positive_fraction"] > 0.5,
        "late_252_positive_fraction_gt_50":
            s5_252_late["positive_fraction"] is not None and s5_252_late["positive_fraction"] > 0.5,
        "late_252_median_calmar_difference_positive":
            s5_252_late["median_calmar_difference"] is not None and s5_252_late["median_calmar_difference"] > 0,
        "late_252_median_maxdd_difference_ge_minus_1pp":
            s5_252_late["median_maxdd_difference"] is not None and s5_252_late["median_maxdd_difference"] >= -0.01,
        "late_126_median_excess_positive":
            s5_126_late["median_excess_return"] is not None and s5_126_late["median_excess_return"] > 0,
        "late_252_20bps_median_excess_positive":
            s20_252_late["median_excess_return"] is not None and s20_252_late["median_excess_return"] > 0,
    }

    decision = "PROMOTED_TO_LONG_HOLD_FRESH_OOS" if all(gates.values()) else "REJECTED_NOT_ADMITTED"

    full = {
        "5bps": full_window_diagnostic(opens, closes, levels, dates, 5.0),
        "20bps": full_window_diagnostic(opens, closes, levels, dates, 20.0),
    }

    out = {
        "meta": {
            "study": "SLTD_RANK_LONG_HOLD_ALLOCATION_V1_STAGE_A",
            "protocol": "SLTD_RANK_LONG_HOLD_ALLOCATION_V1_PROTOCOL.md",
            "parent_closeout": "4b19c5b3b3a328eef25239142a3dd357118ca318",
            "stable_state_count": len(stable),
            "symbol_count": len(symbols),
            "chan_used": False,
            "v7_used_as_signal": False,
            "momentum_used": False,
            "v4_probability_used": False,
            "rank_rebalanced_after_entry": False,
            "fresh_oos_consumed": False,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        },
        "formation_pair_count": len(pairs),
        "summaries": summaries,
        "full_window_static_diagnostic": full,
        "gates": gates,
        "decision": decision,
        "cohorts": cohorts,
    }
    OUT_JSON.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# SLTD Rank -> Long-Hold Allocation v1 — Stage A Result",
        "",
        f"Status: **{decision}**",
        "",
        "Interpretation: ranking is used only at initial formation; positions are not rebalanced because rank changes.",
        "",
        "Chan/缠论: **NOT USED**",
        "V7 as signal: **NOT USED**",
        "Score Momentum: **NOT USED**",
        "v4 probability: **NOT USED**",
        "Fresh OOS consumed: **NO**",
        "",
        f"- Symbols: **{len(symbols)}**",
        f"- Monthly formation pairs available: **{len(pairs)}**",
        "",
        "## Aggregate cohort results — 5 bps",
        "",
        "| Horizon | Segment | Cohorts | Median excess | Mean excess | Positive fraction | Median MaxDD diff | Median Calmar diff |",
        "|---:|---|---:|---:|---:|---:|---:|---:|",
    ]

    for horizon in HORIZONS:
        for segment in ("EARLY","LATE","ALL"):
            z=summaries["5bps"][str(horizon)][segment]
            if z["cohort_count"] == 0:
                continue
            lines.append(
                f"| {horizon} | {segment} | {z['cohort_count']} | "
                f"{100*z['median_excess_return']:.3f}% | {100*z['mean_excess_return']:.3f}% | "
                f"{100*z['positive_fraction']:.1f}% | {100*z['median_maxdd_difference']:.3f}% | "
                f"{z['median_calmar_difference']:.3f} |"
            )

    lines += [
        "",
        "## Full-window static diagnostic — 5 bps",
        "",
    ]
    fw=full["5bps"]
    for name,key in (("RANK_STATIC","rank_static"),("EQUAL_STATIC","equal_static")):
        z=fw[key]
        lines.append(
            f"- {name}: Return **{100*z['total_return']:.2f}%**, CAGR **{100*z['cagr']:.2f}%**, "
            f"MaxDD **{100*z['max_drawdown']:.2f}%**, Calmar **{z['calmar']:.3f}**"
        )
    lines += [
        f"- Rank minus Equal full-window return: **{100*fw['excess_return']:.2f}%**",
        "",
        "## Gates",
        "",
    ]
    for k,v in gates.items():
        lines.append(f"- {k}: **{'PASS' if v else 'FAIL'}**")
    lines += [
        "",
        f"`SLTD_RANK_LONG_HOLD_ALLOCATION_V1_STAGE_A = {decision}`",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps({
        "decision": decision,
        "summaries_5bps_126_late": s5_126_late,
        "summaries_5bps_252_early": s5_252_early,
        "summaries_5bps_252_late": s5_252_late,
        "full_window_5bps": full["5bps"],
        "gates": gates,
    }, indent=2))


if __name__ == "__main__":
    main()
