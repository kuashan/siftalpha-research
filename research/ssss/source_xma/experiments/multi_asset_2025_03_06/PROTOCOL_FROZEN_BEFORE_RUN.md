# March–June 2025 Multi-Asset Protocol

Status: FROZEN BEFORE RUN  
Frozen: 2026-09-28

## Study window

- Stocks: 2025-03-03 through 2025-06-30
- Crypto: 2025-03-01 through 2025-06-30
- Capital continuity: one continuous March–June path; no monthly reset.
- Nominal initial capital: $10,000 **per symbol research sleeve**.
- Fractional units allowed.
- Commission: $0.
- Slippage: 5 bps one way.

This is still signal/position research, not a shared $10,000 portfolio. A shared-capital portfolio is a later stage.

## Universe

### US-listed equities
ABT, AAPL, AMZN, ORCL, INTC, MSFT, NVDA, GOOGL, META, JPM, XOM

ARM remains in the Discovery universe but is not silently included until a sufficiently verified **daily** OHLCV source is available. Weekly summaries are not enough for this model.

### Crypto
- BTCUSDT
- ETHUSDT
- BNBUSDT
- SOLUSDT

Crypto source convention: Binance spot USDT daily bars.

## Market branches

### FIVEGZ5SE
- equities: SCTYPE=1
- crypto: SCTYPE=2

These source branches are reproduced for this run, but are **not assumed optimal**.

### HYS2
- equities: SCQH=1
- crypto: SCQH=2

Again, source branch selection is a reproduction choice, not a claim of optimality.

## Execution model

Primary execution model:

`SAME_BAR_CLOSE_PROXY_V2`

Reason:
the research objective is that when the **current** daily bar has satisfied the complete trading rule, the action belongs to that bar rather than being mechanically delayed to the next bar.

With daily-only historical data, exact intrabar first-confirm time is not observable.

Therefore this run uses:
- signal computed from the completed current daily bar,
- execution proxy = current bar close,
- 5 bps adverse slippage.

This is explicitly a **proxy for same-bar current-K execution**, not a claim that the final official close was known before it occurred.

A smaller sensitivity audit may compare against legacy next-open execution, but NEXT_OPEN is no longer the primary model.

## Source-XMA remains primary

SSSS + ADKBY-E are one Source-XMA system.

No DEMA/EMA substitution.

For every study bar:
- recompute point-in-time using only data through the current bar,
- preserve first-observed XMA values,
- do not use later-repainted XMA history for the decision.

## FIVEGZ color-state interpretation

Ignore display words such as:
- 清仓
- 抄底
- 主升
- 逃顶

Use raw state transitions.

Numerical state map:

```text
SHORT / GREEN             = -2
LIGHT_SHORT / LIGHT_GREEN = -1
GRAY                      =  0
LIGHT_LONG / LIGHT_RED    = +1
LONG / RED                = +2
```

Per bar record:
- five individual states,
- total score,
- score delta,
- count improving,
- count deteriorating.

A red -> light-red transition means deterioration, not an automatic sell.

## Frozen rules — MARJUN_XMA_v2

### Flat: normal probe

Allow a 20% long probe if:
- XMA regime != BEAR,
- lower extreme occurs:
  - source lower cross OR normalized low-position < 20,000,
- no active cooldown.

### Flat: transition override

Allow a 15% counter-regime long probe even when XMA regime == BEAR only if ALL are true:
- HYS2 resonance == true,
- FIVEGZ total score >= +6,
- FIVEGZ score delta >= +6,
- relative volume >= 1.50.

This is a small reversal probe only.

### Confirmation

If a probe exists and:
- close > FastMid,
- XMA momentum == BOTH_UP,

raise target to 60%.

HYS2 resonance or a low-side fire impulse may add 10 percentage points.

### Breakout

If:
- close > FastUpper,
- XMA momentum == BOTH_UP,
- relative volume >= 1.50,

target = 80%.

If FIVEGZ score >= +6:
target may rise to 100%.

### Position deterioration

FIVEGZ sizing adjustment:
- score >= +6: permits +15 percentage points, capped at 100%.
- score <= -3: subtract 20 percentage points.
- score delta <= -3 while long: subtract an additional 15 percentage points on a reduction event.

### XMA reduce

If:
- normalized close-position > 120,000,
- current XMA momentum-sum < previous bar momentum-sum,

reduce 25 percentage points.

If FIVEGZ score remains >= +6 and no previous suppression has been used in the current leg:
- suppress this reduction once.

### Hard exit

Exit to 0% if ANY:
- XMA regime == BEAR and no Transition Override is active,
- close < FastMid AND XMA momentum != BOTH_UP,
- slow XMA momentum delta < 0 AND normalized close-position > 80,000.

### Failed-probe cooldown

If a probe is exited before it ever reaches >= 60% confirmed exposure:
- start a 3-bar cooldown for that symbol.
- no new normal probe during cooldown.
- Transition Override may break cooldown only if all override conditions are satisfied.

For stocks, a bar means a trading session.
For crypto, a bar means a UTC daily bar.

## Shorting

No automatic short-entry rule is enabled.

Bearish evidence can produce:
- smaller long size,
- exit,
- remain flat.

A short position requires separate evidence and is not forced merely because a source indicator prints a high-side or sell-like state.

## Candidate variants

A. `XMA_ONLY_V2`
- only XMA rules + cooldown + transition override uses XMA/rvol but HYS2/FIVEGZ override disabled

B. `XMA_HYS2_V2`
- HYS2 selective low-side confirmation enabled
- no global high-side short interpretation

C. `XMA_FIVEGZ_V2`
- FIVEGZ raw color score modifies size/risk
- text labels ignored

D. `XMA_HYS2_FIVEGZ_V2`
- both candidate layers enabled

## Evaluation

Do not choose a combination by gross profit alone.

Record:
- total March–June return,
- max drawdown,
- average exposure,
- number of executions,
- profitable symbols,
- worst-symbol outcome,
- behavior by asset class,
- repeated-probe count,
- Transition Override events,
- false-breakout / gap-risk observations.

No result from this window can retroactively alter this frozen protocol.
