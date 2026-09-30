#!/usr/bin/env python3
"""Download exchange-native OHLCV for SSSS crypto research via CCXT.

Research data utility only.  It does not implement trading logic.

One output directory represents one fixed provider/venue configuration.
Do not silently merge different venues inside one official experiment stage.
"""

from __future__ import annotations

import argparse
import csv
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import ccxt


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--exchange", required=True, help="CCXT exchange id, e.g. binance")
    p.add_argument("--symbols", nargs="+", required=True, help="e.g. BTC/USDT ETH/USDT")
    p.add_argument("--timeframe", default="1d")
    p.add_argument("--since", required=True, help="ISO date/time, e.g. 2021-01-01T00:00:00Z")
    p.add_argument("--until", required=True, help="ISO date/time, exclusive upper bound")
    p.add_argument("--market-type", default="spot", choices=["spot", "swap", "future"])
    p.add_argument("--limit", type=int, default=1000)
    p.add_argument("--output-dir", required=True)
    return p.parse_args()


def iso_ms(exchange, value: str) -> int:
    ms = exchange.parse8601(value)
    if ms is None:
        raise ValueError(f"Could not parse ISO timestamp: {value}")
    return int(ms)


def safe_name(symbol: str) -> str:
    return symbol.replace("/", "_").replace(":", "_")


def fetch_symbol(exchange, symbol: str, timeframe: str, since_ms: int, until_ms: int, limit: int):
    rows = []
    cursor = since_ms
    tf_ms = exchange.parse_timeframe(timeframe) * 1000

    while cursor < until_ms:
        batch = exchange.fetch_ohlcv(
            symbol,
            timeframe=timeframe,
            since=cursor,
            limit=limit,
        )

        if not batch:
            break

        advanced = False
        for row in batch:
            ts = int(row[0])
            if ts >= until_ms:
                continue
            if ts < since_ms:
                continue
            rows.append(row[:6])
            if ts >= cursor:
                cursor = ts + tf_ms
                advanced = True

        if not advanced:
            break

        if len(batch) < limit:
            break

        # CCXT also applies enableRateLimit, but keep a small cooperative pause.
        time.sleep(max(getattr(exchange, "rateLimit", 0), 0) / 1000.0)

    # De-duplicate by candle timestamp and sort.
    dedup = {int(r[0]): r for r in rows}
    return [dedup[k] for k in sorted(dedup)]


def main() -> None:
    args = parse_args()
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    exchange_cls = getattr(ccxt, args.exchange)
    exchange = exchange_cls(
        {
            "enableRateLimit": True,
            "options": {"defaultType": args.market_type},
        }
    )
    exchange.load_markets()

    since_ms = iso_ms(exchange, args.since)
    until_ms = iso_ms(exchange, args.until)

    metadata = {
        "provider": "CCXT",
        "ccxt_version": ccxt.__version__,
        "exchange_id": exchange.id,
        "exchange_name": exchange.name,
        "market_type": args.market_type,
        "timeframe": args.timeframe,
        "since_inclusive": args.since,
        "until_exclusive": args.until,
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "symbols": {},
    }

    for symbol in args.symbols:
        if symbol not in exchange.markets:
            metadata["symbols"][symbol] = {"status": "missing_market"}
            continue

        rows = fetch_symbol(
            exchange,
            symbol,
            args.timeframe,
            since_ms,
            until_ms,
            args.limit,
        )

        path = out_dir / f"{safe_name(symbol)}.csv"
        with path.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["timestamp_ms", "open", "high", "low", "close", "volume"])
            w.writerows(rows)

        metadata["symbols"][symbol] = {
            "status": "ok",
            "rows": len(rows),
            "first_timestamp_ms": rows[0][0] if rows else None,
            "last_timestamp_ms": rows[-1][0] if rows else None,
            "market_id": exchange.markets[symbol].get("id"),
        }

    (out_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
