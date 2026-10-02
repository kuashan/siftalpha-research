from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Iterable, Sequence


RANK = {
    "SHORT": -2,
    "LIGHT_SHORT": -1,
    "GRAY": 0,
    "LIGHT_LONG": 1,
    "LONG": 2,
}
DIMS = ("trend", "capital", "momentum", "accel", "anomaly")


@dataclass(frozen=True)
class Candle:
    open_time: int
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass(frozen=True)
class BarEvaluation:
    index: int
    open_time: int
    states: dict[str, str]
    buy_active: tuple[str, ...]
    sell_active: tuple[str, ...]
    buy_onsets: tuple[str, ...]
    sell_onsets: tuple[str, ...]
    features: dict[str, float | int] | None


def _finite(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def _num(value: Any) -> float | None:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def normalize_candles(rows: Iterable[Any]) -> list[Candle]:
    out: list[Candle] = []
    for i, row in enumerate(rows):
        if isinstance(row, Candle):
            candle = row
        elif isinstance(row, dict):
            open_time = row.get("open_time", row.get("openTime", row.get("time", i)))
            candle = Candle(
                open_time=int(open_time),
                open=float(row["open"]),
                high=float(row["high"]),
                low=float(row["low"]),
                close=float(row["close"]),
                volume=float(row["volume"]),
            )
        elif isinstance(row, Sequence) and len(row) >= 6:
            candle = Candle(
                open_time=int(row[0]),
                open=float(row[1]),
                high=float(row[2]),
                low=float(row[3]),
                close=float(row[4]),
                volume=float(row[5]),
            )
        else:
            raise ValueError(f"unsupported candle row at index {i}")

        if not all(math.isfinite(x) for x in (candle.open, candle.high, candle.low, candle.close, candle.volume)):
            raise ValueError(f"non-finite candle at index {i}")
        if candle.close <= 0 or candle.high <= 0 or candle.low <= 0 or candle.open <= 0:
            raise ValueError(f"non-positive price at index {i}")
        out.append(candle)

    out.sort(key=lambda x: x.open_time)
    return out


def _blank(n: int) -> list[float | None]:
    return [None] * n


def _ma(values: Sequence[float | None], window: int) -> list[float | None]:
    n = len(values)
    out = _blank(n)
    queue: list[float | None] = []
    total = 0.0
    for i, value in enumerate(values):
        queue.append(value)
        total += float(value) if _finite(value) else 0.0
        if len(queue) > window:
            old = queue.pop(0)
            total -= float(old) if _finite(old) else 0.0
        if len(queue) == window and all(_finite(x) for x in queue):
            out[i] = total / window
    return out


def _ema(values: Sequence[float | None], window: int) -> list[float | None]:
    n = len(values)
    out = _blank(n)
    k = 2.0 / (window + 1.0)
    previous: float | None = None
    for i, value in enumerate(values):
        if not _finite(value):
            continue
        x = float(value)
        previous = x if previous is None else k * x + (1.0 - k) * previous
        out[i] = previous
    return out


def _sma(values: Sequence[float | None], n_window: int, m: int) -> list[float | None]:
    n = len(values)
    out = _blank(n)
    previous: float | None = None
    for i, value in enumerate(values):
        if not _finite(value):
            continue
        x = float(value)
        previous = x if previous is None else (m * x + (n_window - m) * previous) / n_window
        out[i] = previous
    return out


def _roll(values: Sequence[float | None], window: int, fn) -> list[float | None]:
    n = len(values)
    out = _blank(n)
    for i in range(window - 1, n):
        chunk = list(values[i - window + 1 : i + 1])
        if all(_finite(x) for x in chunk):
            out[i] = float(fn([float(x) for x in chunk]))
    return out


def _hhv(values: Sequence[float | None], window: int) -> list[float | None]:
    return _roll(values, window, max)


def _llv(values: Sequence[float | None], window: int) -> list[float | None]:
    return _roll(values, window, min)


def _std(values: Sequence[float | None], window: int) -> list[float | None]:
    def calc(chunk: list[float]) -> float:
        mean = sum(chunk) / window
        return math.sqrt(sum((x - mean) ** 2 for x in chunk) / window)

    return _roll(values, window, calc)


def _count(values: Sequence[bool], window: int) -> list[float | None]:
    n = len(values)
    out = _blank(n)
    total = 0
    for i, value in enumerate(values):
        total += 1 if value else 0
        if i >= window:
            total -= 1 if values[i - window] else 0
        if i >= window - 1:
            out[i] = float(total)
    return out


def _forecast(values: Sequence[float | None], window: int) -> list[float | None]:
    n = len(values)
    out = _blank(n)
    mx = (window - 1) / 2.0
    den = sum((k - mx) ** 2 for k in range(window))
    for i in range(window - 1, n):
        y = list(values[i - window + 1 : i + 1])
        if not all(_finite(x) for x in y):
            continue
        yy = [float(x) for x in y]
        my = sum(yy) / window
        num = sum((k - mx) * (yy[k] - my) for k in range(window))
        out[i] = my + (num / den) * (window - 1) / 2.0
    return out


def _slope(values: Sequence[int]) -> float:
    n = len(values)
    mx = (n - 1) / 2.0
    my = sum(values) / n
    numerator = sum((i - mx) * (values[i] - my) for i in range(n))
    denominator = sum((i - mx) ** 2 for i in range(n))
    return numerator / denominator if denominator else 0.0


def _state(long: Sequence[bool], light_long: Sequence[bool], short: Sequence[bool], light_short: Sequence[bool], i: int) -> str:
    if long[i]:
        return "LONG"
    if light_long[i]:
        return "LIGHT_LONG"
    if short[i]:
        return "SHORT"
    if light_short[i]:
        return "LIGHT_SHORT"
    return "GRAY"


def _base_states(candles: list[Candle]) -> list[dict[str, str]]:
    n = len(candles)
    c = [r.close for r in candles]
    h = [r.high for r in candles]
    l = [r.low for r in candles]
    v = [r.volume for r in candles]

    vol_ma5 = _ma(v, 5)
    vol_ma20 = _ma(v, 20)
    ma20 = _ma(c, 20)
    rel_vol = [v[i] / vol_ma20[i] if _finite(vol_ma20[i]) and vol_ma20[i] != 0 else None for i in range(n)]
    hsl_ma5 = _ma(rel_vol, 5)

    tr: list[float] = []
    for i in range(n):
        tr.append(
            h[i] - l[i]
            if i == 0
            else max(h[i] - l[i], abs(h[i] - c[i - 1]), abs(l[i] - c[i - 1]))
        )
    atr14 = _ma(tr, 14)
    atr_ma50 = _ma(atr14, 50)
    vol_ratio = [
        atr14[i] / atr_ma50[i]
        if _finite(atr14[i]) and _finite(atr_ma50[i]) and atr_ma50[i] != 0
        else None
        for i in range(n)
    ]
    amp = [None if i == 0 else (h[i] - l[i]) / c[i - 1] * 100.0 for i in range(n)]
    amp_atr = [
        amp[i] / (atr14[i] / c[i - 1] * 100.0)
        if i > 0 and _finite(amp[i]) and _finite(atr14[i]) and atr14[i] != 0
        else None
        for i in range(n)
    ]
    shock = [1.0 + (x - 2.0) * 0.3 if _finite(x) and x > 2.0 else (1.0 if _finite(x) else None) for x in amp_atr]
    emotion_vol = [1.0 + (x - 1.0) * 0.1 if _finite(x) else None for x in vol_ratio]
    emotion_gain = [1.0 + (x - 1.0) * 0.5 if _finite(x) else None for x in vol_ratio]
    wash_vol = [max(min(2.5 * x, 3.0), 1.2) if _finite(x) else None for x in emotion_vol]
    wash_gain = [
        max(min(5.0 * emotion_gain[i] * shock[i], 12.0), 0.5)
        if _finite(emotion_gain[i]) and _finite(shock[i])
        else None
        for i in range(n)
    ]
    bias20 = [(c[i] - ma20[i]) / ma20[i] * 100.0 if _finite(ma20[i]) and ma20[i] != 0 else None for i in range(n)]

    v2 = _ema(c, 5)
    v3 = [(c[i] - v2[i]) * 100.0 / c[i] if _finite(v2[i]) and c[i] != 0 else None for i in range(n)]
    v4 = [_finite(x) for x in v3]
    ll30, hh30 = _llv(l, 30), _hhv(h, 30)
    v8 = [
        (c[i] - ll30[i]) / (hh30[i] - ll30[i]) * 100.0
        if _finite(ll30[i]) and _finite(hh30[i]) and hh30[i] != ll30[i]
        else None
        for i in range(n)
    ]
    v9 = _sma(v8, 6, 1)
    v10 = _sma(v9, 3, 1)
    v11 = _ema(c, 17)
    ll9, hh9 = _llv(l, 9), _hhv(h, 9)
    v12 = [
        (c[i] - ll9[i]) / (hh9[i] - ll9[i]) * 100.0
        if _finite(ll9[i]) and _finite(hh9[i]) and hh9[i] != ll9[i]
        else None
        for i in range(n)
    ]
    v13 = _sma(v12, 3, 1)
    v14 = _sma(v13, 3, 1)
    v15 = [3.0 * v13[i] - 2.0 * v14[i] if _finite(v13[i]) and _finite(v14[i]) else None for i in range(n)]
    up = [None if i == 0 else max(c[i] - c[i - 1], 0.0) for i in range(n)]
    absd = [None if i == 0 else abs(c[i] - c[i - 1]) for i in range(n)]
    sup, sab = _sma(up, 9, 1), _sma(absd, 9, 1)
    v18 = [sup[i] / sab[i] * 100.0 if _finite(sup[i]) and _finite(sab[i]) and sab[i] != 0 else None for i in range(n)]
    f20 = _forecast(_ema(c, 5), 6)
    f21 = _forecast(_ema(c, 8), 6)
    f22 = _forecast(_ema(c, 11), 6)
    f23 = _forecast(_ema(c, 14), 6)
    f24 = _forecast(_ema(c, 17), 6)
    f25 = [
        f20[i] + f21[i] + f22[i] + f23[i] - 4.0 * f24[i]
        if all(_finite(x) for x in (f20[i], f21[i], f22[i], f23[i], f24[i]))
        else None
        for i in range(n)
    ]
    f26 = _ema(f25, 2)

    t_long = [False] * n
    t_short = [False] * n
    t_light_long = [False] * n
    t_light_short = [False] * n
    tabs = _blank(n)
    for i in range(n):
        tabs[i] = v10[i] - v10[i - 3] if i >= 3 and _finite(v10[i]) and _finite(v10[i - 3]) else None
        vok = _finite(vol_ma20[i]) and v[i] >= vol_ma20[i]
        vbad = (
            i > 0
            and _finite(vol_ma20[i])
            and (
                (v[i] >= vol_ma20[i] * 1.2 and c[i] < c[i - 1])
                or (v[i] <= vol_ma20[i] * 0.95)
            )
        )
        bl = (
            _finite(v9[i]) and _finite(v10[i]) and i > 0 and _finite(v10[i - 1])
            and v9[i] > v10[i] and v10[i] > v10[i - 1]
            and _finite(v3[i]) and v3[i] > -0.5
        )
        bs = (
            _finite(v9[i]) and _finite(v10[i]) and i > 0 and _finite(v10[i - 1])
            and v9[i] < v10[i] and v10[i] < v10[i - 1]
            and _finite(v3[i]) and v3[i] < 0.5
        )
        t_long[i] = bool(bl and vok and _finite(tabs[i]) and tabs[i] >= 2.0 and v4[i])
        t_short[i] = bool(bs and _finite(tabs[i]) and tabs[i] <= -1.15 and vbad and v4[i])
        t_light_long[i] = bool(bl and not t_long[i])
        t_light_short[i] = bool(bs and not t_short[i])

    tc = _count(t_long, 2)
    mstd = _std(f26, 5)
    m_long = [False] * n
    m_short = [False] * n
    m_light_long = [False] * n
    m_light_short = [False] * n
    for i in range(n):
        sl = f26[i] - f26[i - 1] if i > 0 and _finite(f26[i]) and _finite(f26[i - 1]) else None
        th = mstd[i] * 0.35 if _finite(mstd[i]) else None
        bl = _finite(v9[i]) and _finite(v10[i]) and v9[i] > v10[i]
        bs = _finite(v9[i]) and _finite(v10[i]) and v9[i] < v10[i]
        m_long[i] = bool(bl and _finite(sl) and _finite(th) and sl > th)
        m_short[i] = bool(bs and _finite(sl) and _finite(th) and sl < -th)
        m_light_long[i] = bool(bl and _finite(sl) and _finite(th) and not (sl > th))
        m_light_short[i] = bool(bs and _finite(sl) and _finite(th) and not (sl < -th))

    a_long = [False] * n
    a_short = [False] * n
    a_light_long = [False] * n
    a_light_short = [False] * n
    for i in range(n):
        jc = v15[i] - v15[i - 2] if i >= 2 and _finite(v15[i]) and _finite(v15[i - 2]) else None
        rc = v18[i] - v18[i - 2] if i >= 2 and _finite(v18[i]) and _finite(v18[i - 2]) else None
        bu = _finite(v9[i]) and _finite(v10[i]) and v9[i] > v10[i]
        be = _finite(v9[i]) and _finite(v10[i]) and v9[i] < v10[i]
        pr = (
            i >= 20 and _finite(v9[i]) and _finite(v10[i]) and abs(v9[i] - v10[i]) < 2.5
            and tc[i] != 2
            and _finite(ma20[i]) and _finite(ma20[i - 20])
            and ma20[i] > ma20[i - 20] * 0.98
        )
        tal = bool(bu and ((_finite(jc) and jc >= 8.0) or (_finite(rc) and rc >= 6.0)))
        tas = bool(be and ((_finite(jc) and jc <= -8.0) or (_finite(rc) and rc <= -6.0)))
        ob = bool(
            pr
            and ((_finite(jc) and jc <= -8.0) or (_finite(rc) and rc <= -6.0))
            and ((_finite(v15[i]) and v15[i] < 30.0) or (_finite(v18[i]) and v18[i] < 40.0))
        )
        os = bool(
            pr
            and ((_finite(jc) and jc >= 8.0) or (_finite(rc) and rc >= 6.0))
            and ((_finite(v15[i]) and v15[i] > 70.0) or (_finite(v18[i]) and v18[i] > 80.0))
        )
        a_long[i] = tal or ob
        a_short[i] = tas or os
        a_light_long[i] = bool(
            (bu and ((_finite(jc) and jc > 0) or (_finite(rc) and rc > 0)) and not tal)
            or (
                pr
                and ((_finite(v15[i]) and v15[i] < 40.0) or (_finite(v18[i]) and v18[i] < 50.0))
                and ((_finite(jc) and jc > 0) or (_finite(rc) and rc > 0))
                and not ob
            )
        )
        a_light_short[i] = bool(
            (be and ((_finite(jc) and jc < 0) or (_finite(rc) and rc < 0)) and not tas)
            or (
                pr
                and ((_finite(v15[i]) and v15[i] > 60.0) or (_finite(v18[i]) and v18[i] > 70.0))
                and ((_finite(jc) and jc < 0) or (_finite(rc) and rc < 0))
                and not os
            )
        )

    hh15, ll12 = _hhv(h, 15), _llv(l, 12)
    c_long = [False] * n
    c_short = [False] * n
    c_light_long = [False] * n
    c_light_short = [False] * n
    bear = [False] * n
    for i in range(n):
        healthy = _finite(rel_vol[i]) and rel_vol[i] > 0.4 and rel_vol[i] < 12.0
        pu = bool(
            i > 0 and _finite(v3[i]) and v3[i] > -0.4
            and _finite(v11[i]) and _finite(v11[i - 1])
            and c[i] > v11[i] and v11[i] > v11[i - 1]
        )
        bh = bool(i > 0 and _finite(hh15[i - 1]) and c[i] > hh15[i - 1])
        ms = (
            (ma20[i] - ma20[i - 3]) / ma20[i - 3] * 100.0
            if i >= 3 and _finite(ma20[i]) and _finite(ma20[i - 3]) and ma20[i - 3] != 0
            else None
        )
        mature = _finite(ms) and ms > 0
        absb = _finite(bias20[i]) and _finite(v15[i]) and bias20[i] < -10.0 and v15[i] < 20.0
        sus = bool(
            i > 0 and not absb and _finite(vol_ma5[i]) and _finite(wash_vol[i]) and _finite(wash_gain[i])
            and v[i] > vol_ma5[i] * wash_vol[i]
            and ((c[i] / c[i - 1] - 1.0) * 100.0) < wash_gain[i]
            and _finite(bias20[i]) and bias20[i] > -5.0 and mature
        )
        lock = bool(i > 0 and _finite(rel_vol[i]) and _finite(hsl_ma5[i - 1]) and rel_vol[i] < hsl_ma5[i - 1] * 0.65)
        locked = bool(
            i > 0 and _finite(vol_ma20[i]) and v[i] < vol_ma20[i] * 0.78
            and c[i] / c[i - 1] > 1.015 and bh and lock and healthy
        )
        ve = bool(_finite(vol_ma5[i]) and v[i] > vol_ma5[i] * 1.15 and healthy and not sus)
        c_long[i] = bool(pu and (ve or locked) and v4[i])

        violent = bool(
            i > 0 and _finite(vol_ma5[i]) and _finite(hsl_ma5[i])
            and v[i] > vol_ma5[i] * 1.2
            and c[i] / c[i - 1] < 0.98
            and _finite(rel_vol[i]) and rel_vol[i] > hsl_ma5[i] * 1.5
        )
        bear[i] = bool(
            i > 0 and _finite(vol_ma20[i]) and v[i] < vol_ma20[i] * 0.75
            and c[i] < c[i - 1]
            and _finite(v11[i]) and _finite(v11[i - 1])
            and c[i] < v11[i] and v11[i] < v11[i - 1]
        )
        nl = bool(i > 0 and _finite(ll12[i - 1]) and c[i] < ll12[i - 1])
        fb = bool(bear[i] and not (i > 0 and bear[i - 1]) and nl)
        c_short[i] = bool(violent or fb or sus)
        c_light_long[i] = bool(pu and not ve and not locked and v4[i] and healthy)
        sw = bool(
            i > 0 and _finite(vol_ma5[i]) and _finite(hsl_ma5[i])
            and v[i] > vol_ma5[i] * 1.1
            and c[i] < c[i - 1]
            and _finite(v11[i]) and c[i] < v11[i]
            and _finite(rel_vol[i]) and rel_vol[i] > hsl_ma5[i]
        )
        bw = bool(bear[i] and not nl)
        c_light_short[i] = bool((sw or bw) and v4[i])

    trend = [_state(t_long, t_light_long, t_short, t_light_short, i) for i in range(n)]
    momentum = [_state(m_long, m_light_long, m_short, m_light_short, i) for i in range(n)]
    accel = [_state(a_long, a_light_long, a_short, a_light_short, i) for i in range(n)]
    capital = [_state(c_long, c_light_long, c_short, c_light_short, i) for i in range(n)]
    return [
        {"trend": trend[i], "capital": capital[i], "momentum": momentum[i], "accel": accel[i]}
        for i in range(n)
    ]


def _with_anomaly(candles: list[Candle], base: list[dict[str, str]]) -> tuple[list[dict[str, str]], list[dict[str, float | int] | None]]:
    n = len(candles)
    c = [r.close for r in candles]
    o = [r.open for r in candles]
    h = [r.high for r in candles]
    l = [r.low for r in candles]
    v = [r.volume for r in candles]

    ma20, ma60, vol_ma5 = _ma(c, 20), _ma(c, 60), _ma(v, 5)
    ll13, hh13 = _llv(l, 13), _hhv(h, 13)
    var5 = [
        (c[i] - ll13[i]) / (hh13[i] - ll13[i]) * 100.0
        if _finite(ll13[i]) and _finite(hh13[i]) and hh13[i] != ll13[i]
        else None
        for i in range(n)
    ]
    var6 = _sma(var5, 4, 1)
    var7 = _sma(var6, 3, 1)
    e5 = _ema(c, 5)
    var3 = [(c[i] - e5[i]) * 100.0 / c[i] if _finite(e5[i]) and c[i] != 0 else None for i in range(n)]

    anomaly = ["GRAY"] * n
    for i in range(1, n):
        body = abs(c[i] - o[i])
        lo = min(c[i], o[i]) - l[i]
        up = h[i] - max(c[i], o[i])
        cb = (
            (c[i - 1] < o[i - 1] and c[i] > o[i] and o[i] < c[i - 1] and c[i] > o[i - 1])
            or (lo > body * 2.0 and up < body * 0.5 and c[i] > c[i - 1])
            or (c[i] > h[i - 1] and c[i] / o[i] > 1.02)
        )
        hb = (
            (_finite(ma20[i]) and _finite(ma60[i]) and ma20[i] > ma60[i])
            or (_finite(vol_ma5[i]) and (v[i] > vol_ma5[i] * 1.15 or v[i] < vol_ma5[i] * 0.65))
            or (_finite(var7[i]) and var7[i] <= 35.0)
        )
        al = cb and hb and _finite(var3[i]) and RANK[base[i]["trend"]] > 0
        all_light = cb and hb and _finite(var3[i]) and not (RANK[base[i]["trend"]] > 0)

        cs = (
            (c[i - 1] > o[i - 1] and c[i] < o[i] and o[i] > c[i - 1] and c[i] < o[i - 1])
            or (up > body * 2.0 and lo < body * 0.5 and c[i] < c[i - 1])
            or (o[i] > h[i - 1] and c[i] < o[i - 1] and c[i] < (o[i - 1] + c[i - 1]) / 2.0)
        )
        hs = (
            (_finite(ma20[i]) and _finite(ma60[i]) and ma20[i] < ma60[i])
            or (_finite(vol_ma5[i]) and (v[i] > vol_ma5[i] * 1.15 or v[i] < vol_ma5[i] * 0.65))
            or (_finite(var7[i]) and var7[i] >= 50.0)
        )
        a_short = cs and hs and _finite(var3[i])
        a_light_short = cs and hs and _finite(var3[i]) and not (RANK[base[i]["trend"]] < 0)
        anomaly[i] = (
            "LONG" if al else
            "LIGHT_LONG" if all_light else
            "SHORT" if a_short else
            "LIGHT_SHORT" if a_light_short else
            "GRAY"
        )

    rows = [{**base[i], "anomaly": anomaly[i]} for i in range(n)]
    features: list[dict[str, float | int] | None] = [None] * n
    for i in range(5, n):
        item: dict[str, float | int] = {}
        for dim in DIMS:
            item[f"{dim}_cur"] = RANK[rows[i][dim]]
            for window in (1, 3, 5):
                values = [RANK[rows[k][dim]] for k in range(i - window, i + 1)]
                item[f"{dim}_net{window}"] = values[-1] - values[0]
                item[f"{dim}_slope{window}"] = _slope(values)
                item[f"{dim}_pos{window}"] = sum(1 for x in values[1:] if x > 0)

        bullbars3 = 0
        for k in range(i - 2, i + 1):
            bullish_dims = sum(1 for dim in DIMS if RANK[rows[k][dim]] > 0)
            if bullish_dims >= 3:
                bullbars3 += 1
        item["bullbars3"] = bullbars3
        features[i] = item

    return rows, features


def _active_signals(feature: dict[str, float | int] | None) -> tuple[tuple[str, ...], tuple[str, ...]]:
    if feature is None:
        return (), ()

    buy: list[str] = []
    sell: list[str] = []

    if feature["trend_slope3"] > 0 and feature["momentum_cur"] == -2 and feature["momentum_slope5"] < 0:
        buy.append("A")
    if feature["capital_cur"] == 0 and feature["capital_net1"] < 0 and feature["accel_slope3"] > 0:
        buy.append("B")
    if (
        feature["trend_cur"] == 0
        and feature["capital_net3"] > 0
        and feature["capital_pos3"] >= 2
        and feature["capital_slope5"] > 0
        and feature["anomaly_cur"] == 0
    ):
        buy.append("C")

    if feature["trend_cur"] == 0 and feature["accel_pos5"] >= 3 and feature["bullbars3"] >= 2:
        sell.append("A")
    if feature["capital_slope5"] < 0 and feature["momentum_cur"] >= 1 and feature["anomaly_net1"] < 0:
        sell.append("B")
    if feature["momentum_cur"] == 2 and feature["anomaly_net3"] > 0 and feature["bullbars3"] >= 2:
        sell.append("C")

    return tuple(buy), tuple(sell)


def evaluate_candles(rows: Iterable[Any]) -> list[BarEvaluation]:
    candles = normalize_candles(rows)
    base = _base_states(candles)
    states, features = _with_anomaly(candles, base)

    active: list[tuple[tuple[str, ...], tuple[str, ...]]] = [
        _active_signals(features[i]) for i in range(len(candles))
    ]
    out: list[BarEvaluation] = []
    for i, candle in enumerate(candles):
        buy_active, sell_active = active[i]
        previous_buy = set(active[i - 1][0]) if i > 0 else set()
        previous_sell = set(active[i - 1][1]) if i > 0 else set()
        buy_onsets = tuple(x for x in buy_active if x not in previous_buy)
        sell_onsets = tuple(x for x in sell_active if x not in previous_sell)
        out.append(
            BarEvaluation(
                index=i,
                open_time=candle.open_time,
                states=dict(states[i]),
                buy_active=buy_active,
                sell_active=sell_active,
                buy_onsets=buy_onsets,
                sell_onsets=sell_onsets,
                features=features[i],
            )
        )
    return out


def latest_evaluation(rows: Iterable[Any]) -> BarEvaluation:
    result = evaluate_candles(rows)
    if not result:
        raise ValueError("no candles")
    return result[-1]
