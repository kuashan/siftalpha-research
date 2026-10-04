#!/usr/bin/env python3
"""Phase18 Stage B: A-share integrated holdout.

Compares:
A) frozen 12 rules only
B) frozen 12 rules + C2
C) frozen 12 rules + C2 + A-share Severe Risk

Only frozen DEVELOPMENT 35 symbols are read. Fresh15 remains untouched.
"""
from __future__ import annotations

import json
import math
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
PHASE11 = ROOT.parent / "phase11"
PHASE14 = ROOT.parent / "phase14"
INTEGRATION = ROOT.parents[2] / "integrations" / "sltd_v7_siftalpha_v1"

sys.path.insert(0, str(PHASE11))
sys.path.insert(0, str(PHASE14))
sys.path.insert(0, str(INTEGRATION))

import pure_sltd_state_probability_v1 as p11  # noqa: E402
import sltd_state_score_momentum_stage_b_v3 as mom  # noqa: E402
import strategy as sltd  # noqa: E402

UNIVERSE = json.loads((ROOT / "A_SHARE_50_UNIVERSE_V1.json").read_text(encoding="utf-8"))
DATA_DIR = ROOT / "ashare50_data_snapshot_v3"
STAGE_A_PATH = ROOT / "SLTD_ASHARE50_INTEGRATED_RISK_V1_STAGE_A_RESULT.json"
OUT_JSON = ROOT / "SLTD_ASHARE50_INTEGRATED_RISK_V1_STAGE_B_RESULT.json"
OUT_MD = ROOT / "SLTD_ASHARE50_INTEGRATED_RISK_V1_STAGE_B_RESULT.md"

FORMAL_START = pd.Timestamp("2025-01-02")
FORMAL_END = pd.Timestamp("2026-09-30")

SYSTEM_A = "SLTD_12_RULES_ONLY"
SYSTEM_B = "SLTD_V7_12_RULES_PLUS_C2"
SYSTEM_C = "SLTD_V7_12_RULES_PLUS_C2_PLUS_SEVERE_RISK"
BUY_HOLD = "BUY_AND_HOLD"
SMA200 = "SMA200"

PRIMARY_COST = {"buy_bps": 5.0, "sell_bps": 10.0}
SENS_COST = {"buy_bps": 10.0, "sell_bps": 15.0}


def finite(x) -> bool:
    return x is not None and math.isfinite(float(x))


def candles_from_frame(frame: pd.DataFrame) -> list[dict]:
    return [
        {
            "date": pd.Timestamp(r.Date).strftime("%Y-%m-%d"),
            "open": float(r.Open),
            "high": float(r.High),
            "low": float(r.Low),
            "close": float(r.Close),
            "volume": 0.0 if pd.isna(r.Volume) else float(r.Volume),
        }
        for r in frame.itertuples(index=False)
    ]


def load_symbol(item: dict, risk_weights: dict[str, float]) -> tuple[pd.DataFrame, list[dict], dict[str, float]]:
    frame = pd.read_csv(DATA_DIR / f'{item["code"]}.csv.gz', parse_dates=["Date"])
    frame["Date"] = pd.to_datetime(frame["Date"]).dt.tz_localize(None)
    frame = frame.sort_values("Date").drop_duplicates("Date").reset_index(drop=True)
    bars = candles_from_frame(frame)
    ledger = sltd.build_ledger(bars, item["code"])

    ledger_df = pd.DataFrame(ledger)
    ledger_df["date"] = pd.to_datetime(ledger_df["date"]).dt.tz_localize(None)
    rows = p11.build_symbol_rows(item["code"], frame, ledger_df)
    levels = {}
    for r in rows.itertuples(index=False):
        lvl, _ = mom.level_for_row(r, risk_weights)
        levels[pd.Timestamp(r.date).strftime("%Y-%m-%d")] = float(lvl)
    return frame, ledger, levels


def one_price_locked(bar: dict, prev_close: float, side: str) -> bool:
    op = float(bar["open"])
    hi = float(bar["high"])
    lo = float(bar["low"])
    tol = max(0.001, abs(float(bar["close"])) * 1e-8)
    one_price = abs(hi - lo) <= tol
    if not one_price or prev_close <= 0:
        return False
    gap = op / prev_close - 1.0
    if side == "BUY":
        return gap >= 0.095
    return gap <= -0.095


@dataclass
class Pending:
    kind: str  # BUY, SELL, HARD_C2, HARD_SEVERE


def max_drawdown(curve: np.ndarray) -> float:
    arr = np.concatenate([[1.0], np.asarray(curve, dtype=float)])
    peak = np.maximum.accumulate(arr)
    return float(np.min(arr / peak - 1.0))


def calc_metrics(curve: list[float], dates: list[pd.Timestamp], exposure: list[float], counts: dict) -> dict:
    arr = np.asarray(curve, dtype=float)
    if len(arr) < 2:
        raise RuntimeError("insufficient formal curve")
    daily = np.empty(len(arr), dtype=float)
    daily[0] = arr[0] - 1.0
    daily[1:] = arr[1:] / arr[:-1] - 1.0
    total = float(arr[-1] - 1.0)
    days = max(1, (dates[-1] - dates[0]).days)
    cagr = float(arr[-1] ** (365.25 / days) - 1.0) if arr[-1] > 0 else -1.0
    mdd = max_drawdown(arr)
    calmar = float(cagr / abs(mdd)) if mdd < -1e-12 else (999.0 if cagr > 0 else 0.0)
    return {
        "start": dates[0].strftime("%Y-%m-%d"),
        "end": dates[-1].strftime("%Y-%m-%d"),
        "observations": int(len(arr)),
        "total_return": total,
        "cagr": cagr,
        "max_drawdown": mdd,
        "calmar": calmar,
        "mean_exposure": float(np.mean(exposure)) if exposure else 0.0,
        "daily_p1": float(np.quantile(daily, 0.01)),
        "daily_p5": float(np.quantile(daily, 0.05)),
        **{k: int(v) for k, v in counts.items()},
    }


def simulate_sltd(
    frame: pd.DataFrame,
    ledger: list[dict],
    risk_levels: dict[str, float],
    threshold: float,
    system: str,
    costs: dict,
) -> dict:
    bars = candles_from_frame(frame)
    if len(bars) != len(ledger):
        raise RuntimeError("bar/ledger mismatch")

    formal_idx = next(i for i, b in enumerate(bars) if pd.Timestamp(b["date"]) >= FORMAL_START)
    end_idx = max(i for i, b in enumerate(bars) if pd.Timestamp(b["date"]) <= FORMAL_END)

    cash = 1.0
    shares = 0.0
    risk_armed = False
    pending: Pending | None = None

    curve, dates, exposure = [], [], []
    counts = {
        "buy_count": 0,
        "ordinary_sell_count": 0,
        "c2_full_exit_count": 0,
        "severe_full_exit_count": 0,
        "blocked_buy_attempts": 0,
        "blocked_sell_attempts": 0,
    }

    buy_rate = costs["buy_bps"] / 10000.0
    sell_rate = costs["sell_bps"] / 10000.0

    for j in range(formal_idx, end_idx + 1):
        bar = bars[j]
        prev = bars[j - 1] if j > 0 else None
        signal = ledger[j - 1] if j > 0 else None
        signal_date = signal["date"] if signal else None

        # Hard-risk eligibility is evaluated from the latest completed signal bar.
        c2_now = bool(
            system in {SYSTEM_B, SYSTEM_C}
            and shares > 1e-14
            and risk_armed
            and sltd.c2_condition(signal)
        )
        severe_now = bool(
            system == SYSTEM_C
            and shares > 1e-14
            and risk_armed
            and signal_date is not None
            and float(risk_levels.get(signal_date, 0.0)) <= threshold
        )

        # Upgrade any pending ordinary action to hard exit when eligible.
        if c2_now:
            pending = Pending("HARD_C2")
        elif severe_now and (pending is None or pending.kind not in {"HARD_C2"}):
            pending = Pending("HARD_SEVERE")

        # If nothing is pending, convert the previous close signal into an intended order.
        if pending is None:
            action = sltd.resolve_action(signal)
            if action == "BUY":
                pending = Pending("BUY")
            elif action == "SELL" and shares > 1e-14:
                pending = Pending("SELL")

        op = float(bar["open"])
        cl = float(bar["close"])
        pre_equity = cash + shares * op
        position_value = shares * op
        current_fraction = position_value / pre_equity if pre_equity > 0 else 0.0

        if pending is not None:
            is_buy = pending.kind == "BUY"
            blocked = one_price_locked(bar, float(prev["close"]), "BUY" if is_buy else "SELL") if prev else False
            if blocked:
                if is_buy:
                    counts["blocked_buy_attempts"] += 1
                else:
                    counts["blocked_sell_attempts"] += 1
            else:
                order_value = 0.0
                if pending.kind == "BUY":
                    desired = 0.25 if shares <= 1e-14 else min(1.0, current_fraction + 0.25)
                    desired = max(current_fraction, desired)
                    order_value = desired * pre_equity - position_value
                    if order_value > 1e-14:
                        max_buy = max(0.0, cash / (1.0 + buy_rate))
                        order_value = min(order_value, max_buy)
                        if order_value > 1e-14:
                            cost = order_value * buy_rate
                            shares += order_value / op
                            cash -= order_value + cost
                            counts["buy_count"] += 1
                            risk_armed = False
                elif pending.kind == "SELL":
                    order_value = -position_value * 0.25
                    if order_value < -1e-14:
                        cost = abs(order_value) * sell_rate
                        shares += order_value / op
                        cash -= order_value + cost
                        if shares <= 1e-12:
                            shares = 0.0
                        counts["ordinary_sell_count"] += 1
                        if system in {SYSTEM_B, SYSTEM_C}:
                            risk_armed = True
                elif pending.kind in {"HARD_C2", "HARD_SEVERE"}:
                    order_value = -position_value
                    if order_value < -1e-14:
                        cost = abs(order_value) * sell_rate
                        shares += order_value / op
                        cash -= order_value + cost
                        shares = 0.0
                        if pending.kind == "HARD_C2":
                            counts["c2_full_exit_count"] += 1
                        else:
                            counts["severe_full_exit_count"] += 1
                        risk_armed = False
                pending = None

        close_equity = cash + shares * cl
        close_fraction = shares * cl / close_equity if close_equity > 0 else 0.0
        curve.append(float(close_equity))
        dates.append(pd.Timestamp(bar["date"]))
        exposure.append(float(max(0.0, min(1.0, close_fraction))))

    m = calc_metrics(curve, dates, exposure, counts)
    return {"metrics": m, "curve_dates": [d.strftime("%Y-%m-%d") for d in dates], "curve": curve}


def simulate_buy_hold(frame: pd.DataFrame, costs: dict) -> dict:
    bars = candles_from_frame(frame)
    formal_idx = next(i for i, b in enumerate(bars) if pd.Timestamp(b["date"]) >= FORMAL_START)
    end_idx = max(i for i, b in enumerate(bars) if pd.Timestamp(b["date"]) <= FORMAL_END)
    cash, shares = 1.0, 0.0
    pending = True
    curve, dates, exposure = [], [], []
    counts = {
        "buy_count": 0, "ordinary_sell_count": 0, "c2_full_exit_count": 0,
        "severe_full_exit_count": 0, "blocked_buy_attempts": 0, "blocked_sell_attempts": 0,
    }
    rate = costs["buy_bps"] / 10000.0
    for j in range(formal_idx, end_idx + 1):
        b = bars[j]
        prev = bars[j - 1] if j > 0 else None
        if pending:
            blocked = one_price_locked(b, float(prev["close"]), "BUY") if prev else False
            if blocked:
                counts["blocked_buy_attempts"] += 1
            else:
                op = float(b["open"])
                invest = cash / (1.0 + rate)
                cost = invest * rate
                shares = invest / op
                cash -= invest + cost
                pending = False
                counts["buy_count"] = 1
        eq = cash + shares * float(b["close"])
        curve.append(float(eq)); dates.append(pd.Timestamp(b["date"]))
        exposure.append(float(shares * float(b["close"]) / eq) if eq > 0 else 0.0)
    return {"metrics": calc_metrics(curve, dates, exposure, counts),
            "curve_dates":[d.strftime("%Y-%m-%d") for d in dates], "curve":curve}


def simulate_sma200(frame: pd.DataFrame, costs: dict) -> dict:
    f = frame.copy()
    f["SMA200"] = f["Close"].rolling(200, min_periods=200).mean()
    bars = candles_from_frame(f)
    sma = {pd.Timestamp(r.Date).strftime("%Y-%m-%d"): (None if pd.isna(r.SMA200) else float(r.SMA200))
           for r in f.itertuples(index=False)}
    formal_idx = next(i for i,b in enumerate(bars) if pd.Timestamp(b["date"]) >= FORMAL_START)
    end_idx = max(i for i,b in enumerate(bars) if pd.Timestamp(b["date"]) <= FORMAL_END)

    cash, shares = 1.0, 0.0
    pending: str | None = None  # TARGET_LONG / TARGET_CASH
    curve, dates, exposure = [], [], []
    counts = {
        "buy_count": 0, "ordinary_sell_count": 0, "c2_full_exit_count": 0,
        "severe_full_exit_count": 0, "blocked_buy_attempts": 0, "blocked_sell_attempts": 0,
    }
    br=costs["buy_bps"]/10000.0; sr=costs["sell_bps"]/10000.0

    for j in range(formal_idx, end_idx+1):
        b=bars[j]; prev=bars[j-1] if j>0 else None
        if pending is None and prev is not None:
            sm=sma.get(prev["date"])
            if sm is not None:
                want_long=float(prev["close"])>sm
                if want_long and shares<=1e-14:
                    pending="TARGET_LONG"
                elif (not want_long) and shares>1e-14:
                    pending="TARGET_CASH"
        if pending is not None:
            side="BUY" if pending=="TARGET_LONG" else "SELL"
            blocked=one_price_locked(b,float(prev["close"]),side) if prev else False
            if blocked:
                counts["blocked_buy_attempts" if side=="BUY" else "blocked_sell_attempts"]+=1
            else:
                op=float(b["open"])
                if pending=="TARGET_LONG":
                    invest=cash/(1.0+br); cost=invest*br; shares+=invest/op; cash-=invest+cost
                    counts["buy_count"]+=1
                else:
                    value=shares*op; cost=value*sr; cash+=value-cost; shares=0.0
                    counts["ordinary_sell_count"]+=1
                pending=None
        eq=cash+shares*float(b["close"])
        curve.append(float(eq)); dates.append(pd.Timestamp(b["date"]))
        exposure.append(float(shares*float(b["close"])/eq) if eq>0 else 0.0)
    return {"metrics":calc_metrics(curve,dates,exposure,counts),
            "curve_dates":[d.strftime("%Y-%m-%d") for d in dates], "curve":curve}


def aggregate_portfolio(results_by_symbol: dict[str, dict]) -> dict:
    series=[]
    for symbol,res in results_by_symbol.items():
        s=pd.Series(res["curve"], index=pd.to_datetime(res["curve_dates"]), name=symbol, dtype=float)
        series.append(s)
    df=pd.concat(series,axis=1).sort_index().ffill().fillna(1.0)
    curve=df.mean(axis=1).to_numpy(float)
    dates=[pd.Timestamp(x) for x in df.index]
    # exposure is the arithmetic mean of per-symbol mean exposure, frozen by Amendment E.
    mean_exp=float(np.mean([r["metrics"]["mean_exposure"] for r in results_by_symbol.values()]))
    counts={}
    for k in ["buy_count","ordinary_sell_count","c2_full_exit_count","severe_full_exit_count",
              "blocked_buy_attempts","blocked_sell_attempts"]:
        counts[k]=sum(int(r["metrics"].get(k,0)) for r in results_by_symbol.values())
    m=calc_metrics(curve,dates,[mean_exp]*len(curve),counts)
    m["mean_exposure"]=mean_exp
    return m


def pairwise(candidate: dict[str, dict], baseline: dict[str, dict],
             cand_agg: dict, base_agg: dict) -> dict:
    syms=sorted(candidate)
    ret_delta=[candidate[s]["metrics"]["total_return"]-baseline[s]["metrics"]["total_return"] for s in syms]
    better_dd=[candidate[s]["metrics"]["max_drawdown"]>baseline[s]["metrics"]["max_drawdown"] for s in syms]
    better_cal=[candidate[s]["metrics"]["calmar"]>baseline[s]["metrics"]["calmar"] for s in syms]
    return {
        "aggregate_total_return_delta": cand_agg["total_return"]-base_agg["total_return"],
        "aggregate_cagr_delta": cand_agg["cagr"]-base_agg["cagr"],
        "aggregate_maxdd_delta": cand_agg["max_drawdown"]-base_agg["max_drawdown"],
        "aggregate_calmar_delta": cand_agg["calmar"]-base_agg["calmar"],
        "aggregate_mean_exposure_delta": cand_agg["mean_exposure"]-base_agg["mean_exposure"],
        "median_per_stock_return_delta": float(np.median(ret_delta)),
        "symbols_better_maxdd": int(sum(better_dd)),
        "symbols_better_calmar": int(sum(better_cal)),
        "symbol_count": len(syms),
    }


def run_cost(costs: dict, dev: list[dict], weights: dict[str,float], threshold: float) -> dict:
    per={SYSTEM_A:{},SYSTEM_B:{},SYSTEM_C:{},BUY_HOLD:{},SMA200:{}}
    for item in dev:
        frame,ledger,levels=load_symbol(item,weights)
        code=item["code"]
        per[SYSTEM_A][code]=simulate_sltd(frame,ledger,levels,threshold,SYSTEM_A,costs)
        per[SYSTEM_B][code]=simulate_sltd(frame,ledger,levels,threshold,SYSTEM_B,costs)
        per[SYSTEM_C][code]=simulate_sltd(frame,ledger,levels,threshold,SYSTEM_C,costs)
        per[BUY_HOLD][code]=simulate_buy_hold(frame,costs)
        per[SMA200][code]=simulate_sma200(frame,costs)

    agg={name:aggregate_portfolio(per[name]) for name in per}
    attr={
        "C2_contribution_B_minus_A":pairwise(per[SYSTEM_B],per[SYSTEM_A],agg[SYSTEM_B],agg[SYSTEM_A]),
        "SevereRisk_increment_C_minus_B":pairwise(per[SYSTEM_C],per[SYSTEM_B],agg[SYSTEM_C],agg[SYSTEM_B]),
        "Combined_C_minus_A":pairwise(per[SYSTEM_C],per[SYSTEM_A],agg[SYSTEM_C],agg[SYSTEM_A]),
    }
    return {"aggregate":agg,"attribution":attr,"per_symbol":{n:{s:r["metrics"] for s,r in d.items()} for n,d in per.items()}}


def main():
    stage_a=json.loads(STAGE_A_PATH.read_text(encoding="utf-8"))
    if stage_a["decision"]!="PROMOTED_TO_INTEGRATED_HOLDOUT":
        raise RuntimeError("Stage A did not authorize Stage B")
    threshold=float(stage_a["summary"]["severe_threshold"])
    weights={x["id"]:float(x["discovery"]["utility"]) for x in stage_a["stable_negative_states_ranked"]}

    dev=[x for x in UNIVERSE["symbols"] if x["role"]=="DEVELOPMENT"]
    fresh=[x for x in UNIVERSE["symbols"] if x["role"]=="FRESH_OOS"]
    if len(dev)!=35 or len(fresh)!=15:
        raise RuntimeError("frozen split mismatch")

    primary=run_cost(PRIMARY_COST,dev,weights,threshold)
    sensitivity=run_cost(SENS_COST,dev,weights,threshold)

    B=primary["aggregate"][SYSTEM_B]
    C=primary["aggregate"][SYSTEM_C]
    pair=primary["attribution"]["SevereRisk_increment_C_minus_B"]
    Bsens=sensitivity["aggregate"][SYSTEM_B]
    Csens=sensitivity["aggregate"][SYSTEM_C]
    perB=primary["per_symbol"][SYSTEM_B]
    perC=primary["per_symbol"][SYSTEM_C]

    ret_retention=(C["total_return"]/B["total_return"]) if B["total_return"]>0 else float("-inf")
    exp_retention=(C["mean_exposure"]/B["mean_exposure"]) if B["mean_exposure"]>0 else 0.0
    severe_symbols=sum(1 for s in perC if perC[s]["severe_full_exit_count"]>0)
    worst_B=min(x["max_drawdown"] for x in perB.values())
    worst_C=min(x["max_drawdown"] for x in perC.values())

    gates={
        "aggregate_maxdd_improves_ge_2pp": C["max_drawdown"]-B["max_drawdown"]>=0.020,
        "aggregate_calmar_improves": C["calmar"]>B["calmar"],
        "aggregate_return_retention_ge_95pct": ret_retention>=0.95,
        "median_per_stock_return_delta_ge_minus_1pp": pair["median_per_stock_return_delta"]>=-0.010,
        "better_maxdd_ge_60pct_symbols": pair["symbols_better_maxdd"]>=21,
        "better_calmar_ge_50pct_symbols": pair["symbols_better_calmar"]>=18,
        "worst_per_stock_maxdd_improves_or_equal": worst_C>=worst_B,
        "sensitivity_calmar_gt_baseline": Csens["calmar"]>Bsens["calmar"],
        "severe_full_exits_on_ge_10_symbols": severe_symbols>=10,
        "mean_exposure_retention_ge_90pct": exp_retention>=0.90,
    }
    decision="PROMOTED_TO_FRESH15" if all(gates.values()) else "REJECTED_NOT_ADMITTED"

    out={
        "meta":{
            "study":"SLTD_ASHARE50_INTEGRATED_RISK_V1_STAGE_B",
            "market":"China A-share main board",
            "window":["2025-01-02","2026-09-30"],
            "development_symbol_count":35,
            "fresh_performance_read":False,
            "fresh_oos_consumed":False,
            "systems":[SYSTEM_A,SYSTEM_B,SYSTEM_C,BUY_HOLD,SMA200],
            "severe_threshold":threshold,
            "stable_negative_state_count":len(weights),
            "generated_at_utc":datetime.now(timezone.utc).isoformat(),
        },
        "primary_costs":PRIMARY_COST,
        "sensitivity_costs":SENS_COST,
        "primary":primary,
        "sensitivity":{
            "aggregate":sensitivity["aggregate"],
            "attribution":sensitivity["attribution"],
        },
        "gate_diagnostics":{
            "return_retention":ret_retention,
            "exposure_retention":exp_retention,
            "severe_exit_symbol_count":severe_symbols,
            "worst_maxdd_baseline":worst_B,
            "worst_maxdd_candidate":worst_C,
        },
        "gates":gates,
        "decision":decision,
    }
    OUT_JSON.write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding="utf-8")

    def pct(x): return f"{100*float(x):.2f}%"
    lines=[
        "# SLTD A-share 50 Integrated Risk v1 — Stage B Holdout Result","",
        f"Status: **{decision}**","",
        "- DEVELOPMENT symbols: **35**",
        "- Holdout: **2025-01-02..2026-09-30**",
        "- Fresh15 performance read: **NO**",
        f"- Severe threshold: **{threshold:.5f}**",
        f"- A-share stable negative states: **{len(weights)}**","",
        "## Primary costs","",
        "| System | Total Return | CAGR | MaxDD | Calmar | Mean Exposure | BUY | Ordinary SELL | C2 exits | Severe exits |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name in [SYSTEM_A,SYSTEM_B,SYSTEM_C,BUY_HOLD,SMA200]:
        m=primary["aggregate"][name]
        lines.append(
            f"| {name} | {pct(m['total_return'])} | {pct(m['cagr'])} | {pct(m['max_drawdown'])} | "
            f"{m['calmar']:.3f} | {pct(m['mean_exposure'])} | {m['buy_count']} | "
            f"{m['ordinary_sell_count']} | {m['c2_full_exit_count']} | {m['severe_full_exit_count']} |"
        )
    lines += ["","## Attribution","",
              "| Comparison | Return Δ | CAGR Δ | MaxDD Δ | Calmar Δ | Exposure Δ | Median stock return Δ | Better DD | Better Calmar |",
              "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for label,key in [
        ("C2: B-A","C2_contribution_B_minus_A"),
        ("Severe Risk: C-B","SevereRisk_increment_C_minus_B"),
        ("Combined: C-A","Combined_C_minus_A"),
    ]:
        x=primary["attribution"][key]
        lines.append(
            f"| {label} | {pct(x['aggregate_total_return_delta'])} | {pct(x['aggregate_cagr_delta'])} | "
            f"{pct(x['aggregate_maxdd_delta'])} | {x['aggregate_calmar_delta']:.3f} | "
            f"{pct(x['aggregate_mean_exposure_delta'])} | {pct(x['median_per_stock_return_delta'])} | "
            f"{x['symbols_better_maxdd']}/35 | {x['symbols_better_calmar']}/35 |"
        )
    lines += ["","## Gate diagnostics","",
              f"- Candidate/Baseline return retention: **{100*ret_retention:.2f}%**",
              f"- Candidate/Baseline exposure retention: **{100*exp_retention:.2f}%**",
              f"- Symbols with Severe Risk full exits: **{severe_symbols}/35**",
              f"- Worst baseline per-stock MaxDD: **{pct(worst_B)}**",
              f"- Worst candidate per-stock MaxDD: **{pct(worst_C)}**","",
              "## Gates",""]
    for k,v in gates.items():
        lines.append(f"- {k}: **{'PASS' if v else 'FAIL'}**")
    lines += ["",f"`SLTD_ASHARE50_INTEGRATED_RISK_V1_STAGE_B = {decision}`",""]
    OUT_MD.write_text("\n".join(lines),encoding="utf-8")

    print(json.dumps({
        "decision":decision,
        "aggregate_primary":primary["aggregate"],
        "attribution_primary":primary["attribution"],
        "gate_diagnostics":out["gate_diagnostics"],
        "gates":gates,
    },indent=2,ensure_ascii=False))


if __name__=="__main__":
    main()
