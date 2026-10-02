#!/usr/bin/env python3
"""SLTD V7 Combination Ablation Study v1."""
from __future__ import annotations

import gzip, json, math, statistics, sys
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parent
PHASE7=ROOT.parent/"phase7"
sys.path.insert(0,str(PHASE7))
import sltd_v6_position_policy_batch_v1 as core  # noqa: E402

DATA_ROOT=PHASE7/"data_snapshot"
LEDGER_ROOT=PHASE7/"signal_ledgers"
FROZEN_C2_RESULT=PHASE7/"SLTD_V6_HARD_EXIT_STUDY_V3_79_STOCKS.json"
OUT_JSON=ROOT/"SLTD_V7_COMBINATION_ABLATION_RESULT_v1.json"
OUT_MD=ROOT/"SLTD_V7_COMBINATION_ABLATION_RESULT_v1.md"
FORMAL_START=pd.Timestamp("2020-01-02")
FORMAL_END=pd.Timestamp("2026-09-30")

B3="BUY_RECENT_BLUE_GRAY_LIGHT_SUPPORT"
S1="SELL_RECENT_BLUE_GRAY_LIGHT_RESIST"
S3="NEW_V5_D_GREEN_11_20_UPPER_WICK_ONLY"

VARIANTS={
    "BASELINE_ALL_15": frozenset(),
    "DROP_B3": frozenset([B3]),
    "DROP_S1": frozenset([S1]),
    "DROP_S3": frozenset([S3]),
    "DROP_B3_S1": frozenset([B3,S1]),
    "DROP_B3_S3": frozenset([B3,S3]),
    "DROP_S1_S3": frozenset([S1,S3]),
    "DROP_B3_S1_S3": frozenset([B3,S1,S3]),
}
ACTION_CODE={None:0,"BUY":1,"HOLD":2,"WAIT":3,"SELL":4}

def read_frame(batch,symbol):
    p=DATA_ROOT/f"batch_{batch:02d}_stocks"/f"{symbol}.csv.gz"
    with gzip.open(p,"rt",encoding="utf-8") as f:
        df=pd.read_csv(f,parse_dates=["Date"])
    df["Date"]=pd.to_datetime(df["Date"]).dt.tz_localize(None)
    return df

def read_ledger(batch,symbol):
    p=LEDGER_ROOT/f"BATCH_{batch:02d}_{symbol}_FIRST_OBSERVED.csv.gz"
    with gzip.open(p,"rt",encoding="utf-8") as f:
        df=pd.read_csv(f)
    df["date"]=pd.to_datetime(df["date"]).dt.tz_localize(None)
    rows=[]
    for rec in df.to_dict("records"):
        for cls in ("BUY","HOLD","WAIT","SELL"):
            v=rec.get(cls)
            rec[cls]=[] if pd.isna(v) or str(v).strip()=="" else [x for x in str(v).split("|") if x]
        rows.append(rec)
    return rows

def resolve_row(row,drops):
    if not row:
        return None
    classes=[]
    for cls in ("BUY","HOLD","WAIT","SELL"):
        ids=[r for r in row.get(cls,[]) if r not in drops]
        if ids:
            classes.append(cls)
    return core.resolve_action(tuple(classes),"NO_CHANGE_MIXED")

def c2_condition(row):
    if not row or str(row.get("color","")).upper()!="GREEN":
        return False
    try:
        high=float(row.get("high")); gzb4=float(row.get("GZB4"))
    except (TypeError,ValueError):
        return False
    return math.isfinite(high) and math.isfinite(gzb4) and high<gzb4

def prepare_symbol(frame,ledger):
    dates=pd.to_datetime(frame["Date"]).dt.tz_localize(None)
    mask=(dates>=FORMAL_START)&(dates<=FORMAL_END)
    idx=np.flatnonzero(mask.to_numpy())
    if len(idx)<2: raise RuntimeError("insufficient bars")
    fd=[pd.Timestamp(dates.iloc[i]) for i in idx]
    by={pd.Timestamp(x["date"]):x for x in ledger}
    actions={}
    for variant,drops in VARIANTS.items():
        arr=np.zeros(len(idx),dtype=np.int8)
        for j in range(1,len(idx)):
            arr[j]=ACTION_CODE[resolve_row(by.get(fd[j-1]),drops)]
        actions[variant]=arr
    c2=np.zeros(len(idx),dtype=np.bool_)
    for j in range(1,len(idx)):
        c2[j]=c2_condition(by.get(fd[j-1]))
    return {
        "dates":[d.strftime("%Y-%m-%d") for d in fd],
        "opens":frame["Open"].astype(float).to_numpy()[idx],
        "closes":frame["Close"].astype(float).to_numpy()[idx],
        "actions":actions,"c2":c2
    }

def simulate(prep,variant,bps):
    opens,closes=prep["opens"],prep["closes"]
    actions,c2=prep["actions"][variant],prep["c2"]
    n=len(opens); cash=1.0; shares=0.0
    turnover=0.0; changes=0; invested=0; hard_exits=0; armed=False
    curve=np.empty(n,dtype=float); cost_rate=bps/10000.0
    for j in range(n):
        op=float(opens[j]); cl=float(closes[j])
        pre=cash+shares*op
        pos=shares*op; frac=pos/pre
        hard=bool(shares>1e-14 and armed and c2[j])
        action=int(actions[j]); ordinary=None; order=0.0
        if hard:
            order=-pos
        else:
            ordinary=action
            if action==1:
                target=0.25 if shares<=1e-14 else min(1.0,frac+0.25)
                order=max(frac,target)*pre-pos
            elif action==4 and shares>0:
                order=-pos*0.25
        if order>1e-14:
            order=min(order,max(0.0,cash/(1.0+cost_rate)))
        elif order<-1e-14:
            order=max(order,-pos)
        executed=abs(order)>1e-14
        if executed:
            cost=abs(order)*cost_rate
            shares+=order/op; cash-=order+cost
            turnover+=abs(order)/pre; changes+=1
            if shares<=1e-12: shares=0.0
        if hard and executed:
            hard_exits+=1; armed=False
        elif executed and ordinary==4 and order<0:
            armed=True
        elif executed and ordinary==1 and order>0:
            armed=False
        curve[j]=cash+shares*cl
        if shares>1e-12: invested+=1
    final=float(curve[-1])
    days=max(1,(pd.Timestamp(prep["dates"][-1])-pd.Timestamp(prep["dates"][0])).days)
    tr=final-1.0
    cagr=final**(365.25/days)-1.0 if final>0 else -1.0
    mdd=core.max_drawdown(curve)
    calmar=cagr/abs(mdd) if mdd<-1e-12 else (999.0 if cagr>0 else 0.0)
    return {"curve":curve,"total_return":tr,"cagr":float(cagr),"max_drawdown":float(mdd),
            "calmar":float(calmar),"turnover":float(turnover),"position_changes":changes,
            "time_in_market":invested/n,"hard_exit_count":hard_exits}

def portfolio(per_symbol,prepared):
    dates,idx=core.prepare_common_alignment(prepared)
    curve=np.mean(np.vstack([per_symbol[s]["curve"][idx[s]] for s in per_symbol]),axis=0)
    days=max(1,(pd.Timestamp(dates[-1])-pd.Timestamp(dates[0])).days)
    tr=float(curve[-1]-1.0)
    cagr=float(curve[-1]**(365.25/days)-1.0) if curve[-1]>0 else -1.0
    mdd=core.max_drawdown(curve)
    calmar=cagr/abs(mdd) if mdd<-1e-12 else (999.0 if cagr>0 else 0.0)
    return {"total_return":tr,"cagr":cagr,"max_drawdown":float(mdd),"calmar":float(calmar),
            "turnover_mean":float(np.mean([v["turnover"] for v in per_symbol.values()])),
            "position_changes_sum":int(sum(v["position_changes"] for v in per_symbol.values())),
            "time_in_market_mean":float(np.mean([v["time_in_market"] for v in per_symbol.values()])),
            "hard_exit_count_sum":int(sum(v["hard_exit_count"] for v in per_symbol.values())),
            "common_start":dates[0],"common_end":dates[-1]}

def compact(v):
    return {k:v[k] for k in ("total_return","cagr","max_drawdown","calmar","turnover","position_changes","time_in_market","hard_exit_count")}

def delta(a,b):
    return {k:a[k]-b[k] for k in ("total_return","cagr","max_drawdown","calmar")} | {
        "turnover_mean":a["turnover_mean"]-b["turnover_mean"],
        "time_in_market_mean":a["time_in_market_mean"]-b["time_in_market_mean"],
        "hard_exit_count_sum":a["hard_exit_count_sum"]-b["hard_exit_count_sum"],
    }

def validate_baseline(all79):
    frozen=json.loads(FROZEN_C2_RESULT.read_text(encoding="utf-8"))
    out={}
    for f in ("5bps","10bps"):
        exp=frozen["all79_equal_weight"][f]["C2_FULL_CANDLE_BELOW_SLOW_BAND"]
        act=all79[f]["BASELINE_ALL_15"]
        diffs={k:float(act[k]-exp[k]) for k in ("total_return","cagr","max_drawdown","calmar")}
        if any(abs(x)>1e-10 for x in diffs.values()):
            raise RuntimeError(f"baseline mismatch {f}: {diffs}")
        out[f]={"status":"PASS","diffs":diffs}
    return out

def interaction_summary(all79,friction,combo,singles):
    base=all79[friction]["BASELINE_ALL_15"]
    combo_d=delta(all79[friction][combo],base)
    expected_cagr=sum(delta(all79[friction][s],base)["cagr"] for s in singles)
    expected_calmar=sum(delta(all79[friction][s],base)["calmar"] for s in singles)
    ic=combo_d["cagr"]-expected_cagr
    im=combo_d["calmar"]-expected_calmar
    def label(x,tol):
        return "BETTER_THAN_ADDITIVE" if x>tol else ("WORSE_THAN_ADDITIVE" if x<-tol else "APPROX_ADDITIVE")
    return {
        "combo_delta_vs_baseline":combo_d,
        "sum_single_deltas":{"cagr":expected_cagr,"calmar":expected_calmar},
        "interaction_delta":{"cagr":ic,"calmar":im},
        "interaction_label_cagr":label(ic,0.001),
        "interaction_label_calmar":label(im,0.01),
    }

def pct(x): return f"{100*x:.2f}%"
def s3(x): return f"{x:+.3f}"

def main():
    prepared={}; batch_of={}
    for batch,symbols in core.BATCHES.items():
        for symbol in symbols:
            prepared[symbol]=prepare_symbol(read_frame(batch,symbol),read_ledger(batch,symbol))
            batch_of[symbol]=batch
    if len(prepared)!=79: raise RuntimeError(f"expected 79, got {len(prepared)}")

    sims={"5bps":{},"10bps":{}}
    for fname,bps in (("5bps",5.0),("10bps",10.0)):
        for v in VARIANTS:
            sims[fname][v]={s:simulate(prepared[s],v,bps) for s in prepared}

    batch_results={"5bps":{},"10bps":{}}
    all79={"5bps":{},"10bps":{}}
    for f in ("5bps","10bps"):
        for v in VARIANTS:
            batch_results[f][v]={}
            for b,symbols in core.BATCHES.items():
                pp={s:prepared[s] for s in symbols}
                ss={s:sims[f][v][s] for s in symbols}
                batch_results[f][v][str(b)]=portfolio(ss,pp)
            all79[f][v]=portfolio(sims[f][v],prepared)

    baseline_check=validate_baseline(all79)
    comparisons={}
    base_batches=batch_results["5bps"]["BASELINE_ALL_15"]
    for v in VARIANTS:
        if v=="BASELINE_ALL_15": continue
        counts={"calmar_improved":0,"calmar_worsened":0,"cagr_improved":0,"cagr_worsened":0,
                "maxdd_improved":0,"maxdd_worsened":0}
        bd={}
        for b in map(str,range(1,9)):
            d=delta(batch_results["5bps"][v][b],base_batches[b]); bd[b]=d
            for metric,pos,neg in (
                ("calmar","calmar_improved","calmar_worsened"),
                ("cagr","cagr_improved","cagr_worsened"),
                ("max_drawdown","maxdd_improved","maxdd_worsened"),
            ):
                if d[metric]>1e-12: counts[pos]+=1
                elif d[metric]<-1e-12: counts[neg]+=1
        comparisons[v]={
            "drops":sorted(VARIANTS[v]),
            "all79_delta_5bps":delta(all79["5bps"][v],all79["5bps"]["BASELINE_ALL_15"]),
            "all79_delta_10bps":delta(all79["10bps"][v],all79["10bps"]["BASELINE_ALL_15"]),
            "batch_counts_5bps":counts,
            "median_batch_delta_5bps":{
                "cagr":float(statistics.median(x["cagr"] for x in bd.values())),
                "max_drawdown":float(statistics.median(x["max_drawdown"] for x in bd.values())),
                "calmar":float(statistics.median(x["calmar"] for x in bd.values())),
            },
            "batch_deltas_5bps":bd,
        }

    interactions={}
    combos={
        "DROP_B3_S1":["DROP_B3","DROP_S1"],
        "DROP_B3_S3":["DROP_B3","DROP_S3"],
        "DROP_S1_S3":["DROP_S1","DROP_S3"],
        "DROP_B3_S1_S3":["DROP_B3","DROP_S1","DROP_S3"],
    }
    for combo,singles in combos.items():
        interactions[combo]={f:interaction_summary(all79,f,combo,singles) for f in ("5bps","10bps")}

    per_symbol={s:{
        "batch":batch_of[s],
        "5bps":{v:compact(sims["5bps"][v][s]) for v in VARIANTS},
        "10bps":{v:compact(sims["10bps"][v][s]) for v in VARIANTS},
    } for s in prepared}

    output={
        "meta":{
            "study":"SLTD_V7_COMBINATION_ABLATION_STUDY_V1","status":"COMPLETE",
            "research_type":"EXPLORATORY_REUSED_79_STOCK_UNIVERSE",
            "baseline_branch":"baseline/sltd-v6-15rules-position-v1",
            "baseline_commit":"05be43e350d9193ba01a2748ef4c0267438a84b1",
            "parent_single_ablation_commit":"d303a2a961eb9adeeb224bf0bef16725919be591",
            "universe_count":79,"formal_window":"2020-01-02..2026-09-30",
            "representation":"FIRST_OBSERVED","execution":"SIGNAL_CLOSE_TO_NEXT_AVAILABLE_OPEN",
            "ordinary_policy":"I25_AADD_25_TO_CAP_S25_WHOLD_RNO_CHANGE_MIXED",
            "hard_exit":"C2_FULL_CANDLE_BELOW_SLOW_BAND",
            "generated_at_utc":datetime.now(timezone.utc).isoformat(),
        },
        "variants":{k:sorted(v) for k,v in VARIANTS.items()},
        "frozen_baseline_reproduction":baseline_check,
        "all79_equal_weight":all79,"batch_results":batch_results,
        "comparisons":comparisons,"interactions":interactions,"per_symbol":per_symbol,
    }
    OUT_JSON.write_text(json.dumps(output,indent=2),encoding="utf-8")

    lines=[
        "# SLTD V7 Combination Ablation Study v1","",
        "Status: **COMPLETE**","",
        "Research status: **EXPLORATORY — reused 79-stock universe**","",
        "Frozen V6 baseline remains unchanged.","",
        "Baseline reproduction against frozen C2 result: **PASS (5 bps and 10 bps)**.","",
        "## All-79 portfolio — 5 bps","",
        "| Variant | Return | CAGR | MaxDD | Calmar | Turnover | C2 exits |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for v in VARIANTS:
        m=all79["5bps"][v]
        lines.append(f"| {v} | {pct(m['total_return'])} | {pct(m['cagr'])} | {pct(m['max_drawdown'])} | {m['calmar']:.3f} | {m['turnover_mean']:.2f} | {m['hard_exit_count_sum']} |")
    lines += ["","## Delta vs frozen baseline — 5 bps","",
              "| Variant | ΔCAGR | ΔMaxDD | ΔCalmar | Calmar better batches | Calmar worse batches |",
              "|---|---:|---:|---:|---:|---:|"]
    for v,x in comparisons.items():
        d=x["all79_delta_5bps"]; c=x["batch_counts_5bps"]
        lines.append(f"| {v} | {pct(d['cagr'])} | {pct(d['max_drawdown'])} | {s3(d['calmar'])} | {c['calmar_improved']}/8 | {c['calmar_worsened']}/8 |")
    lines += ["","## Combination interaction — 5 bps","",
              "| Combo | Interaction ΔCAGR | CAGR label | Interaction ΔCalmar | Calmar label |",
              "|---|---:|---|---:|---|"]
    for combo,x in interactions.items():
        y=x["5bps"]
        lines.append(f"| {combo} | {pct(y['interaction_delta']['cagr'])} | {y['interaction_label_cagr']} | {s3(y['interaction_delta']['calmar'])} | {y['interaction_label_calmar']} |")
    lines += ["","This study does not change the frozen V6 baseline. Any candidate must receive fresh OOS validation before replacement.","",
              "`SLTD_V7_COMBINATION_ABLATION_STUDY_V1 = COMPLETE`",""]
    OUT_MD.write_text("\n".join(lines),encoding="utf-8")

if __name__=="__main__":
    main()
