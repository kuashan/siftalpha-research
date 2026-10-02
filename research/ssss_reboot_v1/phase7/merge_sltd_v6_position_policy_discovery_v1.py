#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PHASE7 = ROOT / "research" / "ssss_reboot_v1" / "phase7"
BATCH_DIR = PHASE7 / "batches"
OUT_JSON = PHASE7 / "SLTD_V6_POSITION_POLICY_DISCOVERY_MERGED_v1.json"
OUT_MD = PHASE7 / "SLTD_V6_POSITION_POLICY_DISCOVERY_MERGED_v1.md"


def median(xs):
    return float(statistics.median(xs))


def load_batch(n: int) -> dict:
    path = BATCH_DIR / f"BATCH_{n:02d}_STOCK_POSITION_POLICY.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    meta = data["meta"]
    if meta.get("status") != "BATCH_COMPLETE":
        raise RuntimeError(f"Batch {n} is not COMPLETE")
    if meta.get("candidate_count") != 1152:
        raise RuntimeError(f"Batch {n} candidate_count != 1152")
    return data


def main() -> None:
    batches = [load_batch(i) for i in range(1, 5)]
    maps = [{p["policy_id"]: p for p in b["policies"]} for b in batches]
    ids = [p["policy_id"] for p in batches[0]["policies"]]
    idset = set(ids)
    for i, m in enumerate(maps[1:], start=2):
        if set(m) != idset:
            raise RuntimeError(f"Batch {i} policy universe mismatch")

    merged = []
    for pid in ids:
        ps = [m[pid] for m in maps]
        cals = [p["baseline_5bps"]["calmar"] for p in ps]
        cagrs = [p["baseline_5bps"]["cagr"] for p in ps]
        mdds = [p["baseline_5bps"]["max_drawdown"] for p in ps]
        turns = [p["baseline_5bps"]["turnover_mean"] for p in ps]
        stress_cals = [p["stress_10bps"]["calmar"] for p in ps]

        # Max Drawdown is stored as a negative return. "Lower Max Drawdown"
        # therefore means lower drawdown magnitude.
        median_mdd_magnitude = median([abs(x) for x in mdds])

        # The preregistered protocol says lower between-batch Calmar dispersion.
        # Operational definition: population standard deviation across B1-B4.
        calmar_dispersion = float(statistics.pstdev(cals))

        batch_rows = []
        for i, p in enumerate(ps, start=1):
            b = p["baseline_5bps"]
            s = p["stress_10bps"]
            batch_rows.append({
                "batch": i,
                "total_return": b["total_return"],
                "cagr": b["cagr"],
                "max_drawdown": b["max_drawdown"],
                "calmar": b["calmar"],
                "turnover_mean": b["turnover_mean"],
                "position_changes_sum": b["position_changes_sum"],
                "time_in_market_mean": b["time_in_market_mean"],
                "stress_10bps_calmar": s["calmar"],
            })

        merged.append({
            "policy_id": pid,
            "policy": ps[0]["policy"],
            "discovery": {
                "median_batch_calmar": median(cals),
                "worst_batch_calmar": min(cals),
                "median_batch_cagr": median(cagrs),
                "median_batch_max_drawdown_magnitude": median_mdd_magnitude,
                "calmar_dispersion_population_std": calmar_dispersion,
                "median_batch_turnover": median(turns),
                "median_stress_10bps_calmar": median(stress_cals),
            },
            "batches": batch_rows,
        })

    merged.sort(key=lambda x: (
        -x["discovery"]["median_batch_calmar"],
        -x["discovery"]["worst_batch_calmar"],
        -x["discovery"]["median_batch_cagr"],
        x["discovery"]["median_batch_max_drawdown_magnitude"],
        x["discovery"]["calmar_dispersion_population_std"],
        x["discovery"]["median_batch_turnover"],
        x["policy_id"],
    ))

    for rank, row in enumerate(merged, start=1):
        row["discovery_rank"] = rank

    out = {
        "meta": {
            "study": "SLTD_V6_POSITION_POLICY_STUDY_V1",
            "stage": "DISCOVERY_MERGED_B1_B4",
            "status": "COMPLETE",
            "candidate_count": len(merged),
            "batches": [1, 2, 3, 4],
            "ranking": [
                "higher median batch Calmar",
                "higher worst-batch Calmar",
                "higher median batch CAGR",
                "lower median batch Max Drawdown magnitude",
                "lower between-batch Calmar population standard deviation",
                "lower median batch turnover",
                "policy_id only as deterministic final tie-break",
            ],
            "note": "This file merges discovery outcomes only. Primary + four Backups are not frozen by this merge step.",
        },
        "policies": merged,
    }
    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")

    def pct(x):
        return f"{100*x:.2f}%"

    def num(x):
        return f"{x:.3f}"

    lines = [
        "# SLTD V6 Position Policy — Discovery Merge B1-B4",
        "",
        "Status: **COMPLETE**",
        "",
        "This is the mechanical merge/ranking of the four frozen discovery batches.",
        "No Stage A parameters were changed.",
        "",
        "Candidates merged: **1,152**",
        "",
        "Primary + four Backups are **not frozen by this merge step**.",
        "",
        "## Ranking semantics",
        "",
        "1. higher median batch Calmar",
        "2. higher worst-batch Calmar",
        "3. higher median batch CAGR",
        "4. lower median batch Max Drawdown magnitude",
        "5. lower between-batch Calmar dispersion (population standard deviation)",
        "6. lower median batch turnover",
        "",
        "## Top 20 merged discovery ranking",
        "",
        "| Rank | Policy | Median Calmar | Worst Calmar | Median CAGR | Median MaxDD | Calmar Disp. | Median Turnover | Median 10bps Calmar |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in merged[:20]:
        d = row["discovery"]
        lines.append(
            f"| {row['discovery_rank']} | \`{row['policy_id']}\` | "
            f"{num(d['median_batch_calmar'])} | {num(d['worst_batch_calmar'])} | "
            f"{pct(d['median_batch_cagr'])} | -{pct(d['median_batch_max_drawdown_magnitude'])} | "
            f"{num(d['calmar_dispersion_population_std'])} | {num(d['median_batch_turnover'])} | "
            f"{num(d['median_stress_10bps_calmar'])} |"
        )

    lines += [
        "",
        "## Top 5 batch-by-batch Calmar",
        "",
        "| Rank | Policy | B1 | B2 | B3 | B4 |",
        "|---:|---|---:|---:|---:|---:|",
    ]
    for row in merged[:5]:
        b = row["batches"]
        lines.append(
            f"| {row['discovery_rank']} | \`{row['policy_id']}\` | "
            + " | ".join(num(x["calmar"]) for x in b) + " |"
        )

    lines += [
        "",
        "`SLTD_V6_POSITION_POLICY_DISCOVERY_MERGE_B1_B4 = COMPLETE`",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
