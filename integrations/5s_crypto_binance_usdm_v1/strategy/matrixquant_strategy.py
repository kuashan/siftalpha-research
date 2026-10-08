"""MatrixQuant PAI default formula, ported from the preserved original Pine v6.

Scope: PAI = ((SMA3(Stoch20(close,high,low))-50)/50)
              * Stoch20(population_stddev20(close)).
No HTF/Laguerre/WT trading confirmation: these are the frozen PAI +5/-5
entry/exit threshold rules. This module never sends orders.
Original © MatrixQuant, Mozilla Public License 2.0.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, sqrt, fsum
from typing import Any, Iterable

PAI_LOOKBACK = 20
PAI_SMOOTH = 3
PAI_THRESHOLD = 5.0
PAI_SOURCE_VERSION = "MatrixQuant-PAI-default-stoch20-sma3-stdev20-v1"


@dataclass(frozen=True)
class PAIPoint:
    open_time: int
    raw: float | None
    buy: bool
    sell: bool


def _as_row(row: Any) -> tuple[int, float, float, float]:
    if isinstance(row, dict):
        timestamp = row.get("open_time", row.get("openTime"))
        close, high, low = (row[key] for key in ("close", "high", "low"))
    else:
        timestamp, high, low, close = row[0], row[2], row[3], row[4]
    ts, h, l, c = int(timestamp), float(high), float(low), float(close)
    if not all(isfinite(x) and x > 0 for x in (h, l, c)) or h < max(l, c):
        raise ValueError("MatrixQuant OHLC 数据不合法")
    return ts, h, l, c


def _stoch(price: list[float | None], high: list[float | None],
           low: list[float | None], length: int) -> list[float | None]:
    out: list[float | None] = [None] * len(price)
    for i in range(length - 1, len(price)):
        p = price[i]
        highs = high[i + 1 - length:i + 1]
        lows = low[i + 1 - length:i + 1]
        if p is None or any(v is None for v in highs) or any(v is None for v in lows):
            continue
        hi = max(highs)
        lo = min(lows)
        if hi > lo:
            out[i] = 100.0 * (p - lo) / (hi - lo)
    return out


def _sma(values: list[float | None], length: int) -> list[float | None]:
    out: list[float | None] = [None] * len(values)
    for i in range(length - 1, len(values)):
        window = values[i + 1 - length:i + 1]
        if all(v is not None for v in window):
            out[i] = fsum(window) / length
    return out


def _stdev(values: list[float], length: int) -> list[float | None]:
    out: list[float | None] = [None] * len(values)
    for i in range(length - 1, len(values)):
        window = values[i + 1 - length:i + 1]
        mean = fsum(window) / length
        out[i] = sqrt(fsum((v - mean) ** 2 for v in window) / length)
    return out


def evaluate_pai(rows: Iterable[Any]) -> list[PAIPoint]:
    records = [_as_row(row) for row in rows]
    if not records:
        return []
    times = [r[0] for r in records]
    if any(b <= a for a, b in zip(times, times[1:])):
        raise ValueError("MatrixQuant K 线必须按时间升序且没有重复")
    high = [r[1] for r in records]
    low = [r[2] for r in records]
    close = [r[3] for r in records]
    momentum_stoch = _stoch(close, high, low, PAI_LOOKBACK)
    momentum_sma = _sma(momentum_stoch, PAI_SMOOTH)
    dispersion = _stdev(close, PAI_LOOKBACK)
    volatility_stoch = _stoch(dispersion, dispersion, dispersion, PAI_LOOKBACK)
    raw: list[float | None] = [
        ((m - 50.0) / 50.0) * v if m is not None and v is not None else None
        for m, v in zip(momentum_sma, volatility_stoch)
    ]
    return [
        PAIPoint(
            open_time=times[i], raw=value,
            buy=(i > 0 and value is not None and raw[i - 1] is not None
                 and raw[i - 1] <= PAI_THRESHOLD < value),
            sell=(i > 0 and value is not None and raw[i - 1] is not None
                  and raw[i - 1] >= -PAI_THRESHOLD > value),
        )
        for i, value in enumerate(raw)
    ]


def chart_snapshot(rows: Iterable[Any]) -> dict[str, object]:
    points = evaluate_pai(rows)
    if not points:
        return {"analysis_error": "K 线为空"}
    last = points[-1]
    return {
        "pai_raw": last.raw,
        "buy_cross_up5": last.buy,
        "sell_cross_down_minus5": last.sell,
        "source_bar_open_time": last.open_time,
        "formula_version": PAI_SOURCE_VERSION,
        "state": "多头动量" if last.raw is not None and last.raw > 5 else (
            "空头动量" if last.raw is not None and last.raw < -5 else "震荡"
        ),
        "analysis_bar_count": len(points),
    }
