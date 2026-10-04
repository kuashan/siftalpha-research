from __future__ import annotations

"""SLTD E 独立策略。

E 与冻结的 SLTD V7 12 条策略并存，但不修改 V7 的任何冻结规则。

用户确认的 E v1 规则：
- 条件1：蓝色/灰色区域，所选周期 K 线收盘价向下跌破 ZD1，下一根所选周期开盘 +25 个百分点。
- 条件2：条件1出现时，最新已完成的大周期 K 线收盘价也位于其 ZD1 下方，再 +25 个百分点。
- 条件3：条件1已经实际执行后，后续价格触碰 GZB3-GZB4 灰带，再 +25 个百分点。
- 每轮持仓周期内条件1/2/3各最多实际执行一次，最高目标仓位 75%；完全清仓后重置。
- 卖出1：任意颜色，收盘价向上突破 ZK1，减 50 个百分点。
- 卖出2：在退出序列已经开始，或同一根 K 线同时发生 ZK1 收盘突破时，价格触碰 BS，上一级动作被覆盖，
  本根只执行最高级别动作：减 25 个百分点。
- 卖出3：在退出序列已经开始，或同一根 K 线同时发生 ZK1 收盘突破时，价格触碰 GZB3-GZB4，
  本根只执行最高级别动作：全部清仓。
- 卖出4：退出序列开始后，若尚未按更高条件清仓而最新收盘价跌回 ZK1 下方，全部清仓。
- 所有信号只使用已结束 K 线确认，在下一根所选周期 K 线开盘执行。
"""

from datetime import datetime, timezone
import time
from typing import Iterable
from zoneinfo import ZoneInfo

from strategy import (
    STATE_NAMES_ZH,
    _validate_candles,
    build_ledger,
)

E_STRATEGY_ID = "e"
E_STRATEGY_VERSION = "SLTD E v1"
E_SOURCE = "USER_CONFIRMED_2026-10-02"
E_MAX_POSITION = 0.75
E_MIN_WARMUP_BARS = 120

HIGHER_TIMEFRAME_MAP = {
    "5m": "20m",
    "15m": "1h",
    "30m": "2h",
    "1h": "4h",
    "4h": "1d",
    "1d": "5d",
    "5d": "20d",
}

E_RULES = {
    "BUY": (
        "E_BUY_1_PRIMARY_CLOSE_BREAK_BELOW_ZD1",
        "E_BUY_2_HIGHER_CLOSE_BELOW_ZD1",
        "E_BUY_3_TOUCH_GZB_BAND",
    ),
    "HOLD": (),
    "WAIT": (),
    "SELL": (
        "E_SELL_1_PRIMARY_CLOSE_BREAK_ABOVE_ZK1_MINUS_50PP",
        "E_SELL_2_TOUCH_BS_MINUS_25PP",
        "E_SELL_3_TOUCH_GZB_BAND_FULL_EXIT",
        "E_SELL_4_CLOSE_BACK_BELOW_ZK1_FULL_EXIT",
    ),
}

E_RULE_NAMES_ZH = {
    "E_BUY_1_PRIMARY_CLOSE_BREAK_BELOW_ZD1": "条件1：蓝色/灰色区域，收盘价跌破内下轨 ZD1，买入 25 个百分点",
    "E_BUY_2_HIGHER_CLOSE_BELOW_ZD1": "条件2：同一时刻大周期收盘也位于其 ZD1 下方，再买入 25 个百分点",
    "E_BUY_3_TOUCH_GZB_BAND": "条件3：条件1已执行后继续下跌触碰 GZB3-GZB4 灰带，再买入 25 个百分点",
    "E_SELL_1_PRIMARY_CLOSE_BREAK_ABOVE_ZK1_MINUS_50PP": "卖出1：任意颜色，收盘价突破内上轨 ZK1，减 50 个百分点",
    "E_SELL_2_TOUCH_BS_MINUS_25PP": "卖出2：退出序列中触碰上外轨 BS，减 25 个百分点",
    "E_SELL_3_TOUCH_GZB_BAND_FULL_EXIT": "卖出3：退出序列中继续上涨触碰 GZB3-GZB4 灰带，全部清仓",
    "E_SELL_4_CLOSE_BACK_BELOW_ZK1_FULL_EXIT": "卖出4：退出序列中收盘价跌回 ZK1 下方，全部清仓",
}

ACTION_NAMES_ZH = {
    "BUY": "买入",
    "SELL": "卖出",
    "HARD_EXIT": "全部清仓",
    "HOLD": "持有",
    "NONE": "无新动作",
}


def higher_timeframe(timeframe: str) -> str:
    tf = str(timeframe or "").strip().lower()
    if tf not in HIGHER_TIMEFRAME_MAP:
        raise ValueError(f"E 策略暂不支持周期：{tf}")
    return HIGHER_TIMEFRAME_MAP[tf]


def _copy_validated(candles: Iterable[dict]) -> list[dict]:
    raw = [dict(x) for x in candles]
    validated = _validate_candles(raw)
    out: list[dict] = []
    for src, clean in zip(raw, validated):
        row = dict(clean)
        if src.get("open_time") is not None:
            row["open_time"] = int(src["open_time"])
        else:
            text = str(row["date"])
            try:
                if "T" in text:
                    dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
                else:
                    dt = datetime.strptime(text[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
                row["open_time"] = int(dt.timestamp())
            except Exception:
                row["open_time"] = len(out)
        out.append(row)
    return out


def _zone(market_meta: dict | None):
    name = str((market_meta or {}).get("exchange_timezone") or "UTC")
    try:
        return ZoneInfo(name)
    except Exception:
        return timezone.utc


def _open_time_epoch_seconds(value: int | float) -> float:
    """Convert only for calendar/timezone bucketing; preserve source open_time elsewhere.

    Binance uses epoch milliseconds. Existing stock providers use epoch seconds.
    """
    raw = float(value)
    return raw / 1000.0 if abs(raw) >= 10_000_000_000 else raw


def _aggregate_chunk(chunk: list[tuple[int, dict]], label: str) -> dict:
    first_i, first = chunk[0]
    last_i, last = chunk[-1]
    return {
        "date": str(first["date"]),
        "open_time": int(first["open_time"]),
        "open": float(first["open"]),
        "high": max(float(x["high"]) for _, x in chunk),
        "low": min(float(x["low"]) for _, x in chunk),
        "close": float(last["close"]),
        "volume": sum(float(x.get("volume") or 0.0) for _, x in chunk),
        "_source_start_index": first_i,
        "_source_end_index": last_i,
        "_aggregate_label": label,
    }


def _aggregate_intraday_factor(
    bars: list[dict],
    factor: int,
    market_meta: dict | None,
    label: str,
) -> list[dict]:
    tz = _zone(market_meta)
    by_day: dict[object, list[tuple[int, dict]]] = {}
    for i, bar in enumerate(bars):
        day = datetime.fromtimestamp(_open_time_epoch_seconds(bar["open_time"]), tz=tz).date()
        by_day.setdefault(day, []).append((i, bar))

    if not by_day:
        return []

    days = sorted(by_day)
    last_day = days[-1]
    regular_end = (market_meta or {}).get("regular_market_end")
    try:
        regular_end_i = int(regular_end) if regular_end is not None else None
    except Exception:
        regular_end_i = None
    session_closed = regular_end_i is not None and int(time.time()) >= regular_end_i

    out: list[dict] = []
    for day in days:
        rows = sorted(by_day[day], key=lambda x: int(x[1]["open_time"]))
        for offset in range(0, len(rows), factor):
            chunk = rows[offset : offset + factor]
            if len(chunk) == factor:
                out.append(_aggregate_chunk(chunk, label))
                continue
            # 历史交易日的尾段在收盘后视为该高周期的最后一个短 K；
            # 当前交易日只有确认收盘后才能使用尾段，避免大周期偷看未来。
            if day != last_day or session_closed:
                out.append(_aggregate_chunk(chunk, label))
    return out


def _aggregate_session_day(
    bars: list[dict],
    market_meta: dict | None,
    label: str,
) -> list[dict]:
    tz = _zone(market_meta)
    by_day: dict[object, list[tuple[int, dict]]] = {}
    for i, bar in enumerate(bars):
        day = datetime.fromtimestamp(int(bar["open_time"]), tz=tz).date()
        by_day.setdefault(day, []).append((i, bar))

    if not by_day:
        return []
    days = sorted(by_day)
    last_day = days[-1]
    regular_end = (market_meta or {}).get("regular_market_end")
    try:
        regular_end_i = int(regular_end) if regular_end is not None else None
    except Exception:
        regular_end_i = None
    session_closed = regular_end_i is not None and int(time.time()) >= regular_end_i

    out: list[dict] = []
    for day in days:
        if day == last_day and not session_closed:
            continue
        chunk = sorted(by_day[day], key=lambda x: int(x[1]["open_time"]))
        if chunk:
            out.append(_aggregate_chunk(chunk, label))
    return out


def _aggregate_fixed_factor(bars: list[dict], factor: int, label: str) -> list[dict]:
    out: list[dict] = []
    indexed = list(enumerate(bars))
    for offset in range(0, len(indexed), factor):
        chunk = indexed[offset : offset + factor]
        if len(chunk) != factor:
            break
        out.append(_aggregate_chunk(chunk, label))
    return out


def build_higher_bars(
    candles: Iterable[dict],
    timeframe: str,
    market_meta: dict | None = None,
) -> tuple[str, list[dict]]:
    bars = _copy_validated(candles)
    tf = str(timeframe).lower()
    higher = higher_timeframe(tf)
    if tf in {"5m", "15m", "30m", "1h"}:
        return higher, _aggregate_intraday_factor(bars, 4, market_meta, higher)
    if tf == "4h":
        return higher, _aggregate_session_day(bars, market_meta, higher)
    if tf == "1d":
        return higher, _aggregate_fixed_factor(bars, 5, higher)
    if tf == "5d":
        return higher, _aggregate_fixed_factor(bars, 4, higher)
    raise ValueError(f"E 策略暂不支持周期：{tf}")


def _band_touch(bar: dict, row: dict) -> bool:
    a = row.get("GZB3")
    b = row.get("GZB4")
    if a is None or b is None:
        return False
    top = max(float(a), float(b))
    bottom = min(float(a), float(b))
    return float(bar["low"]) <= top and float(bar["high"]) >= bottom


def _break_below_zd1(i: int, bars: list[dict], ledger: list[dict]) -> bool:
    if i <= 0:
        return False
    now = ledger[i].get("ZD1")
    prev = ledger[i - 1].get("ZD1")
    if now is None or prev is None:
        return False
    return (
        float(bars[i]["close"]) < float(now)
        and float(bars[i - 1]["close"]) >= float(prev)
    )


def _break_above_zk1(i: int, bars: list[dict], ledger: list[dict]) -> bool:
    if i <= 0:
        return False
    now = ledger[i].get("ZK1")
    prev = ledger[i - 1].get("ZK1")
    if now is None or prev is None:
        return False
    return (
        float(bars[i]["close"]) > float(now)
        and float(bars[i - 1]["close"]) <= float(prev)
    )


def _risk_text(position: float, b1: bool, b2: bool, b3: bool, sell_stage: int) -> str:
    if position <= 1e-12:
        return "空仓 · 等待条件1"
    if sell_stage > 0:
        return f"退出阶段 {sell_stage}/2"
    used = sum(1 for x in (b1, b2, b3) if x)
    return f"持仓 {position * 100:.0f}% · 买入条件已用 {used}/3"


def _next_action_text(signal: dict | None) -> str:
    if not signal:
        return "当前没有新的 E 策略动作"
    kind = signal["kind"]
    if kind == "BUY":
        pp = int(round(float(signal["delta"]) * 100))
        return f"下一根所选周期 K 线开盘买入 {pp} 个百分点，最高 75%"
    if kind == "SELL50":
        return "下一根所选周期 K 线开盘减仓 50 个百分点"
    if kind == "SELL25":
        return "下一根所选周期 K 线开盘减仓 25 个百分点"
    if kind == "EXIT":
        return "下一根所选周期 K 线开盘全部清仓"
    return "当前没有新的 E 策略动作"


def analyze_e(
    symbol: str,
    candles: Iterable[dict],
    *,
    display_limit: int = 300,
    timeframe: str = "1d",
    market_meta: dict | None = None,
) -> dict:
    bars = _copy_validated(candles)
    tf = str(timeframe).lower()
    higher_tf, higher_bars = build_higher_bars(bars, tf, market_meta)
    if len(higher_bars) < E_MIN_WARMUP_BARS:
        raise ValueError(
            f"{symbol}: E 策略的大周期 {higher_tf} 已完成 K 线不足 {E_MIN_WARMUP_BARS} 根"
        )

    primary_ledger = build_ledger(bars, symbol)
    higher_ledger = build_ledger(higher_bars, f"{symbol}:{higher_tf}")

    higher_at_primary: list[tuple[int, dict] | None] = [None] * len(bars)
    h = -1
    for i in range(len(bars)):
        while h + 1 < len(higher_bars) and int(higher_bars[h + 1]["_source_end_index"]) <= i:
            h += 1
        if h >= 0:
            higher_at_primary[i] = (h, higher_ledger[h])

    warmup_index = None
    for i in range(E_MIN_WARMUP_BARS - 1, len(bars)):
        pair = higher_at_primary[i]
        if pair is not None and pair[0] >= E_MIN_WARMUP_BARS - 1:
            warmup_index = i
            break
    if warmup_index is None:
        raise ValueError(f"{symbol}: E 策略没有足够的主周期/大周期共同预热数据")

    position = 0.0
    b1_used = False
    b2_used = False
    b3_used = False
    sell_stage = 0
    pending: dict | None = None
    markers: list[dict] = []
    events: list[dict] = []
    positions: list[dict] = []
    latest_signal: dict | None = None

    for i, bar in enumerate(bars):
        if i < warmup_index:
            positions.append(
                {
                    "date": bar["date"],
                    "fraction": 0.0,
                    "risk_armed": False,
                    "risk_text": "预热",
                }
            )
            continue

        # 上一根已结束 K 线确认的动作，在本根开盘执行。
        if pending is not None:
            kind = pending["kind"]
            before = position
            if kind == "BUY":
                position = min(E_MAX_POSITION, position + float(pending["delta"]))
                if "E_BUY_1_PRIMARY_CLOSE_BREAK_BELOW_ZD1" in pending["rule_ids"]:
                    b1_used = True
                if "E_BUY_2_HIGHER_CLOSE_BELOW_ZD1" in pending["rule_ids"]:
                    b2_used = True
                if "E_BUY_3_TOUCH_GZB_BAND" in pending["rule_ids"]:
                    b3_used = True
            elif kind == "SELL50":
                position = max(0.0, position - 0.50)
                sell_stage = max(sell_stage, 1)
            elif kind == "SELL25":
                position = max(0.0, position - 0.25)
                sell_stage = max(sell_stage, 2)
            elif kind == "EXIT":
                position = 0.0

            if position <= 1e-12:
                position = 0.0
                b1_used = b2_used = b3_used = False
                sell_stage = 0

            action = "BUY" if kind == "BUY" else ("HARD_EXIT" if kind == "EXIT" else "SELL")
            side = "B" if action == "BUY" else ("X" if action == "HARD_EXIT" else "S")
            marker = {
                "signal_date": pending["signal_date"],
                "execution_date": bar["date"],
                "price": float(bar["open"]),
                "side": side,
                "action": action,
                "rule_ids": list(pending["rule_ids"]),
                "rule_names_zh": [E_RULE_NAMES_ZH[x] for x in pending["rule_ids"]],
                "position_before": before,
                "position_after": position,
                "risk_after": _risk_text(position, b1_used, b2_used, b3_used, sell_stage),
            }
            markers.append(marker)
            event_i = pending.get("event_index")
            if isinstance(event_i, int) and 0 <= event_i < len(events):
                events[event_i]["execution_date"] = bar["date"]
                events[event_i]["execution_price"] = float(bar["open"])
                events[event_i]["position_after"] = position
                events[event_i]["risk_after"] = marker["risk_after"]
            pending = None

        row = primary_ledger[i]
        pair = higher_at_primary[i]
        higher_row = pair[1] if pair is not None and pair[0] >= E_MIN_WARMUP_BARS - 1 else None

        signal: dict | None = None
        if position > 1e-12:
            inner_up = _break_above_zk1(i, bars, primary_ledger)
            exit_sequence_active = sell_stage > 0 or inner_up
            band_hit = _band_touch(bar, row)
            bs = row.get("BS")
            bs_hit = bs is not None and float(bar["high"]) >= float(bs)

            # 同一根 K 线只执行最高级别动作：灰带清仓 > BS -25pp > ZK1 -50pp。
            if exit_sequence_active and band_hit:
                signal = {
                    "kind": "EXIT",
                    "rule_ids": ["E_SELL_3_TOUCH_GZB_BAND_FULL_EXIT"],
                }
            elif sell_stage > 0 and row.get("ZK1") is not None and float(bar["close"]) < float(row["ZK1"]):
                signal = {
                    "kind": "EXIT",
                    "rule_ids": ["E_SELL_4_CLOSE_BACK_BELOW_ZK1_FULL_EXIT"],
                }
            elif exit_sequence_active and bs_hit:
                signal = {
                    "kind": "SELL25",
                    "rule_ids": ["E_SELL_2_TOUCH_BS_MINUS_25PP"],
                }
            elif sell_stage == 0 and inner_up:
                signal = {
                    "kind": "SELL50",
                    "rule_ids": ["E_SELL_1_PRIMARY_CLOSE_BREAK_ABOVE_ZK1_MINUS_50PP"],
                }

        # 一旦退出序列开始，不再在同一轮持仓中重新加仓。
        if signal is None and sell_stage == 0:
            state = str(row.get("color") or "")
            inner_down = (
                not b1_used
                and state in {"BLUE", "GRAY"}
                and _break_below_zd1(i, bars, primary_ledger)
            )
            if inner_down:
                rule_ids = ["E_BUY_1_PRIMARY_CLOSE_BREAK_BELOW_ZD1"]
                delta = 0.25
                if (
                    not b2_used
                    and higher_row is not None
                    and higher_row.get("ZD1") is not None
                    and float(higher_row["close"]) < float(higher_row["ZD1"])
                ):
                    rule_ids.append("E_BUY_2_HIGHER_CLOSE_BELOW_ZD1")
                    delta += 0.25
                signal = {"kind": "BUY", "delta": delta, "rule_ids": rule_ids}
            elif b1_used and not b3_used and _band_touch(bar, row):
                signal = {
                    "kind": "BUY",
                    "delta": 0.25,
                    "rule_ids": ["E_BUY_3_TOUCH_GZB_BAND"],
                }

        positions.append(
            {
                "date": bar["date"],
                "fraction": position,
                "risk_armed": sell_stage > 0,
                "risk_text": _risk_text(position, b1_used, b2_used, b3_used, sell_stage),
            }
        )

        if signal is not None:
            action = "BUY" if signal["kind"] == "BUY" else (
                "HARD_EXIT" if signal["kind"] == "EXIT" else "SELL"
            )
            event = {
                "date": row["date"],
                "state": row["color"],
                "state_zh": STATE_NAMES_ZH.get(str(row["color"]), str(row["color"])),
                "age": row["run_age"],
                "origin": row["origin"],
                "action": action,
                "action_zh": ACTION_NAMES_ZH[action],
                "rule_ids": list(signal["rule_ids"]),
                "rule_names_zh": [E_RULE_NAMES_ZH[x] for x in signal["rule_ids"]],
                "execution_date": None,
                "execution_price": None,
                "position_after": None,
                "risk_after": None,
            }
            events.append(event)
            signal = dict(signal)
            signal["signal_date"] = row["date"]
            signal["event_index"] = len(events) - 1
            pending = signal
            latest_signal = signal
        else:
            latest_signal = None

    last = primary_ledger[-1]
    last_pair = higher_at_primary[-1]
    last_higher = last_pair[1] if last_pair is not None else None

    limit = max(80, min(int(display_limit), 500))
    start = max(0, len(bars) - limit)
    position_by_date = {x["date"]: x for x in positions}
    chart = []
    for i in range(start, len(bars)):
        bar = bars[i]
        row = primary_ledger[i]
        pos = position_by_date.get(bar["date"]) or {}
        chart.append(
            {
                "date": bar["date"],
                "open": bar["open"],
                "high": bar["high"],
                "low": bar["low"],
                "close": bar["close"],
                "volume": bar["volume"],
                "state": row["color"],
                "GZB3": row["GZB3"],
                "GZB4": row["GZB4"],
                "ZD1": row["ZD1"],
                "ZK1": row["ZK1"],
                "BS": row["BS"],
                "position": float(pos.get("fraction") or 0.0),
                "risk_armed": bool(pos.get("risk_armed")),
            }
        )

    visible_dates = {x["date"] for x in chart}
    visible_markers = [m for m in markers if m["execution_date"] in visible_dates]

    resolved_action = "NONE"
    if latest_signal is not None:
        resolved_action = "BUY" if latest_signal["kind"] == "BUY" else (
            "HARD_EXIT" if latest_signal["kind"] == "EXIT" else "SELL"
        )

    return {
        "strategy": {
            "id": E_STRATEGY_ID,
            "selector_label": "E",
            "version": E_STRATEGY_VERSION,
            "source_commit": E_SOURCE,
            "active_rule_count": sum(len(x) for x in E_RULES.values()),
            "active_rules": E_RULES,
            "active_rules_zh": {
                group: [E_RULE_NAMES_ZH[x] for x in ids] for group, ids in E_RULES.items()
            },
            "position_policy": "E_I25_I25_I25_CAP75_S50PP_S25PP_FULL",
            "position_policy_zh": "条件1/2/3每轮各一次，分别 +25pp，最高75%；卖出按 -50pp / -25pp / 清仓",
            "hard_exit": "E_GZB_OR_ZK1_RETURN_FULL_EXIT",
            "hard_exit_zh": "退出序列中触碰灰带或收盘跌回 ZK1 下方时全部清仓",
            "display_candles": limit,
            "timeframe": tf,
            "higher_timeframe": higher_tf,
            "bar_close_contract": "CONFIRMED_ON_SELECTED_BAR_CLOSE_EXECUTE_ON_NEXT_SELECTED_BAR_OPEN",
            "bar_close_contract_zh": "所选周期 K 线结束后确认信号，并在下一根同周期 K 线开盘执行",
            "rules_title_zh": "SLTD E 独立策略",
            "policy_title_zh": "E 仓位 / 退出执行策略",
            "summary_state_label_zh": "E 周期状态",
            "policy_steps_zh": [
                "① 条件1：蓝/灰区收盘跌破 ZD1 → +25pp",
                f"② 条件2：同一时刻 {higher_tf} 收盘也低于其 ZD1 → 再 +25pp",
                "③ 条件3：之后触碰 GZB3-GZB4 → 再 +25pp；最高75%",
                "④ 收盘突破 ZK1 → -50pp",
                "⑤ 触碰 BS → -25pp",
                "⑥ 触碰灰带，或退出后收盘跌回 ZK1 → 全部清仓",
            ],
        },
        "snapshot": {
            "symbol": symbol,
            "latest_date": str(last["date"]),
            "latest_close": float(last["close"]),
            "state": str(last["color"]),
            "state_zh": STATE_NAMES_ZH.get(str(last["color"]), str(last["color"])),
            "run_age": int(last["run_age"]),
            "age_bucket": str(last["age"]),
            "origin": str(last["origin"]) if last["origin"] is not None else None,
            "resolved_action": resolved_action,
            "resolved_action_zh": ACTION_NAMES_ZH.get(resolved_action, resolved_action),
            "rule_ids": list(latest_signal["rule_ids"]) if latest_signal else [],
            "rule_names_zh": [E_RULE_NAMES_ZH[x] for x in latest_signal["rule_ids"]] if latest_signal else [],
            "position_fraction": position,
            "risk_state": "E",
            "risk_state_zh": _risk_text(position, b1_used, b2_used, b3_used, sell_stage),
            "risk_sub_zh": "每轮条件1/2/3各最多执行一次；完全清仓后重置",
            "next_action": _next_action_text(latest_signal),
            "GZB4": last["GZB4"],
            "ZD1": last["ZD1"],
            "ZK1": last["ZK1"],
            "BS": last["BS"],
            "higher_timeframe": higher_tf,
            "higher_latest_date": str(last_higher["date"]) if last_higher else None,
            "higher_close": float(last_higher["close"]) if last_higher else None,
            "higher_ZD1": float(last_higher["ZD1"]) if last_higher and last_higher.get("ZD1") is not None else None,
            "higher_below_ZD1": bool(
                last_higher
                and last_higher.get("ZD1") is not None
                and float(last_higher["close"]) < float(last_higher["ZD1"])
            ),
        },
        "chart": chart,
        "markers": visible_markers,
        "events": events[-60:],
    }
