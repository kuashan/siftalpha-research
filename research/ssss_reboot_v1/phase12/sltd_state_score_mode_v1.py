#!/usr/bin/env python3
"""Independent SLTD State Score Mode v1.

This mode does NOT use V7 rules or C2 internally.
It learns a categorical state-effect map from prior development data,
maps a close-time SLTD score to target exposure, and rebalances next open.
"""
from __future__ import annotations

import json
import math
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

ROOT = Path(__file__).resolve().parent
PHASE7 = ROOT.parent / "phase7"
PHASE8 = ROOT.parent / "phase8"
sys.path.insert(0, str(ROOT))
import pure_sltd_state_probability_v1 as st
import pure_sltd_v8_probability_map_r2_v1 as r2
import pure_sltd_v8_probability_map_r3_v1 as r3

PROJECT = ROOT.parents[2] / "integrations" / "sltd_v7_siftalpha_v1"
sys.path.insert(0, str(PROJECT))
import strategy as sltd

sys.path.insert(0, str(PHASE7))
import sltd_v6_position_policy_batch_v1 as core

FORMAL_START = pd.Timestamp("2020-01-02")
FORMAL_END = pd.Timestamp("2026-09-30")
DISCOVERY_END = pd.Timestamp("2023-12-31")
TEMPORAL_START = pd.Timestamp("2024-01-01")
FETCH_START = "2010-01-04"
FETCH_END_EXCLUSIVE = "2026-10-01"

FAMILIES = {
    "F1_COLOR_AGE",
    "F2_COLOR_AGE_ORIGIN",
    "F3_COLOR_AGE_INNER",
    "F4_COLOR_AGE_SLOWPOS",
    "F5_COLOR_AGE_SLOWTREND",
    "F6_COLOR_AGE_EVENT",
    "F7_COLOR_AGE_EVENT_SUBTYPE",
}
DENSE = {
    "F1_COLOR_AGE",
    "F2_COLOR_AGE_ORIGIN",
    "F3_COLOR_AGE_INNER",
    "F4_COLOR_AGE_SLOWPOS",
    "F5_COLOR_AGE_SLOWTREND",
}

UNIVERSE = [
    ("COF", "Financial"), ("MMC", "Financial"), ("AJG", "Financial"),
    ("KLAC", "Technology"), ("SNPS", "Technology"), ("CDNS", "Technology"),
    ("EA", "Communication"), ("TTWO", "Communication"), ("FOXA", "Communication"),
    ("EW", "Healthcare"), ("BSX", "Healthcare"), ("REGN", "Healthcare"),
    ("FAST", "Industrials"), ("URI", "Industrials"), ("PCAR", "Industrials"),
    ("NUE", "Materials"), ("MLM", "Materials"), ("ECL", "Materials"),
    ("DG", "ConsumerDiscretionary"), ("LULU", "ConsumerDiscretionary"), ("AZO", "ConsumerDiscretionary"),
    ("KMB", "ConsumerStaples"), ("SYY", "ConsumerStaples"), ("HSY", "ConsumerStaples"),
    ("AEP", "Utilities"), ("XEL", "Utilities"), ("WEC", "Utilities"),
    ("MPC", "Energy"), ("OXY", "Energy"), ("VLO", "Energy"),
]
SYMBOLS = [s for s, _ in UNIVERSE]

DATA_DIR = ROOT / "state_score_fresh30_data"
OUT_JSON = ROOT / "SLTD_STATE_SCORE_MODE_V1_RESULT.json"
OUT_MD = ROOT / "SLTD_STATE_SCORE_MODE_V1_RESULT.md"
MODEL_JSON = ROOT / "SLTD_STATE_SCORE_MODE_V1_MODEL.json"


def sign(x: float | None) -> int:
    if x is None or not math.isfinite(float(x)) or abs(float(x)) < 1e-15:
        return 0
    return 1 if float(x) > 0 else -1


def load_dev_panels() -> tuple[dict[str, pd.DataFrame], dict[str, pd.DataFrame]]:
    all79: dict[str, pd.DataFrame] = {}
    for batch, symbols in core.BATCHES.items():
        for symbol in symbols:
            frame, ledger = st.load_79_symbol(batch, symbol)
            all79[symbol] = st.build_symbol_rows(symbol, frame, ledger)
    if len(all79) != 79:
        raise RuntimeError(f"expected 79 development stocks, got {len(all79)}")

    oos10: dict[str, pd.DataFrame] = {}
    for symbol in st.OOS10:
        frame, ledger = st.load_oos_symbol(symbol)
        oos10[symbol] = st.build_symbol_rows(symbol, frame, ledger)
    return all79, oos10


def support_ok(rec: dict) -> bool:
    fam = rec["family"]
    if fam in DENSE:
        return rec["n"] >= 300 and rec["symbol_count"] >= 25
    return rec["n"] >= 50 and rec["symbol_count"] >= 10


def build_model() -> tuple[dict[str, float], list[float], dict]:
    all79, oos10 = load_dev_panels()
    disc = st.subset_rows(all79, FORMAL_START, DISCOVERY_END)
    temp = st.subset_rows(all79, TEMPORAL_START, FORMAL_END)
    ext = st.subset_rows(oos10, FORMAL_START, FORMAL_END)

    dm = st.aggregate_split(disc, "DISCOVERY")
    tm = st.aggregate_split(temp, "TEMPORAL")
    om = st.aggregate_split(ext, "OOS10")

    state_map: dict[str, float] = {}
    audit = []

    for ident, drec in dm.items():
        fam = drec["family"]
        if fam not in FAMILIES or not support_ok(drec):
            continue
        d10 = drec["horizons"]["10"]["symbol_median_excess"]
        d20 = drec["horizons"]["20"]["symbol_median_excess"]
        s = sign(d10)
        if s == 0 or sign(d20) != s:
            continue
        trec = tm.get(ident)
        orec = om.get(ident)
        if trec is None or orec is None:
            continue
        vals = [
            d10, d20,
            trec["horizons"]["10"]["symbol_median_excess"],
            trec["horizons"]["20"]["symbol_median_excess"],
            orec["horizons"]["10"]["symbol_median_excess"],
            orec["horizons"]["20"]["symbol_median_excess"],
        ]
        if any(sign(v) != s for v in vals):
            continue
        if orec["symbol_count"] < 5:
            continue
        effect = float(np.median(np.asarray(vals, dtype=float)))
        state_map[ident] = effect
        audit.append({
            "id": ident,
            "family": fam,
            "key": drec["key"],
            "effect": effect,
            "direction": "POSITIVE" if s > 0 else "NEGATIVE",
            "discovery_n": drec["n"],
            "discovery_symbols": drec["symbol_count"],
            "oos10_symbols": orec["symbol_count"],
            "components": vals,
        })

    if not state_map:
        raise RuntimeError("no admitted state effects")

    scores = []
    for symbol, df in disc.items():
        for row in df.itertuples(index=False):
            scores.append(score_row(row, state_map))
    arr = np.asarray(scores, dtype=float)
    qs = [float(np.quantile(arr, q)) for q in (0.20, 0.40, 0.60, 0.80)]

    model = {
        "study": "SLTD_STATE_SCORE_MODE_V1",
        "status": "FROZEN_MODEL",
        "families": sorted(FAMILIES),
        "admitted_state_count": len(state_map),
        "state_effects": dict(sorted(state_map.items())),
        "state_audit": sorted(audit, key=lambda x: abs(x["effect"]), reverse=True),
        "score_quantiles": {"q20": qs[0], "q40": qs[1], "q60": qs[2], "q80": qs[3]},
        "mapping": [
            {"max_score": qs[0], "target_exposure": 0.00},
            {"max_score": qs[1], "target_exposure": 0.25},
            {"max_score": qs[2], "target_exposure": 0.50},
            {"max_score": qs[3], "target_exposure": 0.75},
            {"max_score": None, "target_exposure": 1.00},
        ],
        "development_score_stats": {
            "count": int(len(arr)),
            "min": float(np.min(arr)),
            "median": float(np.median(arr)),
            "max": float(np.max(arr)),
            "zero_fraction": float(np.mean(arr == 0.0)),
        },
    }
    return state_map, qs, model


def score_row(row, state_map: dict[str, float]) -> float:
    vals = []
    for fam, key in st.keys_for_row(row):
        if fam not in FAMILIES:
            continue
        ident = f"{fam}::{key}"
        if ident in state_map:
            vals.append(state_map[ident])
    if not vals:
        return 0.0
    return float(np.median(np.asarray(vals, dtype=float)))


def target_from_score(score: float, qs: list[float]) -> float:
    q20, q40, q60, q80 = qs
    if score <= q20:
        return 0.00
    if score <= q40:
        return 0.25
    if score <= q60:
        return 0.50
    if score <= q80:
        return 0.75
    return 1.00


def fetch_stock(ticker: str) -> pd.DataFrame:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / f"{ticker}.csv.gz"
    if path.exists():
        return pd.read_csv(path, parse_dates=["Date"])
    last = None
    for attempt in range(4):
        try:
            f = yf.download(
                ticker,
                start=FETCH_START,
                end=FETCH_END_EXCLUSIVE,
                interval="1d",
                auto_adjust=False,
                actions=False,
                repair=False,
                progress=False,
                threads=False,
                multi_level_index=True,
            )
            if f is not None and not f.empty:
                out = r2.flatten_yf(f, ticker)
                out.to_csv(path, index=False, compression="gzip")
                return out
            last = RuntimeError("empty")
        except Exception as exc:
            last = exc
        time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"{ticker}: download failed: {last}")


def build_fresh_state(frame: pd.DataFrame, ticker: str) -> tuple[list[dict], list[dict], pd.DataFrame]:
    bars = r2.candles_from_frame(frame)
    ledger = sltd.build_ledger(bars, ticker)
    state_df = st.build_symbol_rows(ticker, frame, pd.DataFrame(ledger))
    return bars, ledger, state_df


def state_scores_aligned(bars: list[dict], state_df: pd.DataFrame, state_map: dict[str, float]) -> dict[str, float]:
    return {
        pd.Timestamp(row.date).strftime("%Y-%m-%d"): score_row(row, state_map)
        for row in state_df.itertuples(index=False)
    }


def max_drawdown(curve: np.ndarray) -> float:
    peak = np.maximum.accumulate(curve)
    return float(np.min(curve / peak - 1.0))


def simulate_score_mode(
    bars: list[dict],
    score_by_date: dict[str, float],
    qs: list[float],
    friction_bps: float,
) -> dict:
    formal = [i for i, b in enumerate(bars) if FORMAL_START.strftime("%Y-%m-%d") <= b["date"] <= FORMAL_END.strftime("%Y-%m-%d")]
    if len(formal) < 2:
        raise RuntimeError("insufficient formal bars")
    start, end = formal[0], formal[-1]
    cash = 1.0
    shares = 0.0
    cost_rate = friction_bps / 10000.0
    curve = []
    dates = []
    targets = []
    scores_used = []
    turnover = 0.0
    changes = 0
    invested = 0

    for j in range(start, end + 1):
        bar = bars[j]
        op = float(bar["open"])
        cl = float(bar["close"])
        pre = cash + shares * op
        pos = shares * op

        if j > 0:
            prev_date = bars[j - 1]["date"]
            score = float(score_by_date.get(prev_date, 0.0))
            target = target_from_score(score, qs)
        else:
            score = 0.0
            target = target_from_score(score, qs)

        desired = target * pre
        order = desired - pos
        if order > 1e-14:
            order = min(order, max(0.0, cash / (1.0 + cost_rate)))
        elif order < -1e-14:
            order = max(order, -pos)

        if abs(order) > 1e-14:
            cost = abs(order) * cost_rate
            shares += order / op
            cash -= order + cost
            if shares <= 1e-12:
                shares = 0.0
            turnover += abs(order) / pre
            changes += 1

        eq = cash + shares * cl
        curve.append(eq)
        dates.append(bar["date"])
        targets.append(target)
        scores_used.append(score)
        if shares > 1e-12:
            invested += 1

    arr = np.asarray(curve, dtype=float)
    days = max(1, (pd.Timestamp(dates[-1]) - pd.Timestamp(dates[0])).days)
    total = float(arr[-1] - 1.0)
    cagr = float(arr[-1] ** (365.25 / days) - 1.0) if arr[-1] > 0 else -1.0
    mdd = max_drawdown(arr)
    calmar = cagr / abs(mdd) if mdd < -1e-12 else (999.0 if cagr > 0 else 0.0)
    return {
        "dates": dates,
        "curve": arr,
        "total_return": total,
        "cagr": cagr,
        "max_drawdown": mdd,
        "calmar": float(calmar),
        "turnover": float(turnover),
        "position_changes": int(changes),
        "time_in_market": float(invested / len(arr)),
        "mean_target_exposure": float(np.mean(targets)),
        "target_counts": {
            str(x): int(sum(abs(t - x) < 1e-12 for t in targets))
            for x in (0.0, 0.25, 0.50, 0.75, 1.0)
        },
    }


def compact(x: dict) -> dict:
    return {k: v for k, v in x.items() if k not in {"dates", "curve"}}


def bucket_forward_stats(
    bars: list[dict],
    score_by_date: dict[str, float],
    qs: list[float],
) -> dict[float, dict[str, list[float]]]:
    out = {x: {"10": [], "20": []} for x in (0.0, 0.25, 0.50, 0.75, 1.0)}
    for t in range(len(bars)):
        d = bars[t]["date"]
        if d < FORMAL_START.strftime("%Y-%m-%d") or d > FORMAL_END.strftime("%Y-%m-%d"):
            continue
        if t + 20 >= len(bars):
            continue
        score = float(score_by_date.get(d, 0.0))
        bucket = target_from_score(score, qs)
        entry = float(bars[t + 1]["open"])
        if entry <= 0:
            continue
        out[bucket]["10"].append(float(bars[t + 10]["close"]) / entry - 1.0)
        out[bucket]["20"].append(float(bars[t + 20]["close"]) / entry - 1.0)
    return out


def merge_bucket_stats(all_stats: list[dict]) -> tuple[dict, bool, list]:
    merged = {x: {"10": [], "20": []} for x in (0.0, 0.25, 0.50, 0.75, 1.0)}
    for stats in all_stats:
        for x in merged:
            merged[x]["10"].extend(stats[x]["10"])
            merged[x]["20"].extend(stats[x]["20"])

    summary = {}
    med20 = []
    for x in (0.0, 0.25, 0.50, 0.75, 1.0):
        a10 = np.asarray(merged[x]["10"], dtype=float)
        a20 = np.asarray(merged[x]["20"], dtype=float)
        summary[str(x)] = {
            "n": int(len(a20)),
            "ret10_median": float(np.median(a10)) if len(a10) else None,
            "ret20_median": float(np.median(a20)) if len(a20) else None,
            "ret10_win_rate": float(np.mean(a10 > 0)) if len(a10) else None,
            "ret20_win_rate": float(np.mean(a20 > 0)) if len(a20) else None,
        }
        med20.append(summary[str(x)]["ret20_median"])

    if any(v is None for v in med20):
        return summary, False, [{"reason": "empty_bucket"}]

    inversions = []
    for i in range(4):
        if med20[i + 1] < med20[i]:
            inversions.append({
                "from": [0.0, 0.25, 0.50, 0.75, 1.0][i],
                "to": [0.0, 0.25, 0.50, 0.75, 1.0][i + 1],
                "drop": float(med20[i] - med20[i + 1]),
            })
    passed = len(inversions) == 0 or (len(inversions) == 1 and inversions[0]["drop"] < 0.0025)
    return summary, passed, inversions


def pct(x: float | None) -> str:
    return "—" if x is None else f"{100.0 * x:.2f}%"


def main() -> None:
    prior79 = {s for xs in core.BATCHES.values() for s in xs}
    prior = set(prior79) | set(st.OOS10) | set(r2.SYMBOLS) | set(r3.SYMBOLS)
    overlap = sorted(set(SYMBOLS) & prior)
    if overlap:
        raise RuntimeError(f"Fresh30 overlap with prior research: {overlap}")
    if len(SYMBOLS) != 30 or len(set(SYMBOLS)) != 30:
        raise RuntimeError("Fresh30 must contain 30 unique stocks")

    state_map, qs, model = build_model()
    MODEL_JSON.write_text(json.dumps(model, indent=2, ensure_ascii=False), encoding="utf-8")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    manifest = {
        "study": "SLTD_STATE_SCORE_MODE_V1",
        "provider": "Yahoo Finance via yfinance",
        "auto_adjust": False,
        "formal_window": ["2020-01-02", "2026-09-30"],
        "fresh30": UNIVERSE,
        "prior_overlap": overlap,
        "files": {},
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }

    bars_by = {}
    ledger_by = {}
    scores_by = {}
    bucket_inputs = []

    for ticker, industry in UNIVERSE:
        frame = fetch_stock(ticker)
        if pd.Timestamp(frame["Date"].min()) >= FORMAL_START:
            raise RuntimeError(f"{ticker}: missing pre-2020 warmup")
        if pd.Timestamp(frame["Date"].max()) < FORMAL_END:
            raise RuntimeError(f"{ticker}: data ends early")
        bars, ledger, state_df = build_fresh_state(frame, ticker)
        score_by = state_scores_aligned(bars, state_df, state_map)
        bars_by[ticker] = bars
        ledger_by[ticker] = ledger
        scores_by[ticker] = score_by
        bucket_inputs.append(bucket_forward_stats(bars, score_by, qs))
        p = DATA_DIR / f"{ticker}.csv.gz"
        manifest["files"][ticker] = {
            "industry": industry,
            "rows": len(frame),
            "first": pd.Timestamp(frame["Date"].min()).strftime("%Y-%m-%d"),
            "last": pd.Timestamp(frame["Date"].max()).strftime("%Y-%m-%d"),
            "sha256": r2.sha256_file(p),
        }

    (DATA_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    systems = {}
    per_symbol = {}
    for flabel, bps in (("5bps", 5.0), ("10bps", 10.0), ("20bps", 20.0)):
        systems[flabel] = {"STATE_SCORE": {}, "V7": {}, "BUY_HOLD": {}, "SMA200_TREND": {}}
        for s in SYMBOLS:
            bars = bars_by[s]
            ledger = ledger_by[s]
            systems[flabel]["STATE_SCORE"][s] = simulate_score_mode(bars, scores_by[s], qs, bps)
            systems[flabel]["V7"][s] = r2.simulate_sltd(bars, ledger, bps, False)
            systems[flabel]["BUY_HOLD"][s] = r2.simulate_buy_hold(bars, bps)
            systems[flabel]["SMA200_TREND"][s] = r2.simulate_sma200(bars, bps)

    portfolio = {
        flabel: {label: r2.portfolio_metrics(vals) for label, vals in systems[flabel].items()}
        for flabel in systems
    }
    per_symbol = {
        s: {
            flabel: {label: compact(systems[flabel][label][s]) for label in systems[flabel]}
            for flabel in systems
        }
        for s in SYMBOLS
    }

    bucket_summary, monotonic_pass, inversions = merge_bucket_stats(bucket_inputs)

    score5 = portfolio["5bps"]["STATE_SCORE"]
    v75 = portfolio["5bps"]["V7"]
    bh5 = portfolio["5bps"]["BUY_HOLD"]
    score10 = portfolio["10bps"]["STATE_SCORE"]
    v710 = portfolio["10bps"]["V7"]
    score20 = portfolio["20bps"]["STATE_SCORE"]
    v720 = portfolio["20bps"]["V7"]

    breadth = {
        "return_gt_v7": sum(per_symbol[s]["5bps"]["STATE_SCORE"]["total_return"] > per_symbol[s]["5bps"]["V7"]["total_return"] for s in SYMBOLS),
        "calmar_gt_v7": sum(per_symbol[s]["5bps"]["STATE_SCORE"]["calmar"] > per_symbol[s]["5bps"]["V7"]["calmar"] for s in SYMBOLS),
        "return_gt_buyhold": sum(per_symbol[s]["5bps"]["STATE_SCORE"]["total_return"] > per_symbol[s]["5bps"]["BUY_HOLD"]["total_return"] for s in SYMBOLS),
    }

    gates = {
        "portfolio_return_gt_v7_5bps": score5["total_return"] > v75["total_return"],
        "portfolio_calmar_gt_v7_5bps": score5["calmar"] > v75["calmar"],
        "portfolio_return_ge_buyhold_5bps": score5["total_return"] >= bh5["total_return"],
        "portfolio_calmar_gt_buyhold_5bps": score5["calmar"] > bh5["calmar"],
        "portfolio_maxdd_better_than_buyhold": score5["max_drawdown"] > bh5["max_drawdown"],
        "symbol_return_gt_v7_ge_16": breadth["return_gt_v7"] >= 16,
        "symbol_calmar_gt_v7_ge_16": breadth["calmar_gt_v7"] >= 16,
        "symbol_return_gt_buyhold_ge_16": breadth["return_gt_buyhold"] >= 16,
        "score_bucket_monotonicity": monotonic_pass,
        "return_gt_v7_10bps": score10["total_return"] > v710["total_return"],
        "calmar_gt_v7_20bps": score20["calmar"] > v720["calmar"],
    }

    if all(gates.values()):
        decision = "PROMOTE_STATE_SCORE_MODE_TO_ENGINEERING_CANDIDATE"
    elif gates["portfolio_return_gt_v7_5bps"] and gates["portfolio_calmar_gt_v7_5bps"]:
        decision = "RESEARCH_ONLY_NEEDS_NEW_SCORE_ARCHITECTURE"
    else:
        decision = "REJECTED_STATE_SCORE_V1"

    out = {
        "meta": {
            "study": "SLTD_STATE_SCORE_MODE_V1",
            "status": "COMPLETE",
            "protocol": "SLTD_STATE_SCORE_MODE_V1_PROTOCOL.md",
            "independent_of_v7_rules": True,
            "chan_used": False,
            "fresh30": UNIVERSE,
            "prior_overlap": overlap,
            "formal_window": "2020-01-02..2026-09-30",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        },
        "model_summary": {
            "admitted_state_count": model["admitted_state_count"],
            "score_quantiles": model["score_quantiles"],
            "development_score_stats": model["development_score_stats"],
        },
        "portfolio": portfolio,
        "breadth_5bps": breadth,
        "fresh30_score_buckets": bucket_summary,
        "score_monotonicity": {
            "pass": monotonic_pass,
            "inversions": inversions,
        },
        "gates": gates,
        "decision": decision,
        "per_symbol": per_symbol,
    }
    OUT_JSON.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# SLTD State Score Mode v1 — Result",
        "",
        "Status: **COMPLETE**",
        "",
        f"Decision: **{decision}**",
        "",
        "This is an independent SLTD mode. It does not use V7 BUY/SELL rules, V7 position changes or C2.",
        "",
        f"Admitted state effects in frozen model: **{model['admitted_state_count']}**",
        "",
        "## Frozen score thresholds",
        "",
        f"- q20: {model['score_quantiles']['q20']:.6f}",
        f"- q40: {model['score_quantiles']['q40']:.6f}",
        f"- q60: {model['score_quantiles']['q60']:.6f}",
        f"- q80: {model['score_quantiles']['q80']:.6f}",
        "",
        "## Equal-weight Fresh30 portfolio — 5 bps",
        "",
        "| System | Return | CAGR | MaxDD | Calmar | Turnover | Exposure |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for label in ("STATE_SCORE", "V7", "BUY_HOLD", "SMA200_TREND"):
        m = portfolio["5bps"][label]
        lines.append(
            f"| {label} | {pct(m['total_return'])} | {pct(m['cagr'])} | {pct(m['max_drawdown'])} | "
            f"{m['calmar']:.3f} | {m['turnover_mean']:.2f} | {pct(m['time_in_market_mean'])} |"
        )

    lines += [
        "",
        "## Fresh30 breadth — 5 bps",
        "",
        f"- State Score return > V7: **{breadth['return_gt_v7']}/30**",
        f"- State Score Calmar > V7: **{breadth['calmar_gt_v7']}/30**",
        f"- State Score return > Buy & Hold: **{breadth['return_gt_buyhold']}/30**",
        "",
        "## Fresh30 score buckets",
        "",
        "| Target exposure | N | 10d median | 20d median | 10d win | 20d win |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for x in ("0.0", "0.25", "0.5", "0.75", "1.0"):
        b = bucket_summary[x]
        lines.append(
            f"| {float(x)*100:.0f}% | {b['n']} | {pct(b['ret10_median'])} | {pct(b['ret20_median'])} | "
            f"{pct(b['ret10_win_rate'])} | {pct(b['ret20_win_rate'])} |"
        )

    lines += [
        "",
        f"Score-bucket monotonicity: **{'PASS' if monotonic_pass else 'FAIL'}**",
        "",
        "## Admission gates",
        "",
    ]
    for k, v in gates.items():
        lines.append(f"- {k}: **{'PASS' if v else 'FAIL'}**")

    lines += [
        "",
        "## Decision boundary",
        "",
        "The production V7 remains untouched. This result governs only the independent State Score mode.",
        "",
        f"SLTD_STATE_SCORE_MODE_V1 = {decision}",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps({
        "decision": decision,
        "model": out["model_summary"],
        "portfolio_5bps": {k: compact(v) for k, v in portfolio["5bps"].items()},
        "portfolio_10bps": {k: compact(v) for k, v in portfolio["10bps"].items()},
        "portfolio_20bps": {k: compact(v) for k, v in portfolio["20bps"].items()},
        "breadth_5bps": breadth,
        "score_monotonicity": out["score_monotonicity"],
        "fresh30_score_buckets": bucket_summary,
        "gates": gates,
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
