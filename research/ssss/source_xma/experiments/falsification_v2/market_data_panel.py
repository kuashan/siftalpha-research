#!/usr/bin/env python3
"""Build and audit a cached Market Data Panel for XMA Falsification v2.

Infrastructure only:
- no signal logic
- no hypothesis outcome analysis
- no sealed-window access

The panel is provider-agnostic. Provider-native raw CSV snapshots are cached
immutably, normalized once, hashed, and then reused by feature/statistical code.

Official experiments must still obey SSSS_DATA_SOURCE_POLICY.md:
- no silent ticker-by-ticker provider mixing
- provider / adjustment / timezone semantics must be frozen
- raw snapshots must be retained
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd


EQUITIES = (
    "AAPL","MSFT","NVDA","AMD","AVGO","ORCL","INTC","QCOM","MU",
    "GOOGL","META","NFLX","AMZN","TSLA","HD","MCD","WMT","COST","PG","KO","PEP",
    "ABT","LLY","UNH","JNJ","TMO","JPM","BAC","GS","V","MA","CAT","BA","GE",
    "XOM","CVX","LIN","NEE","PLD",
)

SECTOR_ETFS = (
    "XLK","XLC","XLY","XLP","XLV","XLF","XLI","XLE","XLB","XLU","XLRE",
)

MARKET_ETFS = ("SPY",)

# VIX is intentionally external to the stock/ETF provider set because the
# official VIX index may come from a dedicated Cboe snapshot.
REQUIRED_STOCK_PANEL = tuple(dict.fromkeys(EQUITIES + SECTOR_ETFS + MARKET_ETFS))

NORMALIZED_COLUMNS = (
    "date","open","high","low","close","volume",
    "provider","adjustment_mode","timezone","retrieved_at",
)


@dataclass(frozen=True)
class SymbolAudit:
    symbol: str
    raw_path: str
    normalized_path: str
    raw_sha256: str
    normalized_sha256: str
    rows: int
    first_date: str | None
    last_date: str | None
    duplicate_dates: int
    missing_ohlcv_rows: int


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _read_provider_csv(path: Path) -> pd.DataFrame:
    """Read common Twelve Data or Yahoo/yfinance daily CSV shapes."""
    first = path.read_text(encoding="utf-8", errors="replace").splitlines()[0]
    sep = ";" if ";" in first else ","
    df = pd.read_csv(path, sep=sep)
    cols = {str(c).strip().lower().replace(" ", "_"): c for c in df.columns}

    date_col = next(
        (cols[k] for k in ("datetime", "date") if k in cols),
        None,
    )
    if date_col is None:
        raise ValueError(f"{path}: no date/datetime column")

    need = {}
    for key in ("open", "high", "low", "close", "volume"):
        if key not in cols:
            raise ValueError(f"{path}: missing {key}")
        need[key] = cols[key]

    out = pd.DataFrame(
        {
            "date": pd.to_datetime(df[date_col], errors="coerce").dt.date.astype("string"),
            "open": pd.to_numeric(df[need["open"]], errors="coerce"),
            "high": pd.to_numeric(df[need["high"]], errors="coerce"),
            "low": pd.to_numeric(df[need["low"]], errors="coerce"),
            "close": pd.to_numeric(df[need["close"]], errors="coerce"),
            "volume": pd.to_numeric(df[need["volume"]], errors="coerce"),
        }
    )
    out = out.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)
    return out


def normalize_symbol(
    *,
    symbol: str,
    raw_path: Path,
    normalized_path: Path,
    provider: str,
    adjustment_mode: str,
    timezone: str,
    retrieved_at: str,
) -> SymbolAudit:
    frame = _read_provider_csv(raw_path)
    duplicate_dates = int(frame["date"].duplicated(keep=False).sum())
    if duplicate_dates:
        raise ValueError(f"{symbol}: duplicate dates found ({duplicate_dates})")

    missing_ohlcv = int(
        frame[["open","high","low","close","volume"]].isna().any(axis=1).sum()
    )

    frame["provider"] = provider
    frame["adjustment_mode"] = adjustment_mode
    frame["timezone"] = timezone
    frame["retrieved_at"] = retrieved_at
    frame = frame[list(NORMALIZED_COLUMNS)]

    normalized_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(normalized_path, index=False)

    return SymbolAudit(
        symbol=symbol,
        raw_path=str(raw_path),
        normalized_path=str(normalized_path),
        raw_sha256=sha256_file(raw_path),
        normalized_sha256=sha256_file(normalized_path),
        rows=int(len(frame)),
        first_date=None if frame.empty else str(frame.iloc[0]["date"]),
        last_date=None if frame.empty else str(frame.iloc[-1]["date"]),
        duplicate_dates=duplicate_dates,
        missing_ohlcv_rows=missing_ohlcv,
    )


def build_panel(
    *,
    raw_dir: Path,
    output_dir: Path,
    provider: str,
    adjustment_mode: str,
    timezone: str,
    retrieved_at: str,
    symbols: Iterable[str] = REQUIRED_STOCK_PANEL,
) -> dict:
    symbols = tuple(symbols)
    audits: list[SymbolAudit] = []
    missing_raw: list[str] = []

    for symbol in symbols:
        candidates = [
            raw_dir / f"{symbol}.csv",
            raw_dir / f"{symbol.lower()}.csv",
        ]
        raw_path = next((p for p in candidates if p.exists()), None)
        if raw_path is None:
            missing_raw.append(symbol)
            continue

        audits.append(
            normalize_symbol(
                symbol=symbol,
                raw_path=raw_path,
                normalized_path=output_dir / "normalized" / f"{symbol}.csv",
                provider=provider,
                adjustment_mode=adjustment_mode,
                timezone=timezone,
                retrieved_at=retrieved_at,
            )
        )

    present = {a.symbol for a in audits}
    breadth_present = len(set(EQUITIES) & present)
    breadth_min = 32

    manifest = {
        "schema": 1,
        "purpose": "XMA Falsification v2 Market Data Panel",
        "provider": provider,
        "adjustment_mode": adjustment_mode,
        "timezone": timezone,
        "retrieved_at": retrieved_at,
        "required_stock_panel_symbols": list(symbols),
        "equity_breadth_universe_size": len(EQUITIES),
        "breadth_min_valid_members": breadth_min,
        "breadth_members_cached": breadth_present,
        "breadth_80pct_path_available": breadth_present >= breadth_min,
        "missing_raw_symbols": missing_raw,
        "symbols": [asdict(a) for a in audits],
        "official_freeze_ready": (
            set(REQUIRED_STOCK_PANEL).issubset(present)
            and not missing_raw
            and all(a.duplicate_dates == 0 for a in audits)
            and all(a.missing_ohlcv_rows == 0 for a in audits)
        ),
        "notes": [
            "VIX index snapshot is frozen separately; do not substitute a VIX futures ETF.",
            "official_freeze_ready requires all 39 equities + 11 sector ETFs + SPY.",
            "32/39 is sufficient only for a specific daily Breadth value, not for Data Freeze completeness.",
            "no official experiment may silently mix equity/ETF providers ticker by ticker.",
        ],
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / "panel_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    return manifest


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--raw-dir", required=True)
    p.add_argument("--output-dir", required=True)
    p.add_argument("--provider", required=True)
    p.add_argument("--adjustment-mode", required=True)
    p.add_argument("--timezone", required=True)
    p.add_argument("--retrieved-at", required=True)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    manifest = build_panel(
        raw_dir=Path(args.raw_dir),
        output_dir=Path(args.output_dir),
        provider=args.provider,
        adjustment_mode=args.adjustment_mode,
        timezone=args.timezone,
        retrieved_at=args.retrieved_at,
    )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
