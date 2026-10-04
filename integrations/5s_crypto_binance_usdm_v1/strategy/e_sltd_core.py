from __future__ import annotations

"""SLTD V7 冻结候选策略：信号引擎与统一仓位管理。

本模块不依赖第三方 Python 包，便于 SiftAlpha 在内部或外部 Python 运行环境中准备和运行。

策略事实源：
- candidate/sltd-v7-12rules-position-v1
- commit 5f9ea4d8fa434b54afdbf32a1cb21ef2f3cb4042

执行语义：
- 只在所选周期 K 线结束后确认信号；
- 在下一根同周期 K 线开盘执行动作；
- 只做多或持有现金，不做空、不加杠杆；
- 第一次买入：目标仓位 25%；
- 后续实际买入：每次增加 25 个百分点，最高 100%；
- 普通卖出：卖出当前持仓的 25%；
- 普通卖出实际执行后，C2 风险状态进入“已警戒”；
- 后续实际买入会把 C2 风险状态重置为“正常”；
- 已警戒时，如果进入绿色状态且整根 K 线位于慢带下方（High < GZB4），
  则在下一根同周期 K 线开盘全部清仓。
"""

from dataclasses import dataclass
from math import isfinite
from typing import Iterable


STRATEGY_VERSION = "SLTD V7 12条规则候选版 v1"
STRATEGY_SOURCE_COMMIT = "5f9ea4d8fa434b54afdbf32a1cb21ef2f3cb4042"
POSITION_POLICY_ID = "I25_AADD_25_TO_CAP_S25_WHOLD_RNO_CHANGE_MIXED"
HARD_EXIT_ID = "C2_FULL_CANDLE_BELOW_SLOW_BAND"
POLICY_START_DATE = "2020-01-02"
MIN_WARMUP_BARS = 120

REMOVED_V6_RULES = (
    "BUY_RECENT_BLUE_GRAY_LIGHT_SUPPORT",
    "SELL_RECENT_BLUE_GRAY_LIGHT_RESIST",
    "NEW_V5_D_GREEN_11_20_UPPER_WICK_ONLY",
)

ACTIVE_RULES = {
    "BUY": (
        "BUY_BLUE_21P_LOWER",
        "BUY_GRAY_4_10_LIGHT_SUPPORT",
        "BLUE_11_20_LOWER_WICK_ONLY",
        "NEW_V5_C_GRAY_4_10_LOWER_WICK_ONLY",
    ),
    "HOLD": (
        "CONT_BLUE_11_20_UPPER",
        "CONT_BLUE_4_10_UPPER",
        "CONT_RECENT_GRAY_BLUE_UPPER",
        "NEW_V5_B_BLUE_21P_UPPER_CLOSE_ABOVE",
    ),
    "WAIT": (
        "AVOID_GREEN_11_20_LOWER",
        "GREEN_11_20_LOWER_CLOSE_BELOW",
    ),
    "SELL": (
        "GREEN_4_10_UPPER",
        "NEW_V5_E_GREEN_11_20_LIGHT_RESIST",
    ),
}

ACTION_ORDER = ("BUY", "HOLD", "WAIT", "SELL")

# 英文编号只作为冻结研究的内部机器标识；用户界面与文档统一显示下面的中文含义。
RULE_NAMES_ZH = {
    "BUY_BLUE_21P_LOWER": "蓝色持续21根以上：下轨触发买入",
    "BUY_GRAY_4_10_LIGHT_SUPPORT": "灰色第4至10根：轻支撑触发买入",
    "BLUE_11_20_LOWER_WICK_ONLY": "蓝色第11至20根：下轨仅影线触发买入",
    "NEW_V5_C_GRAY_4_10_LOWER_WICK_ONLY": "灰色第4至10根：下轨仅影线触发买入",
    "CONT_BLUE_11_20_UPPER": "蓝色第11至20根：上轨触发继续持有",
    "CONT_BLUE_4_10_UPPER": "蓝色第4至10根：上轨触发继续持有",
    "CONT_RECENT_GRAY_BLUE_UPPER": "近期灰转蓝：上轨触发继续持有",
    "NEW_V5_B_BLUE_21P_UPPER_CLOSE_ABOVE": "蓝色持续21根以上：收盘站上上轨继续持有",
    "AVOID_GREEN_11_20_LOWER": "绿色第11至20根：下轨触发等待",
    "GREEN_11_20_LOWER_CLOSE_BELOW": "绿色第11至20根：收盘跌破下轨继续等待",
    "GREEN_4_10_UPPER": "绿色第4至10根：上轨触发卖出",
    "NEW_V5_E_GREEN_11_20_LIGHT_RESIST": "绿色第11至20根：轻阻力触发卖出",
}

REMOVED_V6_RULE_NAMES_ZH = {
    "BUY_RECENT_BLUE_GRAY_LIGHT_SUPPORT": "已移除：近期蓝/灰轻支撑买入",
    "SELL_RECENT_BLUE_GRAY_LIGHT_RESIST": "已移除：近期蓝/灰轻阻力卖出",
    "NEW_V5_D_GREEN_11_20_UPPER_WICK_ONLY": "已移除：绿色第11至20根上轨仅影线卖出",
}

ACTION_NAMES_ZH = {
    "BUY": "买入",
    "HOLD": "持有",
    "WAIT": "等待",
    "SELL": "卖出",
    "HARD_EXIT": "C2 强制清仓",
    "MIXED": "冲突信号不动作",
    "NONE": "无新动作",
}
STATE_NAMES_ZH = {
    "BLUE": "蓝色",
    "GRAY": "灰色",
    "GREEN": "绿色",
    "OTHER": "其他",
}
RISK_NAMES_ZH = {
    "ARMED": "已警戒",
    "NORMAL": "正常",
}
POSITION_POLICY_NAME_ZH = "首次买入25%；后续每次加25个百分点至100%；普通卖出每次减当前仓位25%；冲突信号不调整仓位"
HARD_EXIT_NAME_ZH = "C2：已警戒时，绿色状态且整根K线跌到慢带下方（High < GZB4），下一根同周期K线开盘全部清仓"


def rule_name_zh(rule_id: str) -> str:
    return RULE_NAMES_ZH.get(str(rule_id), str(rule_id))


def rule_names_zh(rule_ids: Iterable[str]) -> list[str]:
    return [rule_name_zh(x) for x in rule_ids]


@dataclass(frozen=True)
class StrategySnapshot:
    symbol: str
    latest_date: str
    latest_close: float
    state: str
    run_age: int
    age_bucket: str
    origin: str | None
    resolved_action: str
    rule_ids: tuple[str, ...]
    position_fraction: float
    risk_state: str
    next_action: str


def _prefix(values: list[float]) -> list[float]:
    out = [0.0]
    running = 0.0
    for value in values:
        running += float(value)
        out.append(running)
    return out


def weighted_20(values: list[float]) -> list[float | None]:
    out: list[float | None] = [None] * len(values)
    for i in range(19, len(values)):
        total = 0.0
        for k in range(20):
            total += (20 - k) * float(values[i - k])
        out[i] = total / 210.0
    return out


def ema_optional(values: list[float | None], period: int) -> list[float | None]:
    alpha = 2.0 / (period + 1.0)
    out: list[float | None] = [None] * len(values)
    prev: float | None = None
    for i, value in enumerate(values):
        if value is None or not isfinite(float(value)):
            continue
        fv = float(value)
        prev = fv if prev is None else alpha * fv + (1.0 - alpha) * prev
        out[i] = prev
    return out


def double_xma_right(prefix: list[float], t: int, period: int) -> float:
    """冻结研究使用的精确因果右端 XMA(XMA(x,n),n) 计算。"""
    p = int((period - 2) / 2)
    outer_left = max(0, t - p - 1)
    inners: list[float] = []
    for j in range(outer_left, t + 1):
        left = max(0, j - p - 1)
        right = min(t + 1, j + (period - p) - 1)
        if right <= left:
            raise RuntimeError("XMA 计算窗口无效")
        inners.append((prefix[right] - prefix[left]) / (right - left))
    return sum(inners) / len(inners)


def age_bucket(age: int) -> str:
    if age <= 3:
        return "1_3"
    if age <= 10:
        return "4_10"
    if age <= 20:
        return "11_20"
    return "21_PLUS"


def _validate_candles(candles: Iterable[dict]) -> list[dict]:
    out = []
    last_date = ""
    for raw in candles:
        date = str(raw.get("date") or "")
        if not date:
            raise ValueError("K 线日期不能为空")
        if last_date and date <= last_date:
            raise ValueError("K 线必须按时间严格递增排列")
        item = {
            "date": date,
            "open": float(raw["open"]),
            "high": float(raw["high"]),
            "low": float(raw["low"]),
            "close": float(raw["close"]),
            "volume": float(raw.get("volume") or 0.0),
        }
        if item["high"] < item["low"]:
            raise ValueError(f"{date}: 最高价小于最低价")
        out.append(item)
        last_date = date
    if len(out) < 120:
        raise ValueError("至少需要 120 根已经结束的 K 线")
    return out


def build_ledger(candles: Iterable[dict], symbol: str) -> list[dict]:
    """构建冻结 V7 的“首次观察”信号账本。"""
    bars = _validate_candles(candles)
    highs = [b["high"] for b in bars]
    lows = [b["low"] for b in bars]
    closes = [b["close"] for b in bars]

    high_prefix = _prefix(highs)
    low_prefix = _prefix(lows)

    wh = weighted_20(highs)
    wl = weighted_20(lows)
    gzb3 = ema_optional(wh, 90)
    gzb4 = ema_optional(wl, 90)

    rows: list[dict] = []
    prev_state: str | None = None
    current_origin: str | None = None
    run_age = 0
    prev_support_contact = False
    prev_resist_contact = False

    for t, bar in enumerate(bars):
        vl25 = double_xma_right(low_prefix, t, 25)
        vh25 = double_xma_right(high_prefix, t, 25)
        w25 = vh25 - vl25
        zd1 = vl25 - w25
        zk1 = vh25 + w25

        vl60 = double_xma_right(low_prefix, t, 60)
        vh60 = double_xma_right(high_prefix, t, 60)
        w60 = vh60 - vl60
        bs = vh60 + 2.2 * w60
        bd = vl60 - 2.8 * w60

        state = "OTHER"
        slow_top = gzb3[t]
        slow_bottom = gzb4[t]
        gzb8 = None
        gzb9 = None
        if slow_top is not None and slow_bottom is not None:
            sw = slow_top - slow_bottom
            gzb8 = slow_top + 2.0 * sw
            gzb9 = slow_bottom - 2.0 * sw
            if zd1 >= gzb9 and zk1 >= gzb8:
                state = "BLUE"
            elif zk1 <= gzb8 and zd1 <= gzb9:
                state = "GREEN"
            elif zd1 >= gzb9 and zk1 <= gzb8:
                state = "GRAY"

        if state == prev_state:
            run_age += 1
        else:
            current_origin = prev_state
            run_age = 1
        bucket = age_bucket(run_age)

        lower = False
        upper = False
        lower_subtype = None
        upper_subtype = None
        if t > 0 and rows:
            prev = rows[-1]
            lower = bool(bar["low"] < zd1 and not (bars[t - 1]["low"] < float(prev["ZD1"])))
            upper = bool(bar["high"] > zk1 and not (bars[t - 1]["high"] > float(prev["ZK1"])))

        if lower:
            if bar["close"] >= zd1:
                lower_subtype = "WICK_ONLY"
            elif bar["high"] >= zd1:
                lower_subtype = "CLOSE_BELOW"
            else:
                lower_subtype = "FULL_BELOW"

        if upper:
            if bar["close"] <= zk1:
                upper_subtype = "WICK_ONLY"
            elif bar["low"] <= zk1:
                upper_subtype = "CLOSE_ABOVE"
            else:
                upper_subtype = "FULL_ABOVE"

        support_contact = False
        resist_contact = False
        light_support = False
        light_resist = False
        if t > 0 and slow_top is not None and slow_bottom is not None:
            prev_top = gzb3[t - 1]
            prev_bottom = gzb4[t - 1]
            if prev_top is not None and prev_bottom is not None:
                intersects = bar["high"] >= slow_bottom and bar["low"] <= slow_top
                support_contact = bool(bars[t - 1]["close"] > prev_top and intersects)
                resist_contact = bool(bars[t - 1]["close"] < prev_bottom and intersects)
                light_support = support_contact and not prev_support_contact
                light_resist = resist_contact and not prev_resist_contact

        recent = current_origin in ("BLUE", "GRAY", "GREEN") and run_age <= 5
        transition = (
            f"{current_origin}->{state}"
            if recent and current_origin != state
            else None
        )

        actions: dict[str, list[str]] = {k: [] for k in ACTION_ORDER}

        # 买入规则——V7 当前启用规则；V6 的“近期蓝/灰轻支撑买入”已移除。
        if state == "BLUE" and run_age >= 21 and lower:
            actions["BUY"].append("BUY_BLUE_21P_LOWER")
        if state == "GRAY" and 4 <= run_age <= 10 and light_support:
            actions["BUY"].append("BUY_GRAY_4_10_LIGHT_SUPPORT")
        if state == "BLUE" and 11 <= run_age <= 20 and lower and lower_subtype == "WICK_ONLY":
            actions["BUY"].append("BLUE_11_20_LOWER_WICK_ONLY")
        if state == "GRAY" and 4 <= run_age <= 10 and lower and lower_subtype == "WICK_ONLY":
            actions["BUY"].append("NEW_V5_C_GRAY_4_10_LOWER_WICK_ONLY")

        # 持有规则
        if state == "BLUE" and 11 <= run_age <= 20 and upper:
            actions["HOLD"].append("CONT_BLUE_11_20_UPPER")
        if state == "BLUE" and 4 <= run_age <= 10 and upper:
            actions["HOLD"].append("CONT_BLUE_4_10_UPPER")
        if state == "BLUE" and current_origin == "GRAY" and run_age <= 5 and upper:
            actions["HOLD"].append("CONT_RECENT_GRAY_BLUE_UPPER")
        if state == "BLUE" and run_age >= 21 and upper and upper_subtype == "CLOSE_ABOVE":
            actions["HOLD"].append("NEW_V5_B_BLUE_21P_UPPER_CLOSE_ABOVE")

        # 等待规则
        if state == "GREEN" and 11 <= run_age <= 20 and lower:
            actions["WAIT"].append("AVOID_GREEN_11_20_LOWER")
        if state == "GREEN" and 11 <= run_age <= 20 and lower and lower_subtype == "CLOSE_BELOW":
            actions["WAIT"].append("GREEN_11_20_LOWER_CLOSE_BELOW")

        # 卖出规则——V7 已移除旧 S1 和 S3。
        if state == "GREEN" and 4 <= run_age <= 10 and upper:
            actions["SELL"].append("GREEN_4_10_UPPER")
        if state == "GREEN" and 11 <= run_age <= 20 and light_resist:
            actions["SELL"].append("NEW_V5_E_GREEN_11_20_LIGHT_RESIST")

        rows.append(
            {
                "symbol": symbol,
                "date": bar["date"],
                "open": bar["open"],
                "high": bar["high"],
                "low": bar["low"],
                "close": bar["close"],
                "volume": bar["volume"],
                "ZD1": zd1,
                "ZK1": zk1,
                "GZB3": slow_top,
                "GZB4": slow_bottom,
                "GZB8": gzb8,
                "GZB9": gzb9,
                "BS": bs,
                "BD": bd,
                "color": state,
                "run_age": run_age,
                "age": bucket,
                "origin": current_origin,
                "recent": recent,
                "transition": transition,
                "lower": lower,
                "lower_subtype": lower_subtype,
                "upper": upper,
                "upper_subtype": upper_subtype,
                "light_support": light_support,
                "light_resist": light_resist,
                "BUY": actions["BUY"],
                "HOLD": actions["HOLD"],
                "WAIT": actions["WAIT"],
                "SELL": actions["SELL"],
            }
        )
        prev_state = state
        prev_support_contact = support_contact
        prev_resist_contact = resist_contact

    return rows


def action_classes(row: dict | None) -> tuple[str, ...]:
    if not row:
        return ()
    return tuple(k for k in ACTION_ORDER if row.get(k))


def resolve_action(row: dict | None) -> str | None:
    """V7 保持冻结规则：出现不同动作类别的冲突信号时不调整仓位。"""
    classes = action_classes(row)
    if len(classes) == 1:
        return classes[0]
    return None


def c2_condition(row: dict | None) -> bool:
    if not row or str(row.get("color") or "").upper() != "GREEN":
        return False
    gzb4 = row.get("GZB4")
    if gzb4 is None:
        return False
    return float(row["high"]) < float(gzb4)


def _rule_ids(row: dict | None) -> list[str]:
    if not row:
        return []
    out: list[str] = []
    for cls in ACTION_ORDER:
        out.extend(str(x) for x in row.get(cls, []))
    return out


def simulate_policy(
    candles: Iterable[dict],
    ledger: list[dict],
    friction_bps: float = 5.0,
) -> dict:
    """重放统一 V7 仓位策略和 C2 强制退出规则。"""
    bars = _validate_candles(candles)
    if len(bars) != len(ledger):
        raise ValueError("K 线数量与信号账本长度不一致")

    cash = 1.0
    shares = 0.0
    risk_armed = False
    cost_rate = float(friction_bps) / 10000.0

    markers: list[dict] = []
    positions: list[dict] = []
    equity_curve: list[float] = []
    execution_by_signal_date: dict[str, dict] = {}

    formal_index = next((i for i, b in enumerate(bars) if b["date"] >= POLICY_START_DATE), 0)
    # 日线研究数据在 2020 年前已有多年预热数据；较短的盘中周期也必须先满足最小预热根数，再开始重放仓位动作。
    warmup_index = min(MIN_WARMUP_BARS, len(bars) - 1)
    start_index = max(formal_index, warmup_index)
    policy_start_key = bars[start_index]["date"]

    for j, bar in enumerate(bars):
        if j < start_index:
            equity_curve.append(1.0)
            positions.append({"date": bar["date"], "fraction": 0.0, "risk_armed": False})
            continue

        op = float(bar["open"])
        cl = float(bar["close"])
        pre_equity = cash + shares * op
        if pre_equity <= 0:
            raise RuntimeError("账户权益不得为零或负数")

        position_value = shares * op
        current_fraction = position_value / pre_equity
        signal = ledger[j - 1] if j > start_index else None

        hard = bool(shares > 1e-14 and risk_armed and c2_condition(signal))
        action = resolve_action(signal)
        order_value = 0.0
        ordinary_action = None
        side = None

        if hard:
            order_value = -position_value
            side = "X"
        else:
            ordinary_action = action
            if action == "BUY":
                desired_fraction = 0.25 if shares <= 1e-14 else min(1.0, current_fraction + 0.25)
                desired_fraction = max(current_fraction, desired_fraction)
                order_value = desired_fraction * pre_equity - position_value
                side = "B"
            elif action == "SELL" and shares > 0:
                order_value = -position_value * 0.25
                side = "S"

        if order_value > 1e-14:
            max_buy = max(0.0, cash / (1.0 + cost_rate))
            order_value = min(order_value, max_buy)
        elif order_value < -1e-14:
            order_value = max(order_value, -position_value)

        executed = abs(order_value) > 1e-14
        if executed:
            cost = abs(order_value) * cost_rate
            shares += order_value / op
            cash -= order_value + cost
            if shares <= 1e-12:
                shares = 0.0

        if hard and executed:
            risk_armed = False
        elif executed and ordinary_action == "SELL" and order_value < 0:
            risk_armed = True
        elif executed and ordinary_action == "BUY" and order_value > 0:
            risk_armed = False

        close_equity = cash + shares * cl
        close_fraction = (shares * cl / close_equity) if close_equity > 0 else 0.0
        equity_curve.append(close_equity)
        positions.append(
            {
                "date": bar["date"],
                "fraction": max(0.0, min(1.0, close_fraction)),
                "risk_armed": risk_armed,
            }
        )

        if executed and signal is not None and side:
            marker = {
                "signal_date": signal["date"],
                "execution_date": bar["date"],
                "price": op,
                "side": side,
                "action": "HARD_EXIT" if hard else str(ordinary_action),
                "rule_ids": _rule_ids(signal),
                "rule_names_zh": rule_names_zh(_rule_ids(signal)),
                "position_after": max(0.0, min(1.0, close_fraction)),
                "risk_after": "ARMED" if risk_armed else "NORMAL",
            }
            markers.append(marker)
            execution_by_signal_date[signal["date"]] = marker

    events: list[dict] = []
    for row in ledger:
        if row["date"] < policy_start_key:
            continue
        classes = action_classes(row)
        if not classes:
            continue
        resolved = resolve_action(row)
        label = resolved or ("MIXED" if len(classes) > 1 else "NONE")
        execution = execution_by_signal_date.get(row["date"])
        if execution and execution["action"] == "HARD_EXIT":
            label = "HARD_EXIT"
        events.append(
            {
                "date": row["date"],
                "state": row["color"],
                "age": row["run_age"],
                "origin": row["origin"],
                "action": label,
                "rule_ids": _rule_ids(row),
                "rule_names_zh": rule_names_zh(_rule_ids(row)),
                "action_zh": ACTION_NAMES_ZH.get(label, label),
                "state_zh": STATE_NAMES_ZH.get(str(row["color"]), str(row["color"])),
                "lower_subtype": row["lower_subtype"],
                "upper_subtype": row["upper_subtype"],
                "execution_date": execution["execution_date"] if execution else None,
                "execution_price": execution["price"] if execution else None,
                "position_after": execution["position_after"] if execution else None,
                "risk_after": execution["risk_after"] if execution else None,
            }
        )

    return {
        "markers": markers,
        "positions": positions,
        "equity_curve": equity_curve,
        "events": events,
        "cash": cash,
        "shares": shares,
        "risk_armed": risk_armed,
        "position_fraction": positions[-1]["fraction"] if positions else 0.0,
        "final_equity": equity_curve[-1] if equity_curve else 1.0,
    }


def next_action_text(row: dict, position_fraction: float, risk_armed: bool) -> tuple[str, str]:
    if risk_armed and c2_condition(row):
        return "HARD_EXIT", "C2 已触发：下一根所选周期 K 线开盘清空全部剩余仓位"

    classes = action_classes(row)
    action = resolve_action(row)
    if len(classes) > 1:
        return "MIXED", "同一根 K 线出现冲突动作：不调整仓位"
    if action == "BUY":
        if position_fraction <= 1e-9:
            return "BUY", "下一根所选周期 K 线开盘建立约 25% 仓位"
        return "BUY", "下一根所选周期 K 线开盘增加约 25 个百分点，上限 100%"
    if action == "SELL":
        return "SELL", "下一根所选周期 K 线开盘卖出当前仓位的 25%，执行后进入“已警戒”状态"
    if action == "HOLD":
        return "HOLD", "保持当前仓位，不下新订单"
    if action == "WAIT":
        return "WAIT", "等待，不开仓也不主动减仓"
    return "NONE", "当前没有新的 SLTD 执行动作"


def build_snapshot(symbol: str, ledger: list[dict], simulation: dict) -> StrategySnapshot:
    row = ledger[-1]
    position = float(simulation["position_fraction"])
    armed = bool(simulation["risk_armed"])
    action, text = next_action_text(row, position, armed)
    return StrategySnapshot(
        symbol=symbol,
        latest_date=str(row["date"]),
        latest_close=float(row["close"]),
        state=str(row["color"]),
        run_age=int(row["run_age"]),
        age_bucket=str(row["age"]),
        origin=str(row["origin"]) if row["origin"] is not None else None,
        resolved_action=action,
        rule_ids=tuple(_rule_ids(row)),
        position_fraction=position,
        risk_state="ARMED" if armed else "NORMAL",
        next_action=text,
    )


def analyze(symbol: str, candles: Iterable[dict], display_limit: int = 300, timeframe: str = "1d") -> dict:
    bars = _validate_candles(candles)
    ledger = build_ledger(bars, symbol)
    simulation = simulate_policy(bars, ledger, friction_bps=5.0)
    snapshot = build_snapshot(symbol, ledger, simulation)

    limit = max(80, min(int(display_limit), 500))
    start = max(0, len(bars) - limit)
    position_by_date = {x["date"]: x for x in simulation["positions"]}

    chart = []
    for i in range(start, len(bars)):
        bar = bars[i]
        row = ledger[i]
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
                "BD": row["BD"],
                "position": float(pos.get("fraction") or 0.0),
                "risk_armed": bool(pos.get("risk_armed")),
            }
        )

    visible_dates = {x["date"] for x in chart}
    markers = [m for m in simulation["markers"] if m["execution_date"] in visible_dates]

    return {
        "strategy": {
            "id": "v7",
            "selector_label": "SLTD",
            "version": STRATEGY_VERSION,
            "source_commit": STRATEGY_SOURCE_COMMIT,
            "position_policy": POSITION_POLICY_ID,
            "position_policy_zh": POSITION_POLICY_NAME_ZH,
            "hard_exit": HARD_EXIT_ID,
            "hard_exit_zh": HARD_EXIT_NAME_ZH,
            "active_rule_count": sum(len(x) for x in ACTIVE_RULES.values()),
            "active_rules": ACTIVE_RULES,
            "active_rules_zh": {
                cls: rule_names_zh(ids) for cls, ids in ACTIVE_RULES.items()
            },
            "removed_v6_rules": REMOVED_V6_RULES,
            "removed_v6_rules_zh": [
                REMOVED_V6_RULE_NAMES_ZH.get(x, x) for x in REMOVED_V6_RULES
            ],
            "display_candles": limit,
            "policy_start_date": POLICY_START_DATE,
            "timeframe": str(timeframe),
            "bar_close_contract": "CONFIRMED_ON_SELECTED_BAR_CLOSE_EXECUTE_ON_NEXT_SELECTED_BAR_OPEN",
            "bar_close_contract_zh": "所选周期 K 线结束后确认信号，并在下一根同周期 K 线开盘执行",
            "rules_title_zh": "SLTD V7 当前 12 条规则",
            "policy_title_zh": "统一仓位 / 退出执行策略",
            "summary_state_label_zh": "C2 风险状态",
            "policy_steps_zh": [
                "① 首次买入：空仓 → 25%",
                "② 后续买入：每次 +25 个百分点，最高 100%",
                "③ 普通卖出：卖当前仓位 25%",
                "④ 卖出后：C2 风险状态 → 已警戒",
                "⑤ C2：已警戒 + 绿色 + 最高价低于 GZB4",
                "⑥ 下一根所选周期 K 线开盘全部清仓 → 0%",
            ],
        },
        "snapshot": {
            "symbol": snapshot.symbol,
            "latest_date": snapshot.latest_date,
            "latest_close": snapshot.latest_close,
            "state": snapshot.state,
            "run_age": snapshot.run_age,
            "age_bucket": snapshot.age_bucket,
            "origin": snapshot.origin,
            "resolved_action": snapshot.resolved_action,
            "rule_ids": list(snapshot.rule_ids),
            "rule_names_zh": rule_names_zh(snapshot.rule_ids),
            "resolved_action_zh": ACTION_NAMES_ZH.get(snapshot.resolved_action, snapshot.resolved_action),
            "state_zh": STATE_NAMES_ZH.get(snapshot.state, snapshot.state),
            "position_fraction": snapshot.position_fraction,
            "risk_state": snapshot.risk_state,
            "risk_state_zh": RISK_NAMES_ZH.get(snapshot.risk_state, snapshot.risk_state),
            "risk_sub_zh": "等待 C2 条件或后续实际买入重置" if snapshot.risk_state == "ARMED" else "正常监测",
            "next_action": snapshot.next_action,
            "GZB4": ledger[-1]["GZB4"],
            "ZD1": ledger[-1]["ZD1"],
            "ZK1": ledger[-1]["ZK1"],
            "BS": ledger[-1]["BS"],
            "BD": ledger[-1]["BD"],
        },
        "chart": chart,
        "markers": markers,
        "events": simulation["events"][-60:],
    }
