#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import baostock as bs
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
UNIVERSE = json.loads((ROOT / "A_SHARE_50_UNIVERSE_V1.json").read_text(encoding="utf-8"))
DATA_DIR = ROOT / "ashare50_data_snapshot_v3"
MANIFEST = DATA_DIR / "manifest.json"
AUDIT = ROOT / "A_SHARE_50_DATA_AUDIT_V3.md"

START_DATE = "2016-01-01"
END_DATE = "2026-09-30"
FORMAL_START = pd.Timestamp("2018-01-02")
FORMAL_END = pd.Timestamp("2026-09-30")
FIELDS = "date,open,high,low,close,volume,tradestatus,isST"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def bs_code(code: str) -> str:
    return ("sh." if code.startswith("6") else "sz.") + code


def fetch_one(code: str) -> tuple[pd.DataFrame, int]:
    rs = bs.query_history_k_data_plus(
        bs_code(code),
        FIELDS,
        start_date=START_DATE,
        end_date=END_DATE,
        frequency="d",
        adjustflag="2",
    )
    if rs.error_code != "0":
        raise RuntimeError(f"{code}: BaoStock query error {rs.error_code} {rs.error_msg}")

    data = []
    while rs.next():
        data.append(rs.get_row_data())
    if not data:
        raise RuntimeError(f"{code}: empty history")

    df = pd.DataFrame(data, columns=rs.fields)
    df = df.rename(
        columns={
            "date": "Date",
            "open": "Open",
            "high": "High",
            "low": "Low",
            "close": "Close",
            "volume": "Volume",
        }
    )
    df["Date"] = pd.to_datetime(df["Date"]).dt.tz_localize(None)
    for c in ["Open", "High", "Low", "Close", "Volume"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["tradestatus"] = pd.to_numeric(df["tradestatus"], errors="coerce").fillna(0).astype(int)
    df["isST"] = pd.to_numeric(df["isST"], errors="coerce").fillna(0).astype(int)

    # Keep actual trading rows only.
    df = df.loc[df["tradestatus"] == 1].copy()
    df = (
        df.dropna(subset=["Open", "High", "Low", "Close"])
        .sort_values("Date")
        .drop_duplicates("Date")
        .reset_index(drop=True)
    )

    formal_st = int(
        df.loc[
            (df["Date"] >= FORMAL_START) & (df["Date"] <= FORMAL_END),
            "isST",
        ].sum()
    )
    return df[["Date", "Open", "High", "Low", "Close", "Volume"]].copy(), formal_st


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    symbols = UNIVERSE["symbols"]
    assert len(symbols) == 50
    assert sum(x["role"] == "DEVELOPMENT" for x in symbols) == 35
    assert sum(x["role"] == "FRESH_OOS" for x in symbols) == 15

    lg = bs.login()
    if lg.error_code != "0":
        raise RuntimeError(f"BaoStock login failed: {lg.error_code} {lg.error_msg}")

    rows = {}
    failures = []
    try:
        for item in symbols:
            code = item["code"]
            try:
                df, formal_st = fetch_one(code)
                path = DATA_DIR / f"{code}.csv.gz"
                df.to_csv(path, index=False, compression="gzip")

                pre = df.loc[df["Date"] < FORMAL_START]
                formal = df.loc[
                    (df["Date"] >= FORMAL_START) & (df["Date"] <= FORMAL_END)
                ]

                one_price = (
                    (df["High"] - df["Low"]).abs()
                    <= np.maximum(0.001, df["Close"].abs() * 1e-8)
                )
                gap = df["Open"] / df["Close"].shift(1) - 1.0
                locked_up = int((one_price & (gap >= 0.095)).sum())
                locked_dn = int((one_price & (gap <= -0.095)).sum())

                local_fail = []
                if len(pre) < 120:
                    local_fail.append(f"{code}: preformal_rows={len(pre)} < 120")
                if len(formal) < 1500:
                    local_fail.append(f"{code}: formal_rows={len(formal)} < 1500")
                if df["Date"].max() < FORMAL_END:
                    local_fail.append(
                        f"{code}: ends {df['Date'].max().date()} before {FORMAL_END.date()}"
                    )
                if formal_st > 0:
                    local_fail.append(f"{code}: formal ST rows={formal_st}")

                rows[code] = {
                    "code": code,
                    "name": item["name"],
                    "sector": item["sector"],
                    "role": item["role"],
                    "rows": int(len(df)),
                    "first": df["Date"].min().strftime("%Y-%m-%d"),
                    "last": df["Date"].max().strftime("%Y-%m-%d"),
                    "preformal_rows": int(len(pre)),
                    "formal_rows": int(len(formal)),
                    "formal_st_rows": formal_st,
                    "locked_up_candidates": locked_up,
                    "locked_down_candidates": locked_dn,
                    "sha256": sha256_file(path),
                }
                failures.extend(local_fail)
                print(f"OK {code} rows={len(df)} formal={len(formal)}", flush=True)
            except Exception as exc:
                failures.append(f"{code}: {exc}")
                print(f"FAIL {code}: {exc}", flush=True)
    finally:
        bs.logout()

    manifest = {
        "study": "SLTD_ASHARE50_INTEGRATED_RISK_V1_DATA_AUDIT_V3",
        "source": "BaoStock",
        "function": "query_history_k_data_plus",
        "adjustflag": "2",
        "adjustment": "qfq",
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
        "# A-share 50 Data Audit v3",
        "",
        f"Status: **{manifest['status']}**",
        "",
        "- Source: **BaoStock**",
        "- Adjustment: **qfq / adjustflag=2**",
        f"- Downloaded: **{len(rows)}/50**",
        "- DEVELOPMENT: **35**",
        "- FRESH_OOS: **15**",
        "",
    ]
    if failures:
        lines += ["## Failures", ""] + [f"- {x}" for x in failures] + [""]

    lines += [
        "| Code | Name | Sector | Role | First | Last | Pre-2018 | Formal | ST rows | Locked-up cand. | Locked-down cand. |",
        "|---|---|---|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for code in sorted(rows):
        x = rows[code]
        lines.append(
            f"| {code} | {x['name']} | {x['sector']} | {x['role']} | "
            f"{x['first']} | {x['last']} | {x['preformal_rows']} | "
            f"{x['formal_rows']} | {x['formal_st_rows']} | "
            f"{x['locked_up_candidates']} | {x['locked_down_candidates']} |"
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
