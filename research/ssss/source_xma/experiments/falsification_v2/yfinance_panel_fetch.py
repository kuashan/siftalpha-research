#!/usr/bin/env python3
"""Resumable yfinance fallback fetcher for the v2 Market Data Panel.

Governance:
- yfinance is the policy-approved fallback, not silently the primary source.
- this adapter preserves provider-native action/adjustment information.
- no hypothesis outcome computation occurs here.
- official use requires V2 provider-parity review before Data Freeze.

Pinned client candidate:
    yfinance==1.7.0
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yfinance as yf

from market_data_panel import REQUIRED_STOCK_PANEL


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--output-dir", required=True)
    p.add_argument("--start", required=True)
    p.add_argument(
        "--end",
        required=True,
        help="Exclusive end date, matching yfinance history semantics.",
    )
    p.add_argument(
        "--mode",
        choices=["raw", "auto_adjust"],
        required=True,
        help="Fetch one adjustment mode per invocation; parity audit decides official mode.",
    )
    p.add_argument("--symbols", nargs="*", default=list(REQUIRED_STOCK_PANEL))
    p.add_argument("--force", action="store_true")
    return p.parse_args()


def fetch_symbol(symbol: str, start: str, end: str, mode: str) -> tuple[pd.DataFrame, dict]:
    auto_adjust = mode == "auto_adjust"
    ticker = yf.Ticker(symbol)

    frame = ticker.history(
        start=start,
        end=end,
        interval="1d",
        actions=True,
        auto_adjust=auto_adjust,
        back_adjust=False,
        repair=False,
        keepna=True,
        rounding=False,
        timeout=30,
        raise_errors=True,
    )

    if frame is None or frame.empty:
        raise RuntimeError(f"{symbol}: empty yfinance history")

    frame = frame.copy()
    frame.index.name = "Date"
    frame = frame.reset_index()

    # Normalize date representation in the provider-native snapshot while
    # keeping all yfinance columns (Adj Close / Dividends / Stock Splits when supplied).
    date_col = "Date"
    dt = pd.to_datetime(frame[date_col], errors="raise")
    if getattr(dt.dt, "tz", None) is not None:
        frame[date_col] = dt.dt.tz_localize(None).dt.strftime("%Y-%m-%d")
    else:
        frame[date_col] = dt.dt.strftime("%Y-%m-%d")

    metadata = dict(ticker.get_history_metadata(repair=False) or {})
    keep_meta = {
        k: metadata.get(k)
        for k in (
            "currency",
            "symbol",
            "exchangeName",
            "fullExchangeName",
            "instrumentType",
            "firstTradeDate",
            "regularMarketTime",
            "gmtoffset",
            "timezone",
            "exchangeTimezoneName",
            "priceHint",
        )
    }

    request = {
        "symbol": symbol,
        "start_inclusive": start,
        "end_exclusive": end,
        "interval": "1d",
        "actions": True,
        "auto_adjust": auto_adjust,
        "back_adjust": False,
        "repair": False,
        "keepna": True,
        "rounding": False,
    }

    return frame, {
        "provider": "Yahoo Finance via yfinance",
        "client": "yfinance",
        "client_version": getattr(yf, "__version__", "unknown"),
        "request": request,
        "history_metadata": keep_meta,
    }


def main() -> None:
    a = parse_args()
    root = Path(a.output_dir)
    raw_dir = root / "raw" / f"yfinance_{a.mode}"
    meta_dir = root / "metadata" / f"yfinance_{a.mode}"
    raw_dir.mkdir(parents=True, exist_ok=True)
    meta_dir.mkdir(parents=True, exist_ok=True)

    fetch_log = root / f"yfinance_{a.mode}_fetch_log.jsonl"

    for symbol in [s.upper() for s in a.symbols]:
        csv_path = raw_dir / f"{symbol}.csv"
        meta_path = meta_dir / f"{symbol}.json"

        if (
            not a.force
            and csv_path.exists()
            and csv_path.stat().st_size > 50
            and meta_path.exists()
        ):
            rec = {
                "symbol": symbol,
                "status": "CACHE_HIT",
                "raw_sha256": sha256_file(csv_path),
                "metadata_sha256": sha256_file(meta_path),
                "logged_at_utc": datetime.now(timezone.utc).isoformat(),
            }
            with fetch_log.open("a", encoding="utf-8") as f:
                f.write(json.dumps(rec, sort_keys=True) + "\n")
            continue

        started = datetime.now(timezone.utc).isoformat()
        try:
            frame, metadata = fetch_symbol(symbol, a.start, a.end, a.mode)

            tmp_csv = csv_path.with_suffix(".csv.tmp")
            frame.to_csv(tmp_csv, index=False)
            tmp_csv.replace(csv_path)

            metadata["retrieved_at_utc"] = datetime.now(timezone.utc).isoformat()
            metadata["row_count"] = int(len(frame))
            metadata["first_date"] = str(frame.iloc[0]["Date"])
            metadata["last_date"] = str(frame.iloc[-1]["Date"])

            tmp_meta = meta_path.with_suffix(".json.tmp")
            tmp_meta.write_text(
                json.dumps(metadata, indent=2, sort_keys=True),
                encoding="utf-8",
            )
            tmp_meta.replace(meta_path)

            rec = {
                "symbol": symbol,
                "status": "FETCHED",
                "rows": int(len(frame)),
                "raw_sha256": sha256_file(csv_path),
                "metadata_sha256": sha256_file(meta_path),
                "started_at_utc": started,
                "finished_at_utc": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as exc:
            rec = {
                "symbol": symbol,
                "status": "ERROR",
                "started_at_utc": started,
                "finished_at_utc": datetime.now(timezone.utc).isoformat(),
                "error": repr(exc),
            }

        with fetch_log.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, sort_keys=True) + "\n")

        if rec["status"] == "ERROR":
            raise SystemExit(f"{symbol}: {rec['error']}")


if __name__ == "__main__":
    main()
