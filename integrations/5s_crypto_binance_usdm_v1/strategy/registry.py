from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from strategy.frozen_signal_engine import evaluate_candles
from strategy import ssss_strategy, zbge_strategy


STRATEGY_5S = "5s_crypto_v1"
STRATEGY_SSSS = "ssss"
STRATEGY_ZBGE = "zbge_bs"
RETIRED_MFRA_ID = "matrixquant_pai"  # legacy ledger recognition only


@dataclass(frozen=True)
class StrategyStep:
    code: str
    order_code: str
    target_fraction: float
    rule_ids: tuple[str, ...]
    state_after: dict[str, Any]


@dataclass(frozen=True)
class StrategyDecision:
    strategy_id: str
    signal: str
    steps: tuple[StrategyStep, ...]
    bar_open_time: int
    metadata: dict[str, Any] | None = None
    state_after: dict[str, Any] | None = None

    @property
    def pending_action(self) -> str | None:
        return "+".join(step.code for step in self.steps) if self.steps else None


@dataclass(frozen=True)
class StrategySpec:
    strategy_id: str
    label: str
    supported_timeframes: tuple[str, ...]
    default_timeframe: str
    fetch_limit: int
    minimum_closed_bars: int
    max_fraction: float
    order_prefix: str
    description: str


_SPECS = {
    STRATEGY_5S: StrategySpec(
        strategy_id=STRATEGY_5S,
        label="5s Crypto V1",
        supported_timeframes=("3m", "5m", "15m", "1h", "2h", "4h", "6h", "12h", "1d"),
        default_timeframe="15m",
        fetch_limit=220,
        minimum_closed_bars=80,
        max_fraction=1.0,
        order_prefix="5sv1",
        description="冻结 5s Crypto V1：A/B 60% 开仓，W3 内 C 补至 100%，首个 SELL 全部退出。",
    ),
    STRATEGY_SSSS: StrategySpec(
        strategy_id=STRATEGY_SSSS,
        label="SSSS",
        supported_timeframes=("3m", "5m", "15m", "1h", "2h", "4h", "6h", "12h", "1d"),
        default_timeframe="15m",
        fetch_limit=1000,
        minimum_closed_bars=180,
        max_fraction=1.0,
        order_prefix="ssss",
        description="原始SSSS：💰仅蓝带或绿转灰可买；首买初始资金25%，后买剩余资金25%；首次💥高于成本卖75%、下一次全清；中途💰重置卖出阶段。",
    ),
    STRATEGY_ZBGE: StrategySpec(
        strategy_id=STRATEGY_ZBGE,
        label="ZBGE B/S",
        supported_timeframes=("3m", "5m", "15m", "1h", "2h", "4h", "6h", "12h", "1d"),
        default_timeframe="4h",
        fetch_limit=1000,
        minimum_closed_bars=180,
        max_fraction=1.0,
        order_prefix="zbge",
        description="B：黄柱+趋势线<20+ZBGE8>15，每次初始资金25%；S：跟随主力>75或连续第3根笑脸，先卖75%再清仓，高于实际持仓成本才卖。",
    ),
}


_RETIRED_MFRA_SPEC = StrategySpec(
    strategy_id=RETIRED_MFRA_ID,
    label="PAI 已停用（请清仓后切换）",
    supported_timeframes=("3m", "5m", "15m", "1h", "2h", "4h", "6h", "12h", "1d"),
    default_timeframe="4h", fetch_limit=1000, minimum_closed_bars=250,
    max_fraction=1.0, order_prefix="mfra",
    description="仅识别旧数据库的策略持仓与订单；禁止新建 PAI 交易。",
)


def strategy_ids() -> tuple[str, ...]:
    return tuple(_SPECS)


def get_spec(strategy_id: str) -> StrategySpec:
    key = str(strategy_id or "").strip().lower()
    if key == RETIRED_MFRA_ID:
        return _RETIRED_MFRA_SPEC
    try:
        return _SPECS[key]
    except KeyError as exc:
        raise ValueError(f"不支持的策略：{strategy_id}") from exc


def strategy_options(selected: str) -> tuple[tuple[str, str, bool], ...]:
    return tuple((sid, spec.label, sid == selected) for sid, spec in _SPECS.items())


def _state(runtime: dict[str, Any]) -> dict[str, Any]:
    value = runtime.get("strategy_state")
    if isinstance(value, dict):
        return dict(value)
    return {}


def _five_s_state(runtime: dict[str, Any]) -> dict[str, Any]:
    state = _state(runtime)
    if state:
        return state
    out: dict[str, Any] = {}
    if runtime.get("entry_signal_open_time") is not None:
        out["entry_signal_open_time"] = int(runtime["entry_signal_open_time"])
    if runtime.get("entry_family"):
        out["entry_family"] = str(runtime["entry_family"])
    out["c_confirmed"] = bool(runtime.get("c_confirmed"))
    return out


def decide_5s(rows: list[Any], runtime: dict[str, Any]) -> StrategyDecision:
    evaluations = evaluate_candles(rows)
    if not evaluations:
        raise ValueError("冻结 5s 信号引擎没有返回结果")
    latest = evaluations[-1]
    fraction = min(max(float(runtime.get("current_fraction") or 0.0), 0.0), 1.0)
    state = _five_s_state(runtime)
    entry_time = state.get("entry_signal_open_time")
    c_confirmed = bool(state.get("c_confirmed"))
    buy = tuple(latest.buy_onsets)
    sell = tuple(latest.sell_onsets)
    closed_times = [int(x.open_time) for x in evaluations]

    steps: list[StrategyStep] = []
    labels: list[str] = []
    working_fraction = fraction
    working_state = dict(state)

    c_eligible = False
    if (
        working_fraction > 0.0
        and working_fraction < 1.0
        and not c_confirmed
        and "C" in buy
        and entry_time is not None
    ):
        try:
            entry_index = closed_times.index(int(entry_time))
            distance = len(closed_times) - 1 - entry_index
            c_eligible = 1 <= distance <= 3
        except (ValueError, TypeError):
            c_eligible = False

    if working_fraction > 0.0:
        if c_eligible:
            working_state["c_confirmed"] = True
            working_fraction = 1.0
            labels.append("BUY_C")
            steps.append(
                StrategyStep(
                    code="5S_TOPUP_TO_100",
                    order_code="B40",
                    target_fraction=1.0,
                    rule_ids=("BUY_C",),
                    state_after=dict(working_state),
                )
            )
        if sell:
            label = "MULTI_SELL" if len(sell) >= 2 else f"SELL_{sell[0]}"
            labels.append(label)
            steps.append(
                StrategyStep(
                    code="5S_SELL_ALL",
                    order_code="S100",
                    target_fraction=0.0,
                    rule_ids=tuple(f"SELL_{x}" for x in sell),
                    state_after={},
                )
            )
    else:
        initial = [x for x in buy if x in ("A", "B")]
        if initial and not sell:
            family = initial[0]
            next_state = {
                "c_confirmed": False,
                "entry_signal_open_time": int(latest.open_time),
                "entry_family": family,
            }
            labels.append(f"BUY_{family}")
            steps.append(
                StrategyStep(
                    code="5S_BUY_60",
                    order_code="B60",
                    target_fraction=0.60,
                    rule_ids=(f"BUY_{family}",),
                    state_after=next_state,
                )
            )

    return StrategyDecision(
        strategy_id=STRATEGY_5S,
        signal="+".join(labels) if labels else "HOLD",
        steps=tuple(steps),
        bar_open_time=int(latest.open_time),
    )


def _ssss_event_key(timeframe: str, icon_id: int, open_time: int) -> str:
    return f"{str(timeframe).lower()}:{int(icon_id)}:{int(open_time)}"


def _ssss_event_parts(key: object) -> tuple[str, int, int] | None:
    parts = str(key).split(":")
    if len(parts) != 3:
        return None
    try:
        icon_id = int(parts[1])
        open_time = int(parts[2])
    except (TypeError, ValueError):
        return None
    if icon_id not in (9, 15):
        return None
    return parts[0].lower(), icon_id, open_time


def _ssss_event_open_time(key: object) -> int | None:
    parts = _ssss_event_parts(key)
    return int(parts[2]) if parts is not None else None


def _ssss_event_icon_id(key: object) -> int | None:
    parts = _ssss_event_parts(key)
    return int(parts[1]) if parts is not None else None


def _ssss_events(analysis, timeframe: str) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for bar in analysis.bars:
        open_time = int(bar.open_time)
        if bool(bar.buy_icon_9):
            events.append({
                "key": _ssss_event_key(timeframe, 9, open_time),
                "icon_id": 9,
                "open_time": open_time,
            })
        if bool(bar.exit_icon_15):
            events.append({
                "key": _ssss_event_key(timeframe, 15, open_time),
                "icon_id": 15,
                "open_time": open_time,
            })
    events.sort(key=lambda item: (int(item["open_time"]), int(item["icon_id"])))
    return events


def baseline_ssss_state(rows: list[Any], timeframe: str) -> dict[str, Any]:
    """Snapshot all currently visible SSSS icons without creating trades."""
    tf = str(timeframe).lower()
    analysis = ssss_strategy.analyze_ssss(rows)
    events = _ssss_events(analysis, tf)
    latest = analysis.latest
    return {
        "signal_tracker_initialized": True,
        "tracker_timeframe": tf,
        "source_sha256": ssss_strategy.source_sha256(),
        "seen_icon_events": [str(item["key"]) for item in events],
        "last_detection_bar_open_time": int(latest.open_time) if latest is not None else None,
    }


def ssss_tracker_matches(runtime: dict[str, Any], timeframe: str) -> bool:
    state = _state(runtime)
    return (
        bool(state.get("signal_tracker_initialized"))
        and str(state.get("tracker_timeframe") or "").lower() == str(timeframe).lower()
        and str(state.get("source_sha256") or "") == ssss_strategy.source_sha256()
        and isinstance(state.get("seen_icon_events"), list)
    )


def decide_ssss(rows: list[Any], runtime: dict[str, Any], timeframe: str) -> StrategyDecision:
    """Only newly detected icons on the LAST closed candle may create orders.

    XMA may repaint older source candles: record such events in the tracker
    and event ledger but NEVER turn a retrospective repaint into a new order.
    """
    spec = get_spec(STRATEGY_SSSS)
    tf = str(timeframe).lower()
    if tf not in spec.supported_timeframes:
        raise ValueError(f"SSSS 当前自动交易不支持周期：{tf}")
    analysis = ssss_strategy.analyze_ssss(rows)
    latest = analysis.latest
    if latest is None:
        raise ValueError("SSSS 原始指标没有返回计算结果")

    fraction = min(max(float(runtime.get("current_fraction") or 0.0), 0.0), 1.0)
    state = _state(runtime)
    stage = 1 if int(state.get("sell_stage") or 0) == 1 else 0
    # Gray may last many bars: its parent is the latest PREVIOUS non-gray
    # band (BLUE or GREEN), not just the immediately previous candle.
    band = ssss_strategy.band_state(latest.values)
    prior_non_gray = None
    for previous in reversed(analysis.bars[:-1]):
        old_band = ssss_strategy.band_state(previous.values)
        if old_band != "GRAY":
            prior_non_gray = old_band
            break
    buy_color_allowed = band == "BLUE" or (
        band == "GRAY" and prior_non_gray == "GREEN"
    )
    events = _ssss_events(analysis, tf)
    earliest_open_time = int(analysis.bars[0].open_time)
    latest_open_time = int(latest.open_time)
    seen_before = {
        str(key) for key in (state.get("seen_icon_events") or [])
        if _ssss_event_parts(key) is not None
        and str(_ssss_event_parts(key)[0]).lower() == tf
        and int(_ssss_event_parts(key)[2]) >= earliest_open_time
    }
    new_events = [e for e in events if str(e["key"]) not in seen_before]
    eligible = [e for e in new_events if int(e["open_time"]) == latest_open_time]
    late = [e for e in new_events if int(e["open_time"]) < latest_open_time]
    seen_after = seen_before | {str(e["key"]) for e in events}
    state.update({
        "signal_tracker_initialized": True,
        "tracker_timeframe": tf,
        "source_sha256": ssss_strategy.source_sha256(),
        "seen_icon_events": sorted(
            seen_after,
            key=lambda key: (
                int(_ssss_event_open_time(key) or 0),
                int(_ssss_event_icon_id(key) or 0),
            ),
        ),
        "last_detection_bar_open_time": latest_open_time,
    })

    # If a bar simultaneously has buy and exit icons, exit always wins.
    exits = [e for e in eligible if int(e["icon_id"]) == 15]
    buys = [e for e in eligible if int(e["icon_id"]) == 9]
    steps: list[StrategyStep] = []
    signal = "HOLD"
    if exits:
        signal = "SSSS_EXIT_15"
        state["last_icon"] = 15
        state["last_icon_bar_open_time"] = latest_open_time
        if fraction > 1e-12:
            cost = runtime.get("position_entry_price")
            if cost is None or float(cost) <= 0:
                signal = "SSSS_EXIT_COST_UNAVAILABLE"
            elif float(latest.close) <= float(cost):
                signal = "SSSS_EXIT_BELOW_COST"
            else:
                first = stage == 0
                target = round(fraction * .25, 10) if first else 0.0
                next_state = {**state, "sell_stage": 1 if first else 0}
                steps.append(StrategyStep(
                    code="SSSS_SELL_75" if first else "SSSS_EXIT_ALL",
                    order_code="S75" if first else "X100",
                    target_fraction=target,
                    rule_ids=(f"DRAWICON_15:{latest_open_time}",),
                    state_after=next_state,
                ))
    elif buys:
        signal = "SSSS_BUY_9"
        state["last_icon"] = 9
        state["last_icon_bar_open_time"] = latest_open_time
        if not buy_color_allowed:
            signal = "SSSS_BUY_COLOR_BLOCKED"
        else:
            # First B in a flat cycle: 25% of the configured initial budget.
            # Later B: 25% of the *remaining* strategy allocation.
            # A B after first successful S: a fresh 25% initial-budget buy
            # and reset sell_stage=0 ONLY after the B is actually FILLED.
            from_initial_budget = fraction <= 1e-12 or stage == 1
            added_fraction = .25 if from_initial_budget else (1.0 - fraction) * .25
            target = min(1.0, round(fraction + added_fraction, 10))
            if added_fraction <= 1e-10 or target - fraction <= 1e-10 or target > 1.0 + 1e-10:
                signal = "SSSS_BUY_BUDGET_EXHAUSTED"
            elif added_fraction > 1.0 - fraction + 1e-10:
                signal = "SSSS_BUY_BUDGET_EXHAUSTED"
            else:
                next_state = {**state, "sell_stage": 0} if stage == 1 else dict(state)
                steps.append(StrategyStep(
                    code="SSSS_BUY_25", order_code="B25",
                    target_fraction=target,
                    rule_ids=(
                        f"DRAWICON_9:{latest_open_time}",
                        f"BAND_{band}", f"PRIOR_BAND_{prior_non_gray or 'NONE'}",
                        "INITIAL_25" if from_initial_budget else "REMAINING_25",
                    ),
                    state_after=next_state,
                ))

    metadata = {
        "buy_icon_9": bool(latest.buy_icon_9),
        "exit_icon_15": bool(latest.exit_icon_15),
        "analysis_bar_count": len(analysis.bars),
        "source_sha256": ssss_strategy.source_sha256(),
        "new_icon_events": [str(e["key"]) for e in new_events],
        "actionable_icon_events": [str(e["key"]) for e in eligible],
        "late_icon_events": [str(e["key"]) for e in late],
        "new_buy_count": len(buys),
        "new_exit_count": len(exits),
        "late_event_count": len(late),
        "detection_bar_open_time": latest_open_time,
        "source_signal_bar_open_time": latest_open_time if eligible else None,
        "signal_close": float(latest.close),
        "sell_stage": stage,
        "band_state": band,
        "preceding_non_gray_band": prior_non_gray,
        "buy_color_allowed": buy_color_allowed,
    }
    return StrategyDecision(
        strategy_id=STRATEGY_SSSS, signal=signal,
        steps=tuple(steps), bar_open_time=latest_open_time,
        metadata=metadata, state_after=dict(state),
    )

def decide_zbge(rows: list[Any], runtime: dict[str, Any], timeframe: str) -> StrategyDecision:
    """Fixed 25%-of-initial-budget B, 75% then all S, with strict cost guard."""
    spec = get_spec(STRATEGY_ZBGE)
    if str(timeframe).lower() not in spec.supported_timeframes:
        raise ValueError(f"ZBGE B/S 不支持周期：{timeframe}")
    points = zbge_strategy.evaluate_zbge(rows)
    if len(points) < spec.minimum_closed_bars:
        raise ValueError("ZBGE 已收盘 K 线不足")
    latest = points[-1]
    fraction = min(max(float(runtime.get("current_fraction") or 0.0), 0.0), 1.0)
    state = _state(runtime)
    stage = 1 if int(state.get("sell_stage") or 0) == 1 else 0
    steps: list[StrategyStep] = []
    signal = "HOLD"
    if latest.sell:
        signal = "ZBGE_SELL_A" if latest.sell_a else "ZBGE_SELL_B"
        if fraction > 1e-12:
            cost = runtime.get("position_entry_price")
            if cost is None or float(cost) <= 0:
                signal = "ZBGE_S_COST_UNAVAILABLE"
            elif latest.close <= float(cost):
                signal = "ZBGE_S_BELOW_COST"
            else:
                first = stage == 0
                target = round(fraction * .25, 10) if first else 0.0
                next_state = {**state, "sell_stage": 1} if first else {}
                steps.append(StrategyStep(
                    code="ZBGE_SELL_75" if first else "ZBGE_SELL_ALL",
                    order_code="S75" if first else "X100",
                    target_fraction=target,
                    rule_ids=tuple(
                        key for key, ok in (
                            ("FOLLOW_MAIN_TREND_GT75", latest.sell_a),
                            ("SMILE_STREAK_EQ3", latest.sell_b),
                        ) if ok
                    ),
                    state_after=next_state,
                ))
    elif latest.buy:
        signal = "ZBGE_BUY_B"
        # Never use a partial 25% purchase; use the configured initial budget.
        if fraction <= .75 + 1e-12:
            steps.append(StrategyStep(
                code="ZBGE_BUY_25", order_code="B25",
                target_fraction=round(fraction + .25, 10),
                rule_ids=("YELLOW", "TREND_LT20", "ZBGE8_GT15"),
                state_after=dict(state),
            ))
        else:
            signal = "ZBGE_B_INSUFFICIENT_BUDGET"
    return StrategyDecision(
        strategy_id=STRATEGY_ZBGE, signal=signal,
        steps=tuple(steps), bar_open_time=int(latest.open_time),
        metadata={
            "trend": latest.trend, "absorption": latest.absorption,
            "yellow": latest.yellow, "smile_count": latest.smile_count,
            "buy": latest.buy, "sell_a": latest.sell_a, "sell_b": latest.sell_b,
            "signal_close": latest.close,
        },
        state_after=dict(state),
    )

def decide(strategy_id: str, rows: list[Any], runtime: dict[str, Any], timeframe: str) -> StrategyDecision:
    sid = get_spec(strategy_id).strategy_id
    if sid == STRATEGY_5S:
        return decide_5s(rows, runtime)
    if sid == STRATEGY_SSSS:
        return decide_ssss(rows, runtime, timeframe)
    if sid == STRATEGY_ZBGE:
        return decide_zbge(rows, runtime, timeframe)
    if sid == RETIRED_MFRA_ID:
        raise ValueError("MatrixQuant PAI 已停用；请停止旧策略、核对持仓并切换至 ZBGE B/S")
    raise ValueError(f"不支持的策略：{strategy_id}")


def strategy_signal_label(strategy_id: str, raw: object) -> str:
    text = str(raw or "").strip().upper()
    if not text:
        return "观望" if strategy_id == STRATEGY_SSSS else "等待信号"
    if strategy_id == STRATEGY_5S:
        labels = {
            "BUY_A": "买入信号一",
            "BUY_B": "买入信号二",
            "BUY_C": "补仓信号三",
            "SELL_A": "卖出信号一",
            "SELL_B": "卖出信号二",
            "SELL_C": "卖出信号三",
            "MULTI_SELL": "多重卖出",
            "HOLD": "观望",
        }
        return " + ".join(labels.get(part, part) for part in text.split("+"))
    if strategy_id == STRATEGY_SSSS:
        labels = {
            "SSSS_BUY_9": "买入 25%",
            "SSSS_EXIT_15": "高于成本则先卖75%，下次全清",
            "SSSS_EXIT_BELOW_COST": "💥低于持仓成本，等待下次有效💥",
            "SSSS_BUY_COLOR_BLOCKED": "💰理论买点被彩色带过滤，未交易",
            "SSSS_EXIT_COST_UNAVAILABLE": "无法核对平均成本，停止卖出",
            "SSSS_BUY_BUDGET_EXHAUSTED": "策略资金不足，跳过💰",
            "HOLD": "观望",
        }
        return " + ".join(labels.get(part, part) for part in text.split("+"))
    if strategy_id == STRATEGY_ZBGE:
        labels = {
            "ZBGE_BUY_B": "B 买入初始资金25%",
            "ZBGE_SELL_A": "S 卖出",
            "ZBGE_SELL_B": "S 卖出",
            "ZBGE_S_BELOW_COST": "S 不高于持仓成本，等待下次",
            "ZBGE_S_COST_UNAVAILABLE": "无法核对成本，停止卖出",
            "ZBGE_B_INSUFFICIENT_BUDGET": "初始策略资金不足，跳过 B",
            "HOLD": "观望",
        }
        return " + ".join(labels.get(part, part) for part in text.split("+"))
    return text
