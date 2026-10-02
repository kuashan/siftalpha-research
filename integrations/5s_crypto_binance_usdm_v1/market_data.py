from __future__ import annotations

"""5s Crypto provider adapter on top of SiftAlpha shared market-data core."""

import sys
from pathlib import Path
from typing import Any

try:
    from shared_market_data import (
        BoundMarketData,
        CN_A_SHARE,
        CRYPTO_24_7,
        MarketDataFetch,
        MarketDataProvider,
        MarketDataRouter,
        MarketProfile,
        US_EQUITY,
    )
except ImportError:
    _integrations_root = Path(__file__).resolve().parent.parent
    if str(_integrations_root) not in sys.path:
        sys.path.insert(0, str(_integrations_root))
    from shared_market_data import (
        BoundMarketData,
        CN_A_SHARE,
        CRYPTO_24_7,
        MarketDataFetch,
        MarketDataProvider,
        MarketDataRouter,
        MarketProfile,
        US_EQUITY,
    )


class BinancePublicMarketDataProvider:
    """Adapter from the existing unauthenticated Binance USDⓈ-M probe."""

    provider_id = "BINANCE_USDM_PUBLIC"
    provider_label_zh = "币安公开行情"
    profile = CRYPTO_24_7

    def __init__(self, probe):
        self.probe = probe

    def fetch(
        self,
        symbol: str,
        timeframe: str,
        *,
        limit: int = 300,
        **_kwargs: Any,
    ) -> list[Any]:
        rows = self.probe.klines(symbol, timeframe, limit=limit)
        if not isinstance(rows, list):
            raise RuntimeError("币安公开行情返回格式异常")
        return rows

    def klines(self, symbol: str, timeframe: str, limit: int = 300) -> list[Any]:
        return self.fetch(symbol, timeframe, limit=limit)

    def stream_url(self, symbol: str) -> str | None:
        name = str(symbol or "").strip().lower()
        if not name:
            return None
        return f"wss://fstream.binance.com/market/ws/{name}@ticker"


__all__ = [
    "MarketProfile",
    "MarketDataProvider",
    "MarketDataFetch",
    "MarketDataRouter",
    "BoundMarketData",
    "CRYPTO_24_7",
    "US_EQUITY",
    "CN_A_SHARE",
    "BinancePublicMarketDataProvider",
]
