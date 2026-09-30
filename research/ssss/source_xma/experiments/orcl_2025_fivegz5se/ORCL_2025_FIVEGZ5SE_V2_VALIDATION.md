# ORCL 2025 FIVEGZ5SE V2 Signal-Only Validation

Status: **EXTERNAL_TEST_RESULT_RECORDED**

Date: 2026-09-29

## 1. Data

- Symbol: ORCL (Oracle)
- Source: Devesh176/Replicating_portfolio `data/ORCL.csv`
- Source blob SHA: `09ac3f0ada8c73f16758a0ef34b5afaa327a9a1c`
- Period: 2025-01-02 through 2025-12-31
- Sessions: 250
- SCTYPE=1

## 2. Frozen rule

No time cap.

Entry:
```
onset(BUY-A) OR onset(BUY-B)
```

Same-bar SELL vetoes entry.

Exit:
```
onset(SELL-A) OR onset(SELL-B) OR onset(SELL-C)
```

Execution:
- signal at close t;
- next-session open execution;
- 5 bps adverse slippage each side.

## 3. Result

- initial capital: $10,000.00
- final marked value: **$17644.61**
- cumulative return: **76.45%**
- maximum drawdown: **-13.04%**
- annualized daily Sharpe: **1.57**
- closed trades: **3**
- closed-trade win rate: **100.00%**
- mean closed trade: **21.33%**
- median closed trade: **22.31%**
- exposure: **19.20%**

ORCL 2025 buy-and-hold with same 5 bps entry/exit slippage:
- return: **15.54%**
- maximum drawdown: **-45.65%**

## 4. Signal counts

- BUY-A onsets: 5
- BUY-B onsets: 0
- SELL-A onsets: 9
- SELL-B onsets: 6
- SELL-C onsets: 7
- same-bar BUY/SELL conflicts: 0

## 5. Closed trades

| Signal | Entry | Exit | Hold | Return | Exit |
|---|---|---|---:|---:|---|
| 2025-01-13 | 2025-01-14 | 2025-01-22 | 5 | 22.31% | S3 |
| 2025-06-24 | 2025-06-25 | 2025-07-11 | 11 | 7.54% | S2 |
| 2025-07-25 | 2025-07-28 | 2025-09-11 | 32 | 34.15% | S3 |

## 6. Interpretation

The frozen no-time-cap V2 path was profitable on ORCL 2025.

However:
- only 3 trades were completed;
- BUY-B produced zero onsets in ORCL 2025;
- the result is concentrated in a very small number of trades.

Therefore this single-symbol result is **supportive but not statistically sufficient**.

It does not reverse the ABT 2025 failure and does not by itself admit V2 as a
general rule.

The daily audit file for all 250 sessions is stored beside this report:

`ORCL_2025_FIVEGZ5SE_V2_DAILY_AUDIT.csv`

That file contains:
- OHLCV;
- five dimension states;
- BUY-A / BUY-B onset flags;
- SELL-A / SELL-B / SELL-C onset flags;
- position state;
- executed action;
- portfolio value.

Research state:

`ORCL_2025_FIVEGZ5SE_V2_NO_TIME_CAP = POSITIVE_EXTERNAL_RESULT`

Not yet:

`V2_GENERALIZATION_PASS`
