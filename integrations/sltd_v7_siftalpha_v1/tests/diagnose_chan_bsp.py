from __future__ import annotations

import csv
import gzip
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
PROJECT = REPO / "integrations" / "sltd_v7_siftalpha_v1"
sys.path.insert(0, str(PROJECT))

import chan_strategy as cs  # noqa: E402

DATA_ROOT = REPO / "research" / "ssss_reboot_v1" / "phase7" / "data_snapshot"


def load(path: Path) -> list[dict]:
    out = []
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            out.append({
                "date": r["Date"][:10],
                "open": float(r["Open"]),
                "high": float(r["High"]),
                "low": float(r["Low"]),
                "close": float(r["Close"]),
                "volume": float(r.get("Volume") or 0.0),
            })
    return out


def gate_counts(bars: list[cs.RawBar], info: dict) -> Counter:
    units = info["units"]
    zss = info["zss"]
    links = info["links"]
    macd = cs.compute_macd([x.close for x in bars])
    dif, hist = macd["dif"], macd["hist"]
    c = Counter()

    for zi, zs in enumerate(zss):
        c["zs_total"] += 1
        if zs.pending:
            c["zs_pending"] += 1
            continue
        c["zs_complete"] += 1

        enter = units[zs.start_sub - 1] if zs.start_sub > 0 else None
        leave = units[zs.end_sub + 1] if zs.end_sub + 1 < len(units) else None
        if enter is None or leave is None or leave.pending:
            c["missing_enter_leave"] += 1
            continue
        c["has_enter_leave"] += 1

        if enter.direction != leave.direction:
            c["direction_mismatch"] += 1
            continue
        c["same_direction"] += 1

        down = enter.direction == "down"
        sign = -1 if down else 1
        expected = "down" if down else "up"

        if zi < len(links) and links[zi] == expected:
            c["link_match"] += 1
        else:
            c["link_fail"] += 1

        new_extreme = (
            leave.low < min(enter.low, zs.dd)
            if down else
            leave.high > max(enter.high, zs.gg)
        )
        if new_extreme:
            c["new_extreme"] += 1
        else:
            c["new_extreme_fail"] += 1

        enter_dif = cs._dif_extreme(enter, dif, sign)
        pulled = False
        for i in range(max(0, zs.start_index), min(len(bars) - 1, zs.end_index) + 1):
            if down:
                if dif[i] >= 0.25 * enter_dif:
                    pulled = True
                    break
            else:
                if dif[i] <= 0.25 * enter_dif:
                    pulled = True
                    break
        if pulled:
            c["pull_pass"] += 1
        else:
            c["pull_fail"] += 1

        weaker = (
            cs._movement_force(leave, hist, sign) < cs._movement_force(enter, hist, sign)
            or abs(cs._dif_extreme(leave, dif, sign)) < abs(enter_dif)
        )
        if weaker:
            c["weaker_pass"] += 1
        else:
            c["weaker_fail"] += 1

        if (
            zi < len(links)
            and links[zi] == expected
            and new_extreme
            and pulled
            and weaker
        ):
            c["b1s1_current_gate_pass"] += 1
            c["B1_gate"] += int(down)
            c["S1_gate"] += int(not down)

    return c




def exact_b1s1_funnel(bars: list[cs.RawBar], info: dict) -> Counter:
    """Sequential B1/S1 funnel using the exact current production predicates."""
    units = info["units"]
    zss = info["zss"]
    links = info["links"]
    macd = cs.compute_macd([x.close for x in bars])
    dif, hist = macd["dif"], macd["hist"]
    c = Counter()

    for zi, zs in enumerate(zss):
        c["zs_total"] += 1
        if zs.pending:
            c["zs_pending"] += 1
            continue
        c["01_zs_complete"] += 1

        enter = units[zs.start_sub - 1] if zs.start_sub > 0 else None
        leave = units[zs.end_sub + 1] if zs.end_sub + 1 < len(units) else None
        if enter is None or leave is None or leave.pending:
            continue
        c["02_has_enter_leave"] += 1

        if enter.direction != leave.direction:
            continue
        c["03_same_direction"] += 1

        down = enter.direction == "down"
        sign = -1 if down else 1
        if down:
            c["03_down_context"] += 1
        else:
            c["03_up_context"] += 1

        outside_center = leave.low < zs.zd if down else leave.high > zs.zg
        if not outside_center:
            continue
        c["04_outside_center"] += 1

        new_extreme = (
            leave.low < min(enter.low, zs.dd)
            if down else
            leave.high > max(enter.high, zs.gg)
        )
        if not new_extreme:
            continue
        c["05_new_extreme"] += 1

        enter_dif = cs._dif_extreme(enter, dif, sign)
        weaker = (
            cs._movement_force(leave, hist, sign)
            < cs._movement_force(enter, hist, sign)
            or abs(cs._dif_extreme(leave, dif, sign))
            < abs(enter_dif)
        )
        if not weaker:
            continue
        c["06_weaker_force"] += 1
        c["06_weaker_down"] += int(down)
        c["06_weaker_up"] += int(not down)

        expected = "down" if down else "up"
        actual = links[zi] if zi < len(links) else None
        c[f"06_link_actual_{actual or 'none'}"] += 1
        c[f"06_link_expected_{expected}"] += 1
        if actual != expected:
            c["07_link_mismatch"] += 1
            continue
        c["07_link_match"] += 1
        c["08_final_b1s1"] += 1
        c["08_B1"] += int(down)
        c["08_S1"] += int(not down)

    return c


def structure_funnel(snapshot: dict) -> Counter:
    c = Counter()
    c["bis_total"] = len(snapshot["bis"])
    c["segments_total"] = len(snapshot["segments"])
    c["segments_completed"] = sum(
        1
        for x in snapshot["segments"]
        if not x.pending and x.confirm_index is not None
    )

    for info in snapshot["levels"]:
        canonical = bool(info.get("canonical", False))
        prefix = "l1plus" if canonical else "l0"
        c[f"{prefix}_levels"] += 1
        c[f"{prefix}_units"] += len(info["units"])
        c[f"{prefix}_zs_total"] += len(info["zss"])
        c[f"{prefix}_zs_complete"] += sum(1 for z in info["zss"] if not z.pending)
        c[f"{prefix}_trends_total"] += len(info["trends"])
        c[f"{prefix}_trends_completed"] += sum(
            1
            for t in info["trends"]
            if not t.pending and t.confirm_index is not None
        )
        c[f"{prefix}_directional_trends"] += sum(
            1
            for t in info["trends"]
            if ("UP_TREND" in t.kind or "DOWN_TREND" in t.kind)
        )
        c[f"{prefix}_completed_directional_trends"] += sum(
            1
            for t in info["trends"]
            if (
                not t.pending
                and t.confirm_index is not None
                and ("UP_TREND" in t.kind or "DOWN_TREND" in t.kind)
            )
        )
    return c


def main() -> None:
    total = Counter()
    sig_counts = Counter()
    structure_total = Counter()
    l0_signal_counts = Counter()
    canonical_signal_counts = Counter()
    canonical_recent_300 = Counter()
    l0_b1s1_funnel = Counter()
    canonical_b1s1_funnel = Counter()
    symbols = 0
    symbols_with_1 = 0
    symbols_with_2 = 0
    symbols_with_l0_signal = 0
    symbols_with_canonical_signal = 0
    symbols_with_recent_canonical_signal = 0
    examples_1 = []
    examples_2 = []

    for path in sorted(DATA_ROOT.glob("batch_*_stocks/*.csv.gz")):
        candles = load(path)
        bars = cs._validate_candles(candles)
        bars, _ = cs._slice_analysis_window(bars)
        snap = cs.build_structure_snapshot(bars)
        symbols += 1
        structure_total.update(structure_funnel(snap))

        macd = cs.compute_macd([x.close for x in bars])
        symbol_l0 = Counter()
        symbol_canonical = Counter()
        symbol_recent = Counter()
        visible_start = max(0, len(bars) - 300)

        for info in snap["levels"]:
            level_signals = cs.compute_level_signals(bars, info, macd)
            level_counts = Counter(x["kind"] for x in level_signals)
            if bool(info.get("canonical", False)):
                symbol_canonical.update(level_counts)
                canonical_signal_counts.update(level_counts)
                canonical_b1s1_funnel.update(exact_b1s1_funnel(bars, info))
                for signal in level_signals:
                    if int(signal["anchor_index"]) >= visible_start:
                        symbol_recent[signal["kind"]] += 1
                        canonical_recent_300[signal["kind"]] += 1
            else:
                symbol_l0.update(level_counts)
                l0_signal_counts.update(level_counts)
                l0_b1s1_funnel.update(exact_b1s1_funnel(bars, info))

        symbols_with_l0_signal += int(bool(symbol_l0))
        symbols_with_canonical_signal += int(bool(symbol_canonical))
        symbols_with_recent_canonical_signal += int(bool(symbol_recent))

        symbol_counts = Counter(x["kind"] for x in snap["signals"])
        sig_counts.update(symbol_counts)
        if symbol_counts["B1"] or symbol_counts["S1"]:
            symbols_with_1 += 1
            examples_1.append((path.stem.replace(".csv", ""), dict(symbol_counts)))
        if symbol_counts["B2"] or symbol_counts["S2"]:
            symbols_with_2 += 1
            examples_2.append((path.stem.replace(".csv", ""), dict(symbol_counts)))

        for info in snap["levels"]:
            total.update(gate_counts(bars, info))

    print("CHAN_BSP_DIAGNOSTIC_SYMBOLS", symbols)
    print("CHAN_FINAL_SIGNAL_COUNTS", dict(sorted(sig_counts.items())))
    print("CHAN_STRUCTURE_FUNNEL", dict(sorted(structure_total.items())))
    print("CHAN_L0_RAW_SIGNAL_COUNTS", dict(sorted(l0_signal_counts.items())))
    print("CHAN_L1PLUS_RAW_SIGNAL_COUNTS", dict(sorted(canonical_signal_counts.items())))
    print("CHAN_L1PLUS_RECENT_300_STATIC_COUNTS", dict(sorted(canonical_recent_300.items())))
    print("CHAN_SYMBOLS_WITH_L0_SIGNAL", symbols_with_l0_signal)
    print("CHAN_SYMBOLS_WITH_L1PLUS_SIGNAL", symbols_with_canonical_signal)
    print("CHAN_SYMBOLS_WITH_L1PLUS_RECENT_300_SIGNAL", symbols_with_recent_canonical_signal)
    print("CHAN_L0_B1S1_EXACT_FUNNEL", dict(sorted(l0_b1s1_funnel.items())))
    print("CHAN_L1PLUS_B1S1_EXACT_FUNNEL", dict(sorted(canonical_b1s1_funnel.items())))
    print("CHAN_SYMBOLS_WITH_B1_S1", symbols_with_1)
    print("CHAN_SYMBOLS_WITH_B2_S2", symbols_with_2)
    print("CHAN_B1_S1_GATE_COUNTS_LEGACY", dict(sorted(total.items())))
    print("CHAN_B1_S1_EXAMPLES", examples_1[:20])
    print("CHAN_B2_S2_EXAMPLES", examples_2[:20])


if __name__ == "__main__":
    main()
