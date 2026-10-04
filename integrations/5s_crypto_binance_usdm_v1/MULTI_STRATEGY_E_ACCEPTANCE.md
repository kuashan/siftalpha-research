# 5s Crypto Multi-Strategy E v1 Acceptance

Status: IMPLEMENTED_AND_VERIFIED  
Date: 2026-10-04

## Goal

Keep the existing 5s Crypto trading console and its fixed four symbols:

- BTCUSDT
- ETHUSDT
- BNBUSDT
- SOLUSDT

Extract the frozen 5s Crypto V1 strategy from the trading framework and add a
per-symbol strategy selector so the same UI and Binance Demo execution
infrastructure can run either:

- 5s Crypto V1
- E

The console does not add a symbol-search workflow.

## Frozen safety boundary

A symbol may not switch strategy while any of the following is true:

- the symbol strategy is enabled/running;
- local strategy fraction is non-zero;
- Binance Demo reports a non-zero position for that symbol;
- Binance Demo still has open orders for that symbol.

The symbol must be stopped and flat before strategy switching.

## Architecture

The shared framework keeps responsibility for:

- Binance USDⓈ-M Demo connection;
- public/authorized K-lines;
- server-time sync;
- leverage and isolated/one-way checks;
- target-position execution;
- reduce-only exits;
- local order ledger;
- PnL/accounting;
- recovery/reconciliation;
- emergency flatten;
- the existing four-coin UI.

Strategy Registry owns strategy-specific behavior.

### 5s Crypto V1

Frozen behavior is preserved:

- BUY-A / BUY-B -> 60%;
- BUY-C in W3 -> 100%;
- first SELL family -> full exit;
- close-confirmed -> next-bar-open execution.

The pre-existing 5s regression and JS/Python signal parity tests remain PASS.

### E

E uses the frozen E v1 rule engine and emits target-position steps to the common
executor.

Current admitted automatic-trading timeframes:

- 5m
- 15m
- 1h
- 4h

The 1d -> 5d live aggregation boundary is intentionally not admitted yet
because a stable fixed five-day anchoring protocol has not been frozen.

For crypto 4h -> 1d, only completed UTC calendar days are admitted, preserving
24/7 causal behavior.

## Generic execution contract

Strategies no longer tell Binance execution to perform hard-coded 5s actions.
They emit ordered target fractions.

Examples:

- 5s: 0 -> 0.60 -> 1.00 -> 0
- E: 0 -> 0.25 / 0.50 -> up to 0.75 -> partial exits -> 0

The shared executor converts target-fraction deltas to Binance quantities using
Decimal arithmetic and exchange step sizes.

## Recovery

Orders persist:

- strategy_id;
- target_fraction_after;
- strategy_state_after.

Recovery uses the selected strategy owner and generic order metadata while
remaining backward-compatible with old 5sv1 order IDs.

## Verification

GitHub Actions workflow:

5s Crypto Multi-Strategy E v1

Verified on functional HEAD:

c04c90bd3b2487167f178a83bd0fcc278e56622d

Run:

37197862174

Result:

PASS

Covered:

- full legacy 5s unit regression;
- frozen JS/Python 5s signal parity;
- E 25% target buy;
- E 75% -> 25% proportional exit;
- strategy ownership persistence;
- four-symbol UI contract;
- strategy selector UI contract;
- flat direct-import ZIP root contract.

## Closure

5S_CRYPTO_MULTI_STRATEGY_E_V1 = IMPLEMENTED_AND_VERIFIED

This branch is an integration candidate. The original frozen
feature/5s-crypto-binance-usdm-v1 branch remains unchanged.
