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
