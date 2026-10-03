from __future__ import annotations

"""Experimental SLTD sell stack.

Purpose
-------
Keep the frozen SLTD entry rules intact while adding two independent exit layers:

1) Vespa314/chan.py current-frame sell points for partial, graded de-risking.
2) Chandelier Exit (22, 3) as a final protective full exit.

This module is intentionally separate from the frozen V7 baseline simulator so
the 79-stock study can compare the old and new exit policies on identical
entries and data.

Execution contract
------------------
- All decisions are confirmed on a completed bar.
- Orders execute at the next bar open.
- Chandelier uses a long stop based on rolling highest high minus 3 * Wilder ATR.
- The live stop is ratcheted upward while a position is open; it never loosens.
- chan.py signals are discovered incrementally through trigger_load.
- Multiple chan.py sell classes on the same bar do not compound; the strongest
  configured fraction for that bar is used.
"""

from dataclasses import dataclass
from math import isfinite
from typing import Iterable

import strategy as sltd


CHANPY_UPSTREAM_SHA = "429d6ed3043e27c93a003ba2b10e70a05575e1f5"
CHANDELIER_LOOKBACK = 22
CHANDELIER_MULTIPLIER = 3.0


@dataclass(frozen=True)
class ExitStackConfig:
    name: str
    chan_levels: str = "all"          # none | l0 | l1 | all
    chan_certainty: str = "any"       # any | sure
    chan_fraction_mode: str = "graded"  # flat25 | graded
    chandelier: bool = True
    chandelier_lookback: int = CHANDELIER_LOOKBACK
    chandelier_multiplier: float = CHANDELIER_MULTIPLIER


def _wilder_atr(bars: list[dict], period: int) -> list[float | None]:
    if period <= 0:
        raise ValueError("ATR period must be positive")
    trs: list[float] = []
    for i, bar in enumerate(bars):
        high = float(bar["high"])
        low = float(bar["low"])
        if i == 0:
            tr = high - low
        else:
            prev_close = float(bars[i - 1]["close"])
            tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
        trs.append(tr)

    out: list[float | None] = [None] * len(bars)
    if len(bars) < period:
        return out

    prev = sum(trs[:period]) / period
    out[period - 1] = prev
    for i in range(period, len(bars)):
        prev = ((period - 1) * prev + trs[i]) / period
        out[i] = prev
    return out


def chandelier_long(
    candles: Iterable[dict],
    *,
    lookback: int = CHANDELIER_LOOKBACK,
    multiplier: float = CHANDELIER_MULTIPLIER,
) -> list[float | None]:
    bars = sltd._validate_candles(candles)
    if lookback <= 0:
        raise ValueError("Chandelier lookback must be positive")
    if multiplier <= 0:
        raise ValueError("Chandelier multiplier must be positive")

    atr = _wilder_atr(bars, lookback)
    out: list[float | None] = [None] * len(bars)
    for i in range(lookback - 1, len(bars)):
        if atr[i] is None:
            continue
        highest = max(float(x["high"]) for x in bars[i - lookback + 1 : i + 1])
        out[i] = highest - float(multiplier) * float(atr[i])
    return out


def _load_chanpy():
    # chan_strategy is the V7 adapter.  CI/package vendors the exact upstream
    # commit before importing it.
    import chan_strategy as chan

    if chan.CHANPY_UPSTREAM_SHA != CHANPY_UPSTREAM_SHA:
        raise RuntimeError(
            f"Unexpected chan.py pin: {chan.CHANPY_UPSTREAM_SHA}"
        )
    return chan


def build_chan_sell_observations(
    symbol: str,
    candles: Iterable[dict],
) -> list[dict]:
    """Incrementally discover first-any and first-sure chan.py sell observations.

    The final rows are keyed by (level, anchor_index, type).  A point can first
    exist on a virtual structure and later become sure; both timestamps are
    retained so the 79-stock study can compare real-time responsiveness against
    confirmation-only behavior without rerunning the upstream engine.
    """
    bars = sltd._validate_candles(candles)
    chan = _load_chanpy()

    engine = chan.CChan(
        code=symbol,
        lv_list=[chan.KL_TYPE.K_DAY],
        config=chan.CChanConfig({"trigger_step": True}),
        autype=chan.AUTYPE.NONE,
    )

    store: dict[tuple[int, int, str], dict] = {}

    for i, row in enumerate(bars):
        engine.trigger_load({chan.KL_TYPE.K_DAY: [chan._klu(row)]})
        kl = engine[0]

        for level, bsp_list in (
            (0, kl.bs_point_lst),
            (1, kl.seg_bs_point_lst),
        ):
            for point in bsp_list.getSortedBspList():
                if bool(point.is_buy):
                    continue
                anchor_index = int(point.klu.idx)
                sure = bool(point.bi.is_sure)
                for bsp_type in point.type:
                    kind = f"S{str(bsp_type.value).upper()}"
                    key = (level, anchor_index, kind)
                    item = store.get(key)
                    if item is None:
                        item = {
                            "symbol": symbol,
                            "level": level,
                            "kind": kind,
                            "anchor_index": anchor_index,
                            "anchor_date": bars[anchor_index]["date"],
                            "first_any_index": i,
                            "first_any_date": bars[i]["date"],
                            "first_any_sure": sure,
                            "first_sure_index": None,
                            "first_sure_date": None,
                        }
                        store[key] = item
                    if sure and item["first_sure_index"] is None:
                        item["first_sure_index"] = i
                        item["first_sure_date"] = bars[i]["date"]

    return sorted(
        store.values(),
        key=lambda x: (
            int(x["first_any_index"]),
            int(x["level"]),
            int(x["anchor_index"]),
            str(x["kind"]),
        ),
    )


def chan_events_by_signal_index(
    observations: list[dict],
    *,
    levels: str,
    certainty: str,
) -> dict[int, list[dict]]:
    if levels not in {"none", "l0", "l1", "all"}:
        raise ValueError(levels)
    if certainty not in {"any", "sure"}:
        raise ValueError(certainty)

    result: dict[int, list[dict]] = {}
    if levels == "none":
        return result

    for obs in observations:
        level = int(obs["level"])
        if levels == "l0" and level != 0:
            continue
        if levels == "l1" and level != 1:
            continue

        if certainty == "any":
            index = obs["first_any_index"]
            date = obs["first_any_date"]
            observed_sure = bool(obs["first_any_sure"])
        else:
            index = obs["first_sure_index"]
            date = obs["first_sure_date"]
            observed_sure = True
        if index is None:
            continue

        event = dict(obs)
        event["signal_index"] = int(index)
        event["signal_date"] = str(date)
        event["observed_sure"] = observed_sure
        result.setdefault(int(index), []).append(event)

    return result


def chan_sell_fraction(kind: str, mode: str) -> float:
    if mode == "flat25":
        return 0.25
    if mode != "graded":
        raise ValueError(mode)

    k = str(kind).upper()
    if k in {"S1", "S1P"}:
        return 0.50
    if k in {"S2", "S2S", "S3A", "S3B"}:
        return 0.25
    raise ValueError(f"Unknown chan.py sell kind: {kind}")


def _max_drawdown(values: list[float]) -> float:
    peak = None
    worst = 0.0
    for value in values:
        v = float(value)
        peak = v if peak is None else max(peak, v)
        if peak > 0:
            worst = min(worst, v / peak - 1.0)
    return worst


def simulate_exit_stack(
    candles: Iterable[dict],
    ledger: list[dict],
    chan_observations: list[dict],
    config: ExitStackConfig,
    *,
    friction_bps: float = 5.0,
) -> dict:
    bars = sltd._validate_candles(candles)
    if len(bars) != len(ledger):
        raise ValueError("K 线数量与信号账本长度不一致")

    chan_by_index = chan_events_by_signal_index(
        chan_observations,
        levels=config.chan_levels,
        certainty=config.chan_certainty,
    )
    chandelier = (
        chandelier_long(
            bars,
            lookback=config.chandelier_lookback,
            multiplier=config.chandelier_multiplier,
        )
        if config.chandelier
        else [None] * len(bars)
    )

    cash = 1.0
    shares = 0.0
    risk_armed = False
    cost_rate = float(friction_bps) / 10000.0
    trail_stop: float | None = None
    chandelier_pending = False

    markers: list[dict] = []
    positions: list[dict] = []
    equity_curve: list[float] = []
    stop_curve: list[float | None] = []
    execution_counts: dict[str, int] = {
        "BUY": 0,
        "SLTD_SELL": 0,
        "CHAN_SELL": 0,
        "C2_FULL_EXIT": 0,
        "CHANDELIER_FULL_EXIT": 0,
    }

    episode_peak_equity: float | None = None
    episode_start_index: int | None = None
    episode_givebacks: list[float] = []
    episode_holding_bars: list[int] = []

    formal_index = next(
        (i for i, b in enumerate(bars) if b["date"] >= sltd.POLICY_START_DATE),
        0,
    )
    warmup_index = min(sltd.MIN_WARMUP_BARS, len(bars) - 1)
    start_index = max(formal_index, warmup_index)

    for j, bar in enumerate(bars):
        if j < start_index:
            equity_curve.append(1.0)
            positions.append(
                {
                    "date": bar["date"],
                    "fraction": 0.0,
                    "risk_armed": False,
                    "chandelier_stop": None,
                }
            )
            stop_curve.append(None)
            continue

        op = float(bar["open"])
        cl = float(bar["close"])
        pre_equity = cash + shares * op
        if pre_equity <= 0:
            raise RuntimeError("账户权益不得为零或负数")

        position_value = shares * op
        current_fraction = position_value / pre_equity
        signal = ledger[j - 1] if j > start_index else None
        chan_events = chan_by_index.get(j - 1, []) if j > start_index else []

        c2_hard = bool(
            shares > 1e-14 and risk_armed and sltd.c2_condition(signal)
        )
        chandelier_hard = bool(
            shares > 1e-14 and config.chandelier and chandelier_pending
        )

        original_action = sltd.resolve_action(signal)
        order_value = 0.0
        side: str | None = None
        action = "NONE"
        rule_ids: list[str] = []
        chan_kinds: list[str] = []

        if c2_hard or chandelier_hard:
            order_value = -position_value
            side = "X"
            if chandelier_hard:
                action = "CHANDELIER_FULL_EXIT"
                rule_ids = ["CHANDELIER_22_3"]
            else:
                action = "C2_FULL_EXIT"
                rule_ids = [sltd.HARD_EXIT_ID]
        elif shares > 1e-14 and chan_events:
            fractions = [
                chan_sell_fraction(x["kind"], config.chan_fraction_mode)
                for x in chan_events
            ]
            frac = max(fractions)
            order_value = -position_value * frac
            side = "S"
            action = "CHAN_SELL"
            chan_kinds = sorted({str(x["kind"]) for x in chan_events})
            rule_ids = [
                f"CHAN_L{int(x['level'])}_{str(x['kind'])}"
                for x in chan_events
            ]
        else:
            if original_action == "BUY":
                desired_fraction = (
                    0.25
                    if shares <= 1e-14
                    else min(1.0, current_fraction + 0.25)
                )
                desired_fraction = max(current_fraction, desired_fraction)
                order_value = desired_fraction * pre_equity - position_value
                side = "B"
                action = "BUY"
                rule_ids = sltd._rule_ids(signal)
            elif original_action == "SELL" and shares > 1e-14:
                order_value = -position_value * 0.25
                side = "S"
                action = "SLTD_SELL"
                rule_ids = sltd._rule_ids(signal)

        if order_value > 1e-14:
            max_buy = max(0.0, cash / (1.0 + cost_rate))
            order_value = min(order_value, max_buy)
        elif order_value < -1e-14:
            order_value = max(order_value, -position_value)

        was_in_position = shares > 1e-14
        executed = abs(order_value) > 1e-14
        if executed:
            cost = abs(order_value) * cost_rate
            shares += order_value / op
            cash -= order_value + cost
            if shares <= 1e-12:
                shares = 0.0
            if action in execution_counts:
                execution_counts[action] += 1

        is_in_position = shares > 1e-14

        if executed and action in {"C2_FULL_EXIT", "CHANDELIER_FULL_EXIT"}:
            risk_armed = False
        elif executed and action in {"SLTD_SELL", "CHAN_SELL"}:
            risk_armed = True
        elif executed and action == "BUY":
            risk_armed = False

        # Close completed holding episode at the execution open.
        if was_in_position and not is_in_position:
            exit_equity = cash
            if episode_peak_equity is not None and episode_peak_equity > 0:
                episode_givebacks.append(
                    max(0.0, 1.0 - exit_equity / episode_peak_equity)
                )
            if episode_start_index is not None:
                episode_holding_bars.append(max(1, j - episode_start_index))
            episode_peak_equity = None
            episode_start_index = None
            trail_stop = None
            chandelier_pending = False

        if (not was_in_position) and is_in_position:
            episode_start_index = j
            episode_peak_equity = cash + shares * cl
            trail_stop = None
            chandelier_pending = False

        close_equity = cash + shares * cl
        if is_in_position:
            episode_peak_equity = (
                close_equity
                if episode_peak_equity is None
                else max(episode_peak_equity, close_equity)
            )

            raw_stop = chandelier[j]
            if config.chandelier and raw_stop is not None and isfinite(float(raw_stop)):
                trail_stop = (
                    float(raw_stop)
                    if trail_stop is None
                    else max(float(trail_stop), float(raw_stop))
                )
            chandelier_pending = bool(
                config.chandelier
                and trail_stop is not None
                and cl < float(trail_stop)
            )
        else:
            trail_stop = None
            chandelier_pending = False

        close_fraction = (
            shares * cl / close_equity if close_equity > 0 else 0.0
        )
        equity_curve.append(close_equity)
        stop_curve.append(trail_stop)
        positions.append(
            {
                "date": bar["date"],
                "fraction": max(0.0, min(1.0, close_fraction)),
                "risk_armed": risk_armed,
                "chandelier_stop": trail_stop,
            }
        )

        if executed and side:
            markers.append(
                {
                    "signal_date": (
                        bars[j - 1]["date"] if j > 0 else bar["date"]
                    ),
                    "execution_date": bar["date"],
                    "price": op,
                    "side": side,
                    "action": action,
                    "rule_ids": rule_ids,
                    "chan_kinds": chan_kinds,
                    "position_after": max(
                        0.0, min(1.0, close_fraction)
                    ),
                    "risk_after": "ARMED" if risk_armed else "NORMAL",
                }
            )

    return {
        "config": config.name,
        "markers": markers,
        "positions": positions,
        "equity_curve": equity_curve,
        "chandelier_curve": chandelier,
        "ratcheted_stop_curve": stop_curve,
        "cash": cash,
        "shares": shares,
        "risk_armed": risk_armed,
        "position_fraction": positions[-1]["fraction"] if positions else 0.0,
        "final_equity": equity_curve[-1] if equity_curve else 1.0,
        "max_drawdown": _max_drawdown(equity_curve),
        "execution_counts": execution_counts,
        "episode_givebacks": episode_givebacks,
        "episode_holding_bars": episode_holding_bars,
    }
