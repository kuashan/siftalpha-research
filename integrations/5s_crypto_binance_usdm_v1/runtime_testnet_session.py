from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from threading import RLock
from typing import Any, Callable

from exchange.binance_usdm_testnet import BinanceUsdMTestnetAdapter


def _first(mapping: dict[str, Any], *keys: str, default: Any = None) -> Any:
    for key in keys:
        if key in mapping:
            return mapping[key]
    return default


def _number(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _mask_key(api_key: str) -> str:
    api_key = api_key.strip()
    if len(api_key) <= 8:
        return "••••••••"
    return f"{api_key[:4]}••••{api_key[-4:]}"


@dataclass(frozen=True)
class TestnetAccountSnapshot:
    environment: str
    usdt_balance: float
    usdt_available_balance: float
    nonzero_position_count: int
    one_way: bool
    connected_at: str


class TestnetSession:
    """In-memory Demo Trading credentials + last verified account snapshot.

    Credentials are deliberately never written to SQLite or returned to the UI.
    A failed connection test does not retain the submitted secret.
    """

    def __init__(
        self,
        *,
        allowed_symbols: tuple[str, ...],
        allowed_timeframes: tuple[str, ...],
        initial_api_key: str = "",
        initial_api_secret: str = "",
        adapter_factory: Callable[..., BinanceUsdMTestnetAdapter] = BinanceUsdMTestnetAdapter,
    ):
        self.allowed_symbols = allowed_symbols
        self.allowed_timeframes = allowed_timeframes
        self._adapter_factory = adapter_factory
        self._lock = RLock()
        self._api_key = initial_api_key.strip()
        self._api_secret = initial_api_secret.strip()
        self._snapshot: TestnetAccountSnapshot | None = None
        self._last_error: str | None = None
        self._recovery_ready = False
        self._recovery_summary: dict[str, Any] | None = None

    def _adapter(self, api_key: str, api_secret: str) -> BinanceUsdMTestnetAdapter:
        return self._adapter_factory(
            mode="DEMO",
            api_key=api_key,
            api_secret=api_secret,
            allowed_symbols=self.allowed_symbols,
            allowed_timeframes=self.allowed_timeframes,
        )

    def connect_and_test(self, api_key: str, api_secret: str) -> TestnetAccountSnapshot:
        api_key = api_key.strip()
        api_secret = api_secret.strip()
        if not api_key or not api_secret:
            raise ValueError("API Key 和 API Secret 都不能为空")

        adapter = self._adapter(api_key, api_secret)
        try:
            balances = adapter.balances()
            positions = adapter.positions()
            one_way = adapter.is_one_way()

            rows = balances if isinstance(balances, list) else [balances]
            usdt = next(
                (
                    row for row in rows
                    if isinstance(row, dict)
                    and str(_first(row, "asset", default="")).upper() == "USDT"
                ),
                None,
            )
            if not isinstance(usdt, dict):
                raise RuntimeError("模拟交易账户中没有找到 USDT 余额")

            position_rows = positions if isinstance(positions, list) else [positions]
            nonzero_positions = 0
            for row in position_rows:
                if not isinstance(row, dict):
                    continue
                symbol = str(_first(row, "symbol", default="")).upper()
                if symbol not in self.allowed_symbols:
                    continue
                amount = _number(_first(row, "positionAmt", "position_amt", default=0))
                if abs(amount) > 0:
                    nonzero_positions += 1

            snapshot = TestnetAccountSnapshot(
                environment="DEMO",
                usdt_balance=_number(_first(usdt, "balance", default=0)),
                usdt_available_balance=_number(
                    _first(usdt, "availableBalance", "available_balance", default=0)
                ),
                nonzero_position_count=nonzero_positions,
                one_way=bool(one_way),
                connected_at=datetime.now(timezone.utc).isoformat(),
            )
        except Exception as exc:
            with self._lock:
                self._api_key = ""
                self._api_secret = ""
                self._snapshot = None
                self._last_error = str(exc)
            raise

        with self._lock:
            self._api_key = api_key
            self._api_secret = api_secret
            self._snapshot = snapshot
            self._last_error = None
            self._recovery_ready = False
            self._recovery_summary = None
        return snapshot

    def test_existing_credentials(self) -> TestnetAccountSnapshot:
        with self._lock:
            api_key, api_secret = self._api_key, self._api_secret
        if not api_key or not api_secret:
            raise ValueError("当前进程没有模拟交易凭据")
        return self.connect_and_test(api_key, api_secret)

    def disconnect(self) -> None:
        with self._lock:
            self._api_key = ""
            self._api_secret = ""
            self._snapshot = None
            self._last_error = None
            self._recovery_ready = False
            self._recovery_summary = None

    def credentials(self) -> tuple[str, str]:
        with self._lock:
            return self._api_key, self._api_secret

    def adapter(self) -> BinanceUsdMTestnetAdapter:
        with self._lock:
            api_key, api_secret = self._api_key, self._api_secret
        if not api_key or not api_secret:
            raise ValueError("当前进程没有模拟交易凭据")
        return self._adapter(api_key, api_secret)

    def set_recovery_status(self, summary: dict[str, Any], ready: bool) -> None:
        with self._lock:
            self._recovery_summary = summary
            self._recovery_ready = bool(ready)

    def recovery_ready(self) -> bool:
        with self._lock:
            return bool(self._snapshot is not None and self._recovery_ready)

    def public_status(self) -> dict[str, Any]:
        with self._lock:
            snapshot = self._snapshot
            return {
                "environment": "DEMO",
                "credentials_present": bool(self._api_key and self._api_secret),
                "connected": snapshot is not None,
                "masked_api_key": _mask_key(self._api_key) if self._api_key else None,
                "last_error": self._last_error,
                "recovery_ready": self._recovery_ready,
                "recovery": self._recovery_summary,
                "account": None if snapshot is None else {
                    "usdt_balance": snapshot.usdt_balance,
                    "usdt_available_balance": snapshot.usdt_available_balance,
                    "nonzero_position_count": snapshot.nonzero_position_count,
                    "one_way": snapshot.one_way,
                    "connected_at": snapshot.connected_at,
                },
            }
