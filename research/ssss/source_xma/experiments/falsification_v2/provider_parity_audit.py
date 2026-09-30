#!/usr/bin/env python3
"""Provider-parity audit for XMA Falsification v2.

This tool compares market-data snapshots only.
It does not compute XMA hypotheses or trading outcomes.

No universal numeric tolerance is embedded.  The tool reports observed
differences so the preregistered parity review can classify them.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


DEFAULT_SUBSET = ("AAPL", "NVDA", "TSLA", "JPM", "XOM", "NEE", "SPY", "XLK")
PRICE_COLS = ("open", "high", "low", "close")


def _load(path: Path) -> tuple[pd.DataFrame, dict]:
    first = path.read_text(encoding="utf-8", errors="replace").splitlines()[0]
    sep = ";" if ";" in first else ","
    raw = pd.read_csv(path, sep=sep)

    canon = {
        str(c).strip().lower().replace(" ", "_"): c
        for c in raw.columns
    }
    date_col = next((canon[k] for k in ("datetime", "date") if k in canon), None)
    if date_col is None:
        raise ValueError(f"{path}: missing date/datetime")

    need = {}
    for k in (*PRICE_COLS, "volume"):
        if k not in canon:
            raise ValueError(f"{path}: missing {k}")
        need[k] = canon[k]

    frame = pd.DataFrame({
        "date": pd.to_datetime(raw[date_col], errors="coerce").dt.strftime("%Y-%m-%d"),
        **{
            k: pd.to_numeric(raw[v], errors="coerce")
            for k, v in need.items()
        },
    })
    frame = frame.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)

    extra = {}
    for canonical in ("adj_close", "dividends", "stock_splits", "capital_gains"):
        if canonical in canon:
            extra[canonical] = pd.to_numeric(raw[canon[canonical]], errors="coerce")

    duplicate_dates = int(frame["date"].duplicated(keep=False).sum())
    return frame, {
        "duplicate_dates": duplicate_dates,
        "extra_columns": sorted(extra),
        "raw_columns": [str(c) for c in raw.columns],
        "extra_series": extra,
    }


def _difference_stats(left: pd.Series, right: pd.Series) -> dict:
    l = left.to_numpy(dtype=float)
    r = right.to_numpy(dtype=float)
    mask = np.isfinite(l) & np.isfinite(r)
    if not mask.any():
        return {"n": 0}

    l = l[mask]
    r = r[mask]
    abs_diff = np.abs(l - r)
    denom = np.maximum(np.maximum(np.abs(l), np.abs(r)), 1e-12)
    rel = abs_diff / denom

    return {
        "n": int(len(l)),
        "abs_diff_median": float(np.median(abs_diff)),
        "abs_diff_p95": float(np.quantile(abs_diff, 0.95)),
        "abs_diff_max": float(np.max(abs_diff)),
        "relative_diff_median": float(np.median(rel)),
        "relative_diff_p95": float(np.quantile(rel, 0.95)),
        "relative_diff_max": float(np.max(rel)),
    }


def audit_symbol(left_path: Path, right_path: Path) -> dict:
    left, left_meta = _load(left_path)
    right, right_meta = _load(right_path)

    left_dates = set(left["date"])
    right_dates = set(right["date"])
    overlap_dates = sorted(left_dates & right_dates)

    lm = left.set_index("date").loc[overlap_dates]
    rm = right.set_index("date").loc[overlap_dates]

    fields = {
        c: _difference_stats(lm[c], rm[c])
        for c in (*PRICE_COLS, "volume")
    }

    return {
        "left": {
            "path": str(left_path),
            "rows": int(len(left)),
            "first_date": None if left.empty else str(left.iloc[0]["date"]),
            "last_date": None if left.empty else str(left.iloc[-1]["date"]),
            "duplicate_dates": left_meta["duplicate_dates"],
            "raw_columns": left_meta["raw_columns"],
        },
        "right": {
            "path": str(right_path),
            "rows": int(len(right)),
            "first_date": None if right.empty else str(right.iloc[0]["date"]),
            "last_date": None if right.empty else str(right.iloc[-1]["date"]),
            "duplicate_dates": right_meta["duplicate_dates"],
            "raw_columns": right_meta["raw_columns"],
        },
        "overlap_rows": int(len(overlap_dates)),
        "left_only_dates": sorted(left_dates - right_dates),
        "right_only_dates": sorted(right_dates - left_dates),
        "field_differences": fields,
        "right_corporate_actions": _corporate_action_summary(right_path),
    }


def _corporate_action_summary(path: Path) -> dict:
    first = path.read_text(encoding="utf-8", errors="replace").splitlines()[0]
    sep = ";" if ";" in first else ","
    raw = pd.read_csv(path, sep=sep)
    canon = {
        str(c).strip().lower().replace(" ", "_"): c
        for c in raw.columns
    }
    date_col = next((canon[k] for k in ("datetime", "date") if k in canon), None)

    result = {}
    for key in ("dividends", "stock_splits", "capital_gains"):
        if key not in canon or date_col is None:
            continue
        vals = pd.to_numeric(raw[canon[key]], errors="coerce").fillna(0)
        dates = pd.to_datetime(raw[date_col], errors="coerce").dt.strftime("%Y-%m-%d")
        events = [
            {"date": str(d), "value": float(v)}
            for d, v in zip(dates, vals)
            if np.isfinite(v) and float(v) != 0.0
        ]
        result[key] = events

    # Adj Close ratio is a useful adjustment-semantics diagnostic when present.
    if "adj_close" in canon and "close" in canon:
        adj = pd.to_numeric(raw[canon["adj_close"]], errors="coerce")
        close = pd.to_numeric(raw[canon["close"]], errors="coerce")
        ratio = (adj / close).replace([np.inf, -np.inf], np.nan).dropna()
        if not ratio.empty:
            result["adj_close_to_close_ratio"] = {
                "n": int(len(ratio)),
                "min": float(ratio.min()),
                "median": float(ratio.median()),
                "max": float(ratio.max()),
                "distinct_rounded_1e8": int(ratio.round(8).nunique()),
            }

    return result


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--left-dir", required=True)
    p.add_argument("--right-dir", required=True)
    p.add_argument("--left-provider", required=True)
    p.add_argument("--right-provider", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--symbols", nargs="*", default=list(DEFAULT_SUBSET))
    return p.parse_args()


def main() -> None:
    a = parse_args()
    left_dir = Path(a.left_dir)
    right_dir = Path(a.right_dir)

    result = {
        "schema": 1,
        "purpose": "SSSS v2 provider parity audit",
        "left_provider": a.left_provider,
        "right_provider": a.right_provider,
        "symbols": list(a.symbols),
        "universal_numeric_tolerance": None,
        "classification": "REQUIRES_REVIEW",
        "per_symbol": {},
        "missing_files": [],
    }

    for symbol in a.symbols:
        lp = left_dir / f"{symbol}.csv"
        rp = right_dir / f"{symbol}.csv"
        if not lp.exists() or not rp.exists():
            result["missing_files"].append({
                "symbol": symbol,
                "left_exists": lp.exists(),
                "right_exists": rp.exists(),
            })
            continue
        result["per_symbol"][symbol] = audit_symbol(lp, rp)

    out = Path(a.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(result, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
