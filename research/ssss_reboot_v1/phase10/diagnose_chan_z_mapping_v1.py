from __future__ import annotations

import csv
import gzip
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PROJECT = ROOT / "integrations" / "sltd_v7_siftalpha_v1"
sys.path.insert(0, str(PROJECT))

import chan_strategy as ch  # noqa: E402

DATA_ROOT = ROOT / "research" / "ssss_reboot_v1" / "phase7" / "data_snapshot"


def load(path: Path) -> list[dict]:
    out: list[dict] = []
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


def triple_overlap(units, i: int) -> bool:
    seed = units[i : i + 3]
    if len(seed) < 3:
        return False
    return max(x.low for x in seed) <= min(x.high for x in seed)


tot = Counter()
by_level: dict[int, Counter] = defaultdict(Counter)
examples: dict[str, list] = defaultdict(list)
symbols = 0

for path in sorted(DATA_ROOT.glob("batch_*_stocks/*.csv.gz")):
    symbols += 1
    sym = path.stem.split(".")[0]
    bars0 = ch._validate_candles(load(path))
    bars, _ = ch._slice_analysis_window(bars0)
    snap = ch.build_structure_snapshot(bars)

    for info in snap["levels"]:
        if not bool(info.get("canonical", False)):
            continue

        level = int(info["level"])
        units = list(info["units"])
        completed = [x for x in units if not x.pending and x.confirm_index is not None]
        c = by_level[level]

        c["streams"] += 1
        c["units"] += len(units)
        c["completed_units"] += len(completed)
        c["current_zhongshus"] += len(info["zss"])

        tot["streams"] += 1
        tot["units"] += len(units)
        tot["completed_units"] += len(completed)
        tot["current_zhongshus"] += len(info["zss"])

        for seq_name, seq in (("all", units), ("completed", completed)):
            for i in range(1, len(seq)):
                a, b = seq[i - 1], seq[i]
                if a.direction == b.direction:
                    key = f"{seq_name}_same_direction"
                    c[key] += 1
                    tot[key] += 1
                    if len(examples[key]) < 20:
                        examples[key].append(
                            {
                                "symbol": sym,
                                "level": level,
                                "left": a.source_start,
                                "right": b.source_start,
                                "direction": a.direction,
                            }
                        )
                if a.to_index != b.from_index:
                    key = f"{seq_name}_chain_break"
                    c[key] += 1
                    tot[key] += 1
                    if len(examples[key]) < 20:
                        examples[key].append(
                            {
                                "symbol": sym,
                                "level": level,
                                "left_to": a.to_index,
                                "right_from": b.from_index,
                            }
                        )

        # Audit each current Zhongshu against lesson-20 Z-movement
        # semantics.  start_sub/end_sub are indices in the completed-unit
        # stream used by build_zhongshus().
        for zi, zs in enumerate(info["zss"]):
            start = int(zs.start_sub)
            end = int(zs.end_sub)
            if start + 2 >= len(completed):
                c["zs_bad_seed_index"] += 1
                tot["zs_bad_seed_index"] += 1
                continue

            z1 = completed[start]
            z2 = completed[start + 2]
            source_zg = min(z1.high, z2.high)
            source_zd = max(z1.low, z2.low)

            if abs(float(zs.zg) - source_zg) > 1e-9:
                c["zs_zg_formula_mismatch"] += 1
                tot["zs_zg_formula_mismatch"] += 1
                if len(examples["zs_zg_formula_mismatch"]) < 20:
                    examples["zs_zg_formula_mismatch"].append(
                        {
                            "symbol": sym,
                            "level": level,
                            "zs": zi,
                            "stored": zs.zg,
                            "source": source_zg,
                            "start": start,
                        }
                    )
            if abs(float(zs.zd) - source_zd) > 1e-9:
                c["zs_zd_formula_mismatch"] += 1
                tot["zs_zd_formula_mismatch"] += 1
                if len(examples["zs_zd_formula_mismatch"]) < 20:
                    examples["zs_zd_formula_mismatch"].append(
                        {
                            "symbol": sym,
                            "level": level,
                            "zs": zi,
                            "stored": zs.zd,
                            "source": source_zd,
                            "start": start,
                        }
                    )

            # Every same-parity Z movement absorbed by the center must still
            # overlap [ZD,ZG].  Strict outside means the source extension
            # theorem has already stopped.
            for j in range(start, min(end, len(completed) - 1) + 1, 2):
                z = completed[j]
                strict_outside = z.low > zs.zg or z.high < zs.zd
                if strict_outside:
                    c["zs_absorbs_outside_z"] += 1
                    tot["zs_absorbs_outside_z"] += 1
                    if len(examples["zs_absorbs_outside_z"]) < 20:
                        examples["zs_absorbs_outside_z"].append(
                            {
                                "symbol": sym,
                                "level": level,
                                "zs": zi,
                                "z_index": j,
                                "z_low": z.low,
                                "z_high": z.high,
                                "ZD": zs.zd,
                                "ZG": zs.zg,
                            }
                        )

            if not zs.pending and (end - start) % 2 != 0:
                c["zs_completed_end_wrong_parity"] += 1
                tot["zs_completed_end_wrong_parity"] += 1
                if len(examples["zs_completed_end_wrong_parity"]) < 20:
                    examples["zs_completed_end_wrong_parity"].append(
                        {
                            "symbol": sym,
                            "level": level,
                            "zs": zi,
                            "start": start,
                            "end": end,
                        }
                    )

            # Find the first same-parity Z movement after the stored end.
            next_z = end + 1
            while next_z < len(completed) and (next_z - start) % 2 != 0:
                next_z += 1
            if next_z < len(completed) and not zs.pending:
                z = completed[next_z]
                strict_overlap = z.low < zs.zg and z.high > zs.zd
                boundary_only = (
                    not strict_overlap
                    and z.low <= zs.zg
                    and z.high >= zs.zd
                )
                if strict_overlap:
                    c["zs_ends_before_overlapping_next_z"] += 1
                    tot["zs_ends_before_overlapping_next_z"] += 1
                    if len(examples["zs_ends_before_overlapping_next_z"]) < 20:
                        examples["zs_ends_before_overlapping_next_z"].append(
                            {
                                "symbol": sym,
                                "level": level,
                                "zs": zi,
                                "end": end,
                                "next_z": next_z,
                                "z_low": z.low,
                                "z_high": z.high,
                                "ZD": zs.zd,
                                "ZG": zs.zg,
                            }
                        )
                elif boundary_only:
                    c["zs_next_z_boundary_touch"] += 1
                    tot["zs_next_z_boundary_touch"] += 1

        if len(completed) >= 3 and triple_overlap(completed, 0):
            c["left_edge_seed_overlap"] += 1
            tot["left_edge_seed_overlap"] += 1
            if not any(int(z.start_sub) == 0 for z in info["zss"]):
                c["left_edge_seed_skipped"] += 1
                tot["left_edge_seed_skipped"] += 1

        for i in range(0, max(0, len(completed) - 2)):
            a, b, cc = completed[i : i + 3]
            c["triples"] += 1
            tot["triples"] += 1

            alternating = (
                a.direction != b.direction
                and b.direction != cc.direction
                and a.direction == cc.direction
            )
            if alternating:
                c["alternating_triples"] += 1
                tot["alternating_triples"] += 1

            overlap = triple_overlap(completed, i)
            if overlap:
                c["overlap_triples"] += 1
                tot["overlap_triples"] += 1

            if alternating and overlap:
                c["z_seed_candidates"] += 1
                tot["z_seed_candidates"] += 1

                z_dir = a.direction
                parity_ok = True
                for j in range(i, len(completed), 2):
                    if completed[j].direction != z_dir:
                        parity_ok = False
                        break
                if parity_ok:
                    c["z_parity_preserved"] += 1
                    tot["z_parity_preserved"] += 1
                else:
                    c["z_parity_violations"] += 1
                    tot["z_parity_violations"] += 1
                    if len(examples["z_parity_violations"]) < 20:
                        examples["z_parity_violations"].append(
                            {"symbol": sym, "level": level, "seed_start": i}
                        )

print("CHAN_Z_MAPPING_SYMBOLS", symbols)
print("CHAN_Z_MAPPING_TOTAL", json.dumps(dict(tot), sort_keys=True))
print(
    "CHAN_Z_MAPPING_BY_LEVEL",
    json.dumps(
        {str(k): dict(v) for k, v in sorted(by_level.items())},
        sort_keys=True,
    ),
)
print("CHAN_Z_MAPPING_EXAMPLES", json.dumps(examples, sort_keys=True))

# These are representation invariants, not signal-count targets.
# A formal lower-level movement stream must alternate and chain end-to-start.
assert tot["completed_same_direction"] == 0, examples["completed_same_direction"]
assert tot["completed_chain_break"] == 0, examples["completed_chain_break"]
assert tot["z_parity_violations"] == 0, examples["z_parity_violations"]

print("CHAN_Z_MAPPING_STREAM_INVARIANTS_PASS")
print(
    "CHAN_Z_MAPPING_CURRENT_CENTER_AUDIT",
    json.dumps(
        {
            k: tot[k]
            for k in (
                "zs_zg_formula_mismatch",
                "zs_zd_formula_mismatch",
                "zs_absorbs_outside_z",
                "zs_completed_end_wrong_parity",
                "zs_ends_before_overlapping_next_z",
                "zs_next_z_boundary_touch",
                "left_edge_seed_overlap",
                "left_edge_seed_skipped",
            )
        },
        sort_keys=True,
    ),
)
