#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

ROOT = Path(__file__).resolve().parent
UNIVERSE = json.loads((ROOT / "A_SHARE_50_UNIVERSE_V1.json").read_text(encoding="utf-8"))
DATA_DIR = ROOT / "ashare50_data_snapshot_v1"
MANIFEST = DATA_DIR / "manifest.json"
AUDIT = ROOT / "A_SHARE_50_DATA_AUDIT_V1.md"

FETCH_START = UNIVERSE["fetch_start"]
FETCH_END_EXCLUSIVE = UNIVERSE["fetch_end_exclusive"]
FORMAL_START = pd.Timestamp(UNIVERSE["formal_window"][0])
FORMAL_END = pd.Timestamp(UNIVERSE["formal_window"][1])


def sha256_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1<<20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch_one(ticker: str) -> pd.DataFrame:
    last=None
    for attempt in range(5):
        try:
            df=yf.download(
                ticker,
                start=FETCH_START,
                end=FETCH_END_EXCLUSIVE,
                interval="1d",
                auto_adjust=True,
                actions=False,
                repair=True,
                progress=False,
                threads=False,
                multi_level_index=False,
            )
            if df is not None and not df.empty:
                df=df.reset_index()
                if "Date" not in df.columns:
                    raise RuntimeError(f"{ticker}: Date missing")
                keep=["Date","Open","High","Low","Close","Volume"]
                missing=[c for c in keep if c not in df.columns]
                if missing:
                    raise RuntimeError(f"{ticker}: missing columns {missing}")
                out=df[keep].copy()
                out["Date"]=pd.to_datetime(out["Date"]).dt.tz_localize(None)
                for c in ["Open","High","Low","Close","Volume"]:
                    out[c]=pd.to_numeric(out[c],errors="coerce")
                out=out.dropna(subset=["Open","High","Low","Close"]).sort_values("Date").drop_duplicates("Date")
                return out.reset_index(drop=True)
            last=RuntimeError("empty download")
        except Exception as e:
            last=e
        time.sleep(2*(attempt+1))
    raise RuntimeError(f"{ticker}: download failed: {last}")


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    symbols=UNIVERSE["symbols"]
    assert len(symbols)==50
    assert len({x["code"] for x in symbols})==50
    assert sum(x["role"]=="DEVELOPMENT" for x in symbols)==35
    assert sum(x["role"]=="FRESH_OOS" for x in symbols)==15
    assert all(not x["code"].startswith(("300","688")) for x in symbols)

    rows={}
    failures=[]
    for item in symbols:
        try:
            df=fetch_one(item["yahoo"])
            path=DATA_DIR/f'{item["code"]}.csv.gz'
            df.to_csv(path,index=False,compression="gzip")
            pre=df.loc[df["Date"]<FORMAL_START]
            formal=df.loc[(df["Date"]>=FORMAL_START)&(df["Date"]<=FORMAL_END)]
            one_price=((df["High"]-df["Low"]).abs()<=np.maximum(0.001,df["Close"].abs()*1e-8))
            prev=df["Close"].shift(1)
            gap=df["Open"]/prev-1.0
            locked_up=int((one_price & (gap>=0.095)).sum())
            locked_dn=int((one_price & (gap<=-0.095)).sum())
            rec={
                "code":item["code"],
                "ticker":item["yahoo"],
                "name":item["name"],
                "sector":item["sector"],
                "role":item["role"],
                "rows":int(len(df)),
                "first":df["Date"].min().strftime("%Y-%m-%d"),
                "last":df["Date"].max().strftime("%Y-%m-%d"),
                "preformal_rows":int(len(pre)),
                "formal_rows":int(len(formal)),
                "locked_up_candidates":locked_up,
                "locked_down_candidates":locked_dn,
                "sha256":sha256_file(path),
            }
            rows[item["code"]]=rec
            if len(pre)<120:
                failures.append(f'{item["code"]}: preformal_rows={len(pre)} < 120')
            if len(formal)<1500:
                failures.append(f'{item["code"]}: formal_rows={len(formal)} < 1500')
            if df["Date"].max()<FORMAL_END:
                failures.append(f'{item["code"]}: ends {df["Date"].max().date()} before {FORMAL_END.date()}')
        except Exception as e:
            failures.append(str(e))

    manifest={
        "study":"SLTD_ASHARE50_INTEGRATED_RISK_V1_DATA_AUDIT",
        "source":"Yahoo Finance via yfinance",
        "auto_adjust":True,
        "fetch_start":FETCH_START,
        "fetch_end_exclusive":FETCH_END_EXCLUSIVE,
        "formal_window":[FORMAL_START.strftime("%Y-%m-%d"),FORMAL_END.strftime("%Y-%m-%d")],
        "symbol_count":len(symbols),
        "development_count":sum(x["role"]=="DEVELOPMENT" for x in symbols),
        "fresh_count":sum(x["role"]=="FRESH_OOS" for x in symbols),
        "files":rows,
        "failures":failures,
        "status":"PASS" if not failures and len(rows)==50 else "FAIL",
        "generated_at_utc":datetime.now(timezone.utc).isoformat(),
    }
    MANIFEST.write_text(json.dumps(manifest,indent=2,ensure_ascii=False),encoding="utf-8")

    lines=[
        "# A-share 50 Data Audit v1","",
        f"Status: **{manifest['status']}**","",
        f"- Downloaded: **{len(rows)}/50**",
        f"- Development: **{manifest['development_count']}**",
        f"- Fresh OOS: **{manifest['fresh_count']}**",
        f"- Formal window: **{FORMAL_START.date()}..{FORMAL_END.date()}**","",
    ]
    if failures:
        lines += ["## Failures",""]+[f"- {x}" for x in failures]+[""]
    lines += [
        "| Code | Name | Sector | Role | First | Last | Pre-2018 rows | Formal rows | Locked-up cand. | Locked-down cand. |",
        "|---|---|---|---|---|---|---:|---:|---:|---:|",
    ]
    for code in sorted(rows):
        x=rows[code]
        lines.append(
            f"| {code} | {x['name']} | {x['sector']} | {x['role']} | {x['first']} | {x['last']} | "
            f"{x['preformal_rows']} | {x['formal_rows']} | {x['locked_up_candidates']} | {x['locked_down_candidates']} |"
        )
    AUDIT.write_text("\n".join(lines)+"\n",encoding="utf-8")
    print(json.dumps({"status":manifest["status"],"failures":failures,"downloaded":len(rows)},indent=2,ensure_ascii=False))
    if manifest["status"]!="PASS":
        raise SystemExit(2)


if __name__=="__main__":
    main()
