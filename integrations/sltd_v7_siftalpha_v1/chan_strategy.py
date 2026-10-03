from __future__ import annotations

"""Independent Chan-theory strategy / structure engine.

This module does not consume SLTD V7, E, 5s Stocks, XMA rails, SLTD states,
or any other strategy output.  It only consumes completed OHLCV bars.

Pipeline:
raw K -> inclusion handling -> fractal -> Bi -> feature-sequence segment
-> multi-level Zhongshu / trend type -> divergence -> B1/B2/B3/S1/S2/S3.

Two display / execution times are intentionally separated:
- anchor_index: where the structural turning point belongs on the chart;
- confirm_index: the first completed bar on which the signal was observable.

The visible historical B/S ledger is produced by prefix replay, so a signal is
never backdated to its anchor for trading purposes.
"""

from dataclasses import dataclass
from math import isfinite
from typing import Iterable, Literal

CHAN_STRATEGY_ID = "chan"
CHAN_STRATEGY_VERSION = "独立缠论 v2"
CHAN_SOURCE = "CHAN_STANDALONE_RECONSTRUCTION_V2"
CHAN_MIN_BARS = 120
CHAN_ANALYSIS_MAX_BARS = 1600
CHAN_CAUSAL_REPLAY_BARS = 480
CHAN_MAX_RECURSIVE_LEVELS = 4

Direction = Literal["up", "down"]
FractalType = Literal["top", "bottom"]


CHAN_RULES = {
    "BUY": ("CHAN_B1", "CHAN_B2", "CHAN_B3"),
    "HOLD": (),
    "WAIT": (),
    "SELL": ("CHAN_S1", "CHAN_S2", "CHAN_S3"),
}

CHAN_RULE_NAMES_ZH = {
    "CHAN_B1": "一买 · 下跌趋势背驰后的第一类买点",
    "CHAN_B2": "二买 · 一买后第一次回试不创新低",
    "CHAN_B3": "三买 · 向上离开中枢后首次回试不跌回中枢",
    "CHAN_S1": "一卖 · 上涨趋势背驰后的第一类卖点",
    "CHAN_S2": "二卖 · 一卖后第一次反抽不创新高",
    "CHAN_S3": "三卖 · 向下离开中枢后首次回抽不升回中枢",
}

ACTION_NAMES_ZH = {
    "BUY": "买点",
    "SELL": "卖点",
    "NONE": "无新买卖点",
}


@dataclass(frozen=True)
class RawBar:
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    index: int


@dataclass
class MergedBar:
    high: float
    low: float
    raw_start: int
    raw_end: int
    high_index: int
    low_index: int


@dataclass(frozen=True)
class Fractal:
    kind: FractalType
    merged_index: int
    price: float
    anchor_index: int
    confirm_index: int


@dataclass(frozen=True)
class StructUnit:
    direction: Direction
    from_index: int
    from_price: float
    to_index: int
    to_price: float
    high: float
    low: float
    start_index: int
    end_index: int
    confirm_index: int | None
    pending: bool
    count: int
    kind: str
    source_start: int
    source_end: int


@dataclass(frozen=True)
class Zhongshu:
    level: int
    unit_kind: str
    start_sub: int
    end_sub: int
    zg: float
    zd: float
    gg: float
    dd: float
    start_index: int
    end_index: int
    confirm_index: int
    count: int
    pending: bool
    upgraded: bool


def _validate_candles(candles: Iterable[dict]) -> list[RawBar]:
    out: list[RawBar] = []
    last_date = ""
    for i, raw in enumerate(candles):
        date = str(raw.get("date") or "")
        if not date:
            raise ValueError("K 线日期不能为空")
        if last_date and date <= last_date:
            raise ValueError("K 线必须按时间严格递增排列")
        o = float(raw["open"])
        h = float(raw["high"])
        l = float(raw["low"])
        c = float(raw["close"])
        if not all(isfinite(v) for v in (o, h, l, c)):
            raise ValueError(f"{date}: K 线价格不是有限数")
        if h < l:
            raise ValueError(f"{date}: 最高价小于最低价")
        out.append(
            RawBar(
                date=date,
                open=o,
                high=h,
                low=l,
                close=c,
                volume=float(raw.get("volume") or 0.0),
                index=i,
            )
        )
        last_date = date
    if len(out) < CHAN_MIN_BARS:
        raise ValueError(f"缠论至少需要 {CHAN_MIN_BARS} 根已结束 K 线")
    return out


def _slice_analysis_window(bars: list[RawBar]) -> tuple[list[RawBar], int]:
    offset = max(0, len(bars) - CHAN_ANALYSIS_MAX_BARS)
    sliced = bars[offset:]
    rebased = [
        RawBar(
            date=x.date,
            open=x.open,
            high=x.high,
            low=x.low,
            close=x.close,
            volume=x.volume,
            index=i,
        )
        for i, x in enumerate(sliced)
    ]
    return rebased, offset


def _has_inclusion(a: MergedBar, b: MergedBar) -> bool:
    return (
        (a.high >= b.high and a.low <= b.low)
        or (b.high >= a.high and b.low <= a.low)
    )


def merge_inclusion(bars: list[RawBar]) -> list[MergedBar]:
    """Direction-aware left-to-right inclusion handling."""
    out: list[MergedBar] = []
    for raw in bars:
        cur = MergedBar(
            high=raw.high,
            low=raw.low,
            raw_start=raw.index,
            raw_end=raw.index,
            high_index=raw.index,
            low_index=raw.index,
        )
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
            # Source beginning has no prior direction.  Keep this engineering
            # choice explicit and deterministic.
            rising = True

        if rising:
            high, high_index = (
                (cur.high, cur.high_index)
                if cur.high > last.high
                else (last.high, last.high_index)
            )
            low, low_index = (
                (cur.low, cur.low_index)
                if cur.low > last.low
                else (last.low, last.low_index)
            )
        else:
            high, high_index = (
                (cur.high, cur.high_index)
                if cur.high < last.high
                else (last.high, last.high_index)
            )
            low, low_index = (
                (cur.low, cur.low_index)
                if cur.low < last.low
                else (last.low, last.low_index)
            )

        out[-1] = MergedBar(
            high=high,
            low=low,
            raw_start=last.raw_start,
            raw_end=cur.raw_end,
            high_index=high_index,
            low_index=low_index,
        )
    return out


def find_fractals(merged: list[MergedBar]) -> list[Fractal]:
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
                    mid.high_index,
                    right.raw_end,
                )
            )
        elif bottom:
            out.append(
                Fractal(
                    "bottom",
                    i,
                    mid.low,
                    mid.low_index,
                    right.raw_end,
                )
            )
    return out


def _can_link_bi(
    merged: list[MergedBar],
    left: Fractal,
    right: Fractal,
) -> bool:
    # Strict lesson-77 research convention: at least one merged K is not part
    # of either endpoint fractal, so center-index distance must be >= 4.
    if right.merged_index - left.merged_index < 4:
        return False
    top = left if left.kind == "top" else right
    bottom = right if left.kind == "top" else left
    return merged[top.merged_index].high > merged[bottom.merged_index].high


def select_bi_points(
    merged: list[MergedBar],
    fractals: list[Fractal],
) -> list[Fractal]:
    points: list[Fractal] = []
    for fx in fractals:
        if not points:
            points.append(fx)
            continue

        last = points[-1]
        if fx.kind == last.kind:
            stronger = (
                fx.price > last.price
                if fx.kind == "top"
                else fx.price < last.price
            )
            if stronger:
                points[-1] = fx
            continue

        if _can_link_bi(merged, last, fx):
            points.append(fx)
    return points


def build_bis(points: list[Fractal]) -> list[StructUnit]:
    out: list[StructUnit] = []
    for i in range(1, len(points)):
        a, b = points[i - 1], points[i]
        out.append(
            StructUnit(
                direction="up" if a.kind == "bottom" else "down",
                from_index=a.anchor_index,
                from_price=a.price,
                to_index=b.anchor_index,
                to_price=b.price,
                high=max(a.price, b.price),
                low=min(a.price, b.price),
                start_index=a.anchor_index,
                end_index=b.anchor_index,
                confirm_index=b.confirm_index,
                pending=False,
                count=1,
                kind="BI",
                source_start=i - 1,
                source_end=i,
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


def _feature_sequence_before(
    bis: list[StructUnit],
    start: int,
    end_exclusive: int,
    main_direction: Direction,
) -> list[list[float]]:
    out: list[list[float]] = []
    for bi in bis[start:end_exclusive]:
        if bi.direction != main_direction:
            _append_feature(
                out,
                (bi.high, bi.low),
                main_direction == "up",
            )
    return out


def _is_new_segment_extreme(
    bis: list[StructUnit],
    start: int,
    idx: int,
    rising: bool,
) -> bool:
    value = bis[idx].high if rising else bis[idx].low
    for j in range(start, idx):
        if rising and bis[j].high >= value:
            return False
        if (not rising) and bis[j].low <= value:
            return False
    return True


def _find_segment_division(
    bis: list[StructUnit],
    start: int,
    min_end: int = -1,
) -> tuple[int, int] | None:
    """Return (segment-anchor Bi index, confirming Bi index)."""
    if start >= len(bis):
        return None

    direction = bis[start].direction
    rising = direction == "up"
    candidate: dict | None = None

    for idx in range(start, len(bis)):
        bi = bis[idx]

        if candidate is not None:
            exceeded = (
                bi.high > candidate["extreme"]
                if rising
                else bi.low < candidate["extreme"]
            )
            if exceeded:
                candidate = None

        if candidate is not None:
            if candidate["case"] is None:
                if bi.direction != direction and idx > candidate["at"]:
                    edge = candidate["edge"]
                    has_gap = (
                        bi.low > edge[0]
                        if rising
                        else bi.high < edge[1]
                    )
                    candidate["case"] = 2 if has_gap else 1
                    candidate["after"] = []
                    candidate["confirm"] = []
                    if not has_gap:
                        candidate["after"].append([bi.high, bi.low])

            elif candidate["case"] == 1:
                if bi.direction != direction and idx > candidate["at"] + 1:
                    _append_feature(
                        candidate["after"],
                        (bi.high, bi.low),
                        rising,
                    )
                    seq = candidate["after"]
                    if len(seq) >= 2:
                        turned = (
                            seq[-1][0] < seq[0][0]
                            if rising
                            else seq[-1][1] > seq[0][1]
                        )
                        if turned:
                            return int(candidate["at"]), idx

            else:
                if bi.direction == direction and idx > candidate["at"] + 1:
                    _append_feature(
                        candidate["confirm"],
                        (bi.high, bi.low),
                        not rising,
                    )
                    seq = candidate["confirm"]
                    if len(seq) >= 3:
                        a, b, c = seq[-3], seq[-2], seq[-1]
                        ok = (
                            b[1] < a[1] and b[1] < c[1]
                            if rising
                            else b[0] > a[0] and b[0] > c[0]
                        )
                        if ok:
                            return int(candidate["at"]), idx

        if (
            candidate is None
            and bi.direction == direction
            and idx >= start + 2
            and idx > min_end
            and _is_new_segment_extreme(bis, start, idx, rising)
        ):
            pre = _feature_sequence_before(bis, start, idx, direction)
            if pre:
                candidate = {
                    "at": idx,
                    "extreme": bi.high if rising else bi.low,
                    "edge": pre[-1],
                    "case": None,
                }

    return None


def _segment_start_broken(bis: list[StructUnit], start: int) -> bool:
    first = bis[start]
    origin = first.from_price
    rising = first.direction == "up"
    for bi in bis[start + 1 :]:
        if rising and bi.low < origin:
            return True
        if (not rising) and bi.high > origin:
            return True
    return False


def _choose_segment_start(bis: list[StructUnit]) -> int:
    if len(bis) < 2:
        return 0
    a = _find_segment_division(bis, 0)
    b = _find_segment_division(bis, 1)
    if a is None:
        return 1 if b is not None else 0
    if b is not None and b[0] < a[0]:
        return 1
    return 0


def _make_segment(
    bis: list[StructUnit],
    start: int,
    end: int,
    confirm_bi: int | None,
    pending: bool,
) -> StructUnit:
    chunk = bis[start : end + 1]
    return StructUnit(
        direction=bis[start].direction,
        from_index=bis[start].from_index,
        from_price=bis[start].from_price,
        to_index=bis[end].to_index,
        to_price=bis[end].to_price,
        high=max(x.high for x in chunk),
        low=min(x.low for x in chunk),
        start_index=bis[start].start_index,
        end_index=bis[end].end_index,
        confirm_index=(
            None
            if confirm_bi is None
            else bis[confirm_bi].confirm_index
        ),
        pending=pending,
        count=end - start + 1,
        kind="SEGMENT",
        source_start=start,
        source_end=end,
    )


def build_segments(bis: list[StructUnit]) -> list[StructUnit]:
    if not bis:
        return []

    out: list[StructUnit] = []
    start = _choose_segment_start(bis)
    recovery_guard = 0

    while start < len(bis):
        division = _find_segment_division(bis, start)
        if division is None:
            if (
                out
                and _segment_start_broken(bis, start)
                and recovery_guard < len(bis)
            ):
                recovery_guard += 1
                previous = out.pop()
                later = _find_segment_division(
                    bis,
                    previous.source_start,
                    previous.source_end,
                )
                if later is not None:
                    out.append(
                        _make_segment(
                            bis,
                            previous.source_start,
                            later[0],
                            later[1],
                            False,
                        )
                    )
                    start = later[0] + 1
                    continue
                start = previous.source_start
                continue
            break

        anchor, confirm_bi = division
        out.append(_make_segment(bis, start, anchor, confirm_bi, False))
        start = anchor + 1

    if start < len(bis):
        out.append(
            _make_segment(
                bis,
                start,
                len(bis) - 1,
                None,
                True,
            )
        )
    return out


def _completed_units(units: list[StructUnit]) -> list[StructUnit]:
    return [
        x
        for x in units
        if not x.pending and x.confirm_index is not None
    ]


def build_zhongshus(
    units: list[StructUnit],
    *,
    level: int,
    unit_kind: str,
) -> list[Zhongshu]:
    """Build Zhongshu from consecutive completed lower-level units."""
    subs = _completed_units(units)
    out: list[Zhongshu] = []
    i = 1  # unit 0 acts as the entering movement

    while i + 2 < len(subs):
        seed = subs[i : i + 3]
        zg = min(x.high for x in seed)
        zd = max(x.low for x in seed)
        if not zg > zd:
            i += 2
            continue

        def touches(unit: StructUnit) -> bool:
            return unit.low <= zg and unit.high >= zd

        end = i + 2
        j = i + 3
        while j < len(subs):
            current_touch = touches(subs[j])
            next_touch = (
                touches(subs[j + 1])
                if j + 1 < len(subs)
                else None
            )

            # A unit that touches the Zhongshu but is immediately followed by
            # a one-way non-return is treated as the departure, not absorbed
            # into the Zhongshu.  This prevents a valid trend from being
            # swallowed into one giant center.
            if current_touch and next_touch is not False:
                end = j
                j += 1
                continue

            # A single excursion outside that is immediately pulled back is
            # still part of the Zhongshu extension.
            if (not current_touch) and next_touch is True:
                end = j + 1
                j += 2
                continue

            break

        chunk = subs[i : end + 1]
        pending = end + 1 >= len(subs)
        out.append(
            Zhongshu(
                level=level,
                unit_kind=unit_kind,
                start_sub=i,
                end_sub=end,
                zg=zg,
                zd=zd,
                gg=max(x.high for x in chunk),
                dd=min(x.low for x in chunk),
                start_index=chunk[0].start_index,
                end_index=chunk[-1].end_index,
                confirm_index=max(
                    int(x.confirm_index)
                    for x in seed
                    if x.confirm_index is not None
                ),
                count=end - i + 1,
                pending=pending,
                upgraded=(end - i + 1) >= 9,
            )
        )
        i = end + 2

    return out


def link_zhongshus(zss: list[Zhongshu]) -> list[str | None]:
    links: list[str | None] = [None] if zss else []
    for i in range(1, len(zss)):
        prev, cur = zss[i - 1], zss[i]
        if cur.dd > prev.gg:
            links.append("up")
        elif cur.gg < prev.dd:
            links.append("down")
        else:
            links.append("overlap")
    return links


def _group_zhongshus(
    zss: list[Zhongshu],
) -> list[dict]:
    groups: list[dict] = []
    current: dict | None = None
    for idx, zs in enumerate(zss):
        if current is None:
            current = {"a": idx, "b": idx, "direction": None}
            continue

        prev = zss[current["b"]]
        if zs.dd > prev.gg:
            rel = "up"
        elif zs.gg < prev.dd:
            rel = "down"
        else:
            rel = "overlap"

        if (
            rel != "overlap"
            and (
                current["direction"] is None
                or current["direction"] == rel
            )
        ):
            current["direction"] = rel
            current["b"] = idx
        else:
            groups.append(current)
            current = {"a": idx, "b": idx, "direction": None}

    if current is not None:
        groups.append(current)
    return groups


def build_trend_types(
    units: list[StructUnit],
    zss: list[Zhongshu],
    *,
    level: int,
) -> list[StructUnit]:
    """Deterministically partition units into consolidation / trend types."""
    if not units or not zss:
        return []

    groups = _group_zhongshus(zss)
    trends: list[StructUnit] = []

    for gi, group in enumerate(groups):
        start_u = 0 if gi == 0 else trends[-1].source_end + 1

        if gi < len(groups) - 1:
            next_zs = zss[groups[gi + 1]["a"]]
            end_u = max(start_u, next_zs.start_sub - 2)
        else:
            end_u = len(units) - 1

        end_u = min(end_u, len(units) - 1)
        if end_u < start_u:
            continue

        chunk = units[start_u : end_u + 1]
        zcount = int(group["b"] - group["a"] + 1)
        trend_direction = group["direction"]
        if trend_direction is None:
            trend_direction = (
                "up"
                if chunk[-1].to_price >= chunk[0].from_price
                else "down"
            )

        structural_kind = (
            "UP_TREND"
            if zcount >= 2 and trend_direction == "up"
            else "DOWN_TREND"
            if zcount >= 2 and trend_direction == "down"
            else "CONSOLIDATION"
        )
        pending = gi == len(groups) - 1
        confirm_index = (
            None
            if pending
            else max(
                x.confirm_index or x.end_index
                for x in chunk
            )
        )

        trends.append(
            StructUnit(
                direction=trend_direction,
                from_index=chunk[0].from_index,
                from_price=chunk[0].from_price,
                to_index=chunk[-1].to_index,
                to_price=chunk[-1].to_price,
                high=max(x.high for x in chunk),
                low=min(x.low for x in chunk),
                start_index=chunk[0].start_index,
                end_index=chunk[-1].end_index,
                confirm_index=confirm_index,
                pending=pending,
                count=end_u - start_u + 1,
                kind=f"L{level}_{structural_kind}",
                source_start=start_u,
                source_end=end_u,
            )
        )
    return trends


def build_levels(
    bis: list[StructUnit],
    segments: list[StructUnit],
) -> list[dict]:
    """Build practical L0 plus canonical recursive levels.

    L0 uses Bi as the lower-level unit so the selected chart can expose local
    Chan structure.  L1 starts from confirmed feature-sequence segments and is
    the canonical segment-derived Zhongshu layer.  L2+ recurse through trend
    types.
    """
    levels: list[dict] = []

    if len(bis) >= 4:
        z0 = build_zhongshus(bis, level=0, unit_kind="BI")
        levels.append(
            {
                "level": 0,
                "label": "L0 笔级",
                "unit_kind": "BI",
                "units": bis,
                "zss": z0,
                "links": link_zhongshus(z0),
                "trends": build_trend_types(bis, z0, level=0),
                "canonical": False,
            }
        )

    units = segments
    for lv in range(1, CHAN_MAX_RECURSIVE_LEVELS + 1):
        if len(units) < 4:
            break

        zss = build_zhongshus(
            units,
            level=lv,
            unit_kind=units[0].kind if units else "UNKNOWN",
        )
        if not zss:
            break

        trends = build_trend_types(units, zss, level=lv)
        levels.append(
            {
                "level": lv,
                "label": f"L{lv} 线段级" if lv == 1 else f"L{lv} 递归级",
                "unit_kind": units[0].kind if units else "UNKNOWN",
                "units": units,
                "zss": zss,
                "links": link_zhongshus(zss),
                "trends": trends,
                "canonical": True,
            }
        )

        completed_trends = _completed_units(trends)
        if (
            len(completed_trends) < 4
            or len(completed_trends) >= len(units)
        ):
            break
        units = completed_trends

    return levels


def _ema(values: list[float], period: int) -> list[float]:
    alpha = 2.0 / (period + 1.0)
    out: list[float] = []
    prev = values[0]
    for i, value in enumerate(values):
        prev = value if i == 0 else alpha * value + (1.0 - alpha) * prev
        out.append(prev)
    return out


def compute_macd(closes: list[float]) -> dict[str, list[float]]:
    fast = _ema(closes, 12)
    slow = _ema(closes, 26)
    dif = [a - b for a, b in zip(fast, slow)]
    dea = _ema(dif, 9)
    hist = [2.0 * (a - b) for a, b in zip(dif, dea)]
    return {"dif": dif, "dea": dea, "hist": hist}


def _movement_force(
    unit: StructUnit,
    hist: list[float],
    sign: int,
) -> float:
    total = 0.0
    a = max(0, unit.start_index)
    b = min(len(hist) - 1, unit.end_index)
    for i in range(a, b + 1):
        value = hist[i]
        if (sign > 0 and value > 0) or (sign < 0 and value < 0):
            total += abs(value)
    return total


def _dif_extreme(
    unit: StructUnit,
    dif: list[float],
    sign: int,
) -> float:
    a = max(0, unit.start_index)
    b = min(len(dif) - 1, unit.end_index)
    values = dif[a : b + 1]
    if not values:
        return 0.0
    return max(values) if sign > 0 else min(values)


def compute_level_signals(
    bars: list[RawBar],
    level_info: dict,
    macd: dict[str, list[float]],
) -> list[dict]:
    units: list[StructUnit] = level_info["units"]
    zss: list[Zhongshu] = level_info["zss"]
    links: list[str | None] = level_info["links"]
    dif = macd["dif"]
    hist = macd["hist"]
    level = int(level_info["level"])
    label = str(level_info["label"])
    out: list[dict] = []

    def emit(
        kind: str,
        unit: StructUnit,
        zs: Zhongshu,
        note: str,
    ) -> None:
        out.append(
            {
                "kind": kind,
                "rule_id": f"CHAN_{kind}",
                "level": level,
                "level_label": label,
                "anchor_index": unit.to_index,
                "source_confirm_index": (
                    unit.confirm_index
                    if unit.confirm_index is not None
                    else unit.end_index
                ),
                "price": unit.to_price,
                "zs_start_index": zs.start_index,
                "zs_end_index": zs.end_index,
                "ZG": zs.zg,
                "ZD": zs.zd,
                "note": note,
            }
        )

    for zi, zs in enumerate(zss):
        if zs.pending:
            continue

        enter = (
            units[zs.start_sub - 1]
            if zs.start_sub > 0
            else None
        )
        leave = (
            units[zs.end_sub + 1]
            if zs.end_sub + 1 < len(units)
            else None
        )

        # B1 / S1: trend context + new extreme + weaker same-direction move.
        if (
            enter is not None
            and leave is not None
            and not leave.pending
            and enter.direction == leave.direction
        ):
            down = enter.direction == "down"
            sign = -1 if down else 1
            new_extreme = (
                leave.low < min(enter.low, zs.dd)
                if down
                else leave.high > max(enter.high, zs.gg)
            )

            enter_dif = _dif_extreme(enter, dif, sign)
            pulled_near_zero = False
            center_start = max(0, zs.start_index)
            center_end = min(len(bars) - 1, zs.end_index)
            for i in range(center_start, center_end + 1):
                if down:
                    if dif[i] >= 0.25 * enter_dif:
                        pulled_near_zero = True
                        break
                else:
                    if dif[i] <= 0.25 * enter_dif:
                        pulled_near_zero = True
                        break

            weaker = (
                _movement_force(leave, hist, sign)
                < _movement_force(enter, hist, sign)
                or abs(_dif_extreme(leave, dif, sign))
                < abs(enter_dif)
            )

            expected_link = "down" if down else "up"
            if (
                new_extreme
                and pulled_near_zero
                and weaker
                and zi < len(links)
                and links[zi] == expected_link
            ):
                first_kind = "B1" if down else "S1"
                emit(
                    first_kind,
                    leave,
                    zs,
                    "下跌趋势背驰" if down else "上涨趋势背驰",
                )

                # After the first-class point, the first rebound/retracement
                # pair is the second-class test.  It must not exceed the first
                # point's extreme.
                second_index = zs.end_sub + 3
                if second_index < len(units):
                    second = units[second_index]
                    if not second.pending:
                        valid = (
                            second.low > leave.low
                            if down
                            else second.high < leave.high
                        )
                        if valid:
                            emit(
                                "B2" if down else "S2",
                                second,
                                zs,
                                (
                                    "一买后第一次回试不创新低"
                                    if down
                                    else "一卖后第一次反抽不创新高"
                                ),
                            )

        # B3 / S3: the first completed return after leaving Zhongshu.
        #
        # Two structural forms are possible:
        # 1) the last unit absorbed into the Zhongshu already extends outside
        #    the boundary; the immediately following opposite unit is the
        #    first return;
        # 2) the next unit is the explicit departure and the following unit
        #    is the first return.
        first = units[zs.end_sub + 1] if zs.end_sub + 1 < len(units) else None
        second = units[zs.end_sub + 2] if zs.end_sub + 2 < len(units) else None
        last_inside = units[zs.end_sub]

        if first is not None and not first.pending:
            if (
                first.direction == "down"
                and last_inside.high > zs.zg
                and first.low >= zs.zg
            ):
                emit(
                    "B3",
                    first,
                    zs,
                    "中枢末段向上脱离后，首次回试不跌回 ZG",
                )
            elif (
                first.direction == "up"
                and last_inside.low < zs.zd
                and first.high <= zs.zd
            ):
                emit(
                    "S3",
                    first,
                    zs,
                    "中枢末段向下脱离后，首次回抽不升回 ZD",
                )
            elif (
                second is not None
                and not second.pending
                and first.direction == "up"
                and first.high > zs.zg
                and second.direction == "down"
                and second.low >= zs.zg
            ):
                emit(
                    "B3",
                    second,
                    zs,
                    "向上离开中枢后首次回试不跌回 ZG",
                )
            elif (
                second is not None
                and not second.pending
                and first.direction == "down"
                and first.low < zs.zd
                and second.direction == "up"
                and second.high <= zs.zd
            ):
                emit(
                    "S3",
                    second,
                    zs,
                    "向下离开中枢后首次回抽不升回 ZD",
                )

    # Deduplicate a structural point rediscovered through overlapping scans.
    unique: dict[tuple[int, str, int], dict] = {}
    for item in sorted(
        out,
        key=lambda x: (
            x["source_confirm_index"],
            x["anchor_index"],
            x["kind"],
        ),
    ):
        key = (
            int(item["level"]),
            str(item["kind"]),
            int(item["anchor_index"]),
        )
        unique.setdefault(key, item)
    return list(unique.values())


def build_structure_snapshot(bars: list[RawBar]) -> dict:
    merged = merge_inclusion(bars)
    fractals = find_fractals(merged)
    bi_points = select_bi_points(merged, fractals)
    bis = build_bis(bi_points)
    segments = build_segments(bis)
    levels = build_levels(bis, segments)
    macd = compute_macd([x.close for x in bars])

    signals: list[dict] = []
    for level in levels:
        signals.extend(
            compute_level_signals(
                bars,
                level,
                macd,
            )
        )
    signals.sort(
        key=lambda x: (
            x["source_confirm_index"],
            x["level"],
            x["anchor_index"],
            x["kind"],
        )
    )

    return {
        "merged": merged,
        "fractals": fractals,
        "bi_points": bi_points,
        "bis": bis,
        "segments": segments,
        "levels": levels,
        "signals": signals,
    }


def replay_first_observed_signals(
    bars: list[RawBar],
) -> list[dict]:
    """Recompute finite prefixes and persist each signal at first observation."""
    n = len(bars)
    start = max(CHAN_MIN_BARS - 1, n - CHAN_CAUSAL_REPLAY_BARS)
    seen: set[tuple[int, str, int]] = set()
    ledger: list[dict] = []

    # Seed existing structures one bar before the replay horizon.  We do not
    # emit them because their first-observed time predates the causal window.
    if start > 0:
        seed = build_structure_snapshot(bars[:start])
        for s in seed["signals"]:
            seen.add(
                (
                    int(s["level"]),
                    str(s["kind"]),
                    int(s["anchor_index"]),
                )
            )

    for end in range(start, n):
        snap = build_structure_snapshot(bars[: end + 1])
        for signal in snap["signals"]:
            key = (
                int(signal["level"]),
                str(signal["kind"]),
                int(signal["anchor_index"]),
            )
            if key in seen:
                continue
            seen.add(key)
            row = dict(signal)
            row["confirm_index"] = end
            row["status"] = "CONFIRMED_FIRST_OBSERVED"
            ledger.append(row)

    return ledger


def _date(bars: list[RawBar], index: int) -> str:
    index = max(0, min(len(bars) - 1, int(index)))
    return bars[index].date


def _clip_index(index: int, start: int, end: int) -> int:
    return max(start, min(end, int(index)))


def _current_structure_text(snapshot: dict) -> str:
    levels = snapshot["levels"]
    if levels:
        highest = levels[-1]
        trends = highest["trends"]
        if trends:
            current = trends[-1]
            if "UP_TREND" in current.kind:
                return f"{highest['label']} · 上涨走势"
            if "DOWN_TREND" in current.kind:
                return f"{highest['label']} · 下跌走势"
            return f"{highest['label']} · 盘整走势"

        zss = highest["zss"]
        if zss:
            return f"{highest['label']} · 中枢震荡"

    segments = snapshot["segments"]
    if segments:
        last = segments[-1]
        return (
            "向上线段 · 未完成"
            if last.direction == "up" and last.pending
            else "向下线段 · 未完成"
            if last.direction == "down" and last.pending
            else "向上线段 · 已确认"
            if last.direction == "up"
            else "向下线段 · 已确认"
        )
    return "结构形成中"


def analyze_chan(
    symbol: str,
    candles: Iterable[dict],
    *,
    display_limit: int = 300,
    timeframe: str = "1d",
) -> dict:
    all_bars = _validate_candles(candles)
    bars, source_offset = _slice_analysis_window(all_bars)

    final = build_structure_snapshot(bars)
    signal_ledger = replay_first_observed_signals(bars)

    limit = max(80, min(int(display_limit), 500))
    visible_start = max(0, len(bars) - limit)
    visible_end = len(bars) - 1
    visible_dates = {x.date for x in bars[visible_start:]}

    chart = [
        {
            "date": b.date,
            "open": b.open,
            "high": b.high,
            "low": b.low,
            "close": b.close,
            "volume": b.volume,
            "state": "OTHER",
            "state_zh": "独立缠论",
            "position": 0.0,
            "risk_armed": False,
        }
        for b in bars[visible_start:]
    ]

    # Default top/bottom display uses valid Bi endpoints rather than every raw
    # fractal.  This removes the wall of duplicate top/bottom labels.
    endpoints = [
        {
            "type": p.kind,
            "anchor_date": _date(bars, p.anchor_index),
            "confirm_date": _date(bars, p.confirm_index),
            "price": p.price,
        }
        for p in final["bi_points"]
        if p.anchor_index >= visible_start
    ]

    bis_overlay = []
    for unit in final["bis"]:
        if unit.end_index < visible_start or unit.start_index > visible_end:
            continue
        bis_overlay.append(
            {
                "direction": unit.direction,
                "start_date": _date(
                    bars,
                    _clip_index(unit.start_index, visible_start, visible_end),
                ),
                "start_price": (
                    bars[visible_start].close
                    if unit.start_index < visible_start
                    else unit.from_price
                ),
                "actual_start_date": _date(bars, unit.start_index),
                "actual_start_price": unit.from_price,
                "end_date": _date(
                    bars,
                    _clip_index(unit.end_index, visible_start, visible_end),
                ),
                "end_price": (
                    bars[visible_end].close
                    if unit.end_index > visible_end
                    else unit.to_price
                ),
                "actual_end_date": _date(bars, unit.end_index),
                "actual_end_price": unit.to_price,
                "confirm_date": (
                    _date(bars, unit.confirm_index)
                    if unit.confirm_index is not None
                    else None
                ),
            }
        )

    segments_overlay = []
    for unit in final["segments"]:
        if unit.end_index < visible_start or unit.start_index > visible_end:
            continue
        segments_overlay.append(
            {
                "direction": unit.direction,
                "start_date": _date(
                    bars,
                    _clip_index(unit.start_index, visible_start, visible_end),
                ),
                "start_price": (
                    bars[visible_start].close
                    if unit.start_index < visible_start
                    else unit.from_price
                ),
                "actual_start_date": _date(bars, unit.start_index),
                "actual_start_price": unit.from_price,
                "end_date": _date(
                    bars,
                    _clip_index(unit.end_index, visible_start, visible_end),
                ),
                "end_price": (
                    bars[visible_end].close
                    if unit.end_index > visible_end
                    else unit.to_price
                ),
                "actual_end_date": _date(bars, unit.end_index),
                "actual_end_price": unit.to_price,
                "confirm_date": (
                    _date(bars, unit.confirm_index)
                    if unit.confirm_index is not None
                    else None
                ),
                "pending": unit.pending,
                "count": unit.count,
            }
        )

    zhongshu_overlay: list[dict] = []
    trends_overlay: list[dict] = []
    level_summary: list[dict] = []
    for info in final["levels"]:
        level = int(info["level"])
        level_summary.append(
            {
                "level": level,
                "label": info["label"],
                "canonical": bool(info["canonical"]),
                "units": len(info["units"]),
                "zhongshus": len(info["zss"]),
                "trends": len(info["trends"]),
            }
        )

        for zs in info["zss"]:
            if zs.end_index < visible_start or zs.start_index > visible_end:
                continue
            zhongshu_overlay.append(
                {
                    "level": level,
                    "level_label": info["label"],
                    "canonical": bool(info["canonical"]),
                    "start_date": _date(
                        bars,
                        _clip_index(zs.start_index, visible_start, visible_end),
                    ),
                    "end_date": _date(
                        bars,
                        _clip_index(zs.end_index, visible_start, visible_end),
                    ),
                    "actual_start_date": _date(bars, zs.start_index),
                    "actual_end_date": _date(bars, zs.end_index),
                    "confirm_date": _date(bars, zs.confirm_index),
                    "ZG": zs.zg,
                    "ZD": zs.zd,
                    "GG": zs.gg,
                    "DD": zs.dd,
                    "count": zs.count,
                    "pending": zs.pending,
                    "upgraded": zs.upgraded,
                }
            )

        for trend in info["trends"]:
            if trend.end_index < visible_start or trend.start_index > visible_end:
                continue
            trends_overlay.append(
                {
                    "level": level,
                    "level_label": info["label"],
                    "kind": trend.kind,
                    "direction": trend.direction,
                    "start_date": _date(
                        bars,
                        _clip_index(trend.start_index, visible_start, visible_end),
                    ),
                    "end_date": _date(
                        bars,
                        _clip_index(trend.end_index, visible_start, visible_end),
                    ),
                    "actual_start_date": _date(bars, trend.start_index),
                    "actual_end_date": _date(bars, trend.end_index),
                    "pending": trend.pending,
                    "count": trend.count,
                }
            )

    signal_overlay = []
    for signal in signal_ledger:
        anchor = int(signal["anchor_index"])
        if anchor < visible_start or anchor > visible_end:
            continue
        signal_overlay.append(
            {
                **signal,
                "anchor_date": _date(bars, anchor),
                "confirm_date": _date(bars, signal["confirm_index"]),
                "rule_name_zh": CHAN_RULE_NAMES_ZH[signal["rule_id"]],
            }
        )

    events = []
    for signal in signal_ledger[-100:]:
        action = "BUY" if signal["kind"].startswith("B") else "SELL"
        next_index = int(signal["confirm_index"]) + 1
        events.append(
            {
                "date": _date(bars, signal["confirm_index"]),
                "state": "OTHER",
                "state_zh": f"{signal['kind']} · {signal['level_label']}",
                "age": f"锚点 {_date(bars, signal['anchor_index'])}",
                "origin": signal["level_label"],
                "action": action,
                "action_zh": ACTION_NAMES_ZH[action],
                "rule_ids": [signal["rule_id"]],
                "rule_names_zh": [CHAN_RULE_NAMES_ZH[signal["rule_id"]]],
                "execution_date": (
                    _date(bars, next_index)
                    if next_index < len(bars)
                    else None
                ),
                "execution_price": (
                    bars[next_index].open
                    if next_index < len(bars)
                    else None
                ),
                "position_after": None,
                "risk_after": "独立缠论信号",
                "note": signal["note"],
            }
        )

    latest_signal = (
        signal_ledger[-1]
        if signal_ledger
        and int(signal_ledger[-1]["confirm_index"]) == len(bars) - 1
        else None
    )
    resolved_action = (
        "BUY"
        if latest_signal and latest_signal["kind"].startswith("B")
        else "SELL"
        if latest_signal and latest_signal["kind"].startswith("S")
        else "NONE"
    )

    last_bi = final["bis"][-1] if final["bis"] else None
    last_segment = final["segments"][-1] if final["segments"] else None
    last_zs = (
        zhongshu_overlay[-1]
        if zhongshu_overlay
        else None
    )
    last_seen_signal = signal_ledger[-1] if signal_ledger else None

    current_structure = _current_structure_text(final)
    latest = bars[-1]

    return {
        "strategy": {
            "id": CHAN_STRATEGY_ID,
            "selector_label": "缠论",
            "version": CHAN_STRATEGY_VERSION,
            "source_commit": CHAN_SOURCE,
            "active_rule_count": 6,
            "active_rules": CHAN_RULES,
            "active_rules_zh": {
                group: [CHAN_RULE_NAMES_ZH[x] for x in ids]
                for group, ids in CHAN_RULES.items()
            },
            "position_policy": "CHAN_SIGNAL_ONLY_V2",
            "position_policy_zh": "独立缠论信号；三买三卖不读取或修改任何其他策略仓位",
            "hard_exit": "NONE",
            "hard_exit_zh": "无外部策略退出规则",
            "display_candles": limit,
            "timeframe": str(timeframe),
            "bar_close_contract": "CHAN_FIRST_OBSERVED_CONFIRM_THEN_NEXT_BAR_OPEN",
            "bar_close_contract_zh": "结构画在锚点；买卖信号按首次确认K线记录，若用于交易则下一根同周期K线开盘执行",
            "rules_title_zh": "独立缠论 · 三买三卖",
            "policy_title_zh": "缠论完整结构链",
            "summary_state_label_zh": "当前缠论结构",
            "policy_steps_zh": [
                "① K线包含处理 → 顶/底分型",
                "② 有效分型 → 严格笔",
                "③ 笔 → 特征序列 → 线段",
                "④ L0笔级 + L1线段级中枢；走势类型继续递归生成更高级别",
                "⑤ 趋势背驰 → 一买/一卖；第一次不创新极值回试 → 二买/二卖",
                "⑥ 离开中枢后第一次不回中枢的回试/回抽 → 三买/三卖",
                "⑦ 所有B/S使用逐Bar FIRST_OBSERVED 首次确认时间，不用最终历史图倒推",
            ],
        },
        "snapshot": {
            "symbol": symbol,
            "latest_date": latest.date,
            "latest_close": latest.close,
            "state": "OTHER",
            "state_zh": current_structure,
            "run_age": None,
            "age_bucket": "FIRST_OBSERVED 逐Bar确认",
            "origin": None,
            "resolved_action": resolved_action,
            "resolved_action_zh": ACTION_NAMES_ZH[resolved_action],
            "rule_ids": [latest_signal["rule_id"]] if latest_signal else [],
            "rule_names_zh": (
                [CHAN_RULE_NAMES_ZH[latest_signal["rule_id"]]]
                if latest_signal
                else []
            ),
            "position_fraction": 0.0,
            "risk_state": "NORMAL",
            "risk_state_zh": current_structure,
            "risk_sub_zh": "独立缠论引擎；与12条/E/5s Stocks完全隔离",
            "next_action": (
                f"本根首次确认 {latest_signal['kind']} · {latest_signal['level_label']}；"
                "若用于交易，下一根同周期K线开盘才可执行。"
                if latest_signal
                else "等待新的已确认缠论买卖点；未完成结构只参与当下结构显示。"
            ),
            "chan_bi": (
                ("向上笔" if last_bi.direction == "up" else "向下笔")
                if last_bi
                else "尚未形成"
            ),
            "chan_segment": (
                (
                    "向上线段"
                    if last_segment.direction == "up"
                    else "向下线段"
                )
                + (" · 未完成" if last_segment.pending else " · 已确认")
                if last_segment
                else "尚未形成"
            ),
            "chan_zhongshu": (
                f"{last_zs['level_label']} · ZG {last_zs['ZG']:.3f} / ZD {last_zs['ZD']:.3f}"
                if last_zs
                else "当前可视区无中枢"
            ),
            "chan_last_signal": (
                f"{last_seen_signal['kind']} · {last_seen_signal['level_label']} · "
                f"{_date(bars, last_seen_signal['confirm_index'])}"
                if last_seen_signal
                else "暂无"
            ),
        },
        "chart": chart,
        "markers": [],
        "events": events,
        "chan": {
            "endpoints": endpoints,
            "bis": bis_overlay,
            "segments": segments_overlay,
            "zhongshus": zhongshu_overlay,
            "trends": trends_overlay,
            "signals": signal_overlay,
            "levels": level_summary,
            "counts": {
                "raw_bars_total": len(all_bars),
                "analysis_bars": len(bars),
                "source_offset": source_offset,
                "merged": len(final["merged"]),
                "all_fractals": len(final["fractals"]),
                "bi_endpoints": len(final["bi_points"]),
                "bis": len(final["bis"]),
                "segments": len(final["segments"]),
                "levels": len(final["levels"]),
                "zhongshus": sum(
                    len(x["zss"]) for x in final["levels"]
                ),
                "first_observed_signals": len(signal_ledger),
            },
            "causal_replay_bars": min(
                CHAN_CAUSAL_REPLAY_BARS,
                len(bars),
            ),
            "display_contract_zh": (
                "图上的顶/底只显示有效笔端点；笔、线段、中枢按结构锚点绘制；"
                "B1/B2/B3/S1/S2/S3只采用逐Bar首次确认时间。"
            ),
        },
    }
