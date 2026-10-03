from __future__ import annotations

import csv
import gzip
import json
import math
import statistics
import sys
from collections import Counter
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
PROJECT = REPO / "integrations" / "sltd_v7_siftalpha_v1"
sys.path.insert(0, str(PROJECT))

import strategy as sltd  # noqa: E402
import sltd_exit_stack as exits  # noqa: E402


DATA_ROOT = REPO / "research" / "ssss_reboot_v1" / "phase7" / "data_snapshot"

VARIANTS = [
    exits.ExitStackConfig(
        name="CHAND_ONLY_22_3",
        chan_levels="none",
        chandelier=True,
    ),
    exits.ExitStackConfig(
        name="L0_ANY_FLAT25_CHAND",
        chan_levels="l0",
        chan_certainty="any",
        chan_fraction_mode="flat25",
        chandelier=True,
    ),
    exits.ExitStackConfig(
        name="L0_ANY_GRADED_CHAND",
        chan_levels="l0",
        chan_certainty="any",
        chan_fraction_mode="graded",
        chandelier=True,
    ),
    exits.ExitStackConfig(
        name="L1_ANY_GRADED_CHAND",
        chan_levels="l1",
        chan_certainty="any",
        chan_fraction_mode="graded",
        chandelier=True,
    ),
    exits.ExitStackConfig(
        name="ALL_ANY_GRADED_CHAND",
        chan_levels="all",
        chan_certainty="any",
        chan_fraction_mode="graded",
        chandelier=True,
    ),
    exits.ExitStackConfig(
        name="ALL_SURE_GRADED_CHAND",
        chan_levels="all",
        chan_certainty="sure",
        chan_fraction_mode="graded",
        chandelier=True,
    ),
]


def load(path: Path) -> list[dict]:
    out = []
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            out.append(
                {
                    "date": row["Date"][:10],
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "volume": float(row.get("Volume") or 0.0),
                }
            )
    return out


def max_drawdown(values: list[float]) -> float:
    peak = None
    worst = 0.0
    for raw in values:
        v = float(raw)
        peak = v if peak is None else max(peak, v)
        if peak and peak > 0:
            worst = min(worst, v / peak - 1.0)
    return worst


def start_index(bars: list[dict]) -> int:
    formal_index = next(
        (i for i, b in enumerate(bars) if b["date"] >= sltd.POLICY_START_DATE),
        0,
    )
    warmup_index = min(sltd.MIN_WARMUP_BARS, len(bars) - 1)
    return max(formal_index, warmup_index)


def cagr(bars: list[dict], final_equity: float) -> float:
    s = start_index(bars)
    d0 = date.fromisoformat(bars[s]["date"][:10])
    d1 = date.fromisoformat(bars[-1]["date"][:10])
    years = max((d1 - d0).days / 365.25, 1.0 / 365.25)
    if final_equity <= 0:
        return -1.0
    return final_equity ** (1.0 / years) - 1.0


def episode_metrics(sim: dict) -> dict:
    positions = sim["positions"]
    equity = sim["equity_curve"]
    in_pos = False
    start = None
    peak = None
    givebacks = []
    holding = []

    for i, (p, eq) in enumerate(zip(positions, equity)):
        active = float(p.get("fraction") or 0.0) > 1e-9
        e = float(eq)
        if active and not in_pos:
            in_pos = True
            start = i
            peak = e
        elif active:
            peak = max(float(peak), e)
        elif in_pos:
            if peak is not None and peak > 0:
                givebacks.append(max(0.0, 1.0 - e / peak))
            if start is not None:
                holding.append(max(1, i - start))
            in_pos = False
            start = None
            peak = None

    return {
        "episodes_closed": len(givebacks),
        "mean_giveback": statistics.fmean(givebacks) if givebacks else None,
        "median_giveback": statistics.median(givebacks) if givebacks else None,
        "mean_holding_bars": statistics.fmean(holding) if holding else None,
        "givebacks": givebacks,
        "holding": holding,
    }


def baseline_counts(sim: dict) -> dict:
    c = Counter()
    for m in sim.get("markers", []):
        action = str(m.get("action") or "")
        if action == "BUY":
            c["BUY"] += 1
        elif action == "SELL":
            c["SLTD_SELL"] += 1
        elif action == "HARD_EXIT":
            c["C2_FULL_EXIT"] += 1
    return dict(c)


def row_metrics(symbol: str, bars: list[dict], sim: dict, name: str) -> dict:
    ep = episode_metrics(sim)
    counts = sim.get("execution_counts") or baseline_counts(sim)
    eq = float(sim["final_equity"])
    dd = float(sim.get("max_drawdown", max_drawdown(sim["equity_curve"])))
    exposure = statistics.fmean(
        float(x.get("fraction") or 0.0) for x in sim["positions"]
    )
    return {
        "symbol": symbol,
        "variant": name,
        "return": eq - 1.0,
        "final_equity": eq,
        "cagr": cagr(bars, eq),
        "max_drawdown": dd,
        "exposure": exposure,
        "episodes_closed": ep["episodes_closed"],
        "mean_giveback": ep["mean_giveback"],
        "mean_holding_bars": ep["mean_holding_bars"],
        "counts": counts,
        "givebacks": ep["givebacks"],
        "holding": ep["holding"],
    }


def r6(x):
    return None if x is None else round(float(x), 6)


def summarize(rows: list[dict], baseline: dict[str, dict] | None = None) -> dict:
    returns = [x["return"] for x in rows]
    cagrs = [x["cagr"] for x in rows]
    dds = [x["max_drawdown"] for x in rows]
    exposures = [x["exposure"] for x in rows]
    givebacks = [g for x in rows for g in x["givebacks"]]
    holding = [h for x in rows for h in x["holding"]]
    counts = Counter()
    for x in rows:
        counts.update(x["counts"])

    out = {
        "symbols": len(rows),
        "positive_return_symbols": sum(x > 0 for x in returns),
        "mean_return": r6(statistics.fmean(returns)),
        "median_return": r6(statistics.median(returns)),
        "mean_cagr": r6(statistics.fmean(cagrs)),
        "median_cagr": r6(statistics.median(cagrs)),
        "mean_max_drawdown": r6(statistics.fmean(dds)),
        "median_max_drawdown": r6(statistics.median(dds)),
        "worst_max_drawdown": r6(min(dds)),
        "mean_exposure": r6(statistics.fmean(exposures)),
        "closed_episodes": len(givebacks),
        "mean_exit_giveback": r6(statistics.fmean(givebacks)) if givebacks else None,
        "median_exit_giveback": r6(statistics.median(givebacks)) if givebacks else None,
        "mean_holding_bars": r6(statistics.fmean(holding)) if holding else None,
        "execution_counts": dict(sorted(counts.items())),
    }

    if baseline is not None:
        outperform = 0
        lower_dd = 0
        both = 0
        ret_delta = []
        dd_delta = []
        for x in rows:
            b = baseline[x["symbol"]]
            ret_better = x["return"] > b["return"]
            dd_better = x["max_drawdown"] > b["max_drawdown"]
            outperform += int(ret_better)
            lower_dd += int(dd_better)
            both += int(ret_better and dd_better)
            ret_delta.append(x["return"] - b["return"])
            dd_delta.append(x["max_drawdown"] - b["max_drawdown"])
        out["vs_baseline"] = {
            "outperform_return_symbols": outperform,
            "lower_drawdown_symbols": lower_dd,
            "both_improved_symbols": both,
            "mean_return_delta": r6(statistics.fmean(ret_delta)),
            "median_return_delta": r6(statistics.median(ret_delta)),
            "mean_drawdown_delta": r6(statistics.fmean(dd_delta)),
            "median_drawdown_delta": r6(statistics.median(dd_delta)),
        }

    return out


def main() -> None:
    all_rows: dict[str, list[dict]] = {"BASELINE": []}
    for v in VARIANTS:
        all_rows[v.name] = []

    paths = sorted(DATA_ROOT.glob("batch_*_stocks/*.csv.gz"))
    print("SLTD_EXIT_STACK_EXPECTED_SYMBOLS", len(paths))

    for n, path in enumerate(paths, 1):
        symbol = path.stem.replace(".csv", "")
        bars = load(path)
        ledger = sltd.build_ledger(bars, symbol)

        baseline_sim = sltd.simulate_policy(bars, ledger, friction_bps=5.0)
        all_rows["BASELINE"].append(
            row_metrics(symbol, bars, baseline_sim, "BASELINE")
        )

        observations = exits.build_chan_sell_observations(symbol, bars)
        obs_counts = Counter()
        for x in observations:
            obs_counts[f"L{x['level']}_{x['kind']}"] += 1

        for variant in VARIANTS:
            sim = exits.simulate_exit_stack(
                bars,
                ledger,
                observations,
                variant,
                friction_bps=5.0,
            )
            all_rows[variant.name].append(
                row_metrics(symbol, bars, sim, variant.name)
            )

        print(
            "SLTD_EXIT_STACK_PROGRESS",
            n,
            symbol,
            len(bars),
            len(observations),
            json.dumps(dict(sorted(obs_counts.items())), sort_keys=True),
        )

    baseline_map = {
        x["symbol"]: x for x in all_rows["BASELINE"]
    }

    summaries = {
        "BASELINE": summarize(all_rows["BASELINE"]),
    }
    for variant in VARIANTS:
        summaries[variant.name] = summarize(
            all_rows[variant.name],
            baseline=baseline_map,
        )

    print("SLTD_EXIT_STACK_SUMMARIES", json.dumps(summaries, sort_keys=True))

    # Compact per-symbol delta table for the two intended combined candidates.
    for name in ("ALL_ANY_GRADED_CHAND", "ALL_SURE_GRADED_CHAND"):
        by_symbol = {x["symbol"]: x for x in all_rows[name]}
        compact = []
        for symbol in sorted(by_symbol):
            x = by_symbol[symbol]
            b = baseline_map[symbol]
            compact.append(
                {
                    "symbol": symbol,
                    "return_base": r6(b["return"]),
                    "return_new": r6(x["return"]),
                    "return_delta": r6(x["return"] - b["return"]),
                    "dd_base": r6(b["max_drawdown"]),
                    "dd_new": r6(x["max_drawdown"]),
                    "dd_delta": r6(x["max_drawdown"] - b["max_drawdown"]),
                    "exposure_base": r6(b["exposure"]),
                    "exposure_new": r6(x["exposure"]),
                    "counts": x["counts"],
                }
            )
        print(
            f"SLTD_EXIT_STACK_PER_SYMBOL_{name}",
            json.dumps(compact, sort_keys=True),
        )


if __name__ == "__main__":
    main()
