"""E035 BTC 15m dynamic-position Discovery implementation.

Research-only implementation.

This module is governed by:
research/ssss/preregistrations/E035.md

It must not be treated as a validated production strategy.

The frozen daily core remains:
models/ssss_core_v0_1.py
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd


BASE_FRICTION = 0.0012
STRESS_FRICTION = 0.0015


@dataclass(frozen=True)
class Config15m:
    name: str
    fast_length: int
    slow_ema_length: int
    atr_length: int
    dsep_lag: int
    confirm_bars: int
    warmup_bars: int


CONFIGS = (
    Config15m("B0_LEGACY_COUNT_REFERENCE", 25, 90, 14, 5, 3, 300),
    Config15m("B1_NATIVE_12H", 48, 192, 24, 8, 4, 512),
    Config15m("B2_NATIVE_24H", 96, 384, 48, 16, 4, 1024),
)


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


def rolling_atr(df: pd.DataFrame, length: int) -> pd.Series:
    return true_range(df).rolling(length, min_periods=length).mean()


def source_weighted_high(high: pd.Series) -> pd.Series:
    """Preserve the source 20-lag structure for E035 comparability."""
    out = 20.0 * high
    for lag in range(1, 19):
        out = out + (20 - lag) * high.shift(lag)
    out = out + high.shift(20)
    return out / 210.0


def source_weighted_low(low: pd.Series, high: pd.Series) -> pd.Series:
    """Preserve source lag-11 HIGH anomaly and skipped lag-19."""
    out = 20.0 * low
    for lag in range(1, 19):
        src = high if lag == 11 else low
        out = out + (20 - lag) * src.shift(lag)
    out = out + low.shift(20)
    return out / 210.0


def effective_state(raw: pd.Series, confirm_bars: int) -> pd.Series:
    valid = {"red", "green", "gray"}
    values = raw.astype(object).tolist()
    current = "neutral"
    out: list[str] = []

    for i, value in enumerate(values):
        if i >= confirm_bars - 1:
            window = values[i - confirm_bars + 1 : i + 1]
            if len(set(window)) == 1 and value in valid:
                current = value
        out.append(current)

    return pd.Series(out, index=raw.index, dtype="object")


def compute_indicators(bars: pd.DataFrame, cfg: Config15m) -> pd.DataFrame:
    required = {"timestamp", "open", "high", "low", "close", "volume"}
    missing = required.difference(bars.columns)
    if missing:
        raise ValueError(f"missing columns: {sorted(missing)}")

    df = bars.copy().sort_values("timestamp").reset_index(drop=True)

    dh = dema(df["high"], cfg.fast_length)
    dl = dema(df["low"], cfg.fast_length)

    df["fast_upper"] = 2.0 * dh - dl
    df["fast_lower"] = 2.0 * dl - dh
    df["fast_mid"] = (dh + dl) / 2.0
    df["fast_width"] = dh - dl

    wh = source_weighted_high(df["high"])
    wl = source_weighted_low(df["low"], df["high"])

    df["white_upper"] = ema(wh, cfg.slow_ema_length)
    df["white_lower"] = ema(wl, cfg.slow_ema_length)
    df["white_mid"] = (df["white_upper"] + df["white_lower"]) / 2.0
    df["white_width"] = df["white_upper"] - df["white_lower"]

    df["atr"] = rolling_atr(df, cfg.atr_length)

    df["sep"] = df["fast_mid"] - df["white_mid"]
    df["dsep"] = df["sep"] - df["sep"].shift(cfg.dsep_lag)

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
    df["effective_state"] = effective_state(
        df["raw_state"], cfg.confirm_bars
    )

    cross_fast_upper = (
        (df["high"] > df["fast_upper"])
        & (df["high"].shift(1) <= df["fast_upper"].shift(1))
    )
    price_near_white = (
        df["close"] >= df["white_lower"] - 2.0 * df["atr"]
    )

    df["qualified_grb"] = (
        (df.index >= cfg.warmup_bars)
        & (df["effective_state"] == "green")
        & cross_fast_upper
        & (df["dsep"] > 0)
        & price_near_white
    )

    df["rte"] = (
        (df["effective_state"] == "red")
        & (df["high"] > df["fast_upper"])
        & (df["close"] >= df["open"])
        & (df["fast_width"] > df["fast_width"].shift(5))
        & (df["dsep"] < 0)
    )

    df["green_transition"] = (
        (df["effective_state"] == "green")
        & (df["effective_state"].shift(1) != "green")
    )
    df["fast_breakout"] = (
        (df["effective_state"] == "green")
        & cross_fast_upper
    )
    df["fastmid_reclaim"] = (
        (df["effective_state"] == "green")
        & (df["close"].shift(1) <= df["fast_mid"].shift(1))
        & (df["close"] > df["fast_mid"])
    )

    df["green_to_gray"] = (
        (df["effective_state"].shift(1) == "green")
        & (df["effective_state"] == "gray")
    )
    df["gray_to_green"] = (
        (df["effective_state"].shift(1) == "gray")
        & (df["effective_state"] == "green")
    )
    df["green_to_red"] = (
        (df["effective_state"].shift(1) == "green")
        & (df["effective_state"] == "red")
    )
    df["red_to_gray"] = (
        (df["effective_state"].shift(1) == "red")
        & (df["effective_state"] == "gray")
    )

    df["dsep_cross_pos"] = (
        (df["dsep"].shift(1) <= 0) & (df["dsep"] > 0)
    )
    df["fastmid_cross_up"] = (
        (df["close"].shift(1) <= df["fast_mid"].shift(1))
        & (df["close"] > df["fast_mid"])
    )
    df["fastmid_cross_down"] = (
        (df["close"].shift(1) >= df["fast_mid"].shift(1))
        & (df["close"] < df["fast_mid"])
    )

    return df


def apply_entry_cost(px: float, friction: float) -> float:
    return px * (1.0 + friction)


def apply_exit_cost(px: float, friction: float) -> float:
    return px * (1.0 - friction)


def lifecycle_return(
    entry_open: float,
    exit_open: float,
    friction: float,
) -> float:
    return apply_exit_cost(exit_open, friction) / apply_entry_cost(
        entry_open, friction
    ) - 1.0


def generate_baseline_lifecycles(
    df: pd.DataFrame,
    friction: float = BASE_FRICTION,
) -> pd.DataFrame:
    """Generate one-at-a-time GRB lifecycles using E035 baseline semantics."""
    rows = []
    in_position = False
    seen_red = False
    trade: dict | None = None
    prev_state = "neutral"

    for i in range(len(df)):
        state = df.at[i, "effective_state"]

        if not in_position:
            if bool(df.at[i, "qualified_grb"]) and i + 1 < len(df):
                in_position = True
                seen_red = False
                trade = {
                    "signal_i": i,
                    "entry_i": i + 1,
                    "entry_open": float(df.at[i + 1, "open"]),
                    "entry_atr": float(df.at[i, "atr"]),
                    "first_red_i": None,
                }
        else:
            assert trade is not None

            if seen_red:
                if prev_state == "red" and state == "gray":
                    if i + 1 < len(df):
                        trade["close_signal_i"] = i
                        trade["exit_i"] = i + 1
                        trade["exit_open"] = float(df.at[i + 1, "open"])
                        trade["path"] = "MATURE"
                        rows.append(trade)
                    trade = None
                    in_position = False
                    seen_red = False
            else:
                if state == "red":
                    seen_red = True
                    trade["first_red_i"] = i
                elif prev_state == "gray" and state == "green":
                    if i + 1 < len(df):
                        trade["close_signal_i"] = i
                        trade["exit_i"] = i + 1
                        trade["exit_open"] = float(df.at[i + 1, "open"])
                        trade["path"] = "FAILURE"
                        rows.append(trade)
                    trade = None
                    in_position = False

        prev_state = state

    out = pd.DataFrame(rows)
    if out.empty:
        return out

    out["gross_return"] = (
        out["exit_open"] / out["entry_open"] - 1.0
    )
    out["base_net_return"] = [
        lifecycle_return(a, b, BASE_FRICTION)
        for a, b in zip(out["entry_open"], out["exit_open"])
    ]
    out["stress_net_return"] = [
        lifecycle_return(a, b, STRESS_FRICTION)
        for a, b in zip(out["entry_open"], out["exit_open"])
    ]
    out["hold_bars"] = out["exit_i"] - out["entry_i"]
    out["hold_hours"] = out["hold_bars"] * 0.25

    mfes = []
    maes = []
    for r in out.itertuples():
        w = df.iloc[r.entry_i : r.exit_i + 1]
        mfes.append(float(w["high"].max()) / r.entry_open - 1.0)
        maes.append(float(w["low"].min()) / r.entry_open - 1.0)
    out["mfe"] = mfes
    out["mae"] = maes

    return out


def current_progress_atr(
    df: pd.DataFrame,
    trade: pd.Series,
    i: int,
) -> float:
    return (
        float(df.at[i, "close"]) - float(trade["entry_open"])
    ) / float(trade["entry_atr"])


def running_mfe_atr(
    df: pd.DataFrame,
    trade: pd.Series,
    i: int,
) -> float:
    high = float(
        df.loc[int(trade["entry_i"]) : i, "high"].max()
    )
    return (high - float(trade["entry_open"])) / float(trade["entry_atr"])


def giveback_atr(
    df: pd.DataFrame,
    trade: pd.Series,
    i: int,
) -> float:
    high = float(
        df.loc[int(trade["entry_i"]) : i, "high"].max()
    )
    return (high - float(df.at[i, "close"])) / float(trade["entry_atr"])


def phase_of(trade: pd.Series, i: int) -> str:
    first_red = trade.get("first_red_i")
    if pd.isna(first_red) or first_red is None:
        return "PRE_RED"
    return "PRE_RED" if i < int(first_red) else "POST_RED"


def bars_bucket(bars: int) -> str:
    if bars <= 7:
        return "B00_07"
    if bars <= 31:
        return "B08_31"
    if bars <= 95:
        return "B32_95"
    return "B96P"


def progress_bucket(x: float) -> str:
    if x <= 0:
        return "P_LE_0"
    if x <= 1:
        return "P_0_1"
    if x <= 2:
        return "P_1_2"
    return "P_GT_2"


def giveback_bucket(x: float) -> str:
    if x < 0.5:
        return "G_LT_05"
    if x < 1.0:
        return "G_05_1"
    if x < 2.0:
        return "G_1_2"
    return "G_GE_2"


def mfe_bucket(x: float) -> str:
    if x < 1:
        return "M_LT_1"
    if x < 2:
        return "M_1_2"
    if x < 4:
        return "M_2_4"
    return "M_GE_4"


def fast_location(df: pd.DataFrame, i: int) -> str:
    close = float(df.at[i, "close"])
    mid = float(df.at[i, "fast_mid"])
    upper = float(df.at[i, "fast_upper"])
    if close < mid:
        return "BELOW_MID"
    if close <= upper:
        return "MID_TO_UPPER"
    return "ABOVE_UPPER"


def dsep_sign(df: pd.DataFrame, i: int) -> str:
    return "POS" if float(df.at[i, "dsep"]) > 0 else "NONPOS"


def risk_markers(df: pd.DataFrame, i: int) -> list[str]:
    out = []
    if bool(df.at[i, "rte"]):
        out.append("K1_RTE")
    if bool(df.at[i, "green_to_gray"]):
        out.append("K2_GREEN_TO_GRAY")
    if bool(df.at[i, "fastmid_cross_down"]):
        out.append("K3_FASTMID_CROSS_DOWN")
    return out


def recovery_events(df: pd.DataFrame, i: int) -> list[str]:
    out = []
    if bool(df.at[i, "dsep_cross_pos"]):
        out.append("RA1_DSEP_CROSS_POS")
    if bool(df.at[i, "fastmid_cross_up"]):
        out.append("RA2_FASTMID_RECLAIM")
    if bool(df.at[i, "gray_to_green"]):
        out.append("RA3_GRAY_TO_GREEN")
    return out


def validate_no_future_access() -> None:
    """Static declaration used by the E035 causality audit."""
    # All feature/event helpers above use current / lagged / rolling history only.
    # Labels use future baseline exits only after candidate decision state is fixed.
    return None


if __name__ == "__main__":
    print("E035 research module loaded; no production action is validated.")
