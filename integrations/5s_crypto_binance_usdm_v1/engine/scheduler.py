from __future__ import annotations

from dataclasses import dataclass
from threading import Event, Thread
from typing import Any, Callable
import time

from exchange.binance_usdm_testnet import BinanceUsdMTestnetAdapter
from strategy.frozen_signal_engine import BarEvaluation, evaluate_candles
from strategy.registry import STRATEGY_5S, decide as decide_strategy, get_spec


@dataclass(frozen=True)
class M3Decision:
    """Legacy 5s-only decision retained for frozen regression compatibility."""
    signal: str
    actions: tuple[str, ...]
    c_eligible: bool = False
    bar_open_time: int | None = None

    @property
    def pending_action(self) -> str | None:
        return "+".join(self.actions) if self.actions else None


def decide_actions(
    runtime: dict[str, Any],
    latest: BarEvaluation,
    closed_open_times: list[int],
) -> M3Decision:
    """Frozen Crypto V1 position rules; kept bit-for-bit compatible."""
    fraction = min(max(float(runtime.get("current_fraction") or 0.0), 0.0), 1.0)
    c_confirmed = bool(runtime.get("c_confirmed"))
    buy = tuple(latest.buy_onsets)
    sell = tuple(latest.sell_onsets)

    c_eligible = False
    entry_time = runtime.get("entry_signal_open_time")
    if (
        fraction > 0.0
        and fraction < 1.0
        and not c_confirmed
        and "C" in buy
        and entry_time is not None
    ):
        try:
            entry_index = closed_open_times.index(int(entry_time))
            distance = len(closed_open_times) - 1 - entry_index
            c_eligible = 1 <= distance <= 3
        except (ValueError, TypeError):
            c_eligible = False

    actions: list[str] = []
    labels: list[str] = []
    if fraction > 0.0:
        if c_eligible:
            actions.append("TOPUP_TO_100")
            labels.append("BUY_C")
        if sell:
            actions.append("SELL_ALL")
            labels.append("MULTI_SELL" if len(sell) >= 2 else f"SELL_{sell[0]}")
    else:
        initial = [x for x in buy if x in ("A", "B")]
        if initial and not sell:
            family = initial[0]
            actions.append("BUY_60")
            labels.append(f"BUY_{family}")

    return M3Decision(
        signal="+".join(labels) if labels else "HOLD",
        actions=tuple(actions),
        c_eligible=c_eligible if actions else False,
        bar_open_time=latest.open_time,
    )


class TerminalDecisionError(RuntimeError):
    terminal = True


def _decision_action_codes(decision) -> list[str]:
    steps = getattr(decision, "steps", None)
    if steps is not None:
        return [str(x.code) for x in steps]
    return list(getattr(decision, "actions", ()))


def _has_actions(decision) -> bool:
    return bool(getattr(decision, "steps", ()) or getattr(decision, "actions", ()))


class StrategyScheduler:
    """One scheduler, four fixed crypto symbols, pluggable strategy adapters."""

    def __init__(
        self,
        *,
        store,
        session,
        symbols: tuple[str, ...],
        allowed_timeframes: tuple[str, ...],
        adapter_factory: Callable[..., Any] = BinanceUsdMTestnetAdapter,
        evaluator: Callable[[Any], list[BarEvaluation]] = evaluate_candles,
        poll_seconds: float = 5.0,
        fetch_limit: int = 220,
        minimum_closed_bars: int = 80,
        on_decision: Callable[..., Any] | None = None,
        on_poll: Callable[..., Any] | None = None,
    ):
        self.store = store
        self.session = session
        self.symbols = symbols
        self.allowed_timeframes = allowed_timeframes
        self.adapter_factory = adapter_factory
        self.evaluator = evaluator
        self.poll_seconds = max(1.0, float(poll_seconds))
        self.fetch_limit = max(100, int(fetch_limit))
        self.minimum_closed_bars = max(64, int(minimum_closed_bars))
        self.on_decision = on_decision
        self.on_poll = on_poll
        self._stop = Event()
        self._thread: Thread | None = None

    def _adapter(self, api_key: str, api_secret: str):
        return self.adapter_factory(
            mode="DEMO",
            api_key=api_key,
            api_secret=api_secret,
            allowed_symbols=self.symbols,
            allowed_timeframes=self.allowed_timeframes,
        )

    @staticmethod
    def _closed_rows(rows: Any) -> list[Any]:
        if not isinstance(rows, list) or len(rows) < 2:
            return []
        return rows[:-1]

    def _make_decision(self, strategy_id: str, closed: list[Any], state: dict[str, Any], timeframe: str):
        # Tests from frozen 5s V1 inject a fake evaluator. Preserve that seam.
        if strategy_id == STRATEGY_5S and self.evaluator is not evaluate_candles:
            evaluations = self.evaluator(closed)
            if not evaluations:
                raise RuntimeError("冻结信号引擎没有返回结果")
            latest = evaluations[-1]
            return decide_actions(state, latest, [int(row[0]) for row in closed])
        return decide_strategy(strategy_id, closed, state, timeframe)

    def run_once(self) -> dict[str, dict[str, Any]]:
        configs = self.store.get_symbol_configs()
        runtime = self.store.get_runtime_states()
        enabled = [s for s in self.symbols if bool(configs.get(s, {}).get("enabled"))]
        result: dict[str, dict[str, Any]] = {}

        if not enabled:
            return result

        api_key, api_secret = self.session.credentials()
        if not api_key or not api_secret:
            for symbol in enabled:
                self.store.set_run_state(symbol, "WAITING_DEMO")
                result[symbol] = {"state": "WAITING_DEMO"}
            return result

        recovery_ready = getattr(self.session, "recovery_ready", None)
        ready_symbols: list[str] = []
        for symbol in enabled:
            if callable(recovery_ready) and not recovery_ready(symbol):
                self.store.set_run_state(symbol, "WAITING_RECONCILE")
                result[symbol] = {"state": "WAITING_RECONCILE"}
            else:
                ready_symbols.append(symbol)
        if not ready_symbols:
            return result

        adapter = self._adapter(api_key, api_secret)

        for symbol in ready_symbols:
            cfg = configs[symbol]
            state = runtime[symbol]
            timeframe = str(cfg["timeframe"])
            strategy_id = str(cfg.get("strategy_id") or STRATEGY_5S)
            try:
                spec = get_spec(strategy_id)
                if timeframe not in spec.supported_timeframes:
                    raise ValueError(f"{spec.label} 不支持当前周期 {timeframe}")

                limit = max(self.fetch_limit, int(spec.fetch_limit))
                min_closed = max(self.minimum_closed_bars, int(spec.minimum_closed_bars))
                rows = adapter.klines(symbol, timeframe, limit=limit)

                if self.on_poll is not None:
                    try:
                        self.on_poll(symbol, adapter)
                    except Exception as exc:
                        self.store.append_audit(
                            "M3_ACCOUNTING_REFRESH_ERROR",
                            symbol,
                            f"{type(exc).__name__}:{exc}",
                        )

                closed = self._closed_rows(rows)
                if len(closed) < min_closed:
                    self.store.set_run_state(symbol, "WAITING_HISTORY")
                    result[symbol] = {
                        "state": "WAITING_HISTORY",
                        "closed_bars": len(closed),
                        "required_bars": min_closed,
                        "strategy_id": strategy_id,
                        "timeframe": timeframe,
                    }
                    continue

                latest_open_time = int(closed[-1][0])
                previous_open_time = state.get("last_closed_bar_open_time")
                if previous_open_time is None:
                    self.store.baseline_closed_bar(symbol, latest_open_time)
                    result[symbol] = {
                        "state": "MONITORING",
                        "baseline": latest_open_time,
                        "strategy_id": strategy_id,
                        "timeframe": timeframe,
                    }
                    continue

                if latest_open_time <= int(previous_open_time):
                    self.store.set_run_state(symbol, "MONITORING")
                    result[symbol] = {
                        "state": "MONITORING",
                        "new_bar": False,
                        "strategy_id": strategy_id,
                        "timeframe": timeframe,
                    }
                    continue

                decision = self._make_decision(strategy_id, closed, state, timeframe)
                execution_context = {
                    "signal_bar_open_time": latest_open_time,
                    "execution_bar_open_time": int(rows[-1][0]),
                    "reference_price": float(rows[-1][1]),
                    "timeframe": timeframe,
                }

                if _has_actions(decision) and self.on_decision is not None:
                    try:
                        self.on_decision(
                            symbol,
                            decision,
                            cfg,
                            state,
                            adapter,
                            execution_context,
                        )
                    except TerminalDecisionError as exc:
                        self.store.record_strategy_observation(
                            symbol,
                            bar_open_time=latest_open_time,
                            signal=decision.signal,
                            pending_action=None,
                            run_state="BLOCKED",
                            strategy_id=strategy_id,
                        )
                        self.store.append_audit(
                            "M3_EXECUTION_BLOCKED",
                            symbol,
                            f"strategy={strategy_id};{exc}",
                        )
                        result[symbol] = {
                            "state": "BLOCKED",
                            "new_bar": True,
                            "strategy_id": strategy_id,
                            "timeframe": timeframe,
                            "signal": decision.signal,
                            "actions": _decision_action_codes(decision),
                            "blocked": str(exc),
                        }
                        continue

                    self.store.record_strategy_observation(
                        symbol,
                        bar_open_time=latest_open_time,
                        signal=decision.signal,
                        pending_action=None,
                        run_state="MONITORING",
                        strategy_id=strategy_id,
                    )
                    state_name = "MONITORING"
                else:
                    self.store.record_strategy_observation(
                        symbol,
                        bar_open_time=latest_open_time,
                        signal=decision.signal,
                        pending_action=getattr(decision, "pending_action", None),
                        strategy_id=strategy_id,
                    )
                    state_name = "SIGNAL_READY" if _has_actions(decision) else "MONITORING"

                result[symbol] = {
                    "state": state_name,
                    "new_bar": True,
                    "strategy_id": strategy_id,
                    "timeframe": timeframe,
                    "signal": decision.signal,
                    "actions": _decision_action_codes(decision),
                }
            except Exception as exc:
                self.store.set_run_state(symbol, "ERROR")
                self.store.append_audit(
                    "SCHEDULER_ERROR",
                    symbol,
                    f"strategy={strategy_id};{type(exc).__name__}:{exc}",
                )
                result[symbol] = {
                    "state": "ERROR",
                    "strategy_id": strategy_id,
                    "error": str(exc),
                }

        return result

    def _loop(self) -> None:
        while not self._stop.is_set():
            started = time.monotonic()
            try:
                self.run_once()
            except Exception as exc:
                self.store.append_audit(
                    "SCHEDULER_LOOP_ERROR",
                    None,
                    f"{type(exc).__name__}:{exc}",
                )
            elapsed = time.monotonic() - started
            self._stop.wait(max(1.0, self.poll_seconds - elapsed))

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = Thread(target=self._loop, name="crypto-multistrategy-scheduler", daemon=True)
        self._thread.start()

    def stop(self, timeout: float = 3.0) -> None:
        self._stop.set()
        thread = self._thread
        if thread is not None and thread.is_alive():
            thread.join(timeout=max(0.0, float(timeout)))
        self._thread = None
