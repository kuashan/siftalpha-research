from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Signal(str, Enum):
    BUY_A = "BUY_A"
    BUY_B = "BUY_B"
    BUY_C = "BUY_C"
    SELL_A = "SELL_A"
    SELL_B = "SELL_B"
    SELL_C = "SELL_C"
    MULTI_SELL = "MULTI_SELL"
    HOLD = "HOLD"


@dataclass(frozen=True)
class FrozenCryptoV1Policy:
    """Frozen sizing/execution contract for 5s-crypto V1.

    Signal generation is deliberately not implemented in M1. M3 will port the
    already-frozen research equations and prove parity against research fixtures.
    """

    initial_fraction: float = 0.60
    confirmed_fraction: float = 1.00
    confirmation_window_bars: int = 3
    execution: str = "CLOSE_CONFIRMED_NEXT_BAR_OPEN"

    def target_fraction(self, current_fraction: float, signal: Signal, *, c_eligible: bool = False) -> float:
        current = min(max(float(current_fraction), 0.0), 1.0)
        if signal in (Signal.SELL_A, Signal.SELL_B, Signal.SELL_C, Signal.MULTI_SELL):
            return 0.0
        if signal in (Signal.BUY_A, Signal.BUY_B) and current <= 0.0:
            return self.initial_fraction
        if signal == Signal.BUY_C and c_eligible and 0.0 < current < self.confirmed_fraction:
            return self.confirmed_fraction
        return current
