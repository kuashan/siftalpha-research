#!/usr/bin/env python3
"""SLTD E7B 89-stock validation.

E7B:
- preserves frozen V7 candidate entry-side resolution and 25pp pyramiding;
- ignores original V7 ordinary SELL execution and original C2;
- pre-breakout adapted C2: GREEN and High < GZB4 -> full exit next open;
- first High crossing above ZK1 -> sell 50% of current holding next open;
- after half-sale execution, disable adapted C2 and all ordinary signals;
- final full exit on BS touch, eligible shallow-gray-band touch, or Low < ZK1.
"""
from __future__ import annotations

import gzip
import json
import math
import statistics
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
PHASE7 = ROOT / "research" / "ssss_reboot_v1" / "phase7"
PHASE8 = ROOT / "research" / "ssss_reboot_v1" / "phase8"
sys.path.insert(0, str(PHASE7))
sys.path.insert(0, str(PHASE8))

import sltd_v6_position_policy_batch_v1 as core  # noqa: E402
import sltd_v7_combination_ablation_v1 as combo  # noqa: E402

FORMAL_START = pd.Timestamp("2020-01-02")
FORMAL_END = pd.Timestamp("2026-09-30")
OOS10 = ["WFC","LMT","PM","ADP","WM","UNP","SO","VZ","PANW","CVS"]
PRIOR79 = [s for xs in core.BATCHES.values() for s in xs]
ALL89 = PRIOR79 + OOS10

OUT_JSON = PHASE8 / "SLTD_E7B_89_STOCK_VALIDATION_RESULT_v1.json"
OUT_MD = PHASE8 / "SLTD_E7B_89_STOCK_VALIDATION_RESULT_v1.md"
FROZEN_V7 = PHASE8 / "SLTD_V7_79_STOCK_ROBUSTNESS_RESULT_v1.json"

YEARS = list(range(2020, 2027))
ERAS = {
    "EARLY_2020_2021": ("2020-01-02", "2021-12-31"),
    "MIDDLE_2022_2023": ("2022-01-01", "2023-12-31"),
    "LATE_2024_2026Q3": ("2024-01-01", "2026-09-30"),
}

CANDIDATE_DROPS = combo.VARIANTS["DROP_B3_S1_S3"]


def pct(x: float) -> str:
    return f"{100.0 * float(x):.2f}%"


def read_frame(path: Path) -> pd.DataFrame:
    with gzip.open(path, "rt", encoding="utf-8") as f:
        df = pd.read_csv(f, parse_dates=["Date"])
    df["Date"] = pd.to_datetime(df["Date"]).dt.tz_localize(None)
    return df[["Date","Open","High","Low","Close","Volume"]].copy().sort_values("Date").reset_index(drop=True)


def read_ledger(path: Path) -> list[dict]:
    with gzip.open(path, "rt", encoding="utf-8") as f:
        df = pd.read_csv(f)
    rows = []
    for rec in df.to_dict("records"):
        for cls in ("BUY","HOLD","WAIT","SELL"):
            val = rec.get(cls)
            rec[cls] = [] if pd.isna(val) or str(val).strip() == "" else [x for x in str(val).split("|") if x]
        rows.append(rec)
    return rows


def load_universe():
    frames, ledgers, groups = {}, {}, {}
    for batch, symbols in core.BATCHES.items():
        for s in symbols:
            dp = PHASE7 / "data_snapshot" / f"batch_{batch:02d}_stocks" / f"{s}.csv.gz"
            lp = PHASE7 / "signal_ledgers" / f"BATCH_{batch:02d}_{s}_FIRST_OBSERVED.csv.gz"
            if not dp.exists() or not lp.exists():
                raise RuntimeError(f"missing frozen files for {s}")
            frames[s] = read_frame(dp)
            ledgers[s] = read_ledger(lp)
            groups[s] = f"B{batch}"
    for s in OOS10:
        dp = PHASE8 / "oos10_data_snapshot" / f"{s}.csv.gz"
        lp = PHASE8 / "oos10_signal_ledgers" / f"{s}_FIRST_OBSERVED.csv.gz"
        if not dp.exists() or not lp.exists():
            raise RuntimeError(f"missing frozen OOS files for {s}")
        if s in frames:
            raise RuntimeError(f"OOS overlap: {s}")
        frames[s] = read_frame(dp)
        ledgers[s] = read_ledger(lp)
        groups[s] = "OOS10"

    if len(frames) != 89 or len(set(frames)) != 89:
        raise RuntimeError(f"expected 89 unique stocks, got {len(frames)}")
    for s in ALL89:
        if len(frames[s]) != len(ledgers[s]):
            raise RuntimeError(f"{s}: frame/ledger length mismatch")
        frame_dates = frames[s]["Date"].dt.strftime("%Y-%m-%d").tolist()
        ledger_dates = [str(x["date"])[:10] for x in ledgers[s]]
        if frame_dates != ledger_dates:
            raise RuntimeError(f"{s}: frame/ledger date mismatch")
    return frames, ledgers, groups


def max_drawdown(curve: np.ndarray) -> float:
    peak = np.maximum.accumulate(curve)
    return float(np.min(curve / peak - 1.0)) if len(curve) else 0.0


def metric_block(dates: list[str], curve: np.ndarray) -> dict:
    days = max(1, (pd.Timestamp(dates[-1]) - pd.Timestamp(dates[0])).days)
    total = float(curve[-1] - 1.0)
    cagr = float(curve[-1] ** (365.25 / days) - 1.0) if curve[-1] > 0 else -1.0
    mdd = max_drawdown(curve)
    calmar = cagr / abs(mdd) if mdd < -1e-12 else (999.0 if cagr > 0 else 0.0)
    return {
        "start": dates[0], "end": dates[-1], "total_return": total,
        "cagr": cagr, "max_drawdown": mdd, "calmar": float(calmar)
    }


def _finite(x) -> bool:
    try:
        return math.isfinite(float(x))
    except (TypeError, ValueError):
        return False


def _upper_cross(row: dict) -> bool:
    return bool(row.get("upper"))


def _adapted_c2(row: dict) -> bool:
    return (
        str(row.get("color") or "").upper() == "GREEN"
        and _finite(row.get("high"))
        and _finite(row.get("GZB4"))
        and float(row["high"]) < float(row["GZB4"])
    )


def _bs_hit(row: dict) -> bool:
    return _finite(row.get("high")) and _finite(row.get("BS")) and float(row["high"]) >= float(row["BS"])


def _gray_band_eligible_hit(row: dict) -> bool:
    if not all(_finite(row.get(k)) for k in ("high","low","GZB3","GZB4","ZK1")):
        return False
    g3 = float(row["GZB3"])
    g4 = float(row["GZB4"])
    zk1 = float(row["ZK1"])
    if not (g4 > zk1):
        return False
    # Same band-intersection convention already used by the frozen SLTD ledger.
    return float(row["high"]) >= g4 and float(row["low"]) <= g3


def _failed_breakout(row: dict) -> bool:
    return _finite(row.get("low")) and _finite(row.get("ZK1")) and float(row["low"]) < float(row["ZK1"])


def simulate_e7b(frame: pd.DataFrame, ledger: list[dict], friction_bps: float) -> dict:
    dates_all = pd.to_datetime(frame["Date"]).dt.tz_localize(None)
    mask = (dates_all >= FORMAL_START) & (dates_all <= FORMAL_END)
    idx = np.flatnonzero(mask.to_numpy())
    if len(idx) < 2:
        raise RuntimeError("insufficient formal bars")

    dates = [pd.Timestamp(dates_all.iloc[i]).strftime("%Y-%m-%d") for i in idx]
    opens = frame["Open"].astype(float).to_numpy()[idx]
    closes = frame["Close"].astype(float).to_numpy()[idx]
    rows = [ledger[i] for i in idx]

    cash = 1.0
    shares = 0.0
    turnover = 0.0
    changes = 0
    invested = 0
    pending: dict | None = None
    exit_stage = False
    curve = np.empty(len(idx), dtype=float)
    stage_days = 0
    counts = Counter()
    entry_buys = 0
    cost_rate = friction_bps / 10000.0

    for j in range(len(idx)):
        op = float(opens[j])
        cl = float(closes[j])
        pre = cash + shares * op
        if pre <= 0:
            raise RuntimeError("non-positive equity")

        # Execute previous completed-bar signal at this open.
        if pending is not None:
            kind = pending["kind"]
            pos_value = shares * op
            order = 0.0

            if kind == "BUY":
                current_fraction = pos_value / pre if pre > 0 else 0.0
                target = 0.25 if shares <= 1e-14 else min(1.0, current_fraction + 0.25)
                order = target * pre - pos_value
                if order < 0:
                    order = 0.0
            elif kind == "HALF":
                # User-defined percentage: sell 50% of the current holding.
                order = -0.50 * pos_value
            elif kind == "EXIT":
                order = -pos_value
            else:
                raise RuntimeError(f"unknown pending kind {kind}")

            if order > 1e-14:
                order = min(order, max(0.0, cash / (1.0 + cost_rate)))
            elif order < -1e-14:
                order = max(order, -pos_value)

            executed = abs(order) > 1e-14
            if executed:
                fee = abs(order) * cost_rate
                shares += order / op
                cash -= order + fee
                turnover += abs(order) / pre
                changes += 1
                if shares <= 1e-12:
                    shares = 0.0

            if kind == "BUY" and executed:
                entry_buys += 1
                counts["BUY_EXEC"] += 1
            elif kind == "HALF" and executed:
                exit_stage = True
                counts["ZK1_HALF_EXEC"] += 1
            elif kind == "EXIT":
                if executed:
                    counts[pending["reason"] + "_EXEC"] += 1
                if shares <= 1e-12:
                    exit_stage = False

            pending = None

        curve[j] = cash + shares * cl
        if shares > 1e-12:
            invested += 1
        if exit_stage and shares > 1e-12:
            stage_days += 1

        row = rows[j]
        signal: dict | None = None

        if shares > 1e-12:
            if exit_stage:
                # Final-exit priority is only for attribution; all are full exits.
                if _bs_hit(row):
                    signal = {"kind":"EXIT","reason":"BS_FULL_EXIT"}
                elif _gray_band_eligible_hit(row):
                    signal = {"kind":"EXIT","reason":"GRAY_ABOVE_ZK1_FULL_EXIT"}
                elif _failed_breakout(row):
                    signal = {"kind":"EXIT","reason":"LOW_BELOW_ZK1_FULL_EXIT"}
            else:
                # First E7B upper crossing has priority over adapted C2.
                if _upper_cross(row):
                    signal = {"kind":"HALF","reason":"ZK1_HALF"}
                    counts["ZK1_HALF_SIGNAL"] += 1
                elif _adapted_c2(row):
                    signal = {"kind":"EXIT","reason":"ADAPTED_C2_FULL_EXIT"}
                    counts["ADAPTED_C2_SIGNAL"] += 1
                else:
                    # Preserve V7 candidate action resolution to isolate exit changes.
                    resolved = combo.resolve_row(row, CANDIDATE_DROPS)
                    if resolved == "BUY":
                        signal = {"kind":"BUY","reason":"V7_BUY"}
        else:
            # Flat: only frozen V7 candidate BUY can open a new E7B cycle.
            resolved = combo.resolve_row(row, CANDIDATE_DROPS)
            if resolved == "BUY":
                signal = {"kind":"BUY","reason":"V7_BUY"}

        pending = signal

    final = float(curve[-1])
    out = metric_block(dates, curve)
    out.update({
        "dates": dates,
        "curve": curve,
        "turnover": float(turnover),
        "position_changes": int(changes),
        "time_in_market": float(invested / len(idx)),
        "exit_stage_time": float(stage_days / len(idx)),
        "entry_buy_exec_count": int(entry_buys),
        "trigger_counts": dict(counts),
        "ending_in_exit_stage": bool(exit_stage),
        "ending_position_value_fraction": float((shares * float(closes[-1])) / final) if final > 0 else 0.0,
    })
    return out


def prepare_v7(frame: pd.DataFrame, ledger: list[dict]) -> dict:
    return combo.prepare_symbol(frame, ledger)


def simulate_v7(prep: dict, bps: float) -> dict:
    r = combo.simulate(prep, "DROP_B3_S1_S3", bps)
    return dict(r) | {"dates": list(prep["dates"])}


def buy_hold(frame: pd.DataFrame, bps: float) -> dict:
    formal = frame[(frame["Date"] >= FORMAL_START) & (frame["Date"] <= FORMAL_END)].copy()
    dates = formal["Date"].dt.strftime("%Y-%m-%d").tolist()
    opens = formal["Open"].astype(float).to_numpy()
    closes = formal["Close"].astype(float).to_numpy()
    cost = bps / 10000.0
    shares = 1.0 / (opens[0] * (1.0 + cost))
    cash = 1.0 - shares * opens[0] * (1.0 + cost)
    curve = cash + shares * closes
    out = metric_block(dates, curve)
    out.update({"dates":dates,"curve":curve,"turnover":1.0/(1.0+cost),"position_changes":1,"time_in_market":1.0})
    return out


def align(per_symbol: dict[str, dict]) -> tuple[list[str], np.ndarray]:
    common = set.intersection(*(set(r["dates"]) for r in per_symbol.values()))
    dates = sorted(common)
    if len(dates) < 2:
        raise RuntimeError("no common dates")
    curves = []
    for s,r in per_symbol.items():
        pos = {d:i for i,d in enumerate(r["dates"])}
        curves.append(np.asarray([r["curve"][pos[d]] for d in dates], dtype=float))
    return dates, np.mean(np.vstack(curves), axis=0)


def portfolio(per_symbol: dict[str, dict]) -> dict:
    dates, curve = align(per_symbol)
    out = metric_block(dates, curve)
    out.update({
        "turnover_mean": float(np.mean([r.get("turnover",0.0) for r in per_symbol.values()])),
        "position_changes_sum": int(sum(r.get("position_changes",0) for r in per_symbol.values())),
        "time_in_market_mean": float(np.mean([r.get("time_in_market",0.0) for r in per_symbol.values()])),
        "profitable_symbols": int(sum(r["total_return"] > 0 for r in per_symbol.values())),
        "positive_calmar_symbols": int(sum(r["calmar"] > 0 for r in per_symbol.values())),
    })
    return out


def slice_portfolio(per_symbol: dict[str, dict], start: str, end: str) -> dict | None:
    dates, curve = align(per_symbol)
    idx = np.flatnonzero(np.asarray([start <= d <= end for d in dates], dtype=bool))
    if len(idx) < 2:
        return None
    d = [dates[i] for i in idx]
    c = curve[idx] / curve[idx[0]]
    return metric_block(d, c)


def subset(per: dict[str,dict], symbols: list[str]) -> dict[str,dict]:
    return {s:per[s] for s in symbols}


def compare(a: dict[str,dict], b: dict[str,dict]) -> dict:
    symbols = list(a)
    return {
        "better_return": int(sum(a[s]["total_return"] > b[s]["total_return"] for s in symbols)),
        "better_cagr": int(sum(a[s]["cagr"] > b[s]["cagr"] for s in symbols)),
        "better_maxdd": int(sum(a[s]["max_drawdown"] > b[s]["max_drawdown"] for s in symbols)),
        "better_calmar": int(sum(a[s]["calmar"] > b[s]["calmar"] for s in symbols)),
        "median_delta_return": float(statistics.median(a[s]["total_return"] - b[s]["total_return"] for s in symbols)),
        "median_delta_cagr": float(statistics.median(a[s]["cagr"] - b[s]["cagr"] for s in symbols)),
        "median_delta_maxdd": float(statistics.median(a[s]["max_drawdown"] - b[s]["max_drawdown"] for s in symbols)),
        "median_delta_calmar": float(statistics.median(a[s]["calmar"] - b[s]["calmar"] for s in symbols)),
    }


def compact(r: dict) -> dict:
    keys = ("total_return","cagr","max_drawdown","calmar","turnover","position_changes","time_in_market")
    out = {k:r[k] for k in keys}
    for k in ("hard_exit_count","exit_stage_time","entry_buy_exec_count","trigger_counts","ending_in_exit_stage","ending_position_value_fraction"):
        if k in r:
            out[k] = r[k]
    return out


def main() -> None:
    frames, ledgers, groups = load_universe()
    prepared_v7 = {s:prepare_v7(frames[s],ledgers[s]) for s in ALL89}

    sims = {f:{name:{} for name in ("E7B","V7","BUY_HOLD")} for f in ("5bps","10bps")}
    for fname,bps in (("5bps",5.0),("10bps",10.0)):
        for n,s in enumerate(ALL89,1):
            sims[fname]["E7B"][s] = simulate_e7b(frames[s],ledgers[s],bps)
            sims[fname]["V7"][s] = simulate_v7(prepared_v7[s],bps)
            sims[fname]["BUY_HOLD"][s] = buy_hold(frames[s],bps)
            print("SIM_PASS",fname,n,89,s,flush=True)

    # Strict frozen V7 parity on the reused 79-stock set.
    frozen = json.loads(FROZEN_V7.read_text(encoding="utf-8"))
    parity_errors = []
    for s in PRIOR79:
        expected = frozen["per_symbol"][s]["5bps"]["CANDIDATE_B_DROP_B3_S1_S3"]["total_return"]
        actual = sims["5bps"]["V7"][s]["total_return"]
        if not math.isclose(actual, expected, rel_tol=1e-10, abs_tol=1e-10):
            parity_errors.append((s,actual,expected))
    if parity_errors:
        raise RuntimeError(f"V7 parity failed: {parity_errors[:5]}")
    print("V7_79_PARITY_PASS",flush=True)

    aggregates, comparisons, yearly, eras, trigger_totals = {}, {}, {}, {}, {}
    for fname in ("5bps","10bps"):
        aggregates[fname], yearly[fname], eras[fname] = {}, {}, {}
        for name in ("E7B","V7","BUY_HOLD"):
            per = sims[fname][name]
            aggregates[fname][name] = {
                "all89": portfolio(per),
                "prior79": portfolio(subset(per,PRIOR79)),
                "oos10": portfolio(subset(per,OOS10)),
            }
            yearly[fname][name] = {str(y):slice_portfolio(per,f"{y}-01-01",f"{y}-12-31") for y in YEARS}
            eras[fname][name] = {era:slice_portfolio(per,a,b) for era,(a,b) in ERAS.items()}

        comparisons[fname] = {
            "E7B_vs_V7_all89": compare(sims[fname]["E7B"],sims[fname]["V7"]),
            "E7B_vs_V7_prior79": compare(subset(sims[fname]["E7B"],PRIOR79),subset(sims[fname]["V7"],PRIOR79)),
            "E7B_vs_V7_oos10": compare(subset(sims[fname]["E7B"],OOS10),subset(sims[fname]["V7"],OOS10)),
            "E7B_vs_BUY_HOLD_all89": compare(sims[fname]["E7B"],sims[fname]["BUY_HOLD"]),
            "E7B_vs_BUY_HOLD_oos10": compare(subset(sims[fname]["E7B"],OOS10),subset(sims[fname]["BUY_HOLD"],OOS10)),
        }
        total = Counter()
        for r in sims[fname]["E7B"].values():
            total.update(r["trigger_counts"])
        trigger_totals[fname] = dict(total)

    per_symbol = {
        s:{
            "group":groups[s],
            "5bps":{n:compact(sims["5bps"][n][s]) for n in ("E7B","V7","BUY_HOLD")},
            "10bps":{n:compact(sims["10bps"][n][s]) for n in ("E7B","V7","BUY_HOLD")},
        } for s in ALL89
    }

    output = {
        "meta":{
            "study":"SLTD_E7B_89_STOCK_VALIDATION_V1",
            "status":"COMPLETE",
            "universe_count":89,
            "prior79_count":79,
            "fresh_oos10_count":10,
            "symbols":ALL89,
            "formal_window":"2020-01-02..2026-09-30",
            "timeframe":"1d",
            "execution":"SIGNAL_CLOSE_TO_NEXT_AVAILABLE_OPEN",
            "frictions_bps":[5.0,10.0],
            "v7_frozen_commit":"5f9ea4d8fa434b54afdbf32a1cb21ef2f3cb4042",
            "v7_79_parity":"PASS",
            "e7b_exit":"ZK1_UPPER_CROSS_SELL_50_PERCENT_CURRENT_THEN_FULL_EXIT",
            "e7b_adapted_c2":"PRE_BREAKOUT_GREEN_AND_HIGH_BELOW_GZB4_FULL_EXIT",
            "generated_at_utc":datetime.now(timezone.utc).isoformat(),
        },
        "aggregates":aggregates,
        "comparisons":comparisons,
        "yearly":yearly,
        "eras":eras,
        "e7b_trigger_totals":trigger_totals,
        "per_symbol":per_symbol,
    }
    OUT_JSON.write_text(json.dumps(output,indent=2),encoding="utf-8")

    a = aggregates["5bps"]
    cv = comparisons["5bps"]["E7B_vs_V7_all89"]
    ov = comparisons["5bps"]["E7B_vs_V7_oos10"]
    cb = comparisons["5bps"]["E7B_vs_BUY_HOLD_all89"]
    lines = [
        "# SLTD E7B 89-Stock Validation v1","",
        "Status: **COMPLETE**","",
        "Universe: **89 unique stocks = prior79 + fresh OOS10**.","",
        "Window: **2020-01-02..2026-09-30**, timeframe **1d**.","",
        "Execution: completed-bar signal -> next available open. Primary friction **5 bps**, stress **10 bps**.","",
        "## Equal-weight portfolio — 5 bps","",
        "| Scope | System | Return | CAGR | MaxDD | Calmar | Time in market | Changes |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for scope in ("all89","prior79","oos10"):
        for name,label in (("E7B","E7B"),("V7","Frozen V7"),("BUY_HOLD","Buy & Hold")):
            m = a[name][scope]
            lines.append(f"| {scope} | {label} | {pct(m['total_return'])} | {pct(m['cagr'])} | {pct(m['max_drawdown'])} | {m['calmar']:.3f} | {pct(m['time_in_market_mean'])} | {m['position_changes_sum']} |")

    lines += [
        "","## Breadth — E7B vs frozen V7, 5 bps","",
        f"- all89 better Return: **{cv['better_return']}/89**",
        f"- all89 better CAGR: **{cv['better_cagr']}/89**",
        f"- all89 better MaxDD: **{cv['better_maxdd']}/89**",
        f"- all89 better Calmar: **{cv['better_calmar']}/89**",
        f"- all89 median ΔReturn: **{pct(cv['median_delta_return'])}**",
        f"- all89 median ΔMaxDD: **{pct(cv['median_delta_maxdd'])}**",
        f"- all89 median ΔCalmar: **{cv['median_delta_calmar']:+.3f}**",
        f"- OOS10 better Return / MaxDD / Calmar: **{ov['better_return']}/10 / {ov['better_maxdd']}/10 / {ov['better_calmar']}/10**",
        "","## Breadth — E7B vs Buy & Hold, 5 bps","",
        f"- all89 better Return: **{cb['better_return']}/89**",
        f"- all89 better MaxDD: **{cb['better_maxdd']}/89**",
        f"- all89 better Calmar: **{cb['better_calmar']}/89**",
        "","## E7B trigger totals — 5 bps","",
    ]
    for k,v in sorted(trigger_totals["5bps"].items()):
        lines.append(f"- {k}: **{v}**")

    lines += ["","## Calendar-year equal-weight returns — 5 bps","",
              "| Year | E7B | V7 | Buy & Hold |","|---|---:|---:|---:|"]
    for y in YEARS:
        e,v,b = yearly["5bps"]["E7B"][str(y)],yearly["5bps"]["V7"][str(y)],yearly["5bps"]["BUY_HOLD"][str(y)]
        lines.append(f"| {y} | {pct(e['total_return'])} | {pct(v['total_return'])} | {pct(b['total_return'])} |")

    lines += ["","## Era Calmar — 5 bps","",
              "| Era | E7B | V7 | Buy & Hold |","|---|---:|---:|---:|"]
    for era in ERAS:
        e,v,b = eras["5bps"]["E7B"][era],eras["5bps"]["V7"][era],eras["5bps"]["BUY_HOLD"][era]
        lines.append(f"| {era} | {e['calmar']:.3f} | {v['calmar']:.3f} | {b['calmar']:.3f} |")

    lines += ["","## Boundaries","",
              "- V7 remains frozen and unchanged.",
              "- Prior79 is reused research data; OOS10 is shown separately.",
              "- This run does not auto-promote E7B.",
              "- Frozen V7 79-stock parity: **PASS**.","",
              "SLTD_E7B_89_STOCK_VALIDATION_V1 = COMPLETE",""]
    OUT_MD.write_text("\n".join(lines),encoding="utf-8")


if __name__ == "__main__":
    main()
