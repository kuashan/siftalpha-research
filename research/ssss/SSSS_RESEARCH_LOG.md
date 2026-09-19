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


## E032 ADD Opportunity Map — 2026-09-19

E032 reversed the research workflow:
instead of proposing an ADD trigger first, every causally available in-trade decision bar was labeled with the hypothetical next-open ADD return to the already validated final CLOSE.

Governance:
- Discovery: 30 fixed stocks
- Reserved OOS: not opened
- Reserved Frozen OOS: not opened
- five formal maps only
- primary statistics used first-entry-per-trade within each map cell

Coverage:
- 30 / 30 Discovery stocks
- 40 resolved trades
- 3332 all-bar hypothetical ADD observations
- Massive only; intermittent rate limits were retried without provider mixing

Result:
- 15 pre-defined cells passed the CANDIDATE_ZONE gate
- E032 outcome = CANDIDATE_ZONES_FOUND

Top five formal zones:

1. m4 / S_LT_0|F_BELOW_MID: 30 events, 22 stocks, win 70.00%, avg 4.65%, median 2.97%, PF 3.67, median entry distance -0.87 EntryATR, median timing 8.5 bars
2. m3 / M_LT_1|P_LE_0: 34 events, 22 stocks, win 64.71%, avg 9.59%, median 2.57%, PF 8.49, median entry distance -0.38 EntryATR, median timing 1 bars
3. m1 / PRE_RED|B00_04: 40 events, 24 stocks, win 62.50%, avg 8.45%, median 2.57%, PF 7.19, median entry distance -0.04 EntryATR, median timing 1 bars
4. m2 / P_LE_0|G_GE_2: 25 events, 17 stocks, win 60.00%, avg 5.45%, median 2.78%, PF 5.48, median entry distance -1.43 EntryATR, median timing 9 bars
5. m5 / GREEN|D_POS: 38 events, 24 stocks, win 63.16%, avg 5.99%, median 2.57%, PF 5.43, median entry distance -0.03 EntryATR, median timing 1 bars

Main interpretation:
the positive marginal-return surface clusters early, before Effective Red and before large price extension.

Several high-ranking cells are extremely close to the original OPEN in both time and price. Therefore they may represent "more initial exposure" rather than a genuinely new confirmation signal.

This is important because it explains why later confirmation-style ADD rules repeatedly failed:
by the time the trade looks obviously stronger, the typical remaining incremental return is often already weak or negative.

Decision:
- do not accept an ADD trigger from E032
- do not modify the state machine
- any selective early-second-entry rule must be a new pre-registered experiment


## E033 Selective Early Second Entry — 2026-09-19

Objective:
test whether early post-entry information can selectively identify trades that deserve a second unit, instead of merely increasing starter size.

Governance:
- Discovery: 30 fixed stocks
- OOS: not opened
- Frozen OOS: not opened
- four exact pre-registered candidates
- Massive only
- actual Massive history begins 2024-09-18 because earlier bars are not entitled
- normal 150-bar warm-up retained
- earliest observed E033 entry: 2025-04-28

Discovery coverage:
- 52 total trades
- 40 resolved
- 31 Mature
- 9 Failure

Benchmarks on the 40 resolved trades:
- BASE_1U: average +8.38%, median +2.22%, win 62.5%, PF 6.41
- NEXTDAY_2ND: average +8.45%, median +2.57%, win 62.5%, PF 7.19

Candidate results:

### C04 — Early Continuation
- 28 resolved ADD legs
- 19 stocks
- win 67.9%
- average +5.62%
- median +1.44%
- PF 4.97
- Mature trigger rate 71.0%
- Failure trigger rate 66.7%
- Failure trades avoiding second unit: 33.3%
- median entry distance +0.37 EntryATR
- median timing 2 bars
- median delay cost vs immediate second unit: -0.83%

Decision: REJECT.
Reason: positive economics but almost no useful path discrimination; failed the required Mature-minus-Failure trigger-rate spread and failure-avoidance gate.

### D10 — Early Discount / Unproven Trend
- 29 resolved ADD legs
- 20 stocks
- win 65.5%
- average +6.34%
- median +1.98%
- PF 5.93
- Mature trigger rate 67.7%
- Failure trigger rate 88.9%
- Failure trades avoiding second unit: 11.1%
- median entry distance -0.38 EntryATR
- median timing 1 bar
- median delay cost +1.10%

Decision: REJECT.
Reason: despite good ADD economics and better entry prices, it triggered Failure trades even more often than Mature trades.

### S10 — Structural Discount
- 17 resolved ADD legs
- 14 stocks
- win 76.5%
- average +5.03%
- median +2.78%
- Q25 +0.18%
- PF 5.95
- Mature trigger rate 38.7%
- Failure trigger rate 55.6%
- Failure trades avoiding second unit: 44.4%
- median entry distance -1.43 EntryATR
- median timing 6 bars
- median delay cost +2.82%

Decision: REJECT.
Reason: attractive per-event economics but inverse selectivity; Failure trades triggered more often than Mature trades.

### R10 — Early Entry Reclaim
- 20 resolved ADD legs
- 16 stocks
- win 70.0%
- average +5.48%
- median +1.31%
- PF 7.00
- top-3 winners 81.5% of gross positive return
- Mature trigger rate 48.4%
- Failure trigger rate 55.6%
- Failure trades avoiding second unit: 44.4%
- median entry distance +0.42 EntryATR
- median timing 3 bars
- median delay cost -0.94%

Decision: REJECT.
Reason: Failure trigger rate exceeded Mature trigger rate and winner concentration exceeded the pre-registered 70% cap.

### E033 conclusion

No candidate passed the pre-registered Discovery gate.

The important finding is not that early second entries are economically bad.
They were generally economically positive.

The failure is selectivity:
none reliably distinguished Mature from Failure paths.

This strengthens a new hypothesis:
the early opportunity found in E032 may be primarily a position-sizing effect rather than a separate technical ADD signal.

Next research should compare starter-size / mechanical split-entry policies under explicit risk and capital-normalization assumptions rather than inventing another early trigger.


## E034 Orthogonal Feature Diagnostic — 2026-09-19

Purpose:
test whether four open-source-derived orthogonal features add lifecycle-quality information beyond the existing SSSS structure.

Duplication audit was completed first.

Features:
- ER10
- CHOP14
- CMF20
- OBVImpulse10

Snapshots:
- S0: Qualified GRB signal close
- S1: original OPEN execution-day close

### Equity Discovery

Coverage:
- 30 / 30 pre-registered stocks completed
- 40 resolved lifecycles
- 31 Mature
- 9 Failure
- no missing feature values at either snapshot

#### S0 — signal close

| Feature | Mature median | Failure median | Cliff delta | Candidate |
|---|---:|---:|---:|---|
| ER10 | 0.2697 | 0.2668 | -0.039 | No |
| CHOP14 | 53.38 | 55.45 | -0.090 | No |
| CMF20 | 0.0455 | 0.0462 | -0.147 | No |
| OBVImpulse10 | 0.2162 | 0.2603 | -0.082 | No |

#### S1 — entry-day close

| Feature | Mature median | Failure median | Cliff delta | Candidate |
|---|---:|---:|---:|---|
| ER10 | 0.2392 | 0.3037 | -0.061 | No |
| CHOP14 | 51.79 | 56.98 | -0.190 | No |
| CMF20 | 0.0335 | 0.0415 | -0.061 | No |
| OBVImpulse10 | 0.2730 | 0.2335 | +0.011 | No |

No feature/snapshot met the pre-registered |Cliff delta| >= 0.33 gate plus quartile-consistency requirements.

CHOP14 at S1 showed the largest equity separation in the expected lower-choppiness-for-Mature direction, but:
- magnitude remained below the fixed gate;
- quartile Mature rates were non-monotonic (90%, 80%, 60%, 80%);
- therefore it is not an E034 diagnostic candidate.

### Crypto Discovery

Coverage:
- BTC, ETH, SOL, BNB
- 7 resolved lifecycles total
- 4 Mature
- 3 Failure
- BNB history began only 2026-03-04

Every crypto feature/snapshot was labeled TOO_SPARSE under the pre-registered rule.

Notable but non-actionable observations:
- ER10 S0 Cliff delta = -1.00
- ER10 S1 Cliff delta = -0.50
- OBVImpulse10 S1 Cliff delta = -0.33

These values must not be treated as validated signals because n=7.

### Decision

E034 = NO_DIAGNOSTIC_CANDIDATE.

Do not open:
- equity OOS
- equity Frozen OOS
- crypto OOS
- crypto Frozen OOS

Do not create a hard filter from any E034 feature.

Main lesson:
these four single-feature snapshots did not materially separate Mature from Failure in the current equity sample, and the crypto daily sample is too small to judge.

The next crypto-oriented research step should increase independent lifecycle sample size through a pre-registered longer-history provider or a separate lower-timeframe experiment rather than mining thresholds from seven trades.


## E035 BTC 15m Dynamic Position Engine — Phase A — 2026-09-19

Status:
NO_15M_BASELINE.

Data:
- X:BTCUSD Massive composite
- 15m UTC bars
- Discovery only
- 33,312 continuous bars
- 2024-09-19 00:00 UTC through 2025-08-31 23:45 UTC
- no gaps / no duplicate timestamps
- 94 sub-1-basis-point OHLC boundary inconsistencies sanitized by high=max(high,open,close), low=min(low,open,close)
- raw FNV-1a 64 fingerprint: 2f6aba04f4ca730c

Phase A results:

### B0 LEGACY_COUNT_REFERENCE
- 134 resolved lifecycles
- 77 Mature / 57 Failure
- 11.59 resolved per 30 days
- median hold 68 bars = 17h
- gross mean +0.230%
- gross median +0.112%
- base-friction mean -0.011%
- base-friction median -0.128%
- base PF 0.987
- stress-friction mean -0.071%
- REJECT

### B1 NATIVE_12H
- 91 resolved
- 58 Mature / 33 Failure
- 7.87 resolved per 30 days
- median hold 97 bars = 24.25h
- gross mean +0.412%
- gross median -0.034%
- base mean +0.172%
- base median -0.274%
- base PF 1.207
- stress mean +0.112%
- REJECT because median net < 0

### B2 NATIVE_24H
- 47 resolved
- 32 Mature / 15 Failure
- 4.06 resolved per 30 days
- median hold 187 bars = 46.75h
- gross mean +0.833%
- gross median -0.192%
- base mean +0.591%
- base median -0.431%
- base PF 1.558
- stress mean +0.531%
- top-3 positive-return concentration 55.7%
- REJECT because median net < 0

Interpretation:
B2 has the strongest positive-skew economics and the best PF, but the typical trade remains negative after realistic friction.

Therefore:
- E035 Phase B OPEN/ADD/REDUCE/RE-ADD/CLOSE maps were NOT opened;
- no 15m baseline was accepted;
- no action trigger was created;
- no OOS / Frozen OOS / cross-asset 15m holdout was opened.

Research implication:
15m dynamic-engine research must first repair entry/lifecycle quality rather than layering position actions on a formally accepted baseline.
