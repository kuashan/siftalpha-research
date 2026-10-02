from __future__ import annotations

"""Frozen 5s-stocks v1 strategy adapter for the SLTD web shell.

Signal equations come byte-for-byte from the frozen 5s engine. This module only
implements the frozen U.S.-stock position policy:
- BUY-A/B -> 60%
- BUY-C onset within W3 -> add 40 percentage points, cap 100%
- first isolated SELL-A/B -> sell half of the current holding
- SELL-C or same-bar multi SELL -> full exit
- after an A/B half exit, the first later onset from a different SELL family -> full exit
- completed selected bar confirms; next selected bar open executes
"""

from typing import Iterable

from five_s_signal_engine import BarEvaluation, evaluate_candles
from strategy import _validate_candles


FIVE_S_STOCKS_ID = "5s_stocks"
FIVE_S_STOCKS_VERSION = "5s Stocks v1"
FIVE_S_STOCKS_SOURCE = "research/ssss/5S_STOCKS_V1_BASELINE.md"
FIVE_S_STOCKS_WARMUP_INDEX = 63
FIVE_S_STOCKS_RULES = {
    "BUY": ("BUY_A", "BUY_B", "BUY_C"),
    "HOLD": (),
    "WAIT": (),
    "SELL": ("SELL_A", "SELL_B", "SELL_C"),
}

RULE_NAMES_ZH = {
    "BUY_A": "BUY-A：空仓时触发，下一根开盘建立 60% 仓位",
    "BUY_B": "BUY-B：空仓时触发，下一根开盘建立 60% 仓位",
    "BUY_C": "BUY-C：初始买入后 W3 内首次触发，下一根开盘再加 40 个百分点",
    "SELL_A": "SELL-A：首次独立触发，下一根开盘卖出当前持仓的一半",
    "SELL_B": "SELL-B：首次独立触发，下一根开盘卖出当前持仓的一半",
    "SELL_C": "SELL-C：触发后下一根开盘全部清仓",
    "MULTI_SELL": "多个 SELL family 同根触发：下一根开盘全部清仓",
    "DISTINCT_SELL_FULL": "A/B 半卖后出现不同 SELL family：下一根开盘清掉剩余仓位",
}

ACTION_NAMES_ZH = {
    "BUY": "买入",
    "SELL": "卖出一半",
    "HARD_EXIT": "全部清仓",
    "NONE": "无新动作",
}

DIM_NAMES_ZH = {
    "trend": "趋势",
    "capital": "资金",
    "momentum": "动量",
    "accel": "加速",
    "anomaly": "异常",
}
STATE_NAMES_ZH = {
    "LONG": "多",
    "LIGHT_LONG": "偏多",
    "GRAY": "灰",
    "LIGHT_SHORT": "偏空",
    "SHORT": "空",
}


def _state_text(ev: BarEvaluation) -> str:
    return " · ".join(
        f"{DIM_NAMES_ZH[k]}{STATE_NAMES_ZH.get(ev.states.get(k, ''), ev.states.get(k, ''))}"
        for k in ("trend", "capital", "momentum", "accel", "anomaly")
    )


def _rule_names(ids: Iterable[str]) -> list[str]:
    return [RULE_NAMES_ZH.get(str(x), str(x)) for x in ids]


def _action_from_pending(actions: list[dict]) -> str:
    if any(a["kind"] == "FULL_EXIT" for a in actions):
        return "HARD_EXIT"
    if any(a["kind"] == "HALF_EXIT" for a in actions):
        return "SELL"
    if any(a["kind"] in {"BUY_60", "TOPUP_40"} for a in actions):
        return "BUY"
    return "NONE"


def _next_action_text(actions: list[dict]) -> str:
    if not actions:
        return "当前没有新的 5s Stocks 执行动作"
    parts: list[str] = []
    for action in actions:
        kind = action["kind"]
        if kind == "BUY_60":
            parts.append("下一根所选周期 K 线开盘建立 60% 仓位")
        elif kind == "TOPUP_40":
            parts.append("下一根所选周期 K 线开盘加 40 个百分点，最高 100%")
        elif kind == "HALF_EXIT":
            parts.append("下一根所选周期 K 线开盘卖出当前持仓的一半")
        elif kind == "FULL_EXIT":
            parts.append("下一根所选周期 K 线开盘全部清仓")
    return "；".join(parts) if parts else "当前没有新的 5s Stocks 执行动作"


def analyze_5s_stocks(
    symbol: str,
    candles: Iterable[dict],
    *,
    display_limit: int = 300,
    timeframe: str = "1d",
) -> dict:
    raw = [dict(x) for x in candles]
    bars = _validate_candles(raw)
    engine_rows = []
    for i, bar in enumerate(bars):
        src = raw[i] if i < len(raw) else {}
        engine_rows.append(
            {
                "open_time": int(src.get("open_time", i)),
                "open": bar["open"],
                "high": bar["high"],
                "low": bar["low"],
                "close": bar["close"],
                "volume": bar["volume"],
            }
        )

    evaluations = evaluate_candles(engine_rows)
    if len(evaluations) != len(bars):
        raise RuntimeError("5s Stocks 冻结信号引擎返回长度异常")

    position = 0.0
    c_confirmed = False
    entry_signal_index: int | None = None
    entry_family: str | None = None
    first_sell_families: set[str] | None = None
    pending: list[dict] = []
    positions: list[dict] = []
    markers: list[dict] = []
    events: list[dict] = []
    latest_pending: list[dict] = []

    for i, (bar, ev) in enumerate(zip(bars, evaluations)):
        # Signal confirmed on t-1 executes at this bar's open.
        if pending:
            for action in pending:
                before = position
                kind = action["kind"]
                if kind == "BUY_60":
                    position = 0.60
                    c_confirmed = False
                    entry_signal_index = int(action["signal_index"])
                    entry_family = str(action["family"])
                    first_sell_families = None
                elif kind == "TOPUP_40":
                    position = min(1.0, position + 0.40)
                    c_confirmed = True
                elif kind == "HALF_EXIT":
                    position *= 0.50
                elif kind == "FULL_EXIT":
                    position = 0.0

                if position <= 1e-12:
                    position = 0.0
                    c_confirmed = False
                    entry_signal_index = None
                    entry_family = None
                    first_sell_families = None

                side = (
                    "B"
                    if kind in {"BUY_60", "TOPUP_40"}
                    else ("X" if kind == "FULL_EXIT" else "S")
                )
                marker = {
                    "signal_date": action["signal_date"],
                    "execution_date": bar["date"],
                    "price": float(bar["open"]),
                    "side": side,
                    "action": (
                        "BUY"
                        if side == "B"
                        else ("HARD_EXIT" if side == "X" else "SELL")
                    ),
                    "rule_ids": list(action["rule_ids"]),
                    "rule_names_zh": _rule_names(action["rule_ids"]),
                    "position_before": before,
                    "position_after": position,
                    "risk_after": "NORMAL",
                }
                markers.append(marker)

                event_index = action.get("event_index")
                if isinstance(event_index, int) and 0 <= event_index < len(events):
                    event = events[event_index]
                    event["execution_date"] = bar["date"]
                    event["execution_price"] = float(bar["open"])
                    event["position_after"] = position
                    event["risk_after"] = "NORMAL"
            pending = []

        positions.append(
            {
                "date": bar["date"],
                "fraction": position,
                "risk_armed": False,
            }
        )

        if i < FIVE_S_STOCKS_WARMUP_INDEX:
            latest_pending = []
            continue

        buy = tuple(ev.buy_onsets)
        sell = tuple(ev.sell_onsets)
        actions: list[dict] = []

        if position <= 1e-12:
            initial = [x for x in buy if x in ("A", "B")]
            if initial and not sell:
                family = initial[0]
                actions.append(
                    {
                        "kind": "BUY_60",
                        "family": family,
                        "rule_ids": [f"BUY_{family}"],
                    }
                )
        else:
            # Match the frozen research ordering: eligible C top-up is queued
            # before any same-bar SELL action.
            if (
                not c_confirmed
                and entry_signal_index is not None
                and 1 <= i - entry_signal_index <= 3
                and "C" in buy
            ):
                actions.append(
                    {
                        "kind": "TOPUP_40",
                        "rule_ids": ["BUY_C"],
                    }
                )

            if sell:
                if first_sell_families is None:
                    first_sell_families = set(sell)
                    if len(sell) >= 2:
                        actions.append(
                            {
                                "kind": "FULL_EXIT",
                                "rule_ids": ["MULTI_SELL"],
                            }
                        )
                    elif "C" in sell:
                        actions.append(
                            {
                                "kind": "FULL_EXIT",
                                "rule_ids": ["SELL_C"],
                            }
                        )
                    else:
                        family = sell[0]
                        actions.append(
                            {
                                "kind": "HALF_EXIT",
                                "rule_ids": [f"SELL_{family}"],
                            }
                        )
                elif any(f not in first_sell_families for f in sell):
                    actions.append(
                        {
                            "kind": "FULL_EXIT",
                            "rule_ids": [
                                "DISTINCT_SELL_FULL",
                                *[f"SELL_{f}" for f in sell],
                            ],
                        }
                    )

        if actions:
            action_name = _action_from_pending(actions)
            state_text = _state_text(ev)
            for action in actions:
                event = {
                    "date": bar["date"],
                    "state": "OTHER",
                    "state_zh": state_text,
                    "age": "—",
                    "origin": entry_family,
                    "action": (
                        "BUY"
                        if action["kind"] in {"BUY_60", "TOPUP_40"}
                        else ("HARD_EXIT" if action["kind"] == "FULL_EXIT" else "SELL")
                    ),
                    "action_zh": ACTION_NAMES_ZH.get(
                        "BUY"
                        if action["kind"] in {"BUY_60", "TOPUP_40"}
                        else ("HARD_EXIT" if action["kind"] == "FULL_EXIT" else "SELL"),
                        action_name,
                    ),
                    "rule_ids": list(action["rule_ids"]),
                    "rule_names_zh": _rule_names(action["rule_ids"]),
                    "execution_date": None,
                    "execution_price": None,
                    "position_after": None,
                    "risk_after": None,
                }
                events.append(event)
                action["signal_date"] = bar["date"]
                action["signal_index"] = i
                action["event_index"] = len(events) - 1
            pending = actions
            latest_pending = [dict(x) for x in actions]
        else:
            latest_pending = []

    latest_ev = evaluations[-1]
    latest = bars[-1]
    latest_rule_ids: list[str] = []
    for action in latest_pending:
        latest_rule_ids.extend(action["rule_ids"])
    resolved_action = _action_from_pending(latest_pending)

    limit = max(80, min(int(display_limit), 500))
    start = max(0, len(bars) - limit)
    pos_by_date = {x["date"]: x for x in positions}
    chart = []
    for i in range(start, len(bars)):
        bar = bars[i]
        pos = pos_by_date.get(bar["date"]) or {}
        chart.append(
            {
                "date": bar["date"],
                "open": bar["open"],
                "high": bar["high"],
                "low": bar["low"],
                "close": bar["close"],
                "volume": bar["volume"],
                "state": "OTHER",
                "state_zh": _state_text(evaluations[i]),
                "position": float(pos.get("fraction") or 0.0),
                "risk_armed": False,
            }
        )

    visible_dates = {x["date"] for x in chart}
    visible_markers = [m for m in markers if m["execution_date"] in visible_dates]
    timeframe_note = (
        "1d 为冻结研究基线验证周期"
        if str(timeframe) == "1d"
        else "当前周期按同一冻结公式运行，属于实验周期"
    )

    return {
        "strategy": {
            "id": FIVE_S_STOCKS_ID,
            "selector_label": "5s Stocks",
            "version": FIVE_S_STOCKS_VERSION,
            "source_commit": FIVE_S_STOCKS_SOURCE,
            "active_rule_count": 6,
            "active_rules": FIVE_S_STOCKS_RULES,
            "active_rules_zh": {
                group: _rule_names(ids) for group, ids in FIVE_S_STOCKS_RULES.items()
            },
            "position_policy": "BUY_AB_60_C_W3_PLUS40_AB_HALF_C_MULTI_FULL",
            "position_policy_zh": "A/B 建仓60%；W3 C +40pp；A/B 首次半卖；C/多重/后续不同 SELL 全清",
            "hard_exit": "SELL_C_OR_MULTI_OR_LATER_DISTINCT_FULL_EXIT",
            "hard_exit_zh": "SELL-C、同根多重 SELL，或 A/B 半卖后首次不同 SELL 全部清仓",
            "display_candles": limit,
            "timeframe": str(timeframe),
            "timeframe_validation_zh": timeframe_note,
            "bar_close_contract": "CONFIRMED_ON_SELECTED_BAR_CLOSE_EXECUTE_ON_NEXT_SELECTED_BAR_OPEN",
            "bar_close_contract_zh": "所选周期 K 线结束后确认信号，并在下一根同周期 K 线开盘执行",
            "rules_title_zh": "5s Stocks v1 冻结信号",
            "policy_title_zh": "5s Stocks v1 仓位 / 卖出策略",
            "summary_state_label_zh": "5s 仓位状态",
            "policy_steps_zh": [
                "① BUY-A / BUY-B：空仓 → 60%",
                "② 初始买入后 W3 内 BUY-C：+40 个百分点，最高100%",
                "③ 首次独立 SELL-A：卖当前持仓的一半",
                "④ 首次独立 SELL-B：卖当前持仓的一半",
                "⑤ SELL-C 或同根多个 SELL：全部清仓",
                "⑥ A/B 半卖后首次出现不同 SELL family：清掉剩余仓位",
            ],
        },
        "snapshot": {
            "symbol": symbol,
            "latest_date": str(latest["date"]),
            "latest_close": float(latest["close"]),
            "state": "OTHER",
            "state_zh": _state_text(latest_ev),
            "run_age": None,
            "age_bucket": timeframe_note,
            "origin": entry_family,
            "resolved_action": resolved_action,
            "resolved_action_zh": ACTION_NAMES_ZH.get(resolved_action, resolved_action),
            "rule_ids": latest_rule_ids,
            "rule_names_zh": _rule_names(latest_rule_ids),
            "position_fraction": position,
            "risk_state": "NORMAL",
            "risk_state_zh": "正常",
            "risk_sub_zh": "A/B 首次半卖；C / 多重 SELL / 后续不同 SELL 全清",
            "next_action": _next_action_text(latest_pending),
        },
        "chart": chart,
        "markers": visible_markers,
        "events": events[-60:],
    }
