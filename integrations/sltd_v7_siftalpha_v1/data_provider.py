from __future__ import annotations

"""SLTD provider-neutral OHLCV market-data facade.

Strategies consume completed normalized bars only. Provider selection, failover
and provider-scoped caching live below the strategy boundary.
"""

import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    from shared_market_data import MarketDataRouter
except ImportError:
    _integrations_root = Path(__file__).resolve().parent.parent
    if str(_integrations_root) not in sys.path:
        sys.path.insert(0, str(_integrations_root))
    from shared_market_data import MarketDataRouter

from providers.binance_usdm import BINANCE_CRYPTO_SYMBOLS, BinanceUsdMProvider
from providers.yahoo import (
    DEFAULT_START,
    DEFAULT_TIMEFRAME,
    MIN_COMPLETED_BARS,
    TIMEFRAMES,
    MarketDataError,
    YahooFinanceProvider,
    _aggregate_daily_bars,
    _aggregate_four_hour_bars,
    _is_complete,
    _request_params,
    _utc_timestamp,
    normalize_symbol,
    normalize_timeframe,
    timeframe_label,
)


_ROUTER = MarketDataRouter()
_ROUTER.register(YahooFinanceProvider())
_ROUTER.register(BinanceUsdMProvider())
_STOCK_MARKET = _ROUTER.for_market("US_EQUITY")
_CRYPTO_MARKET = _ROUTER.for_market("CRYPTO")
_SAFE_CACHE_PART = re.compile(r"[^A-Z0-9_.\-]+")


def _cache_dir() -> Path:
    root = os.environ.get("SLTD_RUNTIME_DATA_DIR", "").strip()
    path = Path(root) if root else Path(__file__).resolve().parent / "runtime_data"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _safe_cache_part(value: str) -> str:
    return _SAFE_CACHE_PART.sub("_", str(value or "").upper())


def _cache_path(symbol: str, timeframe: str, provider_id: str) -> Path:
    return _cache_dir() / (
        f"{_safe_cache_part(provider_id)}__{_safe_cache_part(symbol)}__"
        f"{_safe_cache_part(timeframe)}.json"
    )


def _read_cache(
    symbol: str,
    timeframe: str,
    provider_id: str,
    max_age_seconds: int | None,
) -> dict | None:
    path = _cache_path(symbol, timeframe, provider_id)
    if not path.exists():
        return None
    if max_age_seconds is not None:
        age = time.time() - path.stat().st_mtime
        if age > max_age_seconds:
            return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if str(payload.get("symbol") or "").upper() != symbol:
            return None
        if str(payload.get("timeframe") or "").lower() != timeframe:
            return None
        if str(payload.get("provider_id") or "").upper() != provider_id.upper():
            return None
        completed = payload.get("completed")
        if isinstance(completed, list) and len(completed) >= MIN_COMPLETED_BARS:
            return payload
    except (OSError, ValueError, TypeError):
        return None
    return None


def _write_cache(
    *,
    symbol: str,
    timeframe: str,
    provider_id: str,
    provider_label: str,
    market_id: str,
    completed: list[dict],
    forming: dict | None,
    meta: dict,
) -> None:
    path = _cache_path(symbol, timeframe, provider_id)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(
        json.dumps(
            {
                "symbol": symbol,
                "timeframe": timeframe,
                "provider_id": provider_id,
                "provider_label": provider_label,
                "market_id": market_id,
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


def _history_window(timeframe: str) -> str:
    cfg = TIMEFRAMES[timeframe]
    if timeframe in {"1d", "5d"}:
        return "2010年至今"
    return f"最近约 {int(cfg['lookback_days'])} 天"


def _decorate_meta(
    base: dict,
    *,
    provider_id: str,
    provider_label: str,
    market_id: str,
    source: str,
    cached: bool,
    timeframe: str,
    rows: int,
    warning: str | None = None,
) -> dict:
    cfg = TIMEFRAMES[timeframe]
    meta = dict(base or {})
    meta.update(
        {
            "provider": provider_label,
            "provider_id": provider_id,
            "market_id": market_id,
            "source": source,
            "cached": cached,
            "rows": rows,
            "timeframe": timeframe,
            "timeframe_label": timeframe_label(timeframe),
            "validated_timeframe": bool(cfg["validated"]),
            "history_window": _history_window(timeframe),
        }
    )
    if warning:
        meta["warning"] = warning
    return meta


def _market_id_for_symbol(symbol: str) -> str:
    return "CRYPTO" if symbol in BINANCE_CRYPTO_SYMBOLS else "US_EQUITY"


def fetch_bars(
    symbol: str,
    timeframe: str,
    *,
    start_date: str = DEFAULT_START,
    force_refresh: bool = False,
) -> tuple[list[dict], dict | None, dict]:
    """Fetch completed and forming bars through the shared MarketDataRouter."""
    symbol = normalize_symbol(symbol)
    timeframe = normalize_timeframe(timeframe)
    cfg = TIMEFRAMES[timeframe]
    cache_age = int(cfg["cache_seconds"])
    market_id = _market_id_for_symbol(symbol)
    provider_ids = _ROUTER.provider_ids(market_id)
    bound_market = _CRYPTO_MARKET if market_id == "CRYPTO" else _STOCK_MARKET

    if not force_refresh:
        for provider_id in provider_ids:
            cached = _read_cache(symbol, timeframe, provider_id, cache_age)
            if not cached:
                continue
            completed = list(cached["completed"])
            forming = cached.get("forming")
            return completed, forming, _decorate_meta(
                dict(cached.get("meta") or {}),
                provider_id=provider_id,
                provider_label=str(cached.get("provider_label") or provider_id),
                market_id=str(cached.get("market_id") or market_id),
                source="缓存",
                cached=True,
                timeframe=timeframe,
                rows=len(completed),
            )

    try:
        fetched = bound_market.fetch(
            symbol,
            timeframe,
            start_date=start_date,
        )
        window = fetched.payload
        if not isinstance(window, dict):
            raise MarketDataError("行情供应商没有返回标准行情窗口")
        completed = list(window.get("completed") or [])
        forming = window.get("forming")
        provider_meta = dict(window.get("meta") or {})
        if len(completed) < MIN_COMPLETED_BARS:
            raise MarketDataError(
                f"{symbol}: {timeframe} 已完成 K 线不足 {MIN_COMPLETED_BARS} 根"
            )
        _write_cache(
            symbol=symbol,
            timeframe=timeframe,
            provider_id=fetched.provider_id,
            provider_label=fetched.provider_label_zh,
            market_id=fetched.market_id,
            completed=completed,
            forming=forming,
            meta=provider_meta,
        )
        return completed, forming, _decorate_meta(
            provider_meta,
            provider_id=fetched.provider_id,
            provider_label=fetched.provider_label_zh,
            market_id=fetched.market_id,
            source="网络",
            cached=False,
            timeframe=timeframe,
            rows=len(completed),
        )
    except Exception as exc:
        # Stale fallback is provider-scoped. A failed AAPL request can never
        # display another symbol's cache, and provider caches are never mixed.
        for provider_id in provider_ids:
            stale = _read_cache(symbol, timeframe, provider_id, None)
            if not stale:
                continue
            completed = list(stale["completed"])
            forming = stale.get("forming")
            return completed, forming, _decorate_meta(
                dict(stale.get("meta") or {}),
                provider_id=provider_id,
                provider_label=str(stale.get("provider_label") or provider_id),
                market_id=str(stale.get("market_id") or market_id),
                source="过期缓存",
                cached=True,
                timeframe=timeframe,
                rows=len(completed),
                warning=f"网络刷新失败，已使用同标的同周期缓存：{type(exc).__name__}",
            )
        if isinstance(exc, (MarketDataError, ValueError)):
            raise
        raise MarketDataError(f"行情获取失败：{type(exc).__name__}: {exc}") from exc


def fetch_daily_candles(
    symbol: str,
    *,
    start_date: str = DEFAULT_START,
    force_refresh: bool = False,
) -> tuple[list[dict], dict]:
    completed, _forming, meta = fetch_bars(
        symbol,
        "1d",
        start_date=start_date,
        force_refresh=force_refresh,
    )
    return completed, meta
