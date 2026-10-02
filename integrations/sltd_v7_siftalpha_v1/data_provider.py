from __future__ import annotations

"""Small, dependency-free daily OHLCV provider for the SLTD Web project."""

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
CACHE_MAX_AGE_SECONDS = 15 * 60
_SYMBOL_RE = re.compile(r"^[A-Z0-9.\-^]{1,15}$")


class MarketDataError(RuntimeError):
    pass


def normalize_symbol(value: str) -> str:
    symbol = str(value or "").strip().upper()
    if not _SYMBOL_RE.fullmatch(symbol):
        raise ValueError("股票代码格式不正确")
    return symbol


def _utc_timestamp(date_text: str) -> int:
    dt = datetime.strptime(date_text, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return int(dt.timestamp())


def _cache_dir() -> Path:
    root = os.environ.get("SLTD_RUNTIME_DATA_DIR", "").strip()
    if root:
        path = Path(root)
    else:
        path = Path(__file__).resolve().parent / "runtime_data"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _cache_path(symbol: str) -> Path:
    return _cache_dir() / f"{symbol}_daily.json"


def _read_cache(symbol: str, max_age_seconds: int | None) -> list[dict] | None:
    path = _cache_path(symbol)
    if not path.exists():
        return None
    if max_age_seconds is not None:
        age = time.time() - path.stat().st_mtime
        if age > max_age_seconds:
            return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        candles = payload.get("candles")
        if isinstance(candles, list) and len(candles) >= 120:
            return candles
    except (OSError, ValueError, TypeError):
        return None
    return None


def _write_cache(symbol: str, candles: list[dict]) -> None:
    path = _cache_path(symbol)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(
        json.dumps(
            {
                "symbol": symbol,
                "provider": "Yahoo Finance chart API",
                "saved_at_utc": datetime.now(timezone.utc).isoformat(),
                "candles": candles,
            },
            ensure_ascii=False,
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )
    tmp.replace(path)


def _request_chart(symbol: str, start_date: str) -> dict:
    period1 = _utc_timestamp(start_date)
    period2 = int(datetime.now(timezone.utc).timestamp()) + 2 * 86400
    params = urlencode(
        {
            "period1": period1,
            "period2": period2,
            "interval": "1d",
            "events": "history",
            "includeAdjustedClose": "true",
        }
    )
    errors: list[str] = []
    for host in ("query1.finance.yahoo.com", "query2.finance.yahoo.com"):
        url = f"https://{host}/v8/finance/chart/{quote(symbol)}?{params}"
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


def _parse_chart(payload: dict, symbol: str) -> list[dict]:
    chart = payload.get("chart") if isinstance(payload, dict) else None
    error = chart.get("error") if isinstance(chart, dict) else None
    if error:
        raise MarketDataError(str(error))

    results = chart.get("result") if isinstance(chart, dict) else None
    if not isinstance(results, list) or not results:
        raise MarketDataError(f"{symbol}: 行情返回为空")

    result = results[0]
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

    candles: list[dict] = []
    for i, ts in enumerate(timestamps):
        try:
            values = (
                opens[i],
                highs[i],
                lows[i],
                closes[i],
                volumes[i] if i < len(volumes) else 0,
            )
        except IndexError:
            continue
        if any(x is None for x in values[:4]):
            continue
        try:
            day = datetime.fromtimestamp(int(ts), tz=timezone.utc).strftime("%Y-%m-%d")
            candle = {
                "date": day,
                "open": float(values[0]),
                "high": float(values[1]),
                "low": float(values[2]),
                "close": float(values[3]),
                "volume": float(values[4] or 0.0),
            }
        except (TypeError, ValueError, OSError):
            continue
        if candle["high"] < candle["low"]:
            continue
        candles.append(candle)

    dedup: dict[str, dict] = {c["date"]: c for c in candles}
    out = [dedup[d] for d in sorted(dedup)]
    if len(out) < 120:
        raise MarketDataError(f"{symbol}: 有效日线不足 120 根")
    return out


def fetch_daily_candles(
    symbol: str,
    *,
    start_date: str = DEFAULT_START,
    force_refresh: bool = False,
) -> tuple[list[dict], dict]:
    symbol = normalize_symbol(symbol)

    if not force_refresh:
        cached = _read_cache(symbol, CACHE_MAX_AGE_SECONDS)
        if cached:
            return cached, {
                "provider": "Yahoo Finance",
                "source": "cache",
                "cached": True,
                "rows": len(cached),
            }

    try:
        payload = _request_chart(symbol, start_date)
        candles = _parse_chart(payload, symbol)
        _write_cache(symbol, candles)
        return candles, {
            "provider": "Yahoo Finance",
            "source": "network",
            "cached": False,
            "rows": len(candles),
        }
    except Exception as exc:
        stale = _read_cache(symbol, None)
        if stale:
            return stale, {
                "provider": "Yahoo Finance",
                "source": "stale-cache",
                "cached": True,
                "rows": len(stale),
                "warning": f"网络刷新失败，已使用缓存：{type(exc).__name__}",
            }
        if isinstance(exc, (MarketDataError, ValueError)):
            raise
        raise MarketDataError(f"行情获取失败：{type(exc).__name__}: {exc}") from exc
