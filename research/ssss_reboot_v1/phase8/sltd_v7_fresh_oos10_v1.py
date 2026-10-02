#!/usr/bin/env python3
"""SLTD V7 Fresh 10-Stock OOS Validation v1."""
from __future__ import annotations

import csv
import gzip
import json
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
PHASE7 = ROOT.parent / "phase7"
sys.path.insert(0, str(PHASE7))
sys.path.insert(0, str(ROOT))

import sltd_v6_position_policy_batch_v1 as core  # noqa: E402
import sltd_v7_combination_ablation_v1 as combo  # noqa: E402


SYMBOLS = ["WFC","LMT","PM","ADP","WM","UNP","SO","VZ","PANW","CVS"]
DATA_DIR = ROOT / "oos10_data_snapshot"
LEDGER_DIR = ROOT / "oos10_signal_ledgers"
OUT_JSON = ROOT / "SLTD_V7_FRESH_OOS10_RESULT_v1.json"
OUT_MD = ROOT / "SLTD_V7_FRESH_OOS10_RESULT_v1.md"

SYSTEMS = {
    "BASELINE_ALL_15": "BASELINE_ALL_15",
    "CANDIDATE_A_DROP_S1_S3": "DROP_S1_S3",
    "CANDIDATE_B_DROP_B3_S1_S3": "DROP_B3_S1_S3",
}

FIELDNAMES = [
    "symbol","date","open","high","low","close","ZD1","ZK1","GZB3","GZB4",
    "GZB8","GZB9","BS","BD","color","run_age","age","origin","recent",
    "transition","lower","lower_subtype","upper","upper_subtype",
    "light_support","light_resist","BUY","HOLD","WAIT","SELL"
]


def write_ledger(path: Path, ledger: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "wt", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES)
        w.writeheader()
        for row in ledger:
            out = dict(row)
            for k in ("BUY","HOLD","WAIT","SELL"):
                out[k] = "|".join(out[k])
            w.writerow(out)


def portfolio(per_symbol: dict[str, dict], prepared: dict[str, dict]) -> dict:
    return combo.portfolio(per_symbol, prepared)


def compact(v: dict) -> dict:
    return {
        k:v[k] for k in (
            "total_return","cagr","max_drawdown","calmar","turnover",
            "position_changes","time_in_market","hard_exit_count"
        )
    }


def pct(x: float) -> str:
    return f"{100*x:.2f}%"


def main() -> None:
    old = {s for xs in core.BATCHES.values() for s in xs}
    overlap = sorted(old.intersection(SYMBOLS))
    if overlap:
        raise RuntimeError(f"OOS10 universe overlaps prior 79: {overlap}")
    if len(SYMBOLS) != 10 or len(set(SYMBOLS)) != 10:
        raise RuntimeError("OOS10 universe must contain exactly 10 unique stocks")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LEDGER_DIR.mkdir(parents=True, exist_ok=True)

    frames: dict[str,pd.DataFrame] = {}
    ledgers: dict[str,list[dict]] = {}
    manifest = {
        "study":"SLTD_V7_FRESH_OOS10_VALIDATION_V1",
        "symbols":SYMBOLS,
        "provider":"Yahoo Finance via yfinance",
        "auto_adjust":False,
        "actions":False,
        "repair":False,
        "fetch_start":core.FETCH_START,
        "fetch_end_exclusive":core.FETCH_END_EXCLUSIVE,
        "formal_start":core.FORMAL_START.strftime("%Y-%m-%d"),
        "formal_end":core.FORMAL_END.strftime("%Y-%m-%d"),
        "prior_79_overlap":overlap,
        "generated_at_utc":datetime.now(timezone.utc).isoformat(),
        "files":{},
    }

    for symbol in SYMBOLS:
        path = DATA_DIR / f"{symbol}.csv.gz"
        frame = core.fetch_stock(symbol, path, force=True)
        if frame.empty:
            raise RuntimeError(f"{symbol}: empty data")
        if pd.Timestamp(frame["Date"].min()) > pd.Timestamp(core.FETCH_START) + pd.Timedelta(days=10):
            raise RuntimeError(f"{symbol}: insufficient warmup history: {frame['Date'].min()}")
        if pd.Timestamp(frame["Date"].max()) < core.FORMAL_END:
            raise RuntimeError(f"{symbol}: data ends before formal end: {frame['Date'].max()}")
        frames[symbol] = frame
        ledger = core.build_ledger(frame, symbol)
        ledgers[symbol] = ledger
        ledger_path = LEDGER_DIR / f"{symbol}_FIRST_OBSERVED.csv.gz"
        write_ledger(ledger_path, ledger)

        manifest["files"][symbol] = {
            "ohlcv_path":str(path.relative_to(ROOT)),
            "ohlcv_sha256":core.sha256_file(path),
            "ledger_path":str(ledger_path.relative_to(ROOT)),
            "ledger_sha256":core.sha256_file(ledger_path),
            "rows":len(frame),
            "first":pd.Timestamp(frame["Date"].min()).strftime("%Y-%m-%d"),
            "last":pd.Timestamp(frame["Date"].max()).strftime("%Y-%m-%d"),
        }

    manifest_path = DATA_DIR / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

    prepared = {s:combo.prepare_symbol(frames[s],ledgers[s]) for s in SYMBOLS}

    sims = {"5bps":{}, "10bps":{}}
    all10 = {"5bps":{}, "10bps":{}}
    per_symbol = {}

    for friction_name,bps in (("5bps",5.0),("10bps",10.0)):
        for label,parent_variant in SYSTEMS.items():
            sims[friction_name][label] = {
                s:combo.simulate(prepared[s],parent_variant,bps) for s in SYMBOLS
            }
            all10[friction_name][label] = portfolio(sims[friction_name][label],prepared)

    for s in SYMBOLS:
        per_symbol[s] = {
            "5bps":{label:compact(sims["5bps"][label][s]) for label in SYSTEMS},
            "10bps":{label:compact(sims["10bps"][label][s]) for label in SYSTEMS},
        }

    comparisons = {}
    for label in ("CANDIDATE_A_DROP_S1_S3","CANDIDATE_B_DROP_B3_S1_S3"):
        c = per_symbol
        comparisons[label] = {
            "all10_delta_5bps":combo.delta(all10["5bps"][label],all10["5bps"]["BASELINE_ALL_15"]),
            "all10_delta_10bps":combo.delta(all10["10bps"][label],all10["10bps"]["BASELINE_ALL_15"]),
            "symbols_better_total_return_5bps":int(sum(
                c[s]["5bps"][label]["total_return"] > c[s]["5bps"]["BASELINE_ALL_15"]["total_return"]
                for s in SYMBOLS
            )),
            "symbols_better_cagr_5bps":int(sum(
                c[s]["5bps"][label]["cagr"] > c[s]["5bps"]["BASELINE_ALL_15"]["cagr"]
                for s in SYMBOLS
            )),
            "symbols_better_maxdd_5bps":int(sum(
                c[s]["5bps"][label]["max_drawdown"] > c[s]["5bps"]["BASELINE_ALL_15"]["max_drawdown"]
                for s in SYMBOLS
            )),
            "symbols_better_calmar_5bps":int(sum(
                c[s]["5bps"][label]["calmar"] > c[s]["5bps"]["BASELINE_ALL_15"]["calmar"]
                for s in SYMBOLS
            )),
            "median_symbol_delta_return_5bps":float(statistics.median(
                c[s]["5bps"][label]["total_return"] - c[s]["5bps"]["BASELINE_ALL_15"]["total_return"]
                for s in SYMBOLS
            )),
            "median_symbol_delta_cagr_5bps":float(statistics.median(
                c[s]["5bps"][label]["cagr"] - c[s]["5bps"]["BASELINE_ALL_15"]["cagr"]
                for s in SYMBOLS
            )),
            "median_symbol_delta_maxdd_5bps":float(statistics.median(
                c[s]["5bps"][label]["max_drawdown"] - c[s]["5bps"]["BASELINE_ALL_15"]["max_drawdown"]
                for s in SYMBOLS
            )),
            "median_symbol_delta_calmar_5bps":float(statistics.median(
                c[s]["5bps"][label]["calmar"] - c[s]["5bps"]["BASELINE_ALL_15"]["calmar"]
                for s in SYMBOLS
            )),
        }

    output = {
        "meta":{
            "study":"SLTD_V7_FRESH_OOS10_VALIDATION_V1",
            "status":"COMPLETE",
            "research_type":"FRESH_STOCK_OOS",
            "symbols":SYMBOLS,
            "universe_count":10,
            "formal_window":"2020-01-02..2026-09-30",
            "representation":"FIRST_OBSERVED",
            "execution":"SIGNAL_CLOSE_TO_NEXT_AVAILABLE_OPEN",
            "ordinary_policy":"I25_AADD_25_TO_CAP_S25_WHOLD_RNO_CHANGE_MIXED",
            "hard_exit":"C2_FULL_CANDLE_BELOW_SLOW_BAND",
            "data_manifest":str(manifest_path.relative_to(ROOT)),
            "generated_at_utc":datetime.now(timezone.utc).isoformat(),
        },
        "systems":SYSTEMS,
        "all10_equal_weight":all10,
        "comparisons":comparisons,
        "per_symbol":per_symbol,
    }
    OUT_JSON.write_text(json.dumps(output,indent=2),encoding="utf-8")

    lines = [
        "# SLTD V7 Fresh 10-Stock OOS Validation v1","",
        "Status: **COMPLETE**","",
        "Research status: **FRESH STOCK OOS**","",
        "Frozen universe: **WFC, LMT, PM, ADP, WM, UNP, SO, VZ, PANW, CVS**","",
        "No symbol overlaps the prior 79-stock universe.","",
        "## Equal-weight 10-stock portfolio — 5 bps","",
        "| System | Return | CAGR | MaxDD | Calmar | Turnover | C2 exits |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for label in SYSTEMS:
        m=all10["5bps"][label]
        lines.append(
            f"| {label} | {pct(m['total_return'])} | {pct(m['cagr'])} | {pct(m['max_drawdown'])} | "
            f"{m['calmar']:.3f} | {m['turnover_mean']:.2f} | {m['hard_exit_count_sum']} |"
        )

    lines += ["","## Breadth vs baseline — 5 bps","",
              "| Candidate | Better return | Better CAGR | Better MaxDD | Better Calmar | Median ΔReturn | Median ΔCAGR | Median ΔMaxDD | Median ΔCalmar |",
              "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for label in ("CANDIDATE_A_DROP_S1_S3","CANDIDATE_B_DROP_B3_S1_S3"):
        x=comparisons[label]
        lines.append(
            f"| {label} | {x['symbols_better_total_return_5bps']}/10 | {x['symbols_better_cagr_5bps']}/10 | "
            f"{x['symbols_better_maxdd_5bps']}/10 | {x['symbols_better_calmar_5bps']}/10 | "
            f"{pct(x['median_symbol_delta_return_5bps'])} | {pct(x['median_symbol_delta_cagr_5bps'])} | "
            f"{pct(x['median_symbol_delta_maxdd_5bps'])} | {x['median_symbol_delta_calmar_5bps']:+.3f} |"
        )

    lines += ["","## Per-symbol 5 bps total return / Calmar","",
              "| Symbol | Baseline Return | A Return | B Return | Baseline Calmar | A Calmar | B Calmar |",
              "|---|---:|---:|---:|---:|---:|---:|"]
    for s in SYMBOLS:
        b=per_symbol[s]["5bps"]["BASELINE_ALL_15"]
        a=per_symbol[s]["5bps"]["CANDIDATE_A_DROP_S1_S3"]
        c=per_symbol[s]["5bps"]["CANDIDATE_B_DROP_B3_S1_S3"]
        lines.append(
            f"| {s} | {pct(b['total_return'])} | {pct(a['total_return'])} | {pct(c['total_return'])} | "
            f"{b['calmar']:.3f} | {a['calmar']:.3f} | {c['calmar']:.3f} |"
        )

    lines += ["","No candidate is auto-promoted by this run.","",
              "`SLTD_V7_FRESH_OOS10_VALIDATION_V1 = COMPLETE`",""]
    OUT_MD.write_text("\n".join(lines),encoding="utf-8")

if __name__=="__main__":
    main()
