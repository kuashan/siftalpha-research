#!/usr/bin/env python3
"""Merge SLTD V6 stock validation batches 5-8 and apply frozen gates.

This script is governance-critical:
- it loads only the five discovery-frozen candidates;
- it does not rerank candidates using validation performance;
- it evaluates the preregistered admission gates;
- the promoted stock policy is the first passing candidate in frozen order.
"""
from __future__ import annotations

import json
import statistics
from pathlib import Path


ROOT = Path(__file__).resolve().parent
BATCH_ROOT = ROOT / "batches"
SHORTLIST = ROOT / "SLTD_V6_POSITION_POLICY_DISCOVERY_FROZEN_SHORTLIST_v1.json"
OUT_JSON = ROOT / "SLTD_V6_POSITION_POLICY_STOCK_VALIDATION_DECISION_v1.json"
OUT_MD = ROOT / "SLTD_V6_POSITION_POLICY_STOCK_VALIDATION_DECISION_v1.md"
BATCHES = (5, 6, 7, 8)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    frozen = load(SHORTLIST)
    if frozen["meta"].get("status") != "FROZEN_BEFORE_VALIDATION":
        raise RuntimeError("Discovery shortlist is not frozen")
    shortlist = frozen.get("shortlist", [])
    if len(shortlist) != 5:
        raise RuntimeError(f"Expected five frozen candidates, got {len(shortlist)}")

    expected_roles = ["PRIMARY", "BACKUP_1", "BACKUP_2", "BACKUP_3", "BACKUP_4"]
    if [x.get("role") for x in shortlist] != expected_roles:
        raise RuntimeError("Frozen role order changed")

    batch_docs = {}
    for b in BATCHES:
        path = BATCH_ROOT / f"BATCH_{b:02d}_STOCK_POSITION_POLICY_VALIDATION.json"
        doc = load(path)
        meta = doc.get("meta", {})
        if meta.get("status") != "BATCH_COMPLETE":
            raise RuntimeError(f"Validation batch {b} is not complete")
        if meta.get("stage") != "VALIDATION":
            raise RuntimeError(f"Batch {b} is not validation")
        candidates = doc.get("candidates", [])
        if len(candidates) != 5:
            raise RuntimeError(f"Batch {b}: expected 5 candidates, got {len(candidates)}")
        frozen_ids = [x["policy_id"] for x in shortlist]
        batch_ids = [x["policy_id"] for x in candidates]
        if batch_ids != frozen_ids:
            raise RuntimeError(f"Batch {b}: candidate order/identity drift")
        batch_docs[b] = doc

    results = []
    for frozen_item in shortlist:
        pid = frozen_item["policy_id"]
        rows = []
        for b in BATCHES:
            item = next(x for x in batch_docs[b]["candidates"] if x["policy_id"] == pid)
            rows.append({
                "batch": b,
                "baseline_5bps": item["baseline_5bps"],
                "stress_10bps": item["stress_10bps"],
            })

        calmars = [x["baseline_5bps"]["calmar"] for x in rows]
        cagrs = [x["baseline_5bps"]["cagr"] for x in rows]
        stress_calmars = [x["stress_10bps"]["calmar"] for x in rows]
        mdds = [x["baseline_5bps"]["max_drawdown"] for x in rows]

        gates = {
            "at_least_3_of_4_calmar_gt_0": sum(x > 0 for x in calmars) >= 3,
            "median_validation_calmar_gt_0": statistics.median(calmars) > 0,
            "median_validation_cagr_gt_0": statistics.median(cagrs) > 0,
            "median_10bps_validation_calmar_gt_0": statistics.median(stress_calmars) > 0,
            "no_validation_batch_maxdd_worse_than_minus_60pct": all(x >= -0.60 for x in mdds),
        }
        passed = all(gates.values())
        results.append({
            "shortlist_rank": frozen_item["shortlist_rank"],
            "role": frozen_item["role"],
            "discovery_rank": frozen_item["discovery_rank"],
            "policy_id": pid,
            "policy": frozen_item["policy"],
            "validation_batches": rows,
            "summary": {
                "positive_calmar_batches": sum(x > 0 for x in calmars),
                "median_validation_calmar": statistics.median(calmars),
                "median_validation_cagr": statistics.median(cagrs),
                "median_10bps_validation_calmar": statistics.median(stress_calmars),
                "worst_validation_max_drawdown": min(mdds),
            },
            "gates": gates,
            "passes_all_validation_gates": passed,
        })

    promoted = next((x for x in results if x["passes_all_validation_gates"]), None)
    decision = {
        "meta": {
            "study": "SLTD_V6_POSITION_POLICY_STUDY_V1",
            "stage": "STOCK_VALIDATION_DECISION",
            "status": "COMPLETE",
            "validation_batches": list(BATCHES),
            "selection_rule": (
                "Choose the first candidate in frozen discovery order that meets all "
                "preregistered validation gates; otherwise NO_POLICY_PROMOTED."
            ),
            "validation_is_admission_not_ranking": True,
        },
        "validation_gates": [
            "at least 3 of 4 validation batches have Calmar > 0",
            "median validation-batch Calmar > 0",
            "median validation-batch CAGR > 0",
            "median 10 bps validation-batch Calmar > 0",
            "no validation batch Max Drawdown worse than -60%",
        ],
        "candidates": results,
        "decision": {
            "stock_policy_promoted": promoted is not None,
            "result": promoted["policy_id"] if promoted else "NO_POLICY_PROMOTED",
            "role": promoted["role"] if promoted else None,
            "shortlist_rank": promoted["shortlist_rank"] if promoted else None,
            "policy": promoted["policy"] if promoted else None,
        },
    }
    OUT_JSON.write_text(json.dumps(decision, indent=2), encoding="utf-8")

    lines = [
        "# SLTD V6 Position Policy — Stock Validation Decision v1",
        "",
        "Status: **COMPLETE**",
        "",
        "Validation batches: **5, 6, 7, 8**",
        "",
        "Selection rule: use the first candidate in the frozen discovery order that passes all",
        "preregistered validation gates. Validation results are admission gates, not a reranking objective.",
        "",
        "## Validation summary",
        "",
        "| Frozen slot | Policy | Positive Calmar batches | Median Calmar | Median CAGR | Median 10bps Calmar | Worst MaxDD | Gates |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for x in results:
        s = x["summary"]
        status = "PASS" if x["passes_all_validation_gates"] else "FAIL"
        lines.append(
            f"| {x['role']} | \`{x['policy_id']}\` | {s['positive_calmar_batches']}/4 | "
            f"{s['median_validation_calmar']:.3f} | {100*s['median_validation_cagr']:.2f}% | "
            f"{s['median_10bps_validation_calmar']:.3f} | {100*s['worst_validation_max_drawdown']:.2f}% | **{status}** |"
        )

    lines += [
        "",
        "## Gate details",
        "",
    ]
    for x in results:
        lines.append(f"### {x['role']} — \`{x['policy_id']}\`")
        lines.append("")
        for name, ok in x["gates"].items():
            lines.append(f"- {'PASS' if ok else 'FAIL'} — {name}")
        lines.append("")

    if promoted:
        p = promoted["policy"]
        lines += [
            "## Stock policy decision",
            "",
            f"**PROMOTED:** \`{promoted['policy_id']}\`",
            "",
            f"Frozen role: **{promoted['role']}**",
            "",
            f"Execution policy: initial={int(round(100*p['initial']))}%, "
            f"add={p['add_mode']}, sell_reduction={int(round(100*p['sell_reduction']))}%, "
            f"wait={p['wait_mode']}, mixed={p['resolution']}.",
            "",
            "The policy was selected by frozen order + admission gates, not by validation reranking.",
            "",
            "Batch 9 remains a crypto transfer check only and cannot change this stock-selected policy.",
            "",
            "\`SLTD_V6_STOCK_POLICY = PROMOTED\`",
            "",
        ]
    else:
        lines += [
            "## Stock policy decision",
            "",
            "**NO_POLICY_PROMOTED**",
            "",
            "No frozen candidate passed every preregistered validation gate.",
            "",
            "\`SLTD_V6_STOCK_POLICY = NO_POLICY_PROMOTED\`",
            "",
        ]

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
