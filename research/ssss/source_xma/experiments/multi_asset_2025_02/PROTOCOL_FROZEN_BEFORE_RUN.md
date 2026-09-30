# Multi-Asset February 2025 Protocol

Status: FROZEN BEFORE RUN  
Frozen: 2026-09-28

## Window

- Study month: 2025-02-03 through 2025-02-28
- Daily bars
- Indicators may use all history available before 2025-02-03 as warm-up.
- Each symbol starts the February paper account flat with nominal $10,000.
- Signals are decided after the daily close and executed at the next tradable open.
- Fractional shares allowed.
- Commission = $0.
- One-way slippage = 5 bps.
- Open positions at month-end are marked to the 2025-02-28 close.

## Universe

Primary February run:
- ABT
- AAPL
- AMZN
- ORCL
- INTC
- MSFT
- NVDA
- GOOGL
- META
- JPM
- XOM

ARM is kept in the research universe but is not included in the first February batch until an independently verifiable daily OHLCV source is established.

## Core principle

SSSS + ADKBY-E are treated as one Source-XMA core.

The primary structure remains:
- double XMA(25) high/low channel
- source slow structure
- regime
- first-observed point-in-time values
- source momentum components

No DEMA/EMA substitution is allowed in this Source-XMA track.

## FIVEGZ5SE interpretation

Do not trust display words or comments such as:
- 清仓
- 抄底
- 底部
- 主升
- 逃顶

Use the actual raw state dimensions only.

Color/state order:

```text
GREEN / SHORT = -2
LIGHT_GREEN / LIGHT_SHORT = -1
GRAY = 0
LIGHT_RED / LIGHT_LONG = +1
RED / LONG = +2
```

A transition such as RED -> LIGHT_RED is deterioration but not an automatic sell.

For each day record:
- trend state
- capital state
- momentum state
- acceleration state
- anomaly state
- five-state score
- day-over-day score delta
- number of dimensions improving
- number of dimensions deteriorating

The 0/1/2 market switch inside the source is not assumed to be optimal. For US equities this run reproduces the source US branch as written, but treats the branch choice itself as a future research variable.

## HYS2 interpretation

HYS2 remains auxiliary:
- low-side fire-mountain impulse
- stochastic/MACD resonance
- bull/bear crosses
- high-side fire-mountain state

No HYS2 label automatically buys, sells, or shorts.

## Frozen XMA action engine — FEB_XMA_v1

### Flat state

1. Lower-extreme probe:
   - regime != BEAR
   - AND (source lower cross OR normalized low position < 20,000)
   - target = 25%
   - open a 3-session WATCH_LONG window

2. Reversal confirmation:
   - WATCH_LONG active
   - close > XMA FastMid
   - BOTH_UP source momentum
   - target = 65%

3. Independent breakout entry:
   - regime != BEAR
   - close > FastUpper
   - BOTH_UP momentum
   - RVOL20 >= 1.50
   - target = 70%

### Existing long

4. Breakout add:
   - close > FastUpper
   - BOTH_UP momentum
   - RVOL20 >= 1.50
   - target = 100%

5. Extreme deceleration reduce:
   - normalized close position > 120,000
   - current (momentum_fast_delta + momentum_slow_delta)
     < previous session's sum
   - reduce target by 30 percentage points, floor 40%

6. Exit:
   Any of:
   - regime == BEAR
   - close < FastMid AND momentum != BOTH_UP
   - slow momentum delta < 0 AND normalized close position > 80,000

   target = 0%

No automatic short entry is enabled in this February protocol.

## Candidate combination variants

### A — XMA_ONLY
Use FEB_XMA_v1 targets unchanged.

### B — XMA_HYS2
XMA decides direction/timing.
HYS2 only changes confidence sizing:
- recent low-side fire impulse or current resonance on reversal confirmation: +10 percentage points
- generic HYS2 cross without XMA setup: no action
- high-side fire state: never creates a short

### C — XMA_FIVEGZ
XMA decides direction/timing.
FIVEGZ5SE raw color states modify target size:
- five-state score >= +6: +15 percentage points
- five-state score <= -3: -20 percentage points
- score delta <= -3 while long: extra -15 percentage points on a reduce event
- score >= +6 may suppress one XMA extreme-deceleration reduction once, but cannot suppress a hard XMA exit

### D — XMA_HYS2_FIVEGZ
Apply both auxiliary sizing rules.
Caps:
- long exposure min 0%
- max 100%

## Evaluation

Do not choose a candidate by total profit alone.

Record:
- mean return
- median return
- number of positive symbols
- worst symbol return
- mean max drawdown
- median max drawdown
- number of executed trades
- average exposure
- relative behavior against XMA_ONLY

Any "best" result is valid only for this exploratory February Discovery run and is not promoted to production.
