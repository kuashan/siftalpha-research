from __future__ import annotations

"""Provider-neutral market-data boundary for SiftAlpha integrations.

The strategy layer consumes market bars; it never owns provider selection.
A provider may fail over only by refetching the whole requested window from
another provider. Rows from different providers are never stitched together.
"""

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class MarketProfile:
    market_id: str
    label_zh: str
    timezone: str
    continuous: bool
    sessions: tuple[tuple[str, str], ...] = ()


CRYPTO_24_7 = MarketProfile(
    market_id="CRYPTO",
    label_zh="加密货币",
    timezone="UTC",
    continuous=True,
)

US_EQUITY = MarketProfile(
    market_id="US_EQUITY",
    label_zh="美股",
    timezone="America/New_York",
    continuous=False,
    sessions=(("09:30", "16:00"),),
)

CN_A_SHARE = MarketProfile(
    market_id="CN_A_SHARE",
    label_zh="中国 A 股",
    timezone="Asia/Shanghai",
    continuous=False,
    sessions=(("09:30", "11:30"), ("13:00", "15:00")),
)


class MarketDataProvider(Protocol):
    provider_id: str
    provider_label_zh: str
    profile: MarketProfile

    def klines(self, symbol: str, timeframe: str, limit: int = 300) -> list[Any]:
        ...


@dataclass(frozen=True)
class MarketDataFetch:
    market_id: str
    provider_id: str
    provider_label_zh: str
    symbol: str
    timeframe: str
    rows: list[Any]


class BinancePublicMarketDataProvider:
    """Adapter from the existing unauthenticated Binance USDⓈ-M probe."""

    provider_id = "BINANCE_USDM_PUBLIC"
    provider_label_zh = "币安公开行情"
    profile = CRYPTO_24_7

    def __init__(self, probe):
        self.probe = probe

    def klines(self, symbol: str, timeframe: str, limit: int = 300) -> list[Any]:
        rows = self.probe.klines(symbol, timeframe, limit=limit)
        if not isinstance(rows, list):
            raise RuntimeError("币安公开行情返回格式异常")
        return rows


class MarketDataRouter:
    """Market-aware provider router with whole-window failover."""

    def __init__(self):
        self._providers: dict[str, list[MarketDataProvider]] = {}

    def register(self, provider: MarketDataProvider) -> None:
        market_id = provider.profile.market_id
        self._providers.setdefault(market_id, []).append(provider)

    def for_market(self, market_id: str) -> "BoundMarketData":
        market = str(market_id or "").strip().upper()
        if market not in self._providers:
            raise KeyError(f"market has no provider: {market}")
        return BoundMarketData(self, market)

    def fetch(
        self,
        market_id: str,
        symbol: str,
        timeframe: str,
        *,
        limit: int,
    ) -> MarketDataFetch:
        market = str(market_id or "").strip().upper()
        providers = self._providers.get(market) or []
        if not providers:
            raise RuntimeError(f"没有可用行情供应商：{market}")

        errors: list[str] = []
        for provider in providers:
            try:
                # Important: every fallback provider fetches the complete window.
                # We never splice provider A and provider B bars together.
                rows = provider.klines(symbol, timeframe, limit=limit)
                return MarketDataFetch(
                    market_id=market,
                    provider_id=provider.provider_id,
                    provider_label_zh=provider.provider_label_zh,
                    symbol=symbol,
                    timeframe=timeframe,
                    rows=rows,
                )
            except Exception as exc:
                errors.append(f"{provider.provider_id}:{type(exc).__name__}:{exc}")
        raise RuntimeError("；".join(errors) or f"{market}: 行情获取失败")


class BoundMarketData:
    """A market-specific view consumed by strategy / chart code."""

    def __init__(self, router: MarketDataRouter, market_id: str):
        self.router = router
        self.market_id = market_id

    def fetch(self, symbol: str, timeframe: str, *, limit: int) -> MarketDataFetch:
        return self.router.fetch(
            self.market_id,
            symbol,
            timeframe,
            limit=limit,
        )

    def klines(self, symbol: str, timeframe: str, limit: int = 300) -> list[Any]:
        return self.fetch(symbol, timeframe, limit=limit).rows
