from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from strategy.frozen_signal_engine import evaluate_candles
from strategy import e_strategy, ssss_strategy


STRATEGY_5S = "5s_crypto_v1"
STRATEGY_E = "e"  # legacy only; no longer registered for new trading
STRATEGY_SSSS = "ssss"


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
        description="原始富途 SSSS.ftindex：图标 9 每次买入 25%，图标 15 全部清仓；同根同时出现时清仓优先。",
    ),
}


def strategy_ids() -> tuple[str, ...]:
    return tuple(_SPECS)


def get_spec(strategy_id: str) -> StrategySpec:
    key = str(strategy_id or "").strip().lower()
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


def _dict_bars(rows: list[Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in rows:
        if isinstance(row, dict):
            open_time = int(row.get("open_time", row.get("openTime")))
            o, h, l, c = row["open"], row["high"], row["low"], row["close"]
            volume = row.get("volume", 0)
        else:
            open_time = int(row[0])
            o, h, l, c, volume = row[1], row[2], row[3], row[4], row[5]
        stamp = open_time / 1000.0 if abs(open_time) >= 10_000_000_000 else float(open_time)
        out.append(
            {
                "date": datetime.fromtimestamp(stamp, tz=timezone.utc).isoformat(),
                "open_time": open_time,
                "open": float(o),
                "high": float(h),
                "low": float(l),
                "close": float(c),
                "volume": float(volume),
            }
        )
    return out


def decide_e(rows: list[Any], runtime: dict[str, Any], timeframe: str) -> StrategyDecision:
    spec = get_spec(STRATEGY_E)
    tf = str(timeframe).lower()
    if tf not in spec.supported_timeframes:
        raise ValueError(f"E 策略当前自动交易不支持周期：{tf}")

    primary = e_strategy._copy_validated(_dict_bars(rows))
    higher_tf, higher_bars = e_strategy.build_higher_bars(
        primary,
        tf,
        {"exchange_timezone": "UTC", "continuous_24_7": True},
    )
    if len(higher_bars) < e_strategy.E_MIN_WARMUP_BARS:
        raise ValueError(f"E 策略大周期 {higher_tf} 预热不足")

    primary_ledger = e_strategy.build_ledger(primary, "BINANCE")
    higher_ledger = e_strategy.build_ledger(higher_bars, f"BINANCE:{higher_tf}")
    i = len(primary) - 1
    h = -1
    for j, row in enumerate(higher_bars):
        if int(row["_source_end_index"]) <= i:
            h = j
        else:
            break
    higher_row = higher_ledger[h] if h >= e_strategy.E_MIN_WARMUP_BARS - 1 else None
    if i < e_strategy.E_MIN_WARMUP_BARS - 1 or higher_row is None:
        raise ValueError("E 策略主周期/大周期共同预热不足")

    fraction = min(max(float(runtime.get("current_fraction") or 0.0), 0.0), e_strategy.E_MAX_POSITION)
    state = _state(runtime)
    b1 = bool(state.get("b1_used", False))
    b2 = bool(state.get("b2_used", False))
    b3 = bool(state.get("b3_used", False))
    sell_stage = int(state.get("sell_stage", 0))
    row = primary_ledger[i]
    bar = primary[i]
    next_state = {"b1_used": b1, "b2_used": b2, "b3_used": b3, "sell_stage": sell_stage}

    steps: list[StrategyStep] = []
    signal = "HOLD"

    if fraction > 1e-12:
        inner_up = e_strategy._break_above_zk1(i, primary, primary_ledger)
        exit_active = sell_stage > 0 or inner_up
        band = e_strategy._band_touch(bar, row)
        bs = row.get("BS")
        bs_hit = bs is not None and float(bar["high"]) >= float(bs)

        if exit_active and band:
            signal = "E_SELL_3"
            steps.append(StrategyStep(
                "E_EXIT", "X100", 0.0,
                ("E_SELL_3_TOUCH_GZB_BAND_FULL_EXIT",), {}
            ))
        elif sell_stage > 0 and row.get("ZK1") is not None and float(bar["close"]) < float(row["ZK1"]):
            signal = "E_SELL_4"
            steps.append(StrategyStep(
                "E_EXIT", "X100", 0.0,
                ("E_SELL_4_CLOSE_BACK_BELOW_ZK1_FULL_EXIT",), {}
            ))
        elif exit_active and bs_hit:
            signal = "E_SELL_2"
            next_state["sell_stage"] = max(sell_stage, 2)
            steps.append(StrategyStep(
                "E_SELL_25PP", "S25", max(0.0, fraction - 0.25),
                ("E_SELL_2_TOUCH_BS_MINUS_25PP",), dict(next_state)
            ))
        elif sell_stage == 0 and inner_up:
            signal = "E_SELL_1"
            next_state["sell_stage"] = 1
            steps.append(StrategyStep(
                "E_SELL_50PP", "S50", max(0.0, fraction - 0.50),
                ("E_SELL_1_PRIMARY_CLOSE_BREAK_ABOVE_ZK1_MINUS_50PP",), dict(next_state)
            ))

    if not steps and sell_stage == 0:
        color = str(row.get("color") or "")
        inner_down = (
            not b1
            and color in {"BLUE", "GRAY"}
            and e_strategy._break_below_zd1(i, primary, primary_ledger)
        )
        if inner_down:
            ids = ["E_BUY_1_PRIMARY_CLOSE_BREAK_BELOW_ZD1"]
            delta = 0.25
            next_state["b1_used"] = True
            if (
                not b2
                and higher_row.get("ZD1") is not None
                and float(higher_row["close"]) < float(higher_row["ZD1"])
            ):
                ids.append("E_BUY_2_HIGHER_CLOSE_BELOW_ZD1")
                delta = 0.50
                next_state["b2_used"] = True
            target = min(e_strategy.E_MAX_POSITION, fraction + delta)
            signal = "E_BUY_1+E_BUY_2" if len(ids) == 2 else "E_BUY_1"
            steps.append(StrategyStep(
                "E_BUY", "B50" if delta > 0.25 else "B25", target,
                tuple(ids), dict(next_state)
            ))
        elif b1 and not b3 and e_strategy._band_touch(bar, row):
            next_state["b3_used"] = True
            signal = "E_BUY_3"
            steps.append(StrategyStep(
                "E_BUY", "B25", min(e_strategy.E_MAX_POSITION, fraction + 0.25),
                ("E_BUY_3_TOUCH_GZB_BAND",), dict(next_state)
            ))

    return StrategyDecision(
        strategy_id=STRATEGY_E,
        signal=signal,
        steps=tuple(steps),
        bar_open_time=int(primary[-1]["open_time"]),
    )


def decide_ssss(rows: list[Any], runtime: dict[str, Any], timeframe: str) -> StrategyDecision:
    spec = get_spec(STRATEGY_SSSS)
    tf = str(timeframe).lower()
    if tf not in spec.supported_timeframes:
        raise ValueError(f"SSSS 当前自动交易不支持周期：{tf}")

    evaluated = ssss_strategy.evaluate_ssss(rows)
    if not evaluated:
        raise ValueError("SSSS 原始指标没有返回计算结果")
    latest = evaluated[-1]
    fraction = min(max(float(runtime.get("current_fraction") or 0.0), 0.0), 1.0)
    state = _state(runtime)
    state.update({
        "source_sha256": ssss_strategy.source_sha256(),
        "last_icon_bar_open_time": int(latest.open_time),
    })

    steps: list[StrategyStep] = []
    signal = "HOLD"

    # User-frozen priority: if both icons somehow exist on one bar, exit wins.
    if latest.exit_icon_15:
        signal = "SSSS_EXIT_15"
        state["last_icon"] = 15
        if fraction > 1e-12:
            steps.append(StrategyStep(
                code="SSSS_EXIT_ALL",
                order_code="X100",
                target_fraction=0.0,
                rule_ids=("DRAWICON_15",),
                state_after={},
            ))
    elif latest.buy_icon_9:
        signal = "SSSS_BUY_9"
        state["last_icon"] = 9
        if fraction < 1.0 - 1e-12:
            target = min(1.0, fraction + 0.25)
            steps.append(StrategyStep(
                code="SSSS_BUY_25",
                order_code="B25",
                target_fraction=target,
                rule_ids=("DRAWICON_9",),
                state_after=dict(state),
            ))

    return StrategyDecision(
        strategy_id=STRATEGY_SSSS,
        signal=signal,
        steps=tuple(steps),
        bar_open_time=int(latest.open_time),
    )


def decide(strategy_id: str, rows: list[Any], runtime: dict[str, Any], timeframe: str) -> StrategyDecision:
    sid = get_spec(strategy_id).strategy_id
    if sid == STRATEGY_5S:
        return decide_5s(rows, runtime)
    if sid == STRATEGY_SSSS:
        return decide_ssss(rows, runtime, timeframe)
    raise ValueError(f"不支持的策略：{strategy_id}")


def strategy_signal_label(strategy_id: str, raw: object) -> str:
    text = str(raw or "").strip().upper()
    if not text:
        return "等待信号"
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
            "SSSS_BUY_9": "💰 买入 25%",
            "SSSS_EXIT_15": "人型图标·全部清仓",
            "HOLD": "观望",
        }
        return " + ".join(labels.get(part, part) for part in text.split("+"))
    return text
