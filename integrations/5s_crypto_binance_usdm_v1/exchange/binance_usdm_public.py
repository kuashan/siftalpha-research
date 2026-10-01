from __future__ import annotations

from dataclasses import dataclass
import json
import time
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class ProbeResult:
    ok: bool
    latency_ms: int | None
    server_time_ms: int | None
    error: str | None = None


class BinanceUsdMPublicProbe:
    """Unauthenticated USDⓈ-M connectivity probe used by M1 only."""

    def __init__(self, base_url: str, timeout_seconds: float = 3.0):
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds

    def _get_json(self, path: str) -> dict:
        req = Request(
            f"{self.base_url}{path}",
            headers={"User-Agent": "5s-crypto-v1-m1/1.0"},
        )
        with urlopen(req, timeout=self.timeout_seconds) as response:
            return json.loads(response.read().decode("utf-8"))

    def probe(self) -> ProbeResult:
        started = time.perf_counter()
        try:
            self._get_json("/fapi/v1/ping")
            data = self._get_json("/fapi/v1/time")
            return ProbeResult(
                ok=True,
                latency_ms=int((time.perf_counter() - started) * 1000),
                server_time_ms=int(data["serverTime"]),
            )
        except Exception as exc:
            return ProbeResult(ok=False, latency_ms=None, server_time_ms=None, error=str(exc))
