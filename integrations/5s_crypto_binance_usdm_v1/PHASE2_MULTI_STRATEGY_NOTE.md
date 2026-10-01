# Phase 2 Multi-Strategy Note

Status: DESIGN_NOTE_UPDATED / STRATEGY_REGISTRY_ALIGNED  
Date: 2026-10-01

## Goal

Keep the current Trading Console UI as the common interface and support more
than one real strategy through a strategy selector, instead of building a
separate UI per strategy.

## Strategy registry

### Strategy 1 — 5s V1 Strategy Family

Strategy 1 is a cross-asset family, not Crypto-only.

Profiles:
- `5s crypto v1`: frozen production/reference baseline for the current Binance Demo integration.
- `5s stock v1`: frozen candidate ruleset; forward/OOS validation still pending.

Do not modify the frozen Crypto profile in place to support stocks.
Stock and Crypto may share signal-family identity while keeping separate
position-management profiles.

### Strategy 2 — SSSS Structure Strategy

Second strategy identity:
`ssss-structure`

Current status:
research in progress / not yet deployable.

Its logic is based on:
- five rails;
- three-color fast state;
- slow gray structure;
- state transitions;
- conditional path confirmation.

It must not be forced into the three-buy / three-sell operating template.

## Current direction

- Add a strategy selector to the current symbol panel.
- Strategy selection should be per symbol.
- Add explicit asset profile selection/resolution where required.
- Shared UI remains reusable: market/account state, K-line chart, live price,
  OHLC, PnL, position, settings, start/stop and reconciliation.

Recommended runtime identity:

`strategy_id + asset_profile + symbol`

Examples:
- `5s-v1 / crypto-v1 / BTCUSDT`
- `5s-v1 / stock-v1 / AMZN`
- `ssss-structure / future-profile / AMZN`

## Required safety boundaries

- Do not change frozen `5s crypto v1` equations or position rules in place.
- Do not silently treat the stock candidate as OOS-validated production logic.
- A running strategy or a strategy with an open position must not be silently
  replaced by another strategy or asset profile.
- Signals, positions, PnL, orders and recovery state must be isolated by
  strategy/profile/symbol ownership.
- Avoid growing `app.py` into strategy-specific if/else branches; use the
  minimum Strategy Registry / Strategy Profile abstraction required.

## Phase 2 definition

Phase 2 =
1. make Strategy 1 profile-aware (Crypto + Stock);
2. preserve the frozen Crypto profile unchanged;
3. prepare Stock-profile routing without falsely promoting it past its current validation state;
4. add Strategy 2 (SSSS) only when its research freeze is complete;
5. keep one reusable Trading Console.
