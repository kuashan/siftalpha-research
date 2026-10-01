from __future__ import annotations

from dataclasses import dataclass
from threading import Event, Thread
from typing import Any, Callable
import time

from exchange.binance_usdm_testnet import BinanceUsdMTestnetAdapter
from strategy.frozen_signal_engine import BarEvaluation, evaluate_candles


@dataclass(frozen=True)
class M3Decision:
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
    """Apply only the frozen Crypto V1 position-state rules."""
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

    if not actions:
        return M3Decision(
            signal="HOLD",
            actions=(),
            c_eligible=False,
            bar_open_time=latest.open_time,
        )
    return M3Decision(
        signal="+".join(labels),
        actions=tuple(actions),
        c_eligible=c_eligible,
        bar_open_time=latest.open_time,
    )


class TerminalDecisionError(RuntimeError):
    terminal = True


class StrategyScheduler:
    """One-process scheduler for four independent symbol slots.

    M3.2 observes newly closed candles and persists frozen strategy decisions.
    It does not place orders. M3.3 will attach the execution callback.
    """

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
        if callable(recovery_ready) and not recovery_ready():
            for symbol in enabled:
                self.store.set_run_state(symbol, "WAITING_RECONCILE")
                result[symbol] = {"state": "WAITING_RECONCILE"}
            return result

        adapter = self._adapter(api_key, api_secret)

        for symbol in enabled:
            cfg = configs[symbol]
            state = runtime[symbol]
            timeframe = str(cfg["timeframe"])
            try:
                rows = adapter.klines(symbol, timeframe, limit=self.fetch_limit)
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
                if len(closed) < self.minimum_closed_bars:
                    self.store.set_run_state(symbol, "WAITING_HISTORY")
                    result[symbol] = {
                        "state": "WAITING_HISTORY",
                        "closed_bars": len(closed),
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
                        "timeframe": timeframe,
                    }
                    continue

                if latest_open_time <= int(previous_open_time):
                    self.store.set_run_state(symbol, "MONITORING")
                    result[symbol] = {
                        "state": "MONITORING",
                        "new_bar": False,
                        "timeframe": timeframe,
                    }
                    continue

                evaluations = self.evaluator(closed)
                if not evaluations:
                    raise RuntimeError("冻结信号引擎没有返回结果")
                latest = evaluations[-1]
                closed_times = [int(row[0]) for row in closed]
                decision = decide_actions(state, latest, closed_times)
                execution_context = {
                    "signal_bar_open_time": latest_open_time,
                    "execution_bar_open_time": int(rows[-1][0]),
                    "reference_price": float(rows[-1][1]),
                    "timeframe": timeframe,
                }

                if decision.actions and self.on_decision is not None:
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
                        )
                        self.store.append_audit(
                            "M3_EXECUTION_BLOCKED",
                            symbol,
                            str(exc),
                        )
                        result[symbol] = {
                            "state": "BLOCKED",
                            "new_bar": True,
                            "timeframe": timeframe,
                            "signal": decision.signal,
                            "actions": list(decision.actions),
                            "blocked": str(exc),
                        }
                        continue

                    self.store.record_strategy_observation(
                        symbol,
                        bar_open_time=latest_open_time,
                        signal=decision.signal,
                        pending_action=None,
                        run_state="MONITORING",
                    )
                    state_name = "MONITORING"
                else:
                    self.store.record_strategy_observation(
                        symbol,
                        bar_open_time=latest_open_time,
                        signal=decision.signal,
                        pending_action=decision.pending_action,
                    )
                    state_name = "SIGNAL_READY" if decision.actions else "MONITORING"

                result[symbol] = {
                    "state": state_name,
                    "new_bar": True,
                    "timeframe": timeframe,
                    "signal": decision.signal,
                    "actions": list(decision.actions),
                }
            except Exception as exc:
                self.store.set_run_state(symbol, "ERROR")
                self.store.append_audit(
                    "SCHEDULER_ERROR",
                    symbol,
                    f"{type(exc).__name__}:{exc}",
                )
                result[symbol] = {"state": "ERROR", "error": str(exc)}

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
        self._thread = Thread(target=self._loop, name="5s-crypto-m3-scheduler", daemon=True)
        self._thread.start()

    def stop(self, timeout: float = 3.0) -> None:
        self._stop.set()
        thread = self._thread
        if thread is not None and thread.is_alive():
            thread.join(timeout=max(0.0, float(timeout)))
        self._thread = None
