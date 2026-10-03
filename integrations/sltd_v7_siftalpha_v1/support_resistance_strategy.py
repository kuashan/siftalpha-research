from __future__ import annotations

"""Independent short/long support-resistance overlay.

This module is a direct Python port of the user-provided TongdaXin formula for
only four DRAWLINE outputs:
- short pressure (VAR1=3)
- short support  (VAR1=3)
- long pressure  (VAR1_L=7)
- long support   (VAR1_L=7)

Important: BACKSET is intentionally preserved.  Therefore this is a visual
structure overlay that can repaint historical turning points as later bars
arrive.  It does not emit trading signals and does not modify V7/E/5s/Chan.
"""

from math import isfinite
from typing import Iterable, Sequence

SUPPORT_RESISTANCE_ID = "support_resistance"
SUPPORT_RESISTANCE_VERSION = "顺势 v1"
SUPPORT_RESISTANCE_SOURCE = "USER_TDX_FORMULA_DIRECT_PORT_VAR3_VAR7"
SHORT_PERIOD = 3
LONG_PERIOD = 7

SUPPORT_RESISTANCE_RULES = {
    "BUY": (),
    "HOLD": (),
    "WAIT": (),
    "SELL": (),
}


def _clean_bars(candles: Iterable[dict]) -> list[dict]:
    out: list[dict] = []
    last_date = ""
    for raw in candles:
        date = str(raw.get("date") or "")
        if not date:
            raise ValueError("K 线日期不能为空")
        if last_date and date <= last_date:
            raise ValueError("K 线必须按时间严格递增排列")
        o = float(raw["open"])
        h = float(raw["high"])
        l = float(raw["low"])
        c = float(raw["close"])
        v = float(raw.get("volume") or 0.0)
        if not all(isfinite(x) for x in (o, h, l, c, v)):
            raise ValueError(f"{date}: K 线包含非有限数")
        if h < l:
            raise ValueError(f"{date}: 最高价小于最低价")
        out.append(
            {
                "date": date,
                "open": o,
                "high": h,
                "low": l,
                "close": c,
                "volume": v,
            }
        )
        last_date = date
    if len(out) < 20:
        raise ValueError("长短支压至少需要 20 根已结束 K 线")
    return out


def _ref(values: Sequence, n: int, default=None) -> list:
    return [default if i < n else values[i - n] for i in range(len(values))]


def _rolling_extreme(values: Sequence[float], n: int, *, high: bool) -> list[float]:
    out: list[float] = []
    for i in range(len(values)):
        window = values[max(0, i - n + 1) : i + 1]
        out.append(max(window) if high else min(window))
    return out


def _filter(signal: Sequence[bool], n: int) -> list[bool]:
    """TongdaXin FILTER: after a true bar, suppress the following N bars."""
    out = [False] * len(signal)
    blocked_through = -1
    for i, value in enumerate(signal):
        if bool(value) and i > blocked_through:
            out[i] = True
            blocked_through = i + int(n)
    return out


def _backset(
    signal: Sequence[bool],
    periods: int | Sequence[int | None],
) -> list[bool]:
    """TongdaXin BACKSET: set current plus previous N-1 bars to true."""
    out = [False] * len(signal)
    dynamic = not isinstance(periods, int)
    for i, value in enumerate(signal):
        if not bool(value):
            continue
        n = periods[i] if dynamic else periods
        if n is None or int(n) <= 0:
            continue
        start = max(0, i - int(n) + 1)
        for j in range(start, i + 1):
            out[j] = True
    return out


def _rising_edge(signal: Sequence[bool]) -> list[bool]:
    out: list[bool] = []
    previous = False
    for value in signal:
        current = bool(value)
        out.append(current and not previous)
        previous = current
    return out


def _barslast(signal: Sequence[bool]) -> list[int | None]:
    out: list[int | None] = []
    last: int | None = None
    for i, value in enumerate(signal):
        if bool(value):
            last = i
        out.append(None if last is None else i - last)
    return out


def _count_dynamic(
    signal: Sequence[bool],
    periods: Sequence[int | None],
) -> list[int]:
    out: list[int] = []
    for i, n in enumerate(periods):
        if n is None or int(n) <= 0:
            out.append(0)
            continue
        start = max(0, i - int(n) + 1)
        out.append(sum(1 for x in signal[start : i + 1] if bool(x)))
    return out


def _extreme_bars_dynamic(
    values: Sequence[float],
    periods: Sequence[int | None],
    *,
    high: bool,
) -> list[int | None]:
    """HHVBARS/LLVBARS with a dynamic lookback; nearest tie wins."""
    out: list[int | None] = []
    for i, n in enumerate(periods):
        if n is None or int(n) <= 0:
            out.append(None)
            continue
        start = max(0, i - int(n) + 1)
        window = values[start : i + 1]
        target = max(window) if high else min(window)
        # "上一高/低点到当前的周期数": use the nearest equal extreme.
        extreme_index = max(
            j for j in range(start, i + 1) if values[j] == target
        )
        out.append(i - extreme_index)
    return out


def _line_from_markers(
    marker_a: Sequence[bool],
    marker_b: Sequence[bool],
    prices: Sequence[float],
) -> tuple[list[float | None], dict | None]:
    a_indices = [i for i, x in enumerate(marker_a) if x]
    b_indices = [i for i, x in enumerate(marker_b) if x]
    if not a_indices or not b_indices:
        return [None] * len(prices), None

    a = a_indices[-1]
    b = b_indices[-1]
    if b <= a:
        return [None] * len(prices), None

    pa = float(prices[a])
    pb = float(prices[b])
    slope = (pb - pa) / float(b - a)
    line: list[float | None] = [None] * len(prices)
    # DRAWLINE(...,1): connect the two anchors and extend to the right.
    for i in range(a, len(prices)):
        line[i] = pa + slope * float(i - a)

    return line, {
        "start_index": a,
        "end_index": b,
        "start_price": pa,
        "end_price": pb,
        "slope_per_bar": slope,
    }


def _period_overlay(highs: list[float], lows: list[float], n: int) -> dict:
    size = len(highs)

    high_window = _rolling_extreme(highs, 2 * n + 1, high=True)
    low_window = _rolling_extreme(lows, 2 * n + 1, high=False)

    var2 = [
        i >= n and highs[i - n] == high_window[i]
        for i in range(size)
    ]
    var3 = _filter(var2, n)
    var4 = _backset(var3, n + 1)
    var5 = _filter(var4, n)

    var6 = [
        i >= n and lows[i - n] == low_window[i]
        for i in range(size)
    ]
    var7 = _filter(var6, n)
    var8 = _backset(var7, n + 1)
    var9 = _filter(var8, n)

    low_2n = _rolling_extreme(lows, 2 * n, high=False)
    high_2n = _rolling_extreme(highs, 2 * n, high=True)
    ref_low = _ref(low_2n, 1)
    ref_high = _ref(high_2n, 1)
    var10 = [
        None
        if ref_low[i] is None or ref_high[i] is None
        else (float(ref_low[i]) + float(ref_high[i])) / 2.0
        for i in range(size)
    ]
    var11 = [(highs[i] + lows[i]) / 2.0 for i in range(size)]

    var12 = [
        (
            var5[i]
            and not (
                var9[i]
                and var10[i] is not None
                and float(var10[i]) >= var11[i]
            )
        )
        or i == size - 1
        or i == 0
        for i in range(size)
    ]
    var13 = [
        var9[i]
        and not (
            var5[i]
            and var10[i] is not None
            and float(var10[i]) < var11[i]
        )
        for i in range(size)
    ]
    var14 = [
        var5[i]
        and not (
            var9[i]
            and var10[i] is not None
            and float(var10[i]) >= var11[i]
        )
        for i in range(size)
    ]

    var15 = [
        None if value is None else int(value) + 1
        for value in _ref(_barslast(var12), 1)
    ]
    count13 = _count_dynamic(var13, var15)
    low_candidates = [
        lows[i] if var13[i] else 10000.0 for i in range(size)
    ]
    low_bars = _extreme_bars_dynamic(
        low_candidates,
        var15,
        high=False,
    )
    var16 = _backset(
        [var12[i] and count13[i] > 0 for i in range(size)],
        low_bars,
    )
    var17 = _rising_edge(var16)
    var18 = _backset(var17, 2)
    var19 = _rising_edge(var18)

    var20 = [
        var19[i] or i == size - 1 or i == 0
        for i in range(size)
    ]
    var21 = [
        None if value is None else int(value) + 1
        for value in _ref(_barslast(var20), 1)
    ]
    count14 = _count_dynamic(var14, var21)
    high_candidates = [
        highs[i] if var14[i] else 0.0 for i in range(size)
    ]
    high_bars = _extreme_bars_dynamic(
        high_candidates,
        var21,
        high=True,
    )
    var22 = _backset(
        [var20[i] and count14[i] > 0 for i in range(size)],
        high_bars,
    )
    var23 = _rising_edge(var22)
    var24 = _backset(var23, 2)
    var25 = _rising_edge(var24)

    barslast25 = _barslast(var25)
    last_high_span: list[int | None] = [None] * size
    if barslast25[-1] is not None:
        last_high_span[-1] = int(barslast25[-1]) + 1
    var26 = _backset([i == size - 1 for i in range(size)], last_high_span)
    var27 = _rising_edge(var26)

    barslast19 = _barslast(var19)
    last_low_span: list[int | None] = [None] * size
    if barslast19[-1] is not None:
        last_low_span[-1] = int(barslast19[-1]) + 1
    var28 = _backset([i == size - 1 for i in range(size)], last_low_span)
    var29 = _rising_edge(var28)

    var30 = _backset(
        var27,
        [
            None if value is None else int(value) + 2
            for value in _ref(barslast25, 1)
        ],
    )
    var31 = _rising_edge(var30)

    var32 = _backset(
        var29,
        [
            None if value is None else int(value) + 2
            for value in _ref(barslast19, 1)
        ],
    )
    var33 = _rising_edge(var32)

    pressure, pressure_anchor = _line_from_markers(
        var31,
        var27,
        highs,
    )
    support, support_anchor = _line_from_markers(
        var33,
        var29,
        lows,
    )

    return {
        "pressure": pressure,
        "support": support,
        "pressure_anchor": pressure_anchor,
        "support_anchor": support_anchor,
        "high_pivots": [i for i, x in enumerate(var25) if x],
        "low_pivots": [i for i, x in enumerate(var19) if x],
    }


def compute_support_resistance(candles: Iterable[dict]) -> dict:
    bars = _clean_bars(candles)
    highs = [float(x["high"]) for x in bars]
    lows = [float(x["low"]) for x in bars]
    short = _period_overlay(highs, lows, SHORT_PERIOD)
    long = _period_overlay(highs, lows, LONG_PERIOD)
    return {
        "bars": bars,
        "short": short,
        "long": long,
    }


def _latest_or_none(values: Sequence[float | None]) -> float | None:
    for value in reversed(values):
        if value is not None and isfinite(float(value)):
            return float(value)
    return None


def analyze_support_resistance(
    symbol: str,
    candles: Iterable[dict],
    *,
    display_limit: int = 300,
    timeframe: str = "1d",
) -> dict:
    calc = compute_support_resistance(candles)
    bars: list[dict] = calc["bars"]
    short = calc["short"]
    long = calc["long"]

    limit = max(80, min(int(display_limit), 500))
    start = max(0, len(bars) - limit)
    chart: list[dict] = []
    for i in range(start, len(bars)):
        bar = bars[i]
        chart.append(
            {
                **bar,
                "state": "OTHER",
                "state_zh": "顺势",
                "position": 0.0,
                "risk_armed": False,
                "sr_short_pressure": short["pressure"][i],
                "sr_short_support": short["support"][i],
                "sr_long_pressure": long["pressure"][i],
                "sr_long_support": long["support"][i],
            }
        )

    latest = bars[-1]
    return {
        "strategy": {
            "id": SUPPORT_RESISTANCE_ID,
            "selector_label": "顺势",
            "version": SUPPORT_RESISTANCE_VERSION,
            "source_commit": SUPPORT_RESISTANCE_SOURCE,
            "active_rule_count": 0,
            "active_rules": SUPPORT_RESISTANCE_RULES,
            "active_rules_zh": {
                "BUY": [],
                "HOLD": [],
                "WAIT": [],
                "SELL": [],
            },
            "position_policy": "DISPLAY_ONLY",
            "position_policy_zh": "仅显示四条支撑/压力线，不产生买卖信号",
            "hard_exit": "NONE",
            "hard_exit_zh": "无",
            "display_candles": limit,
            "timeframe": str(timeframe),
            "bar_close_contract": "VISUAL_OVERLAY_WITH_BACKSET_REPAINT",
            "bar_close_contract_zh": "保留原公式 BACKSET 语义；历史转折点可能随后续 K 线重新确认",
            "rules_title_zh": "顺势 · 四线显示",
            "policy_title_zh": "顺势独立可视化策略",
            "summary_state_label_zh": "支压结构",
            "policy_steps_zh": [],
            "repainting": True,
            "short_period": SHORT_PERIOD,
            "long_period": LONG_PERIOD,
        },
        "snapshot": {
            "symbol": symbol,
            "latest_date": str(latest["date"]),
            "latest_close": float(latest["close"]),
            "state": "OTHER",
            "state_zh": "四线显示",
            "run_age": None,
            "age_bucket": "BACKSET · 可重绘",
            "origin": None,
            "resolved_action": "NONE",
            "resolved_action_zh": "无交易信号",
            "rule_ids": [],
            "rule_names_zh": [],
            "position_fraction": 0.0,
            "risk_state": "NORMAL",
            "risk_state_zh": "仅显示",
            "risk_sub_zh": "不参与 V7/E/5s/缠论买卖逻辑",
            "next_action": "仅观察短压、短支、长压、长支四条线",
            "sr_short_pressure": _latest_or_none(short["pressure"]),
            "sr_short_support": _latest_or_none(short["support"]),
            "sr_long_pressure": _latest_or_none(long["pressure"]),
            "sr_long_support": _latest_or_none(long["support"]),
        },
        "support_resistance": {
            "short_period": SHORT_PERIOD,
            "long_period": LONG_PERIOD,
            "short_pressure_anchor": short["pressure_anchor"],
            "short_support_anchor": short["support_anchor"],
            "long_pressure_anchor": long["pressure_anchor"],
            "long_support_anchor": long["support_anchor"],
            "repainting": True,
        },
        "chart": chart,
        "markers": [],
        "events": [],
    }
