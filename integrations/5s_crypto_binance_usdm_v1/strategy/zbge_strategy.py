"""Causal implementation of the owner's ZBGE B/S indicator.

All signals use the latest *closed* candle; no future bars, no repaint and
no chart annotation is treated as an execution confirmation.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any


@dataclass(frozen=True)
class ZBGEPoint:
    open_time: int
    close: float
    trend: float | None
    absorption: float | None
    yellow: bool
    smile: bool
    smile_count: int
    follow_main: bool
    buy: bool
    sell_a: bool
    sell_b: bool
    # Additional plot-only values; never read these fields in trading decisions.
    z2: float | None = None
    cyan: float | None = None
    red: float | None = None
    gray: float | None = None
    pink: bool = False
    rush: float | None = None
    rush_red: bool = False
    big_bull: bool = False

    @property
    def sell(self) -> bool:
        return self.sell_a or self.sell_b


def _finite(value: float) -> bool:
    return math.isfinite(value)


def _sma(values: list[float], n: int) -> list[float]:
    """TDX SMA(X,N,1): first finite source value seeds the recurrence."""
    result: list[float] = []
    previous = math.nan
    for value in values:
        if _finite(value):
            previous = value if not _finite(previous) else (
                value + (n - 1) * previous
            ) / n
        result.append(previous)
    return result


def _ema(values: list[float], n: int) -> list[float]:
    result: list[float] = []
    previous = math.nan
    for value in values:
        if _finite(value):
            previous = value if not _finite(previous) else (
                2 * value + (n - 1) * previous
            ) / (n + 1)
        result.append(previous)
    return result


def _rolling(values: list[float], n: int, *, minimum: bool) -> list[float]:
    result: list[float] = []
    for i in range(len(values)):
        window = [v for v in values[max(0, i - n + 1):i + 1] if _finite(v)]
        result.append(
            (min(window) if minimum else max(window)) if window else math.nan
        )
    return result


def _cross_above(a: list[float], b: list[float], index: int) -> bool:
    return (
        index > 0
        and all(_finite(x) for x in (a[index], b[index], a[index - 1], b[index - 1]))
        and a[index] > b[index]
        and a[index - 1] <= b[index - 1]
    )


def _safe_ratio(numerator: float, denominator: float) -> float:
    return (
        numerator / denominator
        if _finite(numerator) and _finite(denominator) and denominator != 0
        else math.nan
    )


def evaluate_zbge(rows: list[Any]) -> list[ZBGEPoint]:
    """Consume Binance kline arrays [open_time, open, high, low, close, ...]."""
    if not rows:
        return []
    times = [int(row[0]) for row in rows]
    high = [float(row[2]) for row in rows]
    low = [float(row[3]) for row in rows]
    close = [float(row[4]) for row in rows]
    if any(not _finite(v) or v <= 0 for v in high + low + close):
        raise ValueError("ZBGE 历史 K 线包含无效价格")

    lo55 = _rolling(low, 55, minimum=True)
    hi55 = _rolling(high, 55, minimum=False)
    z1 = [
        100 * _safe_ratio(c - lo55[i], hi55[i] - lo55[i])
        for i, c in enumerate(close)
    ]
    inner = _sma(_sma(z1, 5), 3)
    z2 = _ema(
        [
            (3 * val - 2 * inner[i]) if _finite(val) and _finite(inner[i]) else math.nan
            for i, val in enumerate(_sma(z1, 5))
        ],
        3,
    )
    trend = [x - 10 if _finite(x) else math.nan for x in z2]

    low_change = [math.nan] + [low[i] - low[i - 1] for i in range(1, len(low))]
    abs_avg = _sma([abs(x) for x in low_change], 3)
    rising_avg = _sma([max(0.0, x) for x in low_change], 3)
    z10 = _ema(
        [1000 * _safe_ratio(abs_avg[i], rising_avg[i]) for i in range(len(low))],
        3,
    )
    lo38 = _rolling(low, 38, minimum=True)
    hi10_38 = _rolling(z10, 38, minimum=False)
    lo13 = _rolling(low, 13, minimum=True)
    hi10_13 = _rolling(z10, 13, minimum=False)
    z8_source = [
        (z10[i] + 2 * hi10_38[i]) / 2 if low[i] <= lo38[i] else 0.0
        for i in range(len(low))
    ]
    z8 = [min(100.0, value / 618.0) for value in _ema(z8_source, 3)]
    z14_source = [
        (z10[i] + 2 * hi10_13[i]) / 2 if low[i] <= lo13[i] else 0.0
        for i in range(len(low))
    ]
    z14 = [min(500.0, value / 618.0) for value in _ema(z14_source, 3)]

    lo9 = _rolling(low, 9, minimum=True)
    hi9 = _rolling(high, 9, minimum=False)
    z27 = [
        100 * _safe_ratio(c - lo9[i], hi9[i] - lo9[i])
        for i, c in enumerate(close)
    ]
    z28 = _sma(z27, 3)
    z29 = _sma(z28, 3)
    z18 = [3 * z28[i] - 2 * z29[i] for i in range(len(close))]

    # 冲顶: 2/ZBGE26-2 (ZBGE26 = SMA(13-period close drawdown, 5, 1)).
    lo_close13 = _rolling(close, 13, minimum=True)
    hi_close13 = _rolling(close, 13, minimum=False)
    z26 = _sma([
        _safe_ratio(hi_close13[i] - c, hi_close13[i] - lo_close13[i])
        for i, c in enumerate(close)
    ], 5)

    points: list[ZBGEPoint] = []
    last_cross_up: int | None = None
    smile_count = 0
    last_kdj_down: int | None = None
    last_kdj_up: int | None = None
    for i in range(len(close)):
        yellow = (
            i >= 2
            and z14[i] > 1
            and z18[i] > z18[i - 1]
            and z18[i - 1] < z18[i - 2]
        )
        buy = bool(yellow and trend[i] < 20 and z8[i] > 15)
        smile = bool(i > 0 and z2[i] > 85 and z2[i] > z2[i - 1])
        smile_count = smile_count + 1 if smile else 0
        top_main = _cross_above(z28, z27, i) and z27[i] > 50
        # BARSLAST(CROSS(ZBGE27,ZBGE28)) includes the current bar.
        if _cross_above(z27, z28, i):
            last_cross_up = i
        follow = bool(
            top_main and last_cross_up is not None and i - last_cross_up >= 4
        )
        sell_a = bool(follow and trend[i] > 75)
        sell_b = smile_count == 3

        # Trend-bull requires the K/D cross-up and a recent cross-down.
        if _cross_above(z29, z28, i):
            last_kdj_down = i
        kdj_up = _cross_above(z28, z29, i)
        if kdj_up:
            last_kdj_up = i
        big_bull = bool(
            kdj_up and z28[i] < 20
            and last_kdj_up is not None and i - last_kdj_up < 9
            and last_kdj_down is not None and i - last_kdj_down < 9
        )
        # The original cyan/red/gray absorption columns all start at zero.
        cyan = z2[i] if _finite(z2[i]) and 0 < z2[i] <= 14 else None
        red = z8[i] if _finite(z8[i]) and z8[i] > 0 else None
        gray = abs(z14[i]) if _finite(z14[i]) and z14[i] > -120 and abs(z14[i]) > 0 else None
        pink = bool(
            i >= 2 and 0.1 < z14[i] < 1
            and z18[i] > z18[i - 2] and z18[i - 1] < z18[i - 2]
        )
        rush = (2 / z26[i] - 2) if _finite(z26[i]) and z26[i] != 0 else math.nan
        rush_red = bool(_finite(z26[i]) and 0 < z26[i] < 1 / 13)
        points.append(
            ZBGEPoint(
                open_time=times[i],
                close=close[i],
                trend=trend[i] if _finite(trend[i]) else None,
                absorption=z8[i] if _finite(z8[i]) else None,
                yellow=yellow,
                smile=smile,
                smile_count=smile_count,
                follow_main=follow,
                buy=buy,
                sell_a=sell_a,
                sell_b=sell_b,
                z2=z2[i] if _finite(z2[i]) else None,
                cyan=cyan,
                red=red,
                gray=gray,
                pink=pink,
                rush=rush if _finite(rush) and rush > 0 else None,
                rush_red=rush_red,
                big_bull=big_bull,
            )
        )
    return points


def chart_snapshot(rows: list[Any]) -> dict[str, object]:
    points = evaluate_zbge(rows)
    latest = points[-1] if points else None
    return {
        "trend": latest.trend if latest else None,
        "absorption": latest.absorption if latest else None,
        "yellow": latest.yellow if latest else False,
        "smile_count": latest.smile_count if latest else 0,
        "buy": latest.buy if latest else False,
        "sell_a": latest.sell_a if latest else False,
        "sell_b": latest.sell_b if latest else False,
    }
