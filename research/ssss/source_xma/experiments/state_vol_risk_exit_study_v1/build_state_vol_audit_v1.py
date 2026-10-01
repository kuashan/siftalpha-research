#!/usr/bin/env python3
import csv, json, math, random, statistics
from pathlib import Path

HERE=Path(__file__).resolve().parent
SEED=20261001
BOOT_N=5000
CONFIGS=["BASELINE","ATR2_ONLY","ATR3_ONLY","LOSS2_MOD","LOSS3_MOD","LOSS2_SEV","PEAK2_MOD","PEAK3_MOD","HYBRID25_MOD","CONFIRM_ADAPT","LOSS4_SEV"]
FORMAL=CONFIGS[3:]
STOCK_EXPECT=["AAPL","MSFT","NVDA","AMD","AVGO","ORCL","INTC","QCOM","MU","GOOGL","META","NFLX","AMZN","TSLA","HD","MCD","WMT","COST","PG","KO","PEP","ABT","LLY","UNH","JNJ","TMO","JPM","BAC","GS","V","MA","CAT","BA","GE","XOM","CVX","LIN","NEE","PLD"]
CRYPTO_EXPECT=["BTC","ETH","BNB","SOL"]

def load(p): return json.loads(Path(p).read_text())
def finite(xs): return [x for x in xs if isinstance(x,(int,float)) and math.isfinite(x)]
def mean(xs):
    a=finite(xs); return statistics.fmean(a) if a else None
def median(xs):
    a=finite(xs); return statistics.median(a) if a else None
def q(xs,p):
    a=sorted(finite(xs))
    if not a:return None
    z=(len(a)-1)*p; lo=math.floor(z); hi=math.ceil(z)
    return a[lo]+(a[hi]-a[lo])*(z-lo)
def wmean(rows,val_key,n_key):
    pairs=[(r.get(val_key),r.get(n_key,0)) for r in rows]
    pairs=[(v,n) for v,n in pairs if isinstance(v,(int,float)) and math.isfinite(v) and n]
    return sum(v*n for v,n in pairs)/sum(n for v,n in pairs) if pairs else None
def cfgmap(a): return {c["config"]:c for c in a["configs"]}

stocks=[]
for i in range(1,7):
    stocks.extend(load(HERE/f"stock_state_vol_batch{i}_v1.json")["results"])
crypto=load(HERE/"crypto_state_vol_results_v1.json")["results"]
assert [a["symbol"] for a in stocks]==STOCK_EXPECT
assert [a["symbol"] for a in crypto]==CRYPTO_EXPECT
for a in stocks+crypto:
    assert [c["config"] for c in a["configs"]]==CONFIGS, a["symbol"]

old_stock={}
for i in range(1,11):
    p=HERE.parent/"stock_risk_exit_study_v1"/f"stock_risk_batch{i}_v1_1.json"
    for a in load(p)["results"]:
        old_stock[a["symbol"]]=cfgmap(a)["BASELINE"]
crypto_repro=load(HERE/"CRYPTO_BASELINE_REPRO_v1.json")
assert crypto_repro["status"]=="PASS"
tol=1e-9
audit=[]
for a in stocks:
    n=cfgmap(a)["BASELINE"]; o=old_stock[a["symbol"]]
    d={k:n[k]-o[k] for k in ["return","close_mdd","intra_mdd","win","p5","cvar10","worst","exposure"]}
    d["trades"]=n["trades"]-o["trades"]
    audit.append({"asset_class":"stock","symbol":a["symbol"],**d})
assert all(max(abs(v) for k,v in r.items() if k not in ("asset_class","symbol"))<=tol for r in audit)
for r in crypto_repro["audit"]:
    audit.append({"asset_class":"crypto",**r})
assert all(max(abs(v) for k,v in r.items() if k not in ("asset_class","symbol"))<=tol for r in audit)

with (HERE/"BASELINE_REPRO_AUDIT_v1.md").open("w") as f:
    f.write("# State / Volatility-Aware Risk Exit Baseline Reproduction Audit v1\n\n")
    f.write("Status: **PASS**\n\n")
    f.write(f"Tolerance: {tol}\n\n")
    f.write("- Stocks: 39/39 reproduced against corrected Stock Risk Exit v1.1 baseline.\n")
    f.write("- Crypto: BTC / ETH / BNB / SOL reproduced exactly against frozen Crypto Risk Exit v1 baseline.\n")
    for cls in ("stock","crypto"):
        rr=[r for r in audit if r["asset_class"]==cls]
        f.write(f"- {cls} max |return diff|: {max(abs(r['return']) for r in rr):.18g}\n")
        f.write(f"- {cls} max |trades diff|: {max(abs(r['trades']) for r in rr):.18g}\n")
    f.write("\nSTATE_VOL_BASELINE_REPRODUCTION = PASS\n")

groups={"stock":stocks,"crypto":crypto}
per=[]; summary=[]; boot=[]; period=[]
for cls,assets in groups.items():
    maps={a["symbol"]:cfgmap(a) for a in assets}
    for a in assets:
        b=maps[a["symbol"]]["BASELINE"]
        for name in CONFIGS:
            r=maps[a["symbol"]][name]
            per.append({
                "asset_class":cls,"symbol":a["symbol"],"config":name,
                "return":r["return"],"return_delta":r["return"]-b["return"],
                "close_mdd":r["close_mdd"],"close_mdd_improvement":r["close_mdd"]-b["close_mdd"],
                "intra_mdd":r["intra_mdd"],"mdd_improvement":r["intra_mdd"]-b["intra_mdd"],
                "p5":r["p5"],"p5_delta":r["p5"]-b["p5"],
                "cvar10":r["cvar10"],"cvar_delta":r["cvar10"]-b["cvar10"],
                "worst":r["worst"],"worst_delta":r["worst"]-b["worst"],
                "win":r["win"],"trades":r["trades"],"exposure":r["exposure"],
                "risk_exits":r.get("risk_exits",0),"matched_stops":r.get("matched_stops",0),
                "killed_winners":r.get("killed_winners",0),"saved_losers":r.get("saved_losers",0),
                "confirmed_matched_stops":r.get("confirmed_matched_stops",0),
                "confirmed_mean_delta":r.get("confirmed_mean_delta"),
                "preconfirm_matched_stops":r.get("preconfirm_matched_stops",0),
                "preconfirm_mean_delta":r.get("preconfirm_mean_delta"),
            })
    for name in CONFIGS:
        rows=[maps[a["symbol"]][name] for a in assets]
        bases=[maps[a["symbol"]]["BASELINE"] for a in assets]
        deltas=[{"ret":r["return"]-b["return"],"mdd":r["intra_mdd"]-b["intra_mdd"],"p5":r["p5"]-b["p5"],"cv":r["cvar10"]-b["cvar10"],"worst":r["worst"]-b["worst"]} for r,b in zip(rows,bases)]
        base_mean_ret=mean([b["return"] for b in bases]); cand_mean_ret=mean([r["return"] for r in rows])
        sr={
            "asset_class":cls,"config":name,"n_assets":len(assets),
            "baseline_mean_return":base_mean_ret,"mean_return":cand_mean_ret,"median_return":median([r["return"] for r in rows]),
            "mean_return_delta":mean([d["ret"] for d in deltas]),"return_preservation_ratio":cand_mean_ret/base_mean_ret if base_mean_ret and base_mean_ret>0 else None,
            "return_improve_n":sum(d["ret"]>0 for d in deltas),
            "mean_close_mdd":mean([r["close_mdd"] for r in rows]),"mean_intra_mdd":mean([r["intra_mdd"] for r in rows]),
            "mean_mdd_improvement":mean([d["mdd"] for d in deltas]),"mdd_improve_n":sum(d["mdd"]>0 for d in deltas),
            "mean_p5":mean([r["p5"] for r in rows]),"mean_p5_delta":mean([d["p5"] for d in deltas]),"p5_improve_n":sum(d["p5"]>=0 for d in deltas),
            "mean_cvar10":mean([r["cvar10"] for r in rows]),"mean_cvar_delta":mean([d["cv"] for d in deltas]),"cvar_improve_n":sum(d["cv"]>=0 for d in deltas),
            "mean_worst":mean([r["worst"] for r in rows]),"mean_worst_delta":mean([d["worst"] for d in deltas]),
            "mean_exposure":mean([r["exposure"] for r in rows]),"total_trades":sum(r["trades"] for r in rows),"total_risk_exits":sum(r.get("risk_exits",0) for r in rows),
            "matched_stops":sum(r.get("matched_stops",0) for r in rows),"killed_winners":sum(r.get("killed_winners",0) for r in rows),"saved_losers":sum(r.get("saved_losers",0) for r in rows),
            "killed_winner_opportunity_cost":wmean(rows,"killed_winner_opportunity_cost","killed_winners"),"saved_loser_improvement":wmean(rows,"saved_loser_improvement","saved_losers"),
            "confirmed_matched_stops":sum(r.get("confirmed_matched_stops",0) for r in rows),"confirmed_baseline_winners":sum(r.get("confirmed_baseline_winners",0) for r in rows),
            "confirmed_mean_delta":wmean(rows,"confirmed_mean_delta","confirmed_matched_stops"),"preconfirm_matched_stops":sum(r.get("preconfirm_matched_stops",0) for r in rows),
            "preconfirm_mean_delta":wmean(rows,"preconfirm_mean_delta","preconfirm_matched_stops"),
        }
        summary.append(sr)
        if name!="BASELINE":
            metric_vals={"return_delta":[d["ret"] for d in deltas],"mdd_improvement":[d["mdd"] for d in deltas],"p5_delta":[d["p5"] for d in deltas],"cvar_delta":[d["cv"] for d in deltas]}
            for mi,(metric,vals) in enumerate(metric_vals.items()):
                rng=random.Random(SEED + (0 if cls=="stock" else 100000) + CONFIGS.index(name)*100 + mi)
                sims=[]; n=len(vals)
                for _ in range(BOOT_N): sims.append(mean([vals[rng.randrange(n)] for __ in range(n)]))
                boot.append({"asset_class":cls,"config":name,"metric":metric,"point_mean":mean(vals),"ci95_low":q(sims,.025),"ci95_high":q(sims,.975),"seed":SEED,"bootstrap_n":BOOT_N})
    periods=["2010-2014","2015-2019","2020-2026"] if cls=="stock" else ["2017-2020","2021-2023","2024-2026"]
    for name in CONFIGS:
        rows=[maps[a["symbol"]][name] for a in assets]
        for label in periods:
            ns=[r.get(f"period_{label}_n",0) or 0 for r in rows]; ds=[r.get(f"period_{label}_delta") for r in rows]
            valid=[d for d,n in zip(ds,ns) if n and isinstance(d,(int,float)) and math.isfinite(d)]
            events=sum(ns); ew=sum(d*n for d,n in zip(ds,ns) if n and isinstance(d,(int,float)) and math.isfinite(d))/events if events else None
            period.append({"asset_class":cls,"config":name,"period":label,"assets_with_events":sum(n>0 for n in ns),"events":events,"asset_mean_delta":mean(valid),"event_weighted_delta":ew,"killed_winners":sum((r.get(f"period_{label}_killed",0) or 0) for r in rows)})

def write_csv(path,rows):
    fields=list(rows[0].keys())
    with path.open("w",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
write_csv(HERE/"STATE_VOL_PER_ASSET_v1.csv",per)
write_csv(HERE/"STATE_VOL_CONFIG_SUMMARY_v1.csv",summary)
write_csv(HERE/"STATE_VOL_BOOTSTRAP_v1.csv",boot)
write_csv(HERE/"STATE_VOL_PERIOD_DIAGNOSTICS_v1.csv",period)

summap={(r["asset_class"],r["config"]):r for r in summary}
bootmap={(r["asset_class"],r["config"],r["metric"]):r for r in boot}

def crypto_dominance(name):
    amap={a["symbol"]:cfgmap(a) for a in crypto}
    deltas={s:amap[s][name]["return"]-amap[s]["BASELINE"]["return"] for s in CRYPTO_EXPECT}
    omit=max(CRYPTO_EXPECT,key=lambda s:deltas[s]); keep=[s for s in CRYPTO_EXPECT if s!=omit]
    cr=[amap[s][name] for s in keep]; br=[amap[s]["BASELINE"] for s in keep]
    cm=mean([r["return"] for r in cr]); bm=mean([r["return"] for r in br])
    vals={"omitted_coin":omit,"remaining_return_preservation_ratio":cm/bm if bm and bm>0 else None,
          "remaining_mean_mdd_improvement":mean([r["intra_mdd"]-b["intra_mdd"] for r,b in zip(cr,br)]),
          "remaining_mean_p5_delta":mean([r["p5"]-b["p5"] for r,b in zip(cr,br)]),
          "remaining_mean_cvar_delta":mean([r["cvar10"]-b["cvar10"] for r,b in zip(cr,br)])}
    vals["pass"]=vals["remaining_return_preservation_ratio"]>=.90 and vals["remaining_mean_mdd_improvement"]>0 and vals["remaining_mean_p5_delta"]>=0 and vals["remaining_mean_cvar_delta"]>=0
    return vals

admission={"seed":SEED,"bootstrap_n":BOOT_N,"formal_candidates":FORMAL,"stock":{},"crypto":{},"universal":[]}
for name in FORMAL:
    s=summap[("stock",name)]; ci=bootmap[("stock",name,"mdd_improvement")]
    sg={"mean_mdd_improvement_positive":s["mean_mdd_improvement"]>0,"mdd_bootstrap_ci_low_positive":ci["ci95_low"]>0,
        "return_preservation_ge_90pct":s["return_preservation_ratio"]>=.90,"p5_not_worse":s["mean_p5_delta"]>=0,"cvar_not_worse":s["mean_cvar_delta"]>=0,
        "mdd_improve_ge_24_of_39":s["mdd_improve_n"]>=24,"killed_not_gt_saved":s["killed_winners"]<=s["saved_losers"],
        "confirmed_no_negative_penalty":s["confirmed_matched_stops"]==0 or (s["confirmed_mean_delta"] is not None and s["confirmed_mean_delta"]>=0)}
    sg["pass"]=all(sg.values()); admission["stock"][name]=sg
    c=summap[("crypto",name)]; dom=crypto_dominance(name)
    cg={"mean_mdd_improvement_positive":c["mean_mdd_improvement"]>0,"mdd_improve_ge_3_of_4":c["mdd_improve_n"]>=3,
        "return_preservation_ge_90pct":c["return_preservation_ratio"]>=.90,"p5_not_worse":c["mean_p5_delta"]>=0,"cvar_not_worse":c["mean_cvar_delta"]>=0,
        "killed_not_gt_saved":c["killed_winners"]<=c["saved_losers"],
        "confirmed_no_negative_penalty":c["confirmed_matched_stops"]==0 or (c["confirmed_mean_delta"] is not None and c["confirmed_mean_delta"]>=0),
        "single_coin_dominance_gate":dom["pass"],"dominance_detail":dom}
    cg["pass"]=all(v for k,v in cg.items() if k not in ("dominance_detail","pass")); admission["crypto"][name]=cg
    if sg["pass"] and cg["pass"]: admission["universal"].append(name)

stock_pass=[k for k,v in admission["stock"].items() if v["pass"]]
crypto_pass=[k for k,v in admission["crypto"].items() if v["pass"]]
admission["stock_pass"]=stock_pass; admission["crypto_pass"]=crypto_pass
admission["decision"]={"STOCK_RISK_EXIT":"PROMOTED_TO_NEXT_VALIDATION" if stock_pass else "NOT_USED_RETAIN_BASELINE",
                       "CRYPTO_RISK_EXIT":"PROMOTED_TO_NEXT_VALIDATION" if crypto_pass else "NOT_USED_RETAIN_BASELINE",
                       "UNIVERSAL_STATE_VOL_RISK_EXIT":"PROMOTED_TO_NEXT_VALIDATION" if admission["universal"] else "REJECTED_NOT_ADMITTED",
                       "RISK_EXIT_LAYER":"PROMOTED_TO_NEXT_VALIDATION" if (stock_pass or crypto_pass) else "NOT_USED_RETAIN_BASELINES"}
(HERE/"STATE_VOL_ADMISSION_v1.json").write_text(json.dumps(admission,indent=2)+"\n")

with (HERE/"STATE_VOL_RISK_STATISTICAL_AUDIT_v1.md").open("w") as f:
    f.write("# State / Volatility-Aware Risk Exit Statistical Audit v1\n\nStatus: **IMPLEMENTED_AND_VERIFIED**\n\n")
    f.write(f"Bootstrap: {BOOT_N} deterministic asset-level resamples, seed {SEED}.\n\n")
    for cls in ("stock","crypto"):
        b=summap[(cls,"BASELINE")]
        f.write(f"## {cls.title()} baseline\n\n- assets: {b['n_assets']}\n- mean cumulative return: {b['mean_return']*100:.2f}%\n- mean intraday-low MDD: {b['mean_intra_mdd']*100:.2f}%\n- mean P5: {b['mean_p5']*100:.2f}%\n- mean CVaR10: {b['mean_cvar10']*100:.2f}%\n\n")
        f.write("## Formal candidates\n\n| Candidate | Return | Retain | MDD imp | MDD n | P5 d | CVaR d | Killed/Saved | Confirm d | Gate |\n|---|---:|---:|---:|---:|---:|---:|---:|---:|---|\n")
        for name in FORMAL:
            s=summap[(cls,name)]; g=admission[cls][name]; cd=s["confirmed_mean_delta"]; cdtext="" if cd is None else f"{cd*100:+.2f}pp"
            f.write(f"| {name} | {s['mean_return']*100:.2f}% | {s['return_preservation_ratio']*100:.1f}% | {s['mean_mdd_improvement']*100:+.2f}pp | {s['mdd_improve_n']}/{s['n_assets']} | {s['mean_p5_delta']*100:+.2f}pp | {s['mean_cvar_delta']*100:+.2f}pp | {s['killed_winners']}/{s['saved_losers']} | {cdtext} | {'PASS' if g['pass'] else 'FAIL'} |\n")
        f.write("\n")
    f.write("## Decision\n\n")
    for k,v in admission["decision"].items(): f.write(f"- {k} = {v}\n")
    f.write("\nFormal candidates only are eligible for promotion. ATR2_ONLY / ATR3_ONLY are diagnostic controls.\n")
print(json.dumps({"status":"PASS","stocks":len(stocks),"crypto":len(crypto),"stock_pass":stock_pass,"crypto_pass":crypto_pass,"universal":admission["universal"],"decision":admission["decision"]}))
