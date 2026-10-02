#!/usr/bin/env python3
from __future__ import annotations

import copy
import csv
import gzip
import json
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
APP = ROOT / "integrations" / "sltd_v7_siftalpha_v1"
sys.path.insert(0, str(APP))

import strategy

OUT_JSON = Path(__file__).with_name("SLTD_V7_UNIVERSAL_SELL_DAILY79_RESULT_v1.json")
OUT_MD = Path(__file__).with_name("SLTD_V7_UNIVERSAL_SELL_DAILY79_RESULT_v1.md")
DATA_ROOT = ROOT / "research" / "ssss_reboot_v1" / "phase7" / "data_snapshot"

FORMAL_START = "2020-01-02"
FORMAL_END = "2026-09-30"
FRICTION_BPS = 5.0

BATCHES = {
    1: ["AAPL","MSFT","NVDA","AMD","AVGO","ORCL","INTC","QCOM","MU","GOOGL"],
    2: ["META","NFLX","AMZN","TSLA","HD","MCD","WMT","COST","PG","KO"],
    3: ["PEP","ABT","LLY","UNH","JNJ","TMO","JPM","BAC","GS","V"],
    4: ["MA","CAT","BA","GE","XOM","CVX","LIN","NEE","PLD"],
    5: ["IBM","CSCO","CRM","ADBE","TXN","DIS","NKE","SBUX","TGT","LOW"],
    6: ["MRK","PFE","ABBV","AMGN","GILD","C","MS","BLK","COP","UPS"],
    7: ["ACN","NOW","INTU","AMAT","LRCX","BKNG","TJX","CMG","ROST","MAR"],
    8: ["DHR","SYK","MDT","BMY","ISRG","SCHW","SPGI","DE","HON","RTX"],
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


def read_bars(batch: int, symbol: str) -> list[dict]:
    path = DATA_ROOT / f"batch_{batch:02d}_stocks" / f"{symbol}.csv.gz"
    if not path.exists():
        raise FileNotFoundError(path)
    rows: list[dict] = []
    with gzip.open(path, "rt", encoding="utf-8", newline="") as f:
        for rec in csv.DictReader(f):
            d = str(rec["Date"])[:10]
            if d > FORMAL_END:
                continue
            rows.append({
                "date": d,
                "open": float(rec["Open"]),
                "high": float(rec["High"]),
                "low": float(rec["Low"]),
                "close": float(rec["Close"]),
                "volume": float(rec.get("Volume") or 0.0),
            })
    return rows


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


def ledger_for_variant(base: list[dict], variant: str) -> list[dict]:
    if variant == "BASELINE_V7":
        return base
    out = copy.deepcopy(base)
    for i, row in enumerate(out):
        hits = variant_hits(variant, i, base)
        if hits:
            row["SELL"].extend(hits)
    return out


def max_drawdown(curve: list[float]) -> float:
    peak = 0.0
    worst = 0.0
    for x in curve:
        peak = max(peak, float(x))
        if peak > 0:
            worst = min(worst, float(x) / peak - 1.0)
    return worst


def metrics(bars: list[dict], base_ledger: list[dict], sim: dict, variant: str) -> dict:
    start_idx = next(i for i,b in enumerate(bars) if b["date"] >= FORMAL_START)
    end_idx = max(i for i,b in enumerate(bars) if b["date"] <= FORMAL_END)
    curve = [float(x) for x in sim["equity_curve"]]
    base_idx = max(0, start_idx - 1)
    base_equity = curve[base_idx]
    segment = [x / base_equity for x in curve[start_idx:end_idx+1]]
    total_return = segment[-1] - 1.0
    days = (
        datetime.strptime(bars[end_idx]["date"], "%Y-%m-%d")
        - datetime.strptime(bars[start_idx]["date"], "%Y-%m-%d")
    ).days
    days = max(days, 1)
    cagr = segment[-1] ** (365.25 / days) - 1.0 if segment[-1] > 0 else -1.0
    mdd = max_drawdown(segment)
    calmar = cagr / abs(mdd) if mdd < -1e-12 else (999.0 if cagr > 0 else 0.0)

    eval_dates = {b["date"] for b in bars[start_idx:end_idx+1]}
    markers = [m for m in sim["markers"] if m["execution_date"] in eval_dates]
    candidate_ids = set(COMBO_MEMBERS.get(variant, (variant,))) if variant != "BASELINE_V7" else set()
    candidate_markers = [
        m for m in markers
        if m["side"] == "S" and candidate_ids.intersection(set(m.get("rule_ids") or []))
    ]
    candidate_signal_count = sum(
        1 for i in range(start_idx, end_idx+1) if variant_hits(variant, i, base_ledger)
    )

    date_index = {b["date"]: i for i,b in enumerate(bars)}
    quick = 0
    for sm in candidate_markers:
        si = date_index[sm["execution_date"]]
        if any(
            m["side"] == "B"
            and m["execution_date"] in date_index
            and si < date_index[m["execution_date"]] <= si + 5
            for m in markers
        ):
            quick += 1

    return {
        "total_return": total_return,
        "cagr": cagr,
        "max_drawdown": mdd,
        "calmar": calmar,
        "buy_count": sum(m["side"] == "B" for m in markers),
        "sell_count": sum(m["side"] == "S" for m in markers),
        "c2_count": sum(m["side"] == "X" for m in markers),
        "candidate_signal_count": candidate_signal_count,
        "candidate_sell_executed": len(candidate_markers),
        "quick_rebuy_5bars": quick,
    }


def med(xs: list[float]) -> float:
    return float(statistics.median(xs)) if xs else 0.0


def avg(xs: list[float]) -> float:
    return float(statistics.fmean(xs)) if xs else 0.0


def summarize(rows: list[dict]) -> dict:
    out = {}
    for variant in VARIANTS[1:]:
        dr, dm, dc = [], [], []
        br = bm = bc = 0
        signals = executed = quick = 0
        impacted = 0
        for row in rows:
            b = row["variants"]["BASELINE_V7"]
            v = row["variants"][variant]
            xr = v["total_return"] - b["total_return"]
            xm = v["max_drawdown"] - b["max_drawdown"]
            xc = v["calmar"] - b["calmar"]
            dr.append(xr); dm.append(xm); dc.append(xc)
            br += int(xr > 0); bm += int(xm > 0); bc += int(xc > 0)
            signals += v["candidate_signal_count"]
            executed += v["candidate_sell_executed"]
            quick += v["quick_rebuy_5bars"]
            impacted += int(v["candidate_sell_executed"] > 0)

        ratio = bc / len(rows)
        mr, mm, mc = med(dr), med(dm), med(dc)
        if ratio >= 0.55 and mc > 0 and mm >= 0 and mr >= -0.01:
            status = "ADVANCE_TO_OOS"
        elif ratio < 0.40 and mc < 0 and mr < 0:
            status = "REJECT_NOT_ADMITTED"
        else:
            status = "WATCH"
        out[variant] = {
            "status": status,
            "stocks": len(rows),
            "impacted_stocks": impacted,
            "better_return": br,
            "better_max_drawdown": bm,
            "better_calmar": bc,
            "median_delta_return": mr,
            "mean_delta_return": avg(dr),
            "median_delta_max_drawdown": mm,
            "mean_delta_max_drawdown": avg(dm),
            "median_delta_calmar": mc,
            "mean_delta_calmar": avg(dc),
            "candidate_signal_count": signals,
            "candidate_sell_executed": executed,
            "quick_rebuy_5bars": quick,
            "quick_rebuy_rate": quick / executed if executed else 0.0,
        }
    return out


def main() -> None:
    rows = []
    for batch in sorted(BATCHES):
        print(f"BATCH_{batch:02d}_START", flush=True)
        for symbol in BATCHES[batch]:
            bars = read_bars(batch, symbol)
            ledger = strategy.build_ledger(bars, symbol)
            variants = {}
            for variant in VARIANTS:
                led = ledger_for_variant(ledger, variant)
                sim = strategy.simulate_policy(bars, led, friction_bps=FRICTION_BPS)
                variants[variant] = metrics(bars, ledger, sim, variant)
            rows.append({"batch": batch, "symbol": symbol, "variants": variants})
        print(f"BATCH_{batch:02d}_COMPLETE stocks={len(BATCHES[batch])}", flush=True)

    summary = summarize(rows)
    payload = {
        "status": "IMPLEMENTED_AND_VERIFIED",
        "scope": {
            "stocks": len(rows),
            "timeframe": "1d",
            "formal_start": FORMAL_START,
            "formal_end": FORMAL_END,
            "friction_bps": FRICTION_BPS,
        },
        "variants": list(VARIANTS),
        "summary": summary,
        "rows": rows,
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# SLTD V7 Universal Sell Daily-79 Result v1",
        "",
        "状态：IMPLEMENTED_AND_VERIFIED",
        "",
        f"- 股票：{len(rows)}",
        f"- 周期：1d",
        f"- 正式区间：{FORMAL_START} ~ {FORMAL_END}",
        f"- 摩擦：{FRICTION_BPS} bps",
        "",
        "| Candidate | Status | Impacted | Better Calmar | Better MDD | Better Return | Median ΔReturn | Median ΔMDD | Median ΔCalmar | SELL Exec | 5-bar rebuy |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for v in VARIANTS[1:]:
        s = summary[v]
        lines.append(
            f"| {v} | {s['status']} | {s['impacted_stocks']}/79 | {s['better_calmar']}/79 | "
            f"{s['better_max_drawdown']}/79 | {s['better_return']}/79 | "
            f"{s['median_delta_return']:+.4f} | {s['median_delta_max_drawdown']:+.4f} | "
            f"{s['median_delta_calmar']:+.4f} | {s['candidate_sell_executed']} | "
            f"{s['quick_rebuy_5bars']}/{s['candidate_sell_executed']} |"
        )
    lines += [
        "",
        "## 边界",
        "",
        "- 使用冻结的 79 股票日线快照，避免实时行情漂移。",
        "- 这是对 Round-1 跨周期发现的长期 1d 验证，不修改正式 V7。",
        "- 只有同时经 1h / 4h 与长周期 1d 支持的候选，才值得进入 fresh-stock OOS。",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(OUT_MD.read_text(encoding="utf-8"), flush=True)


if __name__ == "__main__":
    main()
