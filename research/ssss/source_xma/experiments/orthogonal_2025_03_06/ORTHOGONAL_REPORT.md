# Orthogonal Feature Re-test — March to June 2025

Status: EXPLORATORY / NOT OOS  
Protocol: `PROTOCOL_FROZEN_BEFORE_RUN.md`  
Retrieval amendment: `PROTOCOL_AMENDMENT_BEFORE_RUN.md`

## Chronology guarantee

This run follows the user's required XMA chronology.

For equities:
- first evaluation bar = 2025-03-03

For crypto:
- first evaluation bar = 2025-03-01

For each evaluation bar t:
- Source-XMA is calculated with data available only through t;
- first-observed right-edge XMA is used;
- later bars never rewrite the trading decision for t;
- the next date is processed only after t is complete.

Earlier historical bars are used only as warm-up for EMA/XMA/rolling features.

This is a forward walk from the first evaluation day, not a today-to-past chart replay.

Execution model:
`SAME_BAR_CLOSE_PROXY_V3`
with 5 bps adverse slippage.

Daily data cannot recover the exact intraday minute of first confirmation, so the current close is still a proxy.

## What changed from the prior experiment

HYS2 and FIVEGZ do **not** control any trade.

The core is Source-XMA only.

Orthogonal candidates:
1. Volume Structure
2. VIX risk/sentiment
3. Market Breadth proxy
4. Daily Volume Profile proxy

They may change position size or suppress an XMA entry/add, but cannot create an independent signal.

## Equity results — 11 symbols

| Variant | Mean | Median | Positive | Worst | Best | Mean DD |
|---|---:|---:|---:|---:|---:|---:|
| XMA_ONLY | +1.786% | +2.784% | 6/11 | -10.340% | +17.845% | -3.972% |
| XMA_VOLUME | +1.842% | +2.952% | 6/11 | -15.216% | +21.153% | -4.516% |
| XMA_VIX | +1.786% | +2.784% | 6/11 | -10.340% | +17.845% | -3.972% |
| XMA_BREADTH | +1.589% | +2.643% | 6/11 | -13.690% | +20.582% | -3.993% |
| XMA_VOLPROFILE | +1.781% | +2.733% | 6/11 | -11.245% | +18.120% | -4.146% |
| XMA_VOLUME_BREADTH | +1.689% | +3.312% | 6/11 | -17.034% | +21.709% | -4.472% |
| XMA_VOLUME_BREADTH_VIX | +1.689% | +3.312% | 6/11 | -17.034% | +21.709% | -4.472% |
| XMA_ORTHO_ALL | +1.967% | +1.548% | 6/11 | -17.769% | +26.185% | -4.589% |

## Equity ablation

### Volume Structure

Compared with XMA_ONLY:
- improved 8/11 symbols
- harmed 3/11
- median return delta: +0.168 percentage points
- trimmed mean: +1.592% vs XMA baseline +1.349%

But:
- worst outcome worsened from -10.34% to -15.22%
- average max drawdown also worsened

Interpretation:
**Volume carries incremental information, but the frozen sizing rule over-weights it in some bad setups.**

INTC is the clearest failure:
positive volume structure increased size on June XMA confirmations, but the underlying XMA trade still failed.

ORCL is the opposite:
volume confirmation raised breakout exposure and materially improved the trend capture.

Therefore volume should remain, but likely as:
**breakout-quality confirmation / exposure cap**, not a generic position amplifier.

### VIX

XMA_VIX was numerically identical to XMA_ONLY.

On the recorded XMA decision events, the frozen VIX score was neutral.

This is a valid null result:
- do not claim VIX is useless;
- do not loosen the thresholds after seeing the result;
- record that this VIX rule did not alter March–June decisions.

### Breadth proxy

Breadth:
- improved 5 stocks
- harmed 5
- unchanged 1
- mean delta negative

It helped some trend names but made AMZN/INTC materially worse.

The 15-name proxy is useful for context but is not strong enough to control sizing on its own.

### Volume Profile proxy

Daily Volume Profile proxy:
- improved 6
- harmed 5
- median incremental effect slightly positive
- overall mean almost unchanged

This is closer to **neutral/slightly helpful** than a new alpha engine.

It remains interesting because it is structurally different from XMA, but exact Volume Profile still requires intraday volume-at-price.

### All orthogonal factors

XMA_ORTHO_ALL produced the highest raw equity mean (+1.967%).

But this is not the best robust result:
- median fell to +1.548%
- worst stock fell to -17.769%
- drawdown worsened
- ORCL (+26.185%) contributed disproportionately

Therefore:
**the "use everything" hypothesis fails again.**

## Crypto results — BTC / ETH / BNB / SOL

| Variant | Mean | Median | Positive | Worst | Best | Mean DD |
|---|---:|---:|---:|---:|---:|---:|
| XMA_ONLY | +0.748% | -0.764% | 2/4 | -3.141% | +7.660% | -6.451% |
| XMA_VOLUME | +0.550% | -1.083% | 2/4 | -3.358% | +7.723% | -7.228% |
| XMA_VIX | +0.748% | -0.764% | 2/4 | -3.141% | +7.660% | -6.451% |
| XMA_BREADTH | +0.966% | -0.706% | 2/4 | -3.556% | +8.834% | -6.855% |
| XMA_VOLPROFILE | +0.887% | -0.686% | 2/4 | -3.251% | +8.170% | **-6.352%** |
| XMA_VOLUME_BREADTH | -3.754% | -4.549% | 1/4 | -6.600% | +0.681% | -8.490% |
| XMA_VOLUME_BREADTH_VIX | -3.754% | -4.549% | 1/4 | -6.600% | +0.681% | -8.490% |
| XMA_ORTHO_ALL | -2.860% | -4.016% | 1/4 | -6.702% | +3.292% | -8.461% |

## Crypto interpretation

A major result changed after removing the same-source technical overlays:

**pure XMA itself is not bad in this March–June window.**

Its average is positive, though the median remains negative because ETH drives most of the positive mean.

The strongest auxiliary candidate by balance is currently the daily Volume Profile proxy:
- slightly higher mean than XMA_ONLY
- slightly better median
- slightly lower average drawdown

Crypto breadth raises mean more, but worsens drawdown.

The big failure is interaction:
Volume + Breadth together aggressively increased exposure during synchronized crypto rallies and then amplified later reversals.

Example ETH:
- XMA breakout positions were 70%
- positive Volume + Breadth raised them to 90%
- this produced a worse total path even though the initial breakout was real

Therefore:
**orthogonal factors should not simply add their position-size bonuses linearly.**

## Provisional conclusion

### Equities

The cleanest research interpretation is:

```text
PRIMARY:
Source-XMA only

USEFUL AUXILIARY:
Volume Structure

SECONDARY / OBSERVATIONAL:
Daily Volume Profile proxy
Breadth
VIX
```

No orthogonal variant dominates XMA_ONLY on both return and downside.

Volume has the clearest repeated incremental signal, but should not automatically increase size.

### Crypto

Current candidate:

```text
PRIMARY:
Source-XMA

SELECTIVE AUXILIARY:
Volume Profile proxy

CONTEXT:
crypto breadth

DO NOT:
linearly stack Volume + Breadth + Profile sizing bonuses
```

### Core lesson

The simpler model is winning the robustness test.

Orthogonal data are valuable when they answer a **specific question**:
- Is this breakout participated by real volume?
- Is price above or below a meaningful traded-value region?
- Is the market broadly participating?
- Is market fear expanding or contracting?

They become harmful when converted into an additive "more indicators = more position" score.

## Next candidate design

Do not re-run March–June with tuned thresholds.

For the next unseen period:
- XMA keeps all direction/timing authority.
- Volume may confirm or cap a breakout, but not boost every entry.
- Volume Profile may classify support/resistance context.
- Breadth and VIX remain non-trading context until they prove stable.
- no automatic shorting.
