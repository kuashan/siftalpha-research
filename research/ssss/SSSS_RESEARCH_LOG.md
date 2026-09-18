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
