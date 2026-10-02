#!/usr/bin/env python3
"""SLTD V6 Position Policy Study v1 — Batch 9 crypto transfer check.

Governance:
- Uses only the stock policy already promoted after frozen B5-B8 validation.
- Does not enumerate, rank, retune, or replace the stock-selected policy.
- Crypto is transfer evidence only.
- Uses Binance Spot daily UTC OHLCV through CCXT exactly as preregistered.
"""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import ccxt
import numpy as np
import pandas as pd

import sltd_v6_position_policy_batch_v1 as core


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data_snapshot" / "batch_09_crypto"
LEDGER_DIR = ROOT / "signal_ledgers"
BATCH_DIR = ROOT / "batches"
DECISION_PATH = ROOT / "SLTD_V6_POSITION_POLICY_STOCK_VALIDATION_DECISION_v1.json"

FORMAL_START = pd.Timestamp("2020-01-02")
FORMAL_END = pd.Timestamp("2026-09-30")
FETCH_START = pd.Timestamp("2016-01-01", tz="UTC")
FETCH_END_EXCLUSIVE = pd.Timestamp("2026-10-01", tz="UTC")

MARKETS = {
    "BTC": "BTC/USDT",
    "ETH": "ETH/USDT",
    "BNB": "BNB/USDT",
    "SOL": "SOL/USDT",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch_binance_daily(exchange: ccxt.Exchange, market: str) -> pd.DataFrame:
    since = int(FETCH_START.timestamp() * 1000)
    end_ms = int(FETCH_END_EXCLUSIVE.timestamp() * 1000)
    one_day_ms = 86_400_000
    rows: list[list[float]] = []

    while since < end_ms:
        chunk = exchange.fetch_ohlcv(market, timeframe="1d", since=since, limit=1000)
        if not chunk:
            break
        rows.extend(chunk)
        last = int(chunk[-1][0])
        next_since = last + one_day_ms
        if next_since <= since:
            raise RuntimeError(f"{market}: CCXT pagination did not advance")
        since = next_since
        if len(chunk) < 1000:
            break
        time.sleep(max(0.05, exchange.rateLimit / 1000.0))

    if not rows:
        raise RuntimeError(f"{market}: no Binance OHLCV returned")

    frame = pd.DataFrame(rows, columns=["timestamp","Open","High","Low","Close","Volume"])
    frame["Date"] = pd.to_datetime(frame["timestamp"], unit="ms", utc=True).dt.tz_convert(None)
    frame = frame[["Date","Open","High","Low","Close","Volume"]].copy()
    for c in ["Open","High","Low","Close","Volume"]:
        frame[c] = pd.to_numeric(frame[c], errors="coerce")
    frame = frame.dropna(subset=["Date","Open","High","Low","Close"])
    frame = frame[frame["Date"] < FETCH_END_EXCLUSIVE.tz_convert(None)]
    frame = frame.sort_values("Date").drop_duplicates("Date", keep="last").reset_index(drop=True)
    return frame


def eligibility_start(frame: pd.DataFrame) -> tuple[pd.Timestamp, str]:
    dates = pd.to_datetime(frame["Date"]).dt.tz_localize(None)
    if (dates < pd.Timestamp("2020-01-01")).any():
        return FORMAL_START, "PRE_2020_HISTORY_AVAILABLE"
    if len(frame) <= 180:
        raise RuntimeError("crypto asset has <=180 returned daily bars; no eligible formal sample")
    start = pd.Timestamp(dates.iloc[180])
    if start > FORMAL_END:
        raise RuntimeError(f"180-bar warm-up ends after formal window: {start.date()}")
    return max(FORMAL_START, start), "FIRST_180_RETURNED_BARS_WARMUP"


def with_symbol_window(start: pd.Timestamp, fn):
    old_start = core.FORMAL_START
    old_end = core.FORMAL_END
    try:
        core.FORMAL_START = start
        core.FORMAL_END = FORMAL_END
        return fn()
    finally:
        core.FORMAL_START = old_start
        core.FORMAL_END = old_end


def compact_symbol_metrics(v: dict) -> dict:
    return {k: v[k] for k in (
        "total_return","cagr","max_drawdown","calmar","turnover",
        "position_changes","time_in_market","trade_count","win_rate",
        "median_trade_return","p5_trade_return","cvar5_trade_return",
        "average_holding_days",
    )}


def fmt_pct(x: float | None) -> str:
    return "NA" if x is None else f"{100*x:.2f}%"


def fmt_num(x: float | None) -> str:
    return "NA" if x is None else f"{x:.3f}"


def main() -> None:
    decision = json.loads(DECISION_PATH.read_text(encoding="utf-8"))
    d = decision.get("decision", {})
    if not d.get("stock_policy_promoted"):
        raise RuntimeError("No promoted stock policy; Batch 9 transfer check cannot proceed")
    policy_spec = d["policy"]
    promoted_id = d["result"]
    policy = core.Policy(
        policy_spec["initial"],
        policy_spec["add_mode"],
        policy_spec["sell_reduction"],
        policy_spec["wait_mode"],
        policy_spec["resolution"],
    )
    if policy.id != promoted_id:
        raise RuntimeError("Promoted policy ID/spec mismatch")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LEDGER_DIR.mkdir(parents=True, exist_ok=True)
    BATCH_DIR.mkdir(parents=True, exist_ok=True)

    exchange = ccxt.binance({
        "enableRateLimit": True,
        "options": {"defaultType": "spot"},
    })
    exchange.load_markets()

    frames: dict[str, pd.DataFrame] = {}
    ledgers: dict[str, list[dict]] = {}
    eligible_starts: dict[str, pd.Timestamp] = {}

    manifest = {
        "study": "SLTD_V6_POSITION_POLICY_STUDY_V1",
        "batch": 9,
        "stage": "CRYPTO_TRANSFER_ONLY",
        "asset_class": "CRYPTO",
        "provider": "Binance Spot via CCXT",
        "timeframe": "1d UTC",
        "markets": MARKETS,
        "fetch_start": "2016-01-01",
        "fetch_end_exclusive": "2026-10-01",
        "formal_start": "2020-01-02",
        "formal_end": "2026-09-30",
        "promoted_stock_policy": promoted_id,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "files": {},
    }

    fieldnames = [
        "symbol","date","open","high","low","close","ZD1","ZK1","GZB3","GZB4",
        "GZB8","GZB9","BS","BD","color","run_age","age","origin","recent",
        "transition","lower","lower_subtype","upper","upper_subtype",
        "light_support","light_resist","BUY","HOLD","WAIT","SELL"
    ]

    for label, market in MARKETS.items():
        frame = fetch_binance_daily(exchange, market)
        start, warmup_rule = eligibility_start(frame)
        if pd.Timestamp(frame["Date"].max()) < FORMAL_END:
            raise RuntimeError(f"{label}: data ends before formal end: {frame['Date'].max()}")

        path = DATA_DIR / f"{label}_USDT.csv.gz"
        with gzip.open(path, "wt", encoding="utf-8", newline="") as f:
            frame.to_csv(f, index=False)

        frames[label] = frame
        eligible_starts[label] = start
        manifest["files"][label] = {
            "market": market,
            "path": str(path.relative_to(ROOT)),
            "sha256": sha256_file(path),
            "rows": len(frame),
            "first": pd.Timestamp(frame["Date"].min()).strftime("%Y-%m-%d"),
            "last": pd.Timestamp(frame["Date"].max()).strftime("%Y-%m-%d"),
            "eligible_start": start.strftime("%Y-%m-%d"),
            "warmup_rule": warmup_rule,
        }

        ledger = core.build_ledger(frame, label)
        ledgers[label] = ledger
        ledger_path = LEDGER_DIR / f"BATCH_09_{label}_FIRST_OBSERVED.csv.gz"
        with gzip.open(ledger_path, "wt", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            for row in ledger:
                out = dict(row)
                for k in ("BUY","HOLD","WAIT","SELL"):
                    out[k] = "|".join(out[k])
                w.writerow(out)

    manifest_path = DATA_DIR / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

    prepared: dict[str, dict] = {}
    per5_full: dict[str, dict] = {}
    per10_full: dict[str, dict] = {}
    for label in MARKETS:
        start = eligible_starts[label]
        prepared[label] = with_symbol_window(
            start, lambda l=label: core.prepare_fast_symbol(frames[l], ledgers[l])
        )
        per5_full[label] = with_symbol_window(
            start, lambda l=label: core.simulate_symbol(frames[l], ledgers[l], policy, 5.0)
        )
        per10_full[label] = with_symbol_window(
            start, lambda l=label: core.simulate_symbol(frames[l], ledgers[l], policy, 10.0)
        )

    common_dates, common_idx = core.prepare_common_alignment(prepared)
    per5_fast = {label: core.simulate_symbol_fast(prepared[label], policy, 5.0) for label in MARKETS}
    per10_fast = {label: core.simulate_symbol_fast(prepared[label], policy, 10.0) for label in MARKETS}
    portfolio5 = core.portfolio_metrics_fast(per5_fast, common_dates, common_idx)
    portfolio10 = core.portfolio_metrics_fast(per10_fast, common_dates, common_idx)

    event_counts = {}
    for label, ledger in ledgers.items():
        start = eligible_starts[label]
        counts = {a: 0 for a in ("BUY","HOLD","WAIT","SELL")}
        rule_counts = {rid: 0 for rid in core.RULE_IDS.values()}
        for row in ledger:
            date = pd.Timestamp(row["date"])
            if date < start or date > FORMAL_END:
                continue
            for action in counts:
                if row[action]:
                    counts[action] += 1
                    for rid in row[action]:
                        rule_counts[rid] += 1
        event_counts[label] = {
            "eligible_start": start.strftime("%Y-%m-%d"),
            "action_class_bars": counts,
            "rule_hits": rule_counts,
        }

    output = {
        "meta": {
            "study": "SLTD_V6_POSITION_POLICY_STUDY_V1",
            "status": "BATCH_COMPLETE",
            "batch": 9,
            "stage": "CRYPTO_TRANSFER_ONLY",
            "asset_class": "CRYPTO",
            "symbols": list(MARKETS.keys()),
            "markets": MARKETS,
            "representation": "FIRST_OBSERVED",
            "execution": "CLOSE_CONFIRMED_NEXT_AVAILABLE_OPEN",
            "promoted_stock_policy": promoted_id,
            "policy_locked": True,
            "retuning_allowed": False,
            "friction_baseline_bps": 5,
            "friction_stress_bps": 10,
            "portfolio_common_start": common_dates[0],
            "portfolio_common_end": common_dates[-1],
            "data_manifest": str(manifest_path.relative_to(ROOT)),
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        },
        "policy": policy_spec,
        "eligibility": {k: v.strftime("%Y-%m-%d") for k, v in eligible_starts.items()},
        "event_counts": event_counts,
        "per_symbol_5bps": {k: compact_symbol_metrics(v) for k, v in per5_full.items()},
        "per_symbol_10bps": {k: compact_symbol_metrics(v) for k, v in per10_full.items()},
        "equal_weight_portfolio_5bps": portfolio5,
        "equal_weight_portfolio_10bps": portfolio10,
        "interpretation_guardrail": (
            "Batch 9 is descriptive transfer evidence only. It cannot retune, rerank, "
            "replace, or revoke the stock-selected policy."
        ),
    }

    json_path = BATCH_DIR / "BATCH_09_CRYPTO_POSITION_POLICY_TRANSFER.json"
    json_path.write_text(json.dumps(output, indent=2), encoding="utf-8")

    lines = [
        "# SLTD V6 Position Policy — Batch 9 Crypto Transfer Check",
        "",
        "Status: **COMPLETE**",
        "",
        "Mode: **TRANSFER-ONLY / NO RETUNING**",
        "",
        f"Stock-promoted policy: \`{promoted_id}\`",
        "",
        "Markets: BTC/USDT, ETH/USDT, BNB/USDT, SOL/USDT",
        "",
        "Data: Binance Spot daily UTC OHLCV via CCXT",
        "",
        "Execution: signal close -> next available daily open",
        "",
        "## Per-asset transfer results — 5 bps",
        "",
        "| Asset | Eligible start | Calmar | CAGR | Max DD | Return | Turnover |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for label in MARKETS:
        m = per5_full[label]
        lines.append(
            f"| {label} | {eligible_starts[label].strftime('%Y-%m-%d')} | {fmt_num(m['calmar'])} | "
            f"{fmt_pct(m['cagr'])} | {fmt_pct(m['max_drawdown'])} | {fmt_pct(m['total_return'])} | "
            f"{m['turnover']:.2f} |"
        )

    lines += [
        "",
        "## Per-asset transfer results — 10 bps stress",
        "",
        "| Asset | Calmar | CAGR | Max DD | Return |",
        "|---|---:|---:|---:|---:|",
    ]
    for label in MARKETS:
        m = per10_full[label]
        lines.append(
            f"| {label} | {fmt_num(m['calmar'])} | {fmt_pct(m['cagr'])} | "
            f"{fmt_pct(m['max_drawdown'])} | {fmt_pct(m['total_return'])} |"
        )

    lines += [
        "",
        "## Equal-weight 4-asset common-window portfolio",
        "",
        f"Common window: **{common_dates[0]} through {common_dates[-1]}**",
        "",
        f"- 5 bps: Calmar {fmt_num(portfolio5['calmar'])}, CAGR {fmt_pct(portfolio5['cagr'])}, "
        f"MaxDD {fmt_pct(portfolio5['max_drawdown'])}, Return {fmt_pct(portfolio5['total_return'])}.",
        f"- 10 bps: Calmar {fmt_num(portfolio10['calmar'])}, CAGR {fmt_pct(portfolio10['cagr'])}, "
        f"MaxDD {fmt_pct(portfolio10['max_drawdown'])}, Return {fmt_pct(portfolio10['total_return'])}.",
        "",
        "Batch 9 is descriptive transfer evidence only. It cannot change the already promoted stock policy.",
        "",
        "\`SLTD_V6_POSITION_POLICY_BATCH_09_CRYPTO_TRANSFER = COMPLETE\`",
        "",
    ]
    md_path = BATCH_DIR / "BATCH_09_CRYPTO_POSITION_POLICY_TRANSFER.md"
    md_path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
