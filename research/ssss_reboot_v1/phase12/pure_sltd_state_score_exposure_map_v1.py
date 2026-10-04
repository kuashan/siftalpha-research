#!/usr/bin/env python3
"""Pure SLTD state score -> target exposure map v1."""
from __future__ import annotations

import gzip
import json
import math
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

ROOT=Path(__file__).resolve().parent
PHASE7=ROOT.parent/"phase7"
PHASE11=ROOT.parent/"phase11"

sys.path.insert(0,str(PHASE7))
sys.path.insert(0,str(PHASE11))
import pure_sltd_v8_probability_map_r2_v1 as r2

PROJECT=ROOT.parents[2]/"integrations"/"sltd_v7_siftalpha_v1"
sys.path.insert(0,str(PROJECT))
import strategy as sltd

FORMAL_START=pd.Timestamp("2020-01-02")
FORMAL_END=pd.Timestamp("2026-09-30")
CAL_END=pd.Timestamp("2023-12-31")
FETCH_START="2010-01-04"
FETCH_END_EXCLUSIVE="2026-10-01"

UNIVERSE=[
 ("COF","Financial"),("MCO","Financial"),("AJG","Financial"),
 ("BSX","Healthcare"),("EW","Healthcare"),("ZTS","Healthcare"),
 ("GD","Industrials"),("NOC","Industrials"),("ROK","Industrials"),
 ("NEM","Materials"),("ECL","Materials"),("DD","Materials"),
 ("KR","Consumer"),("KHC","Consumer"),("DG","Consumer"),
 ("CHTR","Communication"),("TTWO","Communication"),("FOXA","Communication"),
 ("EQIX","RealEstate"),("PSA","RealEstate"),("O","RealEstate"),
 ("MPC","Energy"),("OXY","Energy"),("VLO","Energy"),
]
SYMBOLS=[x[0] for x in UNIVERSE]

DATA_DIR=ROOT/"fresh24_state_score_exposure_data"
OUT_JSON=ROOT/"PURE_SLTD_STATE_SCORE_EXPOSURE_MAP_RESULT_v1.json"
OUT_MD=ROOT/"PURE_SLTD_STATE_SCORE_EXPOSURE_MAP_RESULT_v1.md"

PRIOR_OOS10={"WFC","LMT","PM","ADP","WM","UNP","SO","VZ","PANW","CVS"}
PRIOR_R2={"AXP","PGR","CB","ICE","T","TMUS","CMCSA","CL","MDLZ","GIS","MMM","FDX","EMR","DUK","D","EXC","SLB","EOG","F","GM"}
PRIOR_R3={"PNC","USB","CME","HCA","CI","BDX","ETN","PH","ITW","APD","SHW","FCX","YUM","ORLY","AMT","CCI","ED","SRE","PSX","KMI"}

PROB_PATH=PHASE11/"PURE_SLTD_STATE_PROBABILITY_RESULT_v1.json"


def pct(x):
    return "—" if x is None else f"{100*x:.2f}%"


def compact(x):
    return {k:v for k,v in x.items() if k not in {"dates","curve"}}


def load_confirmed_weights():
    x=json.loads(PROB_PATH.read_text(encoding="utf-8"))
    weights={}
    metadata={}
    for c in x["confirmed"]:
        ident=c["id"]
        d10=c["discovery"]["h10"]["symbol_median_excess"]
        t10=c["temporal"]["h10"]["symbol_median_excess"]
        o10=c["external_oos"]["h10"]["symbol_median_excess"]
        d20=c["discovery"]["h20"]["symbol_median_excess"]
        t20=c["temporal"]["h20"]["symbol_median_excess"]
        o20=c["external_oos"]["h20"]["symbol_median_excess"]
        e10=float(np.median([d10,t10,o10]))
        e20=float(np.median([d20,t20,o20]))
        w=(e10+e20)/2.0
        weights[ident]=w
        metadata[ident]={"e10":e10,"e20":e20,"weight":w,"direction":c["direction"]}
    if len(weights)!=20:
        raise RuntimeError(f"expected 20 confirmed states, got {len(weights)}")
    return weights,metadata


def parse_bool(v):
    if isinstance(v,(bool,np.bool_)):
        return bool(v)
    if v is None or (isinstance(v,float) and math.isnan(v)):
        return False
    return str(v).strip().lower() in {"1","true","yes","y"}

def norm(v,default="NONE"):
    if v is None or (isinstance(v,float) and math.isnan(v)):
        return default
    s=str(v).strip().upper()
    return s if s else default


def descriptor(ledger, i):
    row=ledger[i]
    color=norm(row.get("color"),"OTHER")
    age=norm(row.get("age"),"NA")
    origin=norm(row.get("origin"),"NONE")
    close=float(row["close"])
    zd1=float(row["ZD1"])
    zk1=float(row["ZK1"])
    if math.isfinite(close) and math.isfinite(zd1) and math.isfinite(zk1) and zk1>zd1:
        if close<zd1: inner="BELOW_ZD1"
        elif close>zk1: inner="ABOVE_ZK1"
        elif close <= (zd1+zk1)/2.0: inner="LOWER_HALF"
        else: inner="UPPER_HALF"
    else:
        inner="NA"

    g3=row.get("GZB3"); g4=row.get("GZB4")
    slow_pos="NA"
    if g3 is not None and g4 is not None:
        g3=float(g3);g4=float(g4)
        if math.isfinite(g3) and math.isfinite(g4) and g3>=g4:
            if close<g4: slow_pos="BELOW_GZB4"
            elif close>g3: slow_pos="ABOVE_GZB3"
            else: slow_pos="IN_GZB_BAND"

    slow_trend="FLAT_OR_NA"
    if i>=5:
        a3=ledger[i-5].get("GZB3");a4=ledger[i-5].get("GZB4")
        if None not in (g3,g4,a3,a4):
            now=(float(g3)+float(g4))/2.0
            old=(float(a3)+float(a4))/2.0
            if math.isfinite(now) and math.isfinite(old):
                if now>old: slow_trend="UP"
                elif now<old: slow_trend="DOWN"

    events=[]
    if parse_bool(row.get("lower")):
        events.append(("LOWER",norm(row.get("lower_subtype"),"NONE")))
    if parse_bool(row.get("upper")):
        events.append(("UPPER",norm(row.get("upper_subtype"),"NONE")))
    if parse_bool(row.get("light_support")):
        events.append(("LIGHT_SUPPORT","CONTACT"))
    if parse_bool(row.get("light_resist")):
        events.append(("LIGHT_RESIST","CONTACT"))

    return {
      "color":color,"age":age,"origin":origin,"inner":inner,
      "slow_pos":slow_pos,"slow_trend":slow_trend,"events":events,
    }


def score_bar(ledger,i,weights):
    d=descriptor(ledger,i)
    c=d["color"];a=d["age"];o=d["origin"]

    regime_candidates=[
      ("F1_COLOR_AGE",f"{c}|{a}"),
      ("F2_COLOR_AGE_ORIGIN",f"{c}|{a}|{o}"),
    ]
    regime_matches=[]
    matched=[]
    for fam,key in regime_candidates:
        ident=f"{fam}::{key}"
        if ident in weights:
            regime_matches.append(weights[ident]);matched.append(ident)
    regime=max(regime_matches,key=lambda x:abs(x)) if regime_matches else 0.0

    inner_ident=f"F3_COLOR_AGE_INNER::{c}|{a}|{d['inner']}"
    inner=weights.get(inner_ident,0.0)
    if inner_ident in weights: matched.append(inner_ident)

    slow_vals=[]
    for ident in [
      f"F4_COLOR_AGE_SLOWPOS::{c}|{a}|{d['slow_pos']}",
      f"F5_COLOR_AGE_SLOWTREND::{c}|{a}|{d['slow_trend']}",
    ]:
        if ident in weights:
            slow_vals.append(weights[ident]);matched.append(ident)
    slow=float(np.mean(slow_vals)) if slow_vals else 0.0

    event_vals=[]
    for event,subtype in d["events"]:
        specific=f"F7_COLOR_AGE_EVENT_SUBTYPE::{c}|{a}|{event}|{subtype}"
        broad=f"F6_COLOR_AGE_EVENT::{c}|{a}|{event}"
        if specific in weights:
            event_vals.append(weights[specific]);matched.append(specific)
        elif broad in weights:
            event_vals.append(weights[broad]);matched.append(broad)
    event=float(np.mean(event_vals)) if event_vals else 0.0

    raw=float(np.mean([regime,inner,slow,event]))
    return raw,matched,{"REGIME":regime,"INNER":inner,"SLOW":slow,"EVENT":event}


def read_phase7(batch,symbol):
    fp=PHASE7/"data_snapshot"/f"batch_{batch:02d}_stocks"/f"{symbol}.csv.gz"
    lp=PHASE7/"signal_ledgers"/f"BATCH_{batch:02d}_{symbol}_FIRST_OBSERVED.csv.gz"
    with gzip.open(fp,"rt",encoding="utf-8") as f:
        frame=pd.read_csv(f,parse_dates=["Date"])
    with gzip.open(lp,"rt",encoding="utf-8") as f:
        ledger_df=pd.read_csv(f)
    ledger_df["date"]=pd.to_datetime(ledger_df["date"]).dt.tz_localize(None)
    # list-of-dicts is enough for pure state descriptors; actions are irrelevant.
    ledger=ledger_df.to_dict("records")
    return frame,ledger


def calibrate(weights):
    scores=[]
    per_symbol={}
    # Freeze from original 79 discovery only.
    import sltd_v6_position_policy_batch_v1 as core
    for batch,symbols in core.BATCHES.items():
        for s in symbols:
            frame,ledger=read_phase7(batch,s)
            vals=[]
            for i,row in enumerate(ledger):
                dt=pd.Timestamp(row["date"])
                if FORMAL_START<=dt<=CAL_END:
                    raw,_,_=score_bar(ledger,i,weights)
                    vals.append(raw)
                    if abs(raw)>1e-15:
                        scores.append(raw)
            per_symbol[s]=vals
    pos=[x for x in scores if x>0]
    neg=[abs(x) for x in scores if x<0]
    if not pos or not neg:
        raise RuntimeError("calibration requires positive and negative nonzero scores")
    return {
      "pos_scale":float(np.median(pos)),
      "neg_scale":float(np.median(neg)),
      "nonzero_n":len(scores),
      "positive_n":len(pos),
      "negative_n":len(neg),
      "score_p10":float(np.quantile(scores,0.10)),
      "score_p50":float(np.quantile(scores,0.50)),
      "score_p90":float(np.quantile(scores,0.90)),
    }


def target_from_score(score,pos_scale,neg_scale):
    if score>=0:
        continuous=0.75+0.25*min(score/pos_scale,1.0)
    else:
        continuous=0.75-0.50*min(abs(score)/neg_scale,1.0)
    continuous=max(0.25,min(1.0,continuous))
    q=round(continuous/0.25)*0.25
    return float(max(0.25,min(1.0,q)))


def fetch_stock(ticker):
    path=DATA_DIR/f"{ticker}.csv.gz"
    if path.exists():
        return pd.read_csv(path,parse_dates=["Date"])
    last=None
    for attempt in range(4):
        try:
            f=yf.download(ticker,start=FETCH_START,end=FETCH_END_EXCLUSIVE,interval="1d",
                          auto_adjust=False,actions=False,repair=False,progress=False,
                          threads=False,multi_level_index=True)
            if f is not None and not f.empty:
                out=r2.flatten_yf(f,ticker)
                DATA_DIR.mkdir(parents=True,exist_ok=True)
                out.to_csv(path,index=False,compression="gzip")
                return out
            last=RuntimeError("empty download")
        except Exception as exc:
            last=exc
        time.sleep(2*(attempt+1))
    raise RuntimeError(f"{ticker}: download failed: {last}")


def simulate_score_exposure(bars,ledger,weights,cal,bps):
    formal_index=next((i for i,b in enumerate(bars) if b["date"]>=FORMAL_START.strftime("%Y-%m-%d")),0)
    start=max(formal_index,min(sltd.MIN_WARMUP_BARS,len(bars)-1))
    end=max(i for i,b in enumerate(bars) if b["date"]<=FORMAL_END.strftime("%Y-%m-%d"))

    cash=1.0;shares=0.0;cost_rate=bps/10000.0
    curve=[];dates=[];turnover=0.0;changes=0;invested=0
    bucket_counts=defaultdict(int)

    for j in range(start,end+1):
        op=float(bars[j]["open"]);cl=float(bars[j]["close"])
        pre=cash+shares*op
        pos=shares*op
        # previous completed bar determines today's target.
        if j>0:
            score,_,_=score_bar(ledger,j-1,weights)
            target=target_from_score(score,cal["pos_scale"],cal["neg_scale"])
        else:
            target=0.75
        bucket_counts[str(target)]+=1
        order=target*pre-pos
        if order>1e-14:
            order=min(order,max(0.0,cash/(1.0+cost_rate)))
        elif order<-1e-14:
            order=max(order,-pos)
        if abs(order)>1e-14:
            cost=abs(order)*cost_rate
            shares+=order/op
            cash-=order+cost
            if shares<=1e-12: shares=0.0
            changes+=1
            turnover+=abs(order)/pre
        eq=cash+shares*cl
        curve.append(eq);dates.append(bars[j]["date"])
        if shares>1e-12: invested+=1

    arr=np.asarray(curve,dtype=float)
    days=max(1,(pd.Timestamp(dates[-1])-pd.Timestamp(dates[0])).days)
    total=float(arr[-1]-1.0)
    cagr=float(arr[-1]**(365.25/days)-1.0) if arr[-1]>0 else -1.0
    mdd=r2.max_drawdown(arr)
    calmar=cagr/abs(mdd) if mdd<-1e-12 else (999.0 if cagr>0 else 0.0)
    return {
      "dates":dates,"curve":arr,"total_return":total,"cagr":cagr,
      "max_drawdown":mdd,"calmar":float(calmar),"turnover":float(turnover),
      "position_changes":int(changes),"time_in_market":float(invested/len(arr)),
      "target_bucket_counts":dict(bucket_counts),
    }


def simulate_fixed75(bars,bps):
    idx=[i for i,b in enumerate(bars) if FORMAL_START.strftime("%Y-%m-%d")<=b["date"]<=FORMAL_END.strftime("%Y-%m-%d")]
    start,end=idx[0],idx[-1]
    op=float(bars[start]["open"]);cost=bps/10000.0
    stock_value=min(0.75,0.75/(1.0+0.75*cost))  # conservative cost-feasible target
    shares=stock_value/op
    cash=1.0-stock_value-stock_value*cost
    curve=np.asarray([cash+shares*float(bars[i]["close"]) for i in range(start,end+1)],dtype=float)
    dates=[bars[i]["date"] for i in range(start,end+1)]
    days=max(1,(pd.Timestamp(dates[-1])-pd.Timestamp(dates[0])).days)
    tr=float(curve[-1]-1.0);cagr=float(curve[-1]**(365.25/days)-1.0)
    mdd=r2.max_drawdown(curve)
    return {"dates":dates,"curve":curve,"total_return":tr,"cagr":cagr,
            "max_drawdown":mdd,"calmar":float(cagr/abs(mdd) if mdd<-1e-12 else 999.0),
            "turnover":stock_value,"position_changes":1,"time_in_market":1.0}


def bucket_diagnostic(bars_by,ledger_by,weights,cal):
    per_bucket={0.25:defaultdict(list),0.5:defaultdict(list),0.75:defaultdict(list),1.0:defaultdict(list)}
    base=defaultdict(lambda:defaultdict(list))
    counts=defaultdict(int)
    symbols_by=defaultdict(set)

    for s in SYMBOLS:
        bars=bars_by[s];ledger=ledger_by[s]
        for t,row in enumerate(ledger):
            dt=pd.Timestamp(row["date"])
            if not (FORMAL_START<=dt<=FORMAL_END):
                continue
            if t+20>=len(bars):
                continue
            entry=float(bars[t+1]["open"])
            if entry<=0: continue
            score,_,_=score_bar(ledger,t,weights)
            bucket=target_from_score(score,cal["pos_scale"],cal["neg_scale"])
            counts[bucket]+=1;symbols_by[bucket].add(s)
            for h in (10,20):
                ret=float(bars[t+h]["close"])/entry-1.0
                per_bucket[bucket][(s,h)].append(ret)
                base[s][h].append(ret)

    result={}
    for bucket in (0.25,0.5,0.75,1.0):
        result[str(bucket)]={"count":counts[bucket],"symbol_count":len(symbols_by[bucket]),"horizons":{}}
        for h in (10,20):
            effects=[]
            for s in SYMBOLS:
                vals=per_bucket[bucket].get((s,h),[])
                if vals and base[s][h]:
                    effects.append(float(np.median(vals)-np.median(base[s][h])))
            result[str(bucket)]["horizons"][str(h)]={
              "cross_symbol_median_excess":float(np.median(effects)) if effects else None,
              "positive_breadth":float(np.mean(np.asarray(effects)>0)) if effects else None,
              "negative_breadth":float(np.mean(np.asarray(effects)<0)) if effects else None,
              "symbol_effect_count":len(effects),
            }
    return result


def main():
    # Prior-universe overlap audit.
    import sltd_v6_position_policy_batch_v1 as core
    prior79={s for xs in core.BATCHES.values() for s in xs}
    prior=prior79|PRIOR_OOS10|PRIOR_R2|PRIOR_R3
    overlap=sorted(set(SYMBOLS)&prior)
    if overlap:
        raise RuntimeError(f"Fresh24 overlap: {overlap}")
    if len(SYMBOLS)!=24 or len(set(SYMBOLS))!=24:
        raise RuntimeError("Fresh24 must contain 24 unique symbols")

    weights,weight_meta=load_confirmed_weights()
    calibration=calibrate(weights)

    DATA_DIR.mkdir(parents=True,exist_ok=True)
    manifest={
      "study":"PURE_SLTD_STATE_SCORE_EXPOSURE_MAP_V1",
      "symbols":SYMBOLS,"industries":dict(UNIVERSE),"prior_overlap":overlap,
      "provider":"Yahoo Finance via yfinance","auto_adjust":False,
      "fetch_start":FETCH_START,"fetch_end_exclusive":FETCH_END_EXCLUSIVE,
      "formal_window":["2020-01-02","2026-09-30"],
      "calibration":calibration,
      "files":{},"generated_at_utc":datetime.now(timezone.utc).isoformat(),
    }

    bars_by={};ledger_by={}
    for s,industry in UNIVERSE:
        frame=fetch_stock(s)
        if pd.Timestamp(frame["Date"].min())>=FORMAL_START:
            raise RuntimeError(f"{s}: no pre-2020 warmup")
        if pd.Timestamp(frame["Date"].max())<FORMAL_END:
            raise RuntimeError(f"{s}: data ends early")
        bars=r2.candles_from_frame(frame)
        ledger=sltd.build_ledger(bars,s)
        bars_by[s]=bars;ledger_by[s]=ledger
        p=DATA_DIR/f"{s}.csv.gz"
        manifest["files"][s]={
          "industry":industry,"rows":len(frame),
          "first":pd.Timestamp(frame["Date"].min()).strftime("%Y-%m-%d"),
          "last":pd.Timestamp(frame["Date"].max()).strftime("%Y-%m-%d"),
          "sha256":r2.sha256_file(p),
        }
    (DATA_DIR/"manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")

    systems={}
    per_symbol={}
    for flabel,bps in (("5bps",5.0),("10bps",10.0)):
        systems[flabel]={"SCORE_EXPOSURE":{},"V7_BASE":{},"FIXED_75_LONG":{},"BUY_HOLD":{},"SMA200_TREND":{}}
        for s in SYMBOLS:
            bars=bars_by[s];ledger=ledger_by[s]
            systems[flabel]["SCORE_EXPOSURE"][s]=simulate_score_exposure(bars,ledger,weights,calibration,bps)
            systems[flabel]["V7_BASE"][s]=r2.simulate_sltd(bars,ledger,bps,False)
            systems[flabel]["FIXED_75_LONG"][s]=simulate_fixed75(bars,bps)
            systems[flabel]["BUY_HOLD"][s]=r2.simulate_buy_hold(bars,bps)
            systems[flabel]["SMA200_TREND"][s]=r2.simulate_sma200(bars,bps)

    portfolio={
      flabel:{label:r2.portfolio_metrics(vals) for label,vals in group.items()}
      for flabel,group in systems.items()
    }
    per_symbol={
      s:{flabel:{label:compact(systems[flabel][label][s]) for label in systems[flabel]}
         for flabel in systems}
      for s in SYMBOLS
    }

    diag=bucket_diagnostic(bars_by,ledger_by,weights,calibration)
    score5=portfolio["5bps"]["SCORE_EXPOSURE"]
    v75=portfolio["5bps"]["V7_BASE"]
    fixed5=portfolio["5bps"]["FIXED_75_LONG"]
    score10=portfolio["10bps"]["SCORE_EXPOSURE"]
    v710=portfolio["10bps"]["V7_BASE"]

    breadth_calmar=sum(
      per_symbol[s]["5bps"]["SCORE_EXPOSURE"]["calmar"]>per_symbol[s]["5bps"]["V7_BASE"]["calmar"]
      for s in SYMBOLS
    )

    low=diag["0.25"];high=diag["1.0"]
    gates={
      "calmar_gt_v7_5bps":score5["calmar"]>v75["calmar"],
      "calmar_gt_fixed75_5bps":score5["calmar"]>fixed5["calmar"],
      "return_gt_fixed75_5bps":score5["total_return"]>fixed5["total_return"],
      "return_ge_95pct_v7_5bps":score5["total_return"]>=0.95*v75["total_return"],
      "maxdd_not_worse_v7_5bps":score5["max_drawdown"]>=v75["max_drawdown"],
      "calmar_breadth_ge_13":breadth_calmar>=13,
      "calmar_gt_v7_10bps":score10["calmar"]>v710["calmar"],
      "return_ge_95pct_v7_10bps":score10["total_return"]>=0.95*v710["total_return"],
      "low_bucket_support":low["count"]>=200 and low["symbol_count"]>=12,
      "high_bucket_support":high["count"]>=200 and high["symbol_count"]>=12,
      "high_10d_positive":high["horizons"]["10"]["cross_symbol_median_excess"] is not None and high["horizons"]["10"]["cross_symbol_median_excess"]>0,
      "high_20d_positive":high["horizons"]["20"]["cross_symbol_median_excess"] is not None and high["horizons"]["20"]["cross_symbol_median_excess"]>0,
      "low_10d_negative":low["horizons"]["10"]["cross_symbol_median_excess"] is not None and low["horizons"]["10"]["cross_symbol_median_excess"]<0,
      "low_20d_negative":low["horizons"]["20"]["cross_symbol_median_excess"] is not None and low["horizons"]["20"]["cross_symbol_median_excess"]<0,
      "high_gt_low_10d":(
        high["horizons"]["10"]["cross_symbol_median_excess"] is not None and
        low["horizons"]["10"]["cross_symbol_median_excess"] is not None and
        high["horizons"]["10"]["cross_symbol_median_excess"]>low["horizons"]["10"]["cross_symbol_median_excess"]
      ),
      "high_gt_low_20d":(
        high["horizons"]["20"]["cross_symbol_median_excess"] is not None and
        low["horizons"]["20"]["cross_symbol_median_excess"] is not None and
        high["horizons"]["20"]["cross_symbol_median_excess"]>low["horizons"]["20"]["cross_symbol_median_excess"]
      ),
    }

    portfolio_keys=[
      "calmar_gt_v7_5bps","calmar_gt_fixed75_5bps","return_gt_fixed75_5bps",
      "return_ge_95pct_v7_5bps","maxdd_not_worse_v7_5bps","calmar_breadth_ge_13",
      "calmar_gt_v7_10bps","return_ge_95pct_v7_10bps",
    ]
    diag_keys=[k for k in gates if k not in portfolio_keys]

    if all(gates.values()):
        decision="PROMOTE_TO_ENGINEERING_CANDIDATE"
    elif all(gates[k] for k in portfolio_keys) and not all(gates[k] for k in diag_keys):
        decision="RESEARCH_ONLY_NOT_PROMOTED"
    else:
        decision="REJECTED_NOT_ADMITTED"

    out={
      "meta":{
        "study":"PURE_SLTD_STATE_SCORE_EXPOSURE_MAP_V1","status":"COMPLETE",
        "protocol":"PURE_SLTD_STATE_SCORE_EXPOSURE_MAP_PROTOCOL_v1.md",
        "chan_used":False,"confirmed_state_count":len(weights),
        "fresh_universe":UNIVERSE,"prior_overlap":overlap,
        "formal_window":"2020-01-02..2026-09-30",
        "generated_at_utc":datetime.now(timezone.utc).isoformat(),
      },
      "weight_metadata":weight_meta,
      "calibration":calibration,
      "portfolio":portfolio,
      "breadth_5bps":{"calmar_better_vs_v7":breadth_calmar},
      "bucket_diagnostic":diag,
      "gates":gates,"decision":decision,
      "per_symbol":per_symbol,
    }
    OUT_JSON.write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding="utf-8")

    lines=[
      "# Pure SLTD State Score -> Exposure Map v1 — Result","",
      "Status: **COMPLETE**","",f"Decision: **{decision}**","",
      "Chan/缠论: **NOT USED**","",
      "## Frozen calibration","",
      f"- Positive scale: **{calibration['pos_scale']:.6f}**",
      f"- Negative scale: **{calibration['neg_scale']:.6f}**",
      f"- Calibration nonzero states: **{calibration['nonzero_n']}**","",
      "## Equal-weight Fresh24 portfolio — 5 bps","",
      "| System | Return | CAGR | MaxDD | Calmar | Turnover mean | Invested bars |",
      "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for label in ("SCORE_EXPOSURE","V7_BASE","FIXED_75_LONG","BUY_HOLD","SMA200_TREND"):
        m=portfolio["5bps"][label]
        lines.append(
          f"| {label} | {pct(m['total_return'])} | {pct(m['cagr'])} | {pct(m['max_drawdown'])} | "
          f"{m['calmar']:.3f} | {m['turnover_mean']:.2f} | {pct(m['time_in_market_mean'])} |"
        )
    lines+=["","## Fresh24 state buckets","",
      "| Target | Count | Stocks | 10d excess | 20d excess |",
      "|---:|---:|---:|---:|---:|"]
    for b in ("0.25","0.5","0.75","1.0"):
        z=diag[b]
        lines.append(
          f"| {float(b)*100:.0f}% | {z['count']} | {z['symbol_count']} | "
          f"{pct(z['horizons']['10']['cross_symbol_median_excess'])} | "
          f"{pct(z['horizons']['20']['cross_symbol_median_excess'])} |"
        )
    lines+=["","## Gates",""]
    for k,v in gates.items():
        lines.append(f"- {k}: **{'PASS' if v else 'FAIL'}**")
    lines+=["","No production V7 rule is changed by this run.","",f"PURE_SLTD_STATE_SCORE_EXPOSURE_MAP_V1 = {decision}",""]
    OUT_MD.write_text("\n".join(lines),encoding="utf-8")

    print(json.dumps({
      "decision":decision,
      "calibration":calibration,
      "portfolio_5bps":{k:compact(v) for k,v in portfolio["5bps"].items()},
      "portfolio_10bps":{k:compact(v) for k,v in portfolio["10bps"].items()},
      "breadth_5bps":out["breadth_5bps"],
      "bucket_diagnostic":diag,
      "gates":gates,
    },indent=2,ensure_ascii=False))


if __name__=="__main__":
    main()
