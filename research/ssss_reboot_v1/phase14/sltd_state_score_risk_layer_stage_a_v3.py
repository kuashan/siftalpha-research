#!/usr/bin/env python3
"""Stage A for SLTD State Score Risk-Exposure v3.\n\nCI_TRIGGER_AFTER_WORKFLOW_REGISTRATION: workflow already exists before this push.

Build a risk-adjusted pure-SLTD state layer from the frozen original 79-stock data.
No portfolio mapping is performed here.
"""
from __future__ import annotations

import json
import math
import sys
from collections import defaultdict, Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
PHASE11 = ROOT.parent / "phase11"
sys.path.insert(0, str(PHASE11))

import pure_sltd_state_probability_v1 as p11  # noqa: E402

HORIZONS = (5, 10, 20)
DIMS = ("RETURN", "UP_PROB", "MFE", "MAE_SAFETY", "RR")
OUT_JSON = ROOT / "SLTD_STATE_SCORE_RISK_LAYER_STAGE_A_V3_RESULT.json"
OUT_MD = ROOT / "SLTD_STATE_SCORE_RISK_LAYER_STAGE_A_V3_RESULT.md"

DISCOVERY_START = pd.Timestamp("2020-01-02")
DISCOVERY_END = pd.Timestamp("2023-12-31")
TEMPORAL_START = pd.Timestamp("2024-01-01")
TEMPORAL_END = pd.Timestamp("2026-09-30")

DENSE = {"F1_COLOR_AGE", "F2_COLOR_AGE_ORIGIN", "F3_COLOR_AGE_INNER",
         "F4_COLOR_AGE_SLOWPOS", "F5_COLOR_AGE_SLOWTREND"}
EVENT = {"F6_COLOR_AGE_EVENT", "F7_COLOR_AGE_EVENT_SUBTYPE", "F8_TRANSITION_EVENT"}

COMPONENT = {
    "F1_COLOR_AGE": "REGIME",
    "F2_COLOR_AGE_ORIGIN": "REGIME",
    "F3_COLOR_AGE_INNER": "INNER",
    "F4_COLOR_AGE_SLOWPOS": "SLOW",
    "F5_COLOR_AGE_SLOWTREND": "SLOW",
    "F6_COLOR_AGE_EVENT": "EVENT",
    "F7_COLOR_AGE_EVENT_SUBTYPE": "EVENT",
    "F8_TRANSITION_EVENT": "TRANSITION",
}


def finite(x):
    return x is not None and math.isfinite(float(x))


def sgn(x):
    if not finite(x) or abs(float(x)) < 1e-15:
        return 0
    return 1 if float(x) > 0 else -1


def median_or_none(xs):
    vals = [float(x) for x in xs if finite(x)]
    return float(np.median(vals)) if vals else None


def support_ok(family: str, n: int, symbol_count: int) -> bool:
    if family in DENSE:
        return n >= 500 and symbol_count >= 30
    return n >= 80 and symbol_count >= 15


def temporal_symbol_floor(family: str) -> int:
    return 15 if family in DENSE else 8


def baseline_for_symbol(df: pd.DataFrame) -> dict:
    out = {}
    for h in HORIZONS:
        ret = pd.to_numeric(df[f"ret{h}"], errors="coerce").dropna().to_numpy(float)
        mfe = pd.to_numeric(df[f"mfe{h}"], errors="coerce").dropna().to_numpy(float)
        mae = pd.to_numeric(df[f"mae{h}"], errors="coerce").dropna().to_numpy(float)
        if not len(ret) or not len(mfe) or not len(mae):
            continue
        med_mfe = float(np.median(mfe))
        med_mae = float(np.median(mae))
        rr = max(med_mfe, 1e-6) / max(abs(med_mae), 1e-6)
        out[h] = {
            "return": float(np.median(ret)),
            "up_prob": float(np.mean(ret > 0)),
            "mfe": med_mfe,
            "mae": med_mae,
            "rr": rr,
        }
    return out


def aggregate_split(frames: dict[str, pd.DataFrame], split_name: str) -> dict[str, dict]:
    baselines = {s: baseline_for_symbol(df) for s, df in frames.items()}

    bucket: dict[tuple[str, str], dict[str, list[object]]] = defaultdict(lambda: defaultdict(list))
    for s, df in frames.items():
        for r in df.itertuples(index=False):
            if not finite(getattr(r, "ret20", None)):
                continue
            for family, key in p11.keys_for_row(r):
                bucket[(family, key)][s].append(r)

    results = {}
    for (family, key), by_symbol in bucket.items():
        n = sum(len(v) for v in by_symbol.values())
        symbols = sorted(by_symbol)
        rec = {
            "split": split_name,
            "family": family,
            "key": key,
            "component": COMPONENT[family],
            "n": n,
            "symbol_count": len(symbols),
            "support_pass": support_ok(family, n, len(symbols)),
            "horizons": {},
        }

        for h in HORIZONS:
            lifts = {d: [] for d in DIMS}
            for s in symbols:
                base = baselines.get(s, {}).get(h)
                if not base:
                    continue
                rows = by_symbol[s]
                rets = np.asarray([float(getattr(r, f"ret{h}")) for r in rows if finite(getattr(r, f"ret{h}", None))], dtype=float)
                mfes = np.asarray([float(getattr(r, f"mfe{h}")) for r in rows if finite(getattr(r, f"mfe{h}", None))], dtype=float)
                maes = np.asarray([float(getattr(r, f"mae{h}")) for r in rows if finite(getattr(r, f"mae{h}", None))], dtype=float)
                if not len(rets) or not len(mfes) or not len(maes):
                    continue

                med_ret = float(np.median(rets))
                up_prob = float(np.mean(rets > 0))
                med_mfe = float(np.median(mfes))
                med_mae = float(np.median(maes))
                rr = max(med_mfe, 1e-6) / max(abs(med_mae), 1e-6)

                lifts["RETURN"].append(med_ret - base["return"])
                lifts["UP_PROB"].append(up_prob - base["up_prob"])
                lifts["MFE"].append(med_mfe - base["mfe"])
                lifts["MAE_SAFETY"].append(med_mae - base["mae"])
                lifts["RR"].append(math.log(rr) - math.log(base["rr"]))

            rec["horizons"][str(h)] = {
                "return_excess": median_or_none(lifts["RETURN"]),
                "up_prob_lift": median_or_none(lifts["UP_PROB"]),
                "mfe_excess": median_or_none(lifts["MFE"]),
                "mae_safety_lift": median_or_none(lifts["MAE_SAFETY"]),
                "rr_log_lift": median_or_none(lifts["RR"]),
                "symbol_effect_count": max((len(v) for v in lifts.values()), default=0),
            }

        raw = {
            "RETURN": median_or_none([rec["horizons"][str(h)]["return_excess"] for h in HORIZONS]),
            "UP_PROB": median_or_none([rec["horizons"][str(h)]["up_prob_lift"] for h in HORIZONS]),
            "MFE": median_or_none([rec["horizons"][str(h)]["mfe_excess"] for h in HORIZONS]),
            "MAE_SAFETY": median_or_none([rec["horizons"][str(h)]["mae_safety_lift"] for h in HORIZONS]),
            "RR": median_or_none([rec["horizons"][str(h)]["rr_log_lift"] for h in HORIZONS]),
        }
        rec["raw_vector"] = raw
        results[f"{family}::{key}"] = rec

    return results


def robust_normalization(discovery: dict[str, dict]) -> dict:
    norm = {}
    supported = [r for r in discovery.values() if r["support_pass"]]
    for d in DIMS:
        vals = np.asarray([r["raw_vector"][d] for r in supported if finite(r["raw_vector"][d])], dtype=float)
        if not len(vals):
            norm[d] = {"active": False, "center": 0.0, "scale": None, "method": "none"}
            continue
        absvals = np.abs(vals)
        scale = float(np.median(absvals))
        method = "MEDIAN_ABS_FROM_ZERO"
        if scale <= 1e-15:
            scale = float(np.quantile(absvals, 0.75))
            method = "P75_ABS_FROM_ZERO"
        if scale <= 1e-15:
            norm[d] = {"active": False, "center": 0.0, "scale": None, "method": "degenerate"}
        else:
            norm[d] = {"active": True, "center": 0.0, "scale": scale, "method": method}
    return norm


def apply_utility(rec: dict, norm: dict) -> dict:
    zs = {}
    for d in DIMS:
        x = rec["raw_vector"].get(d)
        n = norm[d]
        if finite(x) and n["active"]:
            zs[d] = (float(x) - float(n["center"])) / float(n["scale"])
        else:
            zs[d] = None
    active = [v for v in zs.values() if finite(v)]
    util = float(np.median(active)) if active else None
    return {"z_vector": zs, "utility": util}


def temporal_gate(drec: dict, trec: dict | None) -> tuple[bool, list[str]]:
    reasons = []
    if trec is None:
        return False, ["missing_temporal_state"]
    if trec["symbol_count"] < temporal_symbol_floor(drec["family"]):
        reasons.append("temporal_symbol_coverage")

    du = drec.get("utility")
    tu = trec.get("utility")
    if sgn(du) == 0 or sgn(tu) != sgn(du):
        reasons.append("utility_sign")

    same_dim = 0
    for d in DIMS:
        ds = sgn(drec["raw_vector"].get(d))
        ts = sgn(trec["raw_vector"].get(d))
        if ds != 0 and ts == ds:
            same_dim += 1
    if same_dim < 3:
        reasons.append("raw_dimension_signs_lt3")

    d10 = drec["horizons"]["10"]["return_excess"]
    t10 = trec["horizons"]["10"]["return_excess"]
    if sgn(d10) == 0 or sgn(t10) != sgn(d10):
        reasons.append("return10_sign")

    return len(reasons) == 0, reasons


def nested_audit(frames: dict[str, pd.DataFrame], stable_ids: set[str]) -> dict:
    regime_pairs = Counter()
    event_pairs = Counter()

    for df in frames.values():
        for r in df.itertuples(index=False):
            keys = p11.keys_for_row(r)
            ids = [(fam, key, f"{fam}::{key}") for fam, key in keys]

            f1 = [(k, i) for fam, k, i in ids if fam == "F1_COLOR_AGE" and i in stable_ids]
            f2 = [(k, i) for fam, k, i in ids if fam == "F2_COLOR_AGE_ORIGIN" and i in stable_ids]
            for _, i1 in f1:
                for _, i2 in f2:
                    regime_pairs[(i1, i2)] += 1

            f6 = [(k, i) for fam, k, i in ids if fam == "F6_COLOR_AGE_EVENT" and i in stable_ids]
            f7 = [(k, i) for fam, k, i in ids if fam == "F7_COLOR_AGE_EVENT_SUBTYPE" and i in stable_ids]
            for k6, i6 in f6:
                prefix = k6 + "|"
                for k7, i7 in f7:
                    if k7.startswith(prefix):
                        event_pairs[(i6, i7)] += 1

    def top(counter):
        return [
            {"broader": a, "specific": b, "cooccurrence_bars": n}
            for (a, b), n in counter.most_common(20)
        ]

    return {"regime_f1_f2": top(regime_pairs), "event_f6_f7": top(event_pairs)}


def main():
    all79 = {}
    for batch, symbols in p11.core.BATCHES.items():
        for symbol in symbols:
            frame, ledger = p11.load_79_symbol(batch, symbol)
            all79[symbol] = p11.build_symbol_rows(symbol, frame, ledger)
    if len(all79) != 79:
        raise RuntimeError(f"expected 79 stocks, got {len(all79)}")

    discovery_frames = p11.subset_rows(all79, DISCOVERY_START, DISCOVERY_END)
    temporal_frames = p11.subset_rows(all79, TEMPORAL_START, TEMPORAL_END)

    discovery = aggregate_split(discovery_frames, "DISCOVERY_79_2020_2023")
    temporal = aggregate_split(temporal_frames, "TEMPORAL_79_2024_2026Q3")
    norm = robust_normalization(discovery)

    for rec in discovery.values():
        rec.update(apply_utility(rec, norm))
    for rec in temporal.values():
        rec.update(apply_utility(rec, norm))

    supported_ids = sorted([i for i, r in discovery.items() if r["support_pass"]])
    stable = []
    for ident in supported_ids:
        drec = discovery[ident]
        trec = temporal.get(ident)
        passed, reasons = temporal_gate(drec, trec)
        item = {
            "id": ident,
            "family": drec["family"],
            "key": drec["key"],
            "component": drec["component"],
            "discovery": drec,
            "temporal": trec,
            "temporal_stable": passed,
            "reasons": reasons,
        }
        stable.append(item)

    stable_pass = [x for x in stable if x["temporal_stable"]]
    pos = [x for x in stable_pass if sgn(x["discovery"]["utility"]) > 0]
    neg = [x for x in stable_pass if sgn(x["discovery"]["utility"]) < 0]
    components = sorted(set(x["component"] for x in stable_pass))

    decision = "IMPLEMENTED_AND_VERIFIED" if pos and neg and len(components) >= 3 else "REJECTED_NOT_ADMITTED"

    family_funnel = {}
    for fam in sorted(DENSE | EVENT):
        family_funnel[fam] = {
            "discovery_keys": sum(1 for r in discovery.values() if r["family"] == fam),
            "discovery_supported": sum(1 for r in discovery.values() if r["family"] == fam and r["support_pass"]),
            "temporal_stable": sum(1 for x in stable_pass if x["family"] == fam),
        }

    stable_ids = {x["id"] for x in stable_pass}
    nested = nested_audit(discovery_frames, stable_ids)

    ranked = sorted(
        stable_pass,
        key=lambda x: abs(float(x["discovery"]["utility"])),
        reverse=True,
    )

    out = {
        "meta": {
            "study": "SLTD_STATE_SCORE_RISK_EXPOSURE_V3_STAGE_A",
            "status": decision,
            "master_protocol": "SLTD_STATE_SCORE_RISK_EXPOSURE_V3_PROTOCOL.md",
            "amendments": ["SLTD_STATE_SCORE_RISK_EXPOSURE_V3_AMENDMENT_A.md", "SLTD_STATE_SCORE_RISK_EXPOSURE_V3_AMENDMENT_B.md"],
            "branch_base": "a7b10493450867960e9bdd8ff05f9e3905e854a6",
            "pure_sltd_base": "09cc68d20ba3b1005cc67caa5c459bb5b21c78d9",
            "chan_used": False,
            "representation": "FIRST_OBSERVED_CAUSAL",
            "outcome_entry": "NEXT_BAR_OPEN",
            "discovery": "79 stocks 2020-01-02..2023-12-31",
            "temporal": "same 79 stocks 2024-01-01..2026-09-30",
            "fresh_oos_consumed": False,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        },
        "normalization": norm,
        "summary": {
            "discovery_state_keys": len(discovery),
            "discovery_supported": len(supported_ids),
            "temporal_stable": len(stable_pass),
            "stable_positive": len(pos),
            "stable_negative": len(neg),
            "stable_components": components,
            "decision": decision,
        },
        "family_funnel": family_funnel,
        "stable_states_ranked": ranked,
        "nested_overlap_audit": nested,
        "all_discovery_states": discovery,
        "all_temporal_states": temporal,
    }

    OUT_JSON.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    def pct(x):
        return "—" if not finite(x) else f"{100*float(x):.2f}%"

    lines = [
        "# SLTD State Score Risk-Exposure v3 — Stage A Result",
        "",
        f"Status: **{decision}**",
        "",
        "Chan/缠论: **NOT USED**",
        "Representation: **FIRST_OBSERVED / causal**",
        "Fresh OOS consumed: **NO**",
        "",
        "## Funnel",
        "",
        f"- Discovery state keys: **{len(discovery)}**",
        f"- Discovery support-pass states: **{len(supported_ids)}**",
        f"- Temporal-stable states: **{len(stable_pass)}**",
        f"- Stable positive utilities: **{len(pos)}**",
        f"- Stable negative utilities: **{len(neg)}**",
        f"- Stable live components: **{', '.join(components) if components else 'none'}**",
        "",
        "## Family funnel",
        "",
        "| Family | Discovery keys | Supported | Temporal stable |",
        "|---|---:|---:|---:|",
    ]
    for fam, r in family_funnel.items():
        lines.append(f"| {fam} | {r['discovery_keys']} | {r['discovery_supported']} | {r['temporal_stable']} |")

    lines += [
        "",
        "## Strongest temporally stable states",
        "",
        "| Direction | Component | State | Discovery utility | Temporal utility | 10d return excess D/T |",
        "|---|---|---|---:|---:|---:|",
    ]
    for x in ranked[:25]:
        d = x["discovery"]
        t = x["temporal"]
        direction = "POSITIVE" if d["utility"] > 0 else "NEGATIVE"
        lines.append(
            f"| {direction} | {x['component']} | `{x['family']}::{x['key']}` | "
            f"{d['utility']:.3f} | {t['utility']:.3f} | "
            f"{pct(d['horizons']['10']['return_excess'])} / {pct(t['horizons']['10']['return_excess'])} |"
        )

    lines += [
        "",
        "## What Stage A means",
        "",
        "Stage A does not define a trading system and does not map score to exposure.",
        "It only determines whether a bidirectional, risk-adjusted SLTD state layer survives temporal validation.",
        "",
        f"`SLTD_STATE_SCORE_RISK_EXPOSURE_V3_STAGE_A = {decision}`",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps({
        "decision": decision,
        "summary": out["summary"],
        "top_states": [
            {
                "id": x["id"],
                "component": x["component"],
                "discovery_utility": x["discovery"]["utility"],
                "temporal_utility": x["temporal"]["utility"],
            }
            for x in ranked[:10]
        ],
    }, indent=2))


if __name__ == "__main__":
    main()
