from __future__ import annotations

import sys, json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
PROJECT=ROOT/"integrations"/"sltd_v7_siftalpha_v1"
sys.path.insert(0,str(PROJECT))
import app

for symbol in ("ABNB","AAPL","NVDA","ABT","AMZN"):
    p=app._payload_for(symbol,"1d",strategy_id="chan",force_refresh=True)
    visible=Counter(x["kind"] for x in p["chan"]["signals"])
    events=Counter(str(x["state_zh"]).split(" · ")[0] for x in p["events"])
    print("SYMBOL",symbol)
    print("COUNTS",json.dumps(p["chan"]["counts"],ensure_ascii=False,sort_keys=True))
    print("VISIBLE",json.dumps(dict(visible),ensure_ascii=False,sort_keys=True))
    print("EVENTS",json.dumps(dict(events),ensure_ascii=False,sort_keys=True))
    print("EVENT_DETAIL",json.dumps([
        {
            "state":x["state_zh"],
            "confirm":x["date"],
            "anchor":x["age"],
        } for x in p["events"]
    ],ensure_ascii=False))
