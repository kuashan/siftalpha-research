from __future__ import annotations

import html
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from urllib.parse import parse_qs

from config import Settings
from engine.paper import preview_exposure
from exchange.binance_usdm_public import BinanceUsdMPublicProbe
from storage import StateStore


settings = Settings.from_env()
store = StateStore(settings.db_path)
store.seed(settings.symbols, settings.default_leverage, settings.default_capital_budget_usdt)
probe = BinanceUsdMPublicProbe(settings.binance_public_base_url, settings.request_timeout_seconds)
TEMPLATE = (Path(__file__).parent / "templates" / "index.html").read_text(encoding="utf-8")


def render_index() -> str:
    leverages = store.get_leverages()
    budget = store.get_budget()
    rows = []
    for symbol in settings.symbols:
        lev = leverages.get(symbol, settings.default_leverage)
        initial = preview_exposure(symbol, budget, 0.60, lev)
        full = preview_exposure(symbol, budget, 1.00, lev)
        rows.append(
            "<tr>"
            f"<td><strong>{html.escape(symbol)}</strong></td>"
            f"<td><input name=\"leverage_{html.escape(symbol)}\" type=\"number\" min=\"1\" max=\"125\" step=\"1\" value=\"{lev}\" required></td>"
            f"<td>{initial.target_notional_usdt:.2f} USDT</td>"
            f"<td>{full.target_notional_usdt:.2f} USDT</td>"
            "</tr>"
        )
    return TEMPLATE.replace("__BUDGET__", f"{budget:.2f}").replace("__ROWS__", "\n".join(rows))


class Handler(BaseHTTPRequestHandler):
    server_version = "5sCryptoM1/1.0"

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path == "/":
            self._send(200, render_index().encode("utf-8"), "text/html; charset=utf-8")
            return
        if self.path == "/api/status":
            result = probe.probe()
            payload = {
                "app": settings.app_name,
                "mode": settings.mode,
                "timeframe": settings.timeframe,
                "market": "BINANCE_USDS_M_PERPETUAL",
                "margin_type": settings.margin_type,
                "position_mode": settings.position_mode,
                "direction": settings.direction,
                "live_enabled": False,
                "binance_public": {
                    "ok": result.ok,
                    "latency_ms": result.latency_ms,
                    "server_time_ms": result.server_time_ms,
                    "error": result.error,
                },
            }
            self._send(200, json.dumps(payload, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")
            return
        self._send(404, b"Not found", "text/plain; charset=utf-8")

    def do_POST(self) -> None:
        if self.path != "/settings":
            self._send(404, b"Not found", "text/plain; charset=utf-8")
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            form = parse_qs(self.rfile.read(length).decode("utf-8"), keep_blank_values=True)
            budget = float(form.get("capital_budget_usdt", [str(store.get_budget())])[0])
            if budget <= 0 or budget > 100_000_000:
                raise ValueError("invalid capital budget")

            leverage_updates: dict[str, int] = {}
            for symbol in settings.symbols:
                raw = form.get(f"leverage_{symbol}")
                if raw is None:
                    continue
                leverage = int(raw[0])
                if not settings.min_leverage <= leverage <= settings.max_leverage:
                    raise ValueError(f"invalid leverage for {symbol}")
                leverage_updates[symbol] = leverage

            store.set_budget(budget)
            for symbol, leverage in leverage_updates.items():
                store.set_leverage(symbol, leverage)

            self.send_response(303)
            self.send_header("Location", "/")
            self.end_headers()
        except Exception as exc:
            self._send(400, str(exc).encode("utf-8"), "text/plain; charset=utf-8")

    def log_message(self, fmt: str, *args) -> None:
        print(f"[web] {self.address_string()} {fmt % args}")


def main(host: str = "0.0.0.0", port: int = 8080) -> None:
    print(f"{settings.app_name}")
    print(f"mode={settings.mode} timeframe={settings.timeframe} live_enabled=false")
    print(f"web=http://127.0.0.1:{port}")
    ThreadingHTTPServer((host, port), Handler).serve_forever()


if __name__ == "__main__":
    main()
