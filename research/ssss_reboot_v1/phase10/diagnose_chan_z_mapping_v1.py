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
