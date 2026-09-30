#!/usr/bin/env python3
import csv, hashlib, json, math, random, statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
STOCK_FILES = [HERE / f"stock_batch{i}_v1.json" for i in (1,2,3)]
CRYPTO_FILE = HERE / "crypto_batch_v1.json"
CRYPTO_KEEP = ["BTC","ETH","BNB","SOL"]
STOCK_EXPECT = [
"AAPL","MSFT","NVDA","AMD","AVGO","ORCL","INTC","QCOM","MU","GOOGL","META","NFLX","AMZN","TSLA","HD",
"MCD","WMT","COST","PG","KO","PEP","ABT","LLY","UNH","JNJ","TMO","JPM","BAC","GS","V","MA","CAT","BA",
"GE","XOM","CVX","LIN","NEE","PLD"]
SEED = 20260930
BOOT_N = 5000

def load(path):
    return json.loads(path.read_text())

def pct(x):
    return None if x is None else x*100.0

def finite(xs):
    return [x for x in xs if isinstance(x,(int,float)) and math.isfinite(x)]

def mean(xs):
    a=finite(xs); return statistics.fmean(a) if a else None

def median(xs):
    a=finite(xs); return statistics.median(a) if a else None

def quantile(xs,q):
    a=sorted(finite(xs))
    if not a: return None
    if len(a)==1: return a[0]
    p=(len(a)-1)*q; lo=math.floor(p); hi=math.ceil(p)
    return a[lo] + (a[hi]-a[lo])*(p-lo)

def cvar10(xs):
    a=sorted(finite(xs))
    if not a: return None
    n=max(1, math.ceil(len(a)*0.1))
    return statistics.fmean(a[:n])

def fmt(x):
    return "" if x is None else f"{x:.6f}"

def cfgmap(asset):
    return {c["name"]:c for c in asset["configs"]}

stocks=[]
for p in STOCK_FILES:
    stocks.extend(load(p)["results"])
crypto_all=load(CRYPTO_FILE)["results"]
crypto=[a for a in crypto_all if a["symbol"] in CRYPTO_KEEP]

assert len(stocks)==39, len(stocks)
assert [a["symbol"] for a in stocks] == STOCK_EXPECT
assert len(crypto)==4 and [a["symbol"] for a in crypto] == CRYPTO_KEEP
assets=stocks+crypto

cfg_names=[c["name"] for c in assets[0]["configs"]]
assert len(cfg_names)==16, cfg_names
for a in assets:
    assert [c["name"] for c in a["configs"]]==cfg_names, a["symbol"]

# Input manifest and filtered crypto archive.
manifest={
    "status":"INPUTS_VERIFIED",
    "stock_assets":len(stocks),
    "crypto_assets":len(crypto),
    "total_assets":len(assets),
    "crypto_universe":CRYPTO_KEEP,
    "config_count_per_asset":16,
    "files":{}
}
for p in STOCK_FILES+[CRYPTO_FILE]:
    b=p.read_bytes()
    manifest["files"][p.name]={"sha256":hashlib.sha256(b).hexdigest(),"bytes":len(b)}
(HERE/"FIVEGZ5SE_STAGED_ENTRY_43_ASSET_INPUT_MANIFEST_v2.json").write_text(json.dumps(manifest,indent=2)+"\n")
(HERE/"crypto_batch4_v2.json").write_text(json.dumps({"assetClass":"crypto","results":crypto},separators=(",",":"))+"\n")

# All-config per-asset table.
per_fields=[
"asset_class","symbol","start","end","sessions","policy","window","exit_policy","initial_pct",
"return_pct","mdd_pct","win_pct","avg_trade_pct","median_trade_pct","p10_trade_pct","p5_trade_pct",
"worst_trade_pct","cvar10_pct","exposure_pct","trades","confirmations","open_at_end",
"return_delta_vs_base_pp","mdd_improvement_vs_base_pp","p5_improvement_vs_base_pp","cvar10_improvement_vs_base_pp"
]
per_rows=[]
for a in assets:
    cm=cfgmap(a)
    for c in a["configs"]:
        r=c["r"]; base=cm[f'BASE_100_{c["exit"]}_W{c["w"]}']["r"]
        row={
            "asset_class":a["assetClass"],"symbol":a["symbol"],"start":a["start"],"end":a["end"],"sessions":a["sessions"],
            "policy":c["name"],"window":c["w"],"exit_policy":c["exit"],"initial_pct":round(c["initial"]*100),
            "return_pct":pct(r["return"]),"mdd_pct":pct(r["mdd"]),"win_pct":pct(r["win"]),
            "avg_trade_pct":pct(r["avg_trade"]),"median_trade_pct":pct(r["median_trade"]),
            "p10_trade_pct":pct(r["p10_trade"]),"p5_trade_pct":pct(r["p5_trade"]),
            "worst_trade_pct":pct(r["worst_trade"]),"cvar10_pct":pct(r["cvar10"]),
            "exposure_pct":pct(r["exposure"]),"trades":r["trades"],"confirmations":r["confirmations"],
            "open_at_end":1 if r["open_at_end"] else 0,
            "return_delta_vs_base_pp":pct(r["return"]-base["return"]),
            "mdd_improvement_vs_base_pp":pct(r["mdd"]-base["mdd"]),
            "p5_improvement_vs_base_pp":pct((r["p5_trade"] or 0)-(base["p5_trade"] or 0)) if r["p5_trade"] is not None and base["p5_trade"] is not None else None,
            "cvar10_improvement_vs_base_pp":pct((r["cvar10"] or 0)-(base["cvar10"] or 0)) if r["cvar10"] is not None and base["cvar10"] is not None else None,
        }
        per_rows.append(row)
with (HERE/"FIVEGZ5SE_STAGED_ENTRY_43_ASSET_ALL_CONFIGS_v2.csv").open("w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=per_fields); w.writeheader()
    for r in per_rows: w.writerow({k:(fmt(v) if isinstance(v,float) else v) for k,v in r.items()})

groups={"stocks":stocks,"crypto":crypto,"combined":assets}
summary_fields=[
"group","policy","n_assets","mean_return_pct","median_return_pct","mean_mdd_pct","median_mdd_pct",
"mean_win_pct","median_win_pct","mean_avg_trade_pct","median_trade_pct","mean_p10_trade_pct","mean_p5_trade_pct",
"mean_cvar10_pct","worst_trade_pct","mean_exposure_pct","total_confirmations","open_positions",
"mean_return_delta_vs_base_pp","median_return_delta_vs_base_pp","return_improved","return_deteriorated",
"mean_mdd_improvement_pp","median_mdd_improvement_pp","mdd_improved","mdd_deteriorated",
"mean_p5_improvement_pp","p5_improved","p5_deteriorated",
"mean_cvar10_improvement_pp","cvar10_improved","cvar10_deteriorated"
]
summary=[]
for gname,alist in groups.items():
    for name in cfg_names:
        vals=[]; deltas=[]
        for a in alist:
            cm=cfgmap(a); c=cm[name]; r=c["r"]; base=cm[f'BASE_100_{c["exit"]}_W{c["w"]}']["r"]
            vals.append(r)
            deltas.append({
                "ret":pct(r["return"]-base["return"]),
                "mdd":pct(r["mdd"]-base["mdd"]),
                "p5":pct(r["p5_trade"]-base["p5_trade"]) if r["p5_trade"] is not None and base["p5_trade"] is not None else None,
                "cv":pct(r["cvar10"]-base["cvar10"]) if r["cvar10"] is not None and base["cvar10"] is not None else None,
            })
        rr=[pct(v["return"]) for v in vals]; mm=[pct(v["mdd"]) for v in vals]; ww=[pct(v["win"]) for v in vals]
        avg=[pct(v["avg_trade"]) for v in vals]; med=[pct(v["median_trade"]) for v in vals]
        p10=[pct(v["p10_trade"]) for v in vals]; p5=[pct(v["p5_trade"]) for v in vals]; cv=[pct(v["cvar10"]) for v in vals]
        worst=[pct(v["worst_trade"]) for v in vals]; exp=[pct(v["exposure"]) for v in vals]
        dr=[d["ret"] for d in deltas]; dm=[d["mdd"] for d in deltas]; dp=[d["p5"] for d in deltas]; dc=[d["cv"] for d in deltas]
        summary.append({
            "group":gname,"policy":name,"n_assets":len(alist),
            "mean_return_pct":mean(rr),"median_return_pct":median(rr),"mean_mdd_pct":mean(mm),"median_mdd_pct":median(mm),
            "mean_win_pct":mean(ww),"median_win_pct":median(ww),"mean_avg_trade_pct":mean(avg),"median_trade_pct":median(med),
            "mean_p10_trade_pct":mean(p10),"mean_p5_trade_pct":mean(p5),"mean_cvar10_pct":mean(cv),"worst_trade_pct":min(finite(worst)) if finite(worst) else None,
            "mean_exposure_pct":mean(exp),"total_confirmations":sum(v["confirmations"] for v in vals),"open_positions":sum(bool(v["open_at_end"]) for v in vals),
            "mean_return_delta_vs_base_pp":mean(dr),"median_return_delta_vs_base_pp":median(dr),
            "return_improved":sum(x>0 for x in finite(dr)),"return_deteriorated":sum(x<0 for x in finite(dr)),
            "mean_mdd_improvement_pp":mean(dm),"median_mdd_improvement_pp":median(dm),
            "mdd_improved":sum(x>0 for x in finite(dm)),"mdd_deteriorated":sum(x<0 for x in finite(dm)),
            "mean_p5_improvement_pp":mean(dp),"p5_improved":sum(x>0 for x in finite(dp)),"p5_deteriorated":sum(x<0 for x in finite(dp)),
            "mean_cvar10_improvement_pp":mean(dc),"cvar10_improved":sum(x>0 for x in finite(dc)),"cvar10_deteriorated":sum(x<0 for x in finite(dc)),
        })
with (HERE/"FIVEGZ5SE_STAGED_ENTRY_43_ASSET_SUMMARY_v2.csv").open("w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=summary_fields); w.writeheader()
    for r in summary: w.writerow({k:(fmt(v) if isinstance(v,float) else v) for k,v in r.items()})

# Tail-risk focused table.
tail_fields=["group","policy","n_assets","mean_p10_trade_pct","mean_p5_trade_pct","mean_cvar10_pct","worst_trade_pct","median_mdd_pct","mean_mdd_pct","p5_improved","cvar10_improved","mdd_improved"]
with (HERE/"FIVEGZ5SE_STAGED_ENTRY_43_ASSET_TAIL_RISK_v2.csv").open("w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=tail_fields); w.writeheader()
    for r in summary:
        w.writerow({k:r[k] for k in tail_fields})

# Confirmation event table: classify baseline FULL_FIRST trades using the corresponding staged 50% trade's confirmed flag.
event_fields=["asset_class","symbol","window","entry_signal","entry_date","entry_family","confirmed","exit_date","baseline_return_pct","days"]
events=[]
for a in assets:
    cm=cfgmap(a)
    for window in (3,5):
        base=cm[f"BASE_100_FULL_FIRST_W{window}"]["r"]["trade_details"]
        stage=cm[f"INIT_50_C_W{window}_FULL_FIRST"]["r"]["trade_details"]
        sk={(t["entry_signal"],t["entry_date"],t["exit_date"]):t for t in stage}
        for t in base:
            key=(t["entry_signal"],t["entry_date"],t["exit_date"])
            st=sk.get(key)
            assert st is not None, (a["symbol"],window,key)
            events.append({
                "asset_class":a["assetClass"],"symbol":a["symbol"],"window":window,
                "entry_signal":t["entry_signal"],"entry_date":t["entry_date"],"entry_family":t["entry_family"],
                "confirmed":1 if st["confirmed"] else 0,"exit_date":t["exit_date"],"baseline_return_pct":pct(t["ret"]),"days":t["days"]
            })
with (HERE/"FIVEGZ5SE_C_CONFIRMATION_EVENTS_43_ASSET_v2.csv").open("w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=event_fields); w.writeheader()
    for r in events: w.writerow({k:(fmt(v) if isinstance(v,float) else v) for k,v in r.items()})

acc_fields=["group","window","confirmation_group","n","mean_trade_pct","median_trade_pct","win_pct","p10_trade_pct","p5_trade_pct","cvar10_pct","worst_trade_pct"]
acc=[]
for gname in ("stocks","crypto","combined"):
    pool=[e for e in events if gname=="combined" or e["asset_class"]==("stock" if gname=="stocks" else "crypto")]
    for window in (3,5):
        for flag,label in ((1,"confirmed"),(0,"unconfirmed")):
            vals=[e["baseline_return_pct"] for e in pool if e["window"]==window and e["confirmed"]==flag]
            acc.append({"group":gname,"window":window,"confirmation_group":label,"n":len(vals),
                        "mean_trade_pct":mean(vals),"median_trade_pct":median(vals),
                        "win_pct":100*sum(x>0 for x in vals)/len(vals) if vals else None,
                        "p10_trade_pct":quantile(vals,.10),"p5_trade_pct":quantile(vals,.05),
                        "cvar10_pct":cvar10(vals),"worst_trade_pct":min(vals) if vals else None})
with (HERE/"FIVEGZ5SE_C_CONFIRMATION_ACCURACY_43_ASSET_v2.csv").open("w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=acc_fields); w.writeheader()
    for r in acc: w.writerow({k:(fmt(v) if isinstance(v,float) else v) for k,v in r.items()})

# Bootstrap asset-level deltas against matching 100% baseline.
boot_fields=["group","policy","metric","point_mean","ci95_mean_low","ci95_mean_high","point_median","ci95_median_low","ci95_median_high","seed","bootstrap_n"]
boot=[]
rng=random.Random(SEED)
metrics={"return_delta_pp":"ret","mdd_improvement_pp":"mdd","p5_improvement_pp":"p5","cvar10_improvement_pp":"cv"}
for gname,alist in groups.items():
    for name in cfg_names:
        rows=[]
        for a in alist:
            cm=cfgmap(a); c=cm[name]; r=c["r"]; b=cm[f'BASE_100_{c["exit"]}_W{c["w"]}']["r"]
            rows.append({
                "ret":pct(r["return"]-b["return"]),
                "mdd":pct(r["mdd"]-b["mdd"]),
                "p5":pct(r["p5_trade"]-b["p5_trade"]) if r["p5_trade"] is not None and b["p5_trade"] is not None else None,
                "cv":pct(r["cvar10"]-b["cvar10"]) if r["cvar10"] is not None and b["cvar10"] is not None else None,
            })
        n=len(rows)
        for metric,key in metrics.items():
            vals=[r[key] for r in rows]
            if not finite(vals): continue
            bm=[]; bd=[]
            for _ in range(BOOT_N):
                samp=[vals[rng.randrange(n)] for __ in range(n)]
                bm.append(mean(samp)); bd.append(median(samp))
            boot.append({"group":gname,"policy":name,"metric":metric,
                         "point_mean":mean(vals),"ci95_mean_low":quantile(bm,.025),"ci95_mean_high":quantile(bm,.975),
                         "point_median":median(vals),"ci95_median_low":quantile(bd,.025),"ci95_median_high":quantile(bd,.975),
                         "seed":SEED,"bootstrap_n":BOOT_N})
with (HERE/"FIVEGZ5SE_STAGED_ENTRY_43_ASSET_BOOTSTRAP_v2.csv").open("w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=boot_fields); w.writeheader()
    for r in boot: w.writerow({k:(fmt(v) if isinstance(v,float) else v) for k,v in r.items()})

# Selective-vs-full synergy table for matched staged configurations.
syn_fields=["group","window","initial_pct","n_assets","mean_return_delta_selective_minus_full_pp","median_return_delta_pp",
            "return_selective_better","mean_mdd_improvement_selective_vs_full_pp","mdd_selective_better",
            "mean_p5_improvement_selective_vs_full_pp","p5_selective_better","mean_cvar10_improvement_selective_vs_full_pp","cvar10_selective_better"]
syn=[]
for gname,alist in groups.items():
    for window in (3,5):
        for initial in (50,60,70):
            ds=[]
            for a in alist:
                cm=cfgmap(a)
                f=cm[f"INIT_{initial}_C_W{window}_FULL_FIRST"]["r"]
                s=cm[f"INIT_{initial}_C_W{window}_SELECTIVE"]["r"]
                ds.append({
                    "ret":pct(s["return"]-f["return"]),"mdd":pct(s["mdd"]-f["mdd"]),
                    "p5":pct(s["p5_trade"]-f["p5_trade"]) if s["p5_trade"] is not None and f["p5_trade"] is not None else None,
                    "cv":pct(s["cvar10"]-f["cvar10"]) if s["cvar10"] is not None and f["cvar10"] is not None else None,
                })
            syn.append({"group":gname,"window":window,"initial_pct":initial,"n_assets":len(alist),
                        "mean_return_delta_selective_minus_full_pp":mean([d["ret"] for d in ds]),
                        "median_return_delta_pp":median([d["ret"] for d in ds]),
                        "return_selective_better":sum(d["ret"]>0 for d in ds),
                        "mean_mdd_improvement_selective_vs_full_pp":mean([d["mdd"] for d in ds]),
                        "mdd_selective_better":sum(d["mdd"]>0 for d in ds),
                        "mean_p5_improvement_selective_vs_full_pp":mean([d["p5"] for d in ds]),
                        "p5_selective_better":sum(d["p5"]>0 for d in ds if d["p5"] is not None),
                        "mean_cvar10_improvement_selective_vs_full_pp":mean([d["cv"] for d in ds]),
                        "cvar10_selective_better":sum(d["cv"]>0 for d in ds if d["cv"] is not None)})
with (HERE/"FIVEGZ5SE_STAGED_ENTRY_43_ASSET_SELECTIVE_SYNERGY_v2.csv").open("w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=syn_fields); w.writeheader()
    for r in syn: w.writerow({k:(fmt(v) if isinstance(v,float) else v) for k,v in r.items()})

# Compact audit note.
note = f"""# FIVEGZ5SE staged-entry 43-asset computation audit v2

Status: COMPUTED_PENDING_INTERPRETATION

Assets:
- stocks: {len(stocks)}
- crypto: {len(crypto)} ({', '.join(CRYPTO_KEEP)})
- combined: {len(assets)}

Each asset has {len(cfg_names)} frozen configurations.
Bootstrap: asset-level resampling, n={BOOT_N}, seed={SEED}.

Generated:
- FIVEGZ5SE_STAGED_ENTRY_43_ASSET_INPUT_MANIFEST_v2.json
- crypto_batch4_v2.json
- FIVEGZ5SE_STAGED_ENTRY_43_ASSET_ALL_CONFIGS_v2.csv
- FIVEGZ5SE_STAGED_ENTRY_43_ASSET_SUMMARY_v2.csv
- FIVEGZ5SE_STAGED_ENTRY_43_ASSET_TAIL_RISK_v2.csv
- FIVEGZ5SE_C_CONFIRMATION_EVENTS_43_ASSET_v2.csv
- FIVEGZ5SE_C_CONFIRMATION_ACCURACY_43_ASSET_v2.csv
- FIVEGZ5SE_STAGED_ENTRY_43_ASSET_BOOTSTRAP_v2.csv
- FIVEGZ5SE_STAGED_ENTRY_43_ASSET_SELECTIVE_SYNERGY_v2.csv

No operating-policy conclusion is encoded in this computation file. Interpretation is performed only after reviewing these outputs.
"""
(HERE/"FIVEGZ5SE_STAGED_ENTRY_43_ASSET_COMPUTATION_AUDIT_v2.md").write_text(note)
print(json.dumps({"status":"PASS","assets":len(assets),"configs_per_asset":len(cfg_names),"events":len(events),"bootstrap_rows":len(boot),"synergy_rows":len(syn)}))
