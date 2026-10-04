#!/usr/bin/env python3
"""Pure SLTD state -> forward probability study v1.

Protocol:
- discovery: 79 stocks, 2020-2023
- temporal validation: same 79, 2024-2026Q3
- external stock OOS: frozen fresh 10-stock snapshots
- pure SLTD only; no Chan inputs
- executable forward outcomes use next-bar open
"""
from __future__ import annotations

import gzip
import hashlib
import json
import math
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
PHASE7 = ROOT.parent / "phase7"
PHASE8 = ROOT.parent / "phase8"
sys.path.insert(0, str(PHASE7))
import sltd_v6_position_policy_batch_v1 as core  # noqa: E402

FORMAL_START = pd.Timestamp("2020-01-02")
FORMAL_END = pd.Timestamp("2026-09-30")
DISCOVERY_END = pd.Timestamp("2023-12-31")
VALIDATION_START = pd.Timestamp("2024-01-01")
HORIZONS = (1, 3, 5, 10, 20)

DENSE_FAMILIES = {"F1_COLOR_AGE", "F2_COLOR_AGE_ORIGIN", "F3_COLOR_AGE_INNER", "F4_COLOR_AGE_SLOWPOS", "F5_COLOR_AGE_SLOWTREND"}
EVENT_FAMILIES = {"F6_COLOR_AGE_EVENT", "F7_COLOR_AGE_EVENT_SUBTYPE", "F8_TRANSITION_EVENT"}

OOS10 = ["WFC", "LMT", "PM", "ADP", "WM", "UNP", "SO", "VZ", "PANW", "CVS"]

OUT_JSON = ROOT / "PURE_SLTD_STATE_PROBABILITY_RESULT_v1.json"
OUT_MD = ROOT / "PURE_SLTD_STATE_PROBABILITY_RESULT_v1.md"


def parse_bool(v) -> bool:
    if isinstance(v, bool):
        return v
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return False
    return str(v).strip().lower() in {"1", "true", "yes", "y"}


def read_gzip_csv(path: Path, parse_dates: list[str] | None = None) -> pd.DataFrame:
    with gzip.open(path, "rt", encoding="utf-8") as f:
        return pd.read_csv(f, parse_dates=parse_dates or [])


def load_79_symbol(batch: int, symbol: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    frame_path = PHASE7 / "data_snapshot" / f"batch_{batch:02d}_stocks" / f"{symbol}.csv.gz"
    ledger_path = PHASE7 / "signal_ledgers" / f"BATCH_{batch:02d}_{symbol}_FIRST_OBSERVED.csv.gz"
    frame = read_gzip_csv(frame_path, ["Date"])
    ledger = read_gzip_csv(ledger_path)
    frame["Date"] = pd.to_datetime(frame["Date"]).dt.tz_localize(None)
    ledger["date"] = pd.to_datetime(ledger["date"]).dt.tz_localize(None)
    return frame, ledger


def load_oos_symbol(symbol: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    frame = read_gzip_csv(PHASE8 / "oos10_data_snapshot" / f"{symbol}.csv.gz", ["Date"])
    ledger = read_gzip_csv(PHASE8 / "oos10_signal_ledgers" / f"{symbol}_FIRST_OBSERVED.csv.gz")
    frame["Date"] = pd.to_datetime(frame["Date"]).dt.tz_localize(None)
    ledger["date"] = pd.to_datetime(ledger["date"]).dt.tz_localize(None)
    return frame, ledger


def origin_norm(v) -> str:
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "NONE"
    s = str(v).strip().upper()
    return s if s else "NONE"


def text_norm(v, default="NONE") -> str:
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return default
    s = str(v).strip().upper()
    return s if s else default


def inner_position(close: float, zd1: float, zk1: float) -> str:
    if not all(math.isfinite(x) for x in (close, zd1, zk1)) or zk1 <= zd1:
        return "NA"
    if close < zd1:
        return "BELOW_ZD1"
    if close > zk1:
        return "ABOVE_ZK1"
    mid = (zd1 + zk1) / 2.0
    return "LOWER_HALF" if close <= mid else "UPPER_HALF"


def slow_position(close: float, gzb4: float, gzb3: float) -> str:
    if not all(math.isfinite(x) for x in (close, gzb4, gzb3)) or gzb3 < gzb4:
        return "NA"
    if close < gzb4:
        return "BELOW_GZB4"
    if close > gzb3:
        return "ABOVE_GZB3"
    return "IN_GZB_BAND"


def build_symbol_rows(symbol: str, frame: pd.DataFrame, ledger: pd.DataFrame) -> pd.DataFrame:
    f = frame[["Date", "Open", "High", "Low", "Close", "Volume"]].copy()
    l = ledger.copy()
    merged = f.merge(l, left_on="Date", right_on="date", how="inner", suffixes=("", "_ledger"))
    if len(merged) < 100:
        raise RuntimeError(f"{symbol}: insufficient merged rows {len(merged)}")
    merged = merged.sort_values("Date").reset_index(drop=True)

    opens = merged["Open"].astype(float).to_numpy()
    highs = merged["High"].astype(float).to_numpy()
    lows = merged["Low"].astype(float).to_numpy()
    closes = merged["Close"].astype(float).to_numpy()

    gzb3 = pd.to_numeric(merged["GZB3"], errors="coerce").to_numpy(dtype=float)
    gzb4 = pd.to_numeric(merged["GZB4"], errors="coerce").to_numpy(dtype=float)
    zd1 = pd.to_numeric(merged["ZD1"], errors="coerce").to_numpy(dtype=float)
    zk1 = pd.to_numeric(merged["ZK1"], errors="coerce").to_numpy(dtype=float)

    slow_mid = (gzb3 + gzb4) / 2.0
    slow_trend = np.full(len(merged), "FLAT_OR_NA", dtype=object)
    for i in range(5, len(merged)):
        a = slow_mid[i - 5]
        b = slow_mid[i]
        if math.isfinite(a) and math.isfinite(b):
            if b > a:
                slow_trend[i] = "UP"
            elif b < a:
                slow_trend[i] = "DOWN"

    out = pd.DataFrame({
        "symbol": symbol,
        "date": merged["Date"],
        "color": [text_norm(v, "OTHER") for v in merged["color"]],
        "age": [text_norm(v, "NA") for v in merged["age"]],
        "origin": [origin_norm(v) for v in merged["origin"]],
        "transition": [text_norm(v, "NONE") for v in merged["transition"]],
        "lower": [parse_bool(v) for v in merged["lower"]],
        "upper": [parse_bool(v) for v in merged["upper"]],
        "light_support": [parse_bool(v) for v in merged["light_support"]],
        "light_resist": [parse_bool(v) for v in merged["light_resist"]],
        "lower_subtype": [text_norm(v, "NONE") for v in merged["lower_subtype"]],
        "upper_subtype": [text_norm(v, "NONE") for v in merged["upper_subtype"]],
        "inner_pos": [inner_position(closes[i], zd1[i], zk1[i]) for i in range(len(merged))],
        "slow_pos": [slow_position(closes[i], gzb4[i], gzb3[i]) for i in range(len(merged))],
        "slow_trend": slow_trend,
    })

    n = len(merged)
    for h in HORIZONS:
        ret = np.full(n, np.nan)
        mfe = np.full(n, np.nan)
        mae = np.full(n, np.nan)
        for t in range(n):
            if t + h >= n:
                continue
            entry = opens[t + 1]
            if not math.isfinite(entry) or entry <= 0:
                continue
            ret[t] = closes[t + h] / entry - 1.0
            mfe[t] = float(np.max(highs[t + 1:t + h + 1])) / entry - 1.0
            mae[t] = float(np.min(lows[t + 1:t + h + 1])) / entry - 1.0
        out[f"ret{h}"] = ret
        out[f"mfe{h}"] = mfe
        out[f"mae{h}"] = mae

    return out


def keys_for_row(r) -> list[tuple[str, str]]:
    c = str(r.color)
    a = str(r.age)
    o = str(r.origin)
    keys = [
        ("F1_COLOR_AGE", f"{c}|{a}"),
        ("F2_COLOR_AGE_ORIGIN", f"{c}|{a}|{o}"),
        ("F3_COLOR_AGE_INNER", f"{c}|{a}|{r.inner_pos}"),
        ("F4_COLOR_AGE_SLOWPOS", f"{c}|{a}|{r.slow_pos}"),
        ("F5_COLOR_AGE_SLOWTREND", f"{c}|{a}|{r.slow_trend}"),
    ]
    events: list[tuple[str, str]] = []
    if bool(r.lower):
        events.append(("LOWER", str(r.lower_subtype)))
    if bool(r.upper):
        events.append(("UPPER", str(r.upper_subtype)))
    if bool(r.light_support):
        events.append(("LIGHT_SUPPORT", "CONTACT"))
    if bool(r.light_resist):
        events.append(("LIGHT_RESIST", "CONTACT"))
    for event, subtype in events:
        keys.append(("F6_COLOR_AGE_EVENT", f"{c}|{a}|{event}"))
        keys.append(("F7_COLOR_AGE_EVENT_SUBTYPE", f"{c}|{a}|{event}|{subtype}"))
        if str(r.transition) != "NONE":
            keys.append(("F8_TRANSITION_EVENT", f"{r.transition}|{event}"))
    return keys


def subset_rows(frames: dict[str, pd.DataFrame], start: pd.Timestamp, end: pd.Timestamp) -> dict[str, pd.DataFrame]:
    out = {}
    for s, df in frames.items():
        mask = (df["date"] >= start) & (df["date"] <= end)
        out[s] = df.loc[mask].reset_index(drop=True)
    return out


def unconditional_medians(frames: dict[str, pd.DataFrame]) -> dict[tuple[str, int], float]:
    out = {}
    for s, df in frames.items():
        for h in HORIZONS:
            x = pd.to_numeric(df[f"ret{h}"], errors="coerce").dropna().to_numpy(dtype=float)
            if len(x):
                out[(s, h)] = float(np.median(x))
    return out


def bootstrap_ci(values: list[float], seed_key: str, qlo=0.05, qhi=0.95, reps=2000) -> tuple[float | None, float | None]:
    if len(values) < 5:
        return None, None
    arr = np.asarray(values, dtype=float)
    seed = int(hashlib.sha256(seed_key.encode("utf-8")).hexdigest()[:16], 16) % (2**32)
    rng = np.random.default_rng(seed)
    n = len(arr)
    meds = np.empty(reps, dtype=float)
    for i in range(reps):
        meds[i] = float(np.median(arr[rng.integers(0, n, size=n)]))
    return float(np.quantile(meds, qlo)), float(np.quantile(meds, qhi))


def aggregate_split(frames: dict[str, pd.DataFrame], split_name: str) -> dict[str, dict]:
    baselines = unconditional_medians(frames)
    bucket: dict[tuple[str, str], list[tuple[str, object]]] = defaultdict(list)
    for s, df in frames.items():
        for r in df.itertuples(index=False):
            if not math.isfinite(float(getattr(r, "ret20"))):
                continue
            for family, key in keys_for_row(r):
                bucket[(family, key)].append((s, r))

    metrics: dict[str, dict] = {}
    for (family, key), rows in bucket.items():
        symbols = sorted(set(s for s, _ in rows))
        rec = {
            "split": split_name,
            "family": family,
            "key": key,
            "n": len(rows),
            "symbol_count": len(symbols),
            "horizons": {},
        }
        for h in HORIZONS:
            pooled = np.asarray([float(getattr(r, f"ret{h}")) for _, r in rows if math.isfinite(float(getattr(r, f"ret{h}")))], dtype=float)
            mfes = np.asarray([float(getattr(r, f"mfe{h}")) for _, r in rows if math.isfinite(float(getattr(r, f"mfe{h}")))], dtype=float)
            maes = np.asarray([float(getattr(r, f"mae{h}")) for _, r in rows if math.isfinite(float(getattr(r, f"mae{h}")))], dtype=float)

            per_symbol_excess = []
            per_symbol_state = []
            for s in symbols:
                vals = np.asarray([
                    float(getattr(r, f"ret{h}")) for ss, r in rows
                    if ss == s and math.isfinite(float(getattr(r, f"ret{h}")))
                ], dtype=float)
                if not len(vals) or (s, h) not in baselines:
                    continue
                smed = float(np.median(vals))
                per_symbol_state.append(smed)
                per_symbol_excess.append(smed - baselines[(s, h)])

            lo, hi = bootstrap_ci(per_symbol_excess, f"{split_name}|{family}|{key}|h{h}")
            rec["horizons"][str(h)] = {
                "pooled_median_return": float(np.median(pooled)) if len(pooled) else None,
                "pooled_mean_return": float(np.mean(pooled)) if len(pooled) else None,
                "pooled_win_rate": float(np.mean(pooled > 0)) if len(pooled) else None,
                "pooled_median_mfe": float(np.median(mfes)) if len(mfes) else None,
                "pooled_median_mae": float(np.median(maes)) if len(maes) else None,
                "symbol_median_return": float(np.median(per_symbol_state)) if per_symbol_state else None,
                "symbol_median_excess": float(np.median(per_symbol_excess)) if per_symbol_excess else None,
                "symbol_breadth_positive": float(np.mean(np.asarray(per_symbol_excess) > 0)) if per_symbol_excess else None,
                "symbol_breadth_negative": float(np.mean(np.asarray(per_symbol_excess) < 0)) if per_symbol_excess else None,
                "bootstrap90_lo": lo,
                "bootstrap90_hi": hi,
                "symbol_effect_count": len(per_symbol_excess),
            }
        metrics[f"{family}::{key}"] = rec
    return metrics


def sign(x: float | None) -> int:
    if x is None or not math.isfinite(float(x)) or abs(float(x)) < 1e-15:
        return 0
    return 1 if x > 0 else -1


def support_ok(rec: dict) -> bool:
    family = rec["family"]
    if family in DENSE_FAMILIES:
        return rec["n"] >= 500 and rec["symbol_count"] >= 30
    return rec["n"] >= 80 and rec["symbol_count"] >= 15


def discovery_gate(rec: dict) -> tuple[bool, str | None, list[str]]:
    reasons = []
    if not support_ok(rec):
        return False, None, ["support"]
    h5 = rec["horizons"]["5"]
    h10 = rec["horizons"]["10"]
    h20 = rec["horizons"]["20"]
    e5 = h5["symbol_median_excess"]
    e10 = h10["symbol_median_excess"]
    e20 = h20["symbol_median_excess"]
    s = sign(e10)
    if s == 0 or sign(e5) != s or sign(e20) != s:
        reasons.append("direction_5_10_20")
    if e10 is None or abs(e10) < 0.0025:
        reasons.append("magnitude_10")
    if e20 is None or abs(e20) < 0.0050:
        reasons.append("magnitude_20")
    breadth10 = h10["symbol_breadth_positive"] if s > 0 else h10["symbol_breadth_negative"]
    breadth20 = h20["symbol_breadth_positive"] if s > 0 else h20["symbol_breadth_negative"]
    if breadth10 is None or breadth10 < 0.60:
        reasons.append("breadth_10")
    if breadth20 is None or breadth20 < 0.60:
        reasons.append("breadth_20")
    lo = h10["bootstrap90_lo"]
    hi = h10["bootstrap90_hi"]
    if lo is None or hi is None or not ((s > 0 and lo > 0) or (s < 0 and hi < 0)):
        reasons.append("bootstrap90_10")
    return len(reasons) == 0, ("POSITIVE" if s > 0 else "NEGATIVE" if s < 0 else None), reasons


def temporal_gate(rec: dict | None, direction: str) -> tuple[bool, list[str]]:
    if rec is None:
        return False, ["missing"]
    s = 1 if direction == "POSITIVE" else -1
    reasons = []
    for h in ("10", "20"):
        x = rec["horizons"][h]
        e = x["symbol_median_excess"]
        if sign(e) != s:
            reasons.append(f"direction_{h}")
        b = x["symbol_breadth_positive"] if s > 0 else x["symbol_breadth_negative"]
        if b is None or b < 0.55:
            reasons.append(f"breadth_{h}")
    return len(reasons) == 0, reasons


def oos_gate(rec: dict | None, direction: str) -> tuple[bool, list[str]]:
    if rec is None:
        return False, ["missing"]
    s = 1 if direction == "POSITIVE" else -1
    reasons = []
    for h in ("10", "20"):
        x = rec["horizons"][h]
        e = x["symbol_median_excess"]
        if sign(e) != s:
            reasons.append(f"direction_{h}")
        b = x["symbol_breadth_positive"] if s > 0 else x["symbol_breadth_negative"]
        if b is None or b < 0.60:
            reasons.append(f"breadth_{h}")
    return len(reasons) == 0, reasons


def short_metrics(rec: dict | None) -> dict | None:
    if rec is None:
        return None
    return {
        "n": rec["n"],
        "symbol_count": rec["symbol_count"],
        "h5": rec["horizons"]["5"],
        "h10": rec["horizons"]["10"],
        "h20": rec["horizons"]["20"],
    }


def pct(x: float | None) -> str:
    return "—" if x is None else f"{100.0 * x:.2f}%"


def main() -> None:
    all79: dict[str, pd.DataFrame] = {}
    for batch, symbols in core.BATCHES.items():
        for symbol in symbols:
            frame, ledger = load_79_symbol(batch, symbol)
            all79[symbol] = build_symbol_rows(symbol, frame, ledger)
    if len(all79) != 79:
        raise RuntimeError(f"expected 79, got {len(all79)}")

    oos: dict[str, pd.DataFrame] = {}
    old = set(all79)
    if old.intersection(OOS10):
        raise RuntimeError("OOS overlap with 79")
    for symbol in OOS10:
        frame, ledger = load_oos_symbol(symbol)
        oos[symbol] = build_symbol_rows(symbol, frame, ledger)

    discovery = subset_rows(all79, FORMAL_START, DISCOVERY_END)
    temporal = subset_rows(all79, VALIDATION_START, FORMAL_END)
    external = subset_rows(oos, FORMAL_START, FORMAL_END)

    discovery_metrics = aggregate_split(discovery, "DISCOVERY_79_2020_2023")
    temporal_metrics = aggregate_split(temporal, "TEMPORAL_79_2024_2026Q3")
    external_metrics = aggregate_split(external, "EXTERNAL_OOS10_2020_2026Q3")

    candidates = []
    rejected_discovery = []
    for ident, rec in discovery_metrics.items():
        passed, direction, reasons = discovery_gate(rec)
        if passed:
            t_rec = temporal_metrics.get(ident)
            t_pass, t_reasons = temporal_gate(t_rec, direction)
            item = {
                "id": ident,
                "family": rec["family"],
                "key": rec["key"],
                "direction": direction,
                "discovery": short_metrics(rec),
                "temporal": short_metrics(t_rec),
                "temporal_pass": t_pass,
                "temporal_reasons": t_reasons,
            }
            if t_pass:
                o_rec = external_metrics.get(ident)
                o_pass, o_reasons = oos_gate(o_rec, direction)
                item["external_oos"] = short_metrics(o_rec)
                item["external_oos_pass"] = o_pass
                item["external_oos_reasons"] = o_reasons
                item["final_status"] = "OOS_CONFIRMED" if o_pass else "REJECTED_NOT_STABLE"
            else:
                item["external_oos"] = None
                item["external_oos_pass"] = False
                item["external_oos_reasons"] = ["not_tested_due_temporal_failure"]
                item["final_status"] = "REJECTED_TEMPORAL"
            candidates.append(item)
        else:
            # keep the strongest near-misses for audit, but do not promote them
            h10 = rec["horizons"]["10"]
            e10 = h10["symbol_median_excess"]
            if support_ok(rec) and e10 is not None:
                rejected_discovery.append({
                    "id": ident, "family": rec["family"], "key": rec["key"],
                    "abs_h10_excess": abs(e10), "h10_excess": e10,
                    "reasons": reasons, "discovery": short_metrics(rec),
                })

    candidates.sort(key=lambda x: abs(x["discovery"]["h10"]["symbol_median_excess"] or 0.0), reverse=True)
    rejected_discovery.sort(key=lambda x: x["abs_h10_excess"], reverse=True)

    confirmed = [x for x in candidates if x["final_status"] == "OOS_CONFIRMED"]
    confirmed_pos = [x for x in confirmed if x["direction"] == "POSITIVE"]
    confirmed_neg = [x for x in confirmed if x["direction"] == "NEGATIVE"]
    temporal_survivors = [x for x in candidates if x["temporal_pass"]]

    family_counts = {}
    for fam in sorted(DENSE_FAMILIES | EVENT_FAMILIES):
        family_counts[fam] = {
            "discovery_keys": sum(1 for r in discovery_metrics.values() if r["family"] == fam),
            "discovery_candidates": sum(1 for x in candidates if x["family"] == fam),
            "temporal_survivors": sum(1 for x in temporal_survivors if x["family"] == fam),
            "oos_confirmed": sum(1 for x in confirmed if x["family"] == fam),
        }

    out = {
        "meta": {
            "study": "PURE_SLTD_STATE_PROBABILITY_V1",
            "status": "COMPLETE",
            "protocol": "PURE_SLTD_STATE_PROBABILITY_PROTOCOL_v1.md",
            "pure_sltd_base": "09cc68d20ba3b1005cc67caa5c459bb5b21c78d9",
            "formula_source": "5f9ea4d8fa434b54afdbf32a1cb21ef2f3cb4042",
            "chan_used": False,
            "representation": "FIRST_OBSERVED_CAUSAL",
            "outcome_entry": "NEXT_BAR_OPEN",
            "horizons": list(HORIZONS),
            "discovery": "79 stocks 2020-01-02..2023-12-31",
            "temporal_validation": "same 79 stocks 2024-01-01..2026-09-30",
            "external_oos": OOS10,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        },
        "summary": {
            "all_discovery_state_keys": len(discovery_metrics),
            "discovery_candidates": len(candidates),
            "temporal_survivors": len(temporal_survivors),
            "oos_confirmed": len(confirmed),
            "oos_confirmed_positive": len(confirmed_pos),
            "oos_confirmed_negative": len(confirmed_neg),
            "probability_map_candidate_allowed": bool(confirmed_pos and confirmed_neg),
        },
        "family_counts": family_counts,
        "candidates": candidates,
        "confirmed": confirmed,
        "top_discovery_near_misses": rejected_discovery[:30],
    }
    OUT_JSON.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# Pure SLTD State Probability Study v1 — Result",
        "",
        "Status: **COMPLETE**",
        "",
        "This study tests the predictive value of pure SLTD state information. Chan/缠论 is excluded.",
        "",
        "## Funnel",
        "",
        f"- Discovery state keys: **{len(discovery_metrics)}**",
        f"- Passed discovery gate: **{len(candidates)}**",
        f"- Passed 79-stock temporal validation: **{len(temporal_survivors)}**",
        f"- Confirmed on fresh 10-stock OOS: **{len(confirmed)}**",
        f"- OOS-confirmed positive states: **{len(confirmed_pos)}**",
        f"- OOS-confirmed negative states: **{len(confirmed_neg)}**",
        "",
        "## OOS-confirmed states",
        "",
    ]
    if confirmed:
        lines += [
            "| Direction | Family | State key | Discovery 10d excess | Temporal 10d excess | OOS 10d excess | OOS 20d excess |",
            "|---|---|---|---:|---:|---:|---:|",
        ]
        for x in confirmed:
            lines.append(
                f"| {x['direction']} | {x['family']} | `{x['key']}` | "
                f"{pct(x['discovery']['h10']['symbol_median_excess'])} | "
                f"{pct(x['temporal']['h10']['symbol_median_excess'])} | "
                f"{pct(x['external_oos']['h10']['symbol_median_excess'])} | "
                f"{pct(x['external_oos']['h20']['symbol_median_excess'])} |"
            )
    else:
        lines.append("**None.**")

    lines += [
        "",
        "## Family funnel",
        "",
        "| Family | Discovery keys | Discovery pass | Temporal pass | OOS confirmed |",
        "|---|---:|---:|---:|---:|",
    ]
    for fam, x in family_counts.items():
        lines.append(
            f"| {fam} | {x['discovery_keys']} | {x['discovery_candidates']} | "
            f"{x['temporal_survivors']} | {x['oos_confirmed']} |"
        )

    lines += [
        "",
        "## Decision",
        "",
    ]
    if confirmed_pos and confirmed_neg:
        lines += [
            "At least one positive and one negative state survived all gates.",
            "A separate `PURE_SLTD_PROBABILITY_MAP_CANDIDATE` is therefore allowed by protocol.",
        ]
    else:
        lines += [
            "The protocol does **not** allow an automatic trading-map rewrite yet.",
            "Without both positive and negative OOS-confirmed states, changing V7 BUY/SELL rules would be data-mining rather than evidence-led modification.",
        ]

    lines += [
        "",
        "No V7 trading rule was changed by this run.",
        "",
        "`PURE_SLTD_STATE_PROBABILITY_V1 = COMPLETE`",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps(out["summary"], indent=2, ensure_ascii=False))
    print("CONFIRMED")
    for x in confirmed:
        print(json.dumps({
            "direction": x["direction"], "family": x["family"], "key": x["key"],
            "disc10": x["discovery"]["h10"]["symbol_median_excess"],
            "temp10": x["temporal"]["h10"]["symbol_median_excess"],
            "oos10": x["external_oos"]["h10"]["symbol_median_excess"],
            "oos20": x["external_oos"]["h20"]["symbol_median_excess"],
        }, ensure_ascii=False))


if __name__ == "__main__":
    main()
