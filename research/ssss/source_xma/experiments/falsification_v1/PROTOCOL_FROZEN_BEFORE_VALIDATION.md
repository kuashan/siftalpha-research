# Canonical XMA Falsification Protocol v1

Status: FROZEN BEFORE HOLDOUT OUTCOME ANALYSIS
Date: 2026-09-28

## 1. Purpose

The research now switches from **effect discovery** to **effect falsification**.

The Jan–Jun 2025 canonical geometry study remains Discovery only.

No threshold discovered there may be changed inside the holdout tests.

The objective is to try to disprove:

1. strict upper fast/outer confluence has incremental bearish/exhaustion information;
2. strict lower fast/outer confluence has delayed reversal/dislocation information;
3. lower confluence below Value Area has incremental value;
4. state transitions and analytic midpoint events add lifecycle information;
5. HYS2 has any incremental interaction beyond the XMA geometry itself.

## 2. Formula baseline — immutable

Canonical v1 only:

- corrected W20 high/low channel:
  lags 0..19, weights 20..1, denominator 210;
- GZB2 lag-11 uses LOW;
- point-in-time XMA25 and XMA60;
- no future repaint may overwrite an earlier bar.

## 3. Frozen geometry definitions

### Upper strict confluence

```text
exclusive state = UP
candle overlaps both ZK1 and BS
abs(ZK1 - BS) <= 0.25 * ATR14
```

Episode rule:
- repeated same-symbol qualifying bars within 3 trading bars are one episode;
- the first bar is the event date.

### Lower strict confluence

```text
exclusive state = DOWN
candle overlaps both ZD1 and BD
abs(ZD1 - BD) <= 0.50 * ATR14
```

Same episode rule.

No threshold may be tuned after holdout results.

## 4. Holdout windows

### Validation A — untouched historical holdout

Equities:
2020-01-02 through 2024-12-31

Crypto:
2020-01-01 through 2024-12-31 where source data exist.

Purpose:
large independent historical sample.

This is an untouched temporal holdout, but not prospective because it occurs before the 2025 discovery window.

### Validation B — forward holdout

2025-07-01 through 2025-12-31.

Purpose:
forward temporal validation after the Jan–Jun 2025 discovery window.

### Sealed future window

2026-01-01 through 2026-06-30 is NOT used in Validation A/B.

It remains reserved for Validation v2.

## 5. Frozen equity universe

39 liquid, widely recognized US equities across sectors:

Technology:
AAPL, MSFT, NVDA, AMD, AVGO, ORCL, INTC, QCOM, MU

Communication Services:
GOOGL, META, NFLX

Consumer Discretionary:
AMZN, TSLA, HD, MCD

Consumer Staples:
WMT, COST, PG, KO, PEP

Health Care:
ABT, LLY, UNH, JNJ, TMO

Financials:
JPM, BAC, GS, V, MA

Industrials:
CAT, BA, GE

Energy:
XOM, CVX

Materials:
LIN

Utilities:
NEE

Real Estate:
PLD

No symbol is removed based on event outcome.

## 6. Crypto universe

BTC, ETH, BNB, SOL.

No claim is made from crypto subgroup results unless independent episode count is adequate.

## 7. Primary event outcomes

For every episode:

### Forward close returns
+1, +3, +5, +10, +20 bars.

### MFE / MAE
For 3, 5, 10, 20 bars:
- MFE = maximum future high relative to event close;
- MAE = minimum future low relative to event close.

### Distribution
Report:
- p10
- p25
- p50
- p75
- p90
- mean
- trimmed mean
- mean after removing single largest winner and single largest loser
- positive-return rate.

### Concentration
Report:
- largest single event contribution to total P&L sum;
- largest two-event contribution;
- largest symbol contribution;
- largest calendar-month contribution.

## 8. Relative-return controls

Absolute return is never sufficient.

### US equities

For every event calculate:

1. SPY excess return:
   asset forward return - SPY forward return.

2. Sector ETF excess return.

Frozen mapping:
- Technology -> XLK
- Communication Services -> XLC
- Consumer Discretionary -> XLY
- Consumer Staples -> XLP
- Health Care -> XLV
- Financials -> XLF
- Industrials -> XLI
- Energy -> XLE
- Materials -> XLB
- Utilities -> XLU
- Real Estate -> XLRE

If a sector ETF series is unavailable for an event date, that event remains in absolute/SPY analysis and is excluded only from the sector-relative statistic. No substitute ETF will be chosen after observing outcome.

### Crypto

- BTC events: excess versus equal-weight ETH/BNB/SOL basket;
- altcoin events: excess versus BTC;
- also report equal-weight 4-asset crypto basket excess.

## 9. State-matched and overextension-matched controls

### Same-state random baseline

For every event family:
- eligible controls have the same symbol and same exclusive XMA state;
- controls must not themselves satisfy the tested event;
- controls within +/-20 bars of a same-family event are excluded.

A deterministic seed is used for resampling.

### Nearest-neighbor matched baseline

For each event choose the 5 nearest eligible same-symbol/same-state controls by standardized Euclidean distance over:

1. `dev20 = close / MA20(close) - 1`
2. prior 20-bar return
3. ATR14 / close

This explicitly tests whether upper confluence is merely a proxy for "already very extended".

Matched-control excess:
```text
event forward return - mean(forward return of 5 matched controls)
```

No matching variable is added after outcomes are inspected.

## 10. Event-overlap and independence audit

Report:

- same-symbol episode spacing distribution;
- count of events by symbol;
- count by calendar month;
- HHI concentration by symbol;
- HHI concentration by month;
- number of dates with multiple symbols triggering;
- global event waves: events within +/-2 trading days across symbols are grouped as one market wave;
- raw episode count versus market-wave count.

This prevents treating one broad selloff/rally as many independent observations.

## 11. Uncertainty / clustered robustness

No naive iid t-test is treated as decisive.

Report deterministic bootstrap confidence intervals:

1. symbol-cluster bootstrap;
2. calendar-month cluster bootstrap;
3. symbol-month block bootstrap where sample size permits.

Seed:
`20260928`

Replicates:
5000.

Primary interval:
95% bootstrap percentile interval for:
- absolute mean;
- SPY excess mean;
- sector excess mean;
- matched-control excess mean.

Also report:
- leave-one-symbol-out range;
- leave-one-month-out range.

## 12. Independent state-transition event study

Study every transition as its own event, regardless of confluence:

- DOWN -> RANGE
- RANGE -> UP
- UP -> RANGE
- RANGE -> DOWN
- DOWN -> UP
- UP -> DOWN

For each:
- n;
- +5/+10/+20 return distribution;
- MFE/MAE;
- SPY/sector excess for equities;
- matched same-origin-state control excess.

No lifecycle interpretation is accepted solely because transition followed a confluence event.

## 13. Analytic midpoint event study

Until the visual middle-white-line mapping is resolved, call:

`GZB18 = (ZK1+ZD1)/2`

**FAST_MID_ANALYTIC**, not the visible middle rail.

Study independently:

- close crosses above FAST_MID_ANALYTIC;
- close crosses below FAST_MID_ANALYTIC;
- reclaim after lower confluence;
- loss after upper confluence.

Compare:
- confluence + midpoint event;
- confluence without midpoint event;
- midpoint event without confluence.

## 14. Time-to-event / time-stop research

No time stop is used as a trading rule in this phase.

Measure survival curves from confluence to:

Lower:
- leave DOWN;
- FAST_MID_ANALYTIC reclaim.

Upper:
- leave UP;
- FAST_MID_ANALYTIC loss.

Report probability of confirmation by:
3, 5, 10, 20, 40 bars.

Candidate time-stop values may be proposed only after distribution analysis and must be tested in a later window.

## 15. Same-bar lower penetration decomposition

The previous full-reclaim definition is not reused as one binary feature.

Freeze three categories:

1. SHALLOW_INTERACTION:
   low crosses/touches the nearer lower rail but does not extend >0.25 ATR below the lower of ZD1/BD.

2. DEEP_PIERCE_RECLAIM:
   low extends >0.25 ATR below the lower of ZD1/BD
   AND close returns above both rails.

3. DEEP_PIERCE_NO_RECLAIM:
   low extends >0.25 ATR below the lower of ZD1/BD
   AND close does not return above both rails.

Compare distributions without tuning 0.25 ATR in this holdout.

## 16. HYS2 2x2 interaction test

HYS2 features:
- ★ resonance
- fire-bottom / fire-top
- L1/L2 bull/bear cross

Primary interaction analysis uses matched event/control samples.

For each direction, estimate:

```text
logit(success_5) =
b0
+ b1 * XMA_EVENT
+ b2 * HYS_FEATURE
+ b3 * XMA_EVENT*HYS_FEATURE
+ controls
```

Controls are frozen:
- dev20
- prior20 return
- ATR14/close

Primary interest:
interaction coefficient `b3`.

Do not interpret HYS2 as incremental unless:
- interaction sign is stable across Validation A and B;
- sample size is adequate;
- bootstrap interval is not dominated by one symbol/month.

Fire-bottom/fire-top remain formally REDUNDANT if near-universal within the XMA event and add no discrimination.

## 17. Volume / Volume Profile / Breadth / VIX

These are falsification targets, not trading rules.

### Pre-registered lower hypotheses

L-VOL-1:
negative/capitulation volume context may improve lower-confluence forward outcome.

L-VP-1:
lower confluence BELOW_VAL may outperform same event INSIDE_VALUE.

L-BREADTH-1:
negative breadth may identify washout contexts.

VIX:
retain prior frozen dimensions and separately record:
- VIX 5-day rate of change;
- VIX relative to MA20;
- 5-day acceleration.

No new VIX threshold is promoted in this run.

### Minimum sample rule

Any subgroup:
- n < 20 = hypothesis only;
- n 20–29 = OBSERVE;
- n >=30 = eligible for validation interpretation.

## 18. Multiple testing

Primary hypothesis family:
1. upper strict confluence matched-control excess;
2. upper strict confluence sector-relative excess;
3. lower strict confluence 10/20-bar matched-control excess;
4. lower confluence BELOW_VAL interaction;
5. upper confluence -> later state deterioration;
6. lower confluence -> later state improvement.

Report raw p-like bootstrap tail probabilities where used, but control the family with Benjamini-Hochberg FDR q=0.10.

No result is promoted from an unregistered exploratory split.

## 19. Falsification criteria

### Upper-confluence hypothesis

SUPPORT only if:
- >=30 independent episodes across combined holdouts;
- negative matched-control excess;
- negative sector-relative excess;
- direction consistent in both Validation A and B;
- no single symbol contributes >25% of episodes;
- result survives leave-one-symbol-out sign check.

Otherwise:
- INCONCLUSIVE or REJECT.

### Lower-confluence hypothesis

SUPPORT only if:
- >=30 independent episodes;
- positive delayed 10/20-bar matched-control excess;
- result is not explained solely by generic DOWN-state mean reversion;
- direction consistent across holdouts.

### Below-VAL interaction

SUPPORT only if:
- >=30 lower events in relevant comparison;
- BELOW_VAL has incremental matched-control separation versus INSIDE_VALUE;
- effect is not concentrated in <=2 symbols/months.

## 20. Governance

- Jan–Jun 2025 definitions remain frozen.
- Validation A/B thresholds never change.
- Failed hypotheses are recorded, not repaired in the same holdout.
- Any revised definition becomes v2 and must use the sealed 2026 window or a new symbol universe.
- No portfolio sizing, stop-loss optimization, or short strategy is introduced during falsification v1.
