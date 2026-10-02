#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PHASE7 = ROOT / "research" / "ssss_reboot_v1" / "phase7"
BATCH_DIR = PHASE7 / "batches"
MERGED = PHASE7 / "SLTD_V6_POSITION_POLICY_DISCOVERY_MERGED_v1.json"
OUT_JSON = PHASE7 / "SLTD_V6_POSITION_POLICY_DISCOVERY_FROZEN_SHORTLIST_v1.json"
OUT_MD = PHASE7 / "SLTD_V6_POSITION_POLICY_DISCOVERY_FROZEN_SHORTLIST_v1.md"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def outcome_signature(policy_id: str, batch_maps: list[dict[str, dict]]) -> str:
    rows = []
    for batch_no, batch_map in enumerate(batch_maps, start=1):
        p = batch_map[policy_id]
        rows.append({
            "batch": batch_no,
            "baseline_5bps": p["baseline_5bps"],
            "stress_10bps": p["stress_10bps"],
        })
    return json.dumps(rows, sort_keys=True, separators=(",", ":"))


def main() -> None:
    merged = load_json(MERGED)
    if merged["meta"].get("status") != "COMPLETE":
        raise RuntimeError("Merged discovery result is not COMPLETE")

    batches = [load_json(BATCH_DIR / f"BATCH_{i:02d}_STOCK_POSITION_POLICY.json") for i in range(1, 5)]
    for i, b in enumerate(batches, start=1):
        if b["meta"].get("status") != "BATCH_COMPLETE":
            raise RuntimeError(f"Batch {i} is not COMPLETE")

    batch_maps = [{p["policy_id"]: p for p in b["policies"]} for b in batches]
    ranked = merged["policies"]

    groups: dict[str, list[dict]] = {}
    group_order: list[str] = []
    for row in ranked:
        sig = outcome_signature(row["policy_id"], batch_maps)
        if sig not in groups:
            groups[sig] = []
            group_order.append(sig)
        groups[sig].append(row)

    unique_reps = [groups[sig][0] for sig in group_order]
    if len(unique_reps) < 5:
        raise RuntimeError("Fewer than five unique discovery-observed outcome groups")

    shortlist = []
    for shortlist_rank, rep in enumerate(unique_reps[:5], start=1):
        sig = outcome_signature(rep["policy_id"], batch_maps)
        members = groups[sig]
        shortlist.append({
            "shortlist_rank": shortlist_rank,
            "role": "PRIMARY" if shortlist_rank == 1 else f"BACKUP_{shortlist_rank-1}",
            "discovery_rank": rep["discovery_rank"],
            "policy_id": rep["policy_id"],
            "policy": rep["policy"],
            "discovery": rep["discovery"],
            "batches": rep["batches"],
            "equivalent_policy_count": len(members),
            "equivalent_policy_ids": [x["policy_id"] for x in members],
        })

    out = {
        "meta": {
            "study": "SLTD_V6_POSITION_POLICY_STUDY_V1",
            "stage": "DISCOVERY_SHORTLIST_FREEZE",
            "status": "FROZEN_BEFORE_VALIDATION",
            "source": MERGED.name,
            "raw_candidate_count": len(ranked),
            "unique_discovery_observed_outcome_groups": len(unique_reps),
            "shortlist_count": 5,
            "dedup_rule": (
                "Policies are discovery-observed equivalents only when their complete "
                "B1-B4 baseline_5bps and stress_10bps aggregate metric dictionaries are "
                "exactly identical. The representative is the earliest policy in the "
                "already-frozen discovery ranking. Deduplication does not reorder any "
                "non-equivalent policy."
            ),
            "governance_note": (
                "User-directed pre-validation procedural amendment: exact discovery-observed "
                "duplicates are skipped when filling Primary + four Backup slots so validation "
                "covers five distinct observed outcomes. No Batch 5-8 validation outcome was "
                "used to define or select this shortlist."
            ),
        },
        "shortlist": shortlist,
    }
    OUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")

    lines = [
        "# SLTD V6 Position Policy — Frozen Discovery Shortlist v1",
        "",
        "Status: **FROZEN BEFORE VALIDATION**",
        "",
        "Source: Batches 1-4 merged discovery ranking.",
        "",
        f"Raw Stage A candidates: **{len(ranked)}**",
        f"Unique discovery-observed outcome groups: **{len(unique_reps)}**",
        "",
        "## Deduplication rule",
        "",
        "Two policies are treated as discovery-observed equivalents only when their complete",
        "B1-B4 baseline 5 bps and stress 10 bps aggregate metric dictionaries are exactly identical.",
        "Within each equivalence group, the earliest policy in the frozen discovery ranking is the representative.",
        "Deduplication never reorders non-equivalent policies.",
        "",
        "This is a user-directed pre-validation procedural amendment made before inspecting any",
        "Batch 5-8 validation outcome. Its only purpose is to prevent Backup slots from being",
        "consumed by policies that produced exactly the same observed discovery outcomes.",
        "",
        "## Frozen Primary + Backups",
        "",
        "| Slot | Discovery Rank | Policy | Median Calmar | Worst Calmar | Median CAGR | Median MaxDD | Median 10bps Calmar | Equivalent Count |",
        "|---|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    for x in shortlist:
        d = x["discovery"]
        lines.append(
            f"| {x['role']} | {x['discovery_rank']} | \`{x['policy_id']}\` | "
            f"{d['median_batch_calmar']:.3f} | {d['worst_batch_calmar']:.3f} | "
            f"{100*d['median_batch_cagr']:.2f}% | -{100*d['median_batch_max_drawdown_magnitude']:.2f}% | "
            f"{d['median_stress_10bps_calmar']:.3f} | {x['equivalent_policy_count']} |"
        )

    lines += [
        "",
        "## Frozen execution semantics",
        "",
    ]
    for x in shortlist:
        p = x["policy"]
        lines.append(
            f"- **{x['role']}**: initial={int(round(100*p['initial']))}%, "
            f"add={p['add_mode']}, sell_reduction={int(round(100*p['sell_reduction']))}%, "
            f"wait={p['wait_mode']}, mixed={p['resolution']}."
        )

    lines += [
        "",
        "These five representatives are frozen in this order for Batch 5-8 validation.",
        "No later batch may retune or reorder them.",
        "",
        "`SLTD_V6_POSITION_POLICY_DISCOVERY_SHORTLIST = FROZEN_BEFORE_VALIDATION`",
        "",
    ]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
