#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
APP = ROOT / "integrations" / "sltd_v7_siftalpha_v1"
sys.path.insert(0, str(APP))

import data_provider
import strategy

OUT_JSON = Path(__file__).with_name("SLTD_V8_UNIVERSAL_SELL_STUDY_R1_RESULT.json")
OUT_MD = Path(__file__).with_name("SLTD_V8_UNIVERSAL_SELL_STUDY_R1_RESULT.md")

SYMBOLS = [
    "AAPL","MSFT","NVDA","AMZN","META",
    "TSLA","WMT","COST","ABT","LLY",
    "UNH","JPM","BAC","V","CAT",
    "XOM","NEE","PLD","IBM","DIS",
]
TIMEFRAMES = ("1h", "4h", "1d")
FORMAL_START = "2025-02-03"
FORMAL_END = "2026-09-30"
FRICTION_BPS = 5.0

VARIANTS = (
    "BASE",
    "S1_MATURE_BLUE_UPPER_WICK",
    "S2_MATURE_BLUE_UPPER_ANY",
    "S3_BLUE_TO_GRAY_TRANSITION",
    "S4_BLUE_TO_GRAY_UPPER",
    "S5_WICK_PLUS_TRANSITION",
    "S6_WICK_PLUS_GRAY_UPPER",
    "S7_TRANSITION_PLUS_GRAY_UPPER",
)

VARIANT_NAMES_ZH = {
    "BASE": "V7 当前卖出基线",
    "S1_MATURE_BLUE_UPPER_WICK": "成熟蓝色21+：上轨仅影线减仓",
    "S2_MATURE_BLUE_UPPER_ANY": "成熟蓝色21+：任何上轨事件减仓",
    "S3_BLUE_TO_GRAY_TRANSITION": "蓝转灰首根：结构降级减仓",
    "S4_BLUE_TO_GRAY_UPPER": "蓝转灰前10根：上轨压力减仓",
    "S5_WICK_PLUS_TRANSITION": "成熟蓝色上轨影线 + 蓝转灰首根",
    "S6_WICK_PLUS_GRAY_UPPER": "成熟蓝色上轨影线 + 蓝转灰上轨压力",
    "S7_TRANSITION_PLUS_GRAY_UPPER": "蓝转灰首根 + 蓝转灰上轨压力",
}


def median(values):
    values = [float(x) for x in values if x is not None and math.isfinite(float(x))]
    return statistics.median(values) if values else None


def max_drawdown(curve):
    peak = None
    worst = 0.0
    for value in curve:
        value = float(value)
        peak = value if peak is None else max(peak, value)
        if peak and peak > 0:
            worst = min(worst, value / peak - 1.0)
    return worst


def in_formal(date_text: str) -> bool:
    day = str(date_text)[:10]
    return FORMAL_START <= day <= FORMAL_END


def extra_sell_hits(row: dict, variant: str) -> list[str]:
    if variant == "BASE":
        return []

    state = str(row.get("color") or "")
    age = int(row.get("run_age") or 0)
    origin = row.get("origin")
    upper = bool(row.get("upper"))
    subtype = row.get("upper_subtype")

    s1 = state == "BLUE" and age >= 21 and upper and subtype == "WICK_ONLY"
    s2 = state == "BLUE" and age >= 21 and upper
    s3 = state == "GRAY" and origin == "BLUE" and age == 1
    s4 = state == "GRAY" and origin == "BLUE" and age <= 10 and upper

    hits = []
    if variant in ("S1_MATURE_BLUE_UPPER_WICK", "S5_WICK_PLUS_TRANSITION", "S6_WICK_PLUS_GRAY_UPPER") and s1:
        hits.append("成熟蓝色21+：上轨仅影线")
    if variant == "S2_MATURE_BLUE_UPPER_ANY" and s2:
        hits.append("成熟蓝色21+：任何上轨事件")
    if variant in ("S3_BLUE_TO_GRAY_TRANSITION", "S5_WICK_PLUS_TRANSITION", "S7_TRANSITION_PLUS_GRAY_UPPER") and s3:
        hits.append("蓝转灰首根")
    if variant in ("S4_BLUE_TO_GRAY_UPPER", "S6_WICK_PLUS_GRAY_UPPER", "S7_TRANSITION_PLUS_GRAY_UPPER") and s4:
        hits.append("蓝转灰前10根：上轨压力")
    return hits


def resolve_variant(row: dict | None, variant: str):
    if row is None:
        return None, [], ()
    classes = list(strategy.action_classes(row))
    hits = extra_sell_hits(row, variant)
    if hits and "SELL" not in classes:
        classes.append("SELL")
    ordered = tuple(x for x in strategy.ACTION_ORDER if x in classes)
    if len(ordered) == 1:
        return ordered[0], hits, ordered
    return None, hits, ordered


def simulate_variant(bars: list[dict], ledger: list[dict], variant: str) -> dict:
    formal_indices = [i for i, b in enumerate(bars) if in_formal(b["date"])]
    if len(formal_indices) < 2:
        raise RuntimeError("formal window has fewer than two bars")

    first_i = formal_indices[0]
    last_i = formal_indices[-1]
    cash = 1.0
    shares = 0.0
    risk_armed = False
    cost_rate = FRICTION_BPS / 10000.0
    curve = []
    turnover = 0.0
    buys = sells = hard_exits = 0
    invested = 0
    extra_sell_execs = []
    all_sell_execs = []

    for j in formal_indices:
        bar = bars[j]
        op = float(bar["open"])
        cl = float(bar["close"])
        pre_equity = cash + shares * op
        if pre_equity <= 0:
            raise RuntimeError("non-positive equity")

        position_value = shares * op
        current_fraction = position_value / pre_equity

        # 不允许正式窗口之前的信号在正式窗口第一根开盘成交。
        signal = ledger[j - 1] if j > first_i else None
        hard = bool(shares > 1e-14 and risk_armed and strategy.c2_condition(signal))
        action, extra_hits, classes = resolve_variant(signal, variant)

        order_value = 0.0
        ordinary_action = None
        side = None

        if hard:
            order_value = -position_value
            side = "X"
        else:
            ordinary_action = action
            if action == "BUY":
                desired = 0.25 if shares <= 1e-14 else min(1.0, current_fraction + 0.25)
                desired = max(current_fraction, desired)
                order_value = desired * pre_equity - position_value
                side = "B"
            elif action == "SELL" and shares > 0:
                order_value = -position_value * 0.25
                side = "S"

        if order_value > 1e-14:
            max_buy = max(0.0, cash / (1.0 + cost_rate))
            order_value = min(order_value, max_buy)
        elif order_value < -1e-14:
            order_value = max(order_value, -position_value)

        executed = abs(order_value) > 1e-14
        if executed:
            cost = abs(order_value) * cost_rate
            turnover += abs(order_value) / pre_equity
            shares += order_value / op
            cash -= order_value + cost
            if shares <= 1e-12:
                shares = 0.0

            if side == "B":
                buys += 1
            elif side == "S":
                sells += 1
            elif side == "X":
                hard_exits += 1

        if hard and executed:
            risk_armed = False
        elif executed and ordinary_action == "SELL" and order_value < 0:
            risk_armed = True
        elif executed and ordinary_action == "BUY" and order_value > 0:
            risk_armed = False

        close_equity = cash + shares * cl
        curve.append(close_equity)
        if shares > 1e-12:
            invested += 1

        if executed and side == "S" and signal is not None:
            rec = {
                "signal_date": signal["date"],
                "execution_date": bar["date"],
                "execution_index": j,
                "execution_price": op,
                "extra_hits": extra_hits,
                "classes": classes,
            }
            all_sell_execs.append(rec)
            if extra_hits:
                extra_sell_execs.append(rec)

    first_date = bars[first_i]["date"][:10]
    last_date = bars[last_i]["date"][:10]
    days = max(
        1,
        (
            datetime.strptime(last_date, "%Y-%m-%d")
            - datetime.strptime(first_date, "%Y-%m-%d")
        ).days,
    )
    final_equity = curve[-1]
    total_return = final_equity - 1.0
    cagr = final_equity ** (365.25 / days) - 1.0 if final_equity > 0 else -1.0
    mdd = max_drawdown(curve)
    calmar = cagr / abs(mdd) if mdd < -1e-12 else (999.0 if cagr > 0 else 0.0)

    def add_forward(records):
        out = []
        for rec in records:
            r = dict(rec)
            j = int(rec["execution_index"])
            px = float(rec["execution_price"])
            for horizon in (3, 5, 10):
                k = j + horizon - 1
                if k <= last_i:
                    r[f"fwd_{horizon}"] = float(bars[k]["close"]) / px - 1.0
                else:
                    r[f"fwd_{horizon}"] = None
            out.append(r)
        return out

    return {
        "total_return": total_return,
        "cagr": cagr,
        "max_drawdown": mdd,
        "calmar": calmar,
        "turnover": turnover,
        "buy_execs": buys,
        "sell_execs": sells,
        "hard_exit_execs": hard_exits,
        "invested_ratio": invested / len(formal_indices),
        "all_sell_execs": add_forward(all_sell_execs),
        "extra_sell_execs": add_forward(extra_sell_execs),
        "formal_bars": len(formal_indices),
        "formal_first": bars[first_i]["date"],
        "formal_last": bars[last_i]["date"],
    }


def fetch_with_retry(symbol: str, timeframe: str):
    last = None
    for attempt in range(4):
        try:
            return data_provider.fetch_bars(
                symbol,
                timeframe,
                start_date="2020-01-02",
                force_refresh=True,
            )
        except Exception as exc:
            last = exc
            if attempt == 3:
                raise
            time.sleep(1.5 * (attempt + 1))
    raise last


def fetch_symbol_data(symbol: str) -> dict[str, list[dict]]:
    # 研究窗口需要比 App 默认 365 天更长的小时线历史，以给 4h 足够预热。
    old_1h = data_provider.TIMEFRAMES["1h"].get("lookback_days")
    old_4h = data_provider.TIMEFRAMES["4h"].get("lookback_days")
    data_provider.TIMEFRAMES["1h"]["lookback_days"] = 700
    data_provider.TIMEFRAMES["4h"]["lookback_days"] = 700
    try:
        one_hour, _, meta_1h = fetch_with_retry(symbol, "1h")
        time.sleep(0.15)
        daily, _, meta_1d = fetch_with_retry(symbol, "1d")
    finally:
        data_provider.TIMEFRAMES["1h"]["lookback_days"] = old_1h
        data_provider.TIMEFRAMES["4h"]["lookback_days"] = old_4h

    # 用同一份 1h 数据生成 4h，避免两次网络请求产生边界差异。
    source = [dict(x, complete=True) for x in one_hour]
    now_ts = int(time.time())
    four_raw = data_provider._aggregate_four_hour_bars(
        source,
        exchange_timezone=meta_1h.get("exchange_timezone"),
        regular_start=meta_1h.get("regular_market_start"),
        regular_end=meta_1h.get("regular_market_end"),
        now_ts=now_ts,
    )
    four_hour = [
        {k: v for k, v in row.items() if k not in ("complete", "source_bars")}
        for row in four_raw
        if row.get("complete")
    ]
    return {"1h": one_hour, "4h": four_hour, "1d": daily}


def summarize(records: list[dict]) -> dict:
    out = {}
    base_by_cell = {
        (r["symbol"], r["timeframe"]): r
        for r in records
        if r["variant"] == "BASE"
    }

    for variant in VARIANTS:
        vr = [r for r in records if r["variant"] == variant]
        by_tf = {}
        for tf in TIMEFRAMES:
            rows = [r for r in vr if r["timeframe"] == tf]
            base_rows = [base_by_cell[(r["symbol"], tf)] for r in rows]
            by_tf[tf] = {
                "cells": len(rows),
                "median_total_return": median(r["total_return"] for r in rows),
                "median_cagr": median(r["cagr"] for r in rows),
                "median_max_drawdown": median(r["max_drawdown"] for r in rows),
                "median_calmar": median(r["calmar"] for r in rows),
                "median_turnover": median(r["turnover"] for r in rows),
                "median_sell_execs": median(r["sell_execs"] for r in rows),
                "delta_median_total_return_vs_base": (
                    median(r["total_return"] for r in rows)
                    - median(r["total_return"] for r in base_rows)
                ),
                "delta_median_max_drawdown_vs_base": (
                    median(r["max_drawdown"] for r in rows)
                    - median(r["max_drawdown"] for r in base_rows)
                ),
                "delta_median_calmar_vs_base": (
                    median(r["calmar"] for r in rows)
                    - median(r["calmar"] for r in base_rows)
                ),
                "better_calmar_symbols": sum(
                    1 for r in rows
                    if r["calmar"] > base_by_cell[(r["symbol"], tf)]["calmar"] + 1e-12
                ),
                "better_return_symbols": sum(
                    1 for r in rows
                    if r["total_return"] > base_by_cell[(r["symbol"], tf)]["total_return"] + 1e-12
                ),
            }

        extra_execs = [
            e for r in vr for e in r["extra_sell_execs"]
        ]
        overall_better_calmar = sum(
            1 for r in vr
            if r["calmar"] > base_by_cell[(r["symbol"], r["timeframe"])]["calmar"] + 1e-12
        )
        overall_better_return = sum(
            1 for r in vr
            if r["total_return"] > base_by_cell[(r["symbol"], r["timeframe"])]["total_return"] + 1e-12
        )
        out[variant] = {
            "name_zh": VARIANT_NAMES_ZH[variant],
            "by_timeframe": by_tf,
            "overall_cells": len(vr),
            "overall_better_calmar_cells": overall_better_calmar,
            "overall_better_return_cells": overall_better_return,
            "overall_median_delta_calmar": median(
                r["calmar"] - base_by_cell[(r["symbol"], r["timeframe"])]["calmar"]
                for r in vr
            ),
            "overall_median_delta_return": median(
                r["total_return"] - base_by_cell[(r["symbol"], r["timeframe"])]["total_return"]
                for r in vr
            ),
            "extra_sell_execs": len(extra_execs),
            "extra_sell_median_fwd_3": median(e.get("fwd_3") for e in extra_execs),
            "extra_sell_median_fwd_5": median(e.get("fwd_5") for e in extra_execs),
            "extra_sell_median_fwd_10": median(e.get("fwd_10") for e in extra_execs),
        }

    # 按协议自动给出 R2 初筛，不直接修改正式 V7。
    shortlist = []
    for variant in VARIANTS:
        if variant == "BASE":
            continue
        s = out[variant]
        positive_tf = sum(
            1
            for tf in TIMEFRAMES
            if s["by_timeframe"][tf]["delta_median_calmar_vs_base"] > 0
        )
        better_ratio = s["overall_better_calmar_cells"] / max(1, s["overall_cells"])
        mdd_deltas = [
            s["by_timeframe"][tf]["delta_median_max_drawdown_vs_base"]
            for tf in TIMEFRAMES
        ]
        median_mdd_delta = median(mdd_deltas)
        if (
            positive_tf >= 2
            and better_ratio > 0.50
            and median_mdd_delta is not None
            and median_mdd_delta >= -1e-12
            and s["overall_median_delta_return"] is not None
            and s["overall_median_delta_return"] >= -0.005
        ):
            shortlist.append(variant)

    return out, shortlist


def main() -> None:
    records = []
    fetch_report = {}

    for idx, symbol in enumerate(SYMBOLS, 1):
        print(f"[{idx}/{len(SYMBOLS)}] fetch {symbol}", flush=True)
        data = fetch_symbol_data(symbol)
        fetch_report[symbol] = {tf: len(data[tf]) for tf in TIMEFRAMES}

        for tf in TIMEFRAMES:
            bars = data[tf]
            ledger = strategy.build_ledger(bars, symbol)
            for variant in VARIANTS:
                metrics = simulate_variant(bars, ledger, variant)
                records.append({
                    "symbol": symbol,
                    "timeframe": tf,
                    "variant": variant,
                    **metrics,
                })
        time.sleep(0.15)

    summary, shortlist = summarize(records)
    payload = {
        "status": "IMPLEMENTED_AND_VERIFIED",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "formal_window": [FORMAL_START, FORMAL_END],
        "friction_bps": FRICTION_BPS,
        "symbols": SYMBOLS,
        "timeframes": TIMEFRAMES,
        "variants": VARIANTS,
        "fetch_report": fetch_report,
        "summary": summary,
        "shortlist_for_r2": shortlist,
        "records": records,
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# SLTD V8 Universal Sell Study R1 Result",
        "",
        "状态：IMPLEMENTED_AND_VERIFIED",
        "",
        f"- 股票：{len(SYMBOLS)}",
        f"- 周期：{', '.join(TIMEFRAMES)}",
        f"- 正式窗口：{FORMAL_START} .. {FORMAL_END}",
        f"- friction：{FRICTION_BPS} bps",
        "",
        "## 汇总",
        "",
        "| Variant | 1h ΔCalmar | 4h ΔCalmar | 1d ΔCalmar | Better Calmar | ΔReturn median | Extra SELL | fwd5 | fwd10 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for variant in VARIANTS:
        s = summary[variant]
        def fmt(x):
            return "NA" if x is None else f"{x:.4f}"
        lines.append(
            f"| {variant} | "
            f"{fmt(s['by_timeframe']['1h']['delta_median_calmar_vs_base'])} | "
            f"{fmt(s['by_timeframe']['4h']['delta_median_calmar_vs_base'])} | "
            f"{fmt(s['by_timeframe']['1d']['delta_median_calmar_vs_base'])} | "
            f"{s['overall_better_calmar_cells']}/{s['overall_cells']} | "
            f"{fmt(s['overall_median_delta_return'])} | "
            f"{s['extra_sell_execs']} | "
            f"{fmt(s['extra_sell_median_fwd_5'])} | "
            f"{fmt(s['extra_sell_median_fwd_10'])} |"
        )

    lines += ["", "## R2 初筛", ""]
    if shortlist:
        for v in shortlist:
            lines.append(f"- {v}: {VARIANT_NAMES_ZH[v]}")
    else:
        lines.append("- 本轮没有候选同时满足预设 R2 晋级门槛。")

    lines += ["", "## 各周期中位指标", ""]
    for variant in VARIANTS:
        lines.append(f"### {variant} — {VARIANT_NAMES_ZH[variant]}")
        for tf in TIMEFRAMES:
            x = summary[variant]["by_timeframe"][tf]
            lines.append(
                f"- {tf}: Return {x['median_total_return']:.4f}, "
                f"MaxDD {x['median_max_drawdown']:.4f}, "
                f"Calmar {x['median_calmar']:.4f}, "
                f"turnover {x['median_turnover']:.4f}, "
                f"betterCalmar {x['better_calmar_symbols']}/{x['cells']}"
            )
        lines.append("")

    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(OUT_MD.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
