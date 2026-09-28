"""Frozen pre-Protocol feature definitions for XMA Falsification v2.

Research status:
- implementation support only
- no trading rule
- no v2 outcome analysis
- no sealed-window access

Definitions come from V2_VARIABLE_DEFINITION_RESOLUTION_v1.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Mapping, Sequence

import numpy as np
import pandas as pd


SECTOR_ETF_MAP: Dict[str, str] = {
    "Technology": "XLK",
    "Communication Services": "XLC",
    "Consumer Discretionary": "XLY",
    "Consumer Staples": "XLP",
    "Health Care": "XLV",
    "Financials": "XLF",
    "Industrials": "XLI",
    "Energy": "XLE",
    "Materials": "XLB",
    "Utilities": "XLU",
    "Real Estate": "XLRE",
}

V2_BREADTH_UNIVERSE: tuple[str, ...] = (
    "AAPL","MSFT","NVDA","AMD","AVGO","ORCL","INTC","QCOM","MU",
    "GOOGL","META","NFLX","AMZN","TSLA","HD","MCD","WMT","COST","PG","KO","PEP",
    "ABT","LLY","UNH","JNJ","TMO","JPM","BAC","GS","V","MA","CAT","BA","GE",
    "XOM","CVX","LIN","NEE","PLD",
)


def _require_columns(df: pd.DataFrame, cols: Sequence[str]) -> None:
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"missing required columns: {missing}")


def true_range(df: pd.DataFrame) -> pd.Series:
    _require_columns(df, ("high", "low", "close"))
    prev_close = df["close"].shift(1)
    return pd.concat(
        [
            df["high"] - df["low"],
            (df["high"] - prev_close).abs(),
            (df["low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)


def atr14(df: pd.DataFrame) -> pd.Series:
    """ATR14 = arithmetic rolling mean of True Range, min_periods=14."""
    return true_range(df).rolling(14, min_periods=14).mean()


def dev20(close: pd.Series) -> pd.Series:
    ma20 = close.rolling(20, min_periods=20).mean()
    return close / ma20 - 1.0


def prior20_return(close: pd.Series) -> pd.Series:
    return close / close.shift(20) - 1.0


def volatility_zscore(close: pd.Series) -> pd.Series:
    """20-return realized volatility z-scored against the prior 60 RV20 values.

    Current RV20 is excluded from its own reference mean/std.
    """
    logret = np.log(close / close.shift(1))
    rv20 = logret.rolling(20, min_periods=20).std(ddof=1)
    ref_mean = rv20.shift(1).rolling(60, min_periods=60).mean()
    ref_std = rv20.shift(1).rolling(60, min_periods=60).std(ddof=1)
    out = (rv20 - ref_mean) / ref_std
    return out.where(ref_std > 0)


def volume_zscore(close: pd.Series, volume: pd.Series) -> pd.Series:
    """Log dollar-volume z-score against the prior 60 observations."""
    if (volume.dropna() < 0).any():
        raise ValueError("negative volume is invalid")
    ldv = np.log1p(close * volume)
    ref_mean = ldv.shift(1).rolling(60, min_periods=60).mean()
    ref_std = ldv.shift(1).rolling(60, min_periods=60).std(ddof=1)
    out = (ldv - ref_mean) / ref_std
    return out.where(ref_std > 0)


def _point_in_time_double_xma_endpoint(values: pd.Series, period: int = 25) -> pd.Series:
    """First-observed right-edge value of centered/truncated XMA(XMA(x,N),N).

    The source-XMA track treats TDX XMA as a centered moving average whose
    right side truncates at the currently available bar.  For each timestamp t
    this function returns the double-XMA value that would have been first
    observable at t, without later repainting.

    Period must be odd. For N=25 radius=12.
    """
    if period % 2 != 1:
        raise ValueError("period must be odd")
    arr = values.astype(float).to_numpy()
    n = len(arr)
    radius = (period - 1) // 2
    out = np.full(n, np.nan, dtype=float)

    # Do not bridge missing values. This implementation expects contiguous
    # valid inputs for a computed endpoint.
    valid = np.isfinite(arr)
    prefix = np.concatenate([[0.0], np.nancumsum(np.where(valid, arr, 0.0))])
    valid_prefix = np.concatenate([[0], np.cumsum(valid.astype(int))])

    for t in range(n):
        first_vals = []
        for i in range(max(0, t - radius), t + 1):
            lo = max(0, i - radius)
            hi = t
            count = valid_prefix[hi + 1] - valid_prefix[lo]
            expected = hi - lo + 1
            if count != expected:
                first_vals = []
                break
            total = prefix[hi + 1] - prefix[lo]
            first_vals.append(total / expected)
        if first_vals:
            out[t] = float(np.mean(first_vals))

    return pd.Series(out, index=values.index, dtype=float)


def fast_mid_analytic(df: pd.DataFrame) -> pd.Series:
    """FAST_MID_ANALYTIC = GZB18 = (A25+B25)/2, first-observed PIT values."""
    _require_columns(df, ("high", "low"))
    a25 = _point_in_time_double_xma_endpoint(df["high"], 25)
    b25 = _point_in_time_double_xma_endpoint(df["low"], 25)
    return (a25 + b25) / 2.0


def distance_to_mid_atr(df: pd.DataFrame) -> pd.Series:
    _require_columns(df, ("close", "high", "low"))
    a = atr14(df)
    mid = fast_mid_analytic(df)
    out = (df["close"] - mid) / a
    return out.where(a > 0)


def midpoint_touch(df: pd.DataFrame) -> pd.Series:
    """Current-bar membership in the frozen 0.25-ATR midpoint touch zone."""
    a = atr14(df)
    mid = fast_mid_analytic(df)
    return (df["close"] - mid).abs() <= 0.25 * a


def sector_rs20(
    sector_etf_close: Mapping[str, pd.Series],
    spy_close: pd.Series,
) -> pd.DataFrame:
    """Return daily sector RS20 percentile ranks for the frozen 11 ETFs.

    RS20 = sector 20-bar simple return - SPY 20-bar simple return.
    A date is retained only when all 11 sector ETFs and SPY are available.
    """
    frames = {}
    spy_ret20 = spy_close / spy_close.shift(20) - 1.0
    for sector, etf in SECTOR_ETF_MAP.items():
        if etf not in sector_etf_close:
            raise ValueError(f"missing sector ETF: {etf}")
        s = sector_etf_close[etf]
        frames[sector] = s / s.shift(20) - 1.0 - spy_ret20

    raw = pd.DataFrame(frames)
    complete = raw.dropna(how="any")

    def pct_rank(row: pd.Series) -> pd.Series:
        n = len(row)
        ranks = row.rank(method="average", ascending=True)
        return (ranks - 1.0) / (n - 1.0)

    return complete.apply(pct_rank, axis=1)


def market_breadth20(close_by_symbol: Mapping[str, pd.Series]) -> pd.Series:
    """Equal-weight % of frozen 39-equity universe above its own SMA20."""
    missing = [s for s in V2_BREADTH_UNIVERSE if s not in close_by_symbol]
    if missing:
        raise ValueError(f"missing breadth symbols: {missing}")

    cols = {}
    for symbol in V2_BREADTH_UNIVERSE:
        close = close_by_symbol[symbol]
        sma20 = close.rolling(20, min_periods=20).mean()
        cols[symbol] = (close > sma20).where(sma20.notna())

    panel = pd.DataFrame(cols)
    valid_count = panel.notna().sum(axis=1)
    min_valid = int(np.ceil(0.80 * len(V2_BREADTH_UNIVERSE)))
    breadth = 100.0 * panel.sum(axis=1, skipna=True) / valid_count
    return breadth.where(valid_count >= min_valid)


def breadth_risk_off(breadth20: pd.Series) -> pd.Series:
    """Risk-Off iff current breadth < prior-20-valid-observation 10th pct."""
    prior_q10 = breadth20.shift(1).rolling(20, min_periods=20).quantile(
        0.10, interpolation="linear"
    )
    out = breadth20 < prior_q10
    return out.where(breadth20.notna() & prior_q10.notna())


def vix_change5(vix_close: pd.Series) -> pd.Series:
    return vix_close / vix_close.shift(5) - 1.0


def vix_risk_off(vix_close: pd.Series) -> pd.Series:
    chg = vix_change5(vix_close)
    return (chg > 0.20).where(chg.notna())


def f3_volatility_control(df: pd.DataFrame) -> pd.Series:
    a = atr14(df)
    return (a / df["close"]).where(df["close"] != 0)


@dataclass(frozen=True)
class H4Quantiles:
    p10: float
    p40: float
    p60: float
    p90: float
    n: int


def h4_reference_quantiles(
    df: pd.DataFrame,
    start: str = "2020-01-02",
    end: str = "2025-12-31",
) -> H4Quantiles:
    """Frozen per-symbol H4 calibration thresholds."""
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError("df index must be DatetimeIndex")
    dist = distance_to_mid_atr(df).loc[start:end].dropna()
    if len(dist) < 252:
        raise ValueError(f"H4 requires >=252 valid observations, got {len(dist)}")
    q = dist.quantile([0.10, 0.40, 0.60, 0.90], interpolation="linear")
    return H4Quantiles(
        p10=float(q.loc[0.10]),
        p40=float(q.loc[0.40]),
        p60=float(q.loc[0.60]),
        p90=float(q.loc[0.90]),
        n=int(len(dist)),
    )
