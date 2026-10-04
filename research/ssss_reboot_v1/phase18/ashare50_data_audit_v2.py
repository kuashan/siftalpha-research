#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import akshare as ak
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
UNIVERSE = json.loads((ROOT / "A_SHARE_50_UNIVERSE_V1.json").read_text(encoding="utf-8"))
DATA_DIR = ROOT / "ashare50_data_snapshot_v2"
MANIFEST = DATA_DIR / "manifest.json"
AUDIT = ROOT / "A_SHARE_50_DATA_AUDIT_V2.md"

START_DATE = "20160101"
END_DATE = "20260930"
FORMAL_START = pd.Timestamp("2018-01-02")
FORMAL_END = pd.Timestamp("2026-09-30")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch_one(code: str) -> pd.DataFrame:
    last = None
    for attempt in range(4):
        try:
            df = ak.stock_zh_a_hist(
                symbol=code,
                period="daily",
                start_date=START_DATE,
                end_date=END_DATE,
                adjust="qfq",
            )
            if df is None or df.empty:
                raise RuntimeError("empty history")
            rename = {
                "日期": "Date",
                "开盘": "Open",
                "最高": "High",
                "最低": "Low",
                "收盘": "Close",
                "成交量": "Volume",
            }
            missing = [x for x in rename if x not in df.columns]
            if missing:
                raise RuntimeError(f"missing columns {missing}")
            out = df[list(rename)].rename(columns=rename).copy()
            out["Date"] = pd.to_datetime(out["Date"]).dt.tz_localize(None)
            for c in ["Open", "High", "Low", "Close", "Volume"]:
                out[c] = pd.to_numeric(out[c], errors="coerce")
            out = (
                out.dropna(subset=["Open", "High", "Low", "Close"])
                .sort_values("Date")
                .drop_duplicates("Date")
                .reset_index(drop=True)
            )
            return out
        except Exception as exc:
            last = exc
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"{code}: download failed: {last}")


def audit_item(item: dict):
    df = fetch_one(item["code"])
    pre = df.loc[df["Date"] < FORMAL_START]
    formal = df.loc[(df["Date"] >= FORMAL_START) & (df["Date"] <= FORMAL_END)]

    one_price = (
        (df["High"] - df["Low"]).abs()
        <= np.maximum(0.001, df["Close"].abs() * 1e-8)
    )
    prev = df["Close"].shift(1)
    gap = df["Open"] / prev - 1.0
    locked_up = int((one_price & (gap >= 0.095)).sum())
    locked_down = int((one_price & (gap <= -0.095)).sum())

    failures = []
    if len(pre) < 120:
        failures.append(f'{item["code"]}: preformal_rows={len(pre)} < 120')
    if len(formal) < 1500:
        failures.append(f'{item["code"]}: formal_rows={len(formal)} < 1500')
    if df["Date"].max() < FORMAL_END:
        failures.append(
            f'{item["code"]}: ends {df["Date"].max().date()} before {FORMAL_END.date()}'
        )
    return item, df, locked_up, locked_down, failures


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    symbols = UNIVERSE["symbols"]
    assert len(symbols) == 50
    assert len({x["code"] for x in symbols}) == 50
    assert sum(x["role"] == "DEVELOPMENT" for x in symbols) == 35
    assert sum(x["role"] == "FRESH_OOS" for x in symbols) == 15

    rows = {}
    failures = []

    with ThreadPoolExecutor(max_workers=5) as ex:
        futures = {ex.submit(audit_item, item): item for item in symbols}
        for fut in as_completed(futures):
            item = futures[fut]
            try:
                item, df, locked_up, locked_down, local_fail = fut.result()
                path = DATA_DIR / f'{item["code"]}.csv.gz'
                df.to_csv(path, index=False, compression="gzip")
                pre = df.loc[df["Date"] < FORMAL_START]
                formal = df.loc[
                    (df["Date"] >= FORMAL_START) & (df["Date"] <= FORMAL_END)
                ]
                rows[item["code"]] = {
                    "code": item["code"],
                    "name": item["name"],
                    "sector": item["sector"],
                    "role": item["role"],
                    "rows": int(len(df)),
                    "first": df["Date"].min().strftime("%Y-%m-%d"),
                    "last": df["Date"].max().strftime("%Y-%m-%d"),
                    "preformal_rows": int(len(pre)),
                    "formal_rows": int(len(formal)),
                    "locked_up_candidates": locked_up,
                    "locked_down_candidates": locked_down,
                    "sha256": sha256_file(path),
                }
                failures.extend(local_fail)
            except Exception as exc:
                failures.append(f'{item["code"]}: {exc}')

    manifest = {
        "study": "SLTD_ASHARE50_INTEGRATED_RISK_V1_DATA_AUDIT_V2",
        "source": "Eastmoney via AkShare",
        "akshare_function": "stock_zh_a_hist",
        "adjust": "qfq",
        "start_date": START_DATE,
        "end_date": END_DATE,
        "formal_window": [
            FORMAL_START.strftime("%Y-%m-%d"),
            FORMAL_END.strftime("%Y-%m-%d"),
        ],
        "symbol_count": 50,
        "development_count": 35,
        "fresh_count": 15,
        "files": rows,
        "failures": failures,
        "status": "PASS" if len(rows) == 50 and not failures else "FAIL",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    MANIFEST.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    lines = [
        "# A-share 50 Data Audit v2",
        "",
        f"Status: **{manifest['status']}**",
        "",
        "- Source: **Eastmoney via AkShare**",
        "- Adjust: **qfq (前复权)**",
        f"- Downloaded: **{len(rows)}/50**",
        "- DEVELOPMENT: **35**",
        "- FRESH_OOS: **15**",
        "",
    ]
    if failures:
        lines += ["## Failures", ""] + [f"- {x}" for x in failures] + [""]

    lines += [
        "| Code | Name | Sector | Role | First | Last | Pre-2018 | Formal rows | Limit-up locked cand. | Limit-down locked cand. |",
        "|---|---|---|---|---|---|---:|---:|---:|---:|",
    ]
    for code in sorted(rows):
        x = rows[code]
        lines.append(
            f"| {code} | {x['name']} | {x['sector']} | {x['role']} | "
            f"{x['first']} | {x['last']} | {x['preformal_rows']} | "
            f"{x['formal_rows']} | {x['locked_up_candidates']} | "
            f"{x['locked_down_candidates']} |"
        )
    AUDIT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(
        json.dumps(
            {
                "status": manifest["status"],
                "downloaded": len(rows),
                "failures": failures,
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    if manifest["status"] != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
