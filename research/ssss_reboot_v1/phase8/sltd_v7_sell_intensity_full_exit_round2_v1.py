#!/usr/bin/env python3
from __future__ import annotations

import json
import statistics
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
APP = ROOT / "integrations" / "sltd_v7_siftalpha_v1"
sys.path.insert(0, str(APP))

import data_provider
import strategy

OUT_JSON = Path(__file__).with_name("SLTD_V7_SELL_INTENSITY_FULL_EXIT_ROUND2_RESULT_v1.json")
OUT_MD = Path(__file__).with_name("SLTD_V7_SELL_INTENSITY_FULL_EXIT_ROUND2_RESULT_v1.md")

HISTORY_DAYS = 365
FORMAL_DAYS = 180
FRICTIONS = (5.0, 10.0)
TIMEFRAMES = ("1h", "4h")
SYMBOLS = (
    "ABT", "AAPL", "MSFT", "NVDA", "AMD",
    "AMZN", "META", "GOOGL", "JPM", "BAC",
    "XOM", "CVX", "LLY", "UNH", "WMT",
    "COST", "CAT", "BA", "MA", "V",
)
VARIANTS = ("BASELINE_V7", "S3_CUR25", "S3_CUR50", "S3_TARGET50", "S3_TARGET25")


def dt_of(value: str) -> datetime:
    s = str(value)
    if s.endswith("Z"):
        return datetime.fromisoformat(s[:-1] + "+00:00")
    if "T" in s:
        x = datetime.fromisoformat(s)
        return x if x.tzinfo else x.replace(tzinfo=timezone.utc)
    return datetime.strptime(s, "%Y-%m-%d").replace(tzinfo=timezone.utc)


def max_drawdown(values: list[float]) -> float:
    peak = 0.0
    worst = 0.0
    for x in values:
        peak = max(peak, float(x))
        if peak > 0:
            worst = min(worst, float(x) / peak - 1.0)
    return worst


def median(values: list[float]) -> float:
    return float(statistics.median(values)) if values else 0.0


def mean(values: list[float]) -> float:
    return float(statistics.fmean(values)) if values else 0.0


def fetch_with_retry(symbol: str, timeframe: str):
    last = None
    for attempt in range(4):
        try:
            return data_provider.fetch_bars(symbol, timeframe, force_refresh=True)
        except Exception as exc:
            last = exc
            if attempt == 3:
                break
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"{symbol}/{timeframe} fetch failed: {last}")


def slice_history(bars: list[dict]) -> list[dict]:
    end = dt_of(bars[-1]["date"])
    cutoff = end - timedelta(days=HISTORY_DAYS)
    out = [b for b in bars if dt_of(b["date"]) >= cutoff]
    if len(out) < strategy.MIN_WARMUP_BARS + 10:
        raise RuntimeError(f"history too short: {len(out)}")
    return out


def s3_hit(i: int, ledger: list[dict]) -> bool:
    if i <= 0:
        return False
    row = ledger[i]
    prev = ledger[i - 1]
    return bool(
        prev["color"] == "BLUE"
        and int(prev["run_age"]) >= 21
        and prev.get("upper")
        and prev.get("upper_subtype") == "WICK_ONLY"
        and float(row["close"]) < float(prev["close"])
    )


def action_classes(row: dict | None, extra_sell: bool) -> tuple[str, ...]:
    if row is None:
        return ()
    classes = [cls for cls in strategy.ACTION_ORDER if row.get(cls)]
    if extra_sell and "SELL" not in classes:
        classes.append("SELL")
    return tuple(classes)


def resolve_action(row: dict | None, extra_sell: bool) -> str | None:
    classes = action_classes(row, extra_sell)
    return classes[0] if len(classes) == 1 else None


def desired_after_sell(mode: str, position_value: float, equity: float) -> float:
    if mode == "CUR25":
        return position_value * 0.75
    if mode == "CUR50":
        return position_value * 0.50
    if mode == "TARGET50":
        return min(position_value, equity * 0.50)
    if mode == "TARGET25":
        return min(position_value, equity * 0.25)
    raise ValueError(mode)


def simulate_custom(bars: list[dict], ledger: list[dict], mode: str | None, friction_bps: float) -> dict:
    cash = 1.0
    shares = 0.0
    risk_armed = False
    cost_rate = float(friction_bps) / 10000.0

    markers = []
    positions = []
    curve = []

    formal_index = next((i for i, b in enumerate(bars) if b["date"] >= strategy.POLICY_START_DATE), 0)
    warmup_index = min(strategy.MIN_WARMUP_BARS, len(bars) - 1)
    start_index = max(formal_index, warmup_index)

    for j, bar in enumerate(bars):
        if j < start_index:
            curve.append(1.0)
            positions.append({"fraction": 0.0, "risk_armed": False})
            continue

        op = float(bar["open"])
        cl = float(bar["close"])
        pre = cash + shares * op
        if pre <= 0:
            raise RuntimeError("non-positive equity")
        pos = shares * op
        frac = pos / pre

        signal_idx = j - 1
        signal = ledger[signal_idx] if j > start_index else None
        extra_sell = bool(mode is not None and signal is not None and s3_hit(signal_idx, ledger))
        hard = bool(shares > 1e-14 and risk_armed and strategy.c2_condition(signal))
        action = resolve_action(signal, extra_sell)
        ordinary_action = None
        order = 0.0
        side = None

        if hard:
            order = -pos
            side = "X"
        else:
            ordinary_action = action
            if action == "BUY":
                target = 0.25 if shares <= 1e-14 else min(1.0, frac + 0.25)
                order = max(frac, target) * pre - pos
                side = "B"
            elif action == "SELL" and shares > 1e-14:
                if extra_sell and mode is not None:
                    desired = desired_after_sell(mode, pos, pre)
                    order = desired - pos
                else:
                    order = -pos * 0.25
                side = "S"

        if order > 1e-14:
            order = min(order, max(0.0, cash / (1.0 + cost_rate)))
        elif order < -1e-14:
            order = max(order, -pos)

        executed = abs(order) > 1e-14
        if executed:
            cost = abs(order) * cost_rate
            shares += order / op
            cash -= order + cost
            if shares <= 1e-12:
                shares = 0.0

        if hard and executed:
            risk_armed = False
        elif executed and ordinary_action == "SELL" and order < 0:
            risk_armed = True
        elif executed and ordinary_action == "BUY" and order > 0:
            risk_armed = False

        close_equity = cash + shares * cl
        close_frac = shares * cl / close_equity if close_equity > 0 else 0.0
        curve.append(float(close_equity))
        positions.append({"fraction": float(close_frac), "risk_armed": bool(risk_armed)})

        if executed and side:
            markers.append({
                "execution_index": j,
                "execution_date": bar["date"],
                "side": side,
                "action": "HARD_EXIT" if hard else ordinary_action,
                "candidate_s3": bool(extra_sell and side == "S"),
                "position_after": float(max(0.0, min(1.0, close_frac))),
            })

    return {
        "equity_curve": curve,
        "positions": positions,
        "markers": markers,
        "final_equity": curve[-1],
    }


def parity_check(bars: list[dict], ledger: list[dict], friction_bps: float) -> float:
    frozen = strategy.simulate_policy(bars, ledger, friction_bps=friction_bps)
    custom = simulate_custom(bars, ledger, None, friction_bps)
    a = frozen["equity_curve"]
    b = custom["equity_curve"]
    if len(a) != len(b):
        raise RuntimeError("parity length mismatch")
    diff = max(abs(float(x) - float(y)) for x, y in zip(a, b))
    if diff > 1e-10:
        raise RuntimeError(f"baseline parity failed: max_abs_diff={diff}")
    return float(diff)


def metrics(bars: list[dict], ledger: list[dict], sim: dict, mode: str | None) -> dict:
    end_dt = dt_of(bars[-1]["date"])
    cut = end_dt - timedelta(days=FORMAL_DAYS)
    start_idx = next(
        (i for i, b in enumerate(bars) if i >= strategy.MIN_WARMUP_BARS and dt_of(b["date"]) >= cut),
        None,
    )
    if start_idx is None or start_idx >= len(bars) - 3:
        raise RuntimeError("formal window unavailable")

    curve = [float(x) for x in sim["equity_curve"]]
    base_equity = curve[max(0, start_idx - 1)]
    segment = [x / base_equity for x in curve[start_idx:]]
    total_return = segment[-1] - 1.0
    days = max(1.0, (dt_of(bars[-1]["date"]) - dt_of(bars[start_idx]["date"])).total_seconds() / 86400.0)
    cagr = segment[-1] ** (365.25 / days) - 1.0 if segment[-1] > 0 else -1.0
    mdd = max_drawdown(segment)
    calmar = cagr / abs(mdd) if mdd < -1e-12 else (999.0 if cagr > 0 else 0.0)

    eval_dates = {b["date"] for b in bars[start_idx:]}
    markers = [m for m in sim["markers"] if m["execution_date"] in eval_dates]
    candidate_exec = [m for m in markers if m["side"] == "S" and m.get("candidate_s3")]
    exits = [m for m in markers if m["side"] == "X"]
    buys = [m for m in markers if m["side"] == "B"]

    quick = 0
    for ex in exits:
        ei = int(ex["execution_index"])
        if any(ei < int(b["execution_index"]) <= ei + 5 for b in buys):
            quick += 1

    signal_count = 0
    if mode is not None:
        for i in range(start_idx, len(ledger)):
            signal_count += int(s3_hit(i, ledger))

    return {
        "formal_start": bars[start_idx]["date"],
        "formal_end": bars[-1]["date"],
        "formal_bars": len(bars) - start_idx,
        "total_return": float(total_return),
        "cagr": float(cagr),
        "max_drawdown": float(mdd),
        "calmar": float(calmar),
        "s3_signal_count": int(signal_count),
        "s3_sell_executed": len(candidate_exec),
        "c2_full_exit_count": len(exits),
        "c2_quick_rebuy_5bars": int(quick),
    }


def run_series(symbol: str, timeframe: str) -> dict:
    raw, forming, meta = fetch_with_retry(symbol, timeframe)
    bars = slice_history(raw)
    ledger = strategy.build_ledger(bars, symbol)

    parity = {f"{int(bps)}bps": parity_check(bars, ledger, bps) for bps in FRICTIONS}
    variants = {}
    for bps in FRICTIONS:
        key = f"{int(bps)}bps"
        variants[key] = {}
        for variant in VARIANTS:
            mode = None if variant == "BASELINE_V7" else variant.replace("S3_", "")
            sim = simulate_custom(bars, ledger, mode, bps)
            variants[key][variant] = metrics(bars, ledger, sim, mode)

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


def status_for(better_calmar: int, med_r: float, med_m: float, med_c: float, per_tf: dict) -> str:
    if (
        better_calmar >= 22
        and med_c > 0
        and med_m >= 0
        and med_r >= -0.01
        and per_tf["1h"]["better_calmar"] >= 8
        and per_tf["4h"]["better_calmar"] >= 8
    ):
        return "ADVANCE_TO_OOS"
    if better_calmar <= 15 and med_c < 0 and med_r < 0:
        return "REJECTED_NOT_ADMITTED"
    return "WATCH"


def summarize(rows: list[dict], friction_key: str) -> dict:
    out = {}
    for variant in VARIANTS[1:]:
        dr, dm, dc = [], [], []
        br = bm = bc = signals = executed = exits = quick = 0
        per_tf = {}
        for tf in TIMEFRAMES:
            tf_rows = [r for r in rows if r["timeframe"] == tf]
            tdr, tdm, tdc = [], [], []
            tbc = 0
            for r in tf_rows:
                b = r["variants"][friction_key]["BASELINE_V7"]
                v = r["variants"][friction_key][variant]
                xr = v["total_return"] - b["total_return"]
                xm = v["max_drawdown"] - b["max_drawdown"]
                xc = v["calmar"] - b["calmar"]
                tdr.append(xr); tdm.append(xm); tdc.append(xc)
                tbc += int(xc > 0)
            per_tf[tf] = {
                "series": len(tf_rows),
                "better_calmar": tbc,
                "median_delta_return": median(tdr),
                "median_delta_max_drawdown": median(tdm),
                "median_delta_calmar": median(tdc),
            }

        for r in rows:
            b = r["variants"][friction_key]["BASELINE_V7"]
            v = r["variants"][friction_key][variant]
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


def pct(x: float) -> str:
    return f"{100*x:+.2f}%"


def main() -> None:
    rows = []
    for symbol in SYMBOLS:
        for tf in TIMEFRAMES:
            print(f"RUN {symbol} {tf}", flush=True)
            rows.append(run_series(symbol, tf))
            time.sleep(0.25)

    s5 = summarize(rows, "5bps")
    s10 = summarize(rows, "10bps")
    payload = {
        "meta": {
            "study": "SLTD_V7_SELL_INTENSITY_FULL_EXIT_STUDY_V1_ROUND2",
            "status": "IMPLEMENTED_AND_VERIFIED",
            "round": 2,
            "source_round1_commit": "39888969074101e3e6034bdcb4550ea4e30e70fe",
            "source_v7_candidate_commit": "5f9ea4d8fa434b54afdbf32a1cb21ef2f3cb4042",
            "support_source_commit": "ea0d2ec5f484bdc35b1f134f236bbd933c9caf15",
            "symbols": list(SYMBOLS),
            "timeframes": list(TIMEFRAMES),
            "series": len(rows),
            "history_days": HISTORY_DAYS,
            "formal_days": FORMAL_DAYS,
            "frictions_bps": list(FRICTIONS),
            "execution": "CONFIRMED_SELECTED_BAR_CLOSE_TO_NEXT_SELECTED_BAR_OPEN",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        },
        "variants": list(VARIANTS),
        "summary_5bps": s5,
        "summary_10bps": s10,
        "rows": rows,
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# SLTD V7 Sell Intensity & Full Exit Study v1 — Round 2",
        "",
        "状态：**IMPLEMENTED_AND_VERIFIED**",
        "",
        "- 股票：20",
        "- 周期：1h / 4h",
        "- series：40",
        "- 正式比较窗口：最近约 180 天",
        "- 5 bps primary；10 bps stress",
        "- 每个 series 的冻结 V7 baseline parity：PASS",
        "",
        "## 5 bps 核心结果",
        "",
        "| Variant | Status | Better Return | Better MDD | Better Calmar | Median ΔReturn | Median ΔMDD | Median ΔCalmar | S3 Exec | C2 exits |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for v in VARIANTS[1:]:
        s = s5[v]
        lines.append(
            f"| {v} | {s['status']} | {s['better_return']}/40 | {s['better_max_drawdown']}/40 | "
            f"{s['better_calmar']}/40 | {pct(s['median_delta_return'])} | "
            f"{pct(s['median_delta_max_drawdown'])} | {s['median_delta_calmar']:+.4f} | "
            f"{s['s3_sell_executed']} | {s['c2_full_exit_count']} |"
        )

    for v in VARIANTS[1:]:
        s = s5[v]
        lines += ["", f"## {v} — {s['status']}"]
        for tf in TIMEFRAMES:
            t = s["per_timeframe"][tf]
            lines.append(
                f"- {tf}: Better Calmar {t['better_calmar']}/20; "
                f"Median ΔReturn {pct(t['median_delta_return'])}; "
                f"Median ΔMDD {pct(t['median_delta_max_drawdown'])}; "
                f"Median ΔCalmar {t['median_delta_calmar']:+.4f}"
            )
        stress = s10[v]
        lines.append(
            f"- 10 bps stress: Better Calmar {stress['better_calmar']}/40; "
            f"Median ΔReturn {pct(stress['median_delta_return'])}; "
            f"Median ΔMDD {pct(stress['median_delta_max_drawdown'])}; "
            f"Median ΔCalmar {stress['median_delta_calmar']:+.4f}"
        )

    lines += [
        "",
        "## 边界",
        "",
        "- Round 2 只验证 S3 卖出强度的跨周期通用性，不新增 FULL EXIT 条件。",
        "- S1/S2、S3 FULL、Direct C2、ZD1 FULL 已按 Round 1 门槛停留在 WATCH/REJECT，不进入本轮。",
        "- 只有 ADVANCE_TO_OOS 才可进入 Round 3 fresh-stock OOS。",
        "- 本轮不修改正式 V7。",
        "",
        "`SLTD_V7_SELL_INTENSITY_FULL_EXIT_ROUND2 = IMPLEMENTED_AND_VERIFIED`",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(OUT_MD.read_text(encoding="utf-8"), flush=True)


if __name__ == "__main__":
    main()
