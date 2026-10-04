#!/usr/bin/env python3
"""SLTD E v1 validation on frozen A-share 50 universe.

Causal/XMA rules:
- repository build_ledger only
- completed 1d close confirms
- completed non-overlapping 5d higher bars only
- next fillable daily open executes
"""
from __future__ import annotations

import json
import math
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
RESEARCH_ROOT = ROOT.parent
INTEGRATION = ROOT.parents[2] / "integrations" / "sltd_v7_siftalpha_v1"
PHASE18 = RESEARCH_ROOT / "phase18"

sys.path.insert(0, str(INTEGRATION))

import e_strategy  # noqa: E402
import strategy as sltd_math  # noqa: E402

UNIVERSE = json.loads((PHASE18 / "A_SHARE_50_UNIVERSE_V1.json").read_text(encoding="utf-8"))
DATA_DIR = PHASE18 / "ashare50_data_snapshot_v3"

REQUESTED_START = pd.Timestamp("2018-01-02")
END = pd.Timestamp("2026-09-30")

OUT_JSON = ROOT / "SLTD_E_ASHARE50_VALIDATION_RESULT_v1.json"
OUT_MD = ROOT / "SLTD_E_ASHARE50_VALIDATION_RESULT_v1.md"

PRIMARY = {"buy_bps": 5.0, "sell_pre_bps": 15.0, "sell_post_bps": 10.0}
SENS = {"buy_bps": 10.0, "sell_pre_bps": 20.0, "sell_post_bps": 15.0}
STAMP_CHANGE = pd.Timestamp("2023-08-28")

RULE_IDS = [
    "E_BUY_1_PRIMARY_CLOSE_BREAK_BELOW_ZD1",
    "E_BUY_2_HIGHER_CLOSE_BELOW_ZD1",
    "E_BUY_3_TOUCH_GZB_BAND",
    "E_SELL_1_PRIMARY_CLOSE_BREAK_ABOVE_ZK1_MINUS_50PP",
    "E_SELL_2_TOUCH_BS_MINUS_25PP",
    "E_SELL_3_TOUCH_GZB_BAND_FULL_EXIT",
    "E_SELL_4_CLOSE_BACK_BELOW_ZK1_FULL_EXIT",
]


def candles_from_frame(frame: pd.DataFrame) -> list[dict]:
    out = []
    for r in frame.itertuples(index=False):
        d = pd.Timestamp(r.Date)
        out.append({
            "date": d.strftime("%Y-%m-%d"),
            "open_time": int(d.tz_localize("UTC").timestamp()),
            "open": float(r.Open),
            "high": float(r.High),
            "low": float(r.Low),
            "close": float(r.Close),
            "volume": 0.0 if pd.isna(r.Volume) else float(r.Volume),
        })
    return out


def read_frame(code: str) -> pd.DataFrame:
    p = DATA_DIR / f"{code}.csv.gz"
    df = pd.read_csv(p, parse_dates=["Date"])
    df["Date"] = pd.to_datetime(df["Date"]).dt.tz_localize(None)
    for c in ["Open", "High", "Low", "Close", "Volume"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return (
        df.dropna(subset=["Date", "Open", "High", "Low", "Close"])
        .sort_values("Date")
        .drop_duplicates("Date")
        .reset_index(drop=True)
    )


def prepare_symbol(code: str) -> dict:
    frame = read_frame(code)
    bars = candles_from_frame(frame)
    primary = sltd_math.build_ledger(bars, code)

    higher_tf, hbars = e_strategy.build_higher_bars(bars, "1d", {})
    if higher_tf != "5d":
        raise RuntimeError(f"{code}: expected 5d higher timeframe, got {higher_tf}")
    hledger = sltd_math.build_ledger(hbars, f"{code}:5d")

    aligned: list[tuple[int, dict] | None] = [None] * len(bars)
    h = -1
    for i in range(len(bars)):
        while h + 1 < len(hbars) and int(hbars[h + 1]["_source_end_index"]) <= i:
            h += 1
        if h >= 0:
            aligned[i] = (h, hledger[h])

    warmup_index = None
    for i in range(e_strategy.E_MIN_WARMUP_BARS - 1, len(bars)):
        pair = aligned[i]
        if pair is not None and pair[0] >= e_strategy.E_MIN_WARMUP_BARS - 1:
            warmup_index = i
            break
    if warmup_index is None:
        raise RuntimeError(f"{code}: insufficient E primary/higher warmup")

    eligible_dates = {
        pd.Timestamp(bars[i]["date"])
        for i in range(max(warmup_index, 0), len(bars))
        if REQUESTED_START <= pd.Timestamp(bars[i]["date"]) <= END
    }
    return {
        "code": code,
        "frame": frame,
        "bars": bars,
        "primary": primary,
        "higher": aligned,
        "warmup_index": warmup_index,
        "eligible_dates": eligible_dates,
    }


def common_formal_start(prepared: dict[str, dict]) -> pd.Timestamp:
    common = None
    for p in prepared.values():
        common = set(p["eligible_dates"]) if common is None else common.intersection(p["eligible_dates"])
    if not common:
        raise RuntimeError("no common E-eligible A-share date across 50 symbols")
    return min(common)


def one_price_locked(bar: dict, prev_close: float, side: str) -> bool:
    tol = max(0.001, abs(float(bar["close"])) * 1e-8)
    if abs(float(bar["high"]) - float(bar["low"])) > tol:
        return False
    if prev_close <= 0:
        return False
    gap = float(bar["open"]) / prev_close - 1.0
    return gap >= 0.095 if side == "BUY" else gap <= -0.095


def sell_rate_for(date: pd.Timestamp, costs: dict) -> float:
    bps = costs["sell_post_bps"] if date >= STAMP_CHANGE else costs["sell_pre_bps"]
    return float(bps) / 10000.0


def maxdd(curve: np.ndarray) -> float:
    if len(curve) == 0:
        return 0.0
    peak = np.maximum.accumulate(curve)
    return float(np.min(curve / peak - 1.0))


def metrics(dates: list[pd.Timestamp], curve: list[float]) -> dict:
    a = np.asarray(curve, dtype=float)
    days = max(1, (dates[-1] - dates[0]).days)
    total = float(a[-1] - 1.0)
    cagr = float(a[-1] ** (365.25 / days) - 1.0) if a[-1] > 0 else -1.0
    mdd = maxdd(a)
    calmar = cagr / abs(mdd) if mdd < -1e-12 else (999.0 if cagr > 0 else 0.0)
    return {
        "start": dates[0].strftime("%Y-%m-%d"),
        "end": dates[-1].strftime("%Y-%m-%d"),
        "observations": len(a),
        "total_return": total,
        "cagr": cagr,
        "max_drawdown": mdd,
        "calmar": float(calmar),
    }


def generate_signal(
    i: int,
    bars: list[dict],
    primary: list[dict],
    higher: list[tuple[int, dict] | None],
    position_target: float,
    b1_used: bool,
    b2_used: bool,
    b3_used: bool,
    sell_stage: int,
) -> dict | None:
    bar = bars[i]
    row = primary[i]
    pair = higher[i]
    higher_row = pair[1] if pair is not None and pair[0] >= e_strategy.E_MIN_WARMUP_BARS - 1 else None

    signal = None
    if position_target > 1e-12:
        inner_up = e_strategy._break_above_zk1(i, bars, primary)
        exit_active = sell_stage > 0 or inner_up
        band_hit = e_strategy._band_touch(bar, row)
        bs = row.get("BS")
        bs_hit = bs is not None and float(bar["high"]) >= float(bs)

        if exit_active and band_hit:
            signal = {
                "kind": "EXIT",
                "rule_ids": ["E_SELL_3_TOUCH_GZB_BAND_FULL_EXIT"],
            }
        elif (
            sell_stage > 0
            and row.get("ZK1") is not None
            and float(bar["close"]) < float(row["ZK1"])
        ):
            signal = {
                "kind": "EXIT",
                "rule_ids": ["E_SELL_4_CLOSE_BACK_BELOW_ZK1_FULL_EXIT"],
            }
        elif exit_active and bs_hit:
            signal = {
                "kind": "SELL25",
                "rule_ids": ["E_SELL_2_TOUCH_BS_MINUS_25PP"],
            }
        elif sell_stage == 0 and inner_up:
            signal = {
                "kind": "SELL50",
                "rule_ids": ["E_SELL_1_PRIMARY_CLOSE_BREAK_ABOVE_ZK1_MINUS_50PP"],
            }

    if signal is None and sell_stage == 0:
        state = str(row.get("color") or "")
        inner_down = (
            not b1_used
            and state in {"BLUE", "GRAY"}
            and e_strategy._break_below_zd1(i, bars, primary)
        )
        if inner_down:
            rule_ids = ["E_BUY_1_PRIMARY_CLOSE_BREAK_BELOW_ZD1"]
            delta = 0.25
            if (
                not b2_used
                and higher_row is not None
                and higher_row.get("ZD1") is not None
                and float(higher_row["close"]) < float(higher_row["ZD1"])
            ):
                rule_ids.append("E_BUY_2_HIGHER_CLOSE_BELOW_ZD1")
                delta += 0.25
            signal = {"kind": "BUY", "delta": delta, "rule_ids": rule_ids}
        elif b1_used and not b3_used and e_strategy._band_touch(bar, row):
            signal = {
                "kind": "BUY",
                "delta": 0.25,
                "rule_ids": ["E_BUY_3_TOUCH_GZB_BAND"],
            }
    return signal


def simulate_e(prep: dict, formal_start: pd.Timestamp, costs: dict) -> dict:
    bars = prep["bars"]
    primary = prep["primary"]
    higher = prep["higher"]

    indices = [
        i for i, b in enumerate(bars)
        if formal_start <= pd.Timestamp(b["date"]) <= END
    ]
    if len(indices) < 2:
        raise RuntimeError(f"{prep['code']}: insufficient formal bars")

    cash = 1.0
    shares = 0.0
    target = 0.0
    b1_used = b2_used = b3_used = False
    sell_stage = 0
    pending = None

    turnover = 0.0
    position_changes = 0
    invested_obs = 0
    rule_exec = Counter()
    blocked_buy = 0
    blocked_sell = 0
    dates: list[pd.Timestamp] = []
    curve: list[float] = []

    buy_rate = costs["buy_bps"] / 10000.0

    for i in indices:
        bar = bars[i]
        date = pd.Timestamp(bar["date"])
        op = float(bar["open"])
        cl = float(bar["close"])
        prev_close = float(bars[i - 1]["close"]) if i > 0 else op

        # Exact pending action retries until fillable. While blocked, no new signal is accepted.
        pending_blocked = False
        if pending is not None:
            side = "BUY" if pending["kind"] == "BUY" else "SELL"
            blocked = one_price_locked(bar, prev_close, side)
            if blocked:
                pending_blocked = True
                if side == "BUY":
                    blocked_buy += 1
                else:
                    blocked_sell += 1
            else:
                before_target = target
                before_equity = cash + shares * op
                kind = pending["kind"]

                if kind == "BUY":
                    target = min(e_strategy.E_MAX_POSITION, target + float(pending["delta"]))
                    if "E_BUY_1_PRIMARY_CLOSE_BREAK_BELOW_ZD1" in pending["rule_ids"]:
                        b1_used = True
                    if "E_BUY_2_HIGHER_CLOSE_BELOW_ZD1" in pending["rule_ids"]:
                        b2_used = True
                    if "E_BUY_3_TOUCH_GZB_BAND" in pending["rule_ids"]:
                        b3_used = True
                elif kind == "SELL50":
                    target = max(0.0, target - 0.50)
                    sell_stage = max(sell_stage, 1)
                elif kind == "SELL25":
                    target = max(0.0, target - 0.25)
                    sell_stage = max(sell_stage, 2)
                elif kind == "EXIT":
                    target = 0.0

                current_pos = shares * op
                desired_pos = target * before_equity
                order = desired_pos - current_pos
                if target <= 1e-12:
                    order = -current_pos

                if order > 1e-14:
                    max_buy = max(0.0, cash / (1.0 + buy_rate))
                    order = min(order, max_buy)
                    if order > 1e-14:
                        cost = order * buy_rate
                        shares += order / op
                        cash -= order + cost
                        turnover += order / before_equity if before_equity > 0 else 0.0
                elif order < -1e-14:
                    order = max(order, -current_pos)
                    sell_rate = sell_rate_for(date, costs)
                    cost = abs(order) * sell_rate
                    shares += order / op
                    cash -= order + cost
                    turnover += abs(order) / before_equity if before_equity > 0 else 0.0
                    if shares <= 1e-12:
                        shares = 0.0

                if abs(target - before_target) > 1e-12:
                    position_changes += 1
                for rid in pending["rule_ids"]:
                    rule_exec[rid] += 1

                if target <= 1e-12:
                    target = 0.0
                    b1_used = b2_used = b3_used = False
                    sell_stage = 0
                    shares = 0.0 if shares <= 1e-12 else shares

                pending = None

        if not pending_blocked and pending is None:
            signal = generate_signal(
                i, bars, primary, higher, target,
                b1_used, b2_used, b3_used, sell_stage
            )
            if signal is not None:
                pending = {
                    **signal,
                    "signal_date": bar["date"],
                }

        eq = cash + shares * cl
        curve.append(float(eq))
        dates.append(date)
        if shares * cl > 1e-12:
            invested_obs += 1

    out = metrics(dates, curve)
    out.update({
        "dates": [d.strftime("%Y-%m-%d") for d in dates],
        "curve": curve,
        "time_in_market": invested_obs / len(dates),
        "turnover": float(turnover),
        "position_changes": int(position_changes),
        "rule_exec": {rid: int(rule_exec.get(rid, 0)) for rid in RULE_IDS},
        "blocked_buy_attempts": int(blocked_buy),
        "blocked_sell_attempts": int(blocked_sell),
    })
    return out


def simulate_buy_hold(prep: dict, formal_start: pd.Timestamp, costs: dict) -> dict:
    bars = prep["bars"]
    indices = [
        i for i, b in enumerate(bars)
        if formal_start <= pd.Timestamp(b["date"]) <= END
    ]
    cash = 1.0
    shares = 0.0
    pending = True
    dates = []
    curve = []
    blocked_buy = 0
    buy_rate = costs["buy_bps"] / 10000.0

    for i in indices:
        b = bars[i]
        date = pd.Timestamp(b["date"])
        op = float(b["open"])
        prev_close = float(bars[i - 1]["close"]) if i > 0 else op
        if pending:
            if one_price_locked(b, prev_close, "BUY"):
                blocked_buy += 1
            else:
                invest = cash / (1.0 + buy_rate)
                cost = invest * buy_rate
                shares = invest / op
                cash -= invest + cost
                pending = False
        eq = cash + shares * float(b["close"])
        curve.append(float(eq))
        dates.append(date)

    out = metrics(dates, curve)
    out.update({
        "dates": [d.strftime("%Y-%m-%d") for d in dates],
        "curve": curve,
        "time_in_market": float(np.mean([1.0 if x > 1e-14 else 0.0 for x in np.asarray(curve) - cash])),
        "turnover": 1.0 if shares > 0 else 0.0,
        "position_changes": 1 if shares > 0 else 0,
        "blocked_buy_attempts": int(blocked_buy),
    })
    return out


def aggregate(per: dict[str, dict]) -> dict:
    series = []
    for code, r in per.items():
        s = pd.Series(r["curve"], index=pd.to_datetime(r["dates"]), name=code, dtype=float)
        series.append(s)
    df = pd.concat(series, axis=1).sort_index().ffill()
    # Start only once every sleeve has a value.
    df = df.dropna()
    portfolio_curve = df.mean(axis=1).to_numpy(float)
    dates = [pd.Timestamp(x) for x in df.index]
    out = metrics(dates, portfolio_curve)
    out.update({
        "time_in_market_mean": float(np.mean([r["time_in_market"] for r in per.values()])),
        "turnover_mean": float(np.mean([r["turnover"] for r in per.values()])),
        "position_changes_sum": int(sum(r["position_changes"] for r in per.values())),
        "profitable_symbols": int(sum(r["total_return"] > 0 for r in per.values())),
        "positive_calmar_symbols": int(sum(r["calmar"] > 0 for r in per.values())),
    })
    return out


def sliced_portfolio(per: dict[str, dict], start: pd.Timestamp, end: pd.Timestamp) -> dict | None:
    series = []
    for code, r in per.items():
        s = pd.Series(r["curve"], index=pd.to_datetime(r["dates"]), name=code, dtype=float)
        series.append(s)
    df = pd.concat(series, axis=1).sort_index().ffill().dropna()
    df = df.loc[(df.index >= start) & (df.index <= end)]
    if len(df) < 2:
        return None
    curve = df.mean(axis=1).to_numpy(float)
    curve = curve / curve[0]
    return metrics([pd.Timestamp(x) for x in df.index], curve.tolist())


def breadth(e: dict[str, dict], bh: dict[str, dict]) -> dict:
    codes = sorted(e)
    dr = np.asarray([e[c]["total_return"] - bh[c]["total_return"] for c in codes], dtype=float)
    dd = np.asarray([e[c]["max_drawdown"] - bh[c]["max_drawdown"] for c in codes], dtype=float)
    dc = np.asarray([e[c]["calmar"] - bh[c]["calmar"] for c in codes], dtype=float)
    return {
        "e_better_return": int(np.sum(dr > 0)),
        "e_better_maxdd": int(np.sum(dd > 0)),
        "e_better_calmar": int(np.sum(dc > 0)),
        "symbol_count": len(codes),
        "median_delta_return": float(np.median(dr)),
        "median_delta_maxdd": float(np.median(dd)),
        "median_delta_calmar": float(np.median(dc)),
    }


def main():
    symbols = UNIVERSE["symbols"]
    if len(symbols) != 50:
        raise RuntimeError("expected frozen 50-symbol universe")

    prepared = {x["code"]: prepare_symbol(x["code"]) for x in symbols}
    formal_start = common_formal_start(prepared)

    results = {}
    for label, costs in (("primary", PRIMARY), ("sensitivity", SENS)):
        e_per = {}
        bh_per = {}
        for item in symbols:
            code = item["code"]
            e_per[code] = simulate_e(prepared[code], formal_start, costs)
            bh_per[code] = simulate_buy_hold(prepared[code], formal_start, costs)

        rule_totals = Counter()
        blocked_buy = blocked_sell = 0
        for r in e_per.values():
            rule_totals.update(r["rule_exec"])
            blocked_buy += int(r["blocked_buy_attempts"])
            blocked_sell += int(r["blocked_sell_attempts"])

        results[label] = {
            "costs": costs,
            "portfolio": {
                "E": aggregate(e_per),
                "BUY_AND_HOLD": aggregate(bh_per),
            },
            "breadth_vs_buy_hold": breadth(e_per, bh_per),
            "rule_execution_totals": {rid: int(rule_totals.get(rid, 0)) for rid in RULE_IDS},
            "blocked_buy_attempts": int(blocked_buy),
            "blocked_sell_attempts": int(blocked_sell),
            "eras": {
                "EARLY": {
                    "E": sliced_portfolio(e_per, formal_start, pd.Timestamp("2020-12-31")),
                    "BUY_AND_HOLD": sliced_portfolio(bh_per, formal_start, pd.Timestamp("2020-12-31")),
                },
                "MIDDLE": {
                    "E": sliced_portfolio(e_per, pd.Timestamp("2021-01-01"), pd.Timestamp("2023-12-31")),
                    "BUY_AND_HOLD": sliced_portfolio(bh_per, pd.Timestamp("2021-01-01"), pd.Timestamp("2023-12-31")),
                },
                "LATE": {
                    "E": sliced_portfolio(e_per, pd.Timestamp("2024-01-01"), END),
                    "BUY_AND_HOLD": sliced_portfolio(bh_per, pd.Timestamp("2024-01-01"), END),
                },
            },
            "per_symbol": {
                "E": {c: {k:v for k,v in r.items() if k not in {"dates","curve"}} for c,r in e_per.items()},
                "BUY_AND_HOLD": {c: {k:v for k,v in r.items() if k not in {"dates","curve"}} for c,r in bh_per.items()},
            },
        }

    out = {
        "meta": {
            "study": "SLTD_E_ASHARE50_VALIDATION_V1",
            "market": "China A-share main board",
            "symbol_count": 50,
            "requested_start": REQUESTED_START.strftime("%Y-%m-%d"),
            "actual_common_formal_start": formal_start.strftime("%Y-%m-%d"),
            "end": END.strftime("%Y-%m-%d"),
            "primary_timeframe": "1d",
            "higher_timeframe": "5d",
            "xma_causal": True,
            "e_strategy_blob_sha": "722fc7cc716f39ee07e58bd2f57d112659a4499c",
            "all_50_used": True,
            "previous_fresh15_consumed_for_this_e_study": True,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        },
        "results": results,
        "status": "COMPLETE",
    }
    OUT_JSON.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    p = results["primary"]
    ep = p["portfolio"]["E"]
    bp = p["portfolio"]["BUY_AND_HOLD"]
    br = p["breadth_vs_buy_hold"]

    def pct(x): return f"{100*float(x):.2f}%"

    lines = [
        "# SLTD E A-share 50 Validation v1","",
        "Status: **COMPLETE**","",
        f"- Symbols: **50**",
        f"- Requested start: **{REQUESTED_START.date()}**",
        f"- Actual common E-valid start after XMA/5d warmup: **{formal_start.date()}**",
        f"- End: **{END.date()}**",
        "- Primary timeframe: **1d**",
        "- Higher timeframe: **completed 5d**",
        "- XMA causal / no future backfill: **YES**","",
        "## Equal-weight 50-stock portfolio — primary costs","",
        "| System | Return | CAGR | MaxDD | Calmar | Time in market | Mean turnover | Changes |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
        f"| E | {pct(ep['total_return'])} | {pct(ep['cagr'])} | {pct(ep['max_drawdown'])} | "
        f"{ep['calmar']:.3f} | {pct(ep['time_in_market_mean'])} | {ep['turnover_mean']:.2f} | {ep['position_changes_sum']} |",
        f"| Buy & Hold | {pct(bp['total_return'])} | {pct(bp['cagr'])} | {pct(bp['max_drawdown'])} | "
        f"{bp['calmar']:.3f} | {pct(bp['time_in_market_mean'])} | {bp['turnover_mean']:.2f} | {bp['position_changes_sum']} |",
        "",
        "## Breadth — E vs Buy & Hold","",
        f"- Better Return: **{br['e_better_return']}/50**",
        f"- Better MaxDD: **{br['e_better_maxdd']}/50**",
        f"- Better Calmar: **{br['e_better_calmar']}/50**",
        f"- Median ΔReturn: **{pct(br['median_delta_return'])}**",
        f"- Median ΔMaxDD: **{pct(br['median_delta_maxdd'])}**",
        f"- Median ΔCalmar: **{br['median_delta_calmar']:.3f}**","",
        "## E rule executions — primary costs","",
    ]
    for rid in RULE_IDS:
        lines.append(f"- {rid}: **{p['rule_execution_totals'][rid]}**")
    lines += [
        f"- blocked BUY attempts: **{p['blocked_buy_attempts']}**",
        f"- blocked SELL attempts: **{p['blocked_sell_attempts']}**","",
        "## Era Calmar — primary costs","",
        "| Era | E | Buy & Hold |",
        "|---|---:|---:|",
    ]
    for era in ["EARLY","MIDDLE","LATE"]:
        e = p["eras"][era]["E"]
        b = p["eras"][era]["BUY_AND_HOLD"]
        lines.append(f"| {era} | {e['calmar']:.3f} | {b['calmar']:.3f} |")
    lines += [
        "",
        "## Interpretation boundary","",
        "- E rules were not retuned.",
        "- All 50 frozen A-share symbols were used.",
        "- The previous Fresh15 is consumed for this separate E study only.",
        "- No conclusion from prior U.S. E results was imported into this A-share result.",
        "",
        "`SLTD_E_ASHARE50_VALIDATION_V1 = COMPLETE`",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps({
        "formal_start": formal_start.strftime("%Y-%m-%d"),
        "portfolio_primary": p["portfolio"],
        "breadth_primary": br,
        "rules_primary": p["rule_execution_totals"],
        "blocked": {
            "buy": p["blocked_buy_attempts"],
            "sell": p["blocked_sell_attempts"],
        },
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
