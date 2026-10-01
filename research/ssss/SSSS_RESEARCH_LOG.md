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


## E036 BTC 15m Multi-Open Discovery — 2026-09-19

Status:
NO_MULTI_OPEN_REFERENCE.

Fixed B2 structural reference.

Independent OPEN-mode results:

### O1 GRB
- 51 resolved
- base mean +0.35%
- base median -0.45%
- base PF 1.28
- stress median -0.51%
- REJECT

### O2 FAST_BREAKOUT
- 68 resolved
- base mean +0.65%
- base median -0.21%
- base PF 1.59
- stress median -0.27%
- REJECT

### O3 GREEN_TRANSITION
- 70 resolved
- 49 Mature / 21 Failure
- 6.05 resolved per 30 days
- base mean +0.94%
- base median +0.24%
- base PF 1.91
- stress mean +0.88%
- stress median +0.18%
- q25 -0.96%
- top-3 positive share 34.3%
- median hold 70.5h
- PASS

### O4 FASTMID_RECLAIM
- 69 resolved
- base mean +0.80%
- base median -0.03%
- base PF 1.74
- stress median -0.09%
- REJECT

Overlap:
nearly all later GREEN-based modes occurred in the same Effective Green episodes as O3.

Interpretation:
on 15m BTC, the earliest Effective Green transition carries materially better typical economics than waiting for later breakout/reclaim confirmation.

Only one mode passed, so the pre-registered requirement for at least two independent OPEN modes was not met.

Therefore:
- no Multi-Open Reference was formed;
- dynamic action maps were not opened;
- OOS/Frozen OOS/cross-asset holdouts remained unopened.

Architecture implication:
O3 is a Discovery starter-OPEN candidate.
Later O1/O2/O4 events should be investigated as post-entry evidence / ADD candidates rather than forced into independent OPEN roles.


## E037 BTC 15m Starter-to-Dynamic Action Map — 2026-09-19

Status:
DYNAMIC_ACTION_ZONES_FOUND.

Reference:
GREEN_TRANSITION starter OPEN under B2 structure.

One-at-a-time starter engine:
- 48 resolved lifecycles
- 33 Mature / 15 Failure
- base-friction average +0.95%
- base-friction median +0.21%
- base PF 1.97

Discrete post-entry ADD events:

### GRB after starter
- 35 events
- base mean +0.74%
- base median -0.36%
- fail

### FAST_BREAKOUT after starter
- 47 events
- base mean +0.56%
- base median -0.18%
- fail

### FASTMID_RECLAIM after starter
- 47 events
- base mean +0.68%
- base median -0.08%
- fail

These later confirmation events have positive averages but negative medians and are not accepted as direct ADD triggers.

### ADD opportunity maps

10 pre-registered map cells passed the Discovery gate.

Top zones:

1. A3 M_LT_1 | P_LE_0
- 32 lifecycle events
- base mean +1.49%
- base median +0.64%
- stress median +0.58%
- PF 2.44
- q25 -0.77%
- median timing 1 bar after starter execution

2. A3 M_GE_4 | P_1_2
- 23 events
- base mean +0.46%
- base median +0.52%
- stress median +0.46%
- PF 1.46
- median timing 101 bars

3. A2 P_LE_0 | G_GE_2
- 41 events
- base mean +1.06%
- base median +0.20%
- stress median +0.14%
- PF 2.17
- median timing 15 bars

4. A1 PRE_RED | B00_07
- 48 events
- base mean +0.89%
- base median +0.20%
- stress median +0.14%
- PF 1.88
- median timing 1 bar

5. A2 P_LE_0 | G_1_2
- 37 events
- base mean +1.15%
- base median +0.17%
- stress median +0.11%
- PF 2.03
- median timing 3 bars

6. A4 GREEN | NONPOS | BELOW_MID
- 47 events
- base mean +0.90%
- base median +0.16%
- stress median +0.10%
- PF 1.87
- median timing 1 bar

Additional passing cells existed in:
- M_LT_1 | P_0_1
- M_1_2 | P_LE_0
- M_2_4 | P_1_2
- P_0_1 | G_LT_05

Main ADD interpretation:
the strongest incremental exposure economics appear very early, before Red, often while progress is <=0 and MFE <1 EntryATR.

This independently reproduces the broad timing lesson from equity E032:
late visual confirmation is weaker than early marginal exposure.

### REDUCE

No map cell passed.

Some post-Red cells had positive median reduction edge but negative mean edge.

Example:
POST_RED | M_GE_4 | G_05_1
- 23 events
- median edge +0.63%
- mean edge -1.02%

Meaning:
early reduction often looks helpful on a typical event but sacrifices rare large continuation winners badly enough to make average economic value negative.

### RE-ADD

No risk-marker/recovery combination passed.

FastMid-down -> FastMid-up was the densest:
- 48 events
- base mean +0.71%
- base median -0.07%
- stress median -0.13%

No validated recovery trigger.

### CLOSE

No close zone passed.

GREEN->GRAY:
- 48 events
- median early-close edge +0.38%
- mean edge -0.62%
- positive edge 68.8%
- Mature median MFE-sacrifice ratio ~0.81

Interpretation:
closing at Green->Gray would often look locally favorable but destroys too much later mature-trend upside.

### E037 conclusion

- starter OPEN reference: promising Discovery structure, not validated
- ADD: candidate zones found
- REDUCE: none
- RE-ADD: none
- CLOSE: no replacement for reference close

No position percentages assigned.
No action promoted to production.
All BTC temporal holdouts and ETH/SOL/BNB 15m remain unopened.


## E038 BTC 15m Tactical Tranche Reduce / Rebuild — 2026-09-19

Status:
NO_TACTICAL_REDUCE_CANDIDATE.

Architecture:
- 30% core from GREEN_TRANSITION
- +10% tactical ADD from MFE<1 ATR and Progress<=0
- REDUCE removes only the tactical 10%
- optional RE-ADD restores only the tactical 10%
- reference CLOSE unchanged

Eligible lifecycles with first ADD:
32.

### R1 GREEN->GRAY after ADD

32 events.

REDUCE_ONLY:
- incremental tactical mean -1.22%
- incremental tactical median +0.32%
- positive incremental rate 68.8%
- Failure-path mean incremental +1.29%
- Failure-path median +1.18%
- Mature-path mean incremental -2.20%
- Mature-path median +0.05%
- mean avoided adverse move ~2.32%
- mean foregone favorable move ~4.10%
- full-close edge mean -1.22%
- full-close edge median +0.32%

Interpretation:
this warning helps every observed Failure path but sacrifices enough large Mature continuation that average economics turn negative.

It is a useful risk-state discriminator candidate, not an unconditional REDUCE.

### R2 post-Red MFE>=4 + Giveback>=0.5 ATR

18 events.

REDUCE_ONLY:
- incremental mean -1.95%
- median +0.10%
- positive 55.6%
- all events were Mature
- mean foregone favorable move ~5.34%

This remains too destructive to large mature winners.

### R3 RTE after MFE>=2 ATR

12 events.

Below the required 15-event minimum.

REDUCE_ONLY:
- incremental mean -1.66%
- median -0.32%

No candidate.

### Can RE-ADD literally reuse the first ADD formula?

No.

A0 exact reuse:
RunningMFE<1 ATR AND Progress<=0 after REDUCE.

Observed re-add counts:
- after R1: 5 / 32
- after R2: 0 / 18
- after R3: 0 / 12

Structural reason:
RunningMFE is cumulative from the original starter and does not reset after a mature trend has already exceeded 1 ATR.

Therefore exact first-ADD reuse is mathematically incompatible with most later-cycle re-entry situations.

### Alternative recovery rules

R1 GREEN->GRAY + FastMid recovery:
- 21 / 32 re-adds
- incremental mean -0.22%
- median approximately 0%
- stress median negative
- fail

R1 + dsep recovery:
- 12 / 32 re-adds
- incremental mean -1.21%
- median +0.22%
- fail because mean is strongly negative

R2 mature giveback + FastMid recovery:
- 16 / 18 re-adds
- incremental mean -1.43%
- median -0.19%
- fail

R3 RTE + dsep recovery:
- 10 / 12 re-adds
- incremental mean ~0.00%
- median -0.24%
- fail / too sparse

R3 RTE + FastMid recovery:
- 9 / 12 re-adds
- incremental mean +0.09%
- median -0.07%
- stress median -0.13%
- fail / too sparse

### Direct CLOSE interpretation

None of these risk markers justifies replacing the existing full-close rule.

GREEN->GRAY is the clearest example:
typical exits look locally attractive, but mean full-close edge is negative because large continuation winners dominate the opportunity cost.

Therefore:
- REDUCE is not yet validated;
- RE-ADD is not yet validated;
- existing reference CLOSE remains unchanged.

### Research frontier

The next REDUCE question is no longer:
"Is GREEN->GRAY a reduce signal?"

The sharper question is:
"At GREEN->GRAY after an early ADD, can current causal information distinguish the Failure paths that benefit strongly from de-risking from the Mature paths that should keep the tactical tranche?"

The next RE-ADD question is no longer:
"Can we repeat the first ADD rule?"

It is:
"After a validated tactical reduction, can a LOCAL reset / recovery state identify when to rebuild the tactical tranche without chasing?"


## E039 BTC 15m Probabilistic Dynamic Sizing — 2026-09-19

Status:
NO_PROBABILITY_ACTION_MODEL.

Architecture tested:
- OPEN 30%
- TREND_ADD +10pp
- LOSS_ADD +10pp
- max exposure 50%
- PROFIT_RISK_REDUCE = sell 15% of current position quantity
- LOSS_RISK_REDUCE = sell 15% of current position quantity
- reference CLOSE unchanged

Probability outputs:
- P_UP
- P_DD4H

Model:
regularized causal logistic regression using only existing SSSS state features.

Validation inside Discovery:
chronological expanding out-of-fold predictions.

OOF model quality improved materially across later folds for P_UP:
- fold1 logloss 0.980
- fold2 0.694
- fold3 0.607
- fold4 0.549

P_DD4H logloss remained around 0.666-0.714.

### Portfolio threshold search

Frozen grid:
- P_UP high: 0.60 / 0.65 / 0.70
- P_DD4H high: 0.60 / 0.65 / 0.70
- LOSS_ADD threshold: -2% through -8%

63 combinations.

Eligible:
0.

OOF benchmark:
30% starter + existing E037 first-ADD benchmark + reference close.

Benchmark final multiplier:
1.03375 over the OOF evaluation lifecycles.

Best probability combination:
P_UP >= 0.70
P_DD4H high = 0.70
LOSS_ADD threshold = -2%

Candidate final multiplier:
1.02849.

Incremental return versus benchmark:
-0.53 percentage points.

Stress-friction incremental:
-0.46 percentage points.

Max drawdown:
10.84% candidate
vs
8.77% benchmark.

Therefore probability-driven sizing did not improve the existing simpler Discovery architecture.

### LOSS_ADD threshold study

No loss threshold passed the frozen evidence gate.

Best provisional region:

#### -6%
Best observed configuration:
- 7 LOSS_ADD events
- mean incremental unit return +0.40%
- median +1.14%
- PF 1.34
- q25 -1.59%

It failed because the required minimum was 8 events.

#### -7%
- 4 events
- mean +1.87%
- median +2.94%
- PF 3.23
- q25 +0.70%

Too sparse for acceptance.

Interpretation:
the empirical candidate band is around -6% to -7%, but -7% looks better largely because only four events survive.

The conservative provisional center is -6%.

It must remain inactive until a new preregistered validation has enough events.

Other thresholds:
-2% through -5% had negative average economics despite some positive medians.
-8% was also negative / sparse.

### Reduce interpretation

The four-action probability engine did not validate either reduce mode.

Profit-risk reduce became too sparse at strict probability thresholds.

Loss-risk reduce became very frequent at lower risk thresholds and contributed to higher turnover / worse mature-trend economics.

No probability reduce rule is activated.

### Model-writing decision

Write:
LOSS_ADD_CANDIDATE_THRESHOLD = -0.06
LOSS_ADD_CANDIDATE_BAND = (-0.07, -0.06)

But:
LOSS_ADD_ENABLED = False.

No E039 probability action is enabled.

This preserves the user's requested architecture without pretending Discovery evidence is validation.


## E040 BTC 15m Repeated Pullback Ladder — 2026-09-19

Status:
NO_REPEATED_PULLBACK_LADDER.

The experiment tested:
- local-reset pullback steps 1% through 10%;
- three existing-model bullish validity floors;
- repeated +10pp ADD to max 50%;
- repeated 15%-of-current-position REDUCE above a 30% core floor.

### Main threshold result

The strongest robust pullback step was 1%.

Using FastLower as the bullish-validity floor:

Portfolio:
- return +24.47%
- stress-friction return +22.84%
- E037 benchmark +19.03%
- E037 stress benchmark +17.77%

However:
- max drawdown 12.04%
- benchmark max drawdown 9.82%
- this exceeded the pre-registered +10% relative drawdown allowance

Therefore the full ladder failed the portfolio gate.

### Repeated ADD at 1% / FastLower

All ADD events:
- 150
- mean incremental unit return +2.24%
- median +0.38%
- PF 3.03
- stress median +0.32%
- q25 -1.49%

Second ADD:
- 26 events
- mean +1.93%
- median +0.53%
- PF 2.89
- stress median +0.47%

Therefore repeated ADD itself passed the pre-registered event gate.

### Critical split: loss-state versus profit-state ADD

LOSS_PULLBACK_ADD:
- 97 events
- mean +2.91%
- median +1.22%
- PF 3.44
- stress median +1.16%
- positive rate 63.9%

TREND_PULLBACK_ADD:
- 53 events
- mean +1.01%
- median -0.46%
- stress median -0.52%
- positive rate 43.4%

Interpretation:
the 1% local pullback ladder is useful primarily when the current position is losing but the SSSS continuation structure remains intact.

The same pullback rule should NOT be used as a generic profitable-position ADD.

### 2% and 3%

2% / FastLower:
- 35 ADD events
- second ADD 9 events
- second-ADD mean +3.37%
- second-ADD median -0.94%
- reject repeated-ADD gate

3% / FastLower:
- only 11 ADD events
- only 3 second ADD events
- attractive returns but too sparse and highly winner-concentrated

4%:
almost no valid actions.

5% through 10%:
no FastLower-valid ladder actions.

This means that waiting for a 4%-10% local pullback usually allows the 15m model structure to invalidate before an ADD can occur.

### REDUCE

No repeated REDUCE definition passed.

At 1% / FastLower:
- 60 REDUCE events
- median edge +0.54%
- positive rate 56.7%
- Failure-path mean edge +1.52%
- Mature-path mean edge -0.91%
- overall mean edge -0.43%

This reproduces the earlier finding:
typical reductions may look locally helpful, but rare large Mature continuations make unconditional repeated reduction economically negative.

### Bullish validity floor

For the repeated loss-add use case, FastLower was the most informative floor.

WhiteLower - 2ATR allowed many more risk actions but produced weaker second-add and REDUCE economics.

The strict combined floor reduced sample size and did not improve the full portfolio gate.

### Research conclusion

The user's repeated-pullback concept is supported for one specific action class:

LOSS_PULLBACK_ADD:
- local reset after every action
- approximately 1% pullback step
- only while SSSS continuation structure is strong
- only while close remains above FastLower
- +10pp exposure
- max exposure currently 50%

It remains a Discovery candidate, not a validated action.

Repeated profitable-position ADD is rejected under this same 1% rule.

Repeated REDUCE remains unvalidated.


## E041 BTC 15m Loss-Pullback Ladder Depth & Drawdown Attribution — 2026-09-19

Status:
NO_LOSS_ADD_DEPTH_CANDIDATE.

Duplication classification:
PARTIAL_OVERLAP with E037-E040.

E041 did not re-search the pullback threshold. It froze the E040 provisional rule:
- 1% local pullback;
- FastLower validity;
- Effective GREEN or RED;
- dsep > 0;
- weighted current position return < 0;
- +10pp LOSS_PULLBACK_ADD;
- local-anchor reset;
- 4-bar cooldown;
- no TREND_PULLBACK_ADD;
- no REDUCE / RE-ADD;
- reference CLOSE unchanged.

Two exact depths were tested:
- L1: maximum one LOSS_ADD, max exposure 40%;
- L2: maximum two LOSS_ADDs, max exposure 50%.

### Continuity audit

The replay exactly reproduced the E037 GREEN_TRANSITION reference:
- 48 resolved lifecycles;
- 33 Mature / 15 Failure;
- mean +0.947922%;
- median +0.205502%;
- PF 1.968088.

E040 Benchmark A final equity and every per-lifecycle return also reproduced to floating-point precision.

The E040 max-drawdown convention was independently recovered:
completed-bar raw close mark-to-market while a position is open, with execution friction charged through entry units and final exit-open liquidation.

Under that convention Benchmark A maxDD reproduced as 7.511515%, matching the E040 checkpoint to approximately 1e-15.

### L1 — one LOSS_ADD maximum

20 first LOSS_ADD events:
- mean incremental unit return +2.18%;
- median +0.57%;
- PF 2.68;
- stress median +0.51%;
- q25 -1.41%;
- positive rate 55.0%;
- top-3 positive-return share 64.9%.

L1 failed the event gate because winner concentration exceeded the frozen 60% ceiling.

Portfolio:
- return +18.61%;
- stress return +17.44%;
- maxDD 9.33%;
- Benchmark B return +19.03%;
- Benchmark B stress +17.77%.

So one-step LOSS_ADD also failed to beat Benchmark B.

### L2 — two LOSS_ADD maximum

37 pooled LOSS_ADD events:
- mean +2.50%;
- median +1.07%;
- PF 3.06;
- stress median +1.01%;
- q25 -1.22%;
- positive rate 64.9%;
- top-3 share 47.4%.

The second LOSS_ADD itself was economically strong:
- 17 events;
- mean +2.88%;
- median +1.22%;
- PF 3.58;
- stress median +1.16%;
- q25 +0.04%;
- positive rate 76.5%.

L2 therefore passed the pre-registered event gate.

Portfolio:
- return +23.98%;
- stress return +22.63%;
- incremental return vs Benchmark B +4.96 percentage points;
- stress incremental +4.86 percentage points;
- Mature total PnL remained above Benchmark B;
- largest single-lifecycle incremental share 32.2%, below the 35% cap.

But bar-level maxDD was 11.33%.

Benchmark B maxDD:
9.82%.

Frozen maximum allowed:
10.80%.

Therefore L2 exceeded the drawdown ceiling by about 0.53 percentage points and worsened maxDD by about 15.43% relative to Benchmark B.

### Drawdown attribution

L1 maxDD:
9.33%, about 0.49 percentage points LOWER than Benchmark B.

L2 maxDD:
11.33%.

Moving from one LOSS_ADD to two LOSS_ADDs therefore added about 2.00 percentage points of max drawdown.

The L1 maximum-drawdown span ran from lifecycle 9 through lifecycle 21.
The L2 maximum-drawdown span ran from lifecycle 9 through lifecycle 17.

This is the central E041 result:

the second LOSS_ADD has strong terminal-to-reference-close economics, but its interim path risk is too large under the current unconditional second-step admission rule.

### Comparison with E040 full ladder

E040 full 1% / FastLower ladder:
- return +24.47%;
- maxDD 12.04%.

E041 L2 LOSS-only ladder:
- return +23.98%;
- maxDD 11.33%.

Removing profitable-position TREND_ADD and repeated REDUCE sacrifices only about 0.49 percentage points of Discovery return while improving maxDD by about 0.71 percentage points.

That cleanup is directionally useful, but still insufficient to satisfy the frozen drawdown gate.

### Decision

No E041 depth is accepted.

- L1: safer, but too concentrated and does not outperform Benchmark B.
- L2: strong economics, but fails portfolio risk.
- no BTC OOS opened;
- no BTC Frozen OOS opened;
- no ETH/SOL/BNB 15m opened;
- no action is activated in the mutable research model.

Next research frontier:
do NOT re-optimize the 1% pullback threshold.

Instead, research a causal risk-admission discriminator specifically for the SECOND LOSS_PULLBACK_ADD, with the objective of preserving its strong terminal economics while rejecting the subset that creates excessive interim drawdown.


## E042 BTC 15m Second LOSS_ADD Risk Admission — 2026-09-19

Status:
NO_SECOND_LOSS_ADD_RISK_GATE.

E042 froze the E041 architecture:
- 30% starter;
- fixed first 1% FastLower LOSS_PULLBACK_ADD -> 40%;
- second base 1% LOSS_PULLBACK_ADD -> candidate 50%;
- no TREND_ADD;
- no REDUCE / RE-ADD;
- reference CLOSE unchanged.

Only the FIRST base second-LOSS_ADD signal in each lifecycle was eligible for admission.
A rejected second signal was not retried later in the same lifecycle.

### Continuity

E041 was reproduced exactly:
- 20 first LOSS_ADD events;
- 17 second LOSS_ADD base signals;
- L1 return +18.61%, maxDD 9.33%;
- L2 return +23.98%, maxDD 11.33%.

The same bar-level completed-close mark-to-market drawdown convention was preserved.

### C1 — GREEN only

All 17 second LOSS_ADD base signals were already Effective GREEN.

Therefore:
- admitted 17 / 17;
- portfolio identical to unfiltered L2;
- return +23.98%;
- maxDD 11.33%.

Conclusion:
Effective GREEN provides zero discrimination for the second LOSS_ADD problem.

### C2 — price above FastMid

Admitted:
8 / 17.

Admitted second-ADD economics:
- mean +1.77%;
- median +0.82%;
- PF 12.61;
- stress median +0.76%;
- q25 +0.26%;
- positive rate 87.5%.

Portfolio:
- return +20.26%;
- stress +19.02%;
- maxDD 9.50%.

This candidate passed:
- event evidence;
- portfolio value;
- risk.

But it retained only 24.9% of the unfiltered L2 incremental return above Benchmark B.

Frozen minimum:
50%.

Therefore C2 failed the economic-preservation gate.

Important diagnostic:
the 9 rejected second signals had strong terminal economics:
- mean +3.87%;
- median +3.03%.

So requiring price recovery above FastMid de-risks effectively but discards too much valuable second-add participation.

### C3 — dsep acceleration

Admitted:
9 / 17.

Portfolio:
- return +19.06%;
- stress +17.83%;
- maxDD 10.96%.

It preserved less than 1% of L2 incremental return above Benchmark B and still exceeded the 10.80% drawdown cap.

Reject.

### C4 — FastLower buffer >= 0.50 ATR

Admitted:
16 / 17.

Portfolio:
- return +22.86%;
- stress +21.53%;
- maxDD 10.96%.

It retained 77.4% of L2 incremental return, which was economically attractive.

But:
- maxDD 10.96% > frozen 10.80% cap;
- largest lifecycle share of incremental positive PnL was 35.97% > frozen 35% ceiling.

The single rejected event itself later returned +9.45% to reference CLOSE.

Conclusion:
0.50 ATR FastLower buffer is too weak as a path-risk discriminator.

### C5 — post-first-ADD MAE no worse than -1 ATR

Admitted:
5 / 17.

Portfolio:
- return +18.64%;
- stress +17.44%;
- maxDD 10.03%.

Risk improved, but:
- sample count below the >=8 gate;
- PF only 1.10;
- stress median slightly negative;
- portfolio failed Benchmark-B return.

The 12 rejected signals had:
- mean terminal return +4.02%;
- median +2.51%.

Conclusion:
this MAE rule filters out too many of the economically valuable second adds.

### C6 / C7

C6 GREEN + dsep acceleration was identical to C3 because every base second signal was already GREEN.

C7 buffer + MAE was identical to C5 inside this Discovery sample.

Neither passed.

### Final interpretation

No pre-registered causal gate separated the second-ADD path-risk problem well enough.

The result is more specific than E041:

1. GREEN is already universal among second LOSS_ADD signals and cannot discriminate.
2. FastMid recovery is a real risk filter, but it is too late / restrictive and sacrifices too much terminal value.
3. A 0.50 ATR FastLower buffer preserves value but does not reduce drawdown enough.
4. A simple post-first-add MAE <=1 ATR screen is too restrictive and selects weak economics.
5. The unresolved information appears to be the SHAPE of the local path between first ADD and second signal, not merely current state, current band location, or one scalar adverse excursion threshold.

### Decision

No E042 candidate is accepted.

- no BTC OOS opened;
- no BTC Frozen OOS opened;
- no ETH/SOL/BNB 15m opened;
- no action is activated;
- no threshold is repaired post-result.

Next research frontier:
study causal pre-second-add local path shape / recovery-versus-continuation structure on the already-GREEN second-signal set under a new Experiment ID.
Do not retune E042 thresholds.

## Stock Risk Exit Study v1.1 corrected closure — 2026-10-01

The first-pass Stock Risk Exit closure was invalidated after audit found a sample-end semantics bug: an open final position had been force-sold with synthetic 5 bps exit slippage and counted as a completed trade. The frozen protocol requires mark-to-market at the final close without a synthetic trade.

The simulator was corrected and all 39 stocks x 49 configurations were recomputed (1,911 runs).

Baseline reproduction against the previously frozen AB_HALF control:
- 39/39 stocks PASS;
- max absolute return difference 1.7763568394002505e-14;
- max MDD difference 4.440892098500626e-16;
- max P5 difference 1.942890293094024e-16;
- max CVaR10 difference 8.326672684688674e-17;
- trades difference 0;
- win-rate difference 0;
- exposure difference 0.

Corrected aggregate baseline:
- mean return +154.92%;
- mean intraday-low MDD -30.65%;
- mean P5 -6.95%;
- mean CVaR10 -8.22%;
- 2,606 completed trades.

Fixed hard/trailing stops show a consistent trade-off: tight stops improve some MDD/tail metrics but destroy substantial return through winner truncation; wide stops preserve more return but lose reliable downside improvement. Matched-stop deltas are negative across all three eras for every tested standalone hard and trailing threshold.

Final decisions:
- `UNIVERSAL_STOCK_HARD_STOP_5_TO_20 = REJECTED_NOT_ADMITTED`
- `UNIVERSAL_STOCK_TRAILING_STOP_5_TO_20 = REJECTED_NOT_ADMITTED`
- `UNIVERSAL_STOCK_HARD_TRAIL_COMBINATION = REJECTED_NOT_ADMITTED`
- `STOCK_SELECTIVE_SIGNAL_EXIT_CONTROL = RETAINED`
- `STATE_OR_VOLATILITY_AWARE_STOCK_RISK_EXIT = PROMOTED_TO_NEXT_VALIDATION`
- `STOCK_RISK_EXIT_STUDY_V1_1 = IMPLEMENTED_AND_VERIFIED`

Corrected final report:
`research/ssss/source_xma/experiments/stock_risk_exit_study_v1/FIVEGZ5SE_STOCK_RISK_EXIT_FINAL_v1_1.md`

Round CLOSED. Do not reopen the fixed 5-20% grid without genuinely new untouched validation data or a different preregistered hypothesis.

## State / Volatility-Aware Risk Exit Study v1 — CLOSED — 2026-10-01

The preregistered State / Volatility-Aware Risk Exit study was completed across the frozen 39-stock universe and BTC / ETH / BNB / SOL.

Baseline reproduction passed exactly before interpretation.

Eight formal candidates were evaluated:
LOSS2_MOD, LOSS3_MOD, LOSS2_SEV, PEAK2_MOD, PEAK3_MOD, HYBRID25_MOD, CONFIRM_ADAPT, LOSS4_SEV.

Results:
- Stock: 0/8 candidates passed.
- Crypto: 0/8 candidates passed.
- Universal: 0/8 candidates passed.

Representative stock result:
CONFIRM_ADAPT improved mean intraday MDD +2.43pp and 25/39 stocks, but retained only 52.6% of baseline return and killed 725 baseline winners versus 434 saved losers.

Representative Crypto result:
LOSS4_SEV increased pooled mean return to +77.87% versus +68.74% baseline, but improved MDD on only 2/4 coins, worsened P5, and failed cross-coin dominance/consistency gates.

Final decisions:
- `STOCK_RISK_EXIT = NOT_USED_RETAIN_BASELINE`
- `CRYPTO_RISK_EXIT = NOT_USED_RETAIN_BASELINE`
- `UNIVERSAL_STATE_VOL_RISK_EXIT = REJECTED_NOT_ADMITTED`
- `RISK_EXIT_LAYER = NOT_USED_RETAIN_BASELINES`
- `STATE_VOL_RISK_EXIT_STUDY_V1 = IMPLEMENTED_AND_VERIFIED`

The current SSSS candidate therefore uses the existing signal-driven SELL controls without an independent risk-exit layer.

Round CLOSED.

## Crypto SELL-C Partial Exit Study v1 — CLOSED — 2026-10-01

A preregistered 25% / 50% / 75% / 100% SELL-C study was completed on BTC / ETH / BNB / SOL using the frozen Binance daily windows.

The first summary pass exposed an MDD-improvement sign-direction bug. The underlying paths were unaffected. The sign was corrected and the complete computation was rerun before interpretation.

Final corrected results:
- SELL 25%: mean return +233.09%, return improved 4/4, mean MDD +1.04pp better, but P5 -3.50pp and CVaR -1.94pp worse.
- SELL 50%: mean return +154.96%, return improved 3/4, mean MDD +2.79pp better, but P5 -2.07pp and CVaR -1.41pp worse.
- SELL 75%: mean return +91.02%, return improved 3/4, MDD improved 4/4 by +4.12pp, but P5 -1.48pp and CVaR -0.93pp worse; SOL return materially underperformed the full-exit control.
- SELL 100% control: mean return +68.74%.

The partial policies capture the known right-tail behavior after SELL-C, but each worsens the loss-tail distribution. None passed the frozen admission gate.

Final:
- `CRYPTO_SELL_C_25 = REJECTED_NOT_ADMITTED`
- `CRYPTO_SELL_C_50 = REJECTED_NOT_ADMITTED`
- `CRYPTO_SELL_C_75 = REJECTED_NOT_ADMITTED`
- `CRYPTO_SELL_C_FULL = RETAINED`
- `CRYPTO_SELL_C_PARTIAL_STUDY_V1 = IMPLEMENTED_AND_VERIFIED`

Round CLOSED.

Stock open-issues audit performed in the same closure:
- no additional structurally undefined stock three-buy / three-sell rule was identified;
- stock 60% + BUY-C top-up and isolated A/B half exit remain clearly defined candidates awaiting genuine future OOS validation;
- SELL-C / multi full exit remains retained;
- no independent Risk Exit layer is used.

`STOCK_THREE_BUY_THREE_SELL_STRUCTURAL_OPEN_ISSUES = NONE_IDENTIFIED`

## Crypto V1 frozen baseline — 2026-10-01

The user designated the completed Crypto three-buy / three-sell research state as the first frozen Crypto baseline.

Name:
`Crypto V1`

Frozen behavior:
- initial BUY-A/B allocation 60%;
- W3 BUY-C top-up +40% to 100%;
- SELL-A/B/C all full exit;
- multi-family SELL full exit;
- no independent Risk Exit layer;
- signal confirmed only on completed bar close;
- execution at the next bar open, with no additional 24-hour wait.

The current evidence base is BTC / ETH / BNB / SOL Binance Spot UTC daily OHLCV. The execution principle can be applied to other timeframes, but those timeframes are not automatically validated by the daily Crypto V1 evidence.

Canonical file:
`research/ssss/CRYPTO_V1_BASELINE.md`

`CRYPTO_V1 = FROZEN_BASELINE`

Crypto V1 must remain an immutable reference control. Any later change requires a new experiment/version.

