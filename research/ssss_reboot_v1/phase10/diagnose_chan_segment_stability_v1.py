from __future__ import annotations

import csv
import gzip
import json
import sys
from collections import Counter
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


def seg_key(s: ch.StructUnit) -> tuple:
    return (
        s.direction,
        int(s.source_start),
        int(s.source_end),
        int(s.from_index),
        int(s.to_index),
        round(float(s.from_price), 10),
        round(float(s.to_price), 10),
        round(float(s.high), 10),
        round(float(s.low), 10),
    )


tot = Counter()
examples: list[dict] = []
symbols = 0

for path in sorted(DATA_ROOT.glob("batch_*_stocks/*.csv.gz")):
    symbols += 1
    sym = path.stem.split(".")[0]
    bars0 = ch._validate_candles(load(path))
    bars, _ = ch._slice_analysis_window(bars0)
    merged = ch.merge_inclusion(bars)
    points = ch.select_bi_points(merged, ch.find_fractals(merged))
    bis = ch.build_bis(points)

    prior_confirmed: list[tuple] = []
    prior_prefix = 0

    for end in range(3, len(bis) + 1):
        segs = ch.build_segments(bis[:end])
        confirmed = [seg_key(s) for s in segs if not s.pending]

        common = min(len(prior_confirmed), len(confirmed))
        changed_at = None
        for i in range(common):
            if prior_confirmed[i] != confirmed[i]:
                changed_at = i
                break

        if changed_at is not None or len(confirmed) < len(prior_confirmed):
            tot["confirmed_revision_events"] += 1
            if changed_at is None:
                changed_at = len(confirmed)
            if len(examples) < 40:
                examples.append(
                    {
                        "symbol": sym,
                        "previous_bi_prefix": prior_prefix,
                        "current_bi_prefix": end,
                        "changed_segment_ordinal": changed_at,
                        "previous": (
                            prior_confirmed[changed_at]
                            if changed_at < len(prior_confirmed)
                            else None
                        ),
                        "current": (
                            confirmed[changed_at]
                            if changed_at < len(confirmed)
                            else None
                        ),
                    }
                )

        # A longer prefix may append new confirmed segments, but it must not
        # alter any segment the engine had already labeled confirmed.
        if len(confirmed) >= len(prior_confirmed):
            if all(
                confirmed[i] == prior_confirmed[i]
                for i in range(len(prior_confirmed))
            ):
                prior_confirmed = confirmed
                prior_prefix = end

    final = ch.build_segments(bis)
    completed = [s for s in final if not s.pending]
    tot["final_completed_segments"] += len(completed)

    for i in range(1, len(completed)):
        a, b = completed[i - 1], completed[i]
        if a.direction == "up" and b.direction == "down":
            if abs(float(a.high) - float(b.high)) > 1e-9:
                tot["final_standardized_boundary_breaks"] += 1
        elif a.direction == "down" and b.direction == "up":
            if abs(float(a.low) - float(b.low)) > 1e-9:
                tot["final_standardized_boundary_breaks"] += 1

print("CHAN_SEGMENT_STABILITY_SYMBOLS", symbols)
print("CHAN_SEGMENT_STABILITY_TOTAL", json.dumps(dict(tot), sort_keys=True))
print("CHAN_SEGMENT_STABILITY_EXAMPLES", json.dumps(examples, sort_keys=True))

# No assertion yet: this file is a falsification diagnostic.  If revisions
# exist, the implementation must first distinguish provisional from truly
# confirmed segments before we can turn this into a gate.
print("CHAN_SEGMENT_STABILITY_DIAGNOSTIC_COMPLETE")
