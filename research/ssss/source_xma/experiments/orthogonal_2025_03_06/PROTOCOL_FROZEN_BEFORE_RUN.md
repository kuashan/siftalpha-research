# Orthogonal-Feature March–June 2025 Protocol

Status: FROZEN BEFORE ORTHOGONAL RUN  
Frozen: 2026-09-28

## Important research status

This is **exploratory**, not OOS.

March–June 2025 price history has already been inspected in prior experiments.  
The purpose of this run is not to claim unbiased performance. It is to test whether orthogonal market information adds more stable value than stacking additional price-derived indicators.

## Window and XMA chronology

Stocks:
- evaluation starts 2025-03-03
- ends 2025-06-30

Crypto:
- evaluation starts 2025-03-01
- ends 2025-06-30

**Hard rule:** Source-XMA is recomputed from the first evaluation bar forward, one bar at a time.

For every date t:
1. only bars available through t are supplied to XMA;
2. the first-observed right-edge XMA value is used;
3. later-repainted historical XMA values are never substituted into the decision;
4. the action is assigned to the current bar.

Execution proxy:
- SAME_BAR_CLOSE_PROXY_V3
- current-bar close + 5 bps adverse slippage
- daily data cannot identify exact intraday first-confirm time.

## Capital

$10,000 nominal initial research sleeve per traded symbol.  
Capital is continuous March -> June.  
No monthly reset.  
No shorting in this run.

## Traded universe

Stocks:
ABT, AAPL, AMZN, ORCL, INTC, MSFT, NVDA, GOOGL, META, JPM, XOM

Crypto:
BTCUSDT, ETHUSDT, BNBUSDT, SOLUSDT

ARM remains pending verified daily OHLCV.

## Core XMA baseline

SSSS + ADKBY-E remain one Source-XMA system.

No HYS2 or FIVEGZ state is allowed to change a trade in this run.

They may remain in diagnostic files only.

### XMA-only actions

Flat:
- lower extreme and regime != BEAR -> 20% PROBE_LONG
- close > FastUpper and BOTH_UP -> 70% BREAKOUT_ENTRY

Long:
- after probe, close > FastMid and BOTH_UP -> 60% CONFIRM_LONG
- close > FastUpper and BOTH_UP -> 80% BREAKOUT_ADD
- normalized close position > 120000 and XMA momentum sum decelerates -> reduce 25 percentage points
- hard exit if:
  - regime == BEAR, OR
  - close < FastMid and momentum != BOTH_UP, OR
  - slow XMA momentum delta < 0 and normalized close position > 80000

Failed probe:
- fixed 3-bar cooldown in the baseline state machine.

No volume, VIX, breadth, or Volume Profile is required by XMA_ONLY.

## Orthogonal auxiliary factors

### 1. Volume Structure

Inputs:
- RVOL20 = volume / MA20(volume)
- signed-volume balance over 5 bars
- accumulation day
- distribution day

Definitions:

```text
signed_volume_5 =
sum(sign(close_t-close_{t-1}) * volume_t, 5)
/
sum(volume_t, 5)
```

Positive volume context:
- accumulation day: return > 0 and RVOL20 >= 1.30
OR
- signed_volume_5 > +0.15 and RVOL20 >= 0.90

Negative volume context:
- distribution day: return < 0 and RVOL20 >= 1.50
OR
- signed_volume_5 < -0.20 and RVOL20 >= 1.00

Otherwise neutral.

### 2. VIX risk/sentiment context

VIX is used as a risk-sentiment variable, not as a buy/sell indicator.

Positive:
- VIX below its 20-day mean
- AND 5-day VIX change <= -5%

Negative:
- VIX >= 1.15 * VIX_MA20
OR
- 5-day VIX change >= +15%

Otherwise neutral.

For crypto it is retained as a global cross-asset risk proxy, not assumed optimal.

### 3. Market Breadth proxy

US-equity breadth source:
- 100-name frozen OHLCV sample from Devesh176/Replicating_portfolio
- exact list in BREADTH_UNIVERSE.txt

This is **not claimed to be official S&P 500 breadth**.

Daily breadth:
- % advancing vs prior close
- % above MA20
- % with positive 5-day return

Positive breadth:
- all three >= 55%

Negative breadth:
- all three <= 45%

Otherwise neutral.

SPY / QQQ context is also recorded but not used to fabricate official breadth.

Crypto breadth proxy:
- BTC / ETH / BNB / SOL
- % above MA20
- % with positive 5-day return
- % advancing
- positive if >= 75% in all three
- negative if <= 25% in all three
- otherwise neutral

### 4. Daily Volume Profile proxy

This is explicitly a **proxy**, not exact intraday Volume Profile.

For each symbol, use only the prior/current 60 daily bars.

Each day's volume is assigned to its typical price:

```text
typical_price = (high + low + close) / 3
```

Across 24 rolling price bins:
- POC = highest-volume bin
- Value Area = contiguous bins expanded from POC until 70% of rolling volume is included
- VAL / VAH = lower / upper edge of that area

Positive profile context:
- close > VAH

Negative:
- close < VAL

Neutral:
- close inside Value Area

This proxy is tested separately because daily OHLCV cannot reconstruct real intraday price-by-volume.

## Sizing logic for auxiliary variants

Base XMA signal determines direction and timing.

For each enabled factor:
- positive = +1
- neutral = 0
- negative = -1

Combined context score = sum enabled factors.

For a new XMA entry/add:
- score <= -2: suppress the new entry/add
- score == -1: execute at 50% of the XMA target
- score == 0: use XMA target
- score == +1: XMA target + 10 percentage points
- score >= +2: XMA target + 20 percentage points
- cap 100%

Auxiliary factors never create an independent long signal.

For an existing long:
- auxiliary score alone cannot force a full exit
- on an XMA reduction:
  - score <= -2: reduce an extra 15 percentage points
  - score >= +2: reduce 10 percentage points less
- XMA hard exit always wins.

## Frozen variants

A. XMA_ONLY  
B. XMA_VOLUME  
C. XMA_VIX  
D. XMA_BREADTH  
E. XMA_VOLPROFILE  
F. XMA_VOLUME_BREADTH  
G. XMA_VOLUME_BREADTH_VIX  
H. XMA_ORTHO_ALL = Volume + Breadth + VIX + Volume Profile

## Required outputs

For each variant:
- total return
- max drawdown
- number of positive symbols
- median return
- worst symbol
- number of trades
- average exposure

Also record:
- factor state on every XMA signal
- signals suppressed by auxiliary context
- cases where auxiliary factors improved or harmed outcome
- stock vs crypto separation

No rule may be changed after this file is committed.
