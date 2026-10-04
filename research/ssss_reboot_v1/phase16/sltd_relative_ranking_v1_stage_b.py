#!/usr/bin/env python3
"""SLTD Relative Ranking v1 — Stage B allocation test."""
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
import pure_sltd_v8_probability_map_r2_v1 as r2  # noqa: E402

OUT_JSON = ROOT / "SLTD_RELATIVE_RANKING_V1_STAGE_B_RESULT.json"
OUT_MD = ROOT / "SLTD_RELATIVE_RANKING_V1_STAGE_B_RESULT.md"

FORMAL_START = pd.Timestamp("2020-01-02")
FORMAL_END = pd.Timestamp("2026-09-30")
MIN_XS = 60
FRICTIONS = (5.0, 10.0, 20.0)


def max_drawdown(curve: np.ndarray) -> float:
    peak = np.maximum.accumulate(curve)
    return float(np.min(curve / peak - 1.0))


def annual_returns(dates: list[pd.Timestamp], daily: np.ndarray) -> dict[str, float]:
    out = {}
    years = sorted(set(int(pd.Timestamp(d).year) for d in dates))
    arr_dates = np.asarray([pd.Timestamp(d) for d in dates], dtype=object)
    for y in years:
        mask = np.asarray([d.year == y for d in arr_dates], dtype=bool)
        vals = daily[mask]
        out[str(y)] = float(np.prod(1.0 + vals) - 1.0) if len(vals) else 0.0
    return out


def metrics(curve: np.ndarray, dates: list[pd.Timestamp], turnover: float, rebalances: int) -> dict:
    arr = np.asarray(curve, dtype=float)
    if len(arr) < 2:
        raise RuntimeError("insufficient portfolio curve")
    daily = np.empty(len(arr), dtype=float)
    daily[0] = arr[0] - 1.0
    daily[1:] = arr[1:] / arr[:-1] - 1.0
    days = max(1, (pd.Timestamp(dates[-1]) - pd.Timestamp(dates[0])).days)
    total = float(arr[-1] - 1.0)
    cagr = float(arr[-1] ** (365.25 / days) - 1.0) if arr[-1] > 0 else -1.0
    mdd = max_drawdown(arr)
    calmar = cagr / abs(mdd) if mdd < -1e-12 else (999.0 if cagr > 0 else 0.0)
    return {
        "start": pd.Timestamp(dates[0]).strftime("%Y-%m-%d"),
        "end": pd.Timestamp(dates[-1]).strftime("%Y-%m-%d"),
        "observations": int(len(arr)),
        "total_return": total,
        "cagr": cagr,
        "max_drawdown": mdd,
        "calmar": float(calmar),
        "turnover": float(turnover),
        "rebalance_count": int(rebalances),
        "daily_p1": float(np.quantile(daily, 0.01)),
        "daily_p5": float(np.quantile(daily, 0.05)),
        "annual_returns": annual_returns(dates, daily),
    }


def build_market_panel(stable: dict[str, float]):
    chunks = []
    bars_by = {}
    ledgers_by = {}

    for batch, symbols in p11.core.BATCHES.items():
        for symbol in symbols:
            frame, ledger_df = p11.load_79_symbol(batch, symbol)
            rows = p11.build_symbol_rows(symbol, frame, ledger_df).copy()
            levels = []
            for rr in rows.itertuples(index=False):
                lvl, _ = b.level_for_row(rr, stable)
                levels.append(float(lvl))
            rows["level"] = np.asarray(levels, dtype=float)

            px = frame[["Date", "Open", "Close"]].copy()
            px["Date"] = pd.to_datetime(px["Date"]).dt.tz_localize(None)
            m = rows[["symbol", "date", "level"]].merge(
                px, left_on="date", right_on="Date", how="inner"
            )
            m = m.drop(columns=["Date"])
            chunks.append(m)

            bars = r2.candles_from_frame(frame)
            ledger = r2.sltd.build_ledger(bars, symbol)
            bars_by[symbol] = bars
            ledgers_by[symbol] = ledger

    panel = pd.concat(chunks, ignore_index=True)
    panel["date"] = pd.to_datetime(panel["date"]).dt.tz_localize(None)
    if panel["symbol"].nunique() != 79:
        raise RuntimeError(f"expected 79 symbols, got {panel['symbol'].nunique()}")

    counts = panel.groupby("date")["symbol"].transform("count")
    panel = panel.loc[counts >= MIN_XS].copy()
    panel["xs_n"] = panel.groupby("date")["symbol"].transform("count").astype(int)
    avg_rank = panel.groupby("date")["level"].rank(method="average", ascending=True)
    panel["rank"] = (avg_rank - 1.0) / (panel["xs_n"].astype(float) - 1.0)

    return panel, bars_by, ledgers_by


def synchronized_matrices(panel: pd.DataFrame):
    opens = panel.pivot(index="date", columns="symbol", values="Open").sort_index()
    closes = panel.pivot(index="date", columns="symbol", values="Close").sort_index()
    ranks = panel.pivot(index="date", columns="symbol", values="rank").sort_index()

    symbols = sorted(panel["symbol"].unique())
    opens = opens.reindex(columns=symbols)
    closes = closes.reindex(columns=symbols)
    ranks = ranks.reindex(columns=symbols)

    all_dates = list(opens.index)
    formal = []
    prev_map = {}
    for i, d in enumerate(all_dates):
        if d < FORMAL_START or d > FORMAL_END or i == 0:
            continue
        prev = all_dates[i - 1]
        op = opens.loc[d].to_numpy(float)
        cl = closes.loc[d].to_numpy(float)
        rr = ranks.loc[prev].to_numpy(float)
        valid = np.isfinite(op) & np.isfinite(cl) & np.isfinite(rr)
        if int(valid.sum()) < MIN_XS:
            continue
        if not valid.all():
            # Keep the research engine deterministic: Stage B only uses fully synchronous dates.
            continue
        formal.append(d)
        prev_map[d] = prev

    if len(formal) < 500:
        raise RuntimeError(f"insufficient synchronized formal dates: {len(formal)}")
    return symbols, opens, closes, ranks, formal, prev_map


def simulate_daily_target(opens, closes, ranks, formal, prev_map, bps: float, mode: str) -> dict:
    symbols = list(opens.columns)
    n = len(symbols)
    shares = np.zeros(n, dtype=float)
    cash = 1.0
    rate = bps / 10000.0
    curve = []
    dates = []
    turnover = 0.0
    rebalances = 0

    for d in formal:
        op = opens.loc[d].to_numpy(float)
        cl = closes.loc[d].to_numpy(float)

        pre = float(cash + np.sum(shares * op))
        if pre <= 0:
            raise RuntimeError("non-positive portfolio equity")

        if mode == "rank":
            raw = ranks.loc[prev_map[d]].to_numpy(float)
            raw = np.clip(raw, 0.0, 1.0)
            s = float(np.sum(raw))
            target = np.full(n, 1.0 / n) if s <= 1e-15 else raw / s
        elif mode == "equal_daily":
            target = np.full(n, 1.0 / n)
        else:
            raise ValueError(mode)

        current_pos = shares * op
        desired_pre = target * pre
        gross_trade = float(np.sum(np.abs(desired_pre - current_pos)))
        day_turn = gross_trade / pre
        cost = gross_trade * rate
        post = pre - cost
        if post <= 0:
            raise RuntimeError("cost exhausted portfolio")

        shares = target * post / op
        cash = 0.0
        turnover += day_turn
        if day_turn > 1e-12:
            rebalances += 1

        eq = float(np.sum(shares * cl))
        curve.append(eq)
        dates.append(pd.Timestamp(d))

    return metrics(np.asarray(curve), dates, turnover, rebalances)


def simulate_equal_buy_hold(opens, closes, formal, bps: float) -> dict:
    symbols = list(opens.columns)
    n = len(symbols)
    first = formal[0]
    op0 = opens.loc[first].to_numpy(float)
    rate = bps / 10000.0
    post = 1.0 - rate  # initial gross turnover is exactly 1.0
    shares = np.full(n, 1.0 / n) * post / op0

    curve = []
    dates = []
    for d in formal:
        cl = closes.loc[d].to_numpy(float)
        curve.append(float(np.sum(shares * cl)))
        dates.append(pd.Timestamp(d))

    return metrics(np.asarray(curve), dates, 1.0, 1)


def compact_benchmark(x: dict) -> dict:
    return {
        "start": x["start"],
        "end": x["end"],
        "total_return": float(x["total_return"]),
        "cagr": float(x["cagr"]),
        "max_drawdown": float(x["max_drawdown"]),
        "calmar": float(x["calmar"]),
        "turnover_mean": float(x["turnover_mean"]),
        "time_in_market_mean": float(x["time_in_market_mean"]),
    }


def build_benchmarks(bars_by, ledgers_by, bps: float) -> dict:
    v7 = {}
    sma = {}
    for s in sorted(bars_by):
        bars = bars_by[s]
        ledger = ledgers_by[s]
        v7[s] = r2.simulate_sltd(bars, ledger, bps, False)
        sma[s] = r2.simulate_sma200(bars, bps)
    return {
        "V7_BASE": compact_benchmark(r2.portfolio_metrics(v7)),
        "SMA200_TREND": compact_benchmark(r2.portfolio_metrics(sma)),
    }


def main():
    stage_a = json.loads(
        (ROOT / "SLTD_SCORE_LEVEL_RELATIVE_RANKING_V1_STAGE_A_RESULT.json").read_text(encoding="utf-8")
    )
    if stage_a["decision"] != "PROMOTED_TO_ALLOCATION_TEST":
        raise RuntimeError("Stage A did not authorize Stage B")

    stable = b.load_stable_utilities()
    if len(stable) != 82:
        raise RuntimeError(f"expected 82 frozen stable states, got {len(stable)}")

    panel, bars_by, ledgers_by = build_market_panel(stable)
    symbols, opens, closes, ranks, formal, prev_map = synchronized_matrices(panel)

    results = {}
    for bps in FRICTIONS:
        key = f"{int(bps)}bps"
        results[key] = {
            "SLTD_RANK_LINEAR": simulate_daily_target(opens, closes, ranks, formal, prev_map, bps, "rank"),
            "EQUAL_WEIGHT_DAILY": simulate_daily_target(opens, closes, ranks, formal, prev_map, bps, "equal_daily"),
            "EQUAL_WEIGHT_BUY_HOLD": simulate_equal_buy_hold(opens, closes, formal, bps),
        }
        results[key].update(build_benchmarks(bars_by, ledgers_by, bps))

    p5 = results["5bps"]
    p10 = results["10bps"]
    p20 = results["20bps"]

    years = sorted(set(p5["SLTD_RANK_LINEAR"]["annual_returns"]) & set(p5["EQUAL_WEIGHT_DAILY"]["annual_returns"]))
    year_beats = sum(
        p5["SLTD_RANK_LINEAR"]["annual_returns"][y] > p5["EQUAL_WEIGHT_DAILY"]["annual_returns"][y]
        for y in years
    )

    gates = {
        "return_gt_equal_daily_5bps":
            p5["SLTD_RANK_LINEAR"]["total_return"] > p5["EQUAL_WEIGHT_DAILY"]["total_return"],
        "calmar_gt_equal_daily_5bps":
            p5["SLTD_RANK_LINEAR"]["calmar"] > p5["EQUAL_WEIGHT_DAILY"]["calmar"],
        "return_gt_equal_buyhold_5bps":
            p5["SLTD_RANK_LINEAR"]["total_return"] > p5["EQUAL_WEIGHT_BUY_HOLD"]["total_return"],
        "calmar_gt_equal_buyhold_5bps":
            p5["SLTD_RANK_LINEAR"]["calmar"] > p5["EQUAL_WEIGHT_BUY_HOLD"]["calmar"],
        "maxdd_no_worse_than_equal_buyhold_5bps":
            p5["SLTD_RANK_LINEAR"]["max_drawdown"] >= p5["EQUAL_WEIGHT_BUY_HOLD"]["max_drawdown"],
        "return_gt_equal_daily_10bps":
            p10["SLTD_RANK_LINEAR"]["total_return"] > p10["EQUAL_WEIGHT_DAILY"]["total_return"],
        "calmar_gt_equal_daily_20bps":
            p20["SLTD_RANK_LINEAR"]["calmar"] > p20["EQUAL_WEIGHT_DAILY"]["calmar"],
        "annual_beats_equal_daily_ge_4_of_7":
            len(years) == 7 and year_beats >= 4,
        "daily_p1_no_worse_than_equal_buyhold_5bps":
            p5["SLTD_RANK_LINEAR"]["daily_p1"] >= p5["EQUAL_WEIGHT_BUY_HOLD"]["daily_p1"],
    }
    decision = "PROMOTED_TO_FRESH_OOS" if all(gates.values()) else "REJECTED_NOT_ADMITTED"

    out = {
        "meta": {
            "study": "SLTD_RELATIVE_RANKING_V1_STAGE_B",
            "protocol": "SLTD_SCORE_LEVEL_RELATIVE_RANKING_V1_PROTOCOL.md",
            "amendment": "SLTD_RELATIVE_RANKING_V1_STAGE_B_AMENDMENT_A.md",
            "stage_a_commit": "beb8f377e25417390ac38c2b2a86fa98ab04e04d",
            "stable_state_count": len(stable),
            "symbol_count": len(symbols),
            "formal_window": ["2020-01-02", "2026-09-30"],
            "development_only": True,
            "chan_used": False,
            "v7_used_as_signal": False,
            "momentum_used": False,
            "v4_probability_used": False,
            "fresh_oos_consumed": False,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        },
        "synchronized_days": len(formal),
        "results": results,
        "annual_comparison_5bps": {
            "years": years,
            "rank_beats_equal_daily_count": int(year_beats),
        },
        "gates": gates,
        "decision": decision,
    }
    OUT_JSON.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# SLTD Relative Ranking v1 — Stage B Result",
        "",
        f"Status: **{decision}**",
        "",
        "Development-only: **YES**",
        "Fresh OOS consumed: **NO**",
        "Chan/缠论: **NOT USED**",
        "V7 as signal: **NOT USED**",
        "Score Momentum: **NOT USED**",
        "v4 probability: **NOT USED**",
        "",
        f"- Symbols: **{len(symbols)}**",
        f"- Synchronized trading days: **{len(formal)}**",
        f"- 5bps annual wins vs Equal Weight Daily: **{year_beats}/{len(years)}**",
        "",
    ]

    for flabel in ("5bps", "10bps", "20bps"):
        lines += [
            f"## {flabel}",
            "",
            "| System | Total Return | CAGR | MaxDD | Calmar | Turnover | Rebalances | Daily p1 |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
        for name in ("SLTD_RANK_LINEAR","EQUAL_WEIGHT_DAILY","EQUAL_WEIGHT_BUY_HOLD"):
            z=results[flabel][name]
            lines.append(
                f"| {name} | {100*z['total_return']:.2f}% | {100*z['cagr']:.2f}% | "
                f"{100*z['max_drawdown']:.2f}% | {z['calmar']:.3f} | {z['turnover']:.2f} | "
                f"{z['rebalance_count']} | {100*z['daily_p1']:.2f}% |"
            )
        for name in ("V7_BASE","SMA200_TREND"):
            z=results[flabel][name]
            lines.append(
                f"| {name} | {100*z['total_return']:.2f}% | {100*z['cagr']:.2f}% | "
                f"{100*z['max_drawdown']:.2f}% | {z['calmar']:.3f} | {z['turnover_mean']:.2f} mean | — | — |"
            )
        lines.append("")

    lines += ["## 5bps annual returns", ""]
    lines += ["| Year | Rank Linear | Equal Weight Daily | Beat? |", "|---|---:|---:|---|"]
    for y in years:
        a=p5["SLTD_RANK_LINEAR"]["annual_returns"][y]
        e=p5["EQUAL_WEIGHT_DAILY"]["annual_returns"][y]
        lines.append(f"| {y} | {100*a:.2f}% | {100*e:.2f}% | {'YES' if a>e else 'NO'} |")

    lines += ["", "## Gates", ""]
    for k,v in gates.items():
        lines.append(f"- {k}: **{'PASS' if v else 'FAIL'}**")
    lines += [
        "",
        f"`SLTD_RELATIVE_RANKING_V1_STAGE_B = {decision}`",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps({
        "decision": decision,
        "annual_beats": year_beats,
        "results_5bps": results["5bps"],
        "gates": gates,
    }, indent=2))


if __name__ == "__main__":
    main()
