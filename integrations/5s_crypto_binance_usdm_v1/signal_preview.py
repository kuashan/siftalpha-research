from __future__ import annotations

"""API-independent strategy signal preview for the 5s crypto chart.

This module reuses the frozen signal engine and frozen position-state decision
function. It simulates only the strategy state needed to locate theoretical B/S
signal bars. It never submits orders and never reads account credentials.
"""

from typing import Any, Callable

from engine.scheduler import M3Decision, decide_actions
from strategy.frozen_signal_engine import BarEvaluation, evaluate_candles


SIGNAL_HISTORY_LIMIT = 600


def _apply_pending(runtime: dict[str, Any], decision: M3Decision) -> None:
    for action in decision.actions:
        if action == "BUY_60":
            runtime["current_fraction"] = 0.60
            runtime["c_confirmed"] = False
            runtime["entry_signal_open_time"] = decision.bar_open_time
            runtime["entry_family"] = (
                "A" if decision.signal.startswith("BUY_A") else "B"
            )
        elif action == "TOPUP_TO_100":
            runtime["current_fraction"] = 1.0
            runtime["c_confirmed"] = True
        elif action == "SELL_ALL":
            runtime["current_fraction"] = 0.0
            runtime["c_confirmed"] = False
            runtime["entry_signal_open_time"] = None
            runtime["entry_family"] = None


def build_strategy_signal_markers(
    rows: list[Any],
    *,
    evaluator: Callable[[Any], list[BarEvaluation]] = evaluate_candles,
    decider: Callable[[dict[str, Any], BarEvaluation, list[int]], M3Decision] = decide_actions,
) -> list[dict[str, object]]:
    """Return theoretical B/S markers from public market bars.

    The last exchange row is considered forming and is excluded, matching the
    scheduler contract. State transitions are applied at the next-bar boundary.
    """
    if not isinstance(rows, list) or len(rows) < 2:
        return []

    closed = rows[:-1]
    evaluations = evaluator(closed)
    if not evaluations:
        return []

    runtime: dict[str, Any] = {
        "current_fraction": 0.0,
        "c_confirmed": False,
        "entry_signal_open_time": None,
        "entry_family": None,
    }
    closed_times: list[int] = []
    pending: M3Decision | None = None
    markers: list[dict[str, object]] = []

    for latest in evaluations:
        if pending is not None:
            _apply_pending(runtime, pending)

        open_time = int(latest.open_time)
        closed_times.append(open_time)
        decision = decider(runtime, latest, closed_times)

        signal = str(decision.signal or "").upper()
        if signal and signal != "HOLD":
            if "BUY_" in signal:
                markers.append({
                    "open_time": open_time,
                    "side": "B",
                    "signal": signal,
                    "source": "STRATEGY_PREVIEW",
                })
            if "SELL_" in signal or "MULTI_SELL" in signal:
                markers.append({
                    "open_time": open_time,
                    "side": "S",
                    "signal": signal,
                    "source": "STRATEGY_PREVIEW",
                })

        pending = decision

    return markers
