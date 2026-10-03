from __future__ import annotations

"""Standalone Chan-theory structure view for the SLTD web page.

This module is intentionally independent from frozen SLTD V7 / E / 5s Stocks.
It implements a causal, completed-bar structure pipeline:

raw K -> inclusion merge -> fractal -> Bi -> segment -> Zhongshu
-> consolidation/trend divergence -> B1/B2/B3/S1/S2/S3.

Important:
- chart anchors are drawn at the structural turning point;
- signal confirmation time is stored separately;
- a signal is never considered tradable before its confirmation bar closes;
- this module produces structure analysis only and does not place simulated orders.

The implementation follows the original Chan-theory definitions audited in
research/sltd-chan-structure-v1, with explicit engineering choices documented
in CHAN_IMPLEMENTATION_NOTE_v1.md.
"""

from dataclasses import dataclass
from math import isfinite
from typing import Iterable, Literal

CHAN_STRATEGY_ID = "chan"
CHAN_STRATEGY_VERSION = "缠论结构 v1"
CHAN_SOURCE = "CHAN_THEORY_LEARNING_COMPLETE_C0A_VERIFIED"
CHAN_MIN_BARS = 80

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
    "CHAN_B2": "二买 · 一买后回试不创新低",
    "CHAN_B3": "三买 · 向上离开中枢后首次回试不跌回中枢",
    "CHAN_S1": "一卖 · 上涨趋势背驰后的第一类卖点",
    "CHAN_S2": "二卖 · 一卖后反抽不创新高",
    "CHAN_S3": "三卖 · 向下离开中枢后首次回抽不升回中枢",
}

ACTION_NAMES_ZH = {
    "BUY": "买点",
    "SELL": "卖点",
    "NONE": "无新买卖点",
}


@dataclass
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
    anchor_raw_index: int
    confirm_raw_index: int


@dataclass(frozen=True)
class Point:
    price: float
    raw_index: int
    confirm_raw_index: int


@dataclass(frozen=True)
class Bi:
    direction: Direction
    start: Point
    end: Point
    high: float
    low: float
    start_index: int
    end_index: int
    confirm_raw_index: int
    index: int


@dataclass(frozen=True)
class Segment:
    direction: Direction
    start_bi: int
    end_bi: int
    start: Point
    end: Point
    high: float
    low: float
    start_index: int
    end_index: int
    confirm_raw_index: int | None
    pending: bool
    count: int


@dataclass(frozen=True)
class Zhongshu:
    start_sub: int
    end_sub: int
    zg: float
    zd: float
    gg: float
    dd: float
    start_index: int
    end_index: int
    confirm_raw_index: int
    count: int
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
        raise ValueError(f"缠论结构至少需要 {CHAN_MIN_BARS} 根已结束 K 线")
    return out


def _contains(a: MergedBar, b: MergedBar) -> bool:
    return (
        (a.high >= b.high and a.low <= b.low)
        or (b.high >= a.high and b.low <= a.low)
    )


def merge_inclusion(bars: list[RawBar]) -> list[MergedBar]:
    """Direction-aware, left-to-right inclusion handling."""
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
        if not _contains(last, cur):
            out.append(cur)
            continue

        if len(out) >= 2:
            prev = out[-2]
            rising = last.high >= prev.high
        else:
            rising = True

        if rising:
            if cur.high > last.high:
                new_high, high_index = cur.high, cur.high_index
            else:
                new_high, high_index = last.high, last.high_index
            if cur.low > last.low:
                new_low, low_index = cur.low, cur.low_index
            else:
                new_low, low_index = last.low, last.low_index
        else:
            if cur.high < last.high:
                new_high, high_index = cur.high, cur.high_index
            else:
                new_high, high_index = last.high, last.high_index
            if cur.low < last.low:
                new_low, low_index = cur.low, cur.low_index
            else:
                new_low, low_index = last.low, last.low_index

        out[-1] = MergedBar(
            high=new_high,
            low=new_low,
            raw_start=last.raw_start,
            raw_end=cur.raw_end,
            high_index=high_index,
            low_index=low_index,
        )
    return out


def find_fractals(merged: list[MergedBar]) -> list[Fractal]:
    out: list[Fractal] = []
    for i in range(1, len(merged) - 1):
        a, b, c = merged[i - 1], merged[i], merged[i + 1]
        top = (
            b.high > a.high and b.high > c.high
            and b.low > a.low and b.low > c.low
        )
        bottom = (
            b.low < a.low and b.low < c.low
            and b.high < a.high and b.high < c.high
        )
        if top:
            out.append(
                Fractal(
                    "top",
                    i,
                    b.high,
                    b.high_index,
                    c.raw_end,
                )
            )
        elif bottom:
            out.append(
                Fractal(
                    "bottom",
                    i,
                    b.low,
                    b.low_index,
                    c.raw_end,
                )
            )
    return out


def _can_link_bi(
    merged: list[MergedBar],
    left: Fractal,
    right: Fractal,
) -> bool:
    # Lesson-77 strict separation: at least one merged K not belonging to
    # either fractal -> center-index gap >= 4.
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
            stronger = fx.price > last.price if fx.kind == "top" else fx.price < last.price
            if stronger:
                points[-1] = fx
            continue

        if _can_link_bi(merged, last, fx):
            points.append(fx)
    return points


def build_bis(points: list[Fractal]) -> list[Bi]:
    out: list[Bi] = []
    for i in range(1, len(points)):
        a, b = points[i - 1], points[i]
        start = Point(a.price, a.anchor_raw_index, a.confirm_raw_index)
        end = Point(b.price, b.anchor_raw_index, b.confirm_raw_index)
        out.append(
            Bi(
                direction="up" if a.kind == "bottom" else "down",
                start=start,
                end=end,
                high=max(a.price, b.price),
                low=min(a.price, b.price),
                start_index=start.raw_index,
                end_index=end.raw_index,
                confirm_raw_index=b.confirm_raw_index,
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


def _is_new_extreme(
    bis: list[Bi],
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


def _feature_before(
    bis: list[Bi],
    start: int,
    end_exclusive: int,
    main_direction: Direction,
) -> list[list[float]]:
    raw = [
        (b.high, b.low)
        for b in bis[start:end_exclusive]
        if b.direction != main_direction
    ]
    return _normalize_features(raw, main_direction == "up")


def _find_segment_division(
    bis: list[Bi],
    start: int,
    min_end: int = -1,
) -> tuple[int, int] | None:
    """Return (anchor Bi index, confirming Bi index)."""
    if start >= len(bis):
        return None
    main_direction = bis[start].direction
    rising = main_direction == "up"
    cand: dict | None = None

    for idx in range(start, len(bis)):
        bi = bis[idx]

        if cand is not None:
            exceeded = bi.high > cand["extreme"] if rising else bi.low < cand["extreme"]
            if exceeded:
                cand = None

        if cand is not None:
            if cand["case"] is None:
                if bi.direction != main_direction and idx > cand["at"]:
                    last_char = cand["last_char"]
                    gap = bi.low > last_char[0] if rising else bi.high < last_char[1]
                    cand["case"] = 2 if gap else 1
                    cand["confirm_seq"] = []
                    cand["post_seq"] = [] if gap else [[bi.high, bi.low]]

            elif cand["case"] == 1:
                if bi.direction != main_direction and idx > cand["at"] + 1:
                    _append_feature(cand["post_seq"], (bi.high, bi.low), rising)
                    seq = cand["post_seq"]
                    if len(seq) >= 2:
                        turned = seq[-1][0] < seq[0][0] if rising else seq[-1][1] > seq[0][1]
                        if turned:
                            return int(cand["at"]), idx

            else:
                if bi.direction == main_direction and idx > cand["at"] + 1:
                    _append_feature(cand["confirm_seq"], (bi.high, bi.low), not rising)
                    seq = cand["confirm_seq"]
                    if len(seq) >= 3:
                        a, b, c = seq[-3], seq[-2], seq[-1]
                        confirmed = (
                            b[1] < a[1] and b[1] < c[1]
                            if rising
                            else b[0] > a[0] and b[0] > c[0]
                        )
                        if confirmed:
                            return int(cand["at"]), idx

        if (
            cand is None
            and bi.direction == main_direction
            and idx >= start + 2
            and idx > min_end
            and _is_new_extreme(bis, start, idx, rising)
        ):
            pre = _feature_before(bis, start, idx, main_direction)
            if pre:
                cand = {
                    "at": idx,
                    "extreme": bi.high if rising else bi.low,
                    "last_char": pre[-1],
                    "case": None,
                }

    return None


def _segment_start_broken(bis: list[Bi], start: int) -> bool:
    first = bis[start]
    origin = first.start.price
    rising = first.direction == "up"
    for bi in bis[start + 1:]:
        if rising and bi.low < origin:
            return True
        if (not rising) and bi.high > origin:
            return True
    return False


def _choose_start(bis: list[Bi]) -> int:
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
    bis: list[Bi],
    start: int,
    end: int,
    confirm_bi: int | None,
    pending: bool,
) -> Segment:
    chunk = bis[start:end + 1]
    return Segment(
        direction=bis[start].direction,
        start_bi=start,
        end_bi=end,
        start=bis[start].start,
        end=bis[end].end,
        high=max(x.high for x in chunk),
        low=min(x.low for x in chunk),
        start_index=bis[start].start_index,
        end_index=bis[end].end_index,
        confirm_raw_index=None if confirm_bi is None else bis[confirm_bi].confirm_raw_index,
        pending=pending,
        count=end - start + 1,
    )


def build_segments(bis: list[Bi]) -> list[Segment]:
    if not bis:
        return []
    out: list[Segment] = []
    start = _choose_start(bis)
    guard = 0

    while start < len(bis):
        division = _find_segment_division(bis, start)
        if division is None:
            if out and _segment_start_broken(bis, start) and guard < len(bis):
                guard += 1
                prev = out.pop()
                later = _find_segment_division(
                    bis,
                    prev.start_bi,
                    prev.end_bi,
                )
                if later is not None:
                    out.append(
                        _make_segment(
                            bis,
                            prev.start_bi,
                            later[0],
                            later[1],
                            False,
                        )
                    )
                    start = later[0] + 1
                    continue
                start = prev.start_bi
                continue
            break

        anchor, confirm_bi = division
        out.append(_make_segment(bis, start, anchor, confirm_bi, False))
        start = anchor + 1

    if start < len(bis):
        out.append(_make_segment(bis, start, len(bis) - 1, None, True))
    return out


def build_zhongshus(segments: list[Segment]) -> list[Zhongshu]:
    """Build canonical current-level Zhongshu from consecutive lower-level segments.

    Only completed segments participate in confirmed Zhongshu construction.
    """
    subs = [x for x in segments if not x.pending and x.confirm_raw_index is not None]
    out: list[Zhongshu] = []
    i = 1  # sub[0] is the entering movement
    while i + 2 < len(subs):
        trio = subs[i:i + 3]
        zg = min(x.high for x in trio)
        zd = max(x.low for x in trio)
        if not zg > zd:
            i += 2
            continue

        def touch(s: Segment) -> bool:
            return s.low <= zg and s.high >= zd

        end = i + 2
        j = i + 3
        while j < len(subs):
            tj = touch(subs[j])
            tn = touch(subs[j + 1]) if j + 1 < len(subs) else False
            if tj and tn:
                end = j
                j += 1
                continue
            if (not tj) and tn:
                end = j + 1
                j += 2
                continue
            break

        chunk = subs[i:end + 1]
        out.append(
            Zhongshu(
                start_sub=i,
                end_sub=end,
                zg=zg,
                zd=zd,
                gg=max(x.high for x in chunk),
                dd=min(x.low for x in chunk),
                start_index=chunk[0].start_index,
                end_index=chunk[-1].end_index,
                confirm_raw_index=max(int(x.confirm_raw_index) for x in trio if x.confirm_raw_index is not None),
                count=end - i + 1,
                upgraded=(end - i + 1) >= 9,
            )
        )
        i = end + 2
    return out


def link_zhongshus(zss: list[Zhongshu]) -> list[str | None]:
    links: list[str | None] = [None]
    for k in range(1, len(zss)):
        a, b = zss[k - 1], zss[k]
        if b.dd > a.gg:
            links.append("up")
        elif b.gg < a.dd:
            links.append("down")
        else:
            links.append("expand")
    return links


def _ema(values: list[float], period: int) -> list[float]:
    alpha = 2.0 / (period + 1.0)
    out: list[float] = []
    prev = values[0]
    for i, value in enumerate(values):
        prev = value if i == 0 else alpha * value + (1.0 - alpha) * prev
        out.append(prev)
    return out


def macd(closes: list[float]) -> dict[str, list[float]]:
    fast = _ema(closes, 12)
    slow = _ema(closes, 26)
    dif = [a - b for a, b in zip(fast, slow)]
    dea = _ema(dif, 9)
    hist = [2.0 * (a - b) for a, b in zip(dif, dea)]
    return {"dif": dif, "dea": dea, "hist": hist}


def _force(sub: Segment, hist: list[float], sign: int) -> float:
    total = 0.0
    a = max(0, sub.start_index)
    b = min(len(hist) - 1, sub.end_index)
    for i in range(a, b + 1):
        h = hist[i]
        if (sign > 0 and h > 0) or (sign < 0 and h < 0):
            total += abs(h)
    return total


def _dif_ext(sub: Segment, dif: list[float], sign: int) -> float:
    a = max(0, sub.start_index)
    b = min(len(dif) - 1, sub.end_index)
    vals = dif[a:b + 1]
    if not vals:
        return 0.0
    return max(vals) if sign > 0 else min(vals)


def compute_signals(
    bars: list[RawBar],
    segments: list[Segment],
    zss: list[Zhongshu],
    links: list[str | None],
) -> list[dict]:
    """Compute six Chan BSP classes on confirmed segment/Zhongshu structure."""
    subs = [x for x in segments if not x.pending and x.confirm_raw_index is not None]
    if not subs or not zss:
        return []

    m = macd([x.close for x in bars])
    signals: list[dict] = []

    def add(kind: str, seg: Segment, zs_idx: int, note: str) -> None:
        confirm_idx = int(seg.confirm_raw_index if seg.confirm_raw_index is not None else seg.end_index)
        signals.append(
            {
                "kind": kind,
                "rule_id": f"CHAN_{kind}",
                "anchor_index": seg.end.raw_index,
                "confirm_index": confirm_idx,
                "price": seg.end.price,
                "zs_index": zs_idx,
                "note": note,
            }
        )

    for k, zs in enumerate(zss):
        enter = subs[zs.start_sub - 1] if zs.start_sub > 0 else None
        leave = subs[zs.end_sub + 1] if zs.end_sub + 1 < len(subs) else None

        if enter and leave and enter.direction == leave.direction:
            down = enter.direction == "down"
            sign = -1 if down else 1
            new_extreme = (
                leave.low < min(enter.low, zs.dd)
                if down
                else leave.high > max(enter.high, zs.gg)
            )
            dif_enter = _dif_ext(enter, m["dif"], sign)

            pulled = False
            lo = max(0, subs[zs.start_sub].start_index)
            hi = min(len(bars) - 1, subs[zs.end_sub].end_index)
            for i in range(lo, hi + 1):
                if down:
                    if m["dif"][i] >= 0.25 * dif_enter:
                        pulled = True
                        break
                else:
                    if m["dif"][i] <= 0.25 * dif_enter:
                        pulled = True
                        break

            weaker = (
                _force(leave, m["hist"], sign) < _force(enter, m["hist"], sign)
                or abs(_dif_ext(leave, m["dif"], sign)) < abs(dif_enter)
            )

            if new_extreme and pulled and weaker:
                trend_link = links[k] if k < len(links) else None
                if trend_link == ("down" if down else "up"):
                    first_kind = "B1" if down else "S1"
                    add(
                        first_kind,
                        leave,
                        k,
                        "下跌趋势背驰" if down else "上涨趋势背驰",
                    )

                    s1_idx = zs.end_sub + 2
                    s2_idx = zs.end_sub + 3
                    if s2_idx < len(subs):
                        s2 = subs[s2_idx]
                        valid = s2.low > leave.low if down else s2.high < leave.high
                        if valid:
                            add(
                                "B2" if down else "S2",
                                s2,
                                k,
                                "一买后回试不创新低" if down else "一卖后反抽不创新高",
                            )

        # B3 / S3: first return after leaving Zhongshu.
        a = subs[zs.end_sub + 1] if zs.end_sub + 1 < len(subs) else None
        b = subs[zs.end_sub + 2] if zs.end_sub + 2 < len(subs) else None
        last_in = subs[zs.end_sub]

        if a and a.direction == "down" and last_in.high > zs.zg and a.low >= zs.zg:
            add("B3", a, k, "向上离开后首次回试不跌回 ZG")
        elif a and a.direction == "up" and last_in.low < zs.zd and a.high <= zs.zd:
            add("S3", a, k, "向下离开后首次回抽不升回 ZD")
        elif a and b and a.direction == "up" and a.high > zs.zg and b.low >= zs.zg:
            add("B3", b, k, "向上离开后首次回试不跌回 ZG")
        elif a and b and a.direction == "down" and a.low < zs.zd and b.high <= zs.zd:
            add("S3", b, k, "向下离开后首次回抽不升回 ZD")

    # A structural point can be rediscovered through overlapping Zhongshu scans.
    # Keep the earliest confirmed instance for each class/anchor.
    unique: dict[tuple[str, int], dict] = {}
    for item in sorted(signals, key=lambda x: (x["confirm_index"], x["anchor_index"], x["kind"])):
        key = (item["kind"], item["anchor_index"])
        unique.setdefault(key, item)
    return sorted(unique.values(), key=lambda x: (x["confirm_index"], x["anchor_index"], x["kind"]))


def _structure_state(
    segments: list[Segment],
    zss: list[Zhongshu],
    latest_index: int,
) -> str:
    if zss:
        zs = zss[-1]
        if zs.start_index <= latest_index <= zs.end_index:
            return "中枢震荡"
    if segments:
        return "向上线段" if segments[-1].direction == "up" else "向下线段"
    return "结构形成中"


def _date(bars: list[RawBar], index: int) -> str:
    index = max(0, min(len(bars) - 1, int(index)))
    return bars[index].date


def analyze_chan(
    symbol: str,
    candles: Iterable[dict],
    *,
    display_limit: int = 300,
    timeframe: str = "1d",
) -> dict:
    bars = _validate_candles(candles)
    merged = merge_inclusion(bars)
    fractals = find_fractals(merged)
    points = select_bi_points(merged, fractals)
    bis = build_bis(points)
    segments = build_segments(bis)
    zss = build_zhongshus(segments)
    links = link_zhongshus(zss)
    signals = compute_signals(bars, segments, zss, links)

    limit = max(80, min(int(display_limit), 500))
    start = max(0, len(bars) - limit)
    visible_dates = {x.date for x in bars[start:]}

    chart = [
        {
            "date": b.date,
            "open": b.open,
            "high": b.high,
            "low": b.low,
            "close": b.close,
            "volume": b.volume,
            "state": "OTHER",
            "state_zh": "缠论结构",
            "position": 0.0,
            "risk_armed": False,
        }
        for b in bars[start:]
    ]

    fractal_overlay = [
        {
            "type": f.kind,
            "anchor_date": _date(bars, f.anchor_raw_index),
            "confirm_date": _date(bars, f.confirm_raw_index),
            "price": f.price,
        }
        for f in fractals
        if _date(bars, f.anchor_raw_index) in visible_dates
    ]
    bi_overlay = [
        {
            "direction": b.direction,
            "start_date": _date(bars, b.start.raw_index),
            "start_price": b.start.price,
            "end_date": _date(bars, b.end.raw_index),
            "end_price": b.end.price,
            "confirm_date": _date(bars, b.confirm_raw_index),
        }
        for b in bis
        if _date(bars, b.end.raw_index) in visible_dates or _date(bars, b.start.raw_index) in visible_dates
    ]
    segment_overlay = [
        {
            "direction": s.direction,
            "start_date": _date(bars, s.start.raw_index),
            "start_price": s.start.price,
            "end_date": _date(bars, s.end.raw_index),
            "end_price": s.end.price,
            "confirm_date": (
                _date(bars, s.confirm_raw_index)
                if s.confirm_raw_index is not None
                else None
            ),
            "pending": s.pending,
            "count": s.count,
        }
        for s in segments
        if _date(bars, s.end.raw_index) in visible_dates or _date(bars, s.start.raw_index) in visible_dates
    ]
    zs_overlay = [
        {
            "start_date": _date(bars, z.start_index),
            "end_date": _date(bars, z.end_index),
            "confirm_date": _date(bars, z.confirm_raw_index),
            "ZG": z.zg,
            "ZD": z.zd,
            "GG": z.gg,
            "DD": z.dd,
            "count": z.count,
            "upgraded": z.upgraded,
        }
        for z in zss
        if _date(bars, z.end_index) in visible_dates or _date(bars, z.start_index) in visible_dates
    ]
    signal_overlay = [
        {
            **s,
            "anchor_date": _date(bars, s["anchor_index"]),
            "confirm_date": _date(bars, s["confirm_index"]),
            "rule_name_zh": CHAN_RULE_NAMES_ZH[s["rule_id"]],
        }
        for s in signals
        if _date(bars, s["anchor_index"]) in visible_dates
    ]

    latest_signal = None
    if signals and int(signals[-1]["confirm_index"]) == len(bars) - 1:
        latest_signal = signals[-1]

    events = []
    for s in signals[-80:]:
        action = "BUY" if s["kind"].startswith("B") else "SELL"
        events.append(
            {
                "date": _date(bars, s["confirm_index"]),
                "state": "OTHER",
                "state_zh": s["kind"],
                "age": f"锚点 {_date(bars, s['anchor_index'])}",
                "origin": None,
                "action": action,
                "action_zh": ACTION_NAMES_ZH[action],
                "rule_ids": [s["rule_id"]],
                "rule_names_zh": [CHAN_RULE_NAMES_ZH[s["rule_id"]]],
                "execution_date": None,
                "execution_price": None,
                "position_after": None,
                "risk_after": "仅结构信号",
                "note": s["note"],
            }
        )

    latest = bars[-1]
    state_text = _structure_state(segments, zss, len(bars) - 1)
    latest_kind = latest_signal["kind"] if latest_signal else None
    resolved_action = (
        "BUY" if latest_kind and latest_kind.startswith("B")
        else "SELL" if latest_kind and latest_kind.startswith("S")
        else "NONE"
    )
    latest_rules = [latest_signal["rule_id"]] if latest_signal else []

    last_bi = bis[-1] if bis else None
    last_segment = segments[-1] if segments else None
    last_zs = zss[-1] if zss else None
    last_signal = signals[-1] if signals else None

    next_action = (
        f"本根确认 {latest_kind}（{CHAN_RULE_NAMES_ZH[latest_signal['rule_id']]}）；"
        "这是独立缠论结构信号，不自动修改 V7 仓位。"
        if latest_signal
        else "等待新的已确认分型 / 笔 / 线段 / 中枢买卖点；未确认结构只画线，不生成交易信号。"
    )

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
            "position_policy": "STRUCTURE_ONLY_NO_POSITION",
            "position_policy_zh": "独立缠论结构分析；本版本不自动管理 V7 / E / 5s Stocks 仓位",
            "hard_exit": "NONE",
            "hard_exit_zh": "无独立强制清仓；一二三卖仅作为缠论结构卖点",
            "display_candles": limit,
            "timeframe": str(timeframe),
            "bar_close_contract": "CHAN_ANCHOR_DRAWN_AT_STRUCTURE_POINT_CONFIRMATION_USED_FOR_SIGNAL",
            "bar_close_contract_zh": "图形画在线段/买卖点锚点；信号只在结构首次确认的已结束K线产生",
            "rules_title_zh": "缠论三买三卖",
            "policy_title_zh": "缠论结构链",
            "summary_state_label_zh": "当前缠论结构",
            "policy_steps_zh": [
                "① K线包含处理 → 顶/底分型",
                "② 顶底分型 → 严格笔（第77课口径）",
                "③ 笔 → 特征序列 → 线段",
                "④ 连续次级别线段重叠 → 中枢",
                "⑤ 趋势/盘整结构 + 力度比较 → 一买/一卖；随后确认二买/二卖",
                "⑥ 离开中枢后的第一次不回中枢回试/回抽 → 三买/三卖",
            ],
        },
        "snapshot": {
            "symbol": symbol,
            "latest_date": latest.date,
            "latest_close": latest.close,
            "state": "OTHER",
            "state_zh": state_text,
            "run_age": None,
            "age_bucket": "FIRST_OBSERVED 确认",
            "origin": None,
            "resolved_action": resolved_action,
            "resolved_action_zh": ACTION_NAMES_ZH[resolved_action],
            "rule_ids": latest_rules,
            "rule_names_zh": [CHAN_RULE_NAMES_ZH[x] for x in latest_rules],
            "position_fraction": 0.0,
            "risk_state": "NORMAL",
            "risk_state_zh": state_text,
            "risk_sub_zh": "结构锚点与首次确认时间分离；不把历史回画位置当成当时已知信号",
            "next_action": next_action,
            "chan_bi": (
                ("向上笔" if last_bi.direction == "up" else "向下笔")
                if last_bi else "尚未形成"
            ),
            "chan_segment": (
                ("向上线段" if last_segment.direction == "up" else "向下线段")
                + (" · 未完成" if last_segment.pending else " · 已确认")
                if last_segment else "尚未形成"
            ),
            "chan_zhongshu": (
                f"ZG {last_zs.zg:.3f} / ZD {last_zs.zd:.3f}"
                if last_zs else "当前无已确认中枢"
            ),
            "chan_last_signal": (
                f"{last_signal['kind']} · {_date(bars, last_signal['confirm_index'])}"
                if last_signal else "暂无"
            ),
        },
        "chart": chart,
        "markers": [],
        "events": events,
        "chan": {
            "fractals": fractal_overlay,
            "bis": bi_overlay,
            "segments": segment_overlay,
            "zhongshus": zs_overlay,
            "signals": signal_overlay,
            "counts": {
                "fractals": len(fractals),
                "bis": len(bis),
                "segments": len(segments),
                "zhongshus": len(zss),
                "signals": len(signals),
            },
            "display_contract_zh": "锚点用于画图；确认日用于信号列表与任何后续交易研究。",
        },
    }
