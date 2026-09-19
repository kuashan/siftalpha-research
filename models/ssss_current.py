# CURRENT DEVELOPMENT MODEL
# This file tracks the latest working research version.
# Frozen snapshot at initialization: ssss_core_v0_1.py

"""
SSSS Core Model v0.1.0
======================

Status:
- OPEN: validated research rule
- FAILURE CLOSE: validated research rule
- MATURE CLOSE: validated research rule
- ADD: not yet validated; E030/E031 trigger families rejected; E032 found early opportunity zones; E033 selective early-entry rules also rejected because they did not distinguish Mature from Failure paths
- FEATURE DIAGNOSTICS: E034 ER10 / CHOP14 / CMF20 / OBVImpulse10 single-snapshot screen produced no equity diagnostic candidate; crypto sample too sparse
- BTC 15m: E037 found GREEN_TRANSITION starter economics and 10 early ADD candidate zones; no REDUCE / RE-ADD / CLOSE zone validated
- BTC 15m E038: paired tactical REDUCE/RE-ADD failed; GREEN->GRAY is risk-classification only; exact first-ADD rule cannot be reused for re-add
- REDUCE: RTE is research candidate only
- RE-ADD: not yet validated

Research assumptions:
- Causal rewrite of source XMA uses DEMA.
- Signal is known after bar close.
- Execution is on next tradable bar open.
- Transaction cost default: 0.1% per side.
- Effective RED/GREEN/GRAY state requires 3 consecutive raw-state bars.
- Source slow-band anomalies are intentionally preserved:
  1) lag 19 is skipped and lag 20 receives weight 1;
  2) lower weighted structure uses HIGH at lag 11 instead of LOW.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

import numpy as np
import pandas as pd


MODEL_VERSION = "0.1.0"
TRANSACTION_COST = 0.001
WARMUP_BARS = 150


class Action(str, Enum):
    NONE = "NONE"
    OPEN = "OPEN"
    HOLD = "HOLD"
    ADD = "ADD"          # reserved: no validated production trigger yet
    REDUCE = "REDUCE"    # reserved: RTE remains a candidate only
    RE_ADD = "RE_ADD"    # reserved: no validated production trigger yet
    CLOSE = "CLOSE"


class CloseReason(str, Enum):
    FAILURE = "GRAY_TO_GREEN"
    MATURE = "RED_TO_GRAY"


@dataclass(frozen=True)
class ModelConfig:
    fast_length: int = 25
    slow_ema_length: int = 90
    atr_length: int = 14
    dsep_lag: int = 5
    confirm_bars: int = 3
    transaction_cost: float = TRANSACTION_COST
    warmup_bars: int = WARMUP_BARS


def ema(s: pd.Series, length: int) -> pd.Series:
    return s.ewm(span=length, adjust=False, min_periods=length).mean()


def dema(s: pd.Series, length: int) -> pd.Series:
    e1 = ema(s, length)
    e2 = ema(e1, length)
    return 2.0 * e1 - e2


def true_range(df: pd.DataFrame) -> pd.Series:
    prev_close = df["close"].shift(1)
    return pd.concat(
        [
            df["high"] - df["low"],
            (df["high"] - prev_close).abs(),
            (df["low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)


def atr(df: pd.DataFrame, length: int = 14) -> pd.Series:
    # Matches the research backtest convention used so far: rolling mean TR.
    return true_range(df).rolling(length, min_periods=length).mean()


def _source_weighted_high(high: pd.Series) -> pd.Series:
    # Source-preserving structure:
    # 20*H + 19*REF(H,1) + ... + 2*REF(H,18) + 1*REF(H,20)
    # REF(...,19) is intentionally absent.
    out = 20.0 * high
    for lag in range(1, 19):
        out = out + (20 - lag) * high.shift(lag)
    out = out + high.shift(20)
    return out / 210.0


def _source_weighted_low(low: pd.Series, high: pd.Series) -> pd.Series:
    # Same source structure, preserving the original anomaly:
    # at lag 11 (weight 9), HIGH is used instead of LOW.
    out = 20.0 * low
    for lag in range(1, 19):
        src = high if lag == 11 else low
        out = out + (20 - lag) * src.shift(lag)
    out = out + low.shift(20)
    return out / 210.0


def _effective_state(raw_state: pd.Series, confirm_bars: int = 3) -> pd.Series:
    valid = {"red", "green", "gray"}
    eff = []
    current = "neutral"

    values = raw_state.astype(object).tolist()
    for i, value in enumerate(values):
        if i >= confirm_bars - 1:
            window = values[i - confirm_bars + 1 : i + 1]
            if len(set(window)) == 1 and value in valid:
                current = value
        eff.append(current)

    return pd.Series(eff, index=raw_state.index, dtype="object")


def compute_indicators(
    bars: pd.DataFrame,
    config: ModelConfig = ModelConfig(),
) -> pd.DataFrame:
    """
    Required columns:
        open, high, low, close

    Returns a copy containing the causal SSSS research indicators.
    """
    required = {"open", "high", "low", "close"}
    missing = required.difference(bars.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    df = bars.copy().reset_index(drop=True)

    # Fast colored band: causal replacement of source XMA using DEMA(25).
    dh = dema(df["high"], config.fast_length)
    dl = dema(df["low"], config.fast_length)

    df["fast_upper"] = 2.0 * dh - dl
    df["fast_lower"] = 2.0 * dl - dh
    df["fast_mid"] = (dh + dl) / 2.0
    df["fast_width"] = dh - dl

    # Slow white band: preserve source formula and anomalies, then EMA(90).
    slow_high_input = _source_weighted_high(df["high"])
    slow_low_input = _source_weighted_low(df["low"], df["high"])

    df["white_upper"] = ema(slow_high_input, config.slow_ema_length)
    df["white_lower"] = ema(slow_low_input, config.slow_ema_length)
    df["white_mid"] = (df["white_upper"] + df["white_lower"]) / 2.0
    df["white_width"] = df["white_upper"] - df["white_lower"]

    df["atr14"] = atr(df, config.atr_length)

    sep = df["fast_mid"] - df["white_mid"]
    df["sep"] = sep
    df["dsep"] = sep - sep.shift(config.dsep_lag)

    upper_expanded = df["white_upper"] + 2.0 * df["white_width"]
    lower_expanded = df["white_lower"] - 2.0 * df["white_width"]

    red = (df["fast_lower"] >= lower_expanded) & (
        df["fast_upper"] >= upper_expanded
    )
    green = (df["fast_upper"] <= upper_expanded) & (
        df["fast_lower"] <= lower_expanded
    )
    gray = (df["fast_lower"] >= lower_expanded) & (
        df["fast_upper"] <= upper_expanded
    )

    df["raw_state"] = np.select(
        [red, green, gray],
        ["red", "green", "gray"],
        default="other",
    )
    df["effective_state"] = _effective_state(
        df["raw_state"], config.confirm_bars
    )

    # Qualified GRB / OPEN signal.
    cross_fast_upper = (
        (df["high"] > df["fast_upper"])
        & (df["high"].shift(1) <= df["fast_upper"].shift(1))
    )
    price_near_white = (
        df["close"] >= df["white_lower"] - 2.0 * df["atr14"]
    )

    df["qualified_grb"] = (
        (df.index >= config.warmup_bars)
        & (df["effective_state"] == "green")
        & cross_fast_upper
        & (df["dsep"] > 0)
        & price_near_white
    )

    # RTE: research candidate for REDUCE only. It is NOT a validated close rule.
    df["rte"] = (
        (df["effective_state"] == "red")
        & (df["high"] > df["fast_upper"])
        & (df["close"] >= df["open"])
        & (df["fast_width"] > df["fast_width"].shift(5))
        & (df["dsep"] < 0)
    )

    return df


def generate_core_actions(
    bars: pd.DataFrame,
    config: ModelConfig = ModelConfig(),
) -> pd.DataFrame:
    """
    Generate the current frozen core actions.

    Core state machine:
        FLAT
          -> Qualified GRB -> OPEN
        POSITION before RED
          -> Gray -> Green -> CLOSE (failure)
        POSITION after RED has occurred
          -> Red -> Gray -> CLOSE (mature)

    ADD / REDUCE / RE-ADD are intentionally NOT executed here yet.
    RTE is exposed as a warning flag for future position-management research.
    """
    df = compute_indicators(bars, config)

    action = [Action.NONE.value] * len(df)
    close_reason: list[Optional[str]] = [None] * len(df)
    in_position = False
    seen_red = False

    prev_state = "neutral"

    for i, row in df.iterrows():
        state = row["effective_state"]

        if not in_position:
            if bool(row["qualified_grb"]):
                action[i] = Action.OPEN.value
                in_position = True
                seen_red = False
            else:
                action[i] = Action.NONE.value
        else:
            if seen_red:
                if prev_state == "red" and state == "gray":
                    action[i] = Action.CLOSE.value
                    close_reason[i] = CloseReason.MATURE.value
                    in_position = False
                    seen_red = False
                else:
                    action[i] = Action.HOLD.value
            else:
                if state == "red":
                    seen_red = True
                    action[i] = Action.HOLD.value
                elif prev_state == "gray" and state == "green":
                    action[i] = Action.CLOSE.value
                    close_reason[i] = CloseReason.FAILURE.value
                    in_position = False
                    seen_red = False
                else:
                    action[i] = Action.HOLD.value

        prev_state = state

    df["action"] = action
    df["close_reason"] = close_reason
    df["execute_next_open"] = df["action"].isin(
        [Action.OPEN.value, Action.CLOSE.value]
    )
    return df


def backtest_core(
    bars: pd.DataFrame,
    config: ModelConfig = ModelConfig(),
) -> pd.DataFrame:
    """
    Single-asset reference backtest.

    - Signal at today's close.
    - Execute at next bar's open.
    - One position at a time.
    - Cost is charged on both entry and exit.
    """
    df = generate_core_actions(bars, config)
    trades = []

    entry_index = None
    entry_price = None

    for i in range(len(df) - 1):
        a = df.at[i, "action"]

        if a == Action.OPEN.value and entry_price is None:
            entry_index = i + 1
            entry_price = float(df.at[i + 1, "open"]) * (
                1.0 + config.transaction_cost
            )

        elif a == Action.CLOSE.value and entry_price is not None:
            exit_index = i + 1
            exit_price = float(df.at[i + 1, "open"]) * (
                1.0 - config.transaction_cost
            )
            net_return = exit_price / entry_price - 1.0

            window = df.iloc[entry_index : exit_index + 1]
            mfe = float(window["high"].max()) / entry_price - 1.0
            mae = float(window["low"].min()) / entry_price - 1.0

            trades.append(
                {
                    "entry_index": entry_index,
                    "exit_index": exit_index,
                    "entry_price": entry_price,
                    "exit_price": exit_price,
                    "net_return": net_return,
                    "mfe": mfe,
                    "mae": mae,
                    "hold_bars": exit_index - entry_index,
                    "close_reason": df.at[i, "close_reason"],
                }
            )

            entry_index = None
            entry_price = None

    return pd.DataFrame(trades)


if __name__ == "__main__":
    print(
        "SSSS Core Model v0.1.0 loaded. "
        "Use compute_indicators(), generate_core_actions(), or backtest_core()."
    )
