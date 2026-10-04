#!/usr/bin/env python3
"""SLTD Score Level -> Relative Ranking v1 — Stage A."""
from __future__ import annotations

import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
PHASE14 = ROOT.parent / "phase14"
sys.path.insert(0, str(PHASE14))
import sltd_state_score_momentum_stage_b_v3 as b  # noqa: E402

OUT_JSON = ROOT / "SLTD_SCORE_LEVEL_RELATIVE_RANKING_V1_STAGE_A_RESULT.json"
OUT_MD = ROOT / "SLTD_SCORE_LEVEL_RELATIVE_RANKING_V1_STAGE_A_RESULT.md"

MIN_XS = 60
MIN_EXTREME_TEMP = 5000


def _finite_series(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce").replace([np.inf, -np.inf], np.nan)


def build_segment(panel: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp, baselines, scales) -> pd.DataFrame:
    seg = b.segment(panel, start, end).copy().reset_index(drop=True)
    raw = b.raw_forward_dims(seg, baselines)
    util = b.utility_from_raw(raw, scales)
    seg["forward_utility"] = util

    required = ["level", "forward_utility", "ret5", "ret10", "ret20", "mae10", "mae20"]
    for c in required:
        seg[c] = _finite_series(seg[c])

    valid = np.ones(len(seg), dtype=bool)
    for c in required:
        valid &= np.isfinite(seg[c].to_numpy(float))
    seg = seg.loc[valid].copy()

    # Require a sufficiently broad same-date cross section before ranking.
    counts = seg.groupby("date")["symbol"].transform("count")
    seg = seg.loc[counts >= MIN_XS].copy()

    # Average rank handles exact LEVEL ties deterministically.
    seg["xs_n"] = seg.groupby("date")["symbol"].transform("count").astype(int)
    avg_rank = seg.groupby("date")["level"].rank(method="average", ascending=True)
    seg["rank"] = (avg_rank - 1.0) / (seg["xs_n"].astype(float) - 1.0)

    # Fixed equal-width rank quintiles. rank==1 belongs to Q5.
    q = np.floor(seg["rank"].to_numpy(float) * 5.0).astype(int) + 1
    q = np.clip(q, 1, 5)
    seg["quintile"] = q

    # Cross-sectional relative labels. These are research outcomes only.
    seg["xs_utility"] = seg["forward_utility"] - seg.groupby("date")["forward_utility"].transform("median")
    for h in (5, 10, 20):
        seg[f"xs_ret{h}"] = seg[f"ret{h}"] - seg.groupby("date")[f"ret{h}"].transform("median")
    for h in (10, 20):
        # MAE is normally <=0; larger / less-negative is safer.
        seg[f"xs_mae_safety{h}"] = seg[f"mae{h}"] - seg.groupby("date")[f"mae{h}"].transform("median")

    return seg.reset_index(drop=True)


def bucket_stats(df: pd.DataFrame) -> dict:
    out = {}
    for q in range(1, 6):
        s = df.loc[df["quintile"] == q]
        out[f"Q{q}"] = {
            "count": int(len(s)),
            "median_xs_utility": float(np.median(s["xs_utility"])) if len(s) else None,
            "median_xs_ret5": float(np.median(s["xs_ret5"])) if len(s) else None,
            "median_xs_ret10": float(np.median(s["xs_ret10"])) if len(s) else None,
            "median_xs_ret20": float(np.median(s["xs_ret20"])) if len(s) else None,
            "median_xs_mae_safety10": float(np.median(s["xs_mae_safety10"])) if len(s) else None,
            "median_xs_mae_safety20": float(np.median(s["xs_mae_safety20"])) if len(s) else None,
        }
    return out


def daily_spread_fraction(df: pd.DataFrame) -> tuple[float | None, int]:
    vals = []
    for _, d in df.groupby("date", sort=True):
        q1 = d.loc[d["quintile"] == 1, "xs_utility"].to_numpy(float)
        q5 = d.loc[d["quintile"] == 5, "xs_utility"].to_numpy(float)
        if len(q1) and len(q5):
            vals.append(float(np.median(q5) - np.median(q1)))
    if not vals:
        return None, 0
    a = np.asarray(vals, dtype=float)
    return float(np.mean(a > 0)), int(len(a))


def summarize(df: pd.DataFrame) -> dict:
    buckets = bucket_stats(df)
    med = [buckets[f"Q{i}"]["median_xs_utility"] for i in range(1, 6)]
    adjacent = 0
    for a, c in zip(med[:-1], med[1:]):
        if a is not None and c is not None and c > a:
            adjacent += 1

    daily_frac, daily_n = daily_spread_fraction(df)
    q1 = buckets["Q1"]
    q5 = buckets["Q5"]

    def spread(key: str):
        a = q1[key]
        c = q5[key]
        if a is None or c is None:
            return None
        return float(c - a)

    return {
        "valid_dates": int(df["date"].nunique()),
        "valid_observations": int(len(df)),
        "mean_daily_cross_section": float(df.groupby("date")["symbol"].count().mean()),
        "rank_corr_rank_vs_xs_utility": b.rank_corr(
            df["rank"].to_numpy(float),
            df["xs_utility"].to_numpy(float),
        ),
        "buckets": buckets,
        "q5_minus_q1": {
            "median_xs_utility": spread("median_xs_utility"),
            "median_xs_ret5": spread("median_xs_ret5"),
            "median_xs_ret10": spread("median_xs_ret10"),
            "median_xs_ret20": spread("median_xs_ret20"),
            "median_xs_mae_safety10": spread("median_xs_mae_safety10"),
            "median_xs_mae_safety20": spread("median_xs_mae_safety20"),
        },
        "adjacent_quintile_utility_increases": int(adjacent),
        "daily_q5_gt_q1_utility_fraction": daily_frac,
        "daily_q5_q1_comparable_dates": daily_n,
    }


def main():
    stable = b.load_stable_utilities()
    if len(stable) != 82:
        raise RuntimeError(f"expected 82 frozen stable states, got {len(stable)}")

    panel = b.build_panel(stable)

    # Discovery segment is used to define symbol baselines and normalization only.
    disc_base = b.segment(panel, b.DISC_START, b.DISC_END).copy().reset_index(drop=True)
    baselines = b.training_baselines(disc_base)
    raw_disc = b.raw_forward_dims(disc_base, baselines)
    scales = b.label_scales(raw_disc)

    disc = build_segment(panel, b.DISC_START, b.DISC_END, baselines, scales)
    temp = build_segment(panel, b.TEMP_START, b.TEMP_END, baselines, scales)

    d = summarize(disc)
    t = summarize(temp)

    gates = {
        "discovery_rank_corr_positive": d["rank_corr_rank_vs_xs_utility"] is not None and d["rank_corr_rank_vs_xs_utility"] > 0,
        "temporal_rank_corr_positive": t["rank_corr_rank_vs_xs_utility"] is not None and t["rank_corr_rank_vs_xs_utility"] > 0,
        "discovery_q5_q1_utility_positive": d["q5_minus_q1"]["median_xs_utility"] is not None and d["q5_minus_q1"]["median_xs_utility"] > 0,
        "temporal_q5_q1_utility_positive": t["q5_minus_q1"]["median_xs_utility"] is not None and t["q5_minus_q1"]["median_xs_utility"] > 0,
        "temporal_q5_q1_ret10_positive": t["q5_minus_q1"]["median_xs_ret10"] is not None and t["q5_minus_q1"]["median_xs_ret10"] > 0,
        "temporal_q5_q1_ret20_positive": t["q5_minus_q1"]["median_xs_ret20"] is not None and t["q5_minus_q1"]["median_xs_ret20"] > 0,
        "temporal_utility_monotonicity_3_of_4": t["adjacent_quintile_utility_increases"] >= 3,
        "temporal_daily_q5_gt_q1_majority": t["daily_q5_gt_q1_utility_fraction"] is not None and t["daily_q5_gt_q1_utility_fraction"] > 0.5,
        "temporal_extreme_support": (
            t["buckets"]["Q1"]["count"] >= MIN_EXTREME_TEMP
            and t["buckets"]["Q5"]["count"] >= MIN_EXTREME_TEMP
        ),
    }

    decision = "PROMOTED_TO_ALLOCATION_TEST" if all(gates.values()) else "REJECTED_NOT_ADMITTED"

    out = {
        "meta": {
            "study": "SLTD_SCORE_LEVEL_RELATIVE_RANKING_V1_STAGE_A",
            "protocol": "SLTD_SCORE_LEVEL_RELATIVE_RANKING_V1_PROTOCOL.md",
            "parent_closeout": "47f81af4e86e667cfbf84471013fd403a05cce69",
            "score_source_commit": "e996e4344e5c40425bc93253d2e00501bacb3eb8",
            "stable_state_count": len(stable),
            "chan_used": False,
            "v7_used_as_signal": False,
            "momentum_used": False,
            "v4_probability_used": False,
            "fresh_oos_consumed": False,
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        },
        "label_scales": scales,
        "discovery": d,
        "temporal": t,
        "gates": gates,
        "decision": decision,
    }

    OUT_JSON.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# SLTD Score Level -> Relative Ranking v1 — Stage A Result",
        "",
        f"Status: **{decision}**",
        "",
        "Chan/缠论: **NOT USED**",
        "V7 as signal: **NOT USED**",
        "Score Momentum: **NOT USED**",
        "v4 probability calibration: **NOT USED**",
        "Fresh OOS consumed: **NO**",
        "",
        "## Core question",
        "",
        "Does frozen SLTD LEVEL order relative future quality across stocks on the same date?",
        "",
    ]

    for name, x in (("Discovery", d), ("Temporal", t)):
        lines += [
            f"## {name}",
            "",
            f"- Valid dates: **{x['valid_dates']}**",
            f"- Valid observations: **{x['valid_observations']}**",
            f"- Mean daily cross-section: **{x['mean_daily_cross_section']:.2f}**",
            f"- Rank corr(RANK, XS_UTILITY): **{x['rank_corr_rank_vs_xs_utility']:.5f}**",
            f"- Q5-Q1 XS_UTILITY: **{x['q5_minus_q1']['median_xs_utility']:.5f}**",
            f"- Q5-Q1 XS_RET_10: **{100*x['q5_minus_q1']['median_xs_ret10']:.3f}%**",
            f"- Q5-Q1 XS_RET_20: **{100*x['q5_minus_q1']['median_xs_ret20']:.3f}%**",
            f"- Adjacent quintile utility increases: **{x['adjacent_quintile_utility_increases']}/4**",
            f"- Daily Q5>Q1 utility fraction: **{100*x['daily_q5_gt_q1_utility_fraction']:.2f}%**",
            "",
            "| Bucket | Count | Median XS utility | XS ret 5d | XS ret 10d | XS ret 20d | XS MAE safety 10d | XS MAE safety 20d |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
        for q in ("Q1","Q2","Q3","Q4","Q5"):
            z=x["buckets"][q]
            lines.append(
                f"| {q} | {z['count']} | {z['median_xs_utility']:.5f} | "
                f"{100*z['median_xs_ret5']:.3f}% | {100*z['median_xs_ret10']:.3f}% | "
                f"{100*z['median_xs_ret20']:.3f}% | {100*z['median_xs_mae_safety10']:.3f}% | "
                f"{100*z['median_xs_mae_safety20']:.3f}% |"
            )
        lines.append("")

    lines += ["## Gates", ""]
    for k,v in gates.items():
        lines.append(f"- {k}: **{'PASS' if v else 'FAIL'}**")
    lines += [
        "",
        f"`SLTD_SCORE_LEVEL_RELATIVE_RANKING_V1_STAGE_A = {decision}`",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps({
        "decision": decision,
        "discovery_corr": d["rank_corr_rank_vs_xs_utility"],
        "temporal_corr": t["rank_corr_rank_vs_xs_utility"],
        "discovery_q5_q1": d["q5_minus_q1"],
        "temporal_q5_q1": t["q5_minus_q1"],
        "temporal_adjacent_increases": t["adjacent_quintile_utility_increases"],
        "temporal_daily_positive_fraction": t["daily_q5_gt_q1_utility_fraction"],
        "gates": gates,
    }, indent=2))


if __name__ == "__main__":
    main()
