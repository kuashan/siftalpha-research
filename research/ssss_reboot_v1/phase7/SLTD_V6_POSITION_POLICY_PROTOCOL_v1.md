# SLTD V6 Position Policy Study v1 — Frozen Protocol

Status: **FROZEN BEFORE OUTCOME RUN**
Date: 2026-10-02

## Objective

Determine a practical, data-supported Position Execution Policy (仓位执行规则)
for the already-official SLTD V6 15-rule action taxonomy.

This study does **not** modify:
- XMA formulas;
- FIRST_OBSERVED point-in-time reconstruction;
- state/color definitions;
- rail/event definitions;
- the official 15 BUY/HOLD/WAIT/SELL rules.

Only the mapping from formal actions to position size / position change is studied.

## Causal XMA requirement

SLTD V6 is an XMA structure. Historical backtesting must therefore use
FIRST_OBSERVED reconstruction only.

At bar t:
1. use only data available through t;
2. recompute the finite-history XMA right edge;
3. persist the state / rails / event visible at t;
4. never replace that historical observation with a later fully rendered rail.

Trading execution:
- signal is confirmed at the close of bar t;
- any position change executes at the next available bar open;
- no same-close execution;
- no future-repainted XMA history.

## Study universe

### Stock Batch 1 — 10
AAPL, MSFT, NVDA, AMD, AVGO, ORCL, INTC, QCOM, MU, GOOGL

### Stock Batch 2 — 10
META, NFLX, AMZN, TSLA, HD, MCD, WMT, COST, PG, KO

### Stock Batch 3 — 10
PEP, ABT, LLY, UNH, JNJ, TMO, JPM, BAC, GS, V

### Stock Batch 4 — 9
MA, CAT, BA, GE, XOM, CVX, LIN, NEE, PLD

### Stock Batch 5 — 10
IBM, CSCO, CRM, ADBE, TXN, DIS, NKE, SBUX, TGT, LOW

### Stock Batch 6 — 10
MRK, PFE, ABBV, AMGN, GILD, C, MS, BLK, COP, UPS

### Stock Batch 7 — 10
ACN, NOW, INTU, AMAT, LRCX, BKNG, TJX, CMG, ROST, MAR

### Stock Batch 8 — 10
DHR, SYK, MDT, BMY, ISRG, SCHW, SPGI, DE, HON, RTX

Total stocks = 79.

### Batch 9 — Crypto transfer
BTC, ETH, BNB, SOL

Crypto is a transfer test and may not be used to retune the stock policy.

## Time window

Formal performance window:

2020-01-02 through 2026-09-30.

Warm-up:
- stocks: request from 2010-01-04 where available;
- crypto: request from 2016-01-01 where available;
- earlier bars are warm-up only;
- if a crypto asset lacks pre-2020 history, at least the first 180 returned daily bars are warm-up before it becomes eligible.

## Data inputs

Stocks:
- daily raw OHLCV;
- Yahoo Finance / yfinance;
- auto_adjust = false;
- end date requested as 2026-10-01 exclusive.

Crypto:
- Binance Spot daily UTC OHLCV through CCXT;
- BTC/USDT, ETH/USDT, BNB/USDT, SOL/USDT;
- normalized research labels BTC, ETH, BNB, SOL.

The workflow freezes a local research snapshot and writes a SHA-256 manifest.
All batch calculations in this study must use that fixed snapshot.

## Canonical SLTD V6 structure

Fast inner rails:
- VL25 = XMA(XMA(L,25),25)
- VH25 = XMA(XMA(H,25),25)
- ZD1 = VL25 - (VH25 - VL25)
- ZK1 = VH25 + (VH25 - VL25)

Slow weighted light-gray band:
- W_H = weighted 20..1 high series / 210
- W_L = weighted 20..1 low series / 210
- GZB3 = EMA(W_H,90)
- GZB4 = EMA(W_L,90)
- GZB7 = GZB3 - GZB4
- GZB8 = GZB3 + 2*GZB7
- GZB9 = GZB4 - 2*GZB7

State:
- BLUE = ZD1 >= GZB9 and ZK1 >= GZB8
- GREEN = ZK1 <= GZB8 and ZD1 <= GZB9
- GRAY = ZD1 >= GZB9 and ZK1 <= GZB8
- otherwise EXPANSION

Outer rails:
- BS = VH60 + 2.2*(VH60-VL60)
- BD = VL60 - 2.8*(VH60-VL60)

## Frozen event definitions

LOWER:
- current Low < current FIRST_OBSERVED ZD1;
- previous Low was not already below previous FIRST_OBSERVED ZD1.

LOWER subtype:
- WICK_ONLY: Low < ZD1 and Close >= ZD1
- CLOSE_BELOW: Close < ZD1 and High >= ZD1
- FULL_BELOW: High < ZD1

UPPER:
- current High > current FIRST_OBSERVED ZK1;
- previous High was not already above previous FIRST_OBSERVED ZK1.

UPPER subtype:
- WICK_ONLY: High > ZK1 and Close <= ZK1
- CLOSE_ABOVE: Close > ZK1 and Low <= ZK1
- FULL_ABOVE: Low > ZK1

LIGHT_SUPPORT:
- prior Close > prior GZB3;
- current bar intersects [GZB4, GZB3].

LIGHT_RESIST:
- prior Close < prior GZB4;
- current bar intersects [GZB4, GZB3].

## Formal 15-rule action map

BUY:
1. BLUE 21+ + LOWER
2. GRAY 4-10 + LIGHT_SUPPORT
3. recent BLUE->GRAY + LIGHT_SUPPORT
4. BLUE 11-20 + LOWER WICK_ONLY
5. GRAY 4-10 + LOWER WICK_ONLY

HOLD:
6. BLUE 11-20 + UPPER
7. BLUE 4-10 + UPPER
8. recent GRAY->BLUE + UPPER
9. BLUE 21+ + UPPER CLOSE_ABOVE

WAIT:
10. GREEN 11-20 + LOWER
11. GREEN 11-20 + LOWER CLOSE_BELOW

SELL:
12. recent BLUE->GRAY + LIGHT_RESIST
13. GREEN 4-10 + UPPER
14. GREEN 11-20 + UPPER WICK_ONLY
15. GREEN 11-20 + LIGHT_RESIST

## Position-policy discovery grid

Stage A searches a global execution policy without changing rule definitions.

### Initial BUY target
25%, 40%, 50%, 60%, 70%, 100%.

### Subsequent BUY while already long
- IGNORE
- ADD_25_TO_CAP
- ADD_ENTRY_TO_CAP
- TOPUP_TO_100

All position fractions are capped at 100%.

### SELL reduction
25%, 50%, 75%, 100% of the current position.

### WAIT behavior while already long
- HOLD
- TRIM_25
- TRIM_50
- EXIT_100

When flat, WAIT always blocks a new entry on that bar.

### Mixed-action same-bar resolution
Three preregistered variants:
- SELL_FIRST: SELL > WAIT > BUY > HOLD
- WAIT_FIRST: WAIT > SELL > BUY > HOLD
- NO_CHANGE_MIXED: if more than one action class is present, make no position change

Same-class multiple rules are treated as one action-class event in Stage A.

## Execution and friction

Long / cash only.
No leverage.
No short selling.
No intraday lookahead.

Signal close -> next available open.

Baseline adverse friction:
- 5 bps on each position turnover.

Stress:
- 10 bps on each position turnover.

Sample-end open position:
- mark to market at the final eligible close.

## Discovery / validation discipline

Batches 1-4 (original 39 stocks):
- discovery / ranking only.

After Batch 4:
- rank policies;
- freeze Primary + four Backup candidates in discovery order;
- do not retune their parameters from later batches.

Batches 5-8 (40 later stocks):
- validation only.

Final stock policy selection:
- choose the first candidate in the frozen discovery order that meets all validation gates;
- if none pass, return NO_POLICY_PROMOTED and do not invent a new policy from validation data.

Batch 9:
- crypto transfer check only;
- may support or contradict transferability;
- cannot modify the stock-selected policy.

## Primary selection objective

Policy ranking is lexicographic, not a single opaque score.

Discovery ranking priority:
1. higher median batch Calmar;
2. higher worst-batch Calmar;
3. higher median batch CAGR;
4. lower median batch Max Drawdown;
5. lower between-batch Calmar dispersion;
6. lower turnover when the above are tied.

This prevents highest raw return alone from deciding the policy.

## Validation gates

A frozen candidate passes stock validation only if:
- at least 3 of 4 validation batches have Calmar > 0;
- median validation-batch Calmar > 0;
- median validation-batch CAGR > 0;
- the 10 bps stress test also has median validation-batch Calmar > 0;
- no validation batch has Max Drawdown worse than -60%.

These are admission gates, not optimization targets.

## Required metrics

For every candidate and batch:
- total return;
- CAGR;
- Max Drawdown;
- Calmar;
- turnover;
- number of position changes;
- time in market.

For promoted / frozen shortlist candidates additionally:
- trade count;
- win rate;
- median trade return;
- P5 trade return;
- CVaR 5% trade return;
- average holding period;
- per-symbol metrics;
- per-batch consistency;
- 5 bps baseline vs 10 bps stress.

## Rule-aware refinement

Only after the Stage A Primary + Backups are frozen may a separate Stage B
rule-aware refinement be opened.

Stage B is not allowed to silently change Stage A results.
Any Stage B refinement must be separately preregistered before inspecting its
outcomes.

This v1 run first establishes the robust global Position Execution Policy.

## Batch closure discipline

Each batch must:
1. use the frozen data snapshot;
2. compute from FIRST_OBSERVED;
3. write machine-readable outputs;
4. write a human summary;
5. be marked COMPLETE before the next batch is accepted.

After Batch 9:
- write final position-policy result;
- record whether a stock policy was promoted;
- record crypto transfer behavior;
- leave the SLTD V6 15-rule taxonomy unchanged.

`SLTD_V6_POSITION_POLICY_STUDY_V1_PROTOCOL = FROZEN`
