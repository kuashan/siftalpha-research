from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_DOWN
from threading import RLock
import time
from typing import Any, Iterable


class TestnetGuardError(RuntimeError):
    pass


class TestnetDependencyError(RuntimeError):
    pass


class TestnetConfigurationError(RuntimeError):
    pass


_CLOCK_PATCH_LOCK = RLock()
_CLOCK_SYNC_TTL_SECONDS = 300.0


def compute_clock_offset_ms(
    server_time_ms: int,
    local_before_ms: int,
    local_after_ms: int,
) -> int:
    """Estimate Binance clock offset using the midpoint of one round trip."""
    before = int(local_before_ms)
    after = max(before, int(local_after_ms))
    midpoint = before + ((after - before) // 2)
    return int(server_time_ms) - midpoint


def _install_binance_clock_offset(offset_ms: int) -> None:
    """Make the official SDK timestamp generator use Binance server time.

    The patch is process-local only. It does not change Android/Alpine system
    time and disappears when this Python process exits.
    """
    try:
        import binance_common.utils as binance_utils
    except Exception as exc:
        raise TestnetDependencyError(
            "Install binance-sdk-derivatives-trading-usds-futures==17.5.0"
        ) from exc

    with _CLOCK_PATCH_LOCK:
        if not hasattr(binance_utils, "_siftalpha_original_get_timestamp"):
            binance_utils._siftalpha_original_get_timestamp = binance_utils.get_timestamp

            def _siftalpha_synced_timestamp() -> int:
                base = int(binance_utils._siftalpha_original_get_timestamp())
                offset = int(getattr(binance_utils, "_siftalpha_time_offset_ms", 0))
                return base + offset

            binance_utils.get_timestamp = _siftalpha_synced_timestamp

        binance_utils._siftalpha_time_offset_ms = int(offset_ms)


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
    """Official-SDK wrapper with a hard sandbox-only mutation boundary.

    DEMO is the primary environment used by the Web UI. TESTNET remains
    supported for backward-compatible acceptance checks.

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
        self._client_injected = client is not None
        self._clock_lock = RLock()
        self._clock_offset_ms: int | None = None
        self._clock_synced_at_monotonic = 0.0

    @property
    def credentials_present(self) -> bool:
        return bool(self.api_key and self.api_secret)

    def _require_sandbox(self) -> None:
        if self.mode not in {"DEMO", "TESTNET"}:
            raise TestnetGuardError("authenticated Binance access is sandbox-only in M2")
        if not self.credentials_present:
            raise TestnetConfigurationError("Binance sandbox API key/secret are required")

    def _rest(self):
        self._require_sandbox()
        if self._client is None:
            try:
                from binance_common.configuration import ConfigurationRestAPI
                from binance_common.constants import (
                    DERIVATIVES_TRADING_USDS_FUTURES_REST_API_TESTNET_URL,
                )
                try:
                    from binance_common.constants import (
                        DERIVATIVES_TRADING_USDS_FUTURES_REST_API_DEMO_URL,
                    )
                except ImportError:
                    DERIVATIVES_TRADING_USDS_FUTURES_REST_API_DEMO_URL = "https://demo-fapi.binance.com"
                from binance_sdk_derivatives_trading_usds_futures.derivatives_trading_usds_futures import (
                    DerivativesTradingUsdsFutures,
                )
            except Exception as exc:
                raise TestnetDependencyError(
                    "Install binance-sdk-derivatives-trading-usds-futures==17.5.0"
                ) from exc

            base_path = (
                DERIVATIVES_TRADING_USDS_FUTURES_REST_API_DEMO_URL
                if self.mode == "DEMO"
                else DERIVATIVES_TRADING_USDS_FUTURES_REST_API_TESTNET_URL
            )
            configuration = ConfigurationRestAPI(
                api_key=self.api_key,
                api_secret=self.api_secret,
                base_path=base_path,
            )
            self._client = DerivativesTradingUsdsFutures(config_rest_api=configuration)
        return self._client.rest_api if hasattr(self._client, "rest_api") else self._client

    def _sync_clock(self, rest: Any, *, force: bool = False) -> None:
        # Existing unit-test mocks from earlier milestones may not expose the
        # public server-time endpoint. Real Binance SDK clients always do.
        if self._client_injected and not hasattr(rest, "check_server_time"):
            return

        now = time.monotonic()
        if (
            not force
            and self._clock_offset_ms is not None
            and now - self._clock_synced_at_monotonic < _CLOCK_SYNC_TTL_SECONDS
        ):
            return

        with self._clock_lock:
            now = time.monotonic()
            if (
                not force
                and self._clock_offset_ms is not None
                and now - self._clock_synced_at_monotonic < _CLOCK_SYNC_TTL_SECONDS
            ):
                return

            local_before = int(time.time() * 1000)
            data = _response_data(rest.check_server_time())
            local_after = int(time.time() * 1000)
            if not isinstance(data, dict):
                raise RuntimeError("币安服务器时间响应格式异常")
            server_time = _first(data, "serverTime", "server_time")
            try:
                server_time_ms = int(server_time)
            except (TypeError, ValueError) as exc:
                raise RuntimeError("币安服务器时间不可用") from exc
            if server_time_ms <= 0:
                raise RuntimeError("币安服务器时间不可用")

            offset_ms = compute_clock_offset_ms(
                server_time_ms,
                local_before,
                local_after,
            )
            _install_binance_clock_offset(offset_ms)
            self._clock_offset_ms = offset_ms
            self._clock_synced_at_monotonic = time.monotonic()

    def _signed_rest(self):
        rest = self._rest()
        self._sync_clock(rest)
        return rest

    @property
    def clock_offset_ms(self) -> int | None:
        return self._clock_offset_ms

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
        return _response_data(self._signed_rest().notional_and_leverage_brackets(symbol=symbol))

    def position_mode(self) -> dict[str, Any]:
        data = _response_data(self._signed_rest().get_current_position_mode())
        if not isinstance(data, dict):
            raise RuntimeError("unexpected position mode response")
        return data

    def is_one_way(self) -> bool:
        data = self.position_mode()
        return not bool(_first(data, "dualSidePosition", "dual_side_position", default=True))

    def balances(self) -> Any:
        return _response_data(self._signed_rest().futures_account_balance_v3())

    def positions(self, symbol: str | None = None) -> Any:
        checked = self._check_symbol(symbol) if symbol else None
        return _response_data(self._signed_rest().position_information_v2(symbol=checked))

    def open_orders(self, symbol: str | None = None) -> Any:
        checked = self._check_symbol(symbol) if symbol else None
        return _response_data(self._signed_rest().current_all_open_orders(symbol=checked))

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
            self._signed_rest().query_order(
                symbol=symbol,
                order_id=order_id,
                orig_client_order_id=client_order_id,
            )
        )

    # ---- Sandbox-only account/order mutations ----

    def ensure_one_way(self) -> dict[str, Any]:
        if self.is_one_way():
            return {"changed": False, "one_way": True}
        data = _response_data(self._signed_rest().change_position_mode(dual_side_position="false"))
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
            self._signed_rest().change_margin_type(symbol=symbol, margin_type="ISOLATED")
        )
        return {"changed": True, "margin_type": "ISOLATED", "response": data}

    def set_leverage(self, symbol: str, leverage: int) -> Any:
        symbol = self._check_symbol(symbol)
        leverage = int(leverage)
        if not 1 <= leverage <= 125:
            raise ValueError("leverage must be 1..125")
        return _response_data(
            self._signed_rest().change_initial_leverage(symbol=symbol, leverage=leverage)
        )

    def modify_isolated_position_margin(
        self,
        symbol: str,
        amount_usdt: float,
        *,
        reduce: bool = False,
    ) -> Any:
        """Add or reduce margin on one isolated one-way position.

        This changes only the isolated margin buffer. It never changes the
        strategy target fraction or order quantity.
        """
        symbol = self._check_symbol(symbol)
        amount = float(amount_usdt)
        if amount <= 0:
            raise ValueError("逐仓保证金调整金额必须大于零")
        if self.margin_type(symbol) != "ISOLATED":
            raise RuntimeError("当前仓位不是逐仓模式，禁止调整逐仓保证金")
        if abs(float(self.position_amount(symbol))) <= 1e-12:
            raise RuntimeError("当前币种没有持仓，不能调整逐仓保证金")
        return _response_data(
            self._signed_rest().modify_isolated_position_margin(
                symbol=symbol,
                amount=amount,
                type=2 if reduce else 1,
                position_side="BOTH",
            )
        )

    def position_metrics(self, symbol: str) -> dict[str, float | str | None]:
        """Return Binance-native isolated position risk fields for the UI."""
        symbol = self._check_symbol(symbol)
        rows = self.positions(symbol)
        position_rows = rows if isinstance(rows, list) else [rows]
        row = next(
            (
                item for item in position_rows
                if isinstance(item, dict)
                and str(_first(item, "symbol", default="")).upper() == symbol
            ),
            {},
        )

        def number(*keys: str) -> float | None:
            value = _first(row, *keys, default=None) if isinstance(row, dict) else None
            try:
                result = float(value)
            except (TypeError, ValueError):
                return None
            return result

        amount = number("positionAmt", "position_amt") or 0.0
        entry_price = number("entryPrice", "entry_price")
        liquidation_price = number("liquidationPrice", "liquidation_price")
        unrealized = number("unRealizedProfit", "unrealizedProfit", "unrealized_profit") or 0.0
        isolated_wallet = number("isolatedWallet", "isolated_wallet")
        isolated_margin = number("isolatedMargin", "isolated_margin")
        margin_type = str(_first(row, "marginType", "margin_type", default="") or "").upper()

        maintenance_margin = None
        try:
            account = _response_data(self._signed_rest().account_information_v3())
            account_positions = _first(account, "positions", default=[]) if isinstance(account, dict) else []
            account_row = next(
                (
                    item for item in (account_positions or [])
                    if isinstance(item, dict)
                    and str(_first(item, "symbol", default="")).upper() == symbol
                ),
                {},
            )
            raw_maint = _first(account_row, "maintMargin", "maint_margin", default=None)
            maintenance_margin = None if raw_maint is None else float(raw_maint)
            if isolated_wallet is None:
                raw_wallet = _first(account_row, "isolatedWallet", "isolated_wallet", default=None)
                isolated_wallet = None if raw_wallet is None else float(raw_wallet)
        except Exception:
            maintenance_margin = None

        wallet = isolated_wallet
        if wallet is None:
            wallet = isolated_margin
        margin_balance = None if wallet is None else wallet + unrealized
        margin_ratio = None
        if maintenance_margin is not None and margin_balance is not None and margin_balance > 0:
            margin_ratio = max(0.0, maintenance_margin / margin_balance * 100.0)

        return {
            "position_amount": amount,
            "margin_type": margin_type or None,
            "isolated_margin_usdt": wallet,
            "entry_price": entry_price if entry_price and entry_price > 0 else None,
            "liquidation_price": liquidation_price if liquidation_price and liquidation_price > 0 else None,
            "maintenance_margin_usdt": maintenance_margin,
            "margin_ratio_percent": margin_ratio,
        }

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
            self._signed_rest().new_order(
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

    def max_allowed_leverage(self, symbol: str) -> int:
        data = self.leverage_brackets(symbol)
        rows = data if isinstance(data, list) else [data]
        values: list[int] = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            for bracket in (_first(row, "brackets", default=[]) or []):
                if not isinstance(bracket, dict):
                    continue
                try:
                    values.append(int(_first(bracket, "initialLeverage", "initial_leverage")))
                except (TypeError, ValueError):
                    pass
        if not values:
            raise RuntimeError(f"{symbol} leverage bracket missing")
        return max(values)

    def available_usdt(self) -> float:
        balances = self.balances()
        rows = balances if isinstance(balances, list) else [balances]
        for row in rows:
            if isinstance(row, dict) and str(_first(row, "asset", default="")).upper() == "USDT":
                return float(_first(row, "availableBalance", "available_balance", default=0))
        raise RuntimeError("USDT available balance missing")

    def position_amount(self, symbol: str) -> float:
        symbol = self._check_symbol(symbol)
        data = self.positions(symbol)
        rows = data if isinstance(data, list) else [data]
        for row in rows:
            if isinstance(row, dict) and str(_first(row, "symbol", default="")).upper() == symbol:
                return float(_first(row, "positionAmt", "position_amt", default=0))
        return 0.0

    def income_history(
        self,
        symbol: str,
        *,
        start_time: int | None = None,
        end_time: int | None = None,
        limit: int = 1000,
    ) -> Any:
        symbol = self._check_symbol(symbol)
        return _response_data(
            self._signed_rest().get_income_history(
                symbol=symbol,
                start_time=start_time,
                end_time=end_time,
                limit=int(limit),
            )
        )

    def submit_market_buy(
        self,
        symbol: str,
        *,
        quantity: Decimal,
        client_order_id: str,
    ) -> Any:
        symbol = self._check_symbol(symbol)
        if quantity <= 0:
            raise ValueError("quantity must be > 0")
        if not client_order_id or len(client_order_id) > 36:
            raise ValueError("client_order_id must be 1..36 chars")
        return _response_data(
            self._signed_rest().new_order(
                symbol=symbol,
                side="BUY",
                type="MARKET",
                position_side="BOTH",
                quantity=float(quantity),
                new_client_order_id=client_order_id,
                new_order_resp_type="RESULT",
            )
        )

    def submit_market_sell_reduce_only(
        self,
        symbol: str,
        *,
        quantity: Decimal,
        client_order_id: str,
    ) -> Any:
        symbol = self._check_symbol(symbol)
        if quantity <= 0:
            raise ValueError("quantity must be > 0")
        if not client_order_id or len(client_order_id) > 36:
            raise ValueError("client_order_id must be 1..36 chars")
        return _response_data(
            self._signed_rest().new_order(
                symbol=symbol,
                side="SELL",
                type="MARKET",
                position_side="BOTH",
                reduce_only="true",
                quantity=float(quantity),
                new_client_order_id=client_order_id,
                new_order_resp_type="RESULT",
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
            self._signed_rest().cancel_order(
                symbol=symbol,
                order_id=order_id,
                orig_client_order_id=client_order_id,
            )
        )
