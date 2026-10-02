#!/usr/bin/env python3
"""SLTD V6 Position Policy validation runner for frozen shortlist only.

Batches 5-8 are validation-only. This runner loads the discovery shortlist
frozen before validation and evaluates exactly those five policies in frozen
order. It does not enumerate, rank, retune, or inspect the other Stage A
candidates.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

import sltd_v6_position_policy_batch_v1 as core


ROOT = Path(__file__).resolve().parent
SHORTLIST_PATH = ROOT / "SLTD_V6_POSITION_POLICY_DISCOVERY_FROZEN_SHORTLIST_v1.json"
DATA_ROOT = ROOT / "data_snapshot"
LEDGER_ROOT = ROOT / "signal_ledgers"
BATCH_ROOT = ROOT / "batches"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--batch", type=int, required=True, choices=(5, 6, 7, 8))
    p.add_argument("--force-fetch", action="store_true")
    return p.parse_args()


def load_shortlist() -> dict:
    data = json.loads(SHORTLIST_PATH.read_text(encoding="utf-8"))
    meta = data["meta"]
    if meta.get("status") != "FROZEN_BEFORE_VALIDATION":
        raise RuntimeError("Shortlist is not frozen before validation")
    items = data.get("shortlist", [])
    if len(items) != 5:
        raise RuntimeError(f"Expected 5 frozen candidates, found {len(items)}")
    expected_roles = ["PRIMARY", "BACKUP_1", "BACKUP_2", "BACKUP_3", "BACKUP_4"]
    roles = [x.get("role") for x in items]
    if roles != expected_roles:
        raise RuntimeError(f"Unexpected frozen shortlist order: {roles}")
    return data


def compact_symbol_metrics(v: dict) -> dict:
    return {k: v[k] for k in (
        "total_return", "cagr", "max_drawdown", "calmar", "turnover",
        "position_changes", "time_in_market", "trade_count", "win_rate",
        "median_trade_return", "p5_trade_return", "cvar5_trade_return",
        "average_holding_days",
    )}


def fmt_pct(x: float | None) -> str:
    return "NA" if x is None else f"{100*x:.2f}%"


def fmt_num(x: float | None) -> str:
    return "NA" if x is None else f"{x:.3f}"


def main() -> None:
    args = parse_args()
    batch = args.batch
    shortlist_data = load_shortlist()
    shortlist = shortlist_data["shortlist"]
    symbols = core.BATCHES[batch]

    data_dir = DATA_ROOT / f"batch_{batch:02d}_stocks"
    data_dir.mkdir(parents=True, exist_ok=True)
    LEDGER_ROOT.mkdir(parents=True, exist_ok=True)
    BATCH_ROOT.mkdir(parents=True, exist_ok=True)

    frames = {}
    ledgers = {}
    manifest = {
        "study": "SLTD_V6_POSITION_POLICY_STUDY_V1",
        "stage": "VALIDATION",
        "batch": batch,
        "asset_class": "STOCK",
        "symbols": symbols,
        "provider": "Yahoo Finance via yfinance",
        "auto_adjust": False,
        "repair": False,
        "fetch_start": core.FETCH_START,
        "fetch_end_exclusive": core.FETCH_END_EXCLUSIVE,
        "formal_start": core.FORMAL_START.strftime("%Y-%m-%d"),
        "formal_end": core.FORMAL_END.strftime("%Y-%m-%d"),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "candidate_scope": "FROZEN_PRIMARY_PLUS_4_BACKUPS_ONLY",
        "frozen_shortlist": SHORTLIST_PATH.name,
        "files": {},
    }

    for symbol in symbols:
        path = data_dir / f"{symbol}.csv.gz"
        frame = core.fetch_stock(symbol, path, args.force_fetch)
        if frame.empty:
            raise RuntimeError(f"{symbol}: empty frame")
        if frame["Date"].max() < core.FORMAL_END:
            raise RuntimeError(f"{symbol}: data ends before formal end: {frame['Date'].max()}")
        frames[symbol] = frame
        manifest["files"][symbol] = {
            "path": str(path.relative_to(ROOT)),
            "sha256": core.sha256_file(path),
            "rows": len(frame),
            "first": pd.Timestamp(frame["Date"].min()).strftime("%Y-%m-%d"),
            "last": pd.Timestamp(frame["Date"].max()).strftime("%Y-%m-%d"),
        }

        ledger = core.build_ledger(frame, symbol)
        ledgers[symbol] = ledger
        ledger_path = LEDGER_ROOT / f"BATCH_{batch:02d}_{symbol}_FIRST_OBSERVED.csv.gz"
        fieldnames = [
            "symbol","date","open","high","low","close","ZD1","ZK1","GZB3","GZB4",
            "GZB8","GZB9","BS","BD","color","run_age","age","origin","recent",
            "transition","lower","lower_subtype","upper","upper_subtype",
            "light_support","light_resist","BUY","HOLD","WAIT","SELL"
        ]
        with gzip.open(ledger_path, "wt", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for row in ledger:
                out = dict(row)
                for k in ("BUY","HOLD","WAIT","SELL"):
                    out[k] = "|".join(out[k])
                w.writerow(out)

    manifest_path = data_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

    prepared = {s: core.prepare_fast_symbol(frames[s], ledgers[s]) for s in symbols}
    common_dates, common_idx = core.prepare_common_alignment(prepared)

    results = []
    for frozen in shortlist:
        p = frozen["policy"]
        policy = core.Policy(
            p["initial"], p["add_mode"], p["sell_reduction"], p["wait_mode"], p["resolution"]
        )
        if policy.id != frozen["policy_id"]:
            raise RuntimeError(f"Frozen policy ID mismatch for {frozen['role']}")

        per5_fast = {s: core.simulate_symbol_fast(prepared[s], policy, 5.0) for s in symbols}
        per10_fast = {s: core.simulate_symbol_fast(prepared[s], policy, 10.0) for s in symbols}
        portfolio5 = core.portfolio_metrics_fast(per5_fast, common_dates, common_idx)
        portfolio10 = core.portfolio_metrics_fast(per10_fast, common_dates, common_idx)

        # Full per-symbol metrics are required for frozen shortlist candidates.
        per5_full = {s: core.simulate_symbol(frames[s], ledgers[s], policy, 5.0) for s in symbols}
        per10_full = {s: core.simulate_symbol(frames[s], ledgers[s], policy, 10.0) for s in symbols}

        results.append({
            "shortlist_rank": frozen["shortlist_rank"],
            "role": frozen["role"],
            "discovery_rank": frozen["discovery_rank"],
            "policy_id": policy.id,
            "policy": p,
            "baseline_5bps": portfolio5,
            "stress_10bps": portfolio10,
            "per_symbol_5bps": {s: compact_symbol_metrics(v) for s, v in per5_full.items()},
            "per_symbol_10bps": {s: compact_symbol_metrics(v) for s, v in per10_full.items()},
        })

    # Preserve the frozen discovery order. Validation results are not allowed to
    # reorder or retune the shortlist.
    results.sort(key=lambda x: x["shortlist_rank"])

    event_counts = {}
    for symbol, ledger in ledgers.items():
        counts = {a: 0 for a in ("BUY", "HOLD", "WAIT", "SELL")}
        rule_counts = {rid: 0 for rid in core.RULE_IDS.values()}
        for row in ledger:
            d = pd.Timestamp(row["date"])
            if d < core.FORMAL_START or d > core.FORMAL_END:
                continue
            for action in counts:
                if row[action]:
                    counts[action] += 1
                    for rid in row[action]:
                        rule_counts[rid] += 1
        event_counts[symbol] = {"action_class_bars": counts, "rule_hits": rule_counts}

    output = {
        "meta": {
            "study": "SLTD_V6_POSITION_POLICY_STUDY_V1",
            "stage": "VALIDATION",
            "status": "BATCH_COMPLETE",
            "batch": batch,
            "asset_class": "STOCK",
            "symbols": symbols,
            "formal_window": "2020-01-02..2026-09-30",
            "representation": "FIRST_OBSERVED",
            "execution": "CLOSE_CONFIRMED_NEXT_AVAILABLE_OPEN",
            "candidate_scope": "FROZEN_PRIMARY_PLUS_4_BACKUPS_ONLY",
            "candidate_count": len(results),
            "friction_baseline_bps": 5,
            "friction_stress_bps": 10,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "data_manifest": str(manifest_path.relative_to(ROOT)),
            "frozen_shortlist": SHORTLIST_PATH.name,
            "governance": "NO_RERANK_NO_RETUNE_FROM_VALIDATION",
        },
        "event_counts": event_counts,
        "candidates": results,
    }

    json_path = BATCH_ROOT / f"BATCH_{batch:02d}_STOCK_POSITION_POLICY_VALIDATION.json"
    json_path.write_text(json.dumps(output, indent=2), encoding="utf-8")

    lines = [
        f"# SLTD V6 Position Policy — Validation Batch {batch}",
        "",
        "Status: **COMPLETE**",
        "",
        "Mode: **FROZEN SHORTLIST VALIDATION ONLY**",
        "",
        "No discovery reranking or parameter retuning is performed in this batch.",
        "",
        "Symbols: " + ", ".join(symbols),
        "",
        "Window: 2020-01-02 through 2026-09-30",
        "",
        "Representation: FIRST_OBSERVED",
        "",
        "Execution: signal close -> next available open",
        "",
        "Candidates evaluated: **5 frozen candidates**",
        "",
        "## Frozen-order results",
        "",
        "| Slot | Policy | Calmar | CAGR | Max DD | Return | 10bps Calmar | Turnover |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for r in results:
        b = r["baseline_5bps"]
        s = r["stress_10bps"]
        lines.append(
            f"| {r['role']} | \`{r['policy_id']}\` | {fmt_num(b['calmar'])} | "
            f"{fmt_pct(b['cagr'])} | {fmt_pct(b['max_drawdown'])} | {fmt_pct(b['total_return'])} | "
            f"{fmt_num(s['calmar'])} | {b['turnover_mean']:.2f} |"
        )

    lines += [
        "",
        "Validation order remains the frozen discovery order:",
        "PRIMARY -> BACKUP_1 -> BACKUP_2 -> BACKUP_3 -> BACKUP_4.",
        "",
        "Final validation gates are evaluated only after Batches 5-8 are complete.",
        "",
        f"`SLTD_V6_POSITION_POLICY_VALIDATION_BATCH_{batch:02d} = COMPLETE`",
        "",
    ]
    md_path = BATCH_ROOT / f"BATCH_{batch:02d}_STOCK_POSITION_POLICY_VALIDATION.md"
    md_path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
