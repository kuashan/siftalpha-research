#!/usr/bin/env python3
"""SLTD E v1 all archived stock daily validation (79 + fresh OOS10 = 89)."""
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
PHASE8 = ROOT / "research" / "ssss_reboot_v1" / "phase8"
PHASE7 = ROOT / "research" / "ssss_reboot_v1" / "phase7"
INTEGRATION = ROOT / "integrations" / "sltd_v7_siftalpha_v1"
sys.path.insert(0, str(INTEGRATION))
sys.path.insert(0, str(PHASE7))

import e_strategy  # noqa: E402
import strategy as v7  # noqa: E402
import sltd_v6_position_policy_batch_v1 as core  # noqa: E402

FORMAL_START = pd.Timestamp("2020-01-02")
FORMAL_END = pd.Timestamp("2026-09-30")
OOS10 = ["WFC","LMT","PM","ADP","WM","UNP","SO","VZ","PANW","CVS"]
OUT_JSON = PHASE8 / "SLTD_E_ALL_STOCK_VALIDATION_RESULT_v1.json"
OUT_MD = PHASE8 / "SLTD_E_ALL_STOCK_VALIDATION_RESULT_v1.md"
ARCHIVED_V7 = PHASE8 / "SLTD_V7_79_STOCK_ROBUSTNESS_RESULT_v1.json"

YEARS = list(range(2020, 2027))
ERAS = {
    "EARLY_2020_2021": ("2020-01-02", "2021-12-31"),
    "MIDDLE_2022_2023": ("2022-01-01", "2023-12-31"),
    "LATE_2024_2026Q3": ("2024-01-01", "2026-09-30"),
}

def pct(x: float) -> str:
    return f"{100.0 * x:.2f}%"

def read_frame(path: Path) -> pd.DataFrame:
    with gzip.open(path, "rt", encoding="utf-8") as f:
        frame = pd.read_csv(f, parse_dates=["Date"])
    frame = frame[["Date","Open","High","Low","Close","Volume"]].copy()
    frame["Date"] = pd.to_datetime(frame["Date"]).dt.tz_localize(None)
    for col in ["Open","High","Low","Close","Volume"]:
        frame[col] = pd.to_numeric(frame[col], errors="coerce")
    frame = frame.dropna(subset=["Date","Open","High","Low","Close"]).sort_values("Date")
    return frame.drop_duplicates("Date", keep="last").reset_index(drop=True)

def all_frames() -> tuple[dict[str, pd.DataFrame], dict[str, str]]:
    frames, groups = {}, {}
    for batch, symbols in core.BATCHES.items():
        for symbol in symbols:
            path = PHASE7 / "data_snapshot" / f"batch_{batch:02d}_stocks" / f"{symbol}.csv.gz"
            if not path.exists():
                raise RuntimeError(f"missing archived stock file: {path}")
            if symbol in frames:
                raise RuntimeError(f"duplicate symbol: {symbol}")
            frames[symbol] = read_frame(path)
            groups[symbol] = f"B{batch}"
    for symbol in OOS10:
        path = PHASE8 / "oos10_data_snapshot" / f"{symbol}.csv.gz"
        if not path.exists():
            raise RuntimeError(f"missing OOS stock file: {path}")
        if symbol in frames:
            raise RuntimeError(f"OOS10 overlap with prior 79: {symbol}")
        frames[symbol] = read_frame(path)
        groups[symbol] = "OOS10"
    if len(frames) != 89 or len(set(frames)) != 89:
        raise RuntimeError(f"expected 89 unique stocks, got {len(frames)}")
    return frames, groups

def to_candles(frame: pd.DataFrame) -> list[dict]:
    out = []
    for row in frame.itertuples(index=False):
        date = pd.Timestamp(row.Date)
        out.append({
            "date": date.strftime("%Y-%m-%d"),
            "open_time": int(date.tz_localize("UTC").timestamp()),
            "open": float(row.Open),
            "high": float(row.High),
            "low": float(row.Low),
            "close": float(row.Close),
            "volume": float(row.Volume) if pd.notna(row.Volume) else 0.0,
        })
    return out

def max_drawdown(curve: np.ndarray) -> float:
    peak = np.maximum.accumulate(curve)
    return float(np.min(curve / peak - 1.0)) if len(curve) else 0.0

def metric_block(dates: list[str], curve: np.ndarray) -> dict:
    days = max(1, (pd.Timestamp(dates[-1]) - pd.Timestamp(dates[0])).days)
    total = float(curve[-1] - 1.0)
    cagr = float(curve[-1] ** (365.25 / days) - 1.0) if curve[-1] > 0 else -1.0
    mdd = max_drawdown(curve)
    calmar = cagr / abs(mdd) if mdd < -1e-12 else (999.0 if cagr > 0 else 0.0)
    return {"start":dates[0],"end":dates[-1],"total_return":total,"cagr":cagr,"max_drawdown":mdd,"calmar":float(calmar)}

def align_portfolio(per_symbol: dict[str, dict]) -> tuple[list[str], np.ndarray]:
    common = set.intersection(*(set(x["dates"]) for x in per_symbol.values()))
    dates = sorted(common)
    if len(dates) < 2:
        raise RuntimeError("no common dates")
    curves = []
    for symbol, result in per_symbol.items():
        pos = {d:i for i,d in enumerate(result["dates"])}
        curves.append(np.asarray([result["curve"][pos[d]] for d in dates], dtype=float))
    return dates, np.mean(np.vstack(curves), axis=0)

def portfolio_metrics(per_symbol: dict[str, dict]) -> dict:
    dates, curve = align_portfolio(per_symbol)
    out = metric_block(dates, curve)
    out["turnover_mean"] = float(np.mean([x.get("turnover", 0.0) for x in per_symbol.values()]))
    out["position_changes_sum"] = int(sum(x.get("position_changes", 0) for x in per_symbol.values()))
    out["time_in_market_mean"] = float(np.mean([x.get("time_in_market", 0.0) for x in per_symbol.values()]))
    out["profitable_symbols"] = int(sum(x["total_return"] > 0 for x in per_symbol.values()))
    out["positive_calmar_symbols"] = int(sum(x["calmar"] > 0 for x in per_symbol.values()))
    return out

def slice_portfolio(per_symbol: dict[str, dict], start: str, end: str) -> dict | None:
    dates, curve = align_portfolio(per_symbol)
    idx = np.flatnonzero(np.asarray([start <= d <= end for d in dates], dtype=bool))
    if len(idx) < 2:
        return None
    d = [dates[i] for i in idx]
    c = curve[idx] / curve[idx[0]]
    return metric_block(d, c)

def v7_result(frame: pd.DataFrame, friction_bps: float) -> dict:
    candles = to_candles(frame)
    ledger = v7.build_ledger(candles, "X")
    sim = v7.simulate_policy(candles, ledger, friction_bps=friction_bps)
    formal_idx = [i for i,b in enumerate(candles) if FORMAL_START <= pd.Timestamp(b["date"]) <= FORMAL_END]
    dates = [candles[i]["date"] for i in formal_idx]
    curve = np.asarray([sim["equity_curve"][i] for i in formal_idx], dtype=float)
    m = metric_block(dates, curve)
    m.update({
        "dates":dates,"curve":curve,"turnover":0.0,
        "position_changes":int(sum(FORMAL_START <= pd.Timestamp(x["execution_date"]) <= FORMAL_END for x in sim["markers"])),
        "time_in_market":float(np.mean([1.0 if sim["positions"][i]["fraction"] > 1e-12 else 0.0 for i in formal_idx])),
    })
    return m

def buy_hold_result(frame: pd.DataFrame, friction_bps: float) -> dict:
    formal = frame[(frame["Date"] >= FORMAL_START) & (frame["Date"] <= FORMAL_END)].copy()
    dates = formal["Date"].dt.strftime("%Y-%m-%d").tolist()
    opens = formal["Open"].astype(float).to_numpy()
    closes = formal["Close"].astype(float).to_numpy()
    cost_rate = friction_bps / 10000.0
    shares = 1.0 / (opens[0] * (1.0 + cost_rate))
    cash = 1.0 - shares * opens[0] * (1.0 + cost_rate)
    curve = cash + shares * closes
    m = metric_block(dates, curve)
    m.update({"dates":dates,"curve":curve,"turnover":1.0/(1.0+cost_rate),"position_changes":1,"time_in_market":1.0})
    return m

def e_result(frame: pd.DataFrame, friction_bps: float, symbol: str) -> dict:
    candles = to_candles(frame)
    primary = v7.build_ledger(candles, symbol)
    higher_tf, higher_bars = e_strategy.build_higher_bars(candles, "1d", {})
    if higher_tf != "5d":
        raise RuntimeError(f"{symbol}: wrong higher timeframe {higher_tf}")
    higher = v7.build_ledger(higher_bars, f"{symbol}:5d")
    higher_at_primary = [None] * len(candles)
    h = -1
    for i in range(len(candles)):
        while h + 1 < len(higher_bars) and int(higher_bars[h+1]["_source_end_index"]) <= i:
            h += 1
        if h >= 0:
            higher_at_primary[i] = (h, higher[h])

    formal_idx = [i for i,b in enumerate(candles) if FORMAL_START <= pd.Timestamp(b["date"]) <= FORMAL_END]
    if higher_at_primary[formal_idx[0]] is None:
        raise RuntimeError(f"{symbol}: missing higher timeframe warmup")

    cash, shares, target = 1.0, 0.0, 0.0
    b1_used = b2_used = b3_used = False
    sell_stage = 0
    pending = None
    turnover = 0.0
    changes = 0
    invested_days = 0
    rule_exec, action_exec = Counter(), Counter()
    dates, curve, targets = [], [], []
    cost_rate = friction_bps / 10000.0

    for i in formal_idx:
        bar = candles[i]
        op, cl = float(bar["open"]), float(bar["close"])
        pre_equity = cash + shares * op
        if pending is not None:
            kind = str(pending["kind"])
            if kind == "BUY":
                target = min(e_strategy.E_MAX_POSITION, target + float(pending["delta"]))
                if "E_BUY_1_PRIMARY_CLOSE_BREAK_BELOW_ZD1" in pending["rule_ids"]: b1_used = True
                if "E_BUY_2_HIGHER_CLOSE_BELOW_ZD1" in pending["rule_ids"]: b2_used = True
                if "E_BUY_3_TOUCH_GZB_BAND" in pending["rule_ids"]: b3_used = True
            elif kind == "SELL50":
                target = max(0.0, target - 0.50); sell_stage = max(sell_stage, 1)
            elif kind == "SELL25":
                target = max(0.0, target - 0.25); sell_stage = max(sell_stage, 2)
            elif kind == "EXIT":
                target = 0.0
            else:
                raise RuntimeError(f"{symbol}: unknown E action {kind}")

            position_value = shares * op
            order_value = target * pre_equity - position_value
            if target <= 1e-12:
                order_value = -position_value
            if order_value > 1e-14:
                order_value = min(order_value, max(0.0, cash/(1.0+cost_rate)))
            elif order_value < -1e-14:
                order_value = max(order_value, -position_value)
            if abs(order_value) > 1e-14:
                cost = abs(order_value) * cost_rate
                shares += order_value / op
                cash -= order_value + cost
                turnover += abs(order_value) / pre_equity
                changes += 1
                if shares <= 1e-12: shares = 0.0
            action_exec[kind] += 1
            rule_exec.update(pending["rule_ids"])
            if target <= 1e-12:
                target = 0.0
                b1_used = b2_used = b3_used = False
                sell_stage = 0
            pending = None

        dates.append(bar["date"])
        curve.append(cash + shares * cl)
        targets.append(target)
        if shares > 1e-12:
            invested_days += 1

        row = primary[i]
        pair = higher_at_primary[i]
        higher_row = pair[1] if pair is not None else None
        signal = None

        if target > 1e-12:
            inner_up = e_strategy._break_above_zk1(i, candles, primary)
            exit_active = sell_stage > 0 or inner_up
            band_hit = e_strategy._band_touch(bar, row)
            bs = row.get("BS")
            bs_hit = bs is not None and float(bar["high"]) >= float(bs)
            if exit_active and band_hit:
                signal = {"kind":"EXIT","rule_ids":["E_SELL_3_TOUCH_GZB_BAND_FULL_EXIT"]}
            elif sell_stage > 0 and row.get("ZK1") is not None and float(bar["close"]) < float(row["ZK1"]):
                signal = {"kind":"EXIT","rule_ids":["E_SELL_4_CLOSE_BACK_BELOW_ZK1_FULL_EXIT"]}
            elif exit_active and bs_hit:
                signal = {"kind":"SELL25","rule_ids":["E_SELL_2_TOUCH_BS_MINUS_25PP"]}
            elif sell_stage == 0 and inner_up:
                signal = {"kind":"SELL50","rule_ids":["E_SELL_1_PRIMARY_CLOSE_BREAK_ABOVE_ZK1_MINUS_50PP"]}

        if signal is None and sell_stage == 0:
            state = str(row.get("color") or "")
            inner_down = (not b1_used and state in {"BLUE","GRAY"} and e_strategy._break_below_zd1(i, candles, primary))
            if inner_down:
                rule_ids = ["E_BUY_1_PRIMARY_CLOSE_BREAK_BELOW_ZD1"]
                delta = 0.25
                if (not b2_used and higher_row is not None and higher_row.get("ZD1") is not None
                    and float(higher_row["close"]) < float(higher_row["ZD1"])):
                    rule_ids.append("E_BUY_2_HIGHER_CLOSE_BELOW_ZD1"); delta += 0.25
                signal = {"kind":"BUY","delta":delta,"rule_ids":rule_ids}
            elif b1_used and not b3_used and e_strategy._band_touch(bar, row):
                signal = {"kind":"BUY","delta":0.25,"rule_ids":["E_BUY_3_TOUCH_GZB_BAND"]}

        pending = signal

    curve_arr = np.asarray(curve, dtype=float)
    m = metric_block(dates, curve_arr)
    m.update({
        "dates":dates,"curve":curve_arr,"turnover":float(turnover),"position_changes":int(changes),
        "time_in_market":float(invested_days/len(dates)),
        "rule_execution_counts":dict(rule_exec),"action_execution_counts":dict(action_exec),
        "ending_target_position":float(target),"mean_target_position":float(np.mean(targets)),
    })
    return m

def compact(result: dict) -> dict:
    keys = ["total_return","cagr","max_drawdown","calmar","turnover","position_changes","time_in_market"]
    out = {k:result[k] for k in keys}
    for k in ("rule_execution_counts","action_execution_counts","ending_target_position","mean_target_position"):
        if k in result: out[k] = result[k]
    return out

def compare(a: dict[str, dict], b: dict[str, dict]) -> dict:
    symbols = list(a)
    return {
        "better_return":int(sum(a[s]["total_return"] > b[s]["total_return"] for s in symbols)),
        "better_cagr":int(sum(a[s]["cagr"] > b[s]["cagr"] for s in symbols)),
        "better_maxdd":int(sum(a[s]["max_drawdown"] > b[s]["max_drawdown"] for s in symbols)),
        "better_calmar":int(sum(a[s]["calmar"] > b[s]["calmar"] for s in symbols)),
        "median_delta_return":float(statistics.median(a[s]["total_return"] - b[s]["total_return"] for s in symbols)),
        "median_delta_cagr":float(statistics.median(a[s]["cagr"] - b[s]["cagr"] for s in symbols)),
        "median_delta_maxdd":float(statistics.median(a[s]["max_drawdown"] - b[s]["max_drawdown"] for s in symbols)),
        "median_delta_calmar":float(statistics.median(a[s]["calmar"] - b[s]["calmar"] for s in symbols)),
    }

def subset(per_symbol: dict[str, dict], symbols: list[str]) -> dict[str, dict]:
    return {s:per_symbol[s] for s in symbols}

def main() -> None:
    frames, groups = all_frames()
    prior79 = [s for batch in core.BATCHES.values() for s in batch]
    all89 = prior79 + OOS10
    if list(frames) != all89:
        raise RuntimeError("universe order drift")

    systems = {f:{n:{} for n in ("E","V7","BUY_HOLD")} for f in ("5bps","10bps")}
    for friction_name,bps in (("5bps",5.0),("10bps",10.0)):
        for n,symbol in enumerate(all89,1):
            frame = frames[symbol]
            systems[friction_name]["E"][symbol] = e_result(frame,bps,symbol)
            systems[friction_name]["V7"][symbol] = v7_result(frame,bps)
            systems[friction_name]["BUY_HOLD"][symbol] = buy_hold_result(frame,bps)
            print("SYMBOL_PASS",friction_name,n,len(all89),symbol,flush=True)

    archived = json.loads(ARCHIVED_V7.read_text(encoding="utf-8"))
    parity_errors = []
    for symbol in prior79:
        expected = archived["per_symbol"][symbol]["5bps"]["CANDIDATE_B_DROP_B3_S1_S3"]["total_return"]
        actual = systems["5bps"]["V7"][symbol]["total_return"]
        if not math.isclose(actual,expected,rel_tol=1e-10,abs_tol=1e-10):
            parity_errors.append((symbol,actual,expected))
    if parity_errors:
        raise RuntimeError(f"V7 parity failed: {parity_errors[:5]}")
    print("V7_79_PARITY_PASS",len(prior79),flush=True)

    aggregates, comparisons, yearly, eras, total_rule_counts = {}, {}, {}, {}, {}
    for friction_name in ("5bps","10bps"):
        aggregates[friction_name], yearly[friction_name], eras[friction_name] = {}, {}, {}
        for system_name in ("E","V7","BUY_HOLD"):
            per = systems[friction_name][system_name]
            aggregates[friction_name][system_name] = {
                "all89":portfolio_metrics(per),
                "prior79":portfolio_metrics(subset(per,prior79)),
                "oos10":portfolio_metrics(subset(per,OOS10)),
            }
            yearly[friction_name][system_name] = {str(y):slice_portfolio(per,f"{y}-01-01",f"{y}-12-31") for y in YEARS}
            eras[friction_name][system_name] = {name:slice_portfolio(per,start,end) for name,(start,end) in ERAS.items()}
        comparisons[friction_name] = {
            "E_vs_V7_all89":compare(systems[friction_name]["E"],systems[friction_name]["V7"]),
            "E_vs_BUY_HOLD_all89":compare(systems[friction_name]["E"],systems[friction_name]["BUY_HOLD"]),
            "E_vs_V7_prior79":compare(subset(systems[friction_name]["E"],prior79),subset(systems[friction_name]["V7"],prior79)),
            "E_vs_V7_oos10":compare(subset(systems[friction_name]["E"],OOS10),subset(systems[friction_name]["V7"],OOS10)),
            "E_vs_BUY_HOLD_oos10":compare(subset(systems[friction_name]["E"],OOS10),subset(systems[friction_name]["BUY_HOLD"],OOS10)),
        }
        rc, ac = Counter(), Counter()
        for result in systems[friction_name]["E"].values():
            rc.update(result["rule_execution_counts"]); ac.update(result["action_execution_counts"])
        total_rule_counts[friction_name] = {"rules":dict(rc),"actions":dict(ac)}

    per_symbol_out = {}
    for symbol in all89:
        per_symbol_out[symbol] = {
            "group":groups[symbol],
            "5bps":{n:compact(systems["5bps"][n][symbol]) for n in ("E","V7","BUY_HOLD")},
            "10bps":{n:compact(systems["10bps"][n][symbol]) for n in ("E","V7","BUY_HOLD")},
        }

    output = {
        "meta":{
            "study":"SLTD_E_ALL_STOCK_VALIDATION_V1","status":"COMPLETE","universe_count":89,
            "prior79_count":79,"fresh_oos10_count":10,"symbols":all89,
            "formal_window":"2020-01-02..2026-09-30","selected_timeframe":"1d","higher_timeframe":"5d",
            "execution":"SIGNAL_CLOSE_TO_NEXT_AVAILABLE_OPEN","frictions_bps":[5.0,10.0],
            "e_source_commit":"f990eb9d2d4567d8acdc617fb1b4b9dd01b45f1c",
            "v7_source_commit":"5f9ea4d8fa434b54afdbf32a1cb21ef2f3cb4042",
            "v7_79_parity":"PASS","generated_at_utc":datetime.now(timezone.utc).isoformat(),
        },
        "aggregates":aggregates,"comparisons":comparisons,"yearly":yearly,"eras":eras,
        "e_execution_counts":total_rule_counts,"per_symbol":per_symbol_out,
    }
    OUT_JSON.write_text(json.dumps(output,indent=2),encoding="utf-8")

    c_v7 = comparisons["5bps"]["E_vs_V7_all89"]
    c_bh = comparisons["5bps"]["E_vs_BUY_HOLD_all89"]
    o_v7 = comparisons["5bps"]["E_vs_V7_oos10"]
    o_bh = comparisons["5bps"]["E_vs_BUY_HOLD_oos10"]
    lines = [
        "# SLTD E All-Stock Validation v1","",
        "Status: **COMPLETE**","",
        "Universe: **89 unique mainstream U.S. stocks** = prior 79 + fresh OOS10.","",
        "Formal window: **2020-01-02 through 2026-09-30**.","",
        "Selected timeframe: **1d**; E higher timeframe: **5d**.","",
        "Execution: signal close -> next available open. Primary friction 5 bps; stress 10 bps.","",
        "## Equal-weight portfolio — 5 bps","",
        "| Scope | System | Return | CAGR | MaxDD | Calmar | Time in market | Changes |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for scope in ("all89","prior79","oos10"):
        for name,label in (("E","E"),("V7","V7 12-rule"),("BUY_HOLD","Buy & Hold")):
            m = aggregates["5bps"][name][scope]
            lines.append(f"| {scope} | {label} | {pct(m['total_return'])} | {pct(m['cagr'])} | {pct(m['max_drawdown'])} | {m['calmar']:.3f} | {pct(m['time_in_market_mean'])} | {m['position_changes_sum']} |")
    lines += [
        "","## Breadth — E vs V7, 5 bps","",
        f"- all89 better Return: **{c_v7['better_return']}/89**",
        f"- all89 better MaxDD: **{c_v7['better_maxdd']}/89**",
        f"- all89 better Calmar: **{c_v7['better_calmar']}/89**",
        f"- all89 median ΔReturn: **{pct(c_v7['median_delta_return'])}**",
        f"- all89 median ΔMaxDD: **{pct(c_v7['median_delta_maxdd'])}**",
        f"- all89 median ΔCalmar: **{c_v7['median_delta_calmar']:+.3f}**",
        f"- OOS10 better Return / MaxDD / Calmar: **{o_v7['better_return']}/10 / {o_v7['better_maxdd']}/10 / {o_v7['better_calmar']}/10**",
        "","## Breadth — E vs Buy & Hold, 5 bps","",
        f"- all89 better Return: **{c_bh['better_return']}/89**",
        f"- all89 better MaxDD: **{c_bh['better_maxdd']}/89**",
        f"- all89 better Calmar: **{c_bh['better_calmar']}/89**",
        f"- all89 median ΔReturn: **{pct(c_bh['median_delta_return'])}**",
        f"- all89 median ΔMaxDD: **{pct(c_bh['median_delta_maxdd'])}**",
        f"- all89 median ΔCalmar: **{c_bh['median_delta_calmar']:+.3f}**",
        f"- OOS10 better Return / MaxDD / Calmar: **{o_bh['better_return']}/10 / {o_bh['better_maxdd']}/10 / {o_bh['better_calmar']}/10**",
        "","## E execution counts — 5 bps","",
    ]
    for rule,count in sorted(total_rule_counts["5bps"]["rules"].items()):
        lines.append(f"- {rule}: **{count}**")
    lines += ["","## Calendar-year equal-weight returns — 5 bps","",
              "| Year | E | V7 | Buy & Hold |","|---|---:|---:|---:|"]
    for y in YEARS:
        e,v,b = yearly["5bps"]["E"][str(y)],yearly["5bps"]["V7"][str(y)],yearly["5bps"]["BUY_HOLD"][str(y)]
        lines.append(f"| {y} | {pct(e['total_return'])} | {pct(v['total_return'])} | {pct(b['total_return'])} |")
    lines += ["","## Era Calmar — 5 bps","",
              "| Era | E | V7 | Buy & Hold |","|---|---:|---:|---:|"]
    for era in ERAS:
        e,v,b = eras["5bps"]["E"][era],eras["5bps"]["V7"][era],eras["5bps"]["BUY_HOLD"][era]
        lines.append(f"| {era} | {e['calmar']:.3f} | {v['calmar']:.3f} | {b['calmar']:.3f} |")
    lines += ["","## Interpretation boundary","",
              "- The prior 79 stocks are reused research data, not fresh OOS.",
              "- The OOS10 subset is reported separately.",
              "- No E rule is changed or promoted by this run.",
              "- Frozen V7 79-stock parity check: **PASS**.","",
              "`SLTD_E_ALL_STOCK_VALIDATION_V1 = COMPLETE`",""]
    OUT_MD.write_text("\n".join(lines),encoding="utf-8")

if __name__ == "__main__":
    main()
