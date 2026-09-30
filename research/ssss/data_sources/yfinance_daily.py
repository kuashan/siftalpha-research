#!/usr/bin/env python3
"""Download fallback SSSS daily bars from Yahoo Finance via yfinance.

This is a research data utility, not trading logic.

Output is intentionally provider-native:
- raw OHLC
- Adj Close when returned
- volume
- corporate-action columns when returned

Do not promote these files into an official SSSS experiment result until the
provider-parity process in SSSS_DATA_SOURCE_POLICY.md has been completed.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yfinance as yf


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--tickers", nargs="+", required=True)
    p.add_argument("--start", required=True, help="YYYY-MM-DD inclusive")
    p.add_argument(
        "--end",
        required=True,
        help="YYYY-MM-DD exclusive, matching yfinance semantics",
    )
    p.add_argument("--output-dir", required=True)
    p.add_argument("--repair", action="store_true")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    tickers = [t.upper() for t in args.tickers]

    data = yf.download(
        tickers=tickers,
        start=args.start,
        end=args.end,
        interval="1d",
        auto_adjust=False,
        actions=True,
        repair=args.repair,
        group_by="ticker",
        threads=True,
        progress=False,
        multi_level_index=True,
    )

    if data is None or data.empty:
        raise SystemExit("No data returned by yfinance")

    retrieval_time = datetime.now(timezone.utc).isoformat()

    if len(tickers) == 1:
        ticker = tickers[0]
        frame = data.copy()
        if isinstance(frame.columns, pd.MultiIndex):
            if ticker in frame.columns.get_level_values(0):
                frame = frame[ticker]
            else:
                frame.columns = frame.columns.get_level_values(-1)
        frame = frame.reset_index()
        frame.to_csv(out_dir / f"{ticker}.csv", index=False)
    else:
        for ticker in tickers:
            if ticker not in data.columns.get_level_values(0):
                continue
            frame = data[ticker].dropna(how="all").reset_index()
            frame.to_csv(out_dir / f"{ticker}.csv", index=False)

    metadata = {
        "provider": "yfinance/Yahoo Finance",
        "client": "yfinance",
        "tickers": tickers,
        "start_inclusive": args.start,
        "end_exclusive": args.end,
        "interval": "1d",
        "auto_adjust": False,
        "actions": True,
        "repair": bool(args.repair),
        "retrieved_at_utc": retrieval_time,
        "note": (
            "Research fallback only. Complete provider-parity audit before "
            "using these bars for official SSSS experiment conclusions."
        ),
    }

    (out_dir / "metadata.json").write_text(
        json.dumps(metadata, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
