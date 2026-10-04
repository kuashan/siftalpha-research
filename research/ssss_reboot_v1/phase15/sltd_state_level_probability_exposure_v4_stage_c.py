#!/usr/bin/env python3
"""SLTD State Level -> Probability Exposure v4 — Stage C temporal validation."""
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
PHASE14 = ROOT.parent / "phase14"
sys.path.insert(0, str(PHASE14))
import sltd_state_score_momentum_stage_b_v3 as b  # noqa: E402

OUT_JSON = ROOT / "SLTD_STATE_LEVEL_PROBABILITY_EXPOSURE_V4_STAGE_C_RESULT.json"
OUT_MD = ROOT / "SLTD_STATE_LEVEL_PROBABILITY_EXPOSURE_V4_STAGE_C_RESULT.md"


def fit_isotonic_probability(x: np.ndarray, y: np.ndarray) -> dict:
    mask = np.isfinite(x) & np.isfinite(y)
    x = np.asarray(x[mask], dtype=float)
    y = np.asarray(y[mask], dtype=float)
    if len(x) < 1000:
        raise RuntimeError("insufficient Discovery rows for isotonic calibration")

    order = np.argsort(x, kind="mergesort")
    x = x[order]; y = y[order]

    # Aggregate exact LEVEL values.
    ux, inv = np.unique(x, return_inverse=True)
    weights = np.bincount(inv).astype(float)
    succ = np.bincount(inv, weights=y).astype(float)

    blocks = []
    for xv, w, s in zip(ux, weights, succ):
        blocks.append({"w": float(w), "s": float(s), "xsum": float(xv * w)})
        while len(blocks) >= 2:
            p0 = blocks[-2]["s"] / blocks[-2]["w"]
            p1 = blocks[-1]["s"] / blocks[-1]["w"]
            if p0 <= p1 + 1e-15:
                break
            right = blocks.pop()
            left = blocks.pop()
            blocks.append({
                "w": left["w"] + right["w"],
                "s": left["s"] + right["s"],
                "xsum": left["xsum"] + right["xsum"],
            })

    knots_x = np.asarray([z["xsum"] / z["w"] for z in blocks], dtype=float)
    knots_p = np.asarray([z["s"] / z["w"] for z in blocks], dtype=float)
    if np.any(np.diff(knots_x) <= 0):
        raise RuntimeError("isotonic knot x must be strictly increasing")
    if np.any(np.diff(knots_p) < -1e-12):
        raise RuntimeError("isotonic probabilities must be monotone")

    return {
        "knots_x": knots_x,
        "knots_p": knots_p,
        "block_weights": np.asarray([z["w"] for z in blocks], dtype=float),
        "discovery_favorable_rate": float(np.mean(y)),
        "discovery_n": int(len(y)),
    }


def predict_iso(model: dict, x: np.ndarray) -> np.ndarray:
    return np.interp(
        np.asarray(x, dtype=float),
        model["knots_x"],
        model["knots_p"],
        left=float(model["knots_p"][0]),
        right=float(model["knots_p"][-1]),
    )


def target_from_probability(p: np.ndarray) -> np.ndarray:
    q = np.floor(np.asarray(p, dtype=float) * 4.0 + 0.5) / 4.0
    return np.clip(q, 0.0, 1.0)


def bucket_metrics(target: np.ndarray, p: np.ndarray, y: np.ndarray) -> dict:
    out = {}
    for t in sorted(set(float(z) for z in target)):
        m = np.isclose(target, t)
        yy = y[m]
        pp = p[m]
        out[f"{t:.2f}"] = {
            "count": int(m.sum()),
            "mean_probability": float(np.mean(pp)) if len(pp) else None,
            "favorable_rate": float(np.mean(yy > 0)) if len(yy) else None,
            "median_forward_utility": float(np.median(yy)) if len(yy) else None,
        }
    return out


def main():
    stable = b.load_stable_utilities()
    panel = b.build_panel(stable)

    disc = b.segment(panel, b.DISC_START, b.DISC_END).reset_index(drop=True)
    temp = b.segment(panel, b.TEMP_START, b.TEMP_END).reset_index(drop=True)

    baselines = b.training_baselines(disc)
    raw_d = b.raw_forward_dims(disc, baselines)
    label_scales = b.label_scales(raw_d)
    yd = b.utility_from_raw(raw_d, label_scales)

    raw_t = b.raw_forward_dims(temp, baselines)
    yt = b.utility_from_raw(raw_t, label_scales)

    xd = disc["level"].to_numpy(float)
    xt = temp["level"].to_numpy(float)

    md = np.isfinite(xd) & np.isfinite(yd)
    mt = np.isfinite(xt) & np.isfinite(yt)
    xd = xd[md]; yd = yd[md]
    xt = xt[mt]; yt = yt[mt]

    fav_d = (yd > 0).astype(float)
    model = fit_isotonic_probability(xd, fav_d)
    p_t = predict_iso(model, xt)
    target_t = target_from_probability(p_t)

    base_p = float(model["discovery_favorable_rate"])
    brier_const = float(np.mean(((yt > 0).astype(float) - base_p) ** 2))
    brier_iso = float(np.mean(((yt > 0).astype(float) - p_t) ** 2))
    brier_improvement = float((brier_const - brier_iso) / brier_const) if brier_const > 0 else None
    corr = b.rank_corr(p_t, yt)
    buckets = bucket_metrics(target_t, p_t, yt)

    used = sorted(float(k) for k, v in buckets.items() if v["count"] > 0)
    lo = f"{used[0]:.2f}"
    hi = f"{used[-1]:.2f}"
    gates = {
        "temporal_brier_improves": brier_iso < brier_const,
        "temporal_probability_utility_rank_corr_positive": corr is not None and corr > 0,
        "highest_bucket_utility_gt_lowest": (
            buckets[hi]["median_forward_utility"] is not None
            and buckets[lo]["median_forward_utility"] is not None
            and buckets[hi]["median_forward_utility"] > buckets[lo]["median_forward_utility"]
        ),
        "at_least_three_buckets_used": len(used) >= 3,
        "extreme_bucket_support": buckets[hi]["count"] >= 500 and buckets[lo]["count"] >= 500,
    }
    decision = "PROMOTED_TO_FRESH_OOS" if all(gates.values()) else "REJECTED_NOT_ADMITTED"

    model_json = {
        "knots_x": [float(v) for v in model["knots_x"]],
        "knots_p": [float(v) for v in model["knots_p"]],
        "block_weights": [int(round(v)) for v in model["block_weights"]],
        "discovery_favorable_rate": base_p,
        "discovery_n": model["discovery_n"],
    }

    out = {
        "meta": {
            "study": "SLTD_STATE_LEVEL_PROBABILITY_EXPOSURE_V4_STAGE_C",
            "protocol": "SLTD_STATE_LEVEL_PROBABILITY_EXPOSURE_V4_PROTOCOL.md",
            "score_source_commit": "e996e4344e5c40425bc93253d2e00501bacb3eb8",
            "v3_closeout": "acf88b42ff9c80834423d228b21e13ecd0fbb9e9",
            "chan_used": False,
            "v7_used_as_signal": False,
            "momentum_used": False,
            "fresh_oos_consumed": False,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        },
        "stable_state_count": len(stable),
        "calibration": model_json,
        "label_scales": label_scales,
        "temporal": {
            "n": int(len(yt)),
            "constant_brier": brier_const,
            "isotonic_brier": brier_iso,
            "relative_brier_improvement": brier_improvement,
            "probability_forward_utility_rank_corr": corr,
            "mean_target_exposure": float(np.mean(target_t)),
            "used_targets": used,
            "buckets": buckets,
        },
        "gates": gates,
        "decision": decision,
    }
    OUT_JSON.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# SLTD State Level -> Probability Exposure v4 — Stage C Result",
        "",
        f"Status: **{decision}**",
        "",
        "Momentum: **NOT USED**",
        "Chan/缠论: **NOT USED**",
        "Fresh OOS consumed: **NO**",
        "",
        "## Discovery calibration",
        "",
        f"- Stable states: **{len(stable)}**",
        f"- Discovery labeled rows: **{model['discovery_n']}**",
        f"- Discovery favorable rate: **{100*base_p:.2f}%**",
        f"- Isotonic pooled blocks / knots: **{len(model['knots_x'])}**",
        "",
        "## Temporal validation",
        "",
        f"- Temporal rows: **{len(yt)}**",
        f"- Constant-probability Brier: **{brier_const:.6f}**",
        f"- Isotonic Brier: **{brier_iso:.6f}**",
        f"- Relative Brier improvement: **{100*brier_improvement:.3f}%**",
        f"- Rank corr(probability, forward utility): **{corr:.5f}**",
        f"- Mean target exposure: **{100*np.mean(target_t):.2f}%**",
        "",
        "## Target buckets",
        "",
        "| Target | Count | Mean calibrated p | Favorable rate | Median forward utility |",
        "|---:|---:|---:|---:|---:|",
    ]
    for k in sorted(buckets, key=float):
        z=buckets[k]
        lines.append(
            f"| {100*float(k):.0f}% | {z['count']} | {100*z['mean_probability']:.2f}% | "
            f"{100*z['favorable_rate']:.2f}% | {z['median_forward_utility']:.5f} |"
        )
    lines += ["", "## Gates", ""]
    for k,v in gates.items():
        lines.append(f"- {k}: **{'PASS' if v else 'FAIL'}**")
    lines += [
        "",
        "Temporal is validation/consistency only; it is not the final independent Fresh OOS.",
        "",
        f"`SLTD_STATE_LEVEL_PROBABILITY_EXPOSURE_V4_STAGE_C = {decision}`",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps({
        "decision": decision,
        "calibration_knots": len(model["knots_x"]),
        "temporal_brier_improvement": brier_improvement,
        "rank_corr": corr,
        "mean_target_exposure": float(np.mean(target_t)),
        "buckets": buckets,
        "gates": gates,
    }, indent=2))


if __name__ == "__main__":
    main()
