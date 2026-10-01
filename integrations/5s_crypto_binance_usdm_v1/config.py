from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    app_name: str = "5s-crypto V1 · Binance USDⓈ-M"
    mode: str = "PAPER"
    default_timeframe: str = "1d"
    allowed_timeframes: tuple[str, ...] = ("3m", "5m", "15m", "1h", "2h", "4h", "6h", "12h", "1d")
    validated_timeframes: tuple[str, ...] = ("1d",)
    symbols: tuple[str, ...] = ("BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT")
    margin_type: str = "ISOLATED"
    position_mode: str = "ONE_WAY"
    direction: str = "LONG_ONLY"
    min_leverage: int = 1
    max_leverage: int = 125
    default_leverage: int = 1
    default_capital_budget_usdt: float = 1000.0
    db_path: Path = Path("data/5s_crypto_v1.db")
    binance_public_base_url: str = "https://fapi.binance.com"
    request_timeout_seconds: float = 3.0
    testnet_api_key: str = ""
    testnet_api_secret: str = ""

    @property
    def testnet_credentials_present(self) -> bool:
        return bool(self.testnet_api_key and self.testnet_api_secret)

    @classmethod
    def from_env(cls) -> "Settings":
        requested_mode = os.getenv("FIVES_MODE", "PAPER").upper().strip()
        mode = requested_mode if requested_mode in {"PAPER", "DEMO", "TESTNET"} else "PAPER"
        db_path = Path(os.getenv("FIVES_DB_PATH", "data/5s_crypto_v1.db"))
        return cls(
            mode=mode,
            db_path=db_path,
            testnet_api_key=(
                os.getenv("BINANCE_DEMO_API_KEY", "").strip()
                or os.getenv("BINANCE_TESTNET_API_KEY", "").strip()
            ),
            testnet_api_secret=(
                os.getenv("BINANCE_DEMO_API_SECRET", "").strip()
                or os.getenv("BINANCE_TESTNET_API_SECRET", "").strip()
            ),
        )
