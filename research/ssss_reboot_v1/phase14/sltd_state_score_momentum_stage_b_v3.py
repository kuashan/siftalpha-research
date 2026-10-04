#!/usr/bin/env python3
"""SLTD State Score Risk-Exposure v3 — Stage B score-momentum study."""
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
PHASE11 = ROOT.parent / "phase11"
sys.path.insert(0, str(PHASE11))
import pure_sltd_state_probability_v1 as p11  # noqa: E402

STAGE_A_JSON = ROOT / "SLTD_STATE_SCORE_RISK_LAYER_STAGE_A_V3_RESULT.json"
OUT_JSON = ROOT / "SLTD_STATE_SCORE_MOMENTUM_STAGE_B_V3_RESULT.json"
OUT_MD = ROOT / "SLTD_STATE_SCORE_MOMENTUM_STAGE_B_V3_RESULT.md"

DISC_START = pd.Timestamp("2020-01-02")
DISC_END = pd.Timestamp("2023-12-31")
TEMP_START = pd.Timestamp("2024-01-01")
TEMP_END = pd.Timestamp("2026-09-30")
HORIZONS = (5, 10, 20)
DIMS = ("RETURN", "UP_PROB", "MFE", "MAE_SAFETY", "RR")
CANDIDATES = ("M1", "M3", "M5")


def finite(x) -> bool:
    return x is not None and math.isfinite(float(x))


def scale_from_zero(values: np.ndarray) -> tuple[float | None, str]:
    arr = np.asarray(values, dtype=float)
    arr = arr[np.isfinite(arr)]
    if not len(arr):
        return None, "none"
    a = np.abs(arr)
    scale = float(np.median(a))
    method = "MEDIAN_ABS_FROM_ZERO"
    if scale <= 1e-15:
        scale = float(np.quantile(a, 0.75))
        method = "P75_ABS_FROM_ZERO"
    if scale <= 1e-15:
        return None, "degenerate"
    return scale, method


def safe_rr(mfe: float, mae: float) -> float:
    return max(float(mfe), 1e-6) / max(abs(float(mae)), 1e-6)


def rank_corr(a: np.ndarray, b: np.ndarray) -> float | None:
    mask = np.isfinite(a) & np.isfinite(b)
    if int(mask.sum()) < 3:
        return None
    ar = pd.Series(a[mask]).rank(method="average").to_numpy(float)
    br = pd.Series(b[mask]).rank(method="average").to_numpy(float)
    if np.std(ar) <= 1e-15 or np.std(br) <= 1e-15:
        return 0.0
    return float(np.corrcoef(ar, br)[0, 1])


def load_stable_utilities() -> dict[str, float]:
    x = json.loads(STAGE_A_JSON.read_text(encoding="utf-8"))
    if x["summary"]["decision"] != "IMPLEMENTED_AND_VERIFIED":
        raise RuntimeError("Stage A is not IMPLEMENTED_AND_VERIFIED")
    out = {}
    for item in x["stable_states_ranked"]:
        if item["temporal_stable"]:
            out[item["id"]] = float(item["discovery"]["utility"])
    if not out:
        raise RuntimeError("no stable Stage-A state utilities")
    return out


def level_for_row(r, stable: dict[str, float]) -> tuple[float, dict]:
    keys = p11.keys_for_row(r)
    by_family: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for fam, key in keys:
        ident = f"{fam}::{key}"
        if ident in stable:
            by_family[fam].append((key, ident))

    comps: dict[str, float] = {}

    # REGIME: F2 overrides F1.
    if by_family.get("F2_COLOR_AGE_ORIGIN"):
        ident = by_family["F2_COLOR_AGE_ORIGIN"][0][1]
        comps["REGIME"] = stable[ident]
    elif by_family.get("F1_COLOR_AGE"):
        ident = by_family["F1_COLOR_AGE"][0][1]
        comps["REGIME"] = stable[ident]

    if by_family.get("F3_COLOR_AGE_INNER"):
        ident = by_family["F3_COLOR_AGE_INNER"][0][1]
        comps["INNER"] = stable[ident]

    slow_vals = []
    for fam in ("F4_COLOR_AGE_SLOWPOS", "F5_COLOR_AGE_SLOWTREND"):
        for _, ident in by_family.get(fam, []):
            slow_vals.append(stable[ident])
    if slow_vals:
        comps["SLOW"] = float(np.median(slow_vals))

    # EVENT: pair broad F6 with subtype F7 by broad-key prefix.
    event_vals = []
    f6 = by_family.get("F6_COLOR_AGE_EVENT", [])
    f7 = by_family.get("F7_COLOR_AGE_EVENT_SUBTYPE", [])
    used_f7 = set()
    for broad_key, broad_ident in f6:
        specific = [(k, i) for k, i in f7 if k.startswith(broad_key + "|")]
        if specific:
            # one subtype per concrete event on a bar; median keeps deterministic if duplicated.
            vals = [stable[i] for _, i in specific]
            event_vals.append(float(np.median(vals)))
            used_f7.update(i for _, i in specific)
        else:
            event_vals.append(stable[broad_ident])
    # Stable F7 can exist while its F6 is not stable.
    for _, ident in f7:
        if ident not in used_f7:
            event_vals.append(stable[ident])
    if event_vals:
        comps["EVENT"] = float(np.median(event_vals))

    trans_vals = [stable[i] for _, i in by_family.get("F8_TRANSITION_EVENT", [])]
    if trans_vals:
        comps["TRANSITION"] = float(np.median(trans_vals))

    nz = [float(v) for v in comps.values() if abs(float(v)) > 1e-15]
    level = float(np.median(nz)) if nz else 0.0
    return level, comps


def build_panel(stable: dict[str, float]) -> pd.DataFrame:
    chunks = []
    for batch, symbols in p11.core.BATCHES.items():
        for symbol in symbols:
            frame, ledger = p11.load_79_symbol(batch, symbol)
            df = p11.build_symbol_rows(symbol, frame, ledger).copy()
            levels = []
            comp_counts = []
            for r in df.itertuples(index=False):
                lvl, comps = level_for_row(r, stable)
                levels.append(lvl)
                comp_counts.append(len(comps))
            df["level"] = np.asarray(levels, dtype=float)
            df["component_count"] = np.asarray(comp_counts, dtype=int)
            df["m1"] = df["level"] - df["level"].shift(1)
            df["m3"] = df["level"] - df["level"].shift(1).rolling(3, min_periods=3).median()
            df["m5"] = df["level"] - df["level"].shift(1).rolling(5, min_periods=5).median()
            df["outcome_end_date"] = df["date"].shift(-20)
            keep = ["symbol", "date", "outcome_end_date", "level", "component_count", "m1", "m3", "m5"]
            for h in HORIZONS:
                keep += [f"ret{h}", f"mfe{h}", f"mae{h}"]
            chunks.append(df[keep])
    panel = pd.concat(chunks, ignore_index=True)
    panel["date"] = pd.to_datetime(panel["date"]).dt.tz_localize(None)
    panel["outcome_end_date"] = pd.to_datetime(panel["outcome_end_date"]).dt.tz_localize(None)
    return panel


def segment(panel: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    m = (
        (panel["date"] >= start)
        & (panel["date"] <= end)
        & panel["outcome_end_date"].notna()
        & (panel["outcome_end_date"] <= end)
    )
    return panel.loc[m].copy().reset_index(drop=True)


def training_baselines(train: pd.DataFrame) -> dict[str, dict[int, dict]]:
    out: dict[str, dict[int, dict]] = {}
    for symbol, sdf in train.groupby("symbol", sort=False):
        out[symbol] = {}
        for h in HORIZONS:
            ret = pd.to_numeric(sdf[f"ret{h}"], errors="coerce").to_numpy(float)
            mfe = pd.to_numeric(sdf[f"mfe{h}"], errors="coerce").to_numpy(float)
            mae = pd.to_numeric(sdf[f"mae{h}"], errors="coerce").to_numpy(float)
            ok = np.isfinite(ret) & np.isfinite(mfe) & np.isfinite(mae)
            if not ok.any():
                continue
            ret = ret[ok]; mfe = mfe[ok]; mae = mae[ok]
            med_mfe = float(np.median(mfe))
            med_mae = float(np.median(mae))
            out[symbol][h] = {
                "ret": float(np.median(ret)),
                "up": float(np.mean(ret > 0)),
                "mfe": med_mfe,
                "mae": med_mae,
                "rr": safe_rr(med_mfe, med_mae),
            }
    return out


def raw_forward_dims(df: pd.DataFrame, baselines: dict[str, dict[int, dict]]) -> np.ndarray:
    rows = np.full((len(df), len(DIMS)), np.nan, dtype=float)
    for j, r in enumerate(df.itertuples(index=False)):
        b_sym = baselines.get(str(r.symbol), {})
        vals = {d: [] for d in DIMS}
        for h in HORIZONS:
            b = b_sym.get(h)
            ret = getattr(r, f"ret{h}")
            mfe = getattr(r, f"mfe{h}")
            mae = getattr(r, f"mae{h}")
            if b is None or not (finite(ret) and finite(mfe) and finite(mae)):
                continue
            ret=float(ret); mfe=float(mfe); mae=float(mae)
            vals["RETURN"].append(ret - b["ret"])
            vals["UP_PROB"].append((1.0 if ret > 0 else 0.0) - b["up"])
            vals["MFE"].append(mfe - b["mfe"])
            vals["MAE_SAFETY"].append(mae - b["mae"])
            vals["RR"].append(math.log(safe_rr(mfe, mae)) - math.log(b["rr"]))
        for k, d in enumerate(DIMS):
            if vals[d]:
                rows[j, k] = float(np.median(vals[d]))
    return rows


def label_scales(raw_train: np.ndarray) -> dict[str, dict]:
    out = {}
    for k, d in enumerate(DIMS):
        scale, method = scale_from_zero(raw_train[:, k])
        out[d] = {"scale": scale, "method": method, "active": scale is not None}
    return out


def utility_from_raw(raw: np.ndarray, scales: dict[str, dict]) -> np.ndarray:
    cols = []
    for k, d in enumerate(DIMS):
        s = scales[d]["scale"]
        if s is not None:
            cols.append(raw[:, k] / float(s))
    if not cols:
        return np.full(len(raw), np.nan)
    mat = np.column_stack(cols)
    return np.nanmedian(mat, axis=1)


def predictor_scales(train: pd.DataFrame, mom_col: str) -> dict:
    ls, lm = scale_from_zero(train["level"].to_numpy(float))
    ms, mm = scale_from_zero(train[mom_col].to_numpy(float))
    if ls is None or ms is None:
        raise RuntimeError(f"degenerate predictor scale for {mom_col}")
    return {
        "level": {"scale": ls, "method": lm},
        "momentum": {"scale": ms, "method": mm},
    }


def design(df: pd.DataFrame, mom_col: str, scales: dict, full: bool) -> np.ndarray:
    level = df["level"].to_numpy(float) / float(scales["level"]["scale"])
    if not full:
        return np.column_stack([np.ones(len(df)), level])
    mom = df[mom_col].to_numpy(float) / float(scales["momentum"]["scale"])
    up = np.maximum(mom, 0.0)
    down = np.minimum(mom, 0.0)
    return np.column_stack([np.ones(len(df)), level, up, down])


def fit_eval(train: pd.DataFrame, valid: pd.DataFrame, mom_col: str) -> dict:
    baselines = training_baselines(train)
    raw_tr = raw_forward_dims(train, baselines)
    raw_va = raw_forward_dims(valid, baselines)
    lscales = label_scales(raw_tr)
    ytr = utility_from_raw(raw_tr, lscales)
    yva = utility_from_raw(raw_va, lscales)
    pscales = predictor_scales(train, mom_col)

    Xb_tr = design(train, mom_col, pscales, False)
    Xf_tr = design(train, mom_col, pscales, True)
    Xb_va = design(valid, mom_col, pscales, False)
    Xf_va = design(valid, mom_col, pscales, True)

    oktr = np.isfinite(ytr) & np.all(np.isfinite(Xf_tr), axis=1)
    okva = np.isfinite(yva) & np.all(np.isfinite(Xf_va), axis=1)
    if int(oktr.sum()) < 1000 or int(okva.sum()) < 500:
        raise RuntimeError(f"insufficient train/valid rows for {mom_col}: {oktr.sum()}/{okva.sum()}")

    bb = np.linalg.lstsq(Xb_tr[oktr], ytr[oktr], rcond=None)[0]
    bf = np.linalg.lstsq(Xf_tr[oktr], ytr[oktr], rcond=None)[0]
    pb = Xb_va[okva] @ bb
    pf = Xf_va[okva] @ bf
    yy = yva[okva]

    mae_b = float(np.mean(np.abs(yy - pb)))
    mae_f = float(np.mean(np.abs(yy - pf)))
    corr_b = rank_corr(pb, yy)
    corr_f = rank_corr(pf, yy)

    q25, q75 = np.quantile(pf, [0.25, 0.75])
    bot = yy[pf <= q25]
    top = yy[pf >= q75]

    return {
        "train_n": int(oktr.sum()),
        "valid_n": int(okva.sum()),
        "baseline_mae": mae_b,
        "full_mae": mae_f,
        "mae_improvement": float((mae_b - mae_f) / mae_b) if mae_b > 0 else None,
        "baseline_rank_corr": corr_b,
        "full_rank_corr": corr_f,
        "rank_corr_improvement": None if corr_b is None or corr_f is None else float(corr_f - corr_b),
        "coefficients": {
            "intercept": float(bf[0]),
            "level": float(bf[1]),
            "mom_up": float(bf[2]),
            "mom_down": float(bf[3]),
        },
        "baseline_coefficients": {"intercept": float(bb[0]), "level": float(bb[1])},
        "predictor_scales": pscales,
        "label_scales": lscales,
        "prediction_quartiles": {
            "q25": float(q25),
            "q75": float(q75),
            "bottom_median_forward_utility": float(np.median(bot)) if len(bot) else None,
            "top_median_forward_utility": float(np.median(top)) if len(top) else None,
        },
    }


def main():
    stable = load_stable_utilities()
    panel = build_panel(stable)

    folds = [
        ("F1_2020_TO_2021", pd.Timestamp("2020-01-02"), pd.Timestamp("2020-12-31"), pd.Timestamp("2021-01-01"), pd.Timestamp("2021-12-31")),
        ("F2_2020_21_TO_2022", pd.Timestamp("2020-01-02"), pd.Timestamp("2021-12-31"), pd.Timestamp("2022-01-01"), pd.Timestamp("2022-12-31")),
        ("F3_2020_22_TO_2023", pd.Timestamp("2020-01-02"), pd.Timestamp("2022-12-31"), pd.Timestamp("2023-01-01"), pd.Timestamp("2023-12-31")),
    ]

    discovery_cv = {}
    for cand in CANDIDATES:
        col = cand.lower()
        cres = []
        for name, ts, te, vs, ve in folds:
            tr = segment(panel, ts, te).dropna(subset=[col]).reset_index(drop=True)
            va = segment(panel, vs, ve).dropna(subset=[col]).reset_index(drop=True)
            r = fit_eval(tr, va, col)
            r["fold"] = name
            cres.append(r)
        imps = [x["mae_improvement"] for x in cres]
        cimps = [x["rank_corr_improvement"] for x in cres if x["rank_corr_improvement"] is not None]
        discovery_cv[cand] = {
            "folds": cres,
            "median_mae_improvement": float(np.median(imps)),
            "positive_mae_folds": int(sum(x > 0 for x in imps)),
            "median_rank_corr_improvement": float(np.median(cimps)) if cimps else None,
            "selection_requirements_pass": bool(np.median(imps) > 0 and sum(x > 0 for x in imps) >= 2),
        }

    order = {"M1": 0, "M3": 1, "M5": 2}
    eligible = [c for c in CANDIDATES if discovery_cv[c]["selection_requirements_pass"]]
    if eligible:
        winner = sorted(
            eligible,
            key=lambda c: (
                -discovery_cv[c]["median_mae_improvement"],
                -(discovery_cv[c]["median_rank_corr_improvement"] if discovery_cv[c]["median_rank_corr_improvement"] is not None else -999),
                -discovery_cv[c]["positive_mae_folds"],
                order[c],
            ),
        )[0]
    else:
        winner = sorted(
            CANDIDATES,
            key=lambda c: (
                -discovery_cv[c]["median_mae_improvement"],
                -(discovery_cv[c]["median_rank_corr_improvement"] if discovery_cv[c]["median_rank_corr_improvement"] is not None else -999),
                -discovery_cv[c]["positive_mae_folds"],
                order[c],
            ),
        )[0]

    disc = segment(panel, DISC_START, DISC_END).dropna(subset=[winner.lower()]).reset_index(drop=True)
    temp = segment(panel, TEMP_START, TEMP_END).dropna(subset=[winner.lower()]).reset_index(drop=True)
    temporal = fit_eval(disc, temp, winner.lower())

    q = temporal["prediction_quartiles"]
    gates = {
        "discovery_selection_pass": discovery_cv[winner]["selection_requirements_pass"],
        "temporal_mae_improves": temporal["full_mae"] < temporal["baseline_mae"],
        "temporal_rank_corr_improves": (
            temporal["full_rank_corr"] is not None
            and temporal["baseline_rank_corr"] is not None
            and temporal["full_rank_corr"] > temporal["baseline_rank_corr"]
        ),
        "temporal_top_gt_bottom": (
            q["top_median_forward_utility"] is not None
            and q["bottom_median_forward_utility"] is not None
            and q["top_median_forward_utility"] > q["bottom_median_forward_utility"]
        ),
    }
    decision = "PROMOTED_TO_STAGE_C" if all(gates.values()) else "REJECTED_NOT_ADMITTED"

    level_nonzero = float(np.mean(np.abs(panel["level"].to_numpy(float)) > 1e-15))
    out = {
        "meta": {
            "study": "SLTD_STATE_SCORE_RISK_EXPOSURE_V3_STAGE_B",
            "status": decision,
            "stage_a_commit": "e996e4344e5c40425bc93253d2e00501bacb3eb8",
            "protocol": "SLTD_STATE_SCORE_RISK_EXPOSURE_V3_STAGE_B_PROTOCOL.md",
            "chan_used": False,
            "v7_used_as_signal": False,
            "fresh_oos_consumed": False,
            "selection_dataset": "Discovery 79 stocks 2020-2023 only",
            "temporal_role": "consistency check; not independent Fresh OOS",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        },
        "stable_state_count": len(stable),
        "panel_rows": len(panel),
        "level_nonzero_fraction": level_nonzero,
        "discovery_cv": discovery_cv,
        "winner": winner,
        "temporal_consistency": temporal,
        "gates": gates,
        "decision": decision,
    }
    OUT_JSON.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# SLTD State Score Risk-Exposure v3 — Stage B Momentum Result",
        "",
        f"Status: **{decision}**",
        "",
        f"Discovery-selected momentum: **{winner}**",
        f"Stable Stage-A state count: **{len(stable)}**",
        f"Bars with non-zero LEVEL: **{100*level_nonzero:.2f}%**",
        "",
        "## Discovery blocked walk-forward",
        "",
        "| Candidate | Median MAE improvement | Positive folds | Median rank-corr improvement | Selection pass |",
        "|---|---:|---:|---:|---|",
    ]
    for c in CANDIDATES:
        r = discovery_cv[c]
        lines.append(
            f"| {c} | {100*r['median_mae_improvement']:.3f}% | {r['positive_mae_folds']}/3 | "
            f"{r['median_rank_corr_improvement']:.5f} | {'PASS' if r['selection_requirements_pass'] else 'FAIL'} |"
        )

    lines += [
        "",
        "## Temporal consistency (2024-2026Q3)",
        "",
        f"- Baseline LEVEL-only MAE: **{temporal['baseline_mae']:.6f}**",
        f"- LEVEL + asymmetric momentum MAE: **{temporal['full_mae']:.6f}**",
        f"- MAE improvement: **{100*temporal['mae_improvement']:.3f}%**",
        f"- Baseline rank correlation: **{temporal['baseline_rank_corr']:.5f}**",
        f"- Full rank correlation: **{temporal['full_rank_corr']:.5f}**",
        f"- MOM_UP coefficient: **{temporal['coefficients']['mom_up']:.6f}**",
        f"- MOM_DOWN coefficient: **{temporal['coefficients']['mom_down']:.6f}**",
        f"- Bottom prediction quartile median forward utility: **{q['bottom_median_forward_utility']:.5f}**",
        f"- Top prediction quartile median forward utility: **{q['top_median_forward_utility']:.5f}**",
        "",
        "## Gates",
        "",
    ]
    for k, v in gates.items():
        lines.append(f"- {k}: **{'PASS' if v else 'FAIL'}**")
    lines += [
        "",
        "Temporal is a consistency check because Stage A already used it for state stability.",
        "No Fresh OOS was consumed.",
        "",
        f"`SLTD_STATE_SCORE_RISK_EXPOSURE_V3_STAGE_B = {decision}`",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps({
        "winner": winner,
        "discovery": {c: {
            "median_mae_improvement": discovery_cv[c]["median_mae_improvement"],
            "positive_mae_folds": discovery_cv[c]["positive_mae_folds"],
            "median_rank_corr_improvement": discovery_cv[c]["median_rank_corr_improvement"],
        } for c in CANDIDATES},
        "temporal": {
            "mae_improvement": temporal["mae_improvement"],
            "baseline_rank_corr": temporal["baseline_rank_corr"],
            "full_rank_corr": temporal["full_rank_corr"],
            "coefficients": temporal["coefficients"],
            "quartiles": temporal["prediction_quartiles"],
        },
        "gates": gates,
        "decision": decision,
    }, indent=2))


if __name__ == "__main__":
    main()
