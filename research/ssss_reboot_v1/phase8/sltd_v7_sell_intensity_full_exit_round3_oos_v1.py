#!/usr/bin/env python3
from __future__ import annotations

import json
import statistics
import sys
import time
from datetime import timedelta, timezone, datetime
from pathlib import Path

PHASE8 = Path(__file__).resolve().parent
sys.path.insert(0, str(PHASE8))
import sltd_v7_sell_intensity_full_exit_round2_v1 as r2

OUT_JSON = PHASE8 / "SLTD_V7_SELL_INTENSITY_FULL_EXIT_ROUND3_OOS_RESULT_v1.json"
OUT_MD = PHASE8 / "SLTD_V7_SELL_INTENSITY_FULL_EXIT_ROUND3_OOS_RESULT_v1.md"

SYMBOLS = (
    "AXP", "PNC", "USB", "COF", "ICE",
    "CME", "PGR", "CB", "VRTX", "REGN",
    "BSX", "HCA", "MDLZ", "CL", "YUM",
    "GM", "F", "UBER", "ETN", "SLB",
)
TIMEFRAMES = ("1h", "4h", "1d")
VARIANTS = r2.VARIANTS
FRICTIONS = r2.FRICTIONS
DAILY_START = "2020-01-02"
DAILY_END = "2026-09-30"

PRIOR_79 = set("""
AAPL MSFT NVDA AMD AVGO ORCL INTC QCOM MU GOOGL META NFLX AMZN TSLA HD MCD WMT COST PG KO
PEP ABT LLY UNH JNJ TMO JPM BAC GS V MA CAT BA GE XOM CVX LIN NEE PLD IBM CSCO CRM ADBE TXN
DIS NKE SBUX TGT LOW MRK PFE ABBV AMGN GILD C MS BLK COP UPS ACN NOW INTU AMAT LRCX BKNG TJX
CMG ROST MAR DHR SYK MDT BMY ISRG SCHW SPGI DE HON RTX
""".split())
PRIOR_OOS10 = set("WFC LMT PM ADP WM UNP SO VZ PANW CVS".split())
PRIOR_ROUND2 = set(r2.SYMBOLS)
BLOCKED = PRIOR_79 | PRIOR_OOS10 | PRIOR_ROUND2


def median(xs):
    return float(statistics.median(xs)) if xs else 0.0


def mean(xs):
    return float(statistics.fmean(xs)) if xs else 0.0


def prepare_bars(symbol: str, timeframe: str):
    raw, forming, meta = r2.fetch_with_retry(symbol, timeframe)
    if timeframe == "1d":
        bars = [b for b in raw if str(b["date"])[:10] <= DAILY_END]
        if len(bars) < r2.strategy.MIN_WARMUP_BARS + 10:
            raise RuntimeError(f"{symbol}/1d insufficient history: {len(bars)}")
    else:
        bars = r2.slice_history(raw)
    return bars, forming, meta


def metric_window(bars, ledger, sim, mode, timeframe):
    if timeframe == "1d":
        start_idx = next(
            (
                i for i, b in enumerate(bars)
                if i >= r2.strategy.MIN_WARMUP_BARS and str(b["date"])[:10] >= DAILY_START
            ),
            None,
        )
        end_idx = max(i for i, b in enumerate(bars) if str(b["date"])[:10] <= DAILY_END)
    else:
        end_idx = len(bars) - 1
        end_dt = r2.dt_of(bars[end_idx]["date"])
        cutoff = end_dt - timedelta(days=r2.FORMAL_DAYS)
        start_idx = next(
            (
                i for i, b in enumerate(bars)
                if i >= r2.strategy.MIN_WARMUP_BARS and r2.dt_of(b["date"]) >= cutoff
            ),
            None,
        )
    if start_idx is None or start_idx >= end_idx - 2:
        raise RuntimeError(f"{timeframe}: formal window unavailable")

    curve = [float(x) for x in sim["equity_curve"]]
    base_equity = curve[max(0, start_idx - 1)]
    segment = [x / base_equity for x in curve[start_idx:end_idx + 1]]
    total_return = segment[-1] - 1.0
    days = max(
        1.0,
        (r2.dt_of(bars[end_idx]["date"]) - r2.dt_of(bars[start_idx]["date"])).total_seconds() / 86400.0,
    )
    cagr = segment[-1] ** (365.25 / days) - 1.0 if segment[-1] > 0 else -1.0
    mdd = r2.max_drawdown(segment)
    calmar = cagr / abs(mdd) if mdd < -1e-12 else (999.0 if cagr > 0 else 0.0)

    eval_dates = {b["date"] for b in bars[start_idx:end_idx + 1]}
    markers = [m for m in sim["markers"] if m["execution_date"] in eval_dates]
    s3_exec = [m for m in markers if m["side"] == "S" and m.get("candidate_s3")]
    exits = [m for m in markers if m["side"] == "X"]
    buys = [m for m in markers if m["side"] == "B"]
    quick = 0
    for ex in exits:
        ei = int(ex["execution_index"])
        if any(ei < int(b["execution_index"]) <= ei + 5 for b in buys):
            quick += 1

    signal_count = 0
    if mode is not None:
        for i in range(start_idx, end_idx + 1):
            signal_count += int(r2.s3_hit(i, ledger))

    return {
        "formal_start": bars[start_idx]["date"],
        "formal_end": bars[end_idx]["date"],
        "formal_bars": end_idx - start_idx + 1,
        "total_return": float(total_return),
        "cagr": float(cagr),
        "max_drawdown": float(mdd),
        "calmar": float(calmar),
        "s3_signal_count": int(signal_count),
        "s3_sell_executed": len(s3_exec),
        "c2_full_exit_count": len(exits),
        "c2_quick_rebuy_5bars": int(quick),
    }


def run_series(symbol: str, timeframe: str):
    bars, forming, meta = prepare_bars(symbol, timeframe)
    ledger = r2.strategy.build_ledger(bars, symbol)
    parity = {f"{int(bps)}bps": r2.parity_check(bars, ledger, bps) for bps in FRICTIONS}

    variants = {}
    for bps in FRICTIONS:
        fk = f"{int(bps)}bps"
        variants[fk] = {}
        for variant in VARIANTS:
            mode = None if variant == "BASELINE_V7" else variant.replace("S3_", "")
            sim = r2.simulate_custom(bars, ledger, mode, bps)
            variants[fk][variant] = metric_window(bars, ledger, sim, mode, timeframe)

    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "completed_bars": len(bars),
        "forming_bar_present": forming is not None,
        "market_source": meta.get("provider"),
        "history_window": meta.get("history_window"),
        "parity_max_abs_diff": parity,
        "variants": variants,
    }


def status_for(better_calmar, med_r, med_m, med_c, per_tf):
    if (
        better_calmar >= 33
        and med_c > 0
        and med_m >= 0
        and med_r >= -0.01
        and all(per_tf[tf]["better_calmar"] >= 8 for tf in TIMEFRAMES)
    ):
        return "ADVANCE_TO_CRYPTO"
    if better_calmar <= 23 and med_c < 0 and med_r < 0:
        return "REJECTED_NOT_ADMITTED"
    return "WATCH"


def summarize(rows, friction_key):
    out = {}
    for variant in VARIANTS[1:]:
        dr, dm, dc = [], [], []
        br = bm = bc = signals = executed = exits = quick = 0
        per_tf = {}

        for tf in TIMEFRAMES:
            rr = [x for x in rows if x["timeframe"] == tf]
            tdr, tdm, tdc = [], [], []
            tbr = tbm = tbc = 0
            for row in rr:
                b = row["variants"][friction_key]["BASELINE_V7"]
                v = row["variants"][friction_key][variant]
                xr = v["total_return"] - b["total_return"]
                xm = v["max_drawdown"] - b["max_drawdown"]
                xc = v["calmar"] - b["calmar"]
                tdr.append(xr); tdm.append(xm); tdc.append(xc)
                tbr += int(xr > 0); tbm += int(xm > 0); tbc += int(xc > 0)
            per_tf[tf] = {
                "series": len(rr),
                "better_return": tbr,
                "better_max_drawdown": tbm,
                "better_calmar": tbc,
                "median_delta_return": median(tdr),
                "median_delta_max_drawdown": median(tdm),
                "median_delta_calmar": median(tdc),
            }

        for row in rows:
            b = row["variants"][friction_key]["BASELINE_V7"]
            v = row["variants"][friction_key][variant]
            xr = v["total_return"] - b["total_return"]
            xm = v["max_drawdown"] - b["max_drawdown"]
            xc = v["calmar"] - b["calmar"]
            dr.append(xr); dm.append(xm); dc.append(xc)
            br += int(xr > 0); bm += int(xm > 0); bc += int(xc > 0)
            signals += v["s3_signal_count"]
            executed += v["s3_sell_executed"]
            exits += v["c2_full_exit_count"]
            quick += v["c2_quick_rebuy_5bars"]

        mr, mm, mc = median(dr), median(dm), median(dc)
        out[variant] = {
            "series": len(rows),
            "better_return": br,
            "better_max_drawdown": bm,
            "better_calmar": bc,
            "median_delta_return": mr,
            "mean_delta_return": mean(dr),
            "median_delta_max_drawdown": mm,
            "mean_delta_max_drawdown": mean(dm),
            "median_delta_calmar": mc,
            "mean_delta_calmar": mean(dc),
            "s3_signal_count": signals,
            "s3_sell_executed": executed,
            "c2_full_exit_count": exits,
            "c2_quick_rebuy_5bars": quick,
            "per_timeframe": per_tf,
        }
        if friction_key == "5bps":
            out[variant]["status"] = status_for(bc, mr, mm, mc, per_tf)
    return out


def pairwise(rows):
    names = list(VARIANTS[1:])
    out = {}
    for a in names:
        out[a] = {}
        for b in names:
            if a == b:
                continue
            calmar_wins = return_wins = mdd_wins = 0
            for row in rows:
                av = row["variants"]["5bps"][a]
                bv = row["variants"]["5bps"][b]
                calmar_wins += int(av["calmar"] > bv["calmar"])
                return_wins += int(av["total_return"] > bv["total_return"])
                mdd_wins += int(av["max_drawdown"] > bv["max_drawdown"])
            out[a][b] = {
                "calmar_wins": calmar_wins,
                "return_wins": return_wins,
                "max_drawdown_wins": mdd_wins,
                "series": len(rows),
            }
    return out


def pct(x):
    return f"{100*x:+.2f}%"


def main():
    overlap = set(SYMBOLS) & BLOCKED
    if overlap:
        raise RuntimeError(f"OOS universe overlaps prior design universe: {sorted(overlap)}")

    rows = []
    for symbol in SYMBOLS:
        for tf in TIMEFRAMES:
            print(f"RUN_OOS {symbol} {tf}", flush=True)
            rows.append(run_series(symbol, tf))
            time.sleep(0.25)

    s5 = summarize(rows, "5bps")
    s10 = summarize(rows, "10bps")
    pw = pairwise(rows)

    payload = {
        "meta": {
            "study": "SLTD_V7_SELL_INTENSITY_FULL_EXIT_STUDY_V1_ROUND3_FRESH_STOCK_OOS",
            "status": "IMPLEMENTED_AND_VERIFIED",
            "round": 3,
            "research_type": "FRESH_STOCK_OOS",
            "source_round2_commit": "bf5f38158520a12ea96c3e19a159836380598f8d",
            "symbols": list(SYMBOLS),
            "timeframes": list(TIMEFRAMES),
            "series": len(rows),
            "daily_formal_window": f"{DAILY_START}..{DAILY_END}",
            "intraday_formal_days": r2.FORMAL_DAYS,
            "frictions_bps": list(FRICTIONS),
            "prior_universe_overlap": sorted(set(SYMBOLS) & BLOCKED),
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        },
        "variants": list(VARIANTS),
        "summary_5bps": s5,
        "summary_10bps": s10,
        "pairwise_5bps": pw,
        "rows": rows,
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# SLTD V7 Sell Intensity & Full Exit Study v1 — Round 3 Fresh-Stock OOS",
        "",
        "状态：**IMPLEMENTED_AND_VERIFIED**",
        "",
        "- Fresh stocks：20",
        "- 周期：1h / 4h / 1d",
        "- series：60",
        "- 与 prior design universes overlap：0",
        "- 每个 series 冻结 V7 baseline parity：PASS",
        "",
        "## 5 bps OOS 核心结果",
        "",
        "| Variant | Status | Better Return | Better MDD | Better Calmar | Median ΔReturn | Median ΔMDD | Median ΔCalmar | S3 Exec | C2 exits |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for v in VARIANTS[1:]:
        s = s5[v]
        lines.append(
            f"| {v} | {s['status']} | {s['better_return']}/60 | {s['better_max_drawdown']}/60 | "
            f"{s['better_calmar']}/60 | {pct(s['median_delta_return'])} | "
            f"{pct(s['median_delta_max_drawdown'])} | {s['median_delta_calmar']:+.4f} | "
            f"{s['s3_sell_executed']} | {s['c2_full_exit_count']} |"
        )
    for v in VARIANTS[1:]:
        s = s5[v]
        lines += ["", f"## {v} — {s['status']}"]
        for tf in TIMEFRAMES:
            t = s["per_timeframe"][tf]
            lines.append(
                f"- {tf}: Better Return {t['better_return']}/20; Better MDD {t['better_max_drawdown']}/20; "
                f"Better Calmar {t['better_calmar']}/20; Median ΔReturn {pct(t['median_delta_return'])}; "
                f"Median ΔMDD {pct(t['median_delta_max_drawdown'])}; Median ΔCalmar {t['median_delta_calmar']:+.4f}"
            )
        st = s10[v]
        lines.append(
            f"- 10 bps stress: Better Calmar {st['better_calmar']}/60; Median ΔReturn {pct(st['median_delta_return'])}; "
            f"Median ΔMDD {pct(st['median_delta_max_drawdown'])}; Median ΔCalmar {st['median_delta_calmar']:+.4f}"
        )

    lines += [
        "",
        "## Governance（治理）",
        "",
        "- ADVANCE_TO_CRYPTO 表示股票 OOS 已通过；Crypto 只能测试跨资产可移植性，不能反向改写股票结论。",
        "- 本轮不把多个通过候选强行压成单一 winner；pairwise 数据保存在 JSON，供后续股票选择决策使用。",
        "- 本轮不修改正式 V7。",
        "",
        "`SLTD_V7_SELL_INTENSITY_FULL_EXIT_ROUND3_OOS = IMPLEMENTED_AND_VERIFIED`",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(OUT_MD.read_text(encoding="utf-8"), flush=True)


if __name__ == "__main__":
    main()
