#!/usr/bin/env python3
"""Post-hoc diagnostic ablation for Fresh20 R2.

This is diagnostic only. Fresh20 outcomes are already known, so this script
cannot promote a new candidate. It separates PM_BUY_1 and PM_SELL_1 contributions.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import pure_sltd_v8_probability_map_r2_v1 as r2

PROJECT=ROOT.parents[2]/"integrations"/"sltd_v7_siftalpha_v1"
sys.path.insert(0,str(PROJECT))
import strategy as sltd

OUT_JSON=ROOT/"PURE_SLTD_V8_PROBABILITY_MAP_R2_ABLATION_DIAGNOSTIC_v1.json"
OUT_MD=ROOT/"PURE_SLTD_V8_PROBABILITY_MAP_R2_ABLATION_DIAGNOSTIC_v1.md"


def resolve(row, buy_on, sell_on):
    if not row:
        return None, []
    classes=set(sltd.action_classes(row))
    extras=[]
    if buy_on and r2.pm_buy(row):
        classes.add("BUY"); extras.append(r2.PM_BUY_ID)
    if sell_on and r2.pm_sell(row):
        classes.add("SELL"); extras.append(r2.PM_SELL_ID)
    if len(classes)!=1:
        return None,extras
    return next(iter(classes)),extras


def simulate(bars,ledger,bps,buy_on,sell_on):
    formal_index=next((i for i,b in enumerate(bars) if b["date"]>=sltd.POLICY_START_DATE),0)
    start=max(formal_index,min(sltd.MIN_WARMUP_BARS,len(bars)-1))
    end=max(i for i,b in enumerate(bars) if b["date"]<=r2.FORMAL_END.strftime("%Y-%m-%d"))
    cash=1.0;shares=0.0;armed=False;cost_rate=bps/10000.0
    curve=[];dates=[];changes=0;turnover=0.0;hard_exits=0;invested=0
    pmb=0;pms=0
    for j in range(start,end+1):
        bar=bars[j];op=float(bar["open"]);cl=float(bar["close"])
        pre=cash+shares*op;pos=shares*op;frac=pos/pre if pre>0 else 0.0
        signal=ledger[j-1] if j>start else None
        hard=bool(shares>1e-14 and armed and sltd.c2_condition(signal))
        action,extras=resolve(signal,buy_on,sell_on)
        ordinary=None;order=0.0
        if hard:
            order=-pos
        else:
            ordinary=action
            if action=="BUY":
                target=0.25 if shares<=1e-14 else min(1.0,frac+0.25)
                order=max(frac,target)*pre-pos
            elif action=="SELL" and shares>0:
                order=-pos*0.25
        if order>1e-14:
            order=min(order,max(0.0,cash/(1.0+cost_rate)))
        elif order<-1e-14:
            order=max(order,-pos)
        executed=abs(order)>1e-14
        if executed:
            cost=abs(order)*cost_rate
            shares+=order/op;cash-=order+cost
            if shares<=1e-12: shares=0.0
            changes+=1;turnover+=abs(order)/pre
            if r2.PM_BUY_ID in extras and ordinary=="BUY" and order>0: pmb+=1
            if r2.PM_SELL_ID in extras and ordinary=="SELL" and order<0: pms+=1
            if hard: hard_exits+=1
        if hard and executed: armed=False
        elif executed and ordinary=="SELL" and order<0: armed=True
        elif executed and ordinary=="BUY" and order>0: armed=False
        eq=cash+shares*cl
        curve.append(eq);dates.append(bar["date"])
        if shares>1e-12:invested+=1
    arr=np.asarray(curve,dtype=float)
    days=max(1,(pd.Timestamp(dates[-1])-pd.Timestamp(dates[0])).days)
    tr=float(arr[-1]-1);cagr=float(arr[-1]**(365.25/days)-1) if arr[-1]>0 else -1
    mdd=r2.max_drawdown(arr);calmar=cagr/abs(mdd) if mdd<-1e-12 else (999.0 if cagr>0 else 0.0)
    return {"dates":dates,"curve":arr,"total_return":tr,"cagr":cagr,"max_drawdown":mdd,
            "calmar":float(calmar),"turnover":float(turnover),"position_changes":changes,
            "time_in_market":invested/len(arr),"hard_exit_count":hard_exits,
            "pm_buy_exec_count":pmb,"pm_sell_exec_count":pms}


def compact(x):
    return {k:v for k,v in x.items() if k not in {"dates","curve"}}


def pct(x): return f"{100*x:.2f}%"


def main():
    specs={
      "V7_BASE":(False,False),
      "BUY_ONLY":(True,False),
      "SELL_ONLY":(False,True),
      "BOTH":(True,True),
    }
    allres={};per_symbol={}
    for flabel,bps in (("5bps",5.0),("10bps",10.0)):
        allres[flabel]={k:{} for k in specs}
        for s in r2.SYMBOLS:
            frame=pd.read_csv(r2.DATA_DIR/f"{s}.csv.gz",parse_dates=["Date"])
            bars=r2.candles_from_frame(frame)
            ledger=sltd.build_ledger(bars,s)
            for label,(bo,so) in specs.items():
                allres[flabel][label][s]=simulate(bars,ledger,bps,bo,so)
        per_symbol.setdefault(flabel,{})
        for s in r2.SYMBOLS:
            per_symbol[flabel][s]={k:compact(allres[flabel][k][s]) for k in specs}

    port={flabel:{k:r2.portfolio_metrics(v) for k,v in systems.items()} for flabel,systems in allres.items()}
    base=allres["5bps"]["V7_BASE"]
    breadth={}
    for k in ("BUY_ONLY","SELL_ONLY","BOTH"):
        breadth[k]={
          "return_better":sum(allres["5bps"][k][s]["total_return"]>base[s]["total_return"] for s in r2.SYMBOLS),
          "calmar_better":sum(allres["5bps"][k][s]["calmar"]>base[s]["calmar"] for s in r2.SYMBOLS),
        }

    out={"study":"PURE_SLTD_V8_PROBABILITY_MAP_R2_ABLATION_DIAGNOSTIC_v1",
         "status":"COMPLETE_DIAGNOSTIC_ONLY_NOT_OOS",
         "fresh20_already_seen":True,
         "portfolio":port,"breadth_5bps":breadth,"per_symbol":per_symbol}
    OUT_JSON.write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding="utf-8")

    lines=["# Pure SLTD V8 Probability Map R2 — Ablation Diagnostic","",
           "Status: **COMPLETE / DIAGNOSTIC ONLY / NOT OOS**","",
           "Fresh20 outcomes were already known before this ablation. Results may diagnose contribution but cannot promote a rule.","",
           "## Equal-weight portfolio — 5 bps","",
           "| Variant | Return | CAGR | MaxDD | Calmar | Turnover | Return breadth | Calmar breadth |",
           "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for k in specs:
        m=port["5bps"][k]
        b={"return_better":0,"calmar_better":0} if k=="V7_BASE" else breadth[k]
        lines.append(f"| {k} | {pct(m['total_return'])} | {pct(m['cagr'])} | {pct(m['max_drawdown'])} | {m['calmar']:.3f} | {m['turnover_mean']:.2f} | {b['return_better']}/20 | {b['calmar_better']}/20 |")
    lines+=["","No rule is promoted by this diagnostic.","","PURE_SLTD_V8_PROBABILITY_MAP_R2_ABLATION_DIAGNOSTIC_V1 = COMPLETE_DIAGNOSTIC_ONLY",""]
    OUT_MD.write_text("\n".join(lines),encoding="utf-8")
    print(json.dumps({"portfolio_5bps":port["5bps"],"breadth_5bps":breadth},indent=2))


if __name__=="__main__":
    main()
