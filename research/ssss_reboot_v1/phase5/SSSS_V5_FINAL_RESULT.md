# SSSS V5 — 20 New Stocks + 4 Crypto Final Optimization Result

Status: **COMPLETE**
Date: 2026-10-02
Window: **2020-01-02 through 2026-09-30**
Representation: **FIRST_OBSERVED**
XMA: **UNCHANGED**

## 1. Coverage

20 new mainstream stocks, none overlapping the prior 39-stock universe:

IBM, CSCO, CRM, ADBE, TXN,
DIS, NKE, SBUX, TGT, LOW,
MRK, PFE, ABBV, AMGN, GILD,
C, MS, BLK, COP, UPS.

Crypto:
BTC/USD, ETH/USD, BNB/USD, SOL/USD.

SOL lacks pre-2020 history at the provider, so its first 180 returned daily bars
were warm-up; its formal sample starts 2021-02-07.

Stock event counts:
- LOWER: 1524
- UPPER: 1642
- LIGHT_SUPPORT: 1248
- LIGHT_RESIST: 1168

Crypto event counts:
- LOWER: 375
- UPPER: 384
- LIGHT_SUPPORT: 318
- LIGHT_RESIST: 287

## 2. Eight previously validated V3 rules

| Rule | V5 optimization | Stock status | Stock n | Stock p | Stock breadth | Crypto status | Crypto n | Crypto p |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| BUY_BLUE_21P_LOWER | KEEP_STRONG_CROSS_ASSET | STRONG_REPEAT | 515 | 69.9% | 19/20 | STRONG_REPEAT | 124 | 82.3% |
| BUY_GRAY_4_10_LIGHT_SUPPORT | KEEP_STRONG_CROSS_ASSET | STRONG_REPEAT | 167 | 75.4% | 19/19 | STRONG_REPEAT | 53 | 81.1% |
| BUY_RECENT_BLUE_GRAY_LIGHT_SUPPORT | KEEP_STRONG_CROSS_ASSET | STRONG_REPEAT | 57 | 75.4% | 6/7 | STRONG_REPEAT | 28 | 85.7% |
| CONT_BLUE_11_20_UPPER | KEEP_STRONG_CROSS_ASSET | STRONG_REPEAT | 86 | 83.7% | 16/17 | STRONG_REPEAT | 20 | 70.0% |
| SELL_RECENT_BLUE_GRAY_LIGHT_RESIST | KEEP_STRONG_CROSS_ASSET | STRONG_REPEAT | 100 | 76.0% | 16/17 | STRONG_REPEAT | 20 | 85.0% |
| AVOID_GREEN_11_20_LOWER | KEEP_STRONG_STOCK | STRONG_REPEAT | 85 | 78.8% | 15/16 | INSUFFICIENT_BREADTH | 11 | 81.8% |
| CONT_BLUE_4_10_UPPER | KEEP_STRONG_STOCK | STRONG_REPEAT | 66 | 81.8% | 11/13 | INSUFFICIENT_BREADTH | 14 | 85.7% |
| CONT_RECENT_GRAY_BLUE_UPPER | KEEP_STRONG_STOCK | STRONG_REPEAT | 61 | 70.5% | 7/10 | INSUFFICIENT_BREADTH | 6 | 100.0% |

### Interpretation

All eight previously validated rules survived the new 20-stock test.

Five remain strong across both stocks and crypto:
- BUY_BLUE_21P_LOWER
- BUY_GRAY_4_10_LIGHT_SUPPORT
- BUY_RECENT_BLUE_GRAY_LIGHT_SUPPORT
- CONT_BLUE_11_20_UPPER
- SELL_RECENT_BLUE_GRAY_LIGHT_RESIST

Three are STRONG_REPEAT in the new stocks, while crypto has the same directional
tendency but insufficient breadth:
- AVOID_GREEN_11_20_LOWER
- CONT_BLUE_4_10_UPPER
- CONT_RECENT_GRAY_BLUE_UPPER

No previously validated V3 rule is demoted by V5.

## 3. Five V3 discoveries

| Rule | V5 optimization | Stock status | Stock n | Stock p | Stock breadth | Crypto status | Crypto n | Crypto p |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| BLUE_11_20_LOWER_WICK_ONLY | PROMOTE_V5 | STRONG_REPEAT | 53 | 84.9% | 12/12 | INSUFFICIENT_BREADTH | 7 | 71.4% |
| GREEN_11_20_LOWER_CLOSE_BELOW | PROMOTE_V5 | STRONG_REPEAT | 39 | 92.3% | 8/8 | INSUFFICIENT_BREADTH | 6 | 100.0% |
| BLUE_11_20_UPPER_CLOSE_ABOVE | WATCH | INSUFFICIENT_BREADTH | 41 | 85.4% | 5/6 | INSUFFICIENT_BREADTH | 7 | 100.0% |
| BLUE_21P_UPPER_FULL_ABOVE | WATCH | INSUFFICIENT_BREADTH | 18 | 100.0% | 2/2 | INSUFFICIENT_BREADTH | 0 | — |
| GREEN_4_10_UPPER | PROMOTE_V5 | REPEAT | 52 | 63.5% | 8/10 | INSUFFICIENT_BREADTH | 7 | 71.4% |

### Promotion decisions

**PROMOTE_V5**
1. BLUE_11_20_LOWER_WICK_ONLY
   - stocks: n=53
   - MID-before-BD 84.9%
   - supporting eligible stocks 12/12
   - this independently repeats the prior 85.1% discovery.

2. GREEN_11_20_LOWER_CLOSE_BELOW
   - stocks: n=39
   - BD-before-MID 92.3%
   - supporting eligible stocks 8/8
   - strengthens the existing broad GREEN 11-20 avoid-buy rule.

3. GREEN_4_10_UPPER
   - stocks: n=52
   - MID-before-BS 63.5%
   - supporting eligible stocks 8/10
   - repeats, but more moderately than the original 71.3% discovery.

**WATCH / not promoted**
4. BLUE_11_20_UPPER_CLOSE_ABOVE
   - stocks: n=41
   - BS-before-MID 85.4%
   - only 6 symbols met the >=3-event breadth condition; protocol required 7.
   - high probability, but insufficient breadth.
   - the broader parent rule CONT_BLUE_11_20_UPPER is already strongly validated.

5. BLUE_21P_UPPER_FULL_ABOVE
   - stocks: n=18
   - BS-before-MID 100.0%
   - too rare for breadth qualification.
   - kept as a rare-event watch condition rather than a standalone operation rule.

## 4. Three previous MIXED rules

| Rule | V5 optimization | Stock status | Stock n | Stock p | Stock breadth | Crypto status | Crypto n | Crypto p |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| BUY_GREEN_21P_LOWER | REMAIN_MIXED | MIXED | 303 | 41.9% | 2/19 | MIXED | 64 | 54.7% |
| AVOID_RECENT_GRAY_GREEN_LOWER | REMAIN_MIXED | REPEAT | 48 | 60.4% | 5/7 | INSUFFICIENT_BREADTH | 11 | 81.8% |
| SELL_GREEN_21P_UPPER | REMAIN_MIXED | REPEAT | 392 | 61.0% | 13/20 | REPEAT | 97 | 60.8% |

### Interpretation

- BUY_GREEN_21P_LOWER remains weak/mixed:
  stock MID-before-BD 41.9% across n=303.
  It should not be restored as a general BUY rule.

- AVOID_RECENT_GRAY_GREEN_LOWER improves to stock REPEAT at
  60.4%, but because it
  entered V5 as a MIXED rule, the frozen promotion discipline requires
  STRONG_REPEAT. It therefore remains MIXED/WATCH.

- SELL_GREEN_21P_UPPER repeats moderately in both stocks
  (61.0%) and crypto
  (60.8%), but it does not meet
  the stricter promotion threshold for a previously mixed rule. Keep as WATCH.

## 5. Optimized operation structure after V5

### BUY / support

**Core BUY-1 — BLUE 21+ + new inner-lower break**
- new stocks: 69.9% MID-before-BD, n=515
- crypto: 82.3%, n=124
- KEEP_STRONG_CROSS_ASSET

**Core BUY-2 — GRAY 4-10 + true light-gray support from above**
- stocks: 75.4%
- crypto: 81.1%
- KEEP_STRONG_CROSS_ASSET

**Core BUY-3 — recent BLUE->GRAY + true light-gray support**
- stocks: 75.4%
- crypto: 85.7%
- KEEP_STRONG_CROSS_ASSET

**New promoted BUY-4 — BLUE 11-20 + LOWER + WICK_ONLY**
- stocks: 84.9%
- PROMOTE_V5

### Do not buy yet / wait for lower target

**Core AVOID-BUY — GREEN 11-20 + LOWER**
- stocks: 78.8% BD-before-MID

**Stronger confirmation — GREEN 11-20 + LOWER + CLOSE_BELOW**
- stocks: 92.3% BD-before-MID
- PROMOTE_V5
- this is best treated as a higher-severity refinement of the broad avoid-buy rule, not as an unrelated rule.

### HOLD / do not sell at inner upper rail

**Core HOLD-1 — BLUE 11-20 + UPPER**
- stocks: 83.7% BS-before-MID
- crypto: 70.0%

**Core HOLD-2 — BLUE 4-10 + UPPER**
- stocks: 81.8% BS-before-MID

**Core HOLD-3 — recent GRAY->BLUE + UPPER**
- stocks: 70.5% BS-before-MID

The CLOSE_ABOVE refinement for BLUE 11-20 remains a confidence booster, not a
separate promoted rule in V5 because breadth was one symbol short of the
preregistered threshold.

### SELL / trim

**Core SELL-1 — recent BLUE->GRAY + true light-gray resistance from below**
- stocks: 76.0%
- crypto: 85.0%
- KEEP_STRONG_CROSS_ASSET

**New promoted SELL-2 — GREEN 4-10 + UPPER**
- stocks: 63.5% MID-before-BS
- PROMOTE_V5
- useful, but weaker than the strongest BUY/HOLD structures.

## 6. MIXED / watch list

Do not use as core operation rules yet:
- GREEN 21+ + LOWER BUY
- recent GRAY->GREEN + LOWER avoid-buy
- GREEN 21+ + UPPER sell
- BLUE 21+ + UPPER + FULL_ABOVE as standalone rare-event rule
- BLUE 11-20 + UPPER + CLOSE_ABOVE as standalone rule; use only as supporting detail under the already validated BLUE 11-20 UPPER HOLD rule

## 7. V5 exploratory scan

The preregistered discovery threshold was intentionally strict:
- stock pooled n >= 40
- >= 8 eligible stocks
- pooled primary probability >= 70%
- support fraction >= 75%

Several patterns passed. The most useful *genuinely new or refining* findings are:

### NEW-V5-A — GREEN->GRAY, GRAY age 1-3, light-gray support
- n=48
- SUPPORT_HOLD = 87.5%
- 9 eligible stocks
- 100% of eligible stocks support the direction
- label: NEW_V5_DISCOVERY_REQUIRES_FUTURE_VALIDATION

### NEW-V5-B — BLUE 21+ + UPPER + CLOSE_ABOVE
- n=228
- BS-before-MID = 82.9%
- 20 eligible stocks
- 95% of eligible stocks support
- this is much less sparse than FULL_ABOVE and may be a better future refinement
- label: NEW_V5_DISCOVERY_REQUIRES_FUTURE_VALIDATION

### NEW-V5-C — GRAY 4-10 + LOWER + WICK_ONLY
- n=45
- MID-before-BD = 82.2%
- 9 eligible stocks
- 77.8% support
- label: NEW_V5_DISCOVERY_REQUIRES_FUTURE_VALIDATION

### NEW-V5-D — GREEN 11-20 + UPPER + WICK_ONLY
- n=49
- MID-before-BS = 77.6%
- 8 eligible stocks
- 87.5% support
- may be a more precise upper-rail sell context than the broad GREEN 21+ rule
- label: NEW_V5_DISCOVERY_REQUIRES_FUTURE_VALIDATION

### NEW-V5-E — GREEN 11-20 + true light-gray resistance
- n=88
- RESIST_HOLD = 78.4%
- 16 eligible stocks
- 93.8% support
- label: NEW_V5_DISCOVERY_REQUIRES_FUTURE_VALIDATION

No other new finding should be promoted merely because it appeared in the scan.

## 8. Final V5 conclusion

V5 did **not** overturn the existing validated core.

- 8 / 8 V3 validated rules remain retained.
- 3 / 5 V3 discoveries are promoted on the new 20-stock sample.
- 2 / 5 remain WATCH because of breadth/sparsity.
- 3 / 3 previous MIXED rules remain outside the core.
- 5 exploratory V5 refinements are worth a future untouched validation round.

The practical optimization is therefore not to add every strong percentage as
a separate operation rule. The better structure is:

1. keep the eight validated core conditions;
2. add BLUE 11-20 lower wick-only as a new BUY condition;
3. strengthen GREEN 11-20 lower avoid-buy when the close is below the rail;
4. add GREEN 4-10 upper as a moderate SELL/mean-reversion condition;
5. treat BLUE 11-20 upper close-above as a confidence booster inside the already validated HOLD rule;
6. keep BLUE 21+ full-above as rare supporting evidence, not its own rule;
7. keep all three old mixed conditions outside the core.

`SSSS_V5_20_NEW_STOCK_4_CRYPTO = COMPLETE`
