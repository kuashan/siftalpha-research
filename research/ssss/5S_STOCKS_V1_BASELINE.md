# SSSS 5s-stocks V1 Baseline

Status: **FROZEN_BASELINE**

Frozen date: 2026-10-01
Branch: `research/source-xma-walkforward`
Parent research state: `5a9d161416e39e38853ce585dbcc7c876262be64`

## Name

**5s-stocks V1**

This is the first frozen U.S. stocks baseline for the current SSSS three-buy / three-sell framework.

## Frozen stock universe used for development evidence

39 U.S. stocks:
AAPL, MSFT, NVDA, AMD, AVGO, ORCL, INTC, QCOM, MU, GOOGL, META, NFLX, AMZN, TSLA,
HD, MCD, WMT, COST, PG, KO, PEP, ABT, LLY, UNH, JNJ, TMO, JPM, BAC, GS, V, MA,
CAT, BA, GE, XOM, CVX, LIN, NEE, PLD.

The development history through 2026-09-29 has already influenced this baseline and is not untouched OOS.

## Frozen BUY rules

- BUY-A or BUY-B -> enter **60%** at the next regular-session bar open.
- If BUY-C onsets within W3 -> add the remaining **40%** at the next regular-session bar open, reaching 100%.
- BUY-C cannot independently open a position.
- No A/A or B/B repeat add.
- No A->B or B->A add.
- No W5 BUY-C top-up.

## Frozen SELL rules

- isolated SELL-A -> sell **50%** at the next regular-session bar open.
- isolated SELL-B -> sell **50%** at the next regular-session bar open.
- SELL-C -> sell **100%**.
- same-bar multi-family SELL -> sell **100%**.
- after an A/B half exit, the first later onset from a different SELL family exits all remaining shares.

## Frozen execution semantics

**Close Confirmed -> Next Regular-Session Bar Open**

For the current daily U.S.-stock baseline:
- the signal is confirmed only after the Regular Session closes;
- execution is at the next actual trading session's Regular Session open;
- weekends and exchange holidays are skipped naturally;
- pre-market and after-hours trading are **not** part of 5s-stocks V1;
- 5 bps adverse slippage is used per transaction in the research model;
- long / cash only;
- no time-based forced exit;
- sample-end open positions are mark-to-market.

For U.S. daily bars this means, conceptually:

`Regular Session Close -> next trading day's Regular Session Open`

It does **not** mean waiting a fixed 24 hours.

## Risk Exit

No independent Risk Exit layer is part of 5s-stocks V1.

Rejected / not admitted:
- universal fixed Hard Stop;
- universal fixed Trailing Stop;
- combined fixed hard + trailing grid;
- tested State / Volatility-Aware Risk Exit v1.

`STOCK_RISK_EXIT = NOT_USED_RETAIN_BASELINE`

## Frozen state

`5S_STOCKS_V1 = FROZEN_BASELINE`

`5S_STOCKS_V1_BUY = 60_INITIAL_PLUS_W3_C_TO_100`

`5S_STOCKS_V1_SELL_A = HALF_EXIT`

`5S_STOCKS_V1_SELL_B = HALF_EXIT`

`5S_STOCKS_V1_SELL_C = FULL_EXIT`

`5S_STOCKS_V1_MULTI_SELL = FULL_EXIT`

`5S_STOCKS_V1_RISK_EXIT = NONE`

`5S_STOCKS_V1_EXECUTION = CLOSE_CONFIRMED_NEXT_REGULAR_SESSION_OPEN`

`5S_STOCKS_V1_EXTENDED_HOURS = NOT_USED`

## Validation boundary

The operating logic is frozen as the V1 reference baseline.

The following still require genuinely new forward / untouched OOS validation:
- 60% initial + W3 BUY-C top-up to 100%;
- isolated SELL-A / SELL-B half exit.

This does not reopen the rules for in-sample retuning.

## Governance

5s-stocks V1 is now the immutable stock reference control.

Do not modify 5s-stocks V1 in place.

Any future stock change must:
1. use a new experiment / version;
2. preserve 5s-stocks V1 as the control;
3. be preregistered before inspecting results;
4. use genuinely new evidence where required;
5. receive an explicit new version name if promoted.
