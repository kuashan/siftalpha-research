# Phase 2 Multi-Strategy Note

Status: **DESIGN_NOTE_UPDATED / STRATEGY_REGISTRY_ALIGNED**  
Date: 2026-10-02

## Goal

Keep the current Trading Console UI as the common interface and support more
than one real strategy through a strategy selector, instead of building a
separate UI per strategy.

## Strategy registry

### Strategy 1 — 5s V1 Strategy Family

Strategy 1 is a cross-asset family, not Crypto-only.

Profiles:
- `5s crypto v1`: `FROZEN_BASELINE`; current Binance Demo integration profile.
- `5s stocks v1`: `FROZEN_BASELINE`; forward / untouched OOS evidence is still required for the production-validation questions recorded in its baseline.

Do not modify the frozen Crypto profile in place to support stocks.
Stock and Crypto may share signal-family identity while keeping separate
position-management profiles.

### Strategy 2 — SLTD V6

Second strategy identity:

`sltd-v6`

Research status:

`OFFICIAL`

SLTD V6 is the formal 15-rule BUY / HOLD / WAIT / SELL strategy produced after
V5 optimization and V6 independent validation.

Runtime status:

**NOT_YET_INTEGRATED_INTO_TRADING_CONSOLE**

Its logic is based on:
- XMA structure;
- state color and state age;
- upper / lower rail events;
- light-gray support / resistance events;
- transition context;
- event subtypes such as WICK_ONLY and CLOSE_ABOVE / CLOSE_BELOW.

SLTD V6 must not be forced into the 5s three-buy / three-sell operating template.

## Current direction

- Keep one reusable Trading Console.
- Add a strategy selector to the current symbol panel when multi-strategy runtime work begins.
- Strategy selection should be per symbol.
- Keep explicit asset-profile selection / resolution where required.
- Shared UI remains reusable: market/account state, K-line chart, live price,
  OHLC, PnL, position, settings, start/stop and reconciliation.
- Implement SLTD V6 through a Strategy Registry / Strategy Profile boundary,
  not through growing strategy-specific if/else branches in `app.py`.

Recommended runtime identity:

`strategy_id + asset_profile + symbol`

Examples:
- `5s-v1 / crypto-v1 / BTCUSDT`
- `5s-v1 / stock-v1 / AMZN`
- `sltd-v6 / future-runtime-profile / AMZN`

The exact SLTD V6 runtime asset profile is intentionally left for the later
execution-integration design and is not invented by this documentation update.

## Required safety boundaries

- Do not change frozen `5s crypto v1` equations or position rules in place.
- Do not change frozen `5s stocks v1` rules in place.
- Do not change the official SLTD V6 15-rule taxonomy in place.
- Do not silently treat research freeze / official naming as equivalent to completed production runtime integration.
- A running strategy or a strategy with an open position must not be silently
  replaced by another strategy or asset profile.
- Signals, positions, PnL, orders and recovery state must be isolated by
  strategy/profile/symbol ownership.
- Avoid growing `app.py` into strategy-specific if/else branches; use the
  minimum Strategy Registry / Strategy Profile abstraction required.

## Phase 2 definition

Phase 2 =
1. make Strategy 1 profile-aware (Crypto + Stock);
2. preserve both frozen 5s profiles unchanged;
3. prepare Stock-profile routing without overstating production validation;
4. add SLTD V6 only after its runtime adapter / execution semantics are explicitly implemented and tested;
5. keep one reusable Trading Console.
