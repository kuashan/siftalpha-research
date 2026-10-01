from __future__ import annotations

import html
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse

from config import Settings
from engine.paper import preview_exposure
from engine.scheduler import StrategyScheduler
from exchange.binance_usdm_public import BinanceUsdMPublicProbe
from runtime_testnet_session import TestnetSession
from storage import StateStore


settings = Settings.from_env()
store = StateStore(settings.db_path)
store.seed(
    settings.symbols,
    settings.default_leverage,
    settings.default_capital_budget_usdt,
    settings.default_timeframe,
)
probe = BinanceUsdMPublicProbe(settings.binance_public_base_url, settings.request_timeout_seconds)
testnet_session = TestnetSession(
    allowed_symbols=settings.symbols,
    allowed_timeframes=settings.allowed_timeframes,
    initial_api_key=settings.testnet_api_key,
    initial_api_secret=settings.testnet_api_secret,
)
strategy_scheduler = StrategyScheduler(
    store=store,
    session=testnet_session,
    symbols=settings.symbols,
    allowed_timeframes=settings.allowed_timeframes,
)
TEMPLATE = (Path(__file__).parent / "templates" / "index.html").read_text(encoding="utf-8")


_TIMEFRAME_LABELS = {
    "15m": "15 分钟",
    "1h": "1 小时",
    "2h": "2 小时",
    "4h": "4 小时",
    "6h": "6 小时",
    "12h": "12 小时",
    "1d": "1 天",
}

_RUN_STATE_LABELS = {
    "ARMED": "已启动",
    "WAITING_DEMO": "等待模拟账户",
    "WAITING_HISTORY": "历史数据不足",
    "MONITORING": "监测中",
    "SIGNAL_READY": "发现信号",
    "ERROR": "检测异常",
    "STOPPED": "未启动",
}

_SIGNAL_LABELS = {
    "BUY_A": "买入信号一",
    "BUY_B": "买入信号二",
    "BUY_C": "补仓信号三",
    "SELL_A": "卖出信号一",
    "SELL_B": "卖出信号二",
    "SELL_C": "卖出信号三",
    "MULTI_SELL": "多重卖出",
    "HOLD": "观望",
}


def _timeframe_options(selected_timeframe: str) -> str:
    options = []
    for interval in settings.allowed_timeframes:
        selected = " selected" if interval == selected_timeframe else ""
        suffix = " · 已验证基线" if interval in settings.validated_timeframes else " · 实验周期"
        label = _TIMEFRAME_LABELS.get(interval, interval) + suffix
        options.append(
            f'<option value="{html.escape(interval)}"{selected}>{html.escape(label)}</option>'
        )
    return "\n".join(options)


def _pnl_class(value: float) -> str:
    return "positive" if value > 0 else "negative" if value < 0 else "neutral"


def _signal_label(value: object) -> str:
    raw = str(value or "").strip().upper()
    return _SIGNAL_LABELS.get(raw, "等待信号")


def _short_symbol(symbol: str) -> str:
    return symbol[:-4] if symbol.endswith("USDT") else symbol


def render_index(selected_symbol: str | None = None) -> str:
    configs = store.get_symbol_configs()
    runtime = store.get_runtime_states()
    pnl = store.get_pnl()
    summary = store.pnl_summary()
    testnet = testnet_session.public_status()
    account = testnet.get("account") or {}

    active_symbols = [s for s in settings.symbols if bool(configs[s]["enabled"])]
    initial_symbol = (
        selected_symbol
        if selected_symbol in settings.symbols
        else (active_symbols[0] if active_symbols else settings.symbols[0])
    )

    tabs: list[str] = []
    panels: list[str] = []

    for symbol in settings.symbols:
        cfg, rt, p = configs[symbol], runtime[symbol], pnl[symbol]
        budget = float(cfg["capital_budget_usdt"])
        leverage = int(cfg["leverage"])
        timeframe = str(cfg["timeframe"])
        enabled = bool(cfg["enabled"])
        initial = preview_exposure(symbol, budget, 0.60, leverage)
        full = preview_exposure(symbol, budget, 1.00, leverage)
        validation = "已验证基线" if timeframe in settings.validated_timeframes else "实验周期"
        run_state = str(rt.get("run_state") or ("ARMED" if enabled else "STOPPED"))
        status_label = _RUN_STATE_LABELS.get(run_state, "运行中" if enabled else "未启动")
        status_class = "running" if enabled and run_state != "ERROR" else "stopped"
        action = "stop" if enabled else "start"
        action_label = "停止" if enabled else "启动"
        action_class = "danger" if enabled else "primary"
        current_fraction = float(rt.get("current_fraction") or 0.0)
        last_signal = _signal_label(rt.get("last_signal"))
        base = _short_symbol(symbol)
        selected = symbol == initial_symbol

        tabs.append(
            f"""
            <button
              class="coin-tab{' active' if selected else ''}"
              type="button"
              data-symbol="{html.escape(symbol)}"
              aria-selected="{'true' if selected else 'false'}"
            >
              <span class="tab-top">
                <span class="run-dot {'on' if enabled else ''}"></span>
                <strong>{html.escape(base)}</strong>
              </span>
              <small class="{_pnl_class(p['total_pnl'])}">{p['total_pnl']:+.2f}</small>
            </button>
            """
        )

        panels.append(
            f"""
            <article class="coin-panel{' active' if selected else ''}" data-panel="{html.escape(symbol)}">
              <div class="coin-hero">
                <div>
                  <div class="eyebrow">当前币种</div>
                  <div class="coin-title-row">
                    <h2>{html.escape(base)} <span>/ USDT</span></h2>
                    <span class="status-pill {status_class}">{status_label}</span>
                  </div>
                </div>
                <div class="hero-pnl">
                  <small>该币总盈亏</small>
                  <strong class="{_pnl_class(p['total_pnl'])}">{p['total_pnl']:+.2f}</strong>
                  <span>USDT</span>
                </div>
              </div>

              <div class="snapshot-grid">
                <div class="snapshot"><small>当前仓位</small><b>{current_fraction * 100:.0f}%</b></div>
                <div class="snapshot"><small>最新信号</small><b>{html.escape(last_signal)}</b></div>
                <div class="snapshot"><small>浮动盈亏</small><b class="{_pnl_class(p['unrealized_pnl'])}">{p['unrealized_pnl']:+.2f}</b></div>
                <div class="snapshot"><small>已实现盈亏</small><b class="{_pnl_class(p['realized_pnl'])}">{p['realized_pnl']:+.2f}</b></div>
              </div>

              <div class="panel-body">
                <section class="settings-block">
                  <div class="section-title">
                    <div>
                      <small>交易设置</small>
                      <strong>{validation}</strong>
                    </div>
                  </div>
                  <form method="post" action="/symbol-settings">
                    <input type="hidden" name="symbol" value="{html.escape(symbol)}">
                    <div class="field-grid">
                      <label class="budget-field">策略资金
                        <div class="input-with-unit">
                          <input name="capital_budget_usdt" type="number" min="1" step="0.01" value="{budget:.2f}" required>
                          <span>USDT</span>
                        </div>
                      </label>
                      <label>杠杆倍数
                        <div class="input-with-unit">
                          <input name="leverage" type="number" min="1" max="125" step="1" value="{leverage}" required>
                          <span>倍</span>
                        </div>
                      </label>
                      <label>K 线周期
                        <select name="timeframe" required>{_timeframe_options(timeframe)}</select>
                      </label>
                    </div>
                    <div class="exposure-row">
                      <div><small>首次买入 60% 名义价值</small><b>{initial.target_notional_usdt:.2f} USDT</b></div>
                      <div><small>补仓后 100% 名义价值</small><b>{full.target_notional_usdt:.2f} USDT</b></div>
                      <div><small>资金费与手续费净额</small><b>{p['funding_fee'] - p['trading_fee']:+.2f} USDT</b></div>
                    </div>
                    <button class="secondary save-button" type="submit">保存设置</button>
                  </form>
                </section>

                <section class="control-block">
                  <div>
                    <small>运行控制</small>
                    <strong>{'策略已启用' if enabled else '策略未启动'}</strong>
                    <p>{'停止只影响当前币种，不影响其他币种。' if enabled else '启动后仅启用当前币种；自动交易将在下一阶段接入。'}</p>
                  </div>
                  <form method="post" action="/symbol-action">
                    <input type="hidden" name="symbol" value="{html.escape(symbol)}">
                    <input type="hidden" name="action" value="{action}">
                    <button class="{action_class} control-button" type="submit">{action_label} {html.escape(base)}</button>
                  </form>
                </section>
              </div>
            </article>
            """
        )

    configured_budget = sum(float(cfg["capital_budget_usdt"]) for cfg in configs.values())
    active_budget = sum(float(configs[s]["capital_budget_usdt"]) for s in active_symbols)
    connected = bool(testnet["connected"])
    balance_label = f"{float(account.get('usdt_balance', 0)):.2f}" if connected else "—"
    available_label = (
        f"{float(account.get('usdt_available_balance', 0)):.2f}" if connected else "—"
    )
    connection_label = "已连接虚拟资金" if connected else "等待连接"
    connection_class = "positive" if connected else "neutral"
    connection_open = "" if connected else " open"
    last_error = str(testnet.get("last_error") or "").lower()
    if last_error:
        if any(token in last_error for token in ("-2015", "invalid api-key", "unauthorized", "401")):
            error_text = "连接失败：接口密钥无效，或该密钥没有币安合约模拟交易权限。"
        elif "-1021" in last_error or "timestamp" in last_error:
            error_text = "连接失败：设备时间与币安服务器时间偏差过大。"
        elif any(token in last_error for token in ("network", "timeout", "connection", "dns")):
            error_text = "连接失败：当前网络无法连接币安合约模拟交易服务器。"
        else:
            error_text = "连接失败：请确认使用的是从币安合约模拟交易页面创建的接口密钥。"
        error_html = f'<div class="connect-error">{html.escape(error_text)}</div>'
    else:
        error_html = ""

    return (
        TEMPLATE
        .replace("__INITIAL_SYMBOL__", html.escape(initial_symbol))
        .replace("__CONNECTION_OPEN__", connection_open)
        .replace("__CONNECTION_LABEL__", connection_label)
        .replace("__CONNECTION_CLASS__", connection_class)
        .replace("__MASKED_API_KEY__", html.escape(str(testnet.get("masked_api_key") or "未连接")))
        .replace("__VIRTUAL_BALANCE__", balance_label)
        .replace("__VIRTUAL_AVAILABLE__", available_label)
        .replace("__POSITION_COUNT__", str(int(account.get("nonzero_position_count", 0))) if connected else "—")
        .replace("__ONE_WAY_STATUS__", "正常" if account.get("one_way") else ("异常" if connected else "—"))
        .replace("__CONNECT_ERROR__", error_html)
        .replace("__ACTIVE_COUNT__", str(len(active_symbols)))
        .replace("__CONFIGURED_BUDGET__", f"{configured_budget:.2f}")
        .replace("__ACTIVE_BUDGET__", f"{active_budget:.2f}")
        .replace("__TOTAL_PNL__", f"{summary['total_pnl']:+.2f}")
        .replace("__TOTAL_PNL_CLASS__", _pnl_class(summary["total_pnl"]))
        .replace("__REALIZED_PNL__", f"{summary['realized_pnl']:+.2f}")
        .replace("__UNREALIZED_PNL__", f"{summary['unrealized_pnl']:+.2f}")
        .replace("__COIN_TABS__", "\n".join(tabs))
        .replace("__COIN_PANELS__", "\n".join(panels))
    )


class Handler(BaseHTTPRequestHandler):
    server_version = "5sCryptoM2_3/1.0"

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _redirect_home(self, symbol: str | None = None) -> None:
        location = "/"
        if symbol in settings.symbols:
            location += "?" + urlencode({"symbol": symbol})
        self.send_response(303)
        self.send_header("Location", location)
        self.end_headers()

    def _read_form(self) -> dict[str, list[str]]:
        length = int(self.headers.get("Content-Length", "0"))
        return parse_qs(self.rfile.read(length).decode("utf-8"), keep_blank_values=True)

    def _symbol_from_form(self, form: dict[str, list[str]]) -> str:
        symbol = form.get("symbol", [""])[0].upper().strip()
        if symbol not in settings.symbols:
            raise ValueError("不支持这个币种")
        return symbol

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/":
            query = parse_qs(parsed.query)
            selected = query.get("symbol", [None])[0]
            self._send(
                200,
                render_index(selected).encode("utf-8"),
                "text/html; charset=utf-8",
            )
            return
        if parsed.path == "/api/status":
            result = probe.probe()
            payload = {
                "app": settings.app_name,
                "environment": testnet_session.public_status(),
                "market": "BINANCE_USDS_M_PERPETUAL",
                "margin_type": settings.margin_type,
                "position_mode": settings.position_mode,
                "direction": settings.direction,
                "live_enabled": False,
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
            self._send(
                200,
                json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                "application/json; charset=utf-8",
            )
            return
        self._send(404, "页面不存在".encode("utf-8"), "text/plain; charset=utf-8")

    def do_POST(self) -> None:
        try:
            form = self._read_form()

            if self.path == "/testnet-connect":
                environment = form.get("environment", ["DEMO"])[0].upper().strip()
                if environment != "DEMO":
                    raise ValueError("当前阶段只允许币安合约模拟交易")
                api_key = form.get("api_key", [""])[0]
                api_secret = form.get("api_secret", [""])[0]
                testnet_session.connect_and_test(api_key, api_secret)
                self._redirect_home()
                return

            if self.path == "/testnet-retest":
                testnet_session.test_existing_credentials()
                self._redirect_home()
                return

            if self.path == "/testnet-disconnect":
                testnet_session.disconnect()
                self._redirect_home()
                return

            if self.path == "/symbol-settings":
                symbol = self._symbol_from_form(form)
                budget = float(form.get("capital_budget_usdt", ["0"])[0])
                leverage = int(form.get("leverage", ["0"])[0])
                timeframe = form.get("timeframe", [""])[0]
                if budget <= 0 or budget > 100_000_000:
                    raise ValueError("策略资金必须大于零")
                if not settings.min_leverage <= leverage <= settings.max_leverage:
                    raise ValueError("杠杆倍数超出允许范围")
                if timeframe not in settings.allowed_timeframes:
                    raise ValueError("不支持这个周期")
                store.set_symbol_config(
                    symbol,
                    capital_budget_usdt=budget,
                    leverage=leverage,
                    timeframe=timeframe,
                )
                self._redirect_home(symbol)
                return

            if self.path == "/symbol-action":
                symbol = self._symbol_from_form(form)
                action = form.get("action", [""])[0].lower().strip()
                if action not in {"start", "stop"}:
                    raise ValueError("不支持这个操作")
                store.set_symbol_enabled(symbol, action == "start")
                self._redirect_home(symbol)
                return

            self._send(404, "页面不存在".encode("utf-8"), "text/plain; charset=utf-8")
        except Exception:
            if self.path.startswith("/testnet-"):
                self._redirect_home()
                return
            body = (
                "<!doctype html><meta charset='utf-8'><title>操作失败</title>"
                "<body style='font-family:system-ui;background:#0b1020;color:#edf2f7;padding:24px'>"
                "<h2>操作失败</h2><p>请返回控制台检查输入内容后重试。</p>"
                "<p><a style='color:#9ecbff' href='/'>返回控制台</a></p></body>"
            )
            self._send(400, body.encode("utf-8"), "text/html; charset=utf-8")

    def log_message(self, fmt: str, *args) -> None:
        print(f"[web] {self.address_string()} {fmt % args}")


def create_server(host: str = "127.0.0.1", port: int = 0) -> ThreadingHTTPServer:
    """Bind the Web UI to an available loopback port.

    Port 0 asks the OS to choose a free ephemeral port, avoiding collisions with
    another SiftAlpha project or a stale local listener.
    """
    return ThreadingHTTPServer((host, port), Handler)


def main(host: str = "127.0.0.1", port: int = 0) -> None:
    enabled = [s for s, cfg in store.get_symbol_configs().items() if cfg["enabled"]]
    server = create_server(host, port)
    actual_port = int(server.server_address[1])
    url = f"http://127.0.0.1:{actual_port}"
    print(f"{settings.app_name}", flush=True)
    print(
        f"environment=DEMO_READY enabled_symbols={','.join(enabled) or 'none'} live_enabled=false",
        flush=True,
    )
    # Publish only after bind succeeds, so SiftAlpha never receives a stale/invalid URL.
    print(f"SIFTALPHA_WEB_URL={url}", flush=True)
    print(f"网页服务已启动：{url}", flush=True)
    strategy_scheduler.start()
    try:
        server.serve_forever()
    finally:
        strategy_scheduler.stop()
        server.server_close()


if __name__ == "__main__":
    main()
