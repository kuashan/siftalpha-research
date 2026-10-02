from __future__ import annotations

"""SiftAlpha-ready Web host for the frozen SLTD V7 candidate strategy."""

import argparse
import html
import json
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from data_provider import (
    DEFAULT_TIMEFRAME,
    TIMEFRAMES,
    MarketDataError,
    fetch_bars,
    normalize_symbol,
    normalize_timeframe,
)
from strategy import (
    ACTIVE_RULES,
    HARD_EXIT_ID,
    POSITION_POLICY_ID,
    STRATEGY_SOURCE_COMMIT,
    STRATEGY_VERSION,
    analyze,
)


ROOT = Path(__file__).resolve().parent
TEMPLATE = (ROOT / "templates" / "index.html").read_text(encoding="utf-8")

DEFAULT_SYMBOL = normalize_symbol(os.environ.get("SLTD_SYMBOL", "AAPL"))
DISPLAY_KLINE_LIMIT = 300

_ANALYSIS_CACHE: dict[tuple[str, str], tuple[float, dict]] = {}
_ANALYSIS_LOCK = threading.RLock()
_ANALYSIS_TTL_SECONDS = 5.0


def _payload_for(
    symbol: str,
    timeframe: str,
    force_refresh: bool = False,
) -> dict:
    symbol = normalize_symbol(symbol)
    timeframe = normalize_timeframe(timeframe)
    cache_key = (symbol, timeframe)
    now = time.time()

    with _ANALYSIS_LOCK:
        cached = _ANALYSIS_CACHE.get(cache_key)
        if cached and not force_refresh and now - cached[0] < _ANALYSIS_TTL_SECONDS:
            payload = dict(cached[1])
            payload["market_data"] = dict(payload["market_data"])
            payload["market_data"]["analysis_cache"] = True
            return payload

    completed, forming, market_meta = fetch_bars(
        symbol,
        timeframe,
        force_refresh=force_refresh,
    )
    result = analyze(
        symbol,
        completed,
        display_limit=DISPLAY_KLINE_LIMIT,
        timeframe=timeframe,
    )
    result["forming_bar"] = forming
    result["market_data"] = market_meta
    result["market_data"]["analysis_cache"] = False
    result["decision_contract"] = {
        "selected_timeframe": timeframe,
        "selected_timeframe_label": market_meta["timeframe_label"],
        "confirmed_bar": result["snapshot"]["latest_date"],
        "forming_bar_present": forming is not None,
        "rule": "只用已结束的所选周期 K 线确认信号；当前未结束 K 线不参与正式决策",
        "execution": "确认后在下一根所选周期 K 线开盘执行",
    }

    with _ANALYSIS_LOCK:
        _ANALYSIS_CACHE[cache_key] = (now, result)
    return result


def _timeframe_options() -> str:
    out = []
    for value, cfg in TIMEFRAMES.items():
        selected = " selected" if value == DEFAULT_TIMEFRAME else ""
        status = "已验证周期" if bool(cfg["validated"]) else "实验周期"
        out.append(
            f'<option value="{html.escape(value)}"{selected}>'
            f'{html.escape(str(cfg["label"]))} · {status}</option>'
        )
    return "\n".join(out)


def render_index() -> str:
    return (
        TEMPLATE.replace("__DEFAULT_SYMBOL__", html.escape(DEFAULT_SYMBOL))
        .replace("__DEFAULT_TIMEFRAME__", html.escape(DEFAULT_TIMEFRAME))
        .replace("__TIMEFRAME_OPTIONS__", _timeframe_options())
        .replace("__STRATEGY_VERSION__", html.escape(STRATEGY_VERSION))
        .replace("__SOURCE_COMMIT_SHORT__", html.escape(STRATEGY_SOURCE_COMMIT[:8]))
        .replace("__POSITION_POLICY_ID__", html.escape(POSITION_POLICY_ID))
        .replace("__HARD_EXIT_ID__", html.escape(HARD_EXIT_ID))
    )


class Handler(BaseHTTPRequestHandler):
    server_version = "SiftAlphaSLTDV7/2.0"

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: int, payload: dict) -> None:
        self._send(
            status,
            json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8"),
            "application/json; charset=utf-8",
        )

    def do_GET(self) -> None:
        parsed = urlparse(self.path)

        if parsed.path == "/":
            self._send(200, render_index().encode("utf-8"), "text/html; charset=utf-8")
            return

        if parsed.path == "/api/health":
            self._json(
                200,
                {
                    "ok": True,
                    "app": "SLTD V7 for SiftAlpha",
                    "strategy": STRATEGY_VERSION,
                    "source_commit": STRATEGY_SOURCE_COMMIT,
                    "active_rules": sum(len(v) for v in ACTIVE_RULES.values()),
                    "display_kline_limit": DISPLAY_KLINE_LIMIT,
                    "default_timeframe": DEFAULT_TIMEFRAME,
                    "timeframes": TIMEFRAMES,
                    "bar_close_contract": True,
                },
            )
            return

        if parsed.path == "/api/rules":
            self._json(
                200,
                {
                    "strategy": STRATEGY_VERSION,
                    "active_rules": ACTIVE_RULES,
                    "position_policy": POSITION_POLICY_ID,
                    "hard_exit": HARD_EXIT_ID,
                    "bar_close_contract": (
                        "selected timeframe bar close -> confirm -> next selected bar open"
                    ),
                },
            )
            return

        if parsed.path == "/api/analyze":
            query = parse_qs(parsed.query)
            raw_symbol = str(query.get("symbol", [DEFAULT_SYMBOL])[0])
            raw_timeframe = str(query.get("timeframe", [DEFAULT_TIMEFRAME])[0])
            force = str(query.get("refresh", ["0"])[0]).lower() in {"1", "true", "yes"}
            try:
                symbol = normalize_symbol(raw_symbol)
                timeframe = normalize_timeframe(raw_timeframe)
                payload = _payload_for(
                    symbol,
                    timeframe,
                    force_refresh=force,
                )
                self._json(200, payload)
            except (ValueError, MarketDataError) as exc:
                self._json(400, {"error": str(exc)})
            except Exception as exc:
                self._json(
                    500,
                    {
                        "error": "SLTD 计算失败",
                        "detail": f"{type(exc).__name__}: {exc}",
                    },
                )
            return

        self._send(404, "页面不存在".encode("utf-8"), "text/plain; charset=utf-8")

    def log_message(self, fmt: str, *args) -> None:
        print(f"[sltd-web] {self.address_string()} {fmt % args}", flush=True)


def create_server(host: str = "127.0.0.1", port: int = 0) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), Handler)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="SLTD V7 SiftAlpha Web")
    parser.add_argument("--host", default=os.environ.get("SLTD_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("SLTD_PORT", "0")))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    server = create_server(args.host, args.port)
    actual_port = int(server.server_address[1])
    url = f"http://127.0.0.1:{actual_port}"

    print("SLTD V7 · SiftAlpha Web", flush=True)
    print(f"strategy={STRATEGY_VERSION}", flush=True)
    print(f"active_rules={sum(len(v) for v in ACTIVE_RULES.values())}", flush=True)
    print("decision_contract=SELECTED_BAR_CLOSE_TO_NEXT_SELECTED_BAR_OPEN", flush=True)
    print(f"default_symbol={DEFAULT_SYMBOL}", flush=True)
    print(f"default_timeframe={DEFAULT_TIMEFRAME}", flush=True)
    print(f"SIFTALPHA_WEB_URL={url}", flush=True)
    print(f"网页服务已启动：{url}", flush=True)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
