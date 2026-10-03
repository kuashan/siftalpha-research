#!/usr/bin/env python3
"""C0-A Chan structure reconstruction.

Scope:
- inclusion handling
- fractal
- Bi (two source-consistent variants kept separate)
- segment
- point-in-time first-observed confirmation ledger

No PnL, no SLTD integration, no strategy actions.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal

Direction = Literal["up", "down"]
FractalType = Literal["top", "bottom"]
BiMode = Literal["strict77", "late106"]


@dataclass(frozen=True)
class RawBar:
    high: float
    low: float
    open: float | None = None
    close: float | None = None
    index: int = 0


@dataclass
class MergedBar:
    high: float
    low: float
    raw_start: int
    raw_end: int


@dataclass(frozen=True)
class Fractal:
    kind: FractalType
    merged_index: int
    price: float
    anchor_raw_index: int
    confirm_raw_index: int


@dataclass(frozen=True)
class Point:
    price: float
    raw_index: int


@dataclass(frozen=True)
class Bi:
    direction: Direction
    start: Point
    end: Point
    high: float
    low: float
    index: int


@dataclass(frozen=True)
class Segment:
    direction: Direction
    start_bi: int
    end_bi: int
    start_price: float
    end_price: float
    count: int
    pending: bool


def _has_inclusion(a: MergedBar, b: MergedBar) -> bool:
    return (
        (a.high >= b.high and a.low <= b.low)
        or (b.high >= a.high and b.low <= a.low)
    )


def merge_inclusion(raw_bars: Iterable[RawBar]) -> list[MergedBar]:
    """Causal left-to-right inclusion handling from lessons 62/65."""
    out: list[MergedBar] = []
    for seq, raw in enumerate(raw_bars):
        idx = raw.index if raw.index is not None else seq
        cur = MergedBar(float(raw.high), float(raw.low), idx, idx)
        if not out:
            out.append(cur)
            continue

        last = out[-1]
        if not _has_inclusion(last, cur):
            out.append(cur)
            continue

        if len(out) >= 2:
            prev = out[-2]
            rising = last.high >= prev.high
        else:
            # Original text does not uniquely define sequence-start direction.
            # This is an explicit engineering choice and is covered by a fixture.
            rising = True

        if rising:
            new_high = max(last.high, cur.high)
            new_low = max(last.low, cur.low)
        else:
            new_high = min(last.high, cur.high)
            new_low = min(last.low, cur.low)

        out[-1] = MergedBar(
            high=new_high,
            low=new_low,
            raw_start=last.raw_start,
            raw_end=cur.raw_end,
        )
    return out


def find_fractals(merged: list[MergedBar]) -> list[Fractal]:
    """Three-unit top/bottom fractals after inclusion handling."""
    out: list[Fractal] = []
    for i in range(1, len(merged) - 1):
        left, mid, right = merged[i - 1], merged[i], merged[i + 1]
        top = (
            mid.high > left.high
            and mid.high > right.high
            and mid.low > left.low
            and mid.low > right.low
        )
        bottom = (
            mid.low < left.low
            and mid.low < right.low
            and mid.high < left.high
            and mid.high < right.high
        )
        if top:
            out.append(
                Fractal(
                    "top",
                    i,
                    mid.high,
                    mid.raw_end,
                    right.raw_end,
                )
            )
        elif bottom:
            out.append(
                Fractal(
                    "bottom",
                    i,
                    mid.low,
                    mid.raw_end,
                    right.raw_end,
                )
            )
    return out


def _can_link_bi(
    merged: list[MergedBar],
    left: Fractal,
    right: Fractal,
    min_gap: int,
) -> bool:
    if right.merged_index - left.merged_index < min_gap:
        return False
    top = left if left.kind == "top" else right
    bottom = right if left.kind == "top" else left
    return merged[top.merged_index].high > merged[bottom.merged_index].high


def select_bi_points(
    merged: list[MergedBar],
    fractals: list[Fractal],
    mode: BiMode,
) -> list[Fractal]:
    """Lesson-77 uniqueness procedure with two source variants kept explicit."""
    min_gap = 4 if mode == "strict77" else 3
    points: list[Fractal] = []

    for fx in fractals:
        if not points:
            points.append(fx)
            continue

        last = points[-1]
        if fx.kind == last.kind:
            more_extreme = (
                fx.price > last.price
                if fx.kind == "top"
                else fx.price < last.price
            )
            if more_extreme:
                points[-1] = fx
            continue

        if _can_link_bi(merged, last, fx, min_gap):
            points.append(fx)

    return points


def build_bis(points: list[Fractal]) -> list[Bi]:
    out: list[Bi] = []
    for i in range(1, len(points)):
        a, b = points[i - 1], points[i]
        p0 = Point(a.price, a.anchor_raw_index)
        p1 = Point(b.price, b.anchor_raw_index)
        out.append(
            Bi(
                direction="up" if a.kind == "bottom" else "down",
                start=p0,
                end=p1,
                high=max(a.price, b.price),
                low=min(a.price, b.price),
                index=len(out),
            )
        )
    return out


def _strict_feature_contains(a: list[float], b: tuple[float, float]) -> bool:
    return (
        (a[0] > b[0] and a[1] < b[1])
        or (b[0] > a[0] and b[1] < a[1])
    )


def _append_feature(
    seq: list[list[float]],
    feature: tuple[float, float],
    default_rising: bool,
) -> None:
    if not seq:
        seq.append([feature[0], feature[1]])
        return

    last = seq[-1]
    if not _strict_feature_contains(last, feature):
        seq.append([feature[0], feature[1]])
        return

    if len(seq) >= 2:
        prev = seq[-2]
        rising = last[0] >= prev[0]
    else:
        rising = default_rising

    if rising:
        last[0] = max(last[0], feature[0])
        last[1] = max(last[1], feature[1])
    else:
        last[0] = min(last[0], feature[0])
        last[1] = min(last[1], feature[1])


def _normalize_features(
    features: list[tuple[float, float]],
    default_rising: bool,
) -> list[list[float]]:
    out: list[list[float]] = []
    for item in features:
        _append_feature(out, item, default_rising)
    return out


def _is_new_segment_extreme(
    bis: list[Bi],
    start: int,
    idx: int,
    rising_segment: bool,
) -> bool:
    value = bis[idx].high if rising_segment else bis[idx].low
    for j in range(start, idx):
        if rising_segment and bis[j].high >= value:
            return False
        if (not rising_segment) and bis[j].low <= value:
            return False
    return True


def _feature_sequence_before(
    bis: list[Bi],
    start: int,
    end_exclusive: int,
    main_direction: Direction,
) -> list[list[float]]:
    raw = [
        (x.high, x.low)
        for x in bis[start:end_exclusive]
        if x.direction != main_direction
    ]
    return _normalize_features(raw, main_direction == "up")


def _find_segment_division(
    bis: list[Bi],
    start: int,
    min_end: int = -1,
) -> int | None:
    if start >= len(bis):
        return None

    main_direction = bis[start].direction
    rising_segment = main_direction == "up"
    candidate: dict | None = None

    for idx in range(start, len(bis)):
        bi = bis[idx]

        if candidate is not None:
            exceeded = (
                bi.high > candidate["extreme"]
                if rising_segment
                else bi.low < candidate["extreme"]
            )
            if exceeded:
                candidate = None

        if candidate is not None:
            if candidate["case"] is None:
                if bi.direction != main_direction and idx > candidate["at"]:
                    last_char = candidate["last_char"]
                    gap = (
                        bi.low > last_char[0]
                        if rising_segment
                        else bi.high < last_char[1]
                    )
                    candidate["case"] = 2 if gap else 1
                    candidate["confirm_seq"] = []
                    candidate["post_seq"] = (
                        [] if gap else [[bi.high, bi.low]]
                    )

            elif candidate["case"] == 1:
                if bi.direction != main_direction and idx > candidate["at"] + 1:
                    _append_feature(
                        candidate["post_seq"],
                        (bi.high, bi.low),
                        rising_segment,
                    )
                    seq = candidate["post_seq"]
                    if len(seq) >= 2:
                        turned = (
                            seq[-1][0] < seq[0][0]
                            if rising_segment
                            else seq[-1][1] > seq[0][1]
                        )
                        if turned:
                            return int(candidate["at"])

            else:
                if bi.direction == main_direction and idx > candidate["at"] + 1:
                    _append_feature(
                        candidate["confirm_seq"],
                        (bi.high, bi.low),
                        not rising_segment,
                    )
                    seq = candidate["confirm_seq"]
                    if len(seq) >= 3:
                        a, b, c = seq[-3], seq[-2], seq[-1]
                        confirmed = (
                            b[1] < a[1] and b[1] < c[1]
                            if rising_segment
                            else b[0] > a[0] and b[0] > c[0]
                        )
                        if confirmed:
                            return int(candidate["at"])

        if (
            candidate is None
            and bi.direction == main_direction
            and idx >= start + 2
            and idx > min_end
            and _is_new_segment_extreme(
                bis,
                start,
                idx,
                rising_segment,
            )
        ):
            before = _feature_sequence_before(
                bis,
                start,
                idx,
                main_direction,
            )
            if before:
                candidate = {
                    "at": idx,
                    "extreme": bi.high if rising_segment else bi.low,
                    "last_char": before[-1],
                    "case": None,
                }

    return None


def _segment_start_was_broken(bis: list[Bi], start: int) -> bool:
    first = bis[start]
    origin = first.start.price
    rising = first.direction == "up"
    for bi in bis[start + 1 :]:
        if rising and bi.low < origin:
            return True
        if (not rising) and bi.high > origin:
            return True
    return False


def _choose_initial_segment_start(bis: list[Bi]) -> int:
    if len(bis) < 2:
        return 0
    a = _find_segment_division(bis, 0)
    b = _find_segment_division(bis, 1)
    if a is None:
        return 1 if b is not None else 0
    if b is not None and b < a:
        return 1
    return 0


def _make_segment(
    bis: list[Bi],
    start: int,
    end: int,
    pending: bool,
) -> Segment:
    return Segment(
        direction=bis[start].direction,
        start_bi=start,
        end_bi=end,
        start_price=bis[start].start.price,
        end_price=bis[end].end.price,
        count=end - start + 1,
        pending=pending,
    )


def build_segments(bis: list[Bi]) -> list[Segment]:
    """Feature-sequence segmentation using lessons 67/71/78/81."""
    if not bis:
        return []

    completed: list[Segment] = []
    start = _choose_initial_segment_start(bis)
    recoveries = 0

    while start < len(bis):
        end = _find_segment_division(bis, start)

        if end is None:
            if (
                completed
                and _segment_start_was_broken(bis, start)
                and recoveries < len(bis)
            ):
                recoveries += 1
                previous = completed.pop()
                later = _find_segment_division(
                    bis,
                    previous.start_bi,
                    previous.end_bi,
                )
                if later is not None:
                    completed.append(
                        _make_segment(
                            bis,
                            previous.start_bi,
                            later,
                            False,
                        )
                    )
                    start = later + 1
                    continue
                start = previous.start_bi
                continue
            break

        completed.append(_make_segment(bis, start, end, False))
        start = end + 1

    if start < len(bis):
        completed.append(
            _make_segment(
                bis,
                start,
                len(bis) - 1,
                True,
            )
        )
    return completed


def strokes_from_path(path: list[float]) -> list[Bi]:
    """Synthetic fixture helper; not used for market data."""
    out: list[Bi] = []
    for i in range(1, len(path)):
        a, b = float(path[i - 1]), float(path[i])
        p0, p1 = Point(a, (i - 1) * 5), Point(b, i * 5)
        out.append(
            Bi(
                direction="up" if b > a else "down",
                start=p0,
                end=p1,
                high=max(a, b),
                low=min(a, b),
                index=i - 1,
            )
        )
    return out


def first_observed_segment_ledger(
    raw_bars: list[RawBar],
    mode: BiMode = "strict77",
) -> list[dict]:
    """Record first-observed confirmed segments by replaying finite prefixes."""
    seen: set[tuple] = set()
    ledger: list[dict] = []

    for end in range(len(raw_bars)):
        prefix = [
            RawBar(x.high, x.low, x.open, x.close, i)
            for i, x in enumerate(raw_bars[: end + 1])
        ]
        merged = merge_inclusion(prefix)
        fxs = find_fractals(merged)
        pts = select_bi_points(merged, fxs, mode)
        bis = build_bis(pts)
        segs = build_segments(bis)

        for seg in segs:
            if seg.pending:
                continue
            key = (
                seg.direction,
                seg.start_price,
                seg.end_price,
                seg.start_bi,
                seg.end_bi,
            )
            if key in seen:
                continue
            seen.add(key)
            ledger.append(
                {
                    "direction": seg.direction,
                    "anchor_price": seg.end_price,
                    "confirm_raw_index": end,
                    "start_bi": seg.start_bi,
                    "end_bi": seg.end_bi,
                }
            )

    return ledger
