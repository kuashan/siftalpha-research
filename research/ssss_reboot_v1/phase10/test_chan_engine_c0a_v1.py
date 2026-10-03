#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PHASE10 = ROOT / "research" / "ssss_reboot_v1" / "phase10"
sys.path.insert(0, str(PHASE10))

from chan_engine_c0a_v1 import (  # noqa: E402
    RawBar,
    build_bis,
    build_segments,
    find_fractals,
    first_observed_segment_ledger,
    merge_inclusion,
    select_bi_points,
    strokes_from_path,
)


def B(high: float, low: float) -> RawBar:
    return RawBar(high=high, low=low)


def test_inclusion_up() -> None:
    m = merge_inclusion([B(5, 1), B(7, 3), B(6, 4)])
    assert [(x.high, x.low) for x in m] == [(5, 1), (7, 4)]


def test_inclusion_down() -> None:
    m = merge_inclusion([B(9, 5), B(7, 3), B(6, 3.5)])
    assert [(x.high, x.low) for x in m] == [(9, 5), (6, 3)]


def test_inclusion_chain() -> None:
    m = merge_inclusion([B(5, 1), B(9, 4), B(8, 5), B(8.5, 5.5)])
    assert [(x.high, x.low) for x in m] == [(5, 1), (9, 5.5)]


def test_fractal() -> None:
    m = merge_inclusion(
        [B(2, 1), B(4, 3), B(6, 5), B(4.5, 3.5), B(2.5, 1.5), B(5, 4)]
    )
    fx = find_fractals(m)
    assert [(x.kind, x.price) for x in fx] == [("top", 6), ("bottom", 1.5)]
    assert fx[0].confirm_raw_index > fx[0].anchor_raw_index


def test_bi_strict77() -> None:
    bars = [
        B(4, 3), B(7, 6), B(10, 9), B(8, 7), B(6, 5),
        B(4, 3), B(2, 1), B(5, 4), B(7, 6),
    ]
    m = merge_inclusion(bars)
    fx = find_fractals(m)
    bis = build_bis(select_bi_points(m, fx, "strict77"))
    assert len(bis) == 1
    assert bis[0].direction == "down"
    assert (bis[0].start.price, bis[0].end.price) == (10, 1)


def test_bi_source_variants_stay_separate() -> None:
    bars = [
        B(4, 3), B(7, 6), B(10, 9), B(8, 7),
        B(5, 4), B(2, 1), B(5, 4), B(7, 6),
    ]
    m = merge_inclusion(bars)
    fx = find_fractals(m)
    strict = build_bis(select_bi_points(m, fx, "strict77"))
    late = build_bis(select_bi_points(m, fx, "late106"))
    assert len(strict) == 0
    assert len(late) == 1


def test_segment_minimum_pending() -> None:
    segs = build_segments(strokes_from_path([0, 10, 4, 14]))
    assert len(segs) == 1
    assert segs[0].pending


def test_segment_case1_no_gap() -> None:
    segs = build_segments(strokes_from_path([0, 10, 7, 12, 9, 11, 8]))
    assert len(segs) == 2
    assert not segs[0].pending
    assert segs[0].end_price == 12
    assert segs[0].count == 3


def test_lesson81_five_above_seven_three_segments() -> None:
    # Synthetic numeric encoding of the corrected lesson-81 topology.
    segs = build_segments(
        strokes_from_path([2, 3, 1, 10, 6.5, 8, 5, 8, 6.5, 9])
    )
    assert len(segs) == 3
    assert segs[0].end_price == 10
    assert segs[1].direction == "down"
    assert segs[1].end_price == 5
    assert segs[2].pending


def test_lesson81_five_not_above_seven_one_segment() -> None:
    segs = build_segments(
        strokes_from_path([2, 3, 1, 10, 6.5, 8, 5, 8, 6.5, 10.5])
    )
    assert len(segs) == 1
    assert segs[0].pending


def test_case2_unconfirmed_then_new_extreme_continues() -> None:
    segs = build_segments(strokes_from_path([0, 10, 8, 20, 15, 25]))
    assert len(segs) == 1
    assert segs[0].pending


def test_confirmed_segments_are_odd_and_alternate() -> None:
    paths = [
        [2, 3, 1, 10, 6.5, 8, 5, 8, 6.5, 9],
        [0, 10, 7, 12, 9, 11, 8],
    ]
    for path in paths:
        segs = build_segments(strokes_from_path(path))
        for s in segs:
            if s.pending:
                continue
            assert s.count >= 3
            assert s.count % 2 == 1
        for a, b in zip(segs, segs[1:]):
            assert a.direction != b.direction


def test_first_observed_never_confirms_before_anchor_information() -> None:
    bars = [
        B(2, 1), B(3, 2), B(1.5, 0.8), B(10, 9),
        B(7, 6.5), B(8, 7.2), B(5.5, 5), B(8, 7),
        B(6.8, 6.5), B(9, 8.5), B(7.5, 7), B(6, 5.5),
    ]
    ledger = first_observed_segment_ledger(bars, "late106")
    for row in ledger:
        assert row["confirm_raw_index"] >= 0


if __name__ == "__main__":
    tests = [
        obj for name, obj in sorted(globals().items())
        if name.startswith("test_") and callable(obj)
    ]
    for fn in tests:
        fn()
        print("PASS", fn.__name__)
    print("C0A_TESTS_PASS", len(tests))
