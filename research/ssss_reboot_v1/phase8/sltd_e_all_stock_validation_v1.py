#!/usr/bin/env python3
"""SLTD E v1 all archived stock daily validation (79 + fresh OOS10 = 89).

Optimization rule: reuse the frozen FIRST_OBSERVED daily ledgers already archived
for all 89 stocks. Only the E-specific 5d higher-timeframe ledgers are computed
during this run. This changes runtime only, not the frozen test semantics.
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
PHASE8 = ROOT / "research" / "ssss_reboot_v1" / "phase8"
PHASE7 = ROOT / "research" / "ssss_reboot_v1" / "phase7"
INTEGRATION = ROOT / "integrations" / "sltd_v7_siftalpha_v1"
sys.path.insert(0, str(INTEGRATION))
sys.path.insert(0, str(PHASE8))
sys.path.insert(0, str(PHASE7))

import e_strategy  # noqa: E402
import strategy as v7_math  # noqa: E402
import sltd_v6_position_policy_batch_v1 as core  # noqa: E402
import sltd_v7_combination_ablation_v1 as combo  # noqa: E402

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

def pct(x): return f"{100.0*float(x):.2f}%"

def read_frame(path: Path) -> pd.DataFrame:
    with gzip.open(path,"rt",encoding="utf-8") as f:
        df=pd.read_csv(f,parse_dates=["Date"])
    df=df[["Date","Open","High","Low","Close","Volume"]].copy()
    df["Date"]=pd.to_datetime(df["Date"]).dt.tz_localize(None)
    for c in ["Open","High","Low","Close","Volume"]:
        df[c]=pd.to_numeric(df[c],errors="coerce")
    return df.dropna(subset=["Date","Open","High","Low","Close"]).sort_values("Date").drop_duplicates("Date",keep="last").reset_index(drop=True)

def read_ledger(path: Path) -> list[dict]:
    with gzip.open(path,"rt",encoding="utf-8") as f:
        df=pd.read_csv(f)
    rows=[]
    for rec in df.to_dict("records"):
        for cls in ("BUY","HOLD","WAIT","SELL"):
            val=rec.get(cls)
            rec[cls]=[] if pd.isna(val) or str(val).strip()=="" else [x for x in str(val).split("|") if x]
        rows.append(rec)
    return rows

def load_universe():
    frames,ledgers,groups={}, {}, {}
    for batch,symbols in core.BATCHES.items():
        for s in symbols:
            dp=PHASE7/"data_snapshot"/f"batch_{batch:02d}_stocks"/f"{s}.csv.gz"
            lp=PHASE7/"signal_ledgers"/f"BATCH_{batch:02d}_{s}_FIRST_OBSERVED.csv.gz"
            if not dp.exists() or not lp.exists(): raise RuntimeError(f"missing frozen files for {s}")
            frames[s]=read_frame(dp); ledgers[s]=read_ledger(lp); groups[s]=f"B{batch}"
    for s in OOS10:
        dp=PHASE8/"oos10_data_snapshot"/f"{s}.csv.gz"
        lp=PHASE8/"oos10_signal_ledgers"/f"{s}_FIRST_OBSERVED.csv.gz"
        if not dp.exists() or not lp.exists(): raise RuntimeError(f"missing frozen OOS files for {s}")
        if s in frames: raise RuntimeError(f"duplicate {s}")
        frames[s]=read_frame(dp); ledgers[s]=read_ledger(lp); groups[s]="OOS10"
    if len(frames)!=89 or len(ledgers)!=89: raise RuntimeError("universe must be exactly 89")
    for s in frames:
        if len(frames[s])!=len(ledgers[s]):
            raise RuntimeError(f"{s}: frame/ledger length mismatch {len(frames[s])}/{len(ledgers[s])}")
        fd=frames[s]["Date"].dt.strftime("%Y-%m-%d").tolist()
        ld=[str(x["date"])[:10] for x in ledgers[s]]
        if fd!=ld: raise RuntimeError(f"{s}: frame/ledger date mismatch")
    return frames,ledgers,groups

def to_candles(frame):
    out=[]
    for r in frame.itertuples(index=False):
        d=pd.Timestamp(r.Date)
        out.append({"date":d.strftime("%Y-%m-%d"),"open_time":int(d.tz_localize("UTC").timestamp()),
                    "open":float(r.Open),"high":float(r.High),"low":float(r.Low),"close":float(r.Close),
                    "volume":float(r.Volume) if pd.notna(r.Volume) else 0.0})
    return out

def maxdd(curve):
    a=np.asarray(curve,dtype=float); peak=np.maximum.accumulate(a)
    return float(np.min(a/peak-1.0)) if len(a) else 0.0

def metrics(dates,curve):
    a=np.asarray(curve,dtype=float)
    days=max(1,(pd.Timestamp(dates[-1])-pd.Timestamp(dates[0])).days)
    tr=float(a[-1]-1.0); cagr=float(a[-1]**(365.25/days)-1.0) if a[-1]>0 else -1.0
    mdd=maxdd(a); calmar=cagr/abs(mdd) if mdd<-1e-12 else (999.0 if cagr>0 else 0.0)
    return {"start":dates[0],"end":dates[-1],"total_return":tr,"cagr":cagr,"max_drawdown":mdd,"calmar":float(calmar)}

def align(per):
    common=set.intersection(*(set(x["dates"]) for x in per.values())); dates=sorted(common)
    if len(dates)<2: raise RuntimeError("no common dates")
    curves=[]
    for s,r in per.items():
        pos={d:i for i,d in enumerate(r["dates"])}
        curves.append(np.asarray([r["curve"][pos[d]] for d in dates],dtype=float))
    return dates,np.mean(np.vstack(curves),axis=0)

def portfolio(per):
    dates,curve=align(per); out=metrics(dates,curve)
    out.update({
        "turnover_mean":float(np.mean([x.get("turnover",0.0) for x in per.values()])),
        "position_changes_sum":int(sum(x.get("position_changes",0) for x in per.values())),
        "time_in_market_mean":float(np.mean([x.get("time_in_market",0.0) for x in per.values()])),
        "profitable_symbols":int(sum(x["total_return"]>0 for x in per.values())),
        "positive_calmar_symbols":int(sum(x["calmar"]>0 for x in per.values())),
    })
    return out

def sliced(per,start,end):
    dates,curve=align(per)
    idx=np.flatnonzero(np.asarray([start<=d<=end for d in dates],dtype=bool))
    if len(idx)<2: return None
    d=[dates[i] for i in idx]; c=curve[idx]/curve[idx[0]]
    return metrics(d,c)

def buy_hold(frame,bps):
    f=frame[(frame["Date"]>=FORMAL_START)&(frame["Date"]<=FORMAL_END)].copy()
    dates=f["Date"].dt.strftime("%Y-%m-%d").tolist()
    o=f["Open"].astype(float).to_numpy(); c=f["Close"].astype(float).to_numpy()
    cost=bps/10000.0; shares=1.0/(o[0]*(1.0+cost)); cash=1.0-shares*o[0]*(1.0+cost)
    curve=cash+shares*c; out=metrics(dates,curve)
    out.update({"dates":dates,"curve":curve,"turnover":1.0/(1.0+cost),"position_changes":1,"time_in_market":1.0})
    return out

def prepare_e(frame,primary,symbol):
    candles=to_candles(frame)
    higher_tf,hbars=e_strategy.build_higher_bars(candles,"1d",{})
    if higher_tf!="5d": raise RuntimeError(f"{symbol}: expected 5d, got {higher_tf}")
    hledger=v7_math.build_ledger(hbars,f"{symbol}:5d")
    aligned=[None]*len(candles); h=-1
    for i in range(len(candles)):
        while h+1<len(hbars) and int(hbars[h+1]["_source_end_index"])<=i: h+=1
        if h>=0: aligned[i]=(h,hledger[h])
    formal=[i for i,b in enumerate(candles) if FORMAL_START<=pd.Timestamp(b["date"])<=FORMAL_END]
    if len(formal)<2 or aligned[formal[0]] is None: raise RuntimeError(f"{symbol}: insufficient E warmup")
    return {"candles":candles,"primary":primary,"higher":aligned,"formal":formal}

def simulate_e(prep,bps):
    candles,primary,halign,formal=prep["candles"],prep["primary"],prep["higher"],prep["formal"]
    cash,shares,target=1.0,0.0,0.0
    b1=b2=b3=False; sell_stage=0; pending=None
    turnover=0.0; changes=0; invested=0; rule_exec=Counter(); action_exec=Counter()
    dates=[]; curve=[]; targets=[]; cost_rate=bps/10000.0
    for i in formal:
        bar=candles[i]; op=float(bar["open"]); cl=float(bar["close"]); pre=cash+shares*op
        if pending is not None:
            kind=pending["kind"]
            if kind=="BUY":
                target=min(0.75,target+float(pending["delta"]))
                if "E_BUY_1_PRIMARY_CLOSE_BREAK_BELOW_ZD1" in pending["rule_ids"]: b1=True
                if "E_BUY_2_HIGHER_CLOSE_BELOW_ZD1" in pending["rule_ids"]: b2=True
                if "E_BUY_3_TOUCH_GZB_BAND" in pending["rule_ids"]: b3=True
            elif kind=="SELL50": target=max(0.0,target-0.50); sell_stage=max(sell_stage,1)
            elif kind=="SELL25": target=max(0.0,target-0.25); sell_stage=max(sell_stage,2)
            elif kind=="EXIT": target=0.0
            pos=shares*op; order=target*pre-pos
            if target<=1e-12: order=-pos
            if order>1e-14: order=min(order,max(0.0,cash/(1.0+cost_rate)))
            elif order<-1e-14: order=max(order,-pos)
            if abs(order)>1e-14:
                fee=abs(order)*cost_rate; shares+=order/op; cash-=order+fee
                turnover+=abs(order)/pre; changes+=1
                if shares<=1e-12: shares=0.0
            action_exec[kind]+=1; rule_exec.update(pending["rule_ids"])
            if target<=1e-12:
                target=0.0; b1=b2=b3=False; sell_stage=0
            pending=None
        dates.append(bar["date"]); curve.append(cash+shares*cl); targets.append(target)
        if shares>1e-12: invested+=1

        row=primary[i]; pair=halign[i]; hrow=pair[1] if pair else None; signal=None
        if target>1e-12:
            inner_up=e_strategy._break_above_zk1(i,candles,primary)
            active=sell_stage>0 or inner_up
            band=e_strategy._band_touch(bar,row); bs=row.get("BS")
            bs_hit=bs is not None and not pd.isna(bs) and float(bar["high"])>=float(bs)
            if active and band:
                signal={"kind":"EXIT","rule_ids":["E_SELL_3_TOUCH_GZB_BAND_FULL_EXIT"]}
            elif sell_stage>0 and row.get("ZK1") is not None and not pd.isna(row.get("ZK1")) and float(bar["close"])<float(row["ZK1"]):
                signal={"kind":"EXIT","rule_ids":["E_SELL_4_CLOSE_BACK_BELOW_ZK1_FULL_EXIT"]}
            elif active and bs_hit:
                signal={"kind":"SELL25","rule_ids":["E_SELL_2_TOUCH_BS_MINUS_25PP"]}
            elif sell_stage==0 and inner_up:
                signal={"kind":"SELL50","rule_ids":["E_SELL_1_PRIMARY_CLOSE_BREAK_ABOVE_ZK1_MINUS_50PP"]}
        if signal is None and sell_stage==0:
            state=str(row.get("color") or "")
            inner_down=(not b1 and state in {"BLUE","GRAY"} and e_strategy._break_below_zd1(i,candles,primary))
            if inner_down:
                ids=["E_BUY_1_PRIMARY_CLOSE_BREAK_BELOW_ZD1"]; delta=0.25
                hzd=hrow.get("ZD1") if hrow else None
                if not b2 and hrow is not None and hzd is not None and not pd.isna(hzd) and float(hrow["close"])<float(hzd):
                    ids.append("E_BUY_2_HIGHER_CLOSE_BELOW_ZD1"); delta+=0.25
                signal={"kind":"BUY","delta":delta,"rule_ids":ids}
            elif b1 and not b3 and e_strategy._band_touch(bar,row):
                signal={"kind":"BUY","delta":0.25,"rule_ids":["E_BUY_3_TOUCH_GZB_BAND"]}
        pending=signal
    a=np.asarray(curve,dtype=float); out=metrics(dates,a)
    out.update({"dates":dates,"curve":a,"turnover":float(turnover),"position_changes":int(changes),
                "time_in_market":float(invested/len(dates)),"rule_execution_counts":dict(rule_exec),
                "action_execution_counts":dict(action_exec),"ending_target_position":float(target),
                "mean_target_position":float(np.mean(targets))})
    return out

def v7_result(prep,bps):
    r=combo.simulate(prep,"DROP_B3_S1_S3",bps)
    return dict(r)|{"dates":list(prep["dates"])}

def compact(r):
    keys=("total_return","cagr","max_drawdown","calmar","turnover","position_changes","time_in_market")
    out={k:r[k] for k in keys}
    for k in ("hard_exit_count","rule_execution_counts","action_execution_counts","ending_target_position","mean_target_position"):
        if k in r: out[k]=r[k]
    return out

def compare(a,b):
    sy=list(a)
    return {
        "better_return":sum(a[s]["total_return"]>b[s]["total_return"] for s in sy),
        "better_cagr":sum(a[s]["cagr"]>b[s]["cagr"] for s in sy),
        "better_maxdd":sum(a[s]["max_drawdown"]>b[s]["max_drawdown"] for s in sy),
        "better_calmar":sum(a[s]["calmar"]>b[s]["calmar"] for s in sy),
        "median_delta_return":float(statistics.median(a[s]["total_return"]-b[s]["total_return"] for s in sy)),
        "median_delta_cagr":float(statistics.median(a[s]["cagr"]-b[s]["cagr"] for s in sy)),
        "median_delta_maxdd":float(statistics.median(a[s]["max_drawdown"]-b[s]["max_drawdown"] for s in sy)),
        "median_delta_calmar":float(statistics.median(a[s]["calmar"]-b[s]["calmar"] for s in sy)),
    }

def subset(per,sy): return {s:per[s] for s in sy}

def main():
    frames,ledgers,groups=load_universe()
    prior79=[s for xs in core.BATCHES.values() for s in xs]; all89=prior79+OOS10
    prepared_e={}; prepared_v7={}
    for n,s in enumerate(all89,1):
        prepared_e[s]=prepare_e(frames[s],ledgers[s],s)
        prepared_v7[s]=combo.prepare_symbol(frames[s],ledgers[s])
        print("PREP_PASS",n,89,s,flush=True)

    systems={f:{n:{} for n in ("E","V7","BUY_HOLD")} for f in ("5bps","10bps")}
    for fname,bps in (("5bps",5.0),("10bps",10.0)):
        for n,s in enumerate(all89,1):
            systems[fname]["E"][s]=simulate_e(prepared_e[s],bps)
            systems[fname]["V7"][s]=v7_result(prepared_v7[s],bps)
            systems[fname]["BUY_HOLD"][s]=buy_hold(frames[s],bps)
            print("SIM_PASS",fname,n,89,s,flush=True)

    frozen=json.loads(ARCHIVED_V7.read_text(encoding="utf-8")); errors=[]
    for s in prior79:
        exp=frozen["per_symbol"][s]["5bps"]["CANDIDATE_B_DROP_B3_S1_S3"]["total_return"]
        act=systems["5bps"]["V7"][s]["total_return"]
        if not math.isclose(act,exp,rel_tol=1e-10,abs_tol=1e-10): errors.append((s,act,exp))
    if errors: raise RuntimeError(f"V7 parity failed: {errors[:5]}")
    print("V7_79_PARITY_PASS",flush=True)

    aggregates={}; comparisons={}; yearly={}; eras={}; counts={}
    for fname in ("5bps","10bps"):
        aggregates[fname]={}; yearly[fname]={}; eras[fname]={}
        for name in ("E","V7","BUY_HOLD"):
            per=systems[fname][name]
            aggregates[fname][name]={"all89":portfolio(per),"prior79":portfolio(subset(per,prior79)),"oos10":portfolio(subset(per,OOS10))}
            yearly[fname][name]={str(y):sliced(per,f"{y}-01-01",f"{y}-12-31") for y in YEARS}
            eras[fname][name]={e:sliced(per,a,b) for e,(a,b) in ERAS.items()}
        comparisons[fname]={
            "E_vs_V7_all89":compare(systems[fname]["E"],systems[fname]["V7"]),
            "E_vs_BUY_HOLD_all89":compare(systems[fname]["E"],systems[fname]["BUY_HOLD"]),
            "E_vs_V7_prior79":compare(subset(systems[fname]["E"],prior79),subset(systems[fname]["V7"],prior79)),
            "E_vs_V7_oos10":compare(subset(systems[fname]["E"],OOS10),subset(systems[fname]["V7"],OOS10)),
            "E_vs_BUY_HOLD_oos10":compare(subset(systems[fname]["E"],OOS10),subset(systems[fname]["BUY_HOLD"],OOS10)),
        }
        rc,ac=Counter(),Counter()
        for r in systems[fname]["E"].values(): rc.update(r["rule_execution_counts"]); ac.update(r["action_execution_counts"])
        counts[fname]={"rules":dict(rc),"actions":dict(ac)}

    per_symbol={s:{"group":groups[s],
                   "5bps":{n:compact(systems["5bps"][n][s]) for n in ("E","V7","BUY_HOLD")},
                   "10bps":{n:compact(systems["10bps"][n][s]) for n in ("E","V7","BUY_HOLD")}} for s in all89}
    out={"meta":{"study":"SLTD_E_ALL_STOCK_VALIDATION_V1","status":"COMPLETE","universe_count":89,
                 "prior79_count":79,"fresh_oos10_count":10,"symbols":all89,"formal_window":"2020-01-02..2026-09-30",
                 "selected_timeframe":"1d","higher_timeframe":"5d","execution":"SIGNAL_CLOSE_TO_NEXT_AVAILABLE_OPEN",
                 "frictions_bps":[5.0,10.0],"e_source_commit":"f990eb9d2d4567d8acdc617fb1b4b9dd01b45f1c",
                 "v7_source_commit":"5f9ea4d8fa434b54afdbf32a1cb21ef2f3cb4042","v7_79_parity":"PASS",
                 "primary_ledger_source":"FROZEN_FIRST_OBSERVED_ARCHIVE","generated_at_utc":datetime.now(timezone.utc).isoformat()},
         "aggregates":aggregates,"comparisons":comparisons,"yearly":yearly,"eras":eras,
         "e_execution_counts":counts,"per_symbol":per_symbol}
    OUT_JSON.write_text(json.dumps(out,indent=2),encoding="utf-8")

    cv=comparisons["5bps"]["E_vs_V7_all89"]; cb=comparisons["5bps"]["E_vs_BUY_HOLD_all89"]
    ov=comparisons["5bps"]["E_vs_V7_oos10"]; ob=comparisons["5bps"]["E_vs_BUY_HOLD_oos10"]
    lines=["# SLTD E All-Stock Validation v1","","Status: **COMPLETE**","",
           "Universe: **89 unique mainstream U.S. stocks** = prior 79 + fresh OOS10.","",
           "Formal window: **2020-01-02 through 2026-09-30**.","",
           "Selected timeframe: **1d**; E higher timeframe: **5d**.","",
           "Execution: signal close -> next available open. Primary friction 5 bps; stress 10 bps.","",
           "## Equal-weight portfolio — 5 bps","",
           "| Scope | System | Return | CAGR | MaxDD | Calmar | Time in market | Changes |",
           "|---|---|---:|---:|---:|---:|---:|---:|"]
    for scope in ("all89","prior79","oos10"):
        for name,label in (("E","E"),("V7","V7 12-rule"),("BUY_HOLD","Buy & Hold")):
            m=aggregates["5bps"][name][scope]
            lines.append(f"| {scope} | {label} | {pct(m['total_return'])} | {pct(m['cagr'])} | {pct(m['max_drawdown'])} | {m['calmar']:.3f} | {pct(m['time_in_market_mean'])} | {m['position_changes_sum']} |")
    lines += ["","## Breadth — E vs V7, 5 bps","",
              f"- all89 better Return: **{cv['better_return']}/89**",f"- all89 better MaxDD: **{cv['better_maxdd']}/89**",
              f"- all89 better Calmar: **{cv['better_calmar']}/89**",f"- all89 median ΔReturn: **{pct(cv['median_delta_return'])}**",
              f"- all89 median ΔMaxDD: **{pct(cv['median_delta_maxdd'])}**",f"- all89 median ΔCalmar: **{cv['median_delta_calmar']:+.3f}**",
              f"- OOS10 better Return / MaxDD / Calmar: **{ov['better_return']}/10 / {ov['better_maxdd']}/10 / {ov['better_calmar']}/10**",
              "","## Breadth — E vs Buy & Hold, 5 bps","",
              f"- all89 better Return: **{cb['better_return']}/89**",f"- all89 better MaxDD: **{cb['better_maxdd']}/89**",
              f"- all89 better Calmar: **{cb['better_calmar']}/89**",f"- all89 median ΔReturn: **{pct(cb['median_delta_return'])}**",
              f"- all89 median ΔMaxDD: **{pct(cb['median_delta_maxdd'])}**",f"- all89 median ΔCalmar: **{cb['median_delta_calmar']:+.3f}**",
              f"- OOS10 better Return / MaxDD / Calmar: **{ob['better_return']}/10 / {ob['better_maxdd']}/10 / {ob['better_calmar']}/10**",
              "","## E execution counts — 5 bps",""]
    for rule,count in sorted(counts["5bps"]["rules"].items()): lines.append(f"- {rule}: **{count}**")
    lines += ["","## Calendar-year equal-weight returns — 5 bps","","| Year | E | V7 | Buy & Hold |","|---|---:|---:|---:|"]
    for y in YEARS:
        e,v,b=yearly["5bps"]["E"][str(y)],yearly["5bps"]["V7"][str(y)],yearly["5bps"]["BUY_HOLD"][str(y)]
        lines.append(f"| {y} | {pct(e['total_return'])} | {pct(v['total_return'])} | {pct(b['total_return'])} |")
    lines += ["","## Era Calmar — 5 bps","","| Era | E | V7 | Buy & Hold |","|---|---:|---:|---:|"]
    for era in ERAS:
        e,v,b=eras["5bps"]["E"][era],eras["5bps"]["V7"][era],eras["5bps"]["BUY_HOLD"][era]
        lines.append(f"| {era} | {e['calmar']:.3f} | {v['calmar']:.3f} | {b['calmar']:.3f} |")
    lines += ["","## Interpretation boundary","","- Prior 79 are reused research data, not fresh OOS.",
              "- OOS10 is reported separately.","- No E rule is changed or promoted by this run.",
              "- Frozen V7 79-stock parity check: **PASS**.","","SLTD_E_ALL_STOCK_VALIDATION_V1 = COMPLETE",""]
    OUT_MD.write_text("\n".join(lines),encoding="utf-8")

if __name__=="__main__":
    main()
