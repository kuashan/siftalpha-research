from __future__ import annotations

"""Dependency-free OHLCV provider for SLTD bar-close execution.

The strategy is NOT bound to a calendar day. A signal is evaluated only from
completed bars of the selected timeframe. The newest still-forming bar is kept
separate for display and never enters the confirmed SLTD decision.
"""

import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


DEFAULT_START = "2010-01-04"
MIN_COMPLETED_BARS = 120
_SYMBOL_RE = re.compile(r"^[A-Z0-9.\-^]{1,15}$")

TIMEFRAMES: dict[str, dict[str, object]] = {
    "5m": {
        "label": "5 分钟",
        "interval": "5m",
        "range": "1mo",
        "seconds": 5 * 60,
        "validated": False,
        "cache_seconds": 15,
    },
    "15m": {
        "label": "15 分钟",
        "interval": "15m",
        "range": "2mo",
        "seconds": 15 * 60,
        "validated": False,
        "cache_seconds": 20,
    },
    "30m": {
        "label": "30 分钟",
        "interval": "30m",
        "range": "2mo",
        "seconds": 30 * 60,
        "validated": False,
        "cache_seconds": 30,
    },
    "1h": {
        "label": "1 小时",
        "interval": "60m",
        "range": "1y",
        "seconds": 60 * 60,
        "validated": False,
        "cache_seconds": 30,
    },
    "1d": {
        "label": "1 天",
        "interval": "1d",
        "seconds": 24 * 60 * 60,
        "validated": True,
        "cache_seconds": 60,
    },
}
DEFAULT_TIMEFRAME = os.environ.get("SLTD_TIMEFRAME", "1d").strip() or "1d"
if DEFAULT_TIMEFRAME not in TIMEFRAMES:
    DEFAULT_TIMEFRAME = "1d"


class MarketDataError(RuntimeError):
    pass


def normalize_symbol(value: str) -> str:
    symbol = str(value or "").strip().upper()
    if not _SYMBOL_RE.fullmatch(symbol):
        raise ValueError("股票代码格式不正确")
    return symbol


def normalize_timeframe(value: str) -> str:
    timeframe = str(value or "").strip().lower()
    if timeframe not in TIMEFRAMES:
        raise ValueError("不支持这个 K 线周期")
    return timeframe


def timeframe_label(value: str) -> str:
    timeframe = normalize_timeframe(value)
    return str(TIMEFRAMES[timeframe]["label"])


def _utc_timestamp(date_text: str) -> int:
    dt = datetime.strptime(date_text, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return int(dt.timestamp())


def _cache_dir() -> Path:
    root = os.environ.get("SLTD_RUNTIME_DATA_DIR", "").strip()
    path = Path(root) if root else Path(__file__).resolve().parent / "runtime_data"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _cache_path(symbol: str, timeframe: str) -> Path:
    safe = timeframe.replace("/", "_")
    return _cache_dir() / f"{symbol}_{safe}.json"


def _read_cache(
    symbol: str,
    timeframe: str,
    max_age_seconds: int | None,
) -> dict | None:
    path = _cache_path(symbol, timeframe)
    if not path.exists():
        return None
    if max_age_seconds is not None:
        age = time.time() - path.stat().st_mtime
        if age > max_age_seconds:
            return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        completed = payload.get("completed")
        if isinstance(completed, list) and len(completed) >= MIN_COMPLETED_BARS:
            return payload
    except (OSError, ValueError, TypeError):
        return None
    return None


def _write_cache(
    symbol: str,
    timeframe: str,
    completed: list[dict],
    forming: dict | None,
    meta: dict,
) -> None:
    path = _cache_path(symbol, timeframe)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(
        json.dumps(
            {
                "symbol": symbol,
                "timeframe": timeframe,
                "provider": "Yahoo Finance chart API",
                "saved_at_utc": datetime.now(timezone.utc).isoformat(),
                "completed": completed,
                "forming": forming,
                "meta": meta,
            },
            ensure_ascii=False,
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )
    tmp.replace(path)


def _request_chart(symbol: str, timeframe: str, start_date: str) -> dict:
    cfg = TIMEFRAMES[timeframe]
    params: dict[str, object] = {
        "interval": str(cfg["interval"]),
        "events": "history",
        "includeAdjustedClose": "true",
        "includePrePost": "false",
    }

    if timeframe == "1d":
        params["period1"] = _utc_timestamp(start_date)
        params["period2"] = int(datetime.now(timezone.utc).timestamp()) + 2 * 86400
    else:
        params["range"] = str(cfg["range"])

    query = urlencode(params)
    errors: list[str] = []
    for host in ("query1.finance.yahoo.com", "query2.finance.yahoo.com"):
        url = f"https://{host}/v8/finance/chart/{quote(symbol)}?{query}"
        req = Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (SiftAlpha SLTD V7)",
                "Accept": "application/json,text/plain,*/*",
            },
        )
        try:
            with urlopen(req, timeout=18) as response:
                return json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
            errors.append(f"{host}:{type(exc).__name__}:{exc}")
    raise MarketDataError("；".join(errors) or "无法获取 Yahoo Finance 行情")


def _is_complete(
    ts: int,
    timeframe: str,
    now_ts: int,
    regular_start: int | None,
    regular_end: int | None,
) -> bool:
    """Return whether this provider bar has reached its selected-timeframe close."""
    if timeframe == "1d":
        if (
            regular_start is not None
            and regular_end is not None
            and regular_start <= ts <= regular_end
        ):
            return now_ts >= regular_end
        # Any daily bar from an earlier session is closed.
        return regular_start is None or ts < regular_start or now_ts >= regular_end

    seconds = int(TIMEFRAMES[timeframe]["seconds"])
    theoretical_end = ts + seconds
    if (
        regular_start is not None
        and regular_end is not None
        and regular_start <= ts < regular_end
    ):
        theoretical_end = min(theoretical_end, regular_end)
    return now_ts >= theoretical_end


def _parse_chart(
    payload: dict,
    symbol: str,
    timeframe: str,
) -> tuple[list[dict], dict | None, dict]:
    chart = payload.get("chart") if isinstance(payload, dict) else None
    error = chart.get("error") if isinstance(chart, dict) else None
    if error:
        raise MarketDataError(str(error))

    results = chart.get("result") if isinstance(chart, dict) else None
    if not isinstance(results, list) or not results:
        raise MarketDataError(f"{symbol}: 行情返回为空")

    result = results[0]
    provider_meta = result.get("meta") or {}
    trading = provider_meta.get("currentTradingPeriod") or {}
    regular = trading.get("regular") or {}

    try:
        regular_start = int(regular.get("start")) if regular.get("start") is not None else None
        regular_end = int(regular.get("end")) if regular.get("end") is not None else None
    except (TypeError, ValueError):
        regular_start = None
        regular_end = None

    timestamps = result.get("timestamp") or []
    indicators = result.get("indicators") or {}
    quotes = indicators.get("quote") or []
    if not quotes:
        raise MarketDataError(f"{symbol}: 缺少 OHLCV")
    q = quotes[0]

    opens = q.get("open") or []
    highs = q.get("high") or []
    lows = q.get("low") or []
    closes = q.get("close") or []
    volumes = q.get("volume") or []
    now_ts = int(time.time())

    bars: list[dict] = []
    for i, raw_ts in enumerate(timestamps):
        try:
            ts = int(raw_ts)
            values = (
                opens[i],
                highs[i],
                lows[i],
                closes[i],
                volumes[i] if i < len(volumes) else 0,
            )
        except (IndexError, TypeError, ValueError):
            continue
        if any(x is None for x in values[:4]):
            continue

        try:
            if timeframe == "1d":
                label = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")
            else:
                label = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            candle = {
                "date": label,
                "open_time": ts,
                "open": float(values[0]),
                "high": float(values[1]),
                "low": float(values[2]),
                "close": float(values[3]),
                "volume": float(values[4] or 0.0),
                "complete": _is_complete(
                    ts,
                    timeframe,
                    now_ts,
                    regular_start,
                    regular_end,
                ),
            }
        except (TypeError, ValueError, OSError):
            continue
        if candle["high"] < candle["low"]:
            continue
        bars.append(candle)

    # Provider may occasionally duplicate a timestamp during session transitions.
    dedup: dict[int, dict] = {int(c["open_time"]): c for c in bars}
    ordered = [dedup[k] for k in sorted(dedup)]
    completed = [
        {k: v for k, v in c.items() if k != "complete"}
        for c in ordered
        if bool(c["complete"])
    ]
    forming_candidates = [c for c in ordered if not bool(c["complete"])]
    forming = None
    if forming_candidates:
        raw = forming_candidates[-1]
        forming = {k: v for k, v in raw.items() if k != "complete"}

    if len(completed) < MIN_COMPLETED_BARS:
        raise MarketDataError(
            f"{symbol}: {timeframe} 已完成 K 线不足 {MIN_COMPLETED_BARS} 根"
        )

    meta = {
        "exchange_name": provider_meta.get("exchangeName"),
        "exchange_timezone": provider_meta.get("exchangeTimezoneName"),
        "currency": provider_meta.get("currency"),
        "regular_market_start": regular_start,
        "regular_market_end": regular_end,
        "has_forming_bar": forming is not None,
    }
    return completed, forming, meta


def fetch_bars(
    symbol: str,
    timeframe: str,
    *,
    start_date: str = DEFAULT_START,
    force_refresh: bool = False,
) -> tuple[list[dict], dict | None, dict]:
    """Fetch selected-timeframe bars and separate confirmed vs forming bars."""
    symbol = normalize_symbol(symbol)
    timeframe = normalize_timeframe(timeframe)
    cfg = TIMEFRAMES[timeframe]
    cache_age = int(cfg["cache_seconds"])

    if not force_refresh:
        cached = _read_cache(symbol, timeframe, cache_age)
        if cached:
            completed = list(cached["completed"])
            forming = cached.get("forming")
            cached_meta = dict(cached.get("meta") or {})
            cached_meta.update(
                {
                    "provider": "Yahoo Finance",
                    "source": "cache",
                    "cached": True,
                    "rows": len(completed),
                    "timeframe": timeframe,
                    "timeframe_label": timeframe_label(timeframe),
                    "validated_timeframe": bool(cfg["validated"]),
                }
            )
            return completed, forming, cached_meta

    try:
        payload = _request_chart(symbol, timeframe, start_date)
        completed, forming, provider_meta = _parse_chart(payload, symbol, timeframe)
        _write_cache(symbol, timeframe, completed, forming, provider_meta)
        meta = dict(provider_meta)
        meta.update(
            {
                "provider": "Yahoo Finance",
                "source": "network",
                "cached": False,
                "rows": len(completed),
                "timeframe": timeframe,
                "timeframe_label": timeframe_label(timeframe),
                "validated_timeframe": bool(cfg["validated"]),
            }
        )
        return completed, forming, meta
    except Exception as exc:
        stale = _read_cache(symbol, timeframe, None)
        if stale:
            completed = list(stale["completed"])
            forming = stale.get("forming")
            stale_meta = dict(stale.get("meta") or {})
            stale_meta.update(
                {
                    "provider": "Yahoo Finance",
                    "source": "stale-cache",
                    "cached": True,
                    "rows": len(completed),
                    "timeframe": timeframe,
                    "timeframe_label": timeframe_label(timeframe),
                    "validated_timeframe": bool(cfg["validated"]),
                    "warning": f"网络刷新失败，已使用缓存：{type(exc).__name__}",
                }
            )
            return completed, forming, stale_meta
        if isinstance(exc, (MarketDataError, ValueError)):
            raise
        raise MarketDataError(f"行情获取失败：{type(exc).__name__}: {exc}") from exc


def fetch_daily_candles(
    symbol: str,
    *,
    start_date: str = DEFAULT_START,
    force_refresh: bool = False,
) -> tuple[list[dict], dict]:
    """Backward-compatible daily wrapper used by older callers/tests."""
    completed, _forming, meta = fetch_bars(
        symbol,
        "1d",
        start_date=start_date,
        force_refresh=force_refresh,
    )
    return completed, meta
