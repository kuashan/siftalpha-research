# ARM 2020-2023 FIVEGZ5SE Three-Buy / Three-Sell Validation

Status: **BLOCKED_BY_DATA**

Date: 2026-09-29

## Requested test

Symbol:
- ARM (Arm Holdings plc ADR, NASDAQ)

Requested period:
- 2020-01-01 through 2023-12-31

Strategy:
- BUY-A
- BUY-B
- BUY-C = B-F5 neutral-zone recovery
- SELL-A
- SELL-B
- SELL-C

Execution:
- signal at close t
- next-session open execution
- 5 bps adverse slippage each side
- long/cash only
- no arbitrary maximum holding period
- original formula-native operation prompts are not used

## Data availability boundary

ARM ADSs began trading on NASDAQ on **2023-09-14**.

Therefore there is no public ARM trading history for:
- 2020
- 2021
- 2022
- 2023 before 2023-09-14

The market-data source independently reports the earliest ARM daily timestamp as:
- 2023-09-14

Available 2023 listed period:
- first bar: 2023-09-14
- last bar: 2023-12-29
- sessions: 75

Thus the requested 2020-2023 four-year test cannot be constructed honestly.

## Five-dimensional warm-up boundary

The current FIVEGZ5SE replay contains long rolling dependencies including:
- MA60
- ATR14 -> MA50
- W1 / W3 / W5 temporal context

The longest required rolling chain becomes complete only on the 63rd listed bar.

For ARM 2023:
- first complete long-window context: **2023-12-12**
- first signal day with both current and previous fully warmed context: **2023-12-13**
- fully eligible signal sessions through 2023-12-29: **12**

This leaves too little data for a meaningful strategy validation.

## Three-buy / three-sell result on the eligible window

Signal counts:

- BUY-A: 0
- BUY-B: 0
- BUY-C (B-F5): 0
- SELL-A: 0
- SELL-B: 1
- SELL-C: 3

Trades opened:
- **0**

Closed trades:
- **0**

Marked strategy return:
- **0.00%**

Maximum drawdown:
- **0.00%**

These figures do **not** mean the strategy outperformed or underperformed.
They mean no valid buy signal occurred during the only 12 fully eligible sessions.

For context only, ARM buy-and-hold over its entire listed 2023 period
(2023-09-14 through 2023-12-29) returned approximately **+33.81%**
with the same 5 bps entry/exit slippage.

That buy-and-hold period is not comparable to the strategy because most of it
falls inside the indicator warm-up period.

## Eligible-period signal audit

- 2023-12-13: no signal
- 2023-12-14: SELL-C
- 2023-12-15: SELL-B
- 2023-12-18: no signal
- 2023-12-19: no signal
- 2023-12-20: no signal
- 2023-12-21: no signal
- 2023-12-22: no signal
- 2023-12-26: SELL-C
- 2023-12-27: no signal
- 2023-12-28: SELL-C
- 2023-12-29: no signal

No BUY-A / BUY-B / BUY-C event occurred.

## Research conclusion

The correct state is:

`ARM_2020_2023_THREE_BUY_THREE_SELL_VALIDATION = BLOCKED_BY_DATA`

Not:
- PASS
- FAIL
- REJECTED

Reason:

ARM did not publicly trade during 2020-2022 and most of 2023, and after the
required five-dimensional warm-up there are only 12 eligible sessions.

The current three-buy / three-sell candidate remains unchanged.

No parameter or rule is modified from this ARM result.

Closure:

`ARM_2020_2023_VALIDATION = BLOCKED_BY_DATA`
