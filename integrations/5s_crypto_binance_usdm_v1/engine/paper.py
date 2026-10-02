from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ExposurePreview:
    symbol: str
    leverage: int
    target_fraction: float
    capital_budget_usdt: float
    margin_allocated_usdt: float
    target_notional_usdt: float


def preview_exposure(symbol: str, capital_budget_usdt: float, target_fraction: float, leverage: int) -> ExposurePreview:
    if capital_budget_usdt <= 0:
        raise ValueError("capital_budget_usdt must be > 0")
    if not 0 <= target_fraction <= 1:
        raise ValueError("target_fraction must be between 0 and 1")
    if not 1 <= leverage <= 125:
        raise ValueError("leverage must be between 1 and 125")

    margin = capital_budget_usdt * target_fraction
    return ExposurePreview(
        symbol=symbol,
        leverage=leverage,
        target_fraction=target_fraction,
        capital_budget_usdt=capital_budget_usdt,
        margin_allocated_usdt=margin,
        target_notional_usdt=margin * leverage,
    )
