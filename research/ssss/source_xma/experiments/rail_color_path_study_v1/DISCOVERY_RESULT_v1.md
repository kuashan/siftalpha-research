# SSSS Rail + Color Path Study v1 — Discovery Result

Status: DISCOVERY_COMPLETE / NOT_OOS
Date: 2026-10-01

## Scope

Universe:
- Equities: ABT, AAPL, AMZN, ORCL, INTC, MSFT, NVDA, GOOGL, META, JPM, XOM
- Crypto: BTC, ETH, BNB, SOL

Window:
- 2025-01 through 2025-06
- earlier data used as warm-up only

Method:
- point-in-time XMA
- RAW SOURCE state formulas are primary for rendered-color grouping
- canonical v1 used only as sensitivity/reference
- episode onset used for fast/outer rail excursions

Raw source state mapping:
- UP_STATE = source dark red band
- DOWN_STATE = source dark green band
- RANGE_STATE = source dark gray band
- EXPANSION_STRADDLE kept separate

Important:
The user's installed Futu theme may visually render the second state differently. Formula state id is the authority.

---

## 1. Fast lower-rail excursion: low < ZD1

Path horizon: next 20 bars.

### UP_STATE / source dark red
n = 30
- +5 mean return: -0.62%
- +5 positive rate: 43.3%
- +10 mean: -1.05%
- +20 mean: -3.41%
- reaches fast upper rail within 20 bars: 36.7%
- reaches midpoint but not upper: 46.7%
- continues lower without midpoint recovery: 16.7%

Interpretation:
Lower-rail break in UP/red is not automatically a strong buy. Most recover at least to midpoint, but full return to upper rail is only about one third in this Discovery sample.

### DOWN_STATE / source dark green
n = 43
- +5 mean: +2.01%
- +5 positive rate: 62.8%
- +10 mean: +5.22%
- +20 mean: +8.92%
- reaches fast upper rail: 60.5%
- reaches midpoint only: 37.2%
- continues lower without midpoint: 2.3%

Interpretation:
Counterintuitively, the DOWN-state lower excursion had the strongest subsequent rebound distribution in this sample. It must not be promoted directly because this is Discovery and may include capitulation/reversal selection effects.

### RANGE_STATE / source dark gray
n = 24
- +5 mean: +1.10%
- +5 positive rate: 50.0%
- +10 mean: +0.75%
- +20 mean: +2.71%
- reaches fast upper rail: 70.8%
- reaches midpoint only: 29.2%
- continues lower without midpoint: 0%

Interpretation:
Gray/range lower excursions showed the highest probability of traversing back to the fast upper rail within 20 bars, although short-horizon average return was modest.

---

## 2. Fast upper-rail excursion: high > ZK1

### UP_STATE / source dark red
n = 38
usable +5 n = 34
- +5 mean: -1.85%
- +5 positive rate: 38.2%
- +10 mean: -2.87%
- +20 mean: -5.20%
- reaches fast lower rail within 20 bars: 52.6%
- reaches midpoint but not lower: 44.7%
- unresolved without midpoint/lower: 2.6%

Midpoint support after falling from above:
- midpoint touched: n = 31
- holds midpoint for 3 bars: 19.4%
- among first-decision paths (upper-before-lower vs lower-before-upper), rebounds to upper before lower: 42.9%

Interpretation:
In UP/red, an upper-rail excursion is materially more exhaustion-like than continuation-like in this sample. Midpoint is frequently reached, but is not a high-probability hard support under the current strict 3-bar definition.

### DOWN_STATE / source dark green
n = 31
- +5 mean: +1.98%
- +5 positive rate: 61.3%
- +10 mean: +3.60%
- +20 mean: +7.83%
- reaches fast lower rail: 48.4%
- midpoint only: 51.6%

Midpoint support:
- 3-bar hold after touch: 36.4%
- rebound to upper before lower: 36.8%

Interpretation:
An upper-rail excursion in DOWN-state is not a clean sell. It often behaves as a rebound/transition episode.

### RANGE_STATE / source dark gray
n = 26
usable +5 n = 24
- +5 mean: +0.68%
- +5 positive rate: 50.0%
- +10 mean: +0.22%
- +20 mean: +2.61%
- reaches fast lower rail: 42.3%
- midpoint only: 53.8%

Midpoint support:
- 3-bar hold: 35.0%
- rebound to upper before lower: 60.0%

Interpretation:
Gray/range upper excursions are mixed, and the midpoint behaves more like a pivot than an absolute support.

---

## 3. Outer rails alone

### Lower outer rail BD touch/break

UP_STATE:
- n = 13
- +5 mean: -0.69%
- +5 positive: 38.5%
- +10 mean: +0.85%
- +20 mean: -3.82%

DOWN_STATE:
- n = 36
- +5 mean: +1.20%
- +5 positive: 58.3%
- +10 mean: +2.64%
- +20 mean: +2.14%

RANGE_STATE:
- n = 9
- +5 mean: +1.99%
- +5 positive: 55.6%
- +10 mean: +7.42%
- +20 mean: +2.27%

Conclusion:
BD is not a universal support by itself. Its behavior is strongly state-dependent.

### Upper outer rail BS touch/break

UP_STATE:
- n = 22
- usable +5 n = 21
- +5 mean: -1.17%
- +5 positive: 47.6%
- +10 mean: -1.02%
- +20 mean: -3.90%

DOWN_STATE:
- n = 12
- +5 mean: +2.79%
- +5 positive: 66.7%
- +10 mean: +1.42%
- +20 mean: +6.45%

RANGE_STATE:
- n = 17
- usable +5 n = 15
- +5 mean: +2.61%
- +5 positive: 73.3%
- +10 mean: +1.21%
- +20 mean: +3.54%

Conclusion:
BS alone is not a universal resistance/sell point. The prior study's stronger bearish result came from the stricter geometry:
UP_STATE + fast upper ZK1 + outer upper BS confluence.
That confluence remains more informative than BS alone.

---

## 4. Light-gray slow band GZB3..GZB4

Support-side event:
price approaches from above and touches/enters the light-gray band.

UP_STATE:
- n = 56
- +5 mean: -1.24%
- +5 positive: 42.9%
- +10 mean: -1.67%
- +20 mean: -3.24%

DOWN_STATE:
- n = 7
- +5 mean: -0.05%
- +5 positive: 57.1%
- +10 mean: +1.24%
- +20 mean: -3.27%

RANGE_STATE:
- n = 40
- usable +5 n = 37
- +5 mean: -0.87%
- +5 positive: 45.9%
- +10 mean: -0.66%
- +20 mean: +0.94%

Resistance-side event:
price approaches from below and touches/enters the light-gray band.

UP_STATE:
- n = 17
- +5 mean: -1.29%
- +5 positive: 35.3%
- +10 mean: -1.50%
- +20 mean: -5.81%

DOWN_STATE:
- n = 45
- +5 mean: +1.80%
- +5 positive: 51.1%
- +10 mean: +1.55%
- +20 mean: +3.97%

RANGE_STATE:
- n = 49
- usable +5 n = 48
- +5 mean: +0.54%
- +5 positive: 45.8%
- +10 mean: +1.48%
- +20 mean: +2.48%

Conclusion:
The light-gray band is not well described as:
"from above = support, from below = resistance".

It is a slow structural/regime band. The same touch has different meaning depending on fast-band state, penetration type, and later state transition. It should be studied as a structural interaction zone, not a single-line support/resistance rule.

---

## Discovery conclusions

1. The five-rail decomposition is analytically valid:
   BD / ZD1 / GZB18 / ZK1 / BS.
2. GZB18 is mathematically defined but not explicitly plotted in the preserved SSSS source.
3. Fast lower excursions must be conditioned on state; they are not one universal buy rule.
4. Fast upper excursions in UP/red show the clearest exhaustion tendency.
5. Midpoint is a meaningful path pivot, but not a uniformly strong support under a strict 3-bar hold definition.
6. Outer rails alone are weaker than fast+outer confluence geometry.
7. The light-gray GZB3..GZB4 band is a slow regime/structure layer, not a simple support/resistance strip.
8. None of these Discovery findings is promoted to a production trading rule yet.
