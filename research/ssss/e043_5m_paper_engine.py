#!/usr/bin/env python3
"""
E043 5m multi-indicator forward paper engine.

Data:
  Binance public REST spot klines for BTCUSDT / ETHUSDT / BNBUSDT.

Execution:
  Paper only. 10x is the instrument leverage setting.
  Orders are virtual and written to repository logs.

Research families:
  F1 LMD2/LMD3
  F2 causalized support/resistance + MA30/Fibonacci structure
  F3 DXBD
  F4 KDJ + accumulation/distribution + MACD resonance
  F5 legacy SSSS structural family (5m diagnostic context)

No E035-E042 OOS data are used.
"""

from __future__ import annotations

import csv
import json
import math
import os
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
LIVE = ROOT / "research" / "ssss" / "live"
STATE_PATH = LIVE / "E043_STATE.json"
TRADES_PATH = LIVE / "E043_5M_PAPER_TRADES.csv"
JOURNAL_PATH = LIVE / "E043_5M_TRADING_JOURNAL.md"

SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
FORWARD_START_MS = 1789928400000  # 2026-09-20 18:20:00 UTC
LEVERAGE = 10.0
START_MARGIN = 0.10
ADD_MARGIN = 0.05
MAX_ASSET_MARGIN = 0.25
MAX_PORTFOLIO_MARGIN = 0.40
REDUCE_FRACTION = 0.25
BASE_FRICTION = 0.0012
DAILY_LOSS_STOP = -0.03
PORTFOLIO_KILL_DD = -0.06
STRATEGY_VERSION = "v0.1-forward"

BINANCE = "https://api.binance.com/api/v3/klines"


def utc(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).isoformat()


def fetch_klines(symbol: str, limit: int = 500) -> pd.DataFrame:
    query = urllib.parse.urlencode(
        {"symbol": symbol, "interval": "5m", "limit": str(limit)}
    )
    req = urllib.request.Request(
        BINANCE + "?" + query,
        headers={"User-Agent": "SiftAlpha-E043/1.0"},
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    cols = [
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "quote_volume", "trades", "taker_base",
        "taker_quote", "ignore",
    ]
    df = pd.DataFrame(data, columns=cols)
    for c in ["open", "high", "low", "close", "volume"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    for c in ["open_time", "close_time", "trades"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    # Completed bars only.
    df = df[df["close_time"] < now_ms].copy().reset_index(drop=True)
    if len(df) < 200:
        raise RuntimeError(f"{symbol}: only {len(df)} completed bars")
    return df


def tdx_sma(s: pd.Series, n: int, m: int = 1) -> pd.Series:
    out = np.full(len(s), np.nan, dtype=float)
    prev = np.nan
    for i, x in enumerate(s.to_numpy(dtype=float)):
        if not np.isfinite(x):
            continue
        if not np.isfinite(prev):
            prev = x
        else:
            prev = (m * x + (n - m) * prev) / n
        out[i] = prev
    return pd.Series(out, index=s.index)


def ema(s: pd.Series, n: int) -> pd.Series:
    return s.ewm(span=n, adjust=False, min_periods=n).mean()


def dema(s: pd.Series, n: int) -> pd.Series:
    e1 = ema(s, n)
    e2 = ema(e1, n)
    return 2 * e1 - e2


def cross_up(a: pd.Series, b: pd.Series) -> pd.Series:
    return (a > b) & (a.shift(1) <= b.shift(1))


def cross_down(a: pd.Series, b: pd.Series) -> pd.Series:
    return (a < b) & (a.shift(1) >= b.shift(1))


def true_range(df: pd.DataFrame) -> pd.Series:
    pc = df["close"].shift(1)
    return pd.concat(
        [
            df["high"] - df["low"],
            (df["high"] - pc).abs(),
            (df["low"] - pc).abs(),
        ],
        axis=1,
    ).max(axis=1)


def barslast(cond: pd.Series) -> pd.Series:
    out = np.full(len(cond), np.nan)
    last = None
    for i, v in enumerate(cond.fillna(False).to_numpy(bool)):
        if v:
            last = i
            out[i] = 0
        elif last is not None:
            out[i] = i - last
    return pd.Series(out, index=cond.index)


def latest_valuewhen(cond: pd.Series, values: pd.Series) -> pd.Series:
    out = np.full(len(cond), np.nan)
    last = np.nan
    for i, (c, v) in enumerate(zip(cond.fillna(False), values)):
        if bool(c) and np.isfinite(v):
            last = float(v)
        out[i] = last
    return pd.Series(out, index=cond.index)


def effective_state(raw: list[str], confirm: int = 3) -> list[str]:
    out = []
    cur = "NEUTRAL"
    for i, v in enumerate(raw):
        if i >= confirm - 1 and v in {"GREEN", "RED", "GRAY"}:
            if all(raw[j] == v for j in range(i - confirm + 1, i + 1)):
                cur = v
        out.append(cur)
    return out


def white_source(high: pd.Series, low: pd.Series) -> tuple[pd.Series, pd.Series]:
    hi = np.full(len(high), np.nan)
    lo = np.full(len(low), np.nan)
    H = high.to_numpy(float)
    L = low.to_numpy(float)
    for i in range(20, len(high)):
        vh = 20 * H[i]
        vl = 20 * L[i]
        for lag in range(1, 19):
            w = 20 - lag
            vh += w * H[i - lag]
            vl += w * (H[i - lag] if lag == 11 else L[i - lag])
        vh += H[i - 20]
        vl += L[i - 20]
        hi[i] = vh / 210
        lo[i] = vl / 210
    return pd.Series(hi, index=high.index), pd.Series(lo, index=low.index)


def family_f1(df: pd.DataFrame) -> dict:
    tr = true_range(df)
    atr14 = tr.rolling(14).mean()
    atr_norm = atr14 / df["close"]
    body = (df["close"] - df["open"]).abs()
    avg_body = body.rolling(20).mean()
    vol_ratio = df["volume"] / ema(df["volume"], 60)
    macro = ema(df["close"], 60)

    hd = df["high"] - df["high"].shift(1)
    ld = df["low"].shift(1) - df["low"]
    dmp = np.where((hd > 0) & (hd > ld), hd, 0.0)
    dmm = np.where((ld > 0) & (ld > hd), ld, 0.0)
    dmp = pd.Series(dmp, index=df.index)
    dmm = pd.Series(dmm, index=df.index)
    pdi = dmp.rolling(14).mean() / tr.rolling(14).mean() * 100
    mdi = dmm.rolling(14).mean() / tr.rolling(14).mean() * 100
    dx = (pdi - mdi).abs() / (pdi + mdi + 0.0001) * 100
    adx = dx.rolling(6).mean()

    out = {"atr14": atr14, "adx": adx}
    for tag, body_mult, volbase, volatr, interval, adx_th, close_ratio in [
        ("2", 2.0, 1.15, 1.5, 5, 20, 0.66),
        ("3", 1.2, 1.00, 1.0, 3, 15, 0.62),
    ]:
        bdy = 1.0 + atr_norm * body_mult
        vol_dyn = volbase + atr_norm * volatr
        rng = (df["high"] - df["low"]).replace(0, np.nan)
        bull = (
            (body > avg_body * bdy)
            & (body > rng * 0.5)
            & ((df["close"] - df["low"]) / (rng + 0.0001) > close_ratio)
        )
        bear = (
            (body > avg_body * bdy)
            & (body > rng * 0.5)
            & ((df["high"] - df["close"]) / (rng + 0.0001) > close_ratio)
        )
        trend_up = (df["close"] > macro) & (macro > macro.shift(1)) & (adx > adx_th)
        trend_dn = (df["close"] < macro) & (macro < macro.shift(1)) & (adx > adx_th)

        b_sig = (
            (df["low"] > df["high"].shift(2))
            & (df["close"].shift(1) > df["high"].shift(2))
            & bull.shift(1).fillna(False)
        )
        s_sig = (
            (df["high"] < df["low"].shift(2))
            & (df["close"].shift(1) < df["low"].shift(2))
            & bear.shift(1).fillna(False)
        )
        b_gold = b_sig & (vol_ratio.shift(1) >= vol_dyn) & trend_up
        s_gold = s_sig & (vol_ratio.shift(1) >= vol_dyn) & trend_dn

        prev_b = barslast(b_gold.shift(1).fillna(False))
        prev_s = barslast(s_gold.shift(1).fillna(False))
        b_start = b_gold & (prev_b > interval)
        s_start = s_gold & (prev_s > interval)

        b_bot = latest_valuewhen(b_start, df["high"].shift(2))
        b_top = latest_valuewhen(b_gold, df["low"])
        s_top = latest_valuewhen(s_start, df["low"].shift(2))
        s_bot = latest_valuewhen(s_gold, df["high"])
        b_mid = (b_top + b_bot) / 2
        s_mid = (s_top + s_bot) / 2

        # Causal mitigation state: once low/high touches the current midpoint after
        # the most recent start, it stays mitigated until a new start.
        b_mitigated = np.zeros(len(df), dtype=bool)
        s_mitigated = np.zeros(len(df), dtype=bool)
        bm = sm = False
        for i in range(len(df)):
            if bool(b_start.iloc[i]):
                bm = False
            if bool(s_start.iloc[i]):
                sm = False
            if np.isfinite(b_mid.iloc[i]) and df["low"].iloc[i] <= b_mid.iloc[i]:
                bm = True
            if np.isfinite(s_mid.iloc[i]) and df["high"].iloc[i] >= s_mid.iloc[i]:
                sm = True
            b_mitigated[i] = bm
            s_mitigated[i] = sm

        b_entry = (
            pd.Series(b_mitigated, index=df.index)
            & cross_up(df["close"], b_mid)
            & (df["close"] > df["close"].shift(1))
            & bull
        )
        s_entry = (
            pd.Series(s_mitigated, index=df.index)
            & cross_down(df["close"], s_mid)
            & (df["close"] < df["close"].shift(1))
            & bear
        )

        out.update(
            {
                f"bull_{tag}": bull,
                f"bear_{tag}": bear,
                f"trend_up_{tag}": trend_up,
                f"trend_dn_{tag}": trend_dn,
                f"b_start_{tag}": b_start,
                f"s_start_{tag}": s_start,
                f"b_entry_{tag}": b_entry,
                f"s_entry_{tag}": s_entry,
                f"b_mid_{tag}": b_mid,
                f"s_mid_{tag}": s_mid,
            }
        )

    i = len(df) - 1
    long_event = any(
        bool(out[k].iloc[i])
        for k in ["b_start_2", "b_start_3", "b_entry_3"]
    )
    short_event = any(
        bool(out[k].iloc[i])
        for k in ["s_start_2", "s_start_3", "s_entry_3"]
    )
    long_context = bool(out["trend_up_3"].iloc[i])
    short_context = bool(out["trend_dn_3"].iloc[i])

    vote = 1 if (long_event or (long_context and not short_context)) else (
        -1 if (short_event or (short_context and not long_context)) else 0
    )
    return {
        "vote": vote,
        "long_event": long_event,
        "short_event": short_event,
        "long_context": long_context,
        "short_context": short_context,
        "adx": float(adx.iloc[i]) if np.isfinite(adx.iloc[i]) else None,
        "atr14": float(atr14.iloc[i]),
        "b_entry_3": bool(out["b_entry_3"].iloc[i]),
        "s_entry_3": bool(out["s_entry_3"].iloc[i]),
    }


def confirmed_pivots(df: pd.DataFrame, radius: int) -> tuple[float | None, float | None]:
    H = df["high"].to_numpy(float)
    L = df["low"].to_numpy(float)
    last_hi = None
    last_lo = None
    # j is usable only after j+radius has completed.
    for j in range(radius, len(df) - radius):
        wh = H[j - radius : j + radius + 1]
        wl = L[j - radius : j + radius + 1]
        if H[j] >= np.nanmax(wh):
            last_hi = float(H[j])
        if L[j] <= np.nanmin(wl):
            last_lo = float(L[j])
    return last_hi, last_lo


def family_f2(df: pd.DataFrame) -> dict:
    c = df["close"]
    ma30 = c.rolling(30).mean()
    sh, sl = confirmed_pivots(df, 3)
    lh, ll = confirmed_pivots(df, 8)

    i = len(df) - 1
    px = float(c.iloc[i])
    prev = float(c.iloc[i - 1])
    short_break_up = sh is not None and px > sh and prev <= sh
    short_break_dn = sl is not None and px < sl and prev >= sl
    long_break_up = lh is not None and px > lh and prev <= lh
    long_break_dn = ll is not None and px < ll and prev >= ll

    ma_up = bool(px > ma30.iloc[i] and ma30.iloc[i] > ma30.iloc[i - 1])
    ma_dn = bool(px < ma30.iloc[i] and ma30.iloc[i] < ma30.iloc[i - 1])

    # Original COST/CAPITAL-based dealer-cost line is stock-specific and is
    # intentionally unavailable for crypto.
    vote = 1 if (ma_up and not ma_dn) else (-1 if (ma_dn and not ma_up) else 0)
    return {
        "vote": vote,
        "long_event": bool(short_break_up or long_break_up),
        "short_event": bool(short_break_dn or long_break_dn),
        "short_resistance": sh,
        "short_support": sl,
        "long_resistance": lh,
        "long_support": ll,
        "ma30": float(ma30.iloc[i]) if np.isfinite(ma30.iloc[i]) else None,
        "dealer_cost": None,
        "dealer_cost_reason": "TDX COST/CAPITAL is not portable to crypto",
        "repaint_guard": "confirmed pivots only",
    }


def family_f3(df: pd.DataFrame) -> dict:
    hh = df["high"].rolling(8).max()
    ll = df["low"].rolling(8).min()
    den = (hh - ll).replace(0, np.nan)
    cs = (df["close"] - ll) / den * 100
    osc = (ema(cs, 3) - 50) * 2

    prev_close = df["close"].shift(1)
    up = (df["close"] - prev_close).clip(lower=0)
    ab = (df["close"] - prev_close).abs()
    rsi_like = tdx_sma(up, 6, 1) / tdx_sma(ab, 6, 1).replace(0, np.nan) * 100

    i = len(df) - 1
    o = float(osc.iloc[i])
    op = float(osc.iloc[i - 1])
    rising = o > op
    falling = o < op

    refill = op <= -60 and o > -60
    accum = op <= -80 and o > -80
    control = op <= 0 and o > 0
    surge = op <= 60 and o > 60
    clear = op <= 78 and o > 78

    long_event = bool(refill or accum or control)
    short_event = bool(clear or (op >= 60 and o < 60))

    vote = 1 if (rising and o < 70) else (-1 if (falling and o > -70) else 0)
    return {
        "vote": vote,
        "long_event": long_event,
        "short_event": short_event,
        "osc": o,
        "rsi_like": float(rsi_like.iloc[i]) if np.isfinite(rsi_like.iloc[i]) else None,
        "labels": {
            "accumulation": bool(accum),
            "refill": bool(refill),
            "control": bool(control),
            "surge": bool(surge),
            "clear": bool(clear),
        },
    }


def family_f4(df: pd.DataFrame) -> dict:
    hh = df["high"].rolling(15).max()
    ll = df["low"].rolling(15).min()
    o00 = (df["close"] - ll) / (hh - ll).replace(0, np.nan) * 100
    l1 = tdx_sma(o00, 3, 1)
    l2 = tdx_sma(l1, 3, 1)
    l3 = 3 * l1 - 2 * l2

    o01 = ((df["low"] + df["open"] + df["close"] + df["high"]) / 4).shift(1)
    o02 = tdx_sma((df["low"] - o01).abs(), 13, 1) / tdx_sma(
        (df["low"] - o01).clip(lower=0), 10, 1
    ).replace(0, np.nan)
    o03 = ema(o02, 10)
    o04 = df["low"].rolling(33).min()
    o05 = ema(pd.Series(np.where(df["low"] <= o04, o03, 0.0), index=df.index), 3)

    # Preserve the exact user formula, including its non-positive denominator.
    high_delta = df["high"] - o01
    denom = tdx_sma(pd.Series(np.minimum(high_delta, 0.0), index=df.index), 10, 1)
    o06 = tdx_sma(high_delta.abs(), 13, 1) / denom.replace(0, np.nan)
    o07 = ema(o06, 10)
    o08 = df["high"].rolling(33).max()
    o09 = ema(pd.Series(np.where(df["high"] >= o08, o07, 0.0), index=df.index), 3)

    macd = ema(df["close"], 12) - ema(df["close"], 26)
    signal = ema(macd, 9)
    hist = 2 * (macd - signal)

    i = len(df) - 1
    bull_cross = bool(l1.iloc[i] > l2.iloc[i] and l1.iloc[i - 1] <= l2.iloc[i - 1])
    bear_cross = bool(l1.iloc[i] < l2.iloc[i] and l1.iloc[i - 1] >= l2.iloc[i - 1])
    hist_up = bool(hist.iloc[i] > hist.iloc[i - 1])
    hist_dn = bool(hist.iloc[i] < hist.iloc[i - 1])
    resonance = bool(bull_cross and hist_up and l2.iloc[i] < 45)

    accum_rising = bool(np.isfinite(o05.iloc[i]) and o05.iloc[i] > o05.iloc[i - 1])
    distrib_rising = bool(np.isfinite(o09.iloc[i]) and o09.iloc[i] > o09.iloc[i - 1])

    vote = 1 if (l1.iloc[i] > l2.iloc[i] and hist_up) else (
        -1 if (l1.iloc[i] < l2.iloc[i] and hist_dn) else 0
    )
    return {
        "vote": vote,
        "long_event": bool(resonance or (bull_cross and l2.iloc[i] < 55)),
        "short_event": bool(bear_cross and l2.iloc[i] > 70),
        "l1": float(l1.iloc[i]),
        "l2": float(l2.iloc[i]),
        "l3": float(l3.iloc[i]),
        "macd_hist": float(hist.iloc[i]),
        "macd_hist_up": hist_up,
        "accumulation_rising": accum_rising,
        "distribution_rising": distrib_rising,
        "o05": float(o05.iloc[i]) if np.isfinite(o05.iloc[i]) else None,
        "o09": float(o09.iloc[i]) if np.isfinite(o09.iloc[i]) else None,
        "o09_exact_formula_audit": True,
    }


def family_f5(df: pd.DataFrame) -> dict:
    # Legacy SSSS signature for 5m observation only.
    dh = dema(df["high"], 25)
    dl = dema(df["low"], 25)
    fu = 2 * dh - dl
    fl = 2 * dl - dh
    fm = (dh + dl) / 2

    wh_src, wl_src = white_source(df["high"], df["low"])
    wu = ema(wh_src, 90)
    wl = ema(wl_src, 90)
    wm = (wu + wl) / 2
    ww = wu - wl

    sep = fm - wm
    dsep = sep - sep.shift(5)

    raw = []
    for i in range(len(df)):
        vals = [fu.iloc[i], fl.iloc[i], wu.iloc[i], wl.iloc[i], ww.iloc[i]]
        if not all(np.isfinite(v) for v in vals):
            raw.append("OTHER")
            continue
        upper = wu.iloc[i] + 2 * ww.iloc[i]
        lower = wl.iloc[i] - 2 * ww.iloc[i]
        red = fl.iloc[i] >= lower and fu.iloc[i] >= upper
        green = fu.iloc[i] <= upper and fl.iloc[i] <= lower
        gray = fl.iloc[i] >= lower and fu.iloc[i] <= upper
        raw.append("RED" if red else "GREEN" if green else "GRAY" if gray else "OTHER")
    eff = effective_state(raw, 3)

    i = len(df) - 1
    px = float(df["close"].iloc[i])
    ds = float(dsep.iloc[i]) if np.isfinite(dsep.iloc[i]) else 0.0
    mid = float(fm.iloc[i]) if np.isfinite(fm.iloc[i]) else px
    vote = 1 if (ds > 0 and px >= mid) else (-1 if (ds < 0 and px <= mid) else 0)
    return {
        "vote": vote,
        "raw_state": raw[i],
        "effective_state": eff[i],
        "dsep": ds,
        "fast_lower": float(fl.iloc[i]) if np.isfinite(fl.iloc[i]) else None,
        "fast_mid": mid,
        "fast_upper": float(fu.iloc[i]) if np.isfinite(fu.iloc[i]) else None,
        "note": "legacy SSSS signature is diagnostic on 5m, not a validated 5m rule",
    }


def analyze(df: pd.DataFrame) -> dict:
    f1 = family_f1(df)
    f2 = family_f2(df)
    f3 = family_f3(df)
    f4 = family_f4(df)
    f5 = family_f5(df)

    families = {"F1": f1, "F2": f2, "F3": f3, "F4": f4, "F5": f5}
    long_votes = sum(1 for x in families.values() if x.get("vote") == 1)
    short_votes = sum(1 for x in families.values() if x.get("vote") == -1)

    structure_long = bool(f1["long_event"] or f2["long_event"])
    structure_short = bool(f1["short_event"] or f2["short_event"])
    fresh_long = bool(
        f1["long_event"] or f3["long_event"] or f4["long_event"]
    )
    fresh_short = bool(
        f1["short_event"] or f3["short_event"] or f4["short_event"]
    )

    return {
        "families": families,
        "long_votes": long_votes,
        "short_votes": short_votes,
        "structure_long": structure_long,
        "structure_short": structure_short,
        "fresh_long": fresh_long,
        "fresh_short": fresh_short,
        "atr": f1["atr14"],
    }


def default_state() -> dict:
    return {
        "equity": 10000.0,
        "peak_equity": 10000.0,
        "daily_date": None,
        "daily_start_equity": 10000.0,
        "positions": {},
        "trade_seq": 0,
    }


def load_state() -> dict:
    if not STATE_PATH.exists():
        return default_state()
    return json.loads(STATE_PATH.read_text(encoding="utf-8"))


def save_state(state: dict) -> None:
    STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")


def total_margin(state: dict) -> float:
    return sum(float(p["margin_pct"]) for p in state["positions"].values())


def unrealized(position: dict, price: float) -> float:
    direction = 1.0 if position["side"] == "LONG" else -1.0
    return direction * position["qty"] * (price - position["weighted_entry"])


def stop_for(
    side: str,
    entry: float,
    atr: float,
    equity: float,
    gross_notional: float,
) -> float:
    notional_multiple = gross_notional / max(equity, 1e-9)
    account_risk_dist = 0.0125 / max(notional_multiple, 1e-9)
    atr_dist = 2.0 * atr / entry
    dist = min(account_risk_dist, atr_dist, 0.04)
    if side == "LONG":
        return entry * (1 - dist)
    return entry * (1 + dist)


def reason_text(analysis: dict, action: str, side: str) -> str:
    fam = analysis["families"]
    parts = [
        f"{action} {side}",
        f"votes L/S={analysis['long_votes']}/{analysis['short_votes']}",
        f"F1={fam['F1']['vote']} LMD",
        f"F2={fam['F2']['vote']} causal-structure",
        f"F3={fam['F3']['vote']} DXBD({fam['F3']['osc']:.1f})",
        f"F4={fam['F4']['vote']} KDJ/MACD",
        f"F5={fam['F5']['vote']} SSSS({fam['F5']['effective_state']},dsep={fam['F5']['dsep']:.4g})",
    ]
    return "; ".join(parts)


def append_trade(row: dict) -> None:
    exists = TRADES_PATH.exists()
    with TRADES_PATH.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=[
            "trade_id","utc_time","asset","side","action","execution_price",
            "margin_pct","gross_notional","leverage","weighted_entry",
            "hard_stop","reason","F1_LMD","F2_STRUCTURE","F3_DXBD",
            "F4_KDJ_FLOW","F5_SSSS","risk_state","realized_pnl",
            "unrealized_pnl","post_action_equity","strategy_version","status"
        ])
        if not exists:
            w.writeheader()
        w.writerow(row)


def append_journal(text: str) -> None:
    with JOURNAL_PATH.open("a", encoding="utf-8") as f:
        f.write("\n\n" + text + "\n")


def make_log_row(
    state: dict,
    symbol: str,
    position: dict | None,
    side: str,
    action: str,
    price: float,
    analysis: dict,
    realized_pnl: float,
    timestamp_ms: int,
) -> dict:
    p = position or {}
    fam = analysis["families"]
    u = unrealized(position, price) if position else 0.0
    return {
        "trade_id": state["trade_seq"],
        "utc_time": utc(timestamp_ms),
        "asset": symbol,
        "side": side,
        "action": action,
        "execution_price": round(price, 8),
        "margin_pct": round(float(p.get("margin_pct", 0.0)), 6),
        "gross_notional": round(float(p.get("gross_notional", 0.0)), 4),
        "leverage": LEVERAGE,
        "weighted_entry": round(float(p.get("weighted_entry", price)), 8),
        "hard_stop": round(float(p.get("hard_stop", price)), 8),
        "reason": reason_text(analysis, action, side),
        "F1_LMD": json.dumps(fam["F1"], separators=(",", ":")),
        "F2_STRUCTURE": json.dumps(fam["F2"], separators=(",", ":")),
        "F3_DXBD": json.dumps(fam["F3"], separators=(",", ":")),
        "F4_KDJ_FLOW": json.dumps(fam["F4"], separators=(",", ":")),
        "F5_SSSS": json.dumps(fam["F5"], separators=(",", ":")),
        "risk_state": "NORMAL",
        "realized_pnl": round(realized_pnl, 4),
        "unrealized_pnl": round(u, 4),
        "post_action_equity": round(float(state["equity"]), 4),
        "strategy_version": STRATEGY_VERSION,
        "status": "PAPER",
    }


def execute_symbol(state: dict, symbol: str, df: pd.DataFrame) -> list[dict]:
    latest = df.iloc[-1]
    open_ms = int(latest["open_time"])
    close_ms = int(latest["close_time"])
    if open_ms < FORWARD_START_MS:
        return []

    analysis = analyze(df)
    px = float(latest["close"])
    low = float(latest["low"])
    high = float(latest["high"])
    atr = float(analysis["atr"])
    actions = []

    date = utc(close_ms)[:10]
    if state["daily_date"] != date:
        state["daily_date"] = date
        state["daily_start_equity"] = state["equity"]

    state["peak_equity"] = max(state["peak_equity"], state["equity"])
    daily_ret = state["equity"] / state["daily_start_equity"] - 1
    dd = state["equity"] / state["peak_equity"] - 1
    blocked = daily_ret <= DAILY_LOSS_STOP or dd <= PORTFOLIO_KILL_DD

    pos = state["positions"].get(symbol)
    if pos:
        # Hard stop first.
        stop_hit = (
            pos["side"] == "LONG" and low <= pos["hard_stop"]
        ) or (
            pos["side"] == "SHORT" and high >= pos["hard_stop"]
        )
        if stop_hit:
            fill = float(pos["hard_stop"])
            pnl = unrealized(pos, fill)
            fee = abs(pos["qty"] * fill) * BASE_FRICTION
            pnl -= fee
            state["equity"] += pnl
            state["trade_seq"] += 1
            side = pos["side"]
            del state["positions"][symbol]
            row = make_log_row(
                state, symbol, None, side, "CLOSE_STOP", fill, analysis, pnl, close_ms
            )
            append_trade(row)
            actions.append(row)
            return actions

        opposite = (
            pos["side"] == "LONG"
            and analysis["structure_short"]
            and analysis["short_votes"] >= 3
        ) or (
            pos["side"] == "SHORT"
            and analysis["structure_long"]
            and analysis["long_votes"] >= 3
        )
        if opposite:
            pnl = unrealized(pos, px)
            fee = abs(pos["qty"] * px) * BASE_FRICTION
            pnl -= fee
            state["equity"] += pnl
            side = pos["side"]
            state["trade_seq"] += 1
            del state["positions"][symbol]
            row = make_log_row(
                state, symbol, None, side, "CLOSE_OPPOSITE", px, analysis, pnl, close_ms
            )
            append_trade(row)
            actions.append(row)
            return actions

        same_votes = analysis["long_votes"] if pos["side"] == "LONG" else analysis["short_votes"]
        opp_votes = analysis["short_votes"] if pos["side"] == "LONG" else analysis["long_votes"]
        fresh = analysis["fresh_long"] if pos["side"] == "LONG" else analysis["fresh_short"]

        current_u = unrealized(pos, px)
        if opp_votes >= 2 and (current_u > 0 or pos["margin_pct"] > START_MARGIN):
            reduce_qty = pos["qty"] * REDUCE_FRACTION
            direction = 1.0 if pos["side"] == "LONG" else -1.0
            pnl = direction * reduce_qty * (px - pos["weighted_entry"])
            fee = reduce_qty * px * BASE_FRICTION
            pnl -= fee
            state["equity"] += pnl
            pos["qty"] -= reduce_qty
            pos["gross_notional"] = pos["qty"] * px
            pos["margin_pct"] *= (1 - REDUCE_FRACTION)
            state["trade_seq"] += 1
            row = make_log_row(
                state, symbol, pos, pos["side"], "REDUCE", px, analysis, pnl, close_ms
            )
            append_trade(row)
            actions.append(row)
            return actions

        bars_since_action = (
            open_ms - int(pos.get("last_action_open_time", 0))
        ) // (5 * 60 * 1000)
        can_add = (
            not blocked
            and same_votes >= 4
            and opp_votes <= 1
            and fresh
            and bars_since_action >= 4
            and pos["margin_pct"] + ADD_MARGIN <= MAX_ASSET_MARGIN + 1e-12
            and total_margin(state) + ADD_MARGIN <= MAX_PORTFOLIO_MARGIN + 1e-12
        )
        if can_add:
            add_notional = state["equity"] * ADD_MARGIN * LEVERAGE
            add_qty = add_notional / px
            old_notional_cost = pos["qty"] * pos["weighted_entry"]
            pos["qty"] += add_qty
            pos["weighted_entry"] = (old_notional_cost + add_qty * px) / pos["qty"]
            pos["margin_pct"] += ADD_MARGIN
            pos["gross_notional"] = pos["qty"] * px
            candidate_stop = stop_for(
                pos["side"], pos["weighted_entry"], atr,
                state["equity"], pos["gross_notional"]
            )
            if pos["side"] == "LONG":
                pos["hard_stop"] = max(pos["hard_stop"], candidate_stop)
            else:
                pos["hard_stop"] = min(pos["hard_stop"], candidate_stop)
            pos["last_action_open_time"] = open_ms
            fee = add_notional * BASE_FRICTION
            state["equity"] -= fee
            state["trade_seq"] += 1
            row = make_log_row(
                state, symbol, pos, pos["side"], "ADD", px, analysis, -fee, close_ms
            )
            append_trade(row)
            actions.append(row)
            return actions

        return actions

    if blocked:
        return actions

    if total_margin(state) + START_MARGIN > MAX_PORTFOLIO_MARGIN + 1e-12:
        return actions

    long_ok = (
        analysis["structure_long"]
        and analysis["long_votes"] >= 3
        and analysis["short_votes"] <= 1
    )
    short_ok = (
        analysis["structure_short"]
        and analysis["short_votes"] >= 3
        and analysis["long_votes"] <= 1
    )
    if long_ok == short_ok:
        return actions

    side = "LONG" if long_ok else "SHORT"
    notional = state["equity"] * START_MARGIN * LEVERAGE
    qty = notional / px
    stop = stop_for(side, px, atr, state["equity"], notional)
    # 10x rough liquidation distance is ~10%; require >=2x stop distance.
    stop_dist = abs(px - stop) / px
    if 0.09 < 2 * stop_dist:
        return actions

    fee = notional * BASE_FRICTION
    state["equity"] -= fee
    pos = {
        "side": side,
        "qty": qty,
        "weighted_entry": px,
        "margin_pct": START_MARGIN,
        "gross_notional": notional,
        "hard_stop": stop,
        "opened_at": close_ms,
        "last_action_open_time": open_ms,
    }
    state["positions"][symbol] = pos
    state["trade_seq"] += 1
    row = make_log_row(
        state, symbol, pos, side, "OPEN", px, analysis, -fee, close_ms
    )
    append_trade(row)
    actions.append(row)
    return actions


def main() -> int:
    LIVE.mkdir(parents=True, exist_ok=True)
    state = load_state()
    all_actions = []
    observations = []

    for symbol in SYMBOLS:
        df = fetch_klines(symbol, 500)
        a = analyze(df)
        latest = df.iloc[-1]
        observations.append(
            {
                "symbol": symbol,
                "bar_open": utc(int(latest["open_time"])),
                "bar_close": utc(int(latest["close_time"])),
                "close": float(latest["close"]),
                "long_votes": a["long_votes"],
                "short_votes": a["short_votes"],
                "structure_long": a["structure_long"],
                "structure_short": a["structure_short"],
                "f1": a["families"]["F1"],
                "f2": a["families"]["F2"],
                "f3": a["families"]["F3"],
                "f4": a["families"]["F4"],
                "f5": a["families"]["F5"],
            }
        )
        all_actions.extend(execute_symbol(state, symbol, df))

    state["peak_equity"] = max(state["peak_equity"], state["equity"])
    save_state(state)

    print("E043_OBSERVATIONS=" + json.dumps(observations, separators=(",", ":")))
    print("E043_ACTIONS=" + json.dumps(all_actions, separators=(",", ":")))
    print("E043_EQUITY=" + str(state["equity"]))

    if all_actions:
        stamp = datetime.now(timezone.utc).isoformat()
        append_journal(
            f"## {stamp} actions\n\n"
            + "\n".join(
                f"- {x['asset']} {x['action']} {x['side']} @ {x['execution_price']}: {x['reason']}"
                for x in all_actions
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# workflow bootstrap touch
