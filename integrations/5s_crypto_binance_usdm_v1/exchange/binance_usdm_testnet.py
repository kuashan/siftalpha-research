from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_DOWN
from typing import Any, Iterable


class TestnetGuardError(RuntimeError):
    pass


class TestnetDependencyError(RuntimeError):
    pass


class TestnetConfigurationError(RuntimeError):
    pass


@dataclass(frozen=True)
class SymbolRules:
    symbol: str
    status: str
    contract_type: str
    quote_asset: str
    tick_size: Decimal | None
    step_size: Decimal | None
    min_qty: Decimal | None
    max_qty: Decimal | None
    min_notional: Decimal | None


def _plain(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, dict):
        return {str(k): _plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(v) for v in value]
    model_dump = getattr(value, "model_dump", None)
    if callable(model_dump):
        try:
            return _plain(model_dump(by_alias=True, exclude_none=True))
        except TypeError:
            return _plain(model_dump())
    to_dict = getattr(value, "to_dict", None)
    if callable(to_dict):
        return _plain(to_dict())
    if hasattr(value, "__dict__"):
        return _plain({k: v for k, v in vars(value).items() if not k.startswith("_")})
    return str(value)


def _response_data(response: Any) -> Any:
    data = getattr(response, "data", None)
    return _plain(data() if callable(data) else response)


def _as_decimal(value: Any) -> Decimal | None:
    if value in (None, ""):
        return None
    return Decimal(str(value))


def _first(mapping: dict[str, Any], *keys: str, default: Any = None) -> Any:
    for key in keys:
        if key in mapping:
            return mapping[key]
    return default


def _filter_map(filters: Iterable[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for item in filters:
        ftype = str(_first(item, "filterType", "filter_type", default=""))
        if ftype:
            out[ftype] = item
    return out


def floor_to_step(value: Decimal, step: Decimal | None) -> Decimal:
    if not step or step <= 0:
        return value
    units = (value / step).to_integral_value(rounding=ROUND_DOWN)
    return units * step


class BinanceUsdMTestnetAdapter:
    """Official-SDK wrapper with a hard TESTNET-only mutation boundary.

    The class can receive a mock client in tests. When a client is not supplied,
    Binance's official modular USDⓈ-M Futures SDK is imported lazily.
    """

    def __init__(
        self,
        *,
        mode: str,
        api_key: str = "",
        api_secret: str = "",
        allowed_symbols: Iterable[str] = ("BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT"),
        allowed_timeframes: Iterable[str] = ("15m", "1h", "2h", "4h", "6h", "12h", "1d"),
        client: Any = None,
    ):
        self.mode = mode.upper().strip()
        self.api_key = api_key.strip()
        self.api_secret = api_secret.strip()
        self.allowed_symbols = tuple(allowed_symbols)
        self.allowed_timeframes = tuple(allowed_timeframes)
        self._client = client

    @property
    def credentials_present(self) -> bool:
        return bool(self.api_key and self.api_secret)

    def _require_testnet(self) -> None:
        if self.mode != "TESTNET":
            raise TestnetGuardError("authenticated Binance mutation/read is TESTNET-only in M2")
        if not self.credentials_present:
            raise TestnetConfigurationError("BINANCE_TESTNET_API_KEY/SECRET are required")

    def _rest(self):
        self._require_testnet()
        if self._client is None:
            try:
                from binance_sdk_derivatives_trading_usds_futures.derivatives_trading_usds_futures import (
                    ConfigurationRestAPI,
                    DERIVATIVES_TRADING_USDS_FUTURES_REST_API_TESTNET_URL,
                    DerivativesTradingUsdsFutures,
                )
            except Exception as exc:
                raise TestnetDependencyError(
                    "Install binance-sdk-derivatives-trading-usds-futures==17.5.0"
                ) from exc

            configuration = ConfigurationRestAPI(
                api_key=self.api_key,
                api_secret=self.api_secret,
                base_path=DERIVATIVES_TRADING_USDS_FUTURES_REST_API_TESTNET_URL,
            )
            self._client = DerivativesTradingUsdsFutures(config_rest_api=configuration)
        return self._client.rest_api if hasattr(self._client, "rest_api") else self._client

    def _check_symbol(self, symbol: str) -> str:
        symbol = symbol.upper().strip()
        if symbol not in self.allowed_symbols:
            raise ValueError(f"unsupported symbol: {symbol}")
        return symbol

    def _check_timeframe(self, timeframe: str) -> str:
        timeframe = timeframe.strip()
        if timeframe not in self.allowed_timeframes:
            raise ValueError(f"unsupported timeframe: {timeframe}")
        return timeframe

    # ---- Read-only market/account inspection ----

    def exchange_information(self) -> dict[str, Any]:
        data = _response_data(self._rest().exchange_information())
        if not isinstance(data, dict):
            raise RuntimeError("unexpected exchange information response")
        return data

    def symbol_rules(self, symbol: str) -> SymbolRules:
        symbol = self._check_symbol(symbol)
        info = self.exchange_information()
        symbols = _first(info, "symbols", default=[]) or []
        item = next((x for x in symbols if str(_first(x, "symbol", default="")).upper() == symbol), None)
        if not item:
            raise RuntimeError(f"{symbol} missing from Testnet exchange information")

        filters = _filter_map(_first(item, "filters", default=[]) or [])
        price = filters.get("PRICE_FILTER", {})
        lot = filters.get("MARKET_LOT_SIZE") or filters.get("LOT_SIZE", {})
        notional = filters.get("MIN_NOTIONAL", {})

        return SymbolRules(
            symbol=symbol,
            status=str(_first(item, "status", default="")),
            contract_type=str(_first(item, "contractType", "contract_type", default="")),
            quote_asset=str(_first(item, "quoteAsset", "quote_asset", default="")),
            tick_size=_as_decimal(_first(price, "tickSize", "tick_size")),
            step_size=_as_decimal(_first(lot, "stepSize", "step_size")),
            min_qty=_as_decimal(_first(lot, "minQty", "min_qty")),
            max_qty=_as_decimal(_first(lot, "maxQty", "max_qty")),
            min_notional=_as_decimal(_first(notional, "notional", "minNotional", "min_notional")),
        )

    def klines(self, symbol: str, timeframe: str, limit: int = 200) -> Any:
        symbol = self._check_symbol(symbol)
        timeframe = self._check_timeframe(timeframe)
        if not 1 <= int(limit) <= 1500:
            raise ValueError("limit must be 1..1500")
        return _response_data(
            self._rest().kline_candlestick_data(
                symbol=symbol,
                interval=timeframe,
                limit=int(limit),
            )
        )

    def leverage_brackets(self, symbol: str) -> Any:
        symbol = self._check_symbol(symbol)
        return _response_data(self._rest().notional_and_leverage_brackets(symbol=symbol))

    def position_mode(self) -> dict[str, Any]:
        data = _response_data(self._rest().get_current_position_mode())
        if not isinstance(data, dict):
            raise RuntimeError("unexpected position mode response")
        return data

    def is_one_way(self) -> bool:
        data = self.position_mode()
        return not bool(_first(data, "dualSidePosition", "dual_side_position", default=True))

    def balances(self) -> Any:
        return _response_data(self._rest().futures_account_balance_v3())

    def positions(self, symbol: str | None = None) -> Any:
        checked = self._check_symbol(symbol) if symbol else None
        return _response_data(self._rest().position_information_v2(symbol=checked))

    def open_orders(self, symbol: str | None = None) -> Any:
        checked = self._check_symbol(symbol) if symbol else None
        return _response_data(self._rest().current_all_open_orders(symbol=checked))

    def query_order(
        self,
        symbol: str,
        *,
        order_id: int | None = None,
        client_order_id: str | None = None,
    ) -> Any:
        symbol = self._check_symbol(symbol)
        if order_id is None and not client_order_id:
            raise ValueError("order_id or client_order_id is required")
        return _response_data(
            self._rest().query_order(
                symbol=symbol,
                order_id=order_id,
                orig_client_order_id=client_order_id,
            )
        )

    # ---- TESTNET-only account/order mutations ----

    def ensure_one_way(self) -> dict[str, Any]:
        if self.is_one_way():
            return {"changed": False, "one_way": True}
        data = _response_data(self._rest().change_position_mode(dual_side_position="false"))
        return {"changed": True, "one_way": True, "response": data}

    def margin_type(self, symbol: str) -> str | None:
        symbol = self._check_symbol(symbol)
        positions = self.positions(symbol)
        rows = positions if isinstance(positions, list) else [positions]
        for row in rows:
            if isinstance(row, dict) and str(_first(row, "symbol", default="")).upper() == symbol:
                value = _first(row, "marginType", "margin_type")
                if value:
                    return str(value).upper()
        return None

    def ensure_isolated(self, symbol: str) -> dict[str, Any]:
        symbol = self._check_symbol(symbol)
        current = self.margin_type(symbol)
        if current == "ISOLATED":
            return {"changed": False, "margin_type": "ISOLATED"}
        data = _response_data(
            self._rest().change_margin_type(symbol=symbol, margin_type="ISOLATED")
        )
        return {"changed": True, "margin_type": "ISOLATED", "response": data}

    def set_leverage(self, symbol: str, leverage: int) -> Any:
        symbol = self._check_symbol(symbol)
        leverage = int(leverage)
        if not 1 <= leverage <= 125:
            raise ValueError("leverage must be 1..125")
        return _response_data(
            self._rest().change_initial_leverage(symbol=symbol, leverage=leverage)
        )

    def submit_limit_buy(
        self,
        symbol: str,
        *,
        quantity: Decimal,
        price: Decimal,
        client_order_id: str,
    ) -> Any:
        symbol = self._check_symbol(symbol)
        if quantity <= 0 or price <= 0:
            raise ValueError("quantity and price must be > 0")
        if not client_order_id or len(client_order_id) > 36:
            raise ValueError("client_order_id must be 1..36 chars")
        return _response_data(
            self._rest().new_order(
                symbol=symbol,
                side="BUY",
                type="LIMIT",
                position_side="BOTH",
                time_in_force="GTC",
                quantity=float(quantity),
                price=float(price),
                new_client_order_id=client_order_id,
            )
        )

    def cancel_order(
        self,
        symbol: str,
        *,
        order_id: int | None = None,
        client_order_id: str | None = None,
    ) -> Any:
        symbol = self._check_symbol(symbol)
        if order_id is None and not client_order_id:
            raise ValueError("order_id or client_order_id is required")
        return _response_data(
            self._rest().cancel_order(
                symbol=symbol,
                order_id=order_id,
                orig_client_order_id=client_order_id,
            )
        )
