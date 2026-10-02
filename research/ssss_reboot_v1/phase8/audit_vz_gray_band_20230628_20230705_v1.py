#!/usr/bin/env python3
import gzip, json, math
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
LEDGER = ROOT / "research/ssss_reboot_v1/phase8/oos10_signal_ledgers/VZ_FIRST_OBSERVED.csv.gz"
OUT = ROOT / "research/ssss_reboot_v1/phase8/VZ_20230628_20230705_GRAY_BAND_AUDIT_v1.json"
OUT_MD = ROOT / "research/ssss_reboot_v1/phase8/VZ_20230628_20230705_GRAY_BAND_AUDIT_v1.md"

with gzip.open(LEDGER, "rt", encoding="utf-8") as f:
    df = pd.read_csv(f)

df["date"] = pd.to_datetime(df["date"])
sel = df[(df["date"] >= "2023-06-27") & (df["date"] <= "2023-07-05")].copy()

rows = []
for _, r in sel.iterrows():
    vals = {k: (None if pd.isna(r[k]) else float(r[k])) for k in ["open","high","low","close","ZK1","GZB3","GZB4","BS"]}
    eligible = all(vals[k] is not None for k in ["ZK1","GZB3","GZB4"]) and vals["GZB4"] > vals["ZK1"]
    touch = False
    if eligible and vals["high"] is not None and vals["low"] is not None:
        touch = vals["high"] >= vals["GZB4"] and vals["low"] <= vals["GZB3"]
    upper_cross = bool(r.get("upper")) if not pd.isna(r.get("upper")) else False
    rows.append({
        "date": r["date"].strftime("%Y-%m-%d"),
        **vals,
        "color": None if pd.isna(r.get("color")) else str(r.get("color")),
        "upper": upper_cross,
        "gray_band_above_zk1": bool(eligible),
        "gray_band_touch": bool(touch),
        "e7b_gray_exit_condition": bool(eligible and touch),
    })

out = {
    "symbol":"VZ",
    "window_requested":"2023-06-28..2023-07-05",
    "context_start":"2023-06-27",
    "definition":{
        "band_above":"GZB4 > ZK1",
        "touch":"High >= GZB4 AND Low <= GZB3",
        "exit":"band_above AND touch"
    },
    "rows":rows
}
OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")

lines = [
    "# VZ 2023-06-28..2023-07-05 浅灰带审计","",
    "定义：GZB4 > ZK1，且 K 线区间与浅灰带相交（High >= GZB4 且 Low <= GZB3）。","",
    "| 日期 | High | Low | ZK1 | GZB4 | GZB3 | GZB4>ZK1 | 触碰灰带 | 满足E7B灰带清仓条件 |",
    "|---|---:|---:|---:|---:|---:|---|---|---|"
]
for x in rows:
    if x["date"] < "2023-06-28":
        continue
    lines.append(
        f"| {x['date']} | {x['high']:.6f} | {x['low']:.6f} | {x['ZK1']:.6f} | {x['GZB4']:.6f} | {x['GZB3']:.6f} | "
        f"{'YES' if x['gray_band_above_zk1'] else 'NO'} | {'YES' if x['gray_band_touch'] else 'NO'} | {'YES' if x['e7b_gray_exit_condition'] else 'NO'} |"
    )
OUT_MD.write_text("\n".join(lines), encoding="utf-8")
print(json.dumps(out, indent=2))
