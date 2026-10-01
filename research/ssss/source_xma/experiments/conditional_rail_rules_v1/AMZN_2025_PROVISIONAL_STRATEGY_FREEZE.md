# AMZN 2025 Provisional SSSS Strategy Test — Freeze Before Run

Status: FROZEN_BEFORE_RUN / PROVISIONAL
Date: 2026-10-01

Purpose:
Test the currently most-supported SSSS conditional path on AMZN during calendar year 2025.
This is not the final Round-2 strategy and must not be tuned after seeing AMZN 2025 outcome.

## Data / chronology
- Symbol: AMZN
- Timeframe: 1D
- Evaluation: 2025-01-01 through 2025-12-31
- Warm-up: 2019-2024
- Provider: Twelve Data
- Strict first-observed Source-XMA:
  at each bar t, use only data <= t, recompute right-edge XMA25/XMA60, freeze t, then advance.

## State authority
Raw Source-SSSS state: UP / DOWN / RANGE / EXPANSION.

## Trading rules

Signal at close, execute next tradable open.

Entry:
- Flat
- new LOWER_FAST episode: LOW < ZD1 and prior bar not below ZD1
- raw state == DOWN
=> target exposure 50%.

Confirm/add:
- after the qualifying lower event, within 20 trading bars
- CLOSE >= current first-observed MID
=> target exposure 100%.

Reduce:
- while long
- new UPPER_FAST episode: HIGH > ZK1 and prior bar not above ZK1
- raw state == UP
=> target exposure 50%.

Exit:
- after a qualifying UP-state upper event, within 20 trading bars
- CLOSE <= current first-observed MID
=> target exposure 0%.

No action from:
- upper outer BS alone
- lower outer BD alone
- light-gray band alone
- RANGE-state lower/upper events
- DOWN upper event
- UP lower event

## Execution / accounting
- initial capital: 10,000
- long-only
- fractional shares
- next-open execution
- 5 bps adverse slippage one way
- commission 0
- rebalance to target fraction of current marked equity at execution
- final 2025 position, if any, liquidated at final close with 5 bps adverse slippage for calendar-year reporting.

## Required outputs
- total return
- max drawdown
- number and dates of actions
- year-end liquidation if applicable
- time in market
- raw signal path
- compare with AMZN 2025 buy-and-hold over same first/last tradable dates using same entry/exit slippage.

Governance:
Do not alter thresholds/rules after outcome inspection.
