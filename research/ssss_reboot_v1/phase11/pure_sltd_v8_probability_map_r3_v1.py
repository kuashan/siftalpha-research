#!/usr/bin/env python3
"""Pure SLTD V8 probability-map R3 on a second untouched Fresh20 universe."""
from __future__ import annotations

import json
import math
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import pure_sltd_v8_probability_map_r2_v1 as r2
import pure_sltd_state_probability_v1 as state_study

PHASE7=ROOT.parent/"phase7"
sys.path.insert(0,str(PHASE7))
import sltd_v6_position_policy_batch_v1 as core

PROJECT=ROOT.parents[2]/"integrations"/"sltd_v7_siftalpha_v1"
sys.path.insert(0,str(PROJECT))
import strategy as sltd

FORMAL_START=pd.Timestamp("2020-01-02")
FORMAL_END=pd.Timestamp("2026-09-30")
FETCH_START="2010-01-04"
FETCH_END_EXCLUSIVE="2026-10-01"

UNIVERSE=[
 ("PNC","Financial"),("USB","Financial"),("CME","Financial"),
 ("HCA","Healthcare"),("CI","Healthcare"),("BDX","Healthcare"),
 ("ETN","Industrials"),("PH","Industrials"),("ITW","Industrials"),
 ("APD","Materials"),("SHW","Materials"),("FCX","Materials"),
 ("YUM","Consumer"),("ORLY","Consumer"),
 ("AMT","RealEstate"),("CCI","RealEstate"),
 ("ED","Utilities"),("SRE","Utilities"),
 ("PSX","Energy"),("KMI","Energy"),
]
SYMBOLS=[x[0] for x in UNIVERSE]
DATA_DIR=ROOT/"fresh20_probability_map_r3_data"
OUT_JSON=ROOT/"PURE_SLTD_V8_PROBABILITY_MAP_R3_RESULT_v1.json"
OUT_MD=ROOT/"PURE_SLTD_V8_PROBABILITY_MAP_R3_RESULT_v1.md"


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
            last=RuntimeError("empty")
        except Exception as exc:
            last=exc
        time.sleep(2*(attempt+1))
    raise RuntimeError(f"{ticker}: download failed: {last}")


def event_metrics(bars,ledger,predicate):
    raw={10:[],20:[]}
    allr={10:[],20:[]}
    for t,row in enumerate(ledger):
        if row["date"]<FORMAL_START.strftime("%Y-%m-%d") or row["date"]>FORMAL_END.strftime("%Y-%m-%d"):
            continue
        if t+20>=len(bars):
            continue
        entry=float(bars[t+1]["open"])
        if not math.isfinite(entry) or entry<=0:
            continue
        for h in (10,20):
            ret=float(bars[t+h]["close"])/entry-1.0
            allr[h].append(ret)
            if predicate(row):
                raw[h].append(ret)
    out={}
    for h in (10,20):
        base=float(np.median(allr[h])) if allr[h] else None
        med=float(np.median(raw[h])) if raw[h] else None
        out[h]={
            "n":len(raw[h]),
            "absolute_median":med,
            "absolute_win_rate":float(np.mean(np.asarray(raw[h])>0)) if raw[h] else None,
            "unconditional_median":base,
            "excess":(med-base) if med is not None and base is not None else None,
        }
    return out


def aggregate_event(per_symbol):
    out={}
    for h in (10,20):
        valid=[v[h] for v in per_symbol.values() if v[h]["n"]>0 and v[h]["excess"] is not None]
        excess=[x["excess"] for x in valid]
        absolute=[]
        for s,v in per_symbol.items():
            # use per-symbol median for absolute summary to avoid event-count domination
            if v[h]["n"]>0 and v[h]["absolute_median"] is not None:
                absolute.append(v[h]["absolute_median"])
        out[str(h)]={
            "event_count":int(sum(v[h]["n"] for v in per_symbol.values())),
            "symbol_count":len(valid),
            "cross_symbol_median_excess":float(np.median(excess)) if excess else None,
            "positive_excess_breadth":float(np.mean(np.asarray(excess)>0)) if excess else None,
            "negative_excess_breadth":float(np.mean(np.asarray(excess)<0)) if excess else None,
            "cross_symbol_median_absolute_return":float(np.median(absolute)) if absolute else None,
        }
    return out


def compact(x):
    return {k:v for k,v in x.items() if k not in {"dates","curve"}}


def pct(x):
    return "—" if x is None else f"{100*x:.2f}%"


def main():
    prior79={s for xs in core.BATCHES.values() for s in xs}
    prior=set(prior79)|set(state_study.OOS10)|set(r2.SYMBOLS)
    overlap=sorted(set(SYMBOLS)&prior)
    if overlap:
        raise RuntimeError(f"R3 overlaps prior research: {overlap}")
    if len(SYMBOLS)!=20 or len(set(SYMBOLS))!=20:
        raise RuntimeError("R3 must contain 20 unique stocks")

    DATA_DIR.mkdir(parents=True,exist_ok=True)
    manifest={
      "study":"PURE_SLTD_V8_PROBABILITY_MAP_R3",
      "symbols":SYMBOLS,
      "industries":dict(UNIVERSE),
      "provider":"Yahoo Finance via yfinance",
      "auto_adjust":False,
      "fetch_start":FETCH_START,
      "fetch_end_exclusive":FETCH_END_EXCLUSIVE,
      "formal_window":["2020-01-02","2026-09-30"],
      "prior_overlap":overlap,
      "files":{},
      "generated_at_utc":datetime.now(timezone.utc).isoformat(),
    }

    bars_by={};ledger_by={}
    for s,industry in UNIVERSE:
        frame=fetch_stock(s)
        if pd.Timestamp(frame["Date"].min())>=FORMAL_START:
            raise RuntimeError(f"{s}: no pre-2020 warmup")
        if pd.Timestamp(frame["Date"].max())<FORMAL_END:
            raise RuntimeError(f"{s}: data ends before formal end")
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
        systems[flabel]={"V7_BASE":{},"PMAP_14":{},"BUY_HOLD":{},"SMA200_TREND":{}}
        for s in SYMBOLS:
            bars=bars_by[s];ledger=ledger_by[s]
            base=r2.simulate_sltd(bars,ledger,bps,False)
            cand=r2.simulate_sltd(bars,ledger,bps,True)
            official=sltd.simulate_policy(bars,ledger,friction_bps=bps)
            if abs(float(official["final_equity"])-(1.0+base["total_return"]))>1e-9:
                raise RuntimeError(f"{s}: V7 baseline parity mismatch {flabel}")
            systems[flabel]["V7_BASE"][s]=base
            systems[flabel]["PMAP_14"][s]=cand
            systems[flabel]["BUY_HOLD"][s]=r2.simulate_buy_hold(bars,bps)
            systems[flabel]["SMA200_TREND"][s]=r2.simulate_sma200(bars,bps)

    portfolio={
      flabel:{label:r2.portfolio_metrics(vals) for label,vals in bysys.items()}
      for flabel,bysys in systems.items()
    }
    per_symbol={
      s:{flabel:{label:compact(systems[flabel][label][s]) for label in systems[flabel]}
         for flabel in systems}
      for s in SYMBOLS
    }

    buy_by={s:event_metrics(bars_by[s],ledger_by[s],r2.pm_buy) for s in SYMBOLS}
    sell_by={s:event_metrics(bars_by[s],ledger_by[s],r2.pm_sell) for s in SYMBOLS}
    buy_event=aggregate_event(buy_by)
    sell_event=aggregate_event(sell_by)

    base5=portfolio["5bps"]["V7_BASE"];cand5=portfolio["5bps"]["PMAP_14"]
    base10=portfolio["10bps"]["V7_BASE"];cand10=portfolio["10bps"]["PMAP_14"]
    trend5=portfolio["5bps"]["SMA200_TREND"]

    br_ret=sum(per_symbol[s]["5bps"]["PMAP_14"]["total_return"]>per_symbol[s]["5bps"]["V7_BASE"]["total_return"] for s in SYMBOLS)
    br_cal=sum(per_symbol[s]["5bps"]["PMAP_14"]["calmar"]>per_symbol[s]["5bps"]["V7_BASE"]["calmar"] for s in SYMBOLS)

    b10=buy_event["10"];b20=buy_event["20"];s10=sell_event["10"];s20=sell_event["20"]
    gates={
      "portfolio_5bps_return_gt_v7":cand5["total_return"]>base5["total_return"],
      "portfolio_5bps_calmar_gt_v7":cand5["calmar"]>base5["calmar"],
      "portfolio_5bps_maxdd_not_worse_gt_1pp":cand5["max_drawdown"]>=base5["max_drawdown"]-0.01,
      "symbol_return_breadth_ge_11":br_ret>=11,
      "symbol_calmar_breadth_ge_11":br_cal>=11,
      "portfolio_10bps_return_gt_v7":cand10["total_return"]>base10["total_return"],
      "portfolio_10bps_calmar_gt_v7":cand10["calmar"]>base10["calmar"],
      "buy_support":b10["event_count"]>=60 and b10["symbol_count"]>=10,
      "buy_excess_10_positive":b10["cross_symbol_median_excess"] is not None and b10["cross_symbol_median_excess"]>0,
      "buy_excess_20_positive":b20["cross_symbol_median_excess"] is not None and b20["cross_symbol_median_excess"]>0,
      "buy_breadth_10_ge_60":b10["positive_excess_breadth"] is not None and b10["positive_excess_breadth"]>=0.60,
      "buy_breadth_20_ge_60":b20["positive_excess_breadth"] is not None and b20["positive_excess_breadth"]>=0.60,
      "sell_support":s10["event_count"]>=100 and s10["symbol_count"]>=12,
      "sell_excess_10_negative":s10["cross_symbol_median_excess"] is not None and s10["cross_symbol_median_excess"]<0,
      "sell_excess_20_negative":s20["cross_symbol_median_excess"] is not None and s20["cross_symbol_median_excess"]<0,
      "sell_breadth_10_ge_60":s10["negative_excess_breadth"] is not None and s10["negative_excess_breadth"]>=0.60,
      "sell_breadth_20_ge_60":s20["negative_excess_breadth"] is not None and s20["negative_excess_breadth"]>=0.60,
      "simple_baseline_guard":(
        cand5["calmar"]>trend5["calmar"]
        or (cand5["total_return"]>trend5["total_return"] and cand5["max_drawdown"]>=trend5["max_drawdown"])
      ),
    }

    if all(gates.values()):
        decision="PROMOTE_TO_ENGINEERING_CANDIDATE"
    elif not gates["portfolio_5bps_return_gt_v7"] or not gates["portfolio_5bps_calmar_gt_v7"]:
        decision="REJECTED_NOT_ADMITTED"
    else:
        decision="RESEARCH_ONLY_NOT_PROMOTED"

    out={
      "meta":{
        "study":"PURE_SLTD_V8_PROBABILITY_MAP_R3","status":"COMPLETE",
        "protocol":"PURE_SLTD_V8_PROBABILITY_MAP_R3_PROTOCOL_v1.md",
        "chan_used":False,
        "candidate_rules":[r2.PM_BUY_ID,r2.PM_SELL_ID],
        "universe":UNIVERSE,"prior_overlap":overlap,
        "formal_window":"2020-01-02..2026-09-30",
        "generated_at_utc":datetime.now(timezone.utc).isoformat(),
      },
      "portfolio":portfolio,
      "breadth_5bps":{"return_better":br_ret,"calmar_better":br_cal},
      "event_validation":{"PM_BUY_1":buy_event,"PM_SELL_1":sell_event},
      "gates":gates,"decision":decision,
      "per_symbol":per_symbol,
    }
    OUT_JSON.write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding="utf-8")

    lines=["# Pure SLTD V8 Probability-Map Candidate R3 — Result","",
           "Status: **COMPLETE**","",f"Decision: **{decision}**","",
           "## Equal-weight portfolio — 5 bps","",
           "| System | Return | CAGR | MaxDD | Calmar | Turnover | Exposure |",
           "|---|---:|---:|---:|---:|---:|---:|"]
    for label in ("V7_BASE","PMAP_14","BUY_HOLD","SMA200_TREND"):
        m=portfolio["5bps"][label]
        lines.append(f"| {label} | {pct(m['total_return'])} | {pct(m['cagr'])} | {pct(m['max_drawdown'])} | {m['calmar']:.3f} | {m['turnover_mean']:.2f} | {pct(m['time_in_market_mean'])} |")
    lines+=["","## Breadth","",f"- Return better than V7: **{br_ret}/20**",f"- Calmar better than V7: **{br_cal}/20**","",
            "## Drift-adjusted event validation","",
            f"- PM_BUY_1: n={b10['event_count']}, symbols={b10['symbol_count']}, 10d excess={pct(b10['cross_symbol_median_excess'])}, breadth={pct(b10['positive_excess_breadth'])}; 20d excess={pct(b20['cross_symbol_median_excess'])}, breadth={pct(b20['positive_excess_breadth'])}",
            f"- PM_SELL_1: n={s10['event_count']}, symbols={s10['symbol_count']}, 10d excess={pct(s10['cross_symbol_median_excess'])}, negative breadth={pct(s10['negative_excess_breadth'])}; 20d excess={pct(s20['cross_symbol_median_excess'])}, negative breadth={pct(s20['negative_excess_breadth'])}","",
            "## Gates",""]
    for k,v in gates.items():
        lines.append(f"- {k}: **{'PASS' if v else 'FAIL'}**")
    lines+=["","Existing V7 remains unchanged unless R3 is promoted and separately engineered.","",f"PURE_SLTD_V8_PROBABILITY_MAP_R3 = {decision}",""]
    OUT_MD.write_text("\n".join(lines),encoding="utf-8")

    print(json.dumps({
      "decision":decision,
      "portfolio_5bps":{k:compact(v) for k,v in portfolio["5bps"].items()},
      "portfolio_10bps":{k:compact(v) for k,v in portfolio["10bps"].items()},
      "breadth_5bps":out["breadth_5bps"],
      "event_validation":out["event_validation"],
      "gates":gates,
    },indent=2,ensure_ascii=False))


if __name__=="__main__":
    main()
