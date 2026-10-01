# Phase 2 Multi-Strategy Note

Status: DESIGN_NOTE_ONLY  
Date: 2026-10-01

## Goal

Keep the current Trading Console UI as the common interface and add a second real strategy later through a strategy selector, instead of building a second UI from scratch.

## Current direction

- Keep `5s crypto v1` as the first strategy.
- Add a second real strategy as the architecture test case.
- Add a strategy selector to the current coin panel.
- Strategy selection should be per symbol, not only global.
- Shared UI stays reusable: market/account state, K-line chart, live price, OHLC, PnL, position, settings, start/stop and reconciliation.

## Required safety boundaries

- Do not change the frozen `5s crypto v1` equations or trading rules during this work.
- A running strategy or a strategy with an open position must not be silently replaced by another strategy.
- Strategy state should migrate toward `strategy_id + symbol` isolation so signals, positions, PnL, orders and recovery state cannot mix.
- Avoid growing `app.py` into strategy-specific `if/else` branches; introduce only the minimum Strategy Registry / Strategy Profile abstraction required by the second real strategy.

## Proposed Phase 2 definition

Phase 2 = Add the second real strategy + strategy selector, while extracting only the parts that must become reusable to support both strategies on the same Trading Console.

The specific second strategy is not selected yet.
