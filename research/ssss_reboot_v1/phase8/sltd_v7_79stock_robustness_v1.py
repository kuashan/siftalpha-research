#!/usr/bin/env python3
"""SLTD V7 79-stock robustness check for the two selected deletion candidates."""
from __future__ import annotations

import json
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import sltd_v7_combination_ablation_v1 as parent  # noqa: E402

core = parent.core

OUT_JSON = ROOT / "SLTD_V7_79_STOCK_ROBUSTNESS_RESULT_v1.json"
OUT_MD = ROOT / "SLTD_V7_79_STOCK_ROBUSTNESS_RESULT_v1.md"

VARIANTS = {
    "BASELINE_ALL_15": "BASELINE_ALL_15",
    "CANDIDATE_A_DROP_S1_S3": "DROP_S1_S3",
    "CANDIDATE_B_DROP_B3_S1_S3": "DROP_B3_S1_S3",
}

YEARS = list(range(2020, 2027))
ERAS = {
    "EARLY_2020_2021": ("2020-01-02", "2021-12-31"),
    "MIDDLE_2022_2023": ("2022-01-01", "2023-12-31"),
    "LATE_2024_2026Q3": ("2024-01-01", "2026-09-30"),
}


def slice_metrics(per_symbol, prepared, start, end):
    start = pd.Timestamp(start)
    end = pd.Timestamp(end)
    common_dates, common_idx = core.prepare_common_alignment(prepared)
    mask = np.array([(pd.Timestamp(d) >= start and pd.Timestamp(d) <= end) for d in common_dates])
    positions = np.flatnonzero(mask)
    if len(positions) < 2:
        return None
    dates = [common_dates[i] for i in positions]
    curves = []
    for s in per_symbol:
        base_curve = per_symbol[s]["curve"]
        vals = base_curve[common_idx[s][positions]]
        vals = vals / vals[0]
        curves.append(vals)
    curve = np.mean(np.vstack(curves), axis=0)
    days = max(1, (pd.Timestamp(dates[-1]) - pd.Timestamp(dates[0])).days)
    total = float(curve[-1] - 1.0)
    cagr = float(curve[-1] ** (365.25 / days) - 1.0) if curve[-1] > 0 else -1.0
    mdd = core.max_drawdown(curve)
    calmar = cagr / abs(mdd) if mdd < -1e-12 else (999.0 if cagr > 0 else 0.0)
    return {
        "start": dates[0], "end": dates[-1], "total_return": total,
        "cagr": cagr, "max_drawdown": float(mdd), "calmar": float(calmar)
    }


def symbol_metrics_from_result(result):
    return {k: result[k] for k in ("total_return","cagr","max_drawdown","calmar","turnover","position_changes","time_in_market","hard_exit_count")}


def pct(x):
    return f"{100*x:.2f}%"

def main():
    prepared = {}
    batch_of = {}
    for batch, symbols in core.BATCHES.items():
        for symbol in symbols:
            frame = parent.read_frame(batch, symbol)
            ledger = parent.read_ledger(batch, symbol)
            prepared[symbol] = parent.prepare_symbol(frame, ledger)
            batch_of[symbol] = batch
    if len(prepared) != 79:
        raise RuntimeError(f"Expected 79 stocks, got {len(prepared)}")

    sims = {"5bps": {}, "10bps": {}}
    for fname, bps in (("5bps",5.0),("10bps",10.0)):
        for label, parent_variant in VARIANTS.items():
            sims[fname][label] = {s: parent.simulate(prepared[s], parent_variant, bps) for s in prepared}

    all79 = {"5bps": {}, "10bps": {}}
    batches = {"5bps": {}, "10bps": {}}
    yearly = {"5bps": {}, "10bps": {}}
    eras = {"5bps": {}, "10bps": {}}
    per_symbol = {}

    for fname in ("5bps","10bps"):
        for label in VARIANTS:
            all79[fname][label] = parent.portfolio(sims[fname][label], prepared)
            batches[fname][label] = {}
            for b, symbols in core.BATCHES.items():
                pp={s:prepared[s] for s in symbols}
                ss={s:sims[fname][label][s] for s in symbols}
                batches[fname][label][str(b)] = parent.portfolio(ss, pp)
            yearly[fname][label] = {}
            for y in YEARS:
                yearly[fname][label][str(y)] = slice_metrics(
                    sims[fname][label], prepared, f"{y}-01-01", f"{y}-12-31"
                )
            eras[fname][label] = {
                era: slice_metrics(sims[fname][label], prepared, start, end)
                for era,(start,end) in ERAS.items()
            }

    for s in prepared:
        per_symbol[s] = {
            "batch": batch_of[s],
            "5bps": {label:symbol_metrics_from_result(sims["5bps"][label][s]) for label in VARIANTS},
            "10bps": {label:symbol_metrics_from_result(sims["10bps"][label][s]) for label in VARIANTS},
        }

    comparisons = {}
    base5 = all79["5bps"]["BASELINE_ALL_15"]
    for label in ("CANDIDATE_A_DROP_S1_S3","CANDIDATE_B_DROP_B3_S1_S3"):
        better_return_symbols = sum(
            per_symbol[s]["5bps"][label]["total_return"] > per_symbol[s]["5bps"]["BASELINE_ALL_15"]["total_return"]
            for s in prepared
        )
        better_calmar_symbols = sum(
            per_symbol[s]["5bps"][label]["calmar"] > per_symbol[s]["5bps"]["BASELINE_ALL_15"]["calmar"]
            for s in prepared
        )
        better_years = sum(
            yearly["5bps"][label][str(y)]["total_return"] > yearly["5bps"]["BASELINE_ALL_15"][str(y)]["total_return"]
            for y in YEARS
        )
        better_eras = sum(
            eras["5bps"][label][era]["calmar"] > eras["5bps"]["BASELINE_ALL_15"][era]["calmar"]
            for era in ERAS
        )
        comparisons[label] = {
            "all79_delta_5bps": parent.delta(all79["5bps"][label], base5),
            "all79_delta_10bps": parent.delta(all79["10bps"][label], all79["10bps"]["BASELINE_ALL_15"]),
            "symbols_better_total_return_5bps": int(better_return_symbols),
            "symbols_better_calmar_5bps": int(better_calmar_symbols),
            "years_better_total_return_5bps": int(better_years),
            "eras_better_calmar_5bps": int(better_eras),
            "median_symbol_delta_total_return_5bps": float(statistics.median(
                per_symbol[s]["5bps"][label]["total_return"] - per_symbol[s]["5bps"]["BASELINE_ALL_15"]["total_return"]
                for s in prepared
            )),
            "median_symbol_delta_calmar_5bps": float(statistics.median(
                per_symbol[s]["5bps"][label]["calmar"] - per_symbol[s]["5bps"]["BASELINE_ALL_15"]["calmar"]
                for s in prepared
            )),
        }

    out = {
        "meta":{
            "study":"SLTD_V7_79_STOCK_ROBUSTNESS_CHECK_V1",
            "status":"COMPLETE",
            "research_type":"ROBUSTNESS_REUSED_79_STOCK_UNIVERSE_NOT_OOS",
            "universe_count":79,
            "formal_window":"2020-01-02..2026-09-30",
            "parent_combination_commit":"73493097a6d0bcc35a101869a01414e8470188fb",
            "baseline_commit":"05be43e350d9193ba01a2748ef4c0267438a84b1",
            "generated_at_utc":datetime.now(timezone.utc).isoformat(),
        },
        "variants":VARIANTS,
        "all79":all79,
        "yearly":yearly,
        "eras":eras,
        "batches":batches,
        "comparisons":comparisons,
        "per_symbol":per_symbol,
    }
    OUT_JSON.write_text(json.dumps(out,indent=2),encoding="utf-8")

    lines=[
        "# SLTD V7 79-Stock Robustness Check v1","",
        "Status: **COMPLETE**","",
        "This is a robustness check on the already-used 79-stock universe, not fresh OOS.","",
        "## Full-window all-79 portfolio — 5 bps","",
        "| Variant | Return | CAGR | MaxDD | Calmar |",
        "|---|---:|---:|---:|---:|",
    ]
    for label in VARIANTS:
        m=all79["5bps"][label]
        lines.append(f"| {label} | {pct(m['total_return'])} | {pct(m['cagr'])} | {pct(m['max_drawdown'])} | {m['calmar']:.3f} |")

    lines += ["","## Calendar-year total return — 5 bps","",
              "| Year | Baseline | Candidate A | Candidate B |",
              "|---|---:|---:|---:|"]
    for y in YEARS:
        b=yearly["5bps"]["BASELINE_ALL_15"][str(y)]
        a=yearly["5bps"]["CANDIDATE_A_DROP_S1_S3"][str(y)]
        c=yearly["5bps"]["CANDIDATE_B_DROP_B3_S1_S3"][str(y)]
        lines.append(f"| {y} | {pct(b['total_return'])} | {pct(a['total_return'])} | {pct(c['total_return'])} |")

    lines += ["","## Era Calmar — 5 bps","",
              "| Era | Baseline | Candidate A | Candidate B |",
              "|---|---:|---:|---:|"]
    for era in ERAS:
        b=eras["5bps"]["BASELINE_ALL_15"][era]
        a=eras["5bps"]["CANDIDATE_A_DROP_S1_S3"][era]
        c=eras["5bps"]["CANDIDATE_B_DROP_B3_S1_S3"][era]
        lines.append(f"| {era} | {b['calmar']:.3f} | {a['calmar']:.3f} | {c['calmar']:.3f} |")

    lines += ["","## Breadth versus baseline — 5 bps","",
              "| Candidate | Symbols better return | Symbols better Calmar | Years better return | Eras better Calmar | Median symbol ΔReturn | Median symbol ΔCalmar |",
              "|---|---:|---:|---:|---:|---:|---:|"]
    for label in ("CANDIDATE_A_DROP_S1_S3","CANDIDATE_B_DROP_B3_S1_S3"):
        x=comparisons[label]
        lines.append(f"| {label} | {x['symbols_better_total_return_5bps']}/79 | {x['symbols_better_calmar_5bps']}/79 | {x['years_better_total_return_5bps']}/7 | {x['eras_better_calmar_5bps']}/3 | {pct(x['median_symbol_delta_total_return_5bps'])} | {x['median_symbol_delta_calmar_5bps']:+.3f} |")

    lines += ["","No baseline rule is changed by this run.","",
              "`SLTD_V7_79_STOCK_ROBUSTNESS_CHECK_V1 = COMPLETE`",""]
    OUT_MD.write_text("\n".join(lines),encoding="utf-8")

if __name__=="__main__":
    main()
