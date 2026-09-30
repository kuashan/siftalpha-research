# ABT Source-XMA Walk-Forward — First Month Report

Status: EXPLORATORY / PREVIOUSLY SEEN  
Window: 2025-01-02 through 2025-01-31  
Initial paper capital: $10,000  
Execution: next tradable open, fractional shares, $0 commission, 5 bps one-way slippage.

## Data provenance

Primary ABT OHLCV:
- Devesh176/Replicating_portfolio — data/ABT.csv
- blob SHA: e9071f4a01e8f50cdab0155b0779ef09ef85e1d4

Cross-check ABT OHLCV:
- ahmedhussain47/xauusd-signal-engine — data/raw/ABT.csv
- blob SHA: 481a0358341edfccd4293f58d1e1571945de678b

Maximum absolute raw OHLCV difference across January matched rows: 0.00000000.

VIX context:
- curingd/risk-factor-decomposition — Data/VIX.csv
- blob SHA: fcc62747dabcfbcfb1ac8a76904f14b6bfdf57cf

## XMA rule

The fast structure is the source double-XMA:

```text
VH25_X = XMA(XMA(H,25),25)
VL25_X = XMA(XMA(L,25),25)
D       = VH25_X - VL25_X
FastUpper = VH25_X + D
FastLower = VL25_X - D
FastMid   = (VH25_X + VL25_X)/2
```

Every session is recomputed point-in-time using only bars through that session. XMA historical revisions are recorded separately; XMA is not replaced.

## The important January sequence

- 2025-01-15: price pierced the first-observed XMA lower boundary. SSSS emitted LOW_ICON and ADKBY-E emitted 多. Momentum was still BOTH_DOWN, so the independent action was only PROBE_LONG, not a full-size buy.
- 2025-01-16: price reclaimed FastMid and both momentum components turned up. Independent action: ENTER_LONG.
- 2025-01-21: price closed above FastUpper with BOTH_UP momentum and RVOL 1.65x. The source indicators simultaneously produced HIGH_ICON / 空 because they still classified the geometry as RANGE. The independent logic overrode the mean-reversion signal and chose ADD_LONG.
- 2025-01-22 to 2025-01-27: breakout follow-through continued with very strong relative volume.
- 2025-01-28: price remained deeply above the normalized upper extreme while momentum acceleration decelerated sharply. Independent action: REDUCE_LONG.
- 2025-01-30: slower momentum turned negative while price remained extended. Independent action: EXIT_LONG.
- 2025-01-31: after exit, both momentum components were down, but the structural regime was BULL. No short was opened.

## Position-management result

Paper actions:
- 30% probe executed 2025-01-16 open
- raise to 70% executed 2025-01-17 open
- raise to 100% executed 2025-01-22 open
- reduce to 70% executed 2025-01-29 open
- exit to 0% executed 2025-01-31 open

Net final capital after 5 bps one-way slippage: **$11345.49**  
Net January return: **13.45%**  
Close-to-close max drawdown of the paper equity curve: **-1.58%**

This is not an OOS performance claim. The month was already visually seen before this exercise and is used only for rule discovery.

## Why the two source indicators should be treated as one system

The January evidence confirms that their key signal geometry is shared. The most important failure case is 2025-01-21:

```text
same XMA upper-boundary event
+ source RANGE classification
=> source says 空 / high-side icon

but:
close > FastUpper
+ BOTH_UP momentum
+ elevated volume
=> independent logic says breakout, not mean reversion
```

The following sessions continued upward. Therefore a raw upper-band cross cannot be treated as an unconditional sell/short trigger.

If the source LONG/SHORT labels were followed literally with next-open execution, the Jan-15 LOW signal bought at Jan-16 open and the Jan-21 high-side signal exited at Jan-22 open for only **2.70%** net. If the Jan-21 空 label were interpreted as a literal reversal to short and covered Jan-31 open, that short leg would have returned **-12.59%** before borrow costs.

## Auxiliary-factor ablation

### Volume
- As a mandatory entry gate: HARMFUL in this month. The Jan-15/16 reversal did not have RVOL >= 1.5, so a strict volume gate would delay or miss the early setup.
- As breakout confirmation: HELPFUL. Jan-21 RVOL was >1.5 and Jan-22 >2.4 while price broke and held above FastUpper.
- Decision: retain volume as contextual confirmation, not a universal hard filter.

### VIX
VIX helped describe market risk but did not add a clean ABT entry/exit rule in January. It did not confirm the Jan-15 low, and an aggressive VIX-based de-risk rule could have reduced exposure during a still-valid ABT trend.
- Decision: NEUTRAL / CONTEXT ONLY for this month. Do not promote to a hard gate.

### Other external features
Heat, social sentiment, volume-profile/chip-distribution approximations, SPY/XLV relative strength, and other features remain candidates. None is promoted merely because it exists. Each must beat the XMA baseline in a later ablation test.

## XMA revision finding

XMA was kept exactly as required. The first-observed values near the right edge revised materially as later bars arrived. For example, the 2025-01-15 FastMid was 113.48 when first observed and 116.70 when recomputed through Jan-31.

This does not invalidate the track; it is why decisions are based on **first-observed point-in-time values** and why `revisions.csv` is maintained.

## Candidate January logic retained for the next exploratory month

```text
LOW EXTREME in non-BEAR regime
    -> small PROBE only

XMA mid reclaim + both momentum components turn up
    -> increase core long

FastUpper breakout + BOTH_UP + strong relative volume
    -> breakout override: do NOT obey automatic RANGE short
    -> add exposure

extreme-high + momentum deceleration
    -> reduce, not reverse short

extended price + slow momentum turns negative
    -> exit

BULL regime after exit
    -> no automatic short
```

No rule is promoted to production from this one month.
