# SSSS Research Log

This file records important accepted and rejected research so failed ideas are not repeatedly rediscovered.

## Core causal rewrite

Source XMA was treated as non-causal / centered for live trading research.

Causal alternatives were compared:
- double SMA: ~62.2% state agreement
- double EMA: ~68.6%
- DEMA: ~86.9%

DEMA was selected as the causal rewrite.

## BUY module retained

Qualified GRB:
- Effective GREEN
- high crosses above FastUpper
- dsep > 0
- PriceNearWhite: close >= WhiteLower - 2*ATR14

PriceNearWhite had the strongest repeated OOS separation among tested BUY eligibility layers.

## BUY ideas rejected or downgraded

- static color-to-position mappings
- simple gray/red upgrades
- MA30 location / slope
- A8 yellow hard confirmation
- A8 turn-up hard confirmation
- active SAR confirmation
- 2-day higher-timeframe hard confirmation
- SPY bull filter
- sector bull filter
- stock > SPY relative-strength filter
- stock > sector relative-strength filter
- volume hard filter
- strong close above fast upper
- fast-width expansion
- white-slope-up filter
- absolute white-width threshold
- fixed cycle-age threshold
- machine-learned BUY quality model from the tested feature set

## Failure SELL research

Current retained rule:
- Effective Gray -> Effective Green

Rejected as full CLOSE:
- Deep Relapse
- C < FastLower during Gray
- first Raw Green
- A8 weakness
- dsep weakness
- earlier Gray failure guesses

Important finding:
some earlier-looking risk signals predicted eventual failure but executed at worse prices. Three-bar Green confirmation often allowed a better rebound exit.

## Mature SELL research

Current retained rule:
- Effective Red -> Effective Gray

Raw Gray 1 / 2 / 3 were compared. Earlier Gray exits were not consistently better out of sample.

RTE:
- not accepted as full CLOSE
- retained as REDUCE candidate only

## Corrected episode accounting

Earlier research grouped some signals by repeated raw-Green confirmations.

This was corrected.

A new independent Green episode now begins only when EffectiveState changes from non-Green to Green.

Corrected baseline:
- 96 independent Qualified BUY lifecycles
- 88 resolved
- 69 mature
- 19 fail
- 71 completed trades
- 59.2% win rate
- +8.84% average net return

This corrected episode definition is the official baseline going forward.

## Profit/loss anatomy

Completed baseline trades showed:
- average winner ~+18.91%
- average loser ~-5.75%
- payoff ratio ~3.29
- profit factor ~4.76

Return distribution is positively skewed and materially dependent on large trends.

Main future research targets:
1. no-progress trades
2. tail-loss control
3. profit giveback control
4. ADD / REDUCE / RE-ADD action discovery
5. only after action validation: position-size optimization


## Action-discovery round — 2026-09-19

### No-Progress REDUCE

Tested:
- first effective Green -> Gray before any Red maturity
- running MFE < 1 entry ATR
- current close <= original entry price

Discovery:
- 20 events
- median candidate price ~1.11% above eventual final close
- average candidate price ~2.54% below eventual final close

New 10-stock OOS:
- 2 events
- average candidate price ~1.20% below eventual final close

Decision: REJECT as a general REDUCE rule.

### Profit-Giveback REDUCE

Tested a path-aware rule:
- effective Red
- prior MFE >= 2 entry ATR
- giveback >= 1 entry ATR
- raw state Gray

Discovery:
- 47 events
- average price advantage vs final close only ~+0.23%

New OOS:
- 5 events
- average advantage reversed to ~-0.68%

Decision: REJECT as a general REDUCE rule.

### RTE after proven progress

RTE after at least 2 ATR of prior MFE:
- 8 baseline events
- 62.5% of RTE prices were above the later final close
- average advantage ~+1.46%
- median advantage ~+5.82%

New 10-stock OOS produced zero qualifying RTE events.

Decision: retain as CANDIDATE only; evidence remains sparse.

### ADD — repeated Qualified GRB

Discovery:
- 37 add events
- win rate 51.4%
- average subsequent add leg +7.31%
- median +0.66%
- 25 later Mature, 12 later Fail

Frozen new OOS:
- 5 events
- win rate 20%
- average -5.22%
- median -2.44%

Decision: REJECT.

### ADD — Red-confirmed path breakout

Definition:
- trade has matured into effective Red
- later close exceeds the highest high formed from entry through Red confirmation

Discovery:
- 33 events
- win rate 39.4%
- average +7.50%
- median -2.63%

Decision: REJECT. Positive mean is not representative of the typical add leg.

### RE-ADD — RTE high reclaim

Definition:
- RTE occurs
- remain in effective Red
- later close exceeds the RTE-day high
- RE-ADD next open

Discovery:
- 6 events
- win rate 33.3%
- average subsequent leg -0.95%
- median -3.05%
- average buyback price ~1.4% above the earlier RTE reduction price

Decision: REJECT.

### Action-layer conclusion

The correct position-management architecture remains:
OPEN / HOLD / ADD / REDUCE / RE-ADD / CLOSE.

However, architectural completeness does not justify inventing triggers.

Current validated/candidate status:
- OPEN = validated
- ADD = none validated
- REDUCE = RTE candidate only
- RE-ADD = none validated
- CLOSE = validated failure/mature rules


## Tail-loss position-action round — 2026-09-19

Objective: reduce the left tail without destroying the large winners that drive the strategy's positive skew.

### No-Progress + WhiteLower

Definition:
- before any Red maturity
- effective Gray
- running MFE < 1 entry ATR
- close < WhiteLower

Baseline:
- 13 triggers
- hit 6 of 10 losses worse than -5%
- hit 4 of 5 losses worse than -10%
- touched only 2 eventual winners
- average action-vs-final-close edge +0.81%
- average edge on <-10% losses +6.46%

Independent follow-up:
- 25 completed trades
- 2 triggers
- both were <-10% losses
- no winners touched
- average action-vs-final-close edge only +0.58%

Decision: CANDIDATE WARNING / possible second-stage REDUCE only. Identification was useful but timing was often late.

### No-Progress + FastMid

Definition:
- before any Red maturity
- effective Gray
- running MFE < 1 entry ATR
- close < FastMid

Baseline:
- 12 triggers
- hit 6 of 10 losses worse than -5%
- hit 4 of 5 losses worse than -10%
- touched 2 winners
- average action-vs-final-close edge +1.41%
- average edge on <-10% losses +9.22%

First independent follow-up:
- 25 completed trades
- 2 triggers
- both were <-10% losses
- no winners touched
- average edge +1.94%

Second frozen OOS:
- 8 completed trades
- 2 triggers
- both were eventual winners
- zero tail-loss hits
- average action-vs-final-close edge -9.30%
- one false reduction was NOC, which later finished about +13.73%

Decision: REJECT as mandatory REDUCE. This was a clear OOS reversal.

### No-Progress loss thresholds

Tested while running MFE remained < 1 entry ATR and before Red:
- close <= entry - 1 ATR
- close <= entry - 1.5 ATR
- close <= entry - 2 ATR

All five baseline losses worse than -10% were captured, but the rules also touched eventual winners and had negative average marginal value.

Decision: REJECT as general REDUCE rules. The strategy cannot use simple ATR-loss de-risking without sacrificing important recoveries.

### Profit round-trip

Tested after a trade had previously reached +2 ATR or +3 ATR of MFE, then returned to the entry-price area.

These rules occasionally protected a tail loss but touched too many eventual winners. Average marginal value was negative or near zero.

Decision: REJECT as general REDUCE.

### Staged-entry / delayed Red unit

Tested the idea of keeping a second notional unit in cash until the trade matured into effective Red.

Correct implementation:
- Failure paths never receive the delayed unit.
- Mature paths add the delayed unit at the next open after Red maturity.

Per-unit results across the 71-trade baseline:
- normal OPEN unit: +8.84% average
- delayed Red unit: +3.89% average
- shifting one full unit from OPEN to Red reduced average return by about 4.95 percentage points

Failure-path benefit:
- the delayed unit stays in cash, so it avoids Failure-path losses completely.

Mature-path cost:
- delayed Red unit average +5.31%
- median -1.21%
- much of the large-trend early move is missed.

Decision: REJECT as a full replacement for initial exposure. Retain as a position-sizing frontier concept only.

### Tail-loss conclusion

No mandatory tail-loss REDUCE trigger passed OOS.

The main structural lesson is that early weakness can later recover into major winners, while waiting until a tail-loss classifier becomes very precise often makes the action too late to add much economic value.

Next direction:
- preserve Qualified GRB as an early starter signal
- search for an ADD point that proves the trade without chasing
- treat RTE as the leading sparse REDUCE candidate
- optimize starter/add allocation only after the action frontier is better established


## E030 ADD round — 2026-09-19

Research question:
Can an early Qualified GRB trade prove direction, complete a controlled pullback, and then re-accelerate into a non-chasing ADD before Effective Red?

The round was pre-registered before results:
- Discovery: 25 stocks
- OOS: 10 stocks
- Frozen OOS: 5 stocks
- six fixed variants only
- no post-result threshold changes permitted

Discovery variants:
- U075 / U100 / U150: FastUpper reset after prior 0.75 / 1.00 / 1.50 EntryATR progress
- M075 / M100 / M150: FastMid test/reclaim after the same three progress thresholds

Common re-acceleration requirements:
- before first Effective Red
- C > FastUpper
- C > prior-day high
- dsep > 0
- signal close no more than 0.25 EntryATR above the prior running high
- next-open ADD execution

Discovery result:
- U075: 3 signals, 0 resolved ADD legs, 3 stocks
- U100: 3 signals, 0 resolved ADD legs, 3 stocks
- U150: 3 signals, 0 resolved ADD legs, 3 stocks
- M075: 0 signals
- M100: 0 signals
- M150: 0 signals

The three U-family signals occurred in AAPL, MSFT, and XOM and were still unresolved by the sample end.

Pre-registered eligibility required:
- at least 12 resolved ADD legs
- at least 6 Discovery stocks
- positive mean
- positive median
- profit factor > 1

Decision: REJECT at Discovery.

OOS was not opened.
Frozen OOS was not opened.

Interpretation:
The combined requirement of prior progress + controlled pullback + pre-Red re-acceleration + anti-chase cap is too restrictive in the available history. This exact six-variant family should not be revived without a materially different hypothesis.

Important: the failure is not evidence that pullback-based ADD is impossible. It only rejects this tightly constrained formulation.


## E031 Structural Confirmation ADD — 2026-09-19

Research question:
Can normalized fast-band vs white-band separation provide a useful ADD confirmation after Qualified GRB but before Effective Red?

Structural variable:

```text
StructuralSep = (FastMid - WhiteMid) / WhiteWidth
```

Pre-registered six-variant family:
- S050B / S100B / S150B
- S050X / S100X / S150X

Discovery cohort:
30 fixed stocks.

OOS and Frozen OOS remained unopened throughout Discovery.

### Discovery results

| Variant | Signals | Resolved | Stocks | Win rate | Avg net | Median net | Q25 | Profit factor | Median entry distance | Median lead to Red | Top-3 positive share |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| S050B | 43 | 34 | 25 | 35.3% | +4.21% | -2.90% | -5.43% | 2.24 | 2.50 EntryATR | 4 bars | 61.9% |
| S100B | 38 | 29 | 24 | 34.5% | +4.22% | -2.97% | -5.40% | 2.30 | 3.00 EntryATR | 2 bars | 69.8% |
| S150B | 16 | 13 | 13 | 38.5% | +11.05% | -3.13% | -6.04% | 4.35 | 3.09 EntryATR | 1 bar | 83.3% |
| S050X | 24 | 19 | 19 | 26.3% | +3.96% | -3.47% | -6.14% | 2.05 | 3.11 EntryATR | 3 bars | 89.4% |
| S100X | 19 | 15 | 16 | 40.0% | +10.07% | -2.70% | -5.25% | 4.24 | 3.40 EntryATR | 2 bars | 76.5% |
| S150X | 12 | 9 | 11 | 44.4% | +12.88% | -3.13% | -6.04% | 4.80 | 3.40 EntryATR | 1 bar | 91.6% |

### Pre-registered eligibility gate

A variant required all of:
- at least 15 resolved ADD legs
- at least 8 stocks
- positive average net ADD-leg return
- positive median net ADD-leg return
- profit factor > 1.25
- 25th percentile > -8%
- top-3 winners <= 70% of gross positive ADD return
- median ADD execution distance <= 2.5 EntryATR
- median lead to Effective Red >= 2 bars

No variant passed.

The decisive common failure was:
- every variant had a negative median ADD-leg return.

Additional problems increased at higher thresholds:
- execution became later / farther from original entry
- lead time to Effective Red compressed
- positive results became increasingly concentrated in a few large winners

### Decision

E031 = REJECT_DISCOVERY.

Do not open OOS.
Do not open Frozen OOS.
Do not add an ADD trigger to the model.

### Interpretation

Structural separation alone is informative about trend strength but is not a robust ADD timing rule.

The positive mean and high profit factor in several variants are misleading if viewed without the median. The typical ADD leg remained negative, while a small number of very large trends lifted the average.

This repeats the central SSSS lesson:
large winners matter greatly, but an ADD rule must improve exposure to those trends without making the typical incremental unit lose money.
