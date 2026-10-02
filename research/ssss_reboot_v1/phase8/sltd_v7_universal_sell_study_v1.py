#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import math
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

OUT_DIR = Path(__file__).resolve().parent
FORMAL_DAYS = 180
HISTORY_DAYS = 365
FRICTION_BPS = 5.0
TIMEFRAMES = ("1h", "4h", "1d")

BATCHES = {
    1: ["ABT", "AAPL", "MSFT", "NVDA", "AMD"],
    2: ["AMZN", "META", "GOOGL", "JPM", "BAC"],
    3: ["XOM", "CVX", "LLY", "UNH", "WMT"],
    4: ["COST", "CAT", "BA", "MA", "V"],
}

VARIANTS = (
    "BASELINE_V7",
    "S1_MATURE_BLUE_UPPER_WICK",
    "S2_MATURE_BLUE_UPPER_ANY",
    "S3_MATURE_BLUE_WICK_CONFIRM_DOWN",
    "S4_BLUE_TO_GRAY_UPPER",
    "S5_BLUE_TO_GRAY_BEARISH",
    "C1_S1_PLUS_S4",
    "C2_S3_PLUS_S4",
    "C3_S1_PLUS_S5",
)

COMBO_MEMBERS = {
    "C1_S1_PLUS_S4": ("S1_MATURE_BLUE_UPPER_WICK", "S4_BLUE_TO_GRAY_UPPER"),
    "C2_S3_PLUS_S4": ("S3_MATURE_BLUE_WICK_CONFIRM_DOWN", "S4_BLUE_TO_GRAY_UPPER"),
    "C3_S1_PLUS_S5": ("S1_MATURE_BLUE_UPPER_WICK", "S5_BLUE_TO_GRAY_BEARISH"),
}


def dt_of(value: str) -> datetime:
    s = str(value)
    if s.endswith("Z"):
        return datetime.fromisoformat(s[:-1] + "+00:00")
    if "T" in s:
        d = datetime.fromisoformat(s)
        return d if d.tzinfo else d.replace(tzinfo=timezone.utc)
    return datetime.strptime(s, "%Y-%m-%d").replace(tzinfo=timezone.utc)


def max_drawdown(values: list[float]) -> float:
    peak = None
    worst = 0.0
    for x in values:
        fx = float(x)
        peak = fx if peak is None else max(peak, fx)
        if peak and peak > 0:
            worst = min(worst, fx / peak - 1.0)
    return float(worst)


def atomic_hits(i: int, ledger: list[dict]) -> list[str]:
    row = ledger[i]
    prev = ledger[i - 1] if i > 0 else None
    out: list[str] = []

    if (
        row["color"] == "BLUE"
        and int(row["run_age"]) >= 21
        and bool(row.get("upper"))
        and row.get("upper_subtype") == "WICK_ONLY"
    ):
        out.append("S1_MATURE_BLUE_UPPER_WICK")

    if (
        row["color"] == "BLUE"
        and int(row["run_age"]) >= 21
        and bool(row.get("upper"))
    ):
        out.append("S2_MATURE_BLUE_UPPER_ANY")

    if (
        prev is not None
        and prev["color"] == "BLUE"
        and int(prev["run_age"]) >= 21
        and bool(prev.get("upper"))
        and prev.get("upper_subtype") == "WICK_ONLY"
        and float(row["close"]) < float(prev["close"])
    ):
        out.append("S3_MATURE_BLUE_WICK_CONFIRM_DOWN")

    if (
        row["color"] == "GRAY"
        and row.get("origin") == "BLUE"
        and int(row["run_age"]) <= 5
        and bool(row.get("upper"))
    ):
        out.append("S4_BLUE_TO_GRAY_UPPER")

    if (
        prev is not None
        and row["color"] == "GRAY"
        and row.get("origin") == "BLUE"
        and int(row["run_age"]) <= 5
        and float(row["close"]) < float(prev["close"])
    ):
        out.append("S5_BLUE_TO_GRAY_BEARISH")

    return out


def variant_hits(variant: str, i: int, ledger: list[dict]) -> list[str]:
    if variant == "BASELINE_V7":
        return []
    atoms = atomic_hits(i, ledger)
    if variant in COMBO_MEMBERS:
        wanted = set(COMBO_MEMBERS[variant])
        return [x for x in atoms if x in wanted]
    return [x for x in atoms if x == variant]


def ledger_for_variant(base_ledger: list[dict], variant: str) -> list[dict]:
    if variant == "BASELINE_V7":
        return base_ledger
    out = copy.deepcopy(base_ledger)
    for i, row in enumerate(out):
        hits = variant_hits(variant, i, base_ledger)
        if hits:
            row["SELL"].extend(hits)
    return out


def fetch_with_retry(symbol: str, timeframe: str) -> tuple[list[dict], dict | None, dict]:
    last: Exception | None = None
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
    sliced = [b for b in bars if dt_of(b["date"]) >= cutoff]
    if len(sliced) < 140:
        raise RuntimeError(f"history too short after 365d slice: {len(sliced)}")
    return sliced


def metrics_for(
    bars: list[dict],
    ledger: list[dict],
    sim: dict,
    variant: str,
) -> dict:
    end_dt = dt_of(bars[-1]["date"])
    formal_cut = end_dt - timedelta(days=FORMAL_DAYS)
    start_idx = next(
        (i for i, b in enumerate(bars) if i >= strategy.MIN_WARMUP_BARS and dt_of(b["date"]) >= formal_cut),
        None,
    )
    if start_idx is None or start_idx >= len(bars) - 3:
        raise RuntimeError("formal window unavailable")

    curve = [float(x) for x in sim["equity_curve"]]
    base_idx = max(0, start_idx - 1)
    base_equity = curve[base_idx]
    if base_equity <= 0:
        raise RuntimeError("invalid base equity")
    segment = [x / base_equity for x in curve[start_idx:]]
    total_return = segment[-1] - 1.0
    elapsed_days = max(1.0, (dt_of(bars[-1]["date"]) - dt_of(bars[start_idx]["date"])).total_seconds() / 86400.0)
    cagr = segment[-1] ** (365.25 / elapsed_days) - 1.0 if segment[-1] > 0 else -1.0
    mdd = max_drawdown(segment)
    calmar = cagr / abs(mdd) if mdd < -1e-12 else (999.0 if cagr > 0 else 0.0)

    eval_dates = {b["date"] for b in bars[start_idx:]}
    markers = [m for m in sim["markers"] if m["execution_date"] in eval_dates]
    buy_count = sum(1 for m in markers if m["side"] == "B")
    sell_count = sum(1 for m in markers if m["side"] == "S")
    c2_count = sum(1 for m in markers if m["side"] == "X")

    candidate_signal_count = 0
    for i in range(start_idx, len(ledger)):
        if variant_hits(variant, i, ledger):
            candidate_signal_count += 1

    candidate_markers = []
    if variant != "BASELINE_V7":
        candidate_ids = set(COMBO_MEMBERS.get(variant, (variant,)))
        for m in markers:
            if m["side"] != "S":
                continue
            if candidate_ids.intersection(set(m.get("rule_ids") or [])):
                candidate_markers.append(m)

    date_index = {b["date"]: i for i, b in enumerate(bars)}
    quick_rebuy = 0
    for sm in candidate_markers:
        si = date_index.get(sm["execution_date"])
        if si is None:
            continue
        for bm in markers:
            if bm["side"] != "B":
                continue
            bi = date_index.get(bm["execution_date"])
            if bi is not None and si < bi <= si + 5:
                quick_rebuy += 1
                break

    return {
        "formal_start": bars[start_idx]["date"],
        "formal_end": bars[-1]["date"],
        "formal_bars": len(bars) - start_idx,
        "total_return": float(total_return),
        "cagr": float(cagr),
        "max_drawdown": float(mdd),
        "calmar": float(calmar),
        "buy_count": buy_count,
        "sell_count": sell_count,
        "c2_count": c2_count,
        "candidate_signal_count": candidate_signal_count,
        "candidate_sell_executed": len(candidate_markers),
        "quick_rebuy_5bars": quick_rebuy,
    }


def run_series(symbol: str, timeframe: str) -> dict:
    raw, forming, meta = fetch_with_retry(symbol, timeframe)
    bars = slice_history(raw)
    ledger = strategy.build_ledger(bars, symbol)
    variants: dict[str, dict] = {}

    for variant in VARIANTS:
        candidate_ledger = ledger_for_variant(ledger, variant)
        sim = strategy.simulate_policy(bars, candidate_ledger, friction_bps=FRICTION_BPS)
        variants[variant] = metrics_for(bars, ledger, sim, variant)

    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "completed_bars": len(bars),
        "forming_bar_present": forming is not None,
        "market_source": meta.get("provider"),
        "history_window": meta.get("history_window"),
        "variants": variants,
    }


def median(values: list[float]) -> float:
    return float(statistics.median(values)) if values else 0.0


def mean(values: list[float]) -> float:
    return float(statistics.fmean(values)) if values else 0.0


def summarize(rows: list[dict]) -> dict:
    summary: dict[str, dict] = {}
    for variant in VARIANTS[1:]:
        deltas_r = []
        deltas_mdd = []
        deltas_c = []
        better_r = better_mdd = better_c = 0
        cand_exec = quick = 0
        per_tf: dict[str, dict] = {}

        for tf in TIMEFRAMES:
            tf_rows = [r for r in rows if r["timeframe"] == tf]
            tf_better_c = 0
            tf_d_c = []
            tf_d_r = []
            tf_d_mdd = []
            for r in tf_rows:
                b = r["variants"]["BASELINE_V7"]
                v = r["variants"][variant]
                dr = v["total_return"] - b["total_return"]
                dm = v["max_drawdown"] - b["max_drawdown"]
                dc = v["calmar"] - b["calmar"]
                tf_d_r.append(dr)
                tf_d_mdd.append(dm)
                tf_d_c.append(dc)
                if dc > 0:
                    tf_better_c += 1
            per_tf[tf] = {
                "series": len(tf_rows),
                "better_calmar": tf_better_c,
                "median_delta_return": median(tf_d_r),
                "median_delta_max_drawdown": median(tf_d_mdd),
                "median_delta_calmar": median(tf_d_c),
            }

        for r in rows:
            b = r["variants"]["BASELINE_V7"]
            v = r["variants"][variant]
            dr = v["total_return"] - b["total_return"]
            dm = v["max_drawdown"] - b["max_drawdown"]
            dc = v["calmar"] - b["calmar"]
            deltas_r.append(dr)
            deltas_mdd.append(dm)
            deltas_c.append(dc)
            better_r += int(dr > 0)
            better_mdd += int(dm > 0)
            better_c += int(dc > 0)
            cand_exec += int(v["candidate_sell_executed"])
            quick += int(v["quick_rebuy_5bars"])

        n = len(rows)
        calmar_ratio = better_c / n if n else 0.0
        med_r = median(deltas_r)
        med_mdd = median(deltas_mdd)
        med_c = median(deltas_c)
        min_tf_ratio = min(
            (x["better_calmar"] / x["series"] if x["series"] else 0.0)
            for x in per_tf.values()
        )

        if (
            calmar_ratio >= 0.55
            and med_c > 0
            and med_mdd >= 0
            and med_r >= -0.01
            and min_tf_ratio >= 0.40
        ):
            status = "ADVANCE_TO_OOS"
        elif calmar_ratio < 0.40 and med_c < 0 and med_r < 0:
            status = "REJECT_NOT_ADMITTED"
        else:
            status = "WATCH"

        summary[variant] = {
            "status": status,
            "series": n,
            "better_return": better_r,
            "better_max_drawdown": better_mdd,
            "better_calmar": better_c,
            "median_delta_return": med_r,
            "mean_delta_return": mean(deltas_r),
            "median_delta_max_drawdown": med_mdd,
            "mean_delta_max_drawdown": mean(deltas_mdd),
            "median_delta_calmar": med_c,
            "mean_delta_calmar": mean(deltas_c),
            "candidate_sell_executed": cand_exec,
            "quick_rebuy_5bars": quick,
            "quick_rebuy_rate": (quick / cand_exec if cand_exec else 0.0),
            "per_timeframe": per_tf,
        }
    return summary


def write_batch(batch_id: int, batch_rows: list[dict]) -> None:
    out = OUT_DIR / f"SLTD_V7_UNIVERSAL_SELL_BATCH_{batch_id:02d}_v1.json"
    payload = {
        "batch": batch_id,
        "symbols": BATCHES[batch_id],
        "timeframes": TIMEFRAMES,
        "rows": batch_rows,
    }
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"BATCH_{batch_id:02d}_COMPLETE rows={len(batch_rows)} file={out.name}", flush=True)


def write_merged(rows: list[dict]) -> None:
    summary = summarize(rows)
    payload = {
        "status": "IMPLEMENTED_AND_VERIFIED",
        "scope": {
            "stocks": sum(len(x) for x in BATCHES.values()),
            "timeframes": list(TIMEFRAMES),
            "series": len(rows),
            "history_days": HISTORY_DAYS,
            "formal_days": FORMAL_DAYS,
            "friction_bps": FRICTION_BPS,
        },
        "batches": BATCHES,
        "variants": list(VARIANTS),
        "summary": summary,
        "rows": rows,
    }
    json_path = OUT_DIR / "SLTD_V7_UNIVERSAL_SELL_STUDY_RESULT_v1.json"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# SLTD V7 Universal Sell Study（通用卖出研究）Result v1",
        "",
        "状态：IMPLEMENTED_AND_VERIFIED",
        "",
        f"- 股票：{payload['scope']['stocks']}",
        f"- 周期：{', '.join(TIMEFRAMES)}",
        f"- series：{len(rows)}",
        f"- 正式比较窗口：最近约 {FORMAL_DAYS} 天",
        f"- 摩擦：{FRICTION_BPS} bps",
        "",
        "## 汇总",
        "",
        "| Candidate | Status | Better Calmar | Better MDD | Better Return | Median ΔReturn | Median ΔMDD | Median ΔCalmar | Added SELL | 5-bar rebuy |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for variant in VARIANTS[1:]:
        s = summary[variant]
        lines.append(
            f"| {variant} | {s['status']} | {s['better_calmar']}/{s['series']} | "
            f"{s['better_max_drawdown']}/{s['series']} | {s['better_return']}/{s['series']} | "
            f"{s['median_delta_return']:+.4f} | {s['median_delta_max_drawdown']:+.4f} | "
            f"{s['median_delta_calmar']:+.4f} | {s['candidate_sell_executed']} | "
            f"{s['quick_rebuy_5bars']}/{s['candidate_sell_executed']} |"
        )

    for variant in VARIANTS[1:]:
        s = summary[variant]
        lines += ["", f"## {variant} — {s['status']}"]
        for tf in TIMEFRAMES:
            t = s["per_timeframe"][tf]
            lines.append(
                f"- {tf}: better Calmar {t['better_calmar']}/{t['series']}; "
                f"median ΔReturn {t['median_delta_return']:+.4f}; "
                f"median ΔMDD {t['median_delta_max_drawdown']:+.4f}; "
                f"median ΔCalmar {t['median_delta_calmar']:+.4f}"
            )

    lines += [
        "",
        "## 边界",
        "",
        "- 本轮是 20 股票 × 1h/4h/1d 的 discovery/screen，不是最终 OOS。",
        "- 没有修改正式 V7 12 条规则、25% 仓位政策或 C2。",
        "- ADVANCE_TO_OOS 只代表值得进入 fresh-stock 独立验证。",
    ]
    md_path = OUT_DIR / "SLTD_V7_UNIVERSAL_SELL_STUDY_RESULT_v1.md"
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(md_path.read_text(encoding="utf-8"), flush=True)


def main() -> None:
    all_rows: list[dict] = []
    for batch_id in sorted(BATCHES):
        batch_rows: list[dict] = []
        for symbol in BATCHES[batch_id]:
            for timeframe in TIMEFRAMES:
                print(f"RUN {symbol} {timeframe}", flush=True)
                row = run_series(symbol, timeframe)
                batch_rows.append(row)
                all_rows.append(row)
                time.sleep(0.25)
        write_batch(batch_id, batch_rows)
    write_merged(all_rows)


if __name__ == "__main__":
    main()
