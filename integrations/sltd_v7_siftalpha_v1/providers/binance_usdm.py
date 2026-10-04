from __future__ import annotations

"""Binance USDⓈ-M public market-data provider for the V7 multi-strategy host.

Public candles intentionally do not require Demo credentials. Authenticated
account/order access stays in binance_demo_exchange.py.
"""

import json
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen

try:
    from shared_market_data import CRYPTO_24_7
except ImportError:
    import sys
    from pathlib import Path
    root = Path(__file__).resolve().parents[2]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    from shared_market_data import CRYPTO_24_7


BINANCE_CRYPTO_SYMBOLS = ("BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT")
BINANCE_TIMEFRAMES = ("5m", "15m", "30m", "1h", "4h", "1d", "5d")


class BinanceUsdMProvider:
    provider_id = "BINANCE_USDM_PUBLIC_MS"
    provider_label_zh = "币安 USDⓈ-M"
    profile = CRYPTO_24_7

    def __init__(self, base_url: str = "https://fapi.binance.com", timeout: float = 8.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = float(timeout)

    def _get(self, path: str, params: dict | None = None):
        query = "?" + urlencode(params or {}) if params else ""
        req = Request(
            self.base_url + path + query,
            headers={"User-Agent": "SiftAlpha-SLTD-V7/3.0", "Accept": "application/json"},
        )
        with urlopen(req, timeout=self.timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def server_time_ms(self) -> int:
        return int(self._get("/fapi/v1/time")["serverTime"])

    @staticmethod
    def _normalize_row(row: list, *, complete: bool) -> dict:
        return {
            "date": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(int(row[0]) / 1000)),
            "open_time": int(row[0]),
            "close_time": int(row[6]),
            "open": float(row[1]),
            "high": float(row[2]),
            "low": float(row[3]),
            "close": float(row[4]),
            "volume": float(row[5]),
            "complete": bool(complete),
        }

    @staticmethod
    def _aggregate_5d(rows: list[dict]) -> list[dict]:
        out: list[dict] = []
        for start in range(0, len(rows), 5):
            chunk = rows[start:start + 5]
            if len(chunk) < 5:
                break
            out.append({
                "date": chunk[0]["date"],
                "open_time": int(chunk[0]["open_time"]),
                "close_time": int(chunk[-1]["close_time"]),
                "open": float(chunk[0]["open"]),
                "high": max(float(x["high"]) for x in chunk),
                "low": min(float(x["low"]) for x in chunk),
                "close": float(chunk[-1]["close"]),
                "volume": sum(float(x["volume"]) for x in chunk),
                "complete": all(bool(x["complete"]) for x in chunk),
            })
        return out

    def fetch(self, symbol: str, timeframe: str, **kwargs):
        symbol = str(symbol).upper().strip()
        timeframe = str(timeframe).lower().strip()
        if symbol not in BINANCE_CRYPTO_SYMBOLS:
            raise ValueError(f"unsupported Binance symbol: {symbol}")
        if timeframe not in BINANCE_TIMEFRAMES:
            raise ValueError(f"unsupported Binance timeframe: {timeframe}")

        raw_tf = "1d" if timeframe == "5d" else timeframe
        limit = 1500 if timeframe != "5d" else 1500
        server_ms = self.server_time_ms()
        raw = self._get(
            "/fapi/v1/klines",
            {"symbol": symbol, "interval": raw_tf, "limit": int(limit)},
        )
        rows = [
            self._normalize_row(r, complete=int(r[6]) < server_ms)
            for r in raw
        ]
        if timeframe == "5d":
            rows = self._aggregate_5d(rows)

        completed = [{k: v for k, v in r.items() if k != "complete"} for r in rows if r["complete"]]
        forming_rows = [r for r in rows if not r["complete"]]
        forming = None
        if forming_rows:
            forming = {k: v for k, v in forming_rows[-1].items() if k != "complete"}

        return {
            "completed": completed,
            "forming": forming,
            "meta": {
                "exchange_name": "Binance USDⓈ-M",
                "exchange_timezone": "UTC",
                "currency": "USDT",
                "continuous": True,
                "server_time_ms": server_ms,
                "has_forming_bar": forming is not None,
            },
        }

    def stream_url(self, symbol: str) -> str:
        return f"wss://fstream.binance.com/ws/{str(symbol).lower()}@markPrice@1s"
