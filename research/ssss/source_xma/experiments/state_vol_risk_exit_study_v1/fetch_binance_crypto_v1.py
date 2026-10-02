#!/usr/bin/env python3
import csv, io, json, urllib.request, zipfile
from datetime import datetime, timezone
from pathlib import Path

HERE=Path(__file__).resolve().parent
OUT=HERE/"crypto_inputs"
OUT.mkdir(parents=True,exist_ok=True)
SPECS={
 "BTCUSDT":("2017-08-17","2026-05-05"),
 "ETHUSDT":("2017-08-17","2026-04-19"),
 "BNBUSDT":("2017-11-06","2026-04-19"),
 "SOLUSDT":("2020-08-11","2026-04-19"),
}
def months(start,end):
 y,m=map(int,start[:7].split("-")); ey,em=map(int,end[:7].split("-"))
 while (y,m)<=(ey,em):
  yield f"{y:04d}-{m:02d}"
  m+=1
  if m==13:y+=1;m=1
def date_from_ts(x):
 n=int(x)
 sec=n/1_000_000 if n>100_000_000_000_000 else n/1000
 return datetime.fromtimestamp(sec,tz=timezone.utc).strftime("%Y-%m-%d")
manifest={}
for sym,(start,end) in SPECS.items():
 rows=[]
 for ym in months(start,end):
  url=f"https://data.binance.vision/data/spot/monthly/klines/{sym}/1d/{sym}-1d-{ym}.zip"
  try:
   with urllib.request.urlopen(url,timeout=60) as r: body=r.read()
  except Exception as e:
   raise SystemExit(f"{sym} {ym} fetch failed: {e}")
  with zipfile.ZipFile(io.BytesIO(body)) as z:
   names=z.namelist()
   if len(names)!=1: raise SystemExit(f"{sym} {ym} unexpected zip members {names}")
   text=z.read(names[0]).decode("utf-8")
  for p in csv.reader(io.StringIO(text)):
   if len(p)<6: continue
   d=date_from_ts(p[0])
   if start<=d<=end: rows.append([d,p[1],p[2],p[3],p[4],p[5]])
 rows.sort(key=lambda r:r[0])
 if not rows: raise SystemExit(f"{sym}: no rows")
 path=OUT/f"{sym}.csv"
 with path.open("w",newline="") as f:
  w=csv.writer(f);w.writerow(["Date","Open","High","Low","Close","Volume"]);w.writerows(rows)
 manifest[sym]={"start":rows[0][0],"end":rows[-1][0],"rows":len(rows)}
(HERE/"CRYPTO_INPUT_MANIFEST_v1.json").write_text(json.dumps(manifest,indent=2)+"\n")
print(json.dumps(manifest))
