# Source-XMA Walk-Forward Protocol

Status: FROZEN FOR THE INITIAL ABT REPLAY  
Date: 2026-09-27

## 1. Objective

Reconstruct the information available from the original SSSS + ADKBY-E source formulas as the chart advances from 2025-01-01 toward the present.

This is not a parameter search and not a profit-maximizing historical backtest.

The goal is to understand how a decision-maker could use the XMA structure without copying the author's displayed signals.

## 2. Instrument and timeframe

- Ticker: ABT
- Market: US equities
- Timeframe: 1D
- Anchor date: 2025-01-01
- First tradable session: 2025-01-02
- End: latest available completed daily bar

## 3. Source formulas

Use the source formulas exactly as recorded in the two supplied ftindex files.

### Core 25-XMA structure

```text
VL25_X = XMA(XMA(L,25),25)
VH25_X = XMA(XMA(H,25),25)
VDIFF  = VH25_X - VL25_X

FastUpper = VH25_X + VDIFF
FastLower = VL25_X - VDIFF
FastMid   = (VH25_X + VL25_X) / 2
```

ADKBY-E maps the same structure to a normalized scale where the source lower/upper signal levels correspond to approximately 20000 / 80000.

## 4. No replacement rule

For this track:

- no DEMA substitution;
- no EMA substitution for the XMA core;
- no SMA substitution;
- no "causal correction" inserted into the source-XMA replay.

The existing causal DEMA research remains valid in its own track and is not modified.

## 5. Point-in-time replay rule

For each replay date T:

1. construct the indicator state as it would be represented with data available through T under the chosen exact XMA implementation;
2. record all source-XMA values for T;
3. record our own decision label for T;
4. only then advance to T+1.

Do not use the later outcome to rewrite the decision label assigned at T.

## 6. Recalculation audit

Because XMA may alter previously displayed historical values as additional bars arrive, the study must explicitly track revisions.

For selected anchor dates, record:

- value first observed at anchor date;
- value after +1 bar;
- +3 bars;
- +5 bars;
- +10 bars;
- +20 bars;
- latest reconstructed value.

This is not treated as a reason to discard XMA. It is itself a research object.

## 7. Information layers

Each day should capture at least:

### Price
- O / H / L / C
- range
- close location inside the bar

### 25-XMA layer
- VL25_X
- VH25_X
- VDIFF
- FastLower
- FastMid
- FastUpper
- price location relative to the band

### 90-period structural layer
Record both source variants separately when they differ:
- SSSS slow structure
- ADKBY-E slow structure

Do not silently merge the two formulas.

### Regime
At minimum distinguish:
- BULL
- BEAR
- RANGE
- EXPANSION / UNCLASSIFIED

The fourth state is required because the original three-state logic does not cover every geometric relationship between the fast and slow bands.

### Momentum
Record the two source momentum components separately:
- DEA3_RAW direction
- DEA33B_RAW direction

Do not collapse them into the source `OR` rule before analysis.

## 8. Author-signal isolation

The following may be logged for comparison but must not determine our decision:

- SSSS money-bag icon
- SSSS person icon
- ADKBY-E 多
- ADKBY-E 空
- ADKBY-E 平
- ADKBY-E ⭐
- ADKBY-E ⚠️

Our decision column must be produced independently.

## 9. Decision vocabulary

Initial research vocabulary:

- NO_TRADE
- WATCH_LONG
- ENTER_LONG
- HOLD_LONG
- EXIT_LONG
- WATCH_SHORT
- ENTER_SHORT
- HOLD_SHORT
- EXIT_SHORT
- REGIME_UNCLEAR

This vocabulary is intentionally more explicit than a single buy/sell icon.

## 10. Initial decision principle

Do not equate "touching an extreme" with a trade.

Use the sequence:

```text
regime
-> location/extreme
-> XMA-band interaction
-> momentum transition
-> confirmation or failure
-> action
```

The exact action rule is a research hypothesis and may evolve inside this exploratory ABT track. Any later validation rule must be frozen under a new official experiment before OOS testing.

## 11. Evidence classification

Because the later ABT chart has already been viewed, all 2025-present ABT results are Discovery-like exploratory evidence.

No result from this replay may be relabeled OOS/Frozen OOS.
