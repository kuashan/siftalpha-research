# FIVEGZ5SE Three-Buy Three-Sell Refinement Protocol v1

Status: **PRE_REGISTERED**

Date: 2026-10-01

## 1. Purpose

This study addresses only the unresolved questions left by the completed staged-entry 43-asset study. It does not invent new BUY/SELL families and does not alter the frozen definitions of BUY-A, BUY-B, BUY-C, SELL-A, SELL-B or SELL-C.

Questions:

1. Stocks: does BUY-C W3 top-up add value versus staying at the same partial initial allocation?
2. Stocks: for first isolated SELL-A / SELL-B, when is HALF exit preferable to FULL exit?
3. Crypto: does BUY-C W3 top-up add value versus staying at the same partial initial allocation?
4. Crypto: should SELL-A / SELL-B / SELL-C remain equivalent FULL_FIRST exits, or do the three families have materially different forward/position outcomes?

## 2. Frozen universe

Stocks: exactly the same 39 symbols used in the completed 43-asset study:
AAPL, MSFT, NVDA, AMD, AVGO, ORCL, INTC, QCOM, MU, GOOGL, META, NFLX, AMZN, TSLA, HD, MCD, WMT, COST, PG, KO, PEP, ABT, LLY, UNH, JNJ, TMO, JPM, BAC, GS, V, MA, CAT, BA, GE, XOM, CVX, LIN, NEE, PLD.

Crypto: exactly BTC, ETH, BNB, SOL. No other cryptocurrency may enter this study.

## 3. Expanded data horizon

Daily OHLCV uses Twelve Data with the same daily-bar representation for every tested asset.

- stocks: request 2010-01-01 through 2026-09-30;
- BTC: request 2014-01-01 through 2026-09-30;
- ETH / BNB / SOL: request 2014-01-01 through 2026-09-30 and accept each instrument's actual available start date;
- warm-up rows are retained; trading begins only after the replay engine has sufficient state history.

This extended sample is development/diagnostic data after this study and must not be called untouched OOS for rules selected here.

## 4. Frozen signal and execution rules

SCTYPE=1 only.

BUY-A / BUY-B / BUY-C and SELL-A / SELL-B / SELL-C definitions remain byte-for-byte equivalent to the completed staged-entry experiment.

Execution:
- signal confirmed on bar close t;
- trade executes on next bar open;
- 5 bps adverse slippage on each transaction;
- long/cash only;
- no time-based forced exit;
- open positions at the final bar are mark-to-market.

BUY-C:
- never opens a new position by itself;
- only an onset within W3 after initial BUY-A/B is eligible for top-up;
- W5 is not reopened.

## 5. C-top-up causal controls

For each initial fraction 50%, 60%, 70%, compare under identical FULL_FIRST exits:

- STATIC_50 / STATIC_60 / STATIC_70: initial A/B entry only; never top up;
- TOPUP_50 / TOPUP_60 / TOPUP_70: same initial entry; first BUY-C onset within W3 adds the remaining fraction to 100%;
- BASE_100: immediate 100% A/B entry.

Primary causal comparison is matched TOPUP_x minus STATIC_x, not TOPUP_x versus BASE_100.

Metrics:
- cumulative return;
- MDD;
- completed-trade win rate;
- mean / median trade return;
- P10, P5, CVaR10, worst trade;
- exposure;
- number of C confirmations;
- per-asset delta;
- group mean/median delta;
- asset-level bootstrap 95% CI;
- BTC reported separately.

## 6. Stock SELL-A/B refinement

Primary BUY sizing for SELL analysis is frozen at initial 60% + W3 BUY-C top-up to 100%.

For a first isolated SELL-A or first isolated SELL-B, compare the following non-optimized action controls:

- FULL: exit 100% next open;
- HALF_THEN_DISTINCT: exit 50% next open; remaining 50% exits only on the next onset from a different SELL family;
- HOLD_TO_DISTINCT: ignore the isolated first A/B; exit 100% only when a different SELL family onsets;
- SELL-C and same-bar multi-family SELL remain mandatory FULL exits in every control.

No threshold search is permitted in this study. The study may profile pre-signal state differences to identify a later falsifiable filter, but it may not select and declare a new numeric threshold from the same data.

Required reporting separately for first SELL-A and first SELL-B:
- event count;
- post-signal 1/3/5/10-session return distribution while still holding;
- MFE / MAE over 3/5/10 sessions;
- FULL vs HALF_THEN_DISTINCT vs HOLD_TO_DISTINCT portfolio deltas;
- bootstrap CI;
- cross-symbol consistency.

## 7. Crypto SELL-family audit

Crypto retains FULL_FIRST as the operating control. The study does not assume that A/B/C are equivalent.

For BTC, ETH, BNB and SOL separately and pooled:
- count first SELL-A, SELL-B, SELL-C events;
- measure position return at each first SELL family;
- measure forward 1/3/5/10-session returns if hypothetically held;
- MFE / MAE over 3/5/10 sessions;
- compare family distributions and cross-coin consistency;
- compare FULL exit against counterfactual delayed exit to next distinct SELL family for diagnosis only.

A delayed crypto SELL policy is not admitted merely because its in-sample mean is higher. Any proposed distinction requires cross-coin consistency and bootstrap support.

## 8. Decision discipline

No conclusion is allowed until every requested stock and crypto asset has completed or is explicitly documented as unavailable.

Possible closure labels:
- IMPLEMENTED_AND_VERIFIED
- PROMOTED_TO_NEXT_VALIDATION
- RETAINED
- REJECTED_NOT_ADMITTED
- BLOCKED_BY_DATA

Historical V2 and the completed staged-entry v2 report are preserved and not overwritten.
