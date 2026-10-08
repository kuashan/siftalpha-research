from __future__ import annotations

import html
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse

from charting import DISPLAY_KLINE_LIMIT, normalize_chart_klines
from config import Settings
from engine.paper import preview_exposure
from engine.execution import M3Executor
from engine.recovery import M4Recovery
from engine.scheduler import StrategyScheduler
from exchange.binance_usdm_public import BinanceUsdMPublicProbe
from runtime_testnet_session import TestnetSession
from storage import StateStore
from strategy.registry import (
    STRATEGY_5S,
    STRATEGY_SSSS,
    STRATEGY_MFRA,
    get_spec,
    strategy_options,
    strategy_signal_label,
)
from strategy.matrixquant_strategy import chart_snapshot as mfra_chart_snapshot, evaluate_pai, chart_signal_markers as mfra_chart_signal_markers
from strategy.ssss_strategy import (
    analyze_ssss,
    closed_bar_window as ssss_closed_bar_window,
    source_sha256 as ssss_source_sha256,
)


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
m3_executor = M3Executor(store)
m4_recovery = M4Recovery(store, execution_lock=m3_executor.operation_lock)
strategy_scheduler = StrategyScheduler(
    store=store,
    session=testnet_session,
    symbols=settings.symbols,
    allowed_timeframes=settings.allowed_timeframes,
    on_decision=m3_executor.execute,
    on_poll=m3_executor.refresh_accounting,
    market_data=probe,
)
TEMPLATE = (Path(__file__).parent / "templates" / "index.html").read_text(encoding="utf-8")


_TIMEFRAME_LABELS = {
    "3m": "3 分钟",
    "5m": "5 分钟",
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
    "WAITING_RECONCILE": "等待恢复对账",
    "RECOVERY_BLOCKED": "恢复对账已阻止",
    "MONITORING": "监测中",
    "SIGNAL_READY": "发现信号",
    "ERROR": "检测异常",
    "BLOCKED": "交易已阻止",
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


def _timeframe_options(selected_timeframe: str, strategy_id: str) -> str:
    options = []
    spec = get_spec(strategy_id)
    for interval in spec.supported_timeframes:
        selected = interval == selected_timeframe
        label = _TIMEFRAME_LABELS.get(interval, interval)
        if strategy_id == STRATEGY_5S:
            status = "已验证基线" if interval in settings.validated_timeframes else "实验周期"
        elif strategy_id == STRATEGY_SSSS:
            status = "SSSS 原始指标周期"
        else:
            status = "MatrixQuant PAI 研究周期"
        options.append(
            '<button '
            'type="button" '
            f'class="timeframe-option{" selected" if selected else ""}" '
            f'data-timeframe-option="{html.escape(interval)}" '
            'role="option" '
            f'aria-selected="{"true" if selected else "false"}">'
            f'<span>{html.escape(label)}</span>'
            f'<small>{html.escape(status)}</small>'
            '</button>'
        )
    return "\n".join(options)


def _pnl_class(value: float) -> str:
    return "positive" if value > 0 else "negative" if value < 0 else "neutral"


def _signal_label(value: object, strategy_id: str) -> str:
    return strategy_signal_label(strategy_id, value)


def _short_symbol(symbol: str) -> str:
    return symbol[:-4] if symbol.endswith("USDT") else symbol


def _position_metrics(symbol: str) -> dict[str, object]:
    api_key, api_secret = testnet_session.credentials()
    if not api_key or not api_secret:
        return {}
    try:
        return dict(testnet_session.adapter().position_metrics(symbol))
    except Exception:
        return {}


def _number_label(value: object, *, suffix: str = "", digits: int = 2) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "—"
    if number <= 0:
        return "—"
    return f"{number:.{digits}f}{suffix}"


def run_m4_recovery() -> dict[str, object]:
    adapter = testnet_session.adapter()
    summary = m4_recovery.reconcile_all(adapter, settings.symbols)
    testnet_session.set_recovery_status(summary, summary.get("status") == "PASS")
    for symbol, item in (summary.get("symbols") or {}).items():
        if isinstance(item, dict) and item.get("status") == "PASS":
            try:
                m3_executor.refresh_accounting(symbol, adapter, force=True)
            except Exception as exc:
                store.append_audit("M4_ACCOUNTING_REFRESH_ERROR", symbol, f"{type(exc).__name__}:{exc}")
    return summary


def ensure_symbol_reconciled_for_start(symbol: str) -> None:
    """Refresh recovery before enabling a symbol; never bypass a block."""
    if not all(testnet_session.credentials()):
        raise ValueError("请先连接模拟交易账户")
    summary = run_m4_recovery()
    item = (summary.get("symbols") or {}).get(symbol)
    if not isinstance(item, dict) or item.get("status") != "PASS":
        raise ValueError("恢复对账未通过，已阻止启动")


def _ssss_chart_analysis(rows: list[object]) -> dict[str, object]:
    # Exact same 1000-closed-bar input and same cached evaluator as automation.
    closed_rows = ssss_closed_bar_window(rows, closed_limit=DISPLAY_KLINE_LIMIT)
    analysis = analyze_ssss(closed_rows)
    overlay = analysis.overlay(display_limit=DISPLAY_KLINE_LIMIT)
    indicators: list[dict[str, object]] = []
    for row in overlay:
        if bool(row.get("buy_icon_9")):
            indicators.append({
                "open_time": int(row["open_time"]),
                "kind": "BUY_ICON_9",
                "text": "💰",
            })
        if bool(row.get("exit_icon_15")):
            indicators.append({
                "open_time": int(row["open_time"]),
                "kind": "EXIT_ICON_15",
                "text": "💥",
            })
    latest = overlay[-1] if overlay else {}
    return {
        "overlay": overlay,
        "indicator_markers": indicators,
        "snapshot": {
            "source_sha256": ssss_source_sha256(),
            "buy_icon_9": bool(latest.get("buy_icon_9")),
            "exit_icon_15": bool(latest.get("exit_icon_15")),
            "state": latest.get("state"),
        },
    }


def chart_payload(symbol: str) -> dict[str, object]:
    symbol = symbol.upper().strip()
    if symbol not in settings.symbols:
        raise ValueError("不支持这个币种")
    cfg = store.get_symbol_configs()[symbol]
    runtime = store.get_runtime_states()[symbol]
    timeframe = str(cfg["timeframe"])
    strategy_id = str(cfg.get("strategy_id") or STRATEGY_5S)
    spec = get_spec(strategy_id)

    # Display may expose up to 1000 bars. Strategy analysis warmup remains independent.
    request_limit = max(DISPLAY_KLINE_LIMIT, int(spec.fetch_limit)) + 1

    source = "币安公开行情"
    try:
        api_key, api_secret = testnet_session.credentials()
        if api_key and api_secret:
            rows = testnet_session.adapter().klines(
                symbol, timeframe, limit=request_limit
            )
            source = "币安模拟交易行情"
        else:
            rows = probe.klines(symbol, timeframe, limit=request_limit)
    except Exception:
        rows = probe.klines(symbol, timeframe, limit=request_limit)
        source = "币安公开行情"

    all_rows = rows if isinstance(rows, list) else []
    display_rows = all_rows[-DISPLAY_KLINE_LIMIT:]
    candles = normalize_chart_klines(display_rows)

    strategy_overlay: list[dict[str, object]] = []
    strategy_snapshot: dict[str, object] = {}
    strategy_indicator_markers: list[dict[str, object]] = []
    markers = store.list_trade_markers(symbol, strategy_id)
    if strategy_id == STRATEGY_SSSS:
        try:
            ssss_view = _ssss_chart_analysis(all_rows)
            strategy_overlay = list(ssss_view["overlay"])
            strategy_snapshot = dict(ssss_view["snapshot"])
            strategy_indicator_markers = list(ssss_view["indicator_markers"])
        except Exception as exc:
            strategy_snapshot = {"analysis_error": str(exc)}
    elif strategy_id == STRATEGY_MFRA:
        try:
            # Strictly CLOSED rows, never the still-forming current candle.
            closed = all_rows[:-1][-int(spec.fetch_limit):]
            points = evaluate_pai(closed)
            strategy_snapshot = mfra_chart_snapshot(closed)
            strategy_overlay = [
                {"open_time": point.open_time, "PAI": point.raw}
                for point in points if point.raw is not None
            ]
            # Visual indicators use confirmed PAI threshold crossings, even
            # when Demo is stopped. These are NOT filled execution markers.
            strategy_indicator_markers = mfra_chart_signal_markers(points)
            # B/X execution markers still come ONLY from SQLite FILLED orders.
        except Exception as exc:
            strategy_snapshot = {"analysis_error": str(exc)}

    if candles:
        first_time = int(candles[0]["open_time"])
        last_time = int(candles[-1]["open_time"])
        markers = [
            marker for marker in markers
            if first_time <= int(marker["open_time"]) <= last_time
        ]
        strategy_overlay = [
            row for row in strategy_overlay
            if first_time <= int(row["open_time"]) <= last_time
        ]
        strategy_indicator_markers = [
            row for row in strategy_indicator_markers
            if first_time <= int(row["open_time"]) <= last_time
        ]
    else:
        markers = []
        strategy_overlay = []
        strategy_indicator_markers = []

    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "strategy_id": strategy_id,
        "strategy_label": spec.label,
        "timeframe_label": _TIMEFRAME_LABELS.get(timeframe, timeframe),
        "display_limit": DISPLAY_KLINE_LIMIT,
        "source": source,
        "candles": candles,
        "markers": markers,
        "strategy_overlay": strategy_overlay,
        "strategy_indicator_markers": strategy_indicator_markers,
        "strategy_snapshot": strategy_snapshot,
        "runtime_state": str(runtime.get("run_state") or "STOPPED"),
        "runtime_state_label": _RUN_STATE_LABELS.get(str(runtime.get("run_state") or "STOPPED"), str(runtime.get("run_state") or "STOPPED")),
        "runtime_last_signal": strategy_signal_label(strategy_id, runtime.get("last_signal")),
        "runtime_fraction": float(runtime.get("current_fraction") or 0.0),
    }


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
        strategy_id = str(cfg.get("strategy_id") or STRATEGY_5S)
        spec = get_spec(strategy_id)
        enabled = bool(cfg["enabled"])
        initial = preview_exposure(symbol, budget, 0.60, leverage)
        full = preview_exposure(symbol, budget, 1.00, leverage)
        ssss25 = preview_exposure(symbol, budget, 0.25, leverage)
        if strategy_id == STRATEGY_5S:
            validation = "已验证基线" if timeframe in settings.validated_timeframes else "实验周期"
        else:
            validation = (spec.label + " 研究周期") if timeframe in spec.supported_timeframes else "当前周期不支持"
        run_state = str(rt.get("run_state") or ("ARMED" if enabled else "STOPPED"))
        status_label = _RUN_STATE_LABELS.get(run_state, "运行中" if enabled else "未启动")
        status_class = "running" if enabled and run_state in {"ARMED", "MONITORING", "SIGNAL_READY"} else "stopped"
        status_detail_html = ""
        if run_state in {"ERROR", "BLOCKED"}:
            recent_problem = store.recent_audit(
                symbol,
                event_types=("SCHEDULER_ERROR", "M3_EXECUTION_BLOCKED"),
                limit=1,
            )
            if recent_problem:
                detail = str(recent_problem[0].get("detail") or "").strip()
                if detail:
                    status_detail_html = (
                        '<div class="status-detail">'
                        + html.escape(detail[:220])
                        + '</div>'
                    )
        action = "stop" if enabled else "start"
        action_label = "停止" if enabled else "启动"
        action_class = "danger" if enabled else "primary"
        current_fraction = float(rt.get("current_fraction") or 0.0)
        last_signal = _signal_label(rt.get("last_signal"), strategy_id)
        base = _short_symbol(symbol)
        selected = symbol == initial_symbol
        position_metrics = _position_metrics(symbol)
        margin_ratio_label = _number_label(
            position_metrics.get("margin_ratio_percent"), suffix="%", digits=2
        )
        entry_price_label = _number_label(position_metrics.get("entry_price"), digits=4)
        liquidation_price_label = _number_label(
            position_metrics.get("liquidation_price"), digits=4
        )
        isolated_margin_label = _number_label(
            position_metrics.get("isolated_margin_usdt"), suffix=" USDT", digits=2
        )
        strategy_locked = enabled or current_fraction > 1e-12
        strategy_current_label = "5s V1" if strategy_id == STRATEGY_5S else spec.label
        strategy_option_html = "".join(
            (
                f'<button type="button" '
                f'class="strategy-option{" selected" if is_selected else ""}" '
                f'data-strategy-option="{html.escape(sid)}" '
                f'role="option" aria-selected="{"true" if is_selected else "false"}">'
                f'<span>{html.escape("5s V1" if sid == STRATEGY_5S else label)}</span>'
                f'<small>{html.escape("A/B 60% · C 补至 100% · SELL 全退" if sid == STRATEGY_5S else ("💰 +25% · 💥 全部清仓" if sid == STRATEGY_SSSS else "PAI +5 买25% · -5 全清"))}</small>'
                f'</button>'
            )
            for sid, label, is_selected in strategy_options(strategy_id)
        )
        strategy_lock_note = "已锁定" if strategy_locked else "可切换"
        if strategy_id == STRATEGY_5S:
            exposure_html = (
                f'<div><small>首次买入 60% 名义价值</small><b>{initial.target_notional_usdt:.2f} USDT</b></div>'
                f'<div><small>补仓后 100% 名义价值</small><b>{full.target_notional_usdt:.2f} USDT</b></div>'
            )
        elif strategy_id == STRATEGY_SSSS:
            exposure_html = (
                f'<div><small>SSSS 每个 💰 买入 25% 名义价值</small><b>{ssss25.target_notional_usdt:.2f} USDT</b></div>'
                f'<div><small>SSSS 满仓 100% 名义价值</small><b>{full.target_notional_usdt:.2f} USDT</b></div>'
            )
        else:
            exposure_html = (
                f'<div><small>PAI 每次 +5 突破买入 25% 名义价值</small><b>{ssss25.target_notional_usdt:.2f} USDT</b></div>'
                f'<div><small>MatrixQuant 满仓 100% 名义价值</small><b>{full.target_notional_usdt:.2f} USDT</b></div>'
            )
        exposure_html += (
            f'<div><small>资金费与手续费净额</small><b>{p["funding_fee"] - p["trading_fee"]:+.2f} USDT</b></div>'
        )

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
                    <span class="market-badge">U本位永续</span>
                    <span class="status-pill {status_class}">{status_label}</span>
                  </div>
                  {status_detail_html}
                </div>
                <div class="hero-right">
                  <form class="strategy-switch" method="post" action="/symbol-strategy" data-strategy-picker>
                    <input type="hidden" name="symbol" value="{html.escape(symbol)}">
                    <input type="hidden" name="strategy_id" value="{html.escape(strategy_id)}">
                    <span class="strategy-field-label">策略</span>
                    <button
                      class="strategy-trigger"
                      type="button"
                      aria-haspopup="listbox"
                      aria-expanded="false"
                      {'disabled' if strategy_locked else ''}
                    >
                      <span class="strategy-current" data-strategy-current>{html.escape(strategy_current_label)}</span>
                      <span class="strategy-chevron" aria-hidden="true">⌄</span>
                    </button>
                    <div class="strategy-menu" role="listbox" hidden>
                      {strategy_option_html}
                    </div>
                    <small>{html.escape(strategy_lock_note)}</small>
                  </form>
                  <div class="hero-pnl">
                    <small>该币总盈亏</small>
                    <strong class="{_pnl_class(p['total_pnl'])}">{p['total_pnl']:+.2f}</strong>
                    <span>USDT</span>
                  </div>
                </div>
              </div>

              <div class="snapshot-grid snapshot-above-chart">
                <div class="snapshot"><small>当前仓位</small><b>{current_fraction * 100:.0f}%</b></div>
                <div class="snapshot"><small>最新信号</small><b>{html.escape(last_signal)}</b></div>
                <div class="snapshot"><small>浮动盈亏</small><b class="{_pnl_class(p['unrealized_pnl'])}">{p['unrealized_pnl']:+.2f}</b></div>
                <div class="snapshot"><small>已实现盈亏</small><b class="{_pnl_class(p['realized_pnl'])}">{p['realized_pnl']:+.2f}</b></div>
                <div class="snapshot"><small>保证金比率</small><b>{html.escape(margin_ratio_label)}</b></div>
                <div class="snapshot"><small>开仓价格</small><b>{html.escape(entry_price_label)}</b></div>
                <div class="snapshot"><small>强平价格</small><b>{html.escape(liquidation_price_label)}</b></div>
              </div>

              <section
                class="market-chart"
                data-chart-symbol="{html.escape(symbol)}"
                data-chart-timeframe="{html.escape(timeframe)}"
              >
                <div class="chart-head">
                  <div class="chart-identity">
                    <small>行情图 · V7 交互</small>
                    <strong>{html.escape(base)} / USDT · {_TIMEFRAME_LABELS.get(timeframe, timeframe)}</strong>
                  </div>
                  <div class="live-price" aria-live="polite">
                    <small>最新价</small>
                    <strong class="live-price-value">—</strong>
                    <span class="live-price-status">正在连接实时行情</span>
                  </div>
                  <div class="chart-ohlc" aria-label="K 线开高低收">
                    <div><small>开</small><b data-ohlc="open">—</b></div>
                    <div><small>高</small><b data-ohlc="high">—</b></div>
                    <div><small>低</small><b data-ohlc="low">—</b></div>
                    <div><small>收</small><b data-ohlc="close">—</b></div>
                  </div>
                </div>
                <div class="chart-scroll">
                  <div class="kline-chart" aria-label="{html.escape(base)} K 线图"></div>
                </div>
                <div class="chart-legend">
                  <span><i class="candle-key candle-up"></i>红涨</span>
                  <span><i class="candle-key candle-down"></i>绿跌</span>
                  <span><b class="legend-buy">B</b> 买入</span>
                  <span><b class="legend-sell">S</b> 卖出</span>
                  <span><b class="legend-exit">X</b> 清仓</span>
                  <span class="strategy-legend"></span>
                </div>
                <div class="chart-gesture-hint">拖动平移 · 双指/滚轮缩放 · 点击锁定十字光标 · 双击恢复最新视图 · 最多显示 1000 根</div>
                <div class="chart-message">正在加载 {_TIMEFRAME_LABELS.get(timeframe, timeframe)} K 线…</div>
              </section>

              <div class="panel-body">
                <details class="settings-block trade-settings">
                  <summary class="trade-settings-summary">
                    <div>
                      <small>交易设置</small>
                      <strong>{validation}</strong>
                    </div>
                    <span>点击展开</span>
                  </summary>
                  <div class="trade-settings-body">
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
                      <div class="timeframe-field">
                        <span class="field-label">K 线周期</span>
                        <div class="timeframe-picker" data-timeframe-picker>
                          <input type="hidden" name="timeframe" value="{html.escape(timeframe)}">
                          <button
                            class="timeframe-trigger"
                            type="button"
                            aria-haspopup="listbox"
                            aria-expanded="false"
                          >
                            <span class="timeframe-current" data-timeframe-current>{html.escape(_TIMEFRAME_LABELS.get(timeframe, timeframe))}</span>
                            <small data-timeframe-current-status>{html.escape(validation)}</small>
                            <span class="timeframe-chevron" aria-hidden="true">⌄</span>
                          </button>
                          <div class="timeframe-menu" role="listbox" hidden>
                            {_timeframe_options(timeframe, strategy_id)}
                          </div>
                        </div>
                      </div>
                    </div>
                    <div class="exposure-row">
                      {exposure_html}
                    </div>
                    <button class="secondary save-button" type="submit">保存设置</button>
                  </form>
                  <div class="isolated-margin-control">
                    <div class="isolated-margin-head">
                      <div>
                        <small>逐仓保证金管理</small>
                        <strong>{html.escape(isolated_margin_label)}</strong>
                      </div>
                      <span>与策略资金独立</span>
                    </div>
                    <form class="isolated-margin-form" method="post" action="/position-margin">
                      <input type="hidden" name="symbol" value="{html.escape(symbol)}">
                      <label>调整金额
                        <div class="input-with-unit">
                          <input name="amount_usdt" type="number" min="0.01" step="0.01" inputmode="decimal" required>
                          <span>USDT</span>
                        </div>
                      </label>
                      <button class="secondary" type="submit" name="action" value="add">追加保证金</button>
                      <button class="danger" type="submit" name="action" value="reduce">减少保证金</button>
                    </form>
                    <small class="isolated-margin-note">只调整当前币种逐仓保证金，不改变策略仓位百分比；减少额度由 Binance 风控最终校验。</small>
                  </div>
                  </div>
                </details>

                <section class="control-block">
                  <div>
                    <small>运行控制</small>
                    <strong>{html.escape(spec.label)} · {'已启用' if enabled else '未启动'}</strong>
                    <p>{'停止只影响当前币种，不影响其他币种。' if enabled else '启动后仅启用当前币种，并按该币设置自动监测模拟交易。'}</p>
                  </div>
                  <div class="control-actions">
                    <form method="post" action="/symbol-action">
                      <input type="hidden" name="symbol" value="{html.escape(symbol)}">
                      <input type="hidden" name="action" value="{action}">
                      <button class="{action_class} control-button" type="submit">{action_label} {html.escape(base)}</button>
                    </form>
                    <form method="post" action="/cancel-strategy-orders">
                      <input type="hidden" name="symbol" value="{html.escape(symbol)}">
                      <button class="secondary control-button" type="submit">取消本策略挂单</button>
                    </form>
                    <form method="post" action="/emergency-flatten" onsubmit="return confirm('确认停止当前币种并紧急平掉模拟仓位？');">
                      <input type="hidden" name="symbol" value="{html.escape(symbol)}">
                      <button class="danger control-button" type="submit">紧急平仓</button>
                    </form>
                  </div>
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
    recovery = testnet.get("recovery") or {}
    recovery_ready = bool(testnet.get("recovery_ready"))
    if not connected:
        recovery_label = "未连接"
        recovery_class = "neutral"
    elif recovery_ready:
        recovery_label = "全部对账通过"
        recovery_class = "positive"
    elif recovery.get("status") == "BLOCKED":
        passed = sum(
            1 for item in (recovery.get("symbols") or {}).values()
            if isinstance(item, dict) and item.get("status") == "PASS"
        )
        recovery_label = f"部分阻止（{passed}/4 通过）"
        recovery_class = "negative"
    else:
        recovery_label = "等待对账"
        recovery_class = "neutral"
    top_connection_status = "已连接" if connected else "未连接"
    top_connection_class = "positive" if connected else "neutral"
    if not connected:
        top_recovery_status = "未对账"
        top_recovery_class = "neutral"
    elif recovery_ready:
        top_recovery_status = "对账通过"
        top_recovery_class = "positive"
    elif recovery.get("status") == "BLOCKED":
        top_recovery_status = "对账阻止"
        top_recovery_class = "negative"
    else:
        top_recovery_status = "等待对账"
        top_recovery_class = "neutral"

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
        .replace("__TOP_CONNECTION_STATUS__", top_connection_status)
        .replace("__TOP_CONNECTION_CLASS__", top_connection_class)
        .replace("__TOP_RECOVERY_STATUS__", top_recovery_status)
        .replace("__TOP_RECOVERY_CLASS__", top_recovery_class)
        .replace("__CONNECTION_LABEL__", connection_label)
        .replace("__CONNECTION_CLASS__", connection_class)
        .replace("__MASKED_API_KEY__", html.escape(str(testnet.get("masked_api_key") or "未连接")))
        .replace("__VIRTUAL_BALANCE__", balance_label)
        .replace("__VIRTUAL_AVAILABLE__", available_label)
        .replace("__POSITION_COUNT__", str(int(account.get("nonzero_position_count", 0))) if connected else "—")
        .replace("__ONE_WAY_STATUS__", "正常" if account.get("one_way") else ("异常" if connected else "—"))
        .replace("__RECOVERY_STATUS__", html.escape(recovery_label))
        .replace("__RECOVERY_CLASS__", recovery_class)
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
        if parsed.path == "/vendor/lightweight-charts.standalone.production.js":
            vendor_path = Path(__file__).parent / "vendor" / "lightweight-charts.standalone.production.js"
            if not vendor_path.exists():
                self._send(404, b"chart vendor missing", "text/plain; charset=utf-8")
                return
            self._send(
                200,
                vendor_path.read_bytes(),
                "application/javascript; charset=utf-8",
            )
            return
        if parsed.path == "/api/chart":
            query = parse_qs(parsed.query)
            symbol = str(query.get("symbol", [""])[0]).upper().strip()
            try:
                payload = chart_payload(symbol)
                self._send(
                    200,
                    json.dumps(payload, ensure_ascii=False, allow_nan=False).encode("utf-8"),
                    "application/json; charset=utf-8",
                )
            except Exception as exc:
                self._send(
                    400,
                    json.dumps({"error": str(exc)}, ensure_ascii=False).encode("utf-8"),
                    "application/json; charset=utf-8",
                )
            return
        if parsed.path == "/api/status":
            result = probe.probe()
            diagnostic_types = (
                "SCHEDULER_ERROR",
                "M3_EXECUTION_BLOCKED",
                "M3_EXECUTION_DISPATCH",
                "BINANCE_EXECUTION_STAGE",
                "BINANCE_ORDER_SUBMIT",
                "SSSS_BAR_DECISION",
                "SSSS_BAR_EXECUTION",
                "SSSS_SIGNAL_BASELINE",
            )
            diagnostics = {
                symbol: store.recent_audit(
                    symbol,
                    event_types=diagnostic_types,
                    limit=12,
                )
                for symbol in settings.symbols
            }
            ssss_signal_events = {
                symbol: store.recent_ssss_signal_events(symbol, limit=20)
                for symbol in settings.symbols
            }
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
                "diagnostics": diagnostics,
                "ssss_signal_events": ssss_signal_events,
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
                run_m4_recovery()
                self._redirect_home()
                return

            if self.path == "/testnet-retest":
                testnet_session.test_existing_credentials()
                run_m4_recovery()
                self._redirect_home()
                return

            if self.path == "/reconcile":
                run_m4_recovery()
                self._redirect_home()
                return

            if self.path == "/testnet-disconnect":
                testnet_session.disconnect()
                self._redirect_home()
                return

            if self.path == "/cancel-strategy-orders":
                symbol = self._symbol_from_form(form)
                adapter = testnet_session.adapter()
                m4_recovery.cancel_strategy_orders(adapter, symbol)
                run_m4_recovery()
                self._redirect_home(symbol)
                return

            if self.path == "/emergency-flatten":
                symbol = self._symbol_from_form(form)
                adapter = testnet_session.adapter()
                m4_recovery.emergency_flatten(adapter, symbol)
                m3_executor.refresh_accounting(symbol, adapter, force=True)
                run_m4_recovery()
                self._redirect_home(symbol)
                return

            if self.path == "/symbol-strategy":
                symbol = self._symbol_from_form(form)
                requested = form.get("strategy_id", [""])[0].strip().lower()
                spec = get_spec(requested)
                cfg = store.get_symbol_configs()[symbol]
                rt = store.get_runtime_states()[symbol]
                if bool(cfg["enabled"]):
                    raise ValueError("策略运行中，必须先停止后才能切换")
                if float(rt.get("current_fraction") or 0.0) > 1e-12:
                    raise ValueError("当前仍有策略仓位，必须先清仓后才能切换")

                api_key, api_secret = testnet_session.credentials()
                if api_key and api_secret:
                    adapter = testnet_session.adapter()
                    if abs(float(adapter.position_amount(symbol))) > 1e-12:
                        raise ValueError("币安模拟账户仍有该币种仓位，禁止切换策略")
                    open_orders = adapter.open_orders(symbol)
                    if open_orders:
                        raise ValueError("该币种仍有挂单，取消挂单后才能切换策略")

                timeframe = str(cfg["timeframe"])
                if timeframe not in spec.supported_timeframes:
                    timeframe = spec.default_timeframe
                store.set_symbol_strategy(symbol, spec.strategy_id, timeframe)
                if api_key and api_secret:
                    run_m4_recovery()
                self._redirect_home(symbol)
                return

            if self.path == "/position-margin":
                symbol = self._symbol_from_form(form)
                action = form.get("action", [""])[0].lower().strip()
                if action not in {"add", "reduce"}:
                    raise ValueError("不支持这个保证金操作")
                amount = float(form.get("amount_usdt", ["0"])[0])
                if amount <= 0:
                    raise ValueError("逐仓保证金调整金额必须大于零")
                adapter = testnet_session.adapter()
                result = adapter.modify_isolated_position_margin(
                    symbol,
                    amount,
                    reduce=action == "reduce",
                )
                store.append_audit(
                    "ISOLATED_MARGIN_CHANGE",
                    symbol,
                    f"action={action};amount_usdt={amount:.8f};result={result!r}",
                )
                self._redirect_home(symbol)
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
                strategy_id = str(store.get_symbol_configs()[symbol].get("strategy_id") or STRATEGY_5S)
                if timeframe not in get_spec(strategy_id).supported_timeframes:
                    raise ValueError("当前策略不支持这个周期")
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
                if action == "start":
                    cfg = store.get_symbol_configs()[symbol]
                    spec = get_spec(str(cfg.get("strategy_id") or STRATEGY_5S))
                    if str(cfg["timeframe"]) not in spec.supported_timeframes:
                        raise ValueError("当前策略不支持所选 K 线周期")
                    ensure_symbol_reconciled_for_start(symbol)
                store.set_symbol_enabled(symbol, action == "start")
                self._redirect_home(symbol)
                return

            self._send(404, "页面不存在".encode("utf-8"), "text/plain; charset=utf-8")
        except Exception as exc:
            if self.path.startswith("/testnet-") or self.path == "/reconcile":
                self._redirect_home()
                return
            body = (
                "<!doctype html><meta charset='utf-8'><title>操作失败</title>"
                "<body style='font-family:system-ui;background:#0b1020;color:#edf2f7;padding:24px'>"
                f"<h2>操作失败</h2><p>{html.escape(str(exc) or '请返回控制台检查输入内容后重试。')}</p>"
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
