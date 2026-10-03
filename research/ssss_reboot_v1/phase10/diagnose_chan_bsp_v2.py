from __future__ import annotations

import csv, gzip, json, sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
PROJECT=ROOT/"integrations"/"sltd_v7_siftalpha_v1"
sys.path.insert(0,str(PROJECT))
import chan_strategy as ch

DATA_ROOT=ROOT/"research"/"ssss_reboot_v1"/"phase7"/"data_snapshot"

def load(path:Path):
    out=[]
    with gzip.open(path,"rt",encoding="utf-8") as f:
        for r in csv.DictReader(f):
            out.append({
                "date":r["Date"][:10],
                "open":float(r["Open"]),
                "high":float(r["High"]),
                "low":float(r["Low"]),
                "close":float(r["Close"]),
                "volume":float(r.get("Volume") or 0),
            })
    return out

tot=Counter()
per={}
examples=defaultdict(list)

for path in sorted(DATA_ROOT.glob("batch_*_stocks/*.csv.gz")):
    sym=path.stem.split(".")[0]
    bars0=ch._validate_candles(load(path))
    bars,_=ch._slice_analysis_window(bars0)
    snap=ch.build_structure_snapshot(bars)
    macd=ch.compute_macd([x.close for x in bars])

    funnel=Counter()
    kind_final=Counter(x["kind"] for x in snap["signals"])
    visible_start=max(0,len(bars)-300)
    kind_visible=Counter(x["kind"] for x in snap["signals"] if int(x["anchor_index"])>=visible_start)

    for info in snap["levels"]:
        units=info["units"]; zss=info["zss"]; links=info["links"]
        dif=macd["dif"]; hist=macd["hist"]
        for zi,zs in enumerate(zss):
            funnel["zs_total"]+=1
            if zs.pending:
                funnel["zs_pending"]+=1
                continue
            funnel["zs_completed"]+=1
            enter=units[zs.start_sub-1] if zs.start_sub>0 else None
            leave=units[zs.end_sub+1] if zs.end_sub+1<len(units) else None
            if enter is None or leave is None or leave.pending:
                funnel["missing_enter_leave"]+=1
                continue
            funnel["has_enter_leave"]+=1
            if enter.direction != leave.direction:
                funnel["dir_mismatch"]+=1
                continue
            funnel["same_direction"]+=1
            down=enter.direction=="down"; sign=-1 if down else 1
            new_extreme=(leave.low<min(enter.low,zs.dd)) if down else (leave.high>max(enter.high,zs.gg))
            outside_center=(leave.low<zs.zd) if down else (leave.high>zs.zg)
            if new_extreme: funnel["new_extreme"]+=1
            if outside_center: funnel["outside_center"]+=1
            enter_dif=ch._dif_extreme(enter,dif,sign)
            pulled=False
            for i in range(max(0,zs.start_index),min(len(bars)-1,zs.end_index)+1):
                if down:
                    if dif[i]>=0.25*enter_dif: pulled=True; break
                else:
                    if dif[i]<=0.25*enter_dif: pulled=True; break
            if pulled: funnel["pulled"]+=1
            weaker=(ch._movement_force(leave,hist,sign)<ch._movement_force(enter,hist,sign)
                    or abs(ch._dif_extreme(leave,dif,sign))<abs(enter_dif))
            if weaker: funnel["weaker"]+=1
            if new_extreme and pulled and weaker:
                funnel["divergence_geometry"]+=1
                examples["divergence_geometry"].append((sym,info["level"],zi,"B1" if down else "S1"))
            source_divergence = outside_center and ((not new_extreme) or weaker)
            if source_divergence:
                funnel["source_divergence"]+=1
            expected="down" if down else "up"
            link=(links[zi] if zi<len(links) else None)
            if link==expected: funnel["link_match"]+=1

            # Compare three common Zhongshu-position relations.
            if zi > 0:
                prev=zss[zi-1]
                cur=zs
                loose = "up" if cur.zd > prev.zg else "down" if cur.zg < prev.zd else "overlap"
                medium = "up" if cur.zd > prev.gg else "down" if cur.zg < prev.dd else "overlap"
                strict = "up" if cur.dd > prev.gg else "down" if cur.gg < prev.dd else "overlap"
                if loose==expected: funnel["link_loose_match"]+=1
                if medium==expected: funnel["link_medium_match"]+=1
                if strict==expected: funnel["link_strict_match"]+=1
                if new_extreme and pulled and weaker and loose==expected:
                    funnel["b1s1_loose_relation"]+=1
                if new_extreme and pulled and weaker and medium==expected:
                    funnel["b1s1_medium_relation"]+=1
                if new_extreme and pulled and weaker and strict==expected:
                    funnel["b1s1_strict_relation"]+=1
                if source_divergence and strict==expected:
                    funnel["b1s1_source_rule_strict"]+=1
                if source_divergence and medium==expected:
                    funnel["b1s1_source_rule_medium"]+=1
                if source_divergence and loose==expected:
                    funnel["b1s1_source_rule_loose"]+=1

            if new_extreme and pulled and weaker and link==expected:
                funnel["all_b1s1"]+=1
                examples["all_b1s1"].append((sym,info["level"],zi,"B1" if down else "S1"))

    replay_counts=Counter()
    per[sym]={
        "final":dict(kind_final),
        "visible300":dict(kind_visible),
        "replay":{},
        "funnel":dict(funnel),
        "levels":[{"level":x["level"],"zss":len(x["zss"]),"links":x["links"]} for x in snap["levels"]],
    }
    tot.update({f"final_{k}":v for k,v in kind_final.items()})
    tot.update({f"visible300_{k}":v for k,v in kind_visible.items()})
    tot.update(funnel)

for sym in ("AAPL","NVDA","ABT","GOOGL","KO"):
    if sym not in per:
        continue
    p=next(DATA_ROOT.glob(f"batch_*_stocks/{sym}.csv.gz"))
    bars0=ch._validate_candles(load(p))
    bars,_=ch._slice_analysis_window(bars0)
    replay=ch.replay_first_observed_signals(bars)
    per[sym]["replay"] = dict(Counter(x["kind"] for x in replay))
    visible_start=max(0,len(bars)-300)
    per[sym]["replay_visible300"] = dict(Counter(
        x["kind"] for x in replay if int(x["anchor_index"])>=visible_start
    ))

visible_examples={k:[] for k in ("B1","B2","S1","S2")}
for sym,row in per.items():
    for kind,count in row.get("visible300",{}).items():
        if kind in visible_examples and count:
            visible_examples[kind].append((sym,count))
out={"totals":dict(tot),"examples":{k:v[:40] for k,v in examples.items()},"visible_examples":visible_examples,"per_symbol":per}
print(json.dumps(out,ensure_ascii=False,indent=2))
