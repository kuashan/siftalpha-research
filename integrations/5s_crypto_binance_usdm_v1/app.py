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
store.seed(settings.symbols, settings.default_leverage, settings.default_capital_budget_usdt, settings.default_timeframe)
probe = BinanceUsdMPublicProbe(settings.binance_public_base_url, settings.request_timeout_seconds)
TEMPLATE = (Path(__file__).parent / "templates" / "index.html").read_text(encoding="utf-8")


def _timeframe_options(selected_timeframe: str) -> str:
    options = []
    for interval in settings.allowed_timeframes:
        selected = " selected" if interval == selected_timeframe else ""
        label = f"{interval} · V1 已验证" if interval in settings.validated_timeframes else f"{interval} · 实验"
        options.append(f'<option value="{html.escape(interval)}"{selected}>{html.escape(label)}</option>')
    return "\n".join(options)


def _pnl_class(value: float) -> str:
    return "positive" if value > 0 else "negative" if value < 0 else "neutral"


def render_index() -> str:
    configs = store.get_symbol_configs()
    runtime = store.get_runtime_states()
    pnl = store.get_pnl()
    summary = store.pnl_summary()
    cards = []

    for symbol in settings.symbols:
        cfg, rt, p = configs[symbol], runtime[symbol], pnl[symbol]
        budget = float(cfg["capital_budget_usdt"])
        leverage = int(cfg["leverage"])
        timeframe = str(cfg["timeframe"])
        enabled = bool(cfg["enabled"])
        initial = preview_exposure(symbol, budget, 0.60, leverage)
        full = preview_exposure(symbol, budget, 1.00, leverage)
        validation = "V1 已验证" if timeframe in settings.validated_timeframes else "Experimental"
        status, status_class = ("已启动", "running") if enabled else ("未启动", "stopped")
        action, action_label, action_class = ("stop", "停止", "danger") if enabled else ("start", "启动", "primary")
        current_fraction = float(rt.get("current_fraction") or 0.0)
        last_signal = str(rt.get("last_signal") or "—")

        cards.append(f"""
        <article class="coin-card">
          <div class="coin-head">
            <div><h2>{html.escape(symbol)}</h2><span class="status {status_class}">{status}</span></div>
            <strong class="pnl {_pnl_class(p['total_pnl'])}">{p['total_pnl']:+.2f} USDT</strong>
          </div>
          <form method="post" action="/symbol-settings">
            <input type="hidden" name="symbol" value="{html.escape(symbol)}">
            <div class="fields">
              <label>策略资金（USDT）<input name="capital_budget_usdt" type="number" min="1" step="0.01" value="{budget:.2f}" required></label>
              <label>杠杆<input name="leverage" type="number" min="1" max="125" step="1" value="{leverage}" required></label>
              <label>K 线周期<select name="timeframe" required>{_timeframe_options(timeframe)}</select></label>
            </div>
            <div class="mini-grid">
              <div><small>周期验证</small><b>{validation}</b></div>
              <div><small>当前仓位</small><b>{current_fraction*100:.0f}%</b></div>
              <div><small>60% 名义价值</small><b>{initial.target_notional_usdt:.2f}</b></div>
              <div><small>100% 名义价值</small><b>{full.target_notional_usdt:.2f}</b></div>
              <div><small>最新信号</small><b>{html.escape(last_signal)}</b></div>
              <div><small>浮动盈亏</small><b>{p['unrealized_pnl']:+.2f}</b></div>
              <div><small>已实现盈亏</small><b>{p['realized_pnl']:+.2f}</b></div>
              <div><small>资金费/手续费</small><b>{p['funding_fee']-p['trading_fee']:+.2f}</b></div>
            </div>
            <button class="secondary" type="submit">保存参数</button>
          </form>
          <form method="post" action="/symbol-action" class="action-form">
            <input type="hidden" name="symbol" value="{html.escape(symbol)}">
            <input type="hidden" name="action" value="{action}">
            <button class="{action_class}" type="submit">{action_label}</button>
          </form>
        </article>
        """)

    active = [cfg for cfg in configs.values() if bool(cfg["enabled"])]
    configured_budget = sum(float(cfg["capital_budget_usdt"]) for cfg in configs.values())
    active_budget = sum(float(cfg["capital_budget_usdt"]) for cfg in active)

    return (
        TEMPLATE
        .replace("__MODE__", html.escape(settings.mode))
        .replace("__TESTNET_CREDENTIAL_STATUS__", "已配置（密钥不会显示）" if settings.testnet_credentials_present else "未配置")
        .replace("__ACTIVE_COUNT__", str(len(active)))
        .replace("__CONFIGURED_BUDGET__", f"{configured_budget:.2f}")
        .replace("__ACTIVE_BUDGET__", f"{active_budget:.2f}")
        .replace("__TOTAL_PNL__", f"{summary['total_pnl']:+.2f}")
        .replace("__TOTAL_PNL_CLASS__", _pnl_class(summary["total_pnl"]))
        .replace("__REALIZED_PNL__", f"{summary['realized_pnl']:+.2f}")
        .replace("__UNREALIZED_PNL__", f"{summary['unrealized_pnl']:+.2f}")
        .replace("__COIN_CARDS__", "\n".join(cards))
    )


class Handler(BaseHTTPRequestHandler):
    server_version = "5sCryptoM2_1/1.0"

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _redirect_home(self) -> None:
        self.send_response(303)
        self.send_header("Location", "/")
        self.end_headers()

    def _read_form(self) -> dict[str, list[str]]:
        length = int(self.headers.get("Content-Length", "0"))
        return parse_qs(self.rfile.read(length).decode("utf-8"), keep_blank_values=True)

    def _symbol_from_form(self, form: dict[str, list[str]]) -> str:
        symbol = form.get("symbol", [""])[0].upper().strip()
        if symbol not in settings.symbols:
            raise ValueError("unsupported symbol")
        return symbol

    def do_GET(self) -> None:
        if self.path == "/":
            self._send(200, render_index().encode("utf-8"), "text/html; charset=utf-8")
            return
        if self.path == "/api/status":
            result = probe.probe()
            payload = {
                "app": settings.app_name,
                "mode": settings.mode,
                "market": "BINANCE_USDS_M_PERPETUAL",
                "margin_type": settings.margin_type,
                "position_mode": settings.position_mode,
                "direction": settings.direction,
                "live_enabled": False,
                "testnet_credentials_present": settings.testnet_credentials_present,
                "symbols": store.get_symbol_configs(),
                "runtime": store.get_runtime_states(),
                "pnl": store.get_pnl(),
                "pnl_summary": store.pnl_summary(),
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
        try:
            form = self._read_form()
            if self.path == "/symbol-settings":
                symbol = self._symbol_from_form(form)
                budget = float(form.get("capital_budget_usdt", ["0"])[0])
                leverage = int(form.get("leverage", ["0"])[0])
                timeframe = form.get("timeframe", [""])[0]
                if budget <= 0 or budget > 100_000_000:
                    raise ValueError("invalid capital budget")
                if not settings.min_leverage <= leverage <= settings.max_leverage:
                    raise ValueError("invalid leverage")
                if timeframe not in settings.allowed_timeframes:
                    raise ValueError("unsupported timeframe")
                store.set_symbol_config(symbol, capital_budget_usdt=budget, leverage=leverage, timeframe=timeframe)
                self._redirect_home()
                return

            if self.path == "/symbol-action":
                symbol = self._symbol_from_form(form)
                action = form.get("action", [""])[0].lower().strip()
                if action not in {"start", "stop"}:
                    raise ValueError("unsupported action")
                store.set_symbol_enabled(symbol, action == "start")
                self._redirect_home()
                return

            self._send(404, b"Not found", "text/plain; charset=utf-8")
        except Exception as exc:
            self._send(400, str(exc).encode("utf-8"), "text/plain; charset=utf-8")

    def log_message(self, fmt: str, *args) -> None:
        print(f"[web] {self.address_string()} {fmt % args}")


def main(host: str = "0.0.0.0", port: int = 8080) -> None:
    enabled = [s for s, cfg in store.get_symbol_configs().items() if cfg["enabled"]]
    print(f"{settings.app_name}")
    print(f"mode={settings.mode} enabled_symbols={','.join(enabled) or 'none'} live_enabled=false")
    print(f"web=http://127.0.0.1:{port}")
    ThreadingHTTPServer((host, port), Handler).serve_forever()


if __name__ == "__main__":
    main()
