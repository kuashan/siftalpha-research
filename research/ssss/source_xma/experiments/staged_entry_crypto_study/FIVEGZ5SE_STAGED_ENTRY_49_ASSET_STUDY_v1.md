# FIVEGZ5SE Staged Entry Study — 39 Stocks + 10 Mainstream Crypto

Status: **IMPLEMENTED_AND_VERIFIED**

Date: 2026-09-30

## Scope

This experiment was requested to test staged entry rather than immediate 100% entry.

Entry candidates:
- initial trigger: BUY-A or BUY-B only;
- initial allocation: 50%, 60%, or 70%;
- add to 100% only if BUY-C appears after the initial A/B signal within W3 or W5;
- same-family repeat does not add;
- A->B / B->A alone does not add;
- no time-based forced exit.

Primary exit control:
- first SELL-A / SELL-B / SELL-C exits the full position.

Secondary selective-exit runs were also executed, but the BUY conclusion below is based primarily on the fixed full-first SELL control so that entry sizing is isolated.

Universe:
- 39 U.S. stocks, effective study roughly 2020-04 through 2025-12 after warm-up.
- 10 mainstream cryptocurrencies: BTC, ETH, BNB, SOL, XRP, DOGE, ADA, AVAX, LINK, TRX.
- Crypto source interval available for this study: 2021-01-03 through 2024-04-09; after 63-bar warm-up, effective start is 2021-03-07.

Total assets: **49**

The 39-stock universe and these 10 crypto assets are now development/diagnostic data for this staged-entry design and must not later be described as untouched OOS for a rule created from this study.

## 1. Does BUY-C improve accuracy as a confirmation signal?

Yes.

### W3 confirmation

Combined 49-asset baseline trades tagged by whether C appeared within 3 sessions after A/B entry signal:

C-confirmed:
- n = **117**
- mean trade = **+4.89%**
- median = **+4.83%**
- win rate = **74.36%**
- worst trade = **-22.36%**

No C confirmation:
- n = **1266**
- mean trade = **+1.41%**
- median = **+1.98%**
- win rate = **63.27%**
- worst trade = **-67.51%**

Stocks:
- C-confirmed win = **72.82%**
- unconfirmed win = **63.19%**

Crypto:
- C-confirmed win = **85.71%**
- unconfirmed win = **63.60%**

Therefore BUY-C is materially more useful as a *confirmation* after BUY-A/B than as a generic independent entry.

### W5 confirmation

C-confirmed:
- n = 167
- mean = +4.68%
- win = 74.25%

Unconfirmed:
- n = 1216
- mean = +1.30%
- win = 62.83%

W5 finds more confirmations, but W3 has the cleaner tail:
- W3 confirmed worst = -22.36%
- W5 confirmed worst = -44.07%

Decision:
`C_CONFIRMATION_WINDOW = W3_PREFERRED`

W5 remains a sensitivity result, not the preferred operating window.

## 2. 50 / 60 / 70 initial allocation — 49 assets, W3

Baseline immediate 100% entry:
- combined mean return ≈ **+61.63%**
- combined mean MDD ≈ **-41.83%**
- mean p5 trade ≈ **-13.72%**
- worst observed trade = **-67.51%**

### 50% initial, C-confirm to 100%

- mean return: **+32.88%**
- median return: **+18.47%**
- mean MDD: **-24.53%**
- MDD improved on **49/49 assets**
- mean p5 trade: **-7.09%**
- mean CVaR10: **-8.29%**
- worst observed trade: **-33.76%**
- C confirmations: 118

Versus immediate 100%:
- mean MDD improvement: **+17.30 pp**
- return improved on 20/49 assets
- return worse on 29/49

### 60% initial, C-confirm to 100%

- mean return: **+38.19%**
- median return: **+21.70%**
- mean MDD: **-28.18%**
- MDD improved on **49/49 assets**
- mean p5 trade: **-8.43%**
- mean CVaR10: **-9.77%**
- worst observed trade: **-40.51%**

Versus immediate 100%:
- mean MDD improvement: **+13.65 pp**
- return improved on 22/49
- return worse on 27/49

### 70% initial, C-confirm to 100%

- mean return: **+43.68%**
- median return: **+23.43%**
- mean MDD: **-31.75%**
- MDD improved on **49/49 assets**
- mean p5 trade: **-9.75%**
- mean CVaR10: **-11.29%**
- worst observed trade: **-47.26%**

Versus immediate 100%:
- mean MDD improvement: **+10.08 pp**
- return improved on 22/49
- return worse on 27/49

## 3. Stock-only result

W3 full-first SELL:

50%:
- mean return +33.93%
- mean MDD -20.88%
- worst trade -23.84%

60%:
- mean return +40.62%
- mean MDD -23.94%
- worst trade -28.61%

70%:
- mean return +47.78%
- mean MDD -26.94%
- worst trade -33.38%

100% baseline:
- mean return +72.48%
- mean MDD -35.66%
- worst trade -47.68%

Stocks therefore show a clear return/risk trade-off: higher initial allocation captures more upside but also progressively increases tail loss.

## 4. Crypto-only result

W3 full-first SELL:

100% baseline:
- mean return +19.31%
- median return -9.24%
- mean MDD -65.90%
- worst trade -67.51%

50%:
- mean return **+28.79%**
- median return **+8.39%**
- mean MDD **-38.74%**
- worst trade **-33.76%**
- improved return on 7/10 crypto assets

60%:
- mean return +28.68%
- mean MDD -44.75%
- worst trade -40.51%
- improved return on 7/10

70%:
- mean return +27.71%
- mean MDD -50.51%
- worst trade -47.26%
- improved return on 7/10

For this crypto sample, 50% dominates 60% and 70% on risk and is also marginally better on mean return.

This is important because crypto volatility makes immediate full allocation especially costly in adverse trades.

## 5. W3 vs W5

W5 produces more confirmations:
- W3 combined confirmations: 118
- W5 combined confirmations: 168

But the extra confirmations do not materially improve accuracy:
- W3 confirmed win: 74.36%
- W5 confirmed win: 74.25%

And W5 has a materially worse confirmed-tail observation.

Therefore the wider window adds quantity more than quality.

`W3 = PREFERRED`

## 6. Operating interpretation

The data does **not** support returning to a mechanical 1/3 + 1/3 + 1/3 pyramid.

It does support a two-stage model:

```
First valid BUY-A or BUY-B
    -> open partial position

If BUY-C appears within next 3 trading sessions
    -> add remaining allocation to reach 100%

If BUY-C does not appear within W3
    -> do not add later
    -> keep the original partial position until SELL logic acts

Repeated A/A, B/B, A/B or B/A
    -> record only
    -> no add
```

## 7. Which initial size?

There is no mathematically unique optimum because 50/60/70 form a smooth risk/return frontier.

However, once crypto is included, the evidence favors **50% as the next candidate** if the design objective is specifically to avoid one-shot full-position risk:

- largest MDD reduction;
- best p5/CVaR tail protection;
- smallest worst trade;
- all 49 assets improve MDD;
- crypto mean return is actually highest at 50% among 50/60/70;
- C confirmation itself has materially higher accuracy than unconfirmed entries.

60% is a reasonable compromise candidate if greater stock upside capture is desired.

70% is closer to the old full-size behavior and gives up a substantial part of the risk reduction.

Research decision:

`INITIAL_ENTRY_50 = PROMOTED_TO_NEXT_VALIDATION`

`INITIAL_ENTRY_60 = RETAINED_AS_SENSITIVITY`

`INITIAL_ENTRY_70 = RETAINED_AS_SENSITIVITY`

`C_CONFIRM_WITHIN_W3_TO_FULL = PROMOTED_TO_NEXT_VALIDATION`

`C_CONFIRM_W5 = NOT_PREFERRED`

`SAME_FAMILY_REPEAT_ADD = REJECTED_NOT_ADMITTED`

`A_B_CROSS_WITHOUT_C_ADD = REJECTED_NOT_ADMITTED`

This is a candidate operating design, not yet a frozen production rule.

## 8. Data files

Raw computed experiment results are archived as:
- stock_batch1_v1.json
- stock_batch2_v1.json
- stock_batch3_v1.json
- crypto_batch_v1.json

The exact experiment code is:
- fivegz5se_staged_entry_experiment_v1.js

Summary files:
- FIVEGZ5SE_STAGED_ENTRY_49_ASSET_SUMMARY_v1.csv
- FIVEGZ5SE_STAGED_ENTRY_49_ASSET_PER_ASSET_v1.csv
- FIVEGZ5SE_C_CONFIRMATION_ACCURACY_v1.csv

Closure:

`FIVEGZ5SE_STAGED_ENTRY_49_ASSET_STUDY_V1 = IMPLEMENTED_AND_VERIFIED`
