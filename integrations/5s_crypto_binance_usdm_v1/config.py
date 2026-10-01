from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    app_name: str = "5s-crypto V1 · Binance USDⓈ-M"
    mode: str = "PAPER"
    timeframe: str = "1d"
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

    @classmethod
    def from_env(cls) -> "Settings":
        mode = os.getenv("FIVES_MODE", "PAPER").upper().strip()
        if mode != "PAPER":
            mode = "PAPER"
        db_path = Path(os.getenv("FIVES_DB_PATH", "data/5s_crypto_v1.db"))
        return cls(mode=mode, db_path=db_path)
