#!/usr/bin/env python3
"""A-share 50 integrated SLTD risk study — Stage A severe-risk validation.

No portfolio trading is performed here.
Only DEVELOPMENT 35 symbols are read.
"""
from __future__ import annotations

import json
import math
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
RESEARCH_ROOT = ROOT.parent
PHASE11 = RESEARCH_ROOT / "phase11"
PHASE14 = RESEARCH_ROOT / "phase14"
PROJECT = ROOT.parents[2] / "integrations" / "sltd_v7_siftalpha_v1"

sys.path.insert(0, str(PHASE11))
sys.path.insert(0, str(PHASE14))
sys.path.insert(0, str(PROJECT))

import pure_sltd_state_probability_v1 as p11  # noqa: E402
import sltd_state_score_risk_layer_stage_a_v3 as rv3  # noqa: E402
import sltd_state_score_momentum_stage_b_v3 as mom  # noqa: E402
import strategy as sltd  # noqa: E402

HORIZONS = (5, 10, 20)
DIMS = ("RETURN", "UP_PROB", "MFE", "MAE_SAFETY", "RR")
DISC_START = pd.Timestamp("2018-01-02")
DISC_END = pd.Timestamp("2022-12-30")
TEMP_START = pd.Timestamp("2023-01-03")
TEMP_END = pd.Timestamp("2024-12-31")

UNIVERSE_PATH = ROOT / "A_SHARE_50_UNIVERSE_V1.json"
DATA_DIR = ROOT / "ashare50_data_snapshot_v1"
MANIFEST_PATH = DATA_DIR / "manifest.json"
OUT_JSON = ROOT / "SLTD_ASHARE50_INTEGRATED_RISK_V1_STAGE_A_RESULT.json"
OUT_MD = ROOT / "SLTD_ASHARE50_INTEGRATED_RISK_V1_STAGE_A_RESULT.md"


def finite(x) -> bool:
    return x is not None and math.isfinite(float(x))


def candles_from_frame(frame: pd.DataFrame) -> list[dict]:
    return [
        {
            "date": pd.Timestamp(r.Date).strftime("%Y-%m-%d"),
            "open": float(r.Open),
            "high": float(r.High),
            "low": float(r.Low),
            "close": float(r.Close),
            "volume": 0.0 if pd.isna(r.Volume) else float(r.Volume),
        }
        for r in frame.itertuples(index=False)
    ]


def forward_max_dd(frame: pd.DataFrame, t: int, h: int) -> float:
    if t + h >= len(frame):
        return float("nan")
    entry = float(frame.iloc[t + 1]["Open"])
    if not math.isfinite(entry) or entry <= 0:
        return float("nan")
    peak = entry
    worst = 0.0
    for k in range(t + 1, t + h + 1):
        hi = float(frame.iloc[k]["High"])
        lo = float(frame.iloc[k]["Low"])
        peak = max(peak, hi)
        if peak <= 0:
            continue
        worst = min(worst, lo / peak - 1.0)
    return float(worst)


def build_symbol_rows(item: dict) -> pd.DataFrame:
    path = DATA_DIR / f'{item["code"]}.csv.gz'
    frame = pd.read_csv(path, parse_dates=["Date"])
    frame["Date"] = pd.to_datetime(frame["Date"]).dt.tz_localize(None)
    frame = frame.sort_values("Date").reset_index(drop=True)

    bars = candles_from_frame(frame)
    ledger = sltd.build_ledger(bars, item["code"])
    ledger_df = pd.DataFrame(ledger)
    ledger_df["date"] = pd.to_datetime(ledger_df["date"]).dt.tz_localize(None)

    rows = p11.build_symbol_rows(item["code"], frame, ledger_df).copy()
    rows["date"] = pd.to_datetime(rows["date"]).dt.tz_localize(None)

    date_to_idx = {pd.Timestamp(d): i for i, d in enumerate(frame["Date"])}
    for h in HORIZONS:
        vals = []
        for d in rows["date"]:
            idx = date_to_idx.get(pd.Timestamp(d))
            vals.append(forward_max_dd(frame, idx, h) if idx is not None else float("nan"))
        rows[f"fdd{h}"] = np.asarray(vals, dtype=float)

    rows["outcome_end_date"] = rows["date"].shift(-20)
    return rows


def segment_rows(df: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    m = (
        (df["date"] >= start)
        & (df["date"] <= end)
        & df["outcome_end_date"].notna()
        & (df["outcome_end_date"] <= end)
    )
    return df.loc[m].copy().reset_index(drop=True)


def discovery_support(family: str, n: int, symbols: int) -> bool:
    if family in rv3.DENSE:
        return n >= 250 and symbols >= 15
    return n >= 50 and symbols >= 8


def temporal_support(family: str, n: int, symbols: int) -> bool:
    if family in rv3.DENSE:
        return n >= 125 and symbols >= 8
    return n >= 25 and symbols >= 4


def adverse_negative_gate(drec: dict, trec: dict | None) -> tuple[bool, list[str]]:
    reasons = []
    if trec is None:
        return False, ["missing_temporal"]
    if not temporal_support(drec["family"], int(trec["n"]), int(trec["symbol_count"])):
        reasons.append("temporal_support")
    if not finite(drec.get("utility")) or float(drec["utility"]) >= 0:
        reasons.append("discovery_utility_not_negative")
    if not finite(trec.get("utility")) or float(trec["utility"]) >= 0:
        reasons.append("temporal_utility_not_negative")

    adverse = 0
    for dim in DIMS:
        dv = drec["raw_vector"].get(dim)
        tv = trec["raw_vector"].get(dim)
        if finite(dv) and finite(tv) and float(dv) < 0 and float(tv) < 0:
            adverse += 1
    if adverse < 3:
        reasons.append("adverse_dims_lt3")

    d10 = drec["horizons"]["10"]["return_excess"]
    t10 = trec["horizons"]["10"]["return_excess"]
    if not finite(d10) or not finite(t10) or float(d10) >= 0 or float(t10) >= 0:
        reasons.append("return10_not_adverse")

    return len(reasons) == 0, reasons


def attach_risk_level(df: pd.DataFrame, stable_negative: dict[str, float]) -> pd.DataFrame:
    out = df.copy()
    levels = []
    counts = []
    for r in out.itertuples(index=False):
        lvl, comps = mom.level_for_row(r, stable_negative)
        levels.append(float(lvl))
        counts.append(len(comps))
    out["risk_level"] = np.asarray(levels, dtype=float)
    out["risk_component_count"] = np.asarray(counts, dtype=int)
    return out


def symbol_baseline(df: pd.DataFrame, h: int) -> dict | None:
    ret = pd.to_numeric(df[f"ret{h}"], errors="coerce").to_numpy(float)
    mae = pd.to_numeric(df[f"mae{h}"], errors="coerce").to_numpy(float)
    mfe = pd.to_numeric(df[f"mfe{h}"], errors="coerce").to_numpy(float)
    fdd = pd.to_numeric(df[f"fdd{h}"], errors="coerce").to_numpy(float)
    ok = np.isfinite(ret) & np.isfinite(mae) & np.isfinite(mfe) & np.isfinite(fdd)
    if not ok.any():
        return None
    ret, mae, mfe, fdd = ret[ok], mae[ok], mfe[ok], fdd[ok]
    return {
        "ret_med": float(np.median(ret)),
        "mae_med": float(np.median(mae)),
        "mfe_med": float(np.median(mfe)),
        "loss_prob": float(np.mean(ret < 0)),
        "fdd_med": float(np.median(fdd)),
        "ret_p10": float(np.quantile(ret, 0.10)),
    }


def severe_metrics(frames: dict[str, pd.DataFrame], threshold: float) -> dict:
    out = {
        "threshold": float(threshold),
        "event_count": 0,
        "symbol_count": 0,
        "horizons": {},
    }
    represented = set()
    effects = {
        h: defaultdict(list)
        for h in HORIZONS
    }

    for symbol, df in frames.items():
        severe = df.loc[df["risk_level"] <= threshold].copy()
        if severe.empty:
            continue
        represented.add(symbol)
        out["event_count"] += int(len(severe))
        for h in HORIZONS:
            base = symbol_baseline(df, h)
            sev = symbol_baseline(severe, h)
            if not base or not sev:
                continue
            effects[h]["return_excess"].append(sev["ret_med"] - base["ret_med"])
            effects[h]["mae_safety_lift"].append(sev["mae_med"] - base["mae_med"])
            effects[h]["mfe_excess"].append(sev["mfe_med"] - base["mfe_med"])
            effects[h]["loss_prob_lift"].append(sev["loss_prob"] - base["loss_prob"])
            effects[h]["fdd_difference"].append(sev["fdd_med"] - base["fdd_med"])
            effects[h]["tail_p10_difference"].append(sev["ret_p10"] - base["ret_p10"])

    out["symbol_count"] = len(represented)
    for h in HORIZONS:
        rec = {}
        for k, vals in effects[h].items():
            rec[k] = float(np.median(vals)) if vals else None
            rec[f"{k}_symbol_n"] = int(len(vals))
        out["horizons"][str(h)] = rec
    return out


def main():
    universe = json.loads(UNIVERSE_PATH.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if manifest.get("status") != "PASS":
        raise RuntimeError("A-share data audit is not PASS")

    dev = [x for x in universe["symbols"] if x["role"] == "DEVELOPMENT"]
    fresh = [x for x in universe["symbols"] if x["role"] == "FRESH_OOS"]
    if len(dev) != 35 or len(fresh) != 15:
        raise RuntimeError("frozen 35/15 split mismatch")

    # Important: Stage A reads DEVELOPMENT files only.
    all_dev = {x["code"]: build_symbol_rows(x) for x in dev}
    if len(all_dev) != 35:
        raise RuntimeError("expected 35 development symbols")

    disc_frames = {s: segment_rows(df, DISC_START, DISC_END) for s, df in all_dev.items()}
    temp_frames = {s: segment_rows(df, TEMP_START, TEMP_END) for s, df in all_dev.items()}

    discovery = rv3.aggregate_split(disc_frames, "A35_DISCOVERY_2018_2022")
    temporal = rv3.aggregate_split(temp_frames, "A35_TEMPORAL_2023_2024")

    for rec in discovery.values():
        rec["support_pass"] = discovery_support(rec["family"], int(rec["n"]), int(rec["symbol_count"]))
    for rec in temporal.values():
        rec["support_pass"] = temporal_support(rec["family"], int(rec["n"]), int(rec["symbol_count"]))

    norm = rv3.robust_normalization(discovery)
    for rec in discovery.values():
        rec.update(rv3.apply_utility(rec, norm))
    for rec in temporal.values():
        rec.update(rv3.apply_utility(rec, norm))

    stable_negative = []
    for ident, drec in discovery.items():
        if not drec["support_pass"]:
            continue
        trec = temporal.get(ident)
        passed, reasons = adverse_negative_gate(drec, trec)
        if passed:
            stable_negative.append({
                "id": ident,
                "family": drec["family"],
                "key": drec["key"],
                "component": drec["component"],
                "discovery": drec,
                "temporal": trec,
                "reasons": reasons,
            })

    weights = {x["id"]: float(x["discovery"]["utility"]) for x in stable_negative}
    components = sorted(set(x["component"] for x in stable_negative))

    disc_level = {s: attach_risk_level(df, weights) for s, df in disc_frames.items()}
    temp_level = {s: attach_risk_level(df, weights) for s, df in temp_frames.items()}

    negative_levels = np.asarray([
        float(v)
        for df in disc_level.values()
        for v in df["risk_level"].to_numpy(float)
        if math.isfinite(float(v)) and float(v) < 0
    ], dtype=float)
    if not len(negative_levels):
        raise RuntimeError("no negative Discovery risk levels")
    threshold = float(np.quantile(negative_levels, 0.25))

    disc_severe = severe_metrics(disc_level, threshold)
    temp_severe = severe_metrics(temp_level, threshold)

    t10 = temp_severe["horizons"]["10"]
    t20 = temp_severe["horizons"]["20"]
    gates = {
        "temporal_event_count_ge_500": temp_severe["event_count"] >= 500,
        "temporal_symbol_count_ge_20": temp_severe["symbol_count"] >= 20,
        "temporal_ret10_excess_negative": finite(t10.get("return_excess")) and t10["return_excess"] < 0,
        "temporal_ret20_excess_negative": finite(t20.get("return_excess")) and t20["return_excess"] < 0,
        "temporal_mae10_safety_negative": finite(t10.get("mae_safety_lift")) and t10["mae_safety_lift"] < 0,
        "temporal_mae20_safety_negative": finite(t20.get("mae_safety_lift")) and t20["mae_safety_lift"] < 0,
        "temporal_loss10_lift_positive": finite(t10.get("loss_prob_lift")) and t10["loss_prob_lift"] > 0,
        "temporal_loss20_lift_positive": finite(t20.get("loss_prob_lift")) and t20["loss_prob_lift"] > 0,
        "temporal_fdd10_worse": finite(t10.get("fdd_difference")) and t10["fdd_difference"] < 0,
        "temporal_fdd20_worse": finite(t20.get("fdd_difference")) and t20["fdd_difference"] < 0,
    }
    decision = "PROMOTED_TO_INTEGRATED_HOLDOUT" if all(gates.values()) else "REJECTED_NOT_ADMITTED"

    ranked = sorted(stable_negative, key=lambda x: float(x["discovery"]["utility"]))

    result = {
        "meta": {
            "study": "SLTD_ASHARE50_INTEGRATED_RISK_V1_STAGE_A",
            "protocol": "SLTD_ASHARE50_INTEGRATED_RISK_V1_PROTOCOL.md",
            "amendment": "SLTD_ASHARE50_INTEGRATED_RISK_V1_AMENDMENT_A.md",
            "market": "China A-share main board",
            "development_symbols": [x["code"] for x in dev],
            "fresh_symbols_read_for_performance": False,
            "fresh_oos_consumed": False,
            "us_fitted_weights_used": False,
            "chan_used": False,
            "score_momentum_used": False,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        },
        "normalization": norm,
        "summary": {
            "discovery_state_keys": len(discovery),
            "discovery_supported": sum(1 for x in discovery.values() if x["support_pass"]),
            "stable_negative_states": len(stable_negative),
            "stable_negative_components": components,
            "severe_threshold": threshold,
        },
        "discovery_severe": disc_severe,
        "temporal_severe": temp_severe,
        "stable_negative_states_ranked": ranked,
        "gates": gates,
        "decision": decision,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    def pct(v):
        return "—" if not finite(v) else f"{100*float(v):.3f}%"

    lines = [
        "# SLTD A-share 50 Integrated Risk v1 — Stage A Result",
        "",
        f"Status: **{decision}**",
        "",
        "- Market: **China A-share main board**",
        "- Development symbols used: **35**",
        "- Fresh OOS performance read: **NO**",
        "- US fitted state weights used: **NO**",
        "- Chan/缠论: **NOT USED**",
        "- Score Momentum: **NOT USED**",
        "",
        "## State funnel",
        "",
        f"- Discovery state keys: **{len(discovery)}**",
        f"- Discovery support-pass: **{sum(1 for x in discovery.values() if x['support_pass'])}**",
        f"- Temporally stable negative states: **{len(stable_negative)}**",
        f"- Stable negative components: **{', '.join(components) if components else 'none'}**",
        f"- Severe threshold (Discovery negative-risk 25th percentile): **{threshold:.5f}**",
        "",
        "## Severe Risk diagnostics",
        "",
        "| Split | Events | Symbols | 10d ret excess | 20d ret excess | 10d MAE safety | 20d MAE safety | 10d loss lift | 20d loss lift | 10d FDD diff | 20d FDD diff |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name, rec in (("Discovery", disc_severe), ("Temporal", temp_severe)):
        h10=rec["horizons"]["10"]; h20=rec["horizons"]["20"]
        lines.append(
            f"| {name} | {rec['event_count']} | {rec['symbol_count']} | "
            f"{pct(h10.get('return_excess'))} | {pct(h20.get('return_excess'))} | "
            f"{pct(h10.get('mae_safety_lift'))} | {pct(h20.get('mae_safety_lift'))} | "
            f"{pct(h10.get('loss_prob_lift'))} | {pct(h20.get('loss_prob_lift'))} | "
            f"{pct(h10.get('fdd_difference'))} | {pct(h20.get('fdd_difference'))} |"
        )

    lines += [
        "",
        "## Strongest A-share stable negative states",
        "",
        "| Component | State | Discovery utility | Temporal utility | D 10d return excess | T 10d return excess |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for x in ranked[:25]:
        d=x["discovery"]; t=x["temporal"]
        lines.append(
            f"| {x['component']} | `{x['id']}` | {d['utility']:.3f} | {t['utility']:.3f} | "
            f"{pct(d['horizons']['10']['return_excess'])} | {pct(t['horizons']['10']['return_excess'])} |"
        )

    lines += ["", "## Gates", ""]
    for k,v in gates.items():
        lines.append(f"- {k}: **{'PASS' if v else 'FAIL'}**")
    lines += [
        "",
        f"`SLTD_ASHARE50_INTEGRATED_RISK_V1_STAGE_A = {decision}`",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps({
        "decision": decision,
        "summary": result["summary"],
        "temporal_severe": temp_severe,
        "gates": gates,
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
