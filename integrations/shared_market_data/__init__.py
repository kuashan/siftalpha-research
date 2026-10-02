from __future__ import annotations

"""SiftAlpha shared provider-neutral market-data routing core."""

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

    def fetch(self, symbol: str, timeframe: str, **kwargs: Any) -> Any:
        ...


@dataclass(frozen=True)
class MarketDataFetch:
    market_id: str
    provider_id: str
    provider_label_zh: str
    symbol: str
    timeframe: str
    payload: Any
    stream_url: str | None = None

    @property
    def rows(self) -> list[Any]:
        if isinstance(self.payload, list):
            return self.payload
        raise TypeError("provider payload is not a row list")


class MarketDataRouter:
    """Route by market and provider priority.

    Failover always asks the next provider for the complete requested window.
    Results from different providers are never stitched together.
    """

    def __init__(self):
        self._providers: dict[str, list[MarketDataProvider]] = {}

    def register(self, provider: MarketDataProvider) -> None:
        market_id = provider.profile.market_id
        self._providers.setdefault(market_id, []).append(provider)

    def provider_ids(self, market_id: str) -> tuple[str, ...]:
        market = str(market_id or "").strip().upper()
        return tuple(p.provider_id for p in self._providers.get(market, ()))

    def fetch(
        self,
        market_id: str,
        symbol: str,
        timeframe: str,
        **kwargs: Any,
    ) -> MarketDataFetch:
        market = str(market_id or "").strip().upper()
        providers = self._providers.get(market) or []
        if not providers:
            raise RuntimeError(f"没有可用行情供应商：{market}")

        errors: list[str] = []
        for provider in providers:
            try:
                payload = provider.fetch(symbol, timeframe, **kwargs)
                stream_factory = getattr(provider, "stream_url", None)
                stream_url = stream_factory(symbol) if callable(stream_factory) else None
                return MarketDataFetch(
                    market_id=market,
                    provider_id=provider.provider_id,
                    provider_label_zh=provider.provider_label_zh,
                    symbol=symbol,
                    timeframe=timeframe,
                    payload=payload,
                    stream_url=stream_url,
                )
            except Exception as exc:
                errors.append(f"{provider.provider_id}:{type(exc).__name__}:{exc}")

        raise RuntimeError("；".join(errors) or f"{market}: 行情获取失败")

    def for_market(self, market_id: str) -> "BoundMarketData":
        market = str(market_id or "").strip().upper()
        if market not in self._providers:
            raise KeyError(f"market has no provider: {market}")
        return BoundMarketData(self, market)


class BoundMarketData:
    def __init__(self, router: MarketDataRouter, market_id: str):
        self.router = router
        self.market_id = market_id

    def fetch(self, symbol: str, timeframe: str, **kwargs: Any) -> MarketDataFetch:
        return self.router.fetch(self.market_id, symbol, timeframe, **kwargs)

    def klines(self, symbol: str, timeframe: str, limit: int = 300) -> list[Any]:
        return self.fetch(symbol, timeframe, limit=limit).rows
