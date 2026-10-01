# SSSS Crypto V1 Baseline

Status: **FROZEN_BASELINE**

Frozen date: 2026-10-01
Branch: `research/source-xma-walkforward`
Parent research state: `699c4f7a65ae22b9613006a2c4185207e162378a`

## Name

**Crypto V1**

This is the first frozen Crypto baseline for the current SSSS three-buy / three-sell framework.

## Validated development universe

- BTC
- ETH
- BNB
- SOL

Current evidence base uses Binance Spot UTC **1d OHLCV**.

Important:
Crypto V1 is frozen from the daily-bar research evidence above.
The execution principle is timeframe-independent, but 4h / 1h / 15m are **not automatically validated by Crypto V1** and require their own validation before being called Crypto V1-equivalent.

## Frozen BUY rules

- BUY-A or BUY-B -> enter **60%** at the next bar open.
- If BUY-C onsets within W3 after the initial BUY-A/B -> add the remaining **40%** at the next bar open, reaching 100%.
- BUY-C cannot independently open a position.
- No A/A or B/B repeat add.
- No A->B or B->A add.
- No W5 BUY-C top-up.

## Frozen SELL rules

- SELL-A -> exit **100%** at the next bar open.
- SELL-B -> exit **100%** at the next bar open.
- SELL-C -> exit **100%** at the next bar open.
- Same-bar multi-family SELL -> exit **100%**.

SELL-C 25% / 50% / 75% partial exits were tested and rejected for V1 because each worsened P5 / CVaR tail-loss behavior despite higher historical mean return.

## Frozen execution semantics

**Close Confirmed -> Next Bar Open Execution**

That means:
- the current bar must fully close before a BUY / SELL signal exists;
- the order executes at the next bar open;
- there is no additional fixed 24-hour waiting period;
- 5 bps adverse slippage is used per transaction in the frozen research model;
- long / cash only;
- no time-based forced exit;
- sample-end open positions are mark-to-market.

For the current daily Binance baseline:
- signal is confirmed on the completed UTC daily bar;
- execution occurs at the next UTC daily bar open.

## Risk Exit

No independent Risk Exit layer is part of Crypto V1.

Rejected / not admitted:
- universal fixed Hard Stop;
- universal fixed Trailing Stop;
- combined fixed hard + trailing grid;
- tested State / Volatility-Aware Risk Exit v1.

`CRYPTO_RISK_EXIT = NOT_USED_RETAIN_BASELINE`

## Frozen state

`CRYPTO_V1 = FROZEN_BASELINE`

`CRYPTO_V1_BUY = 60_INITIAL_PLUS_W3_C_TO_100`

`CRYPTO_V1_SELL_A = FULL_EXIT`

`CRYPTO_V1_SELL_B = FULL_EXIT`

`CRYPTO_V1_SELL_C = FULL_EXIT`

`CRYPTO_V1_RISK_EXIT = NONE`

`CRYPTO_V1_EXECUTION = CLOSE_CONFIRMED_NEXT_BAR_OPEN`

## Governance

Crypto V1 is now the reference baseline.

Do not modify Crypto V1 in place.

Any future Crypto change must:
1. use a new experiment / version;
2. preserve Crypto V1 as the control;
3. be preregistered before inspecting results;
4. use genuinely new evidence where required;
5. receive an explicit new version name if promoted.
