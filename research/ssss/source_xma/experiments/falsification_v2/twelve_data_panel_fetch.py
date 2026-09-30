#!/usr/bin/env python3
"""Resumable Twelve Data daily-bar cache fetcher for the v2 Market Data Panel.

Infrastructure only. This script does not compute research outcomes.

Properties:
- one immutable raw CSV per symbol;
- resume: existing non-empty files are not refetched unless --force;
- conservative rate limiting;
- request/response metadata log;
- no API key is stored in the repository.

Environment:
    TWELVE_DATA_API_KEY
"""

from __future__ import annotations

import argparse
import json
import os
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from market_data_panel import REQUIRED_STOCK_PANEL


BASE_URL = "https://api.twelvedata.com/time_series"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--output-dir", required=True)
    p.add_argument("--start", default=None)
    p.add_argument("--end", default=None)
    p.add_argument("--outputsize", type=int, default=5000)
    p.add_argument(
        "--requests-per-minute",
        type=int,
        default=7,
        help="Use < provider ceiling. Default 7 for an observed 8/min connection.",
    )
    p.add_argument("--force", action="store_true")
    p.add_argument("--symbols", nargs="*", default=list(REQUIRED_STOCK_PANEL))
    return p.parse_args()


def _fetch_csv(
    *,
    api_key: str,
    symbol: str,
    outputsize: int,
    start: str | None,
    end: str | None,
) -> bytes:
    params = {
        "symbol": symbol,
        "interval": "1day",
        "outputsize": str(outputsize),
        "format": "CSV",
        "apikey": api_key,
    }
    if start:
        params["start_date"] = start
    if end:
        params["end_date"] = end

    url = BASE_URL + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "SiftAlphaResearch/1.0"})
    with urllib.request.urlopen(req, timeout=60) as response:
        body = response.read()

    # Twelve Data can return an error as text/JSON despite HTTP success.
    probe = body[:300].decode("utf-8", errors="replace").lower()
    if "error" in probe and ("code" in probe or "message" in probe):
        raise RuntimeError(body[:1000].decode("utf-8", errors="replace"))
    if b"datetime" not in body[:200].lower():
        raise RuntimeError(
            f"{symbol}: response does not look like Twelve Data CSV: "
            + body[:500].decode("utf-8", errors="replace")
        )
    return body


def main() -> None:
    args = parse_args()
    api_key = os.environ.get("TWELVE_DATA_API_KEY")
    if not api_key:
        raise SystemExit("TWELVE_DATA_API_KEY is required")

    if args.requests_per_minute < 1:
        raise SystemExit("--requests-per-minute must be >=1")

    out = Path(args.output_dir)
    raw = out / "raw" / "twelve_data"
    raw.mkdir(parents=True, exist_ok=True)
    log_path = out / "twelve_data_fetch_log.jsonl"

    min_spacing = 60.0 / args.requests_per_minute
    last_request_at = 0.0

    for symbol in [s.upper() for s in args.symbols]:
        path = raw / f"{symbol}.csv"
        if path.exists() and path.stat().st_size > 50 and not args.force:
            record = {
                "symbol": symbol,
                "status": "CACHE_HIT",
                "path": str(path),
                "logged_at_utc": datetime.now(timezone.utc).isoformat(),
            }
            with log_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")
            continue

        elapsed = time.monotonic() - last_request_at
        if last_request_at and elapsed < min_spacing:
            time.sleep(min_spacing - elapsed)

        started = datetime.now(timezone.utc).isoformat()
        try:
            body = _fetch_csv(
                api_key=api_key,
                symbol=symbol,
                outputsize=args.outputsize,
                start=args.start,
                end=args.end,
            )
            last_request_at = time.monotonic()

            tmp = path.with_suffix(".csv.tmp")
            tmp.write_bytes(body)
            tmp.replace(path)

            status = "FETCHED"
            error = None
        except Exception as exc:
            last_request_at = time.monotonic()
            status = "ERROR"
            error = repr(exc)

        record = {
            "symbol": symbol,
            "status": status,
            "path": str(path),
            "start": args.start,
            "end": args.end,
            "outputsize": args.outputsize,
            "requests_per_minute": args.requests_per_minute,
            "started_at_utc": started,
            "finished_at_utc": datetime.now(timezone.utc).isoformat(),
            "error": error,
        }
        with log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")

        if status == "ERROR":
            # Fail fast. Resume on the next invocation without refetching
            # previously completed symbols.
            raise SystemExit(f"{symbol}: {error}")


if __name__ == "__main__":
    main()
