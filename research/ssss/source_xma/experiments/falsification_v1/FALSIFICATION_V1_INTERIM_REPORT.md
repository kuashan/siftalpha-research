# Falsification v1 — Interim Decision Report

Status: INTERIM / PRIMARY GEOMETRY FALSIFICATION COMPLETE  
Date: 2026-09-28

## Executive conclusion

The Jan–Jun 2025 Discovery effects do **not** survive broad falsification as universal trading rules.

This is the most important result of the current research cycle.

The study deliberately kept the canonical geometry thresholds unchanged and expanded:

- equities from 11 to 39 symbols;
- historical holdout to 2020–2024;
- forward holdout to 2025H2;
- sector/SPY relative-return controls;
- same-state controls;
- nearest-neighbor controls matched on MA20 extension, prior-20 return, and ATR/price;
- clustered bootstrap and leave-one-symbol/month robustness;
- penetration/reclaim decomposition;
- independent state-transition and FAST_MID_ANALYTIC studies.

The sealed 2026H1 window remains unused.

---

## 1. Upper strict confluence — the original strong Discovery effect does not replicate

Frozen event:

```text
state = UP
candle overlaps ZK1 + BS
abs(ZK1-BS) <= 0.25 ATR14
episode dedup = first event within 3 bars
```

Discovery Jan–Jun 2025 had suggested a strongly negative post-event distribution.

### Validation A — 2020–2024 equities

n = 392 independent episodes.

5-bar:
- absolute mean: +0.13%
- median: +0.15%
- SPY excess: +0.07%
- sector ETF excess: +0.16%
- same-state excess: +0.01%
- MA20/prior-return/ATR matched-control excess: +0.25%

Matched-control symbol-cluster 95% bootstrap interval:
- -0.28% to +0.72%

Calendar-month cluster interval:
- -0.37% to +0.83%

The interval spans zero and the point estimate is opposite the Discovery bearish effect.

### Validation B — 2025H2 equities

n = 46 episodes.

5-bar:
- absolute mean: -0.63%
- sector ETF excess: -0.34%
- matched-control excess: -1.67% on 39 matchable events

Symbol-cluster bootstrap:
- -4.11% to +0.34%

Again the interval spans zero.

### Combined equities

n = 438.

5-bar:
- absolute mean: +0.05%
- SPY excess: -0.01%
- sector ETF excess: +0.11%
- matched-control excess: +0.08%

Matched-control bootstrap:
- symbol clusters: -0.41% to +0.51%
- month clusters: -0.57% to +0.69%

No single symbol dominates:
- max symbol share ≈ 5.0%

### Crypto

The sign reverses even more clearly.

Upper strict confluence:
- Validation A n=41, 5-bar absolute mean +2.95%
- matched-control excess +0.19%
- Validation B n=5, absolute mean +2.15%

Therefore the initial "upper strict confluence -> top/decline" effect is not cross-market robust.

### Decision

**REJECT AS A GENERAL RULE.**

Do not use:
`upper confluence => sell/short/top`.

The geometry may still matter in a narrower lifecycle context, but that narrower context must be newly preregistered and tested in the sealed 2026 window.

---

## 2. Lower strict confluence — absolute rebound was largely generic mean reversion

Frozen event:

```text
state = DOWN
candle overlaps ZD1 + BD
abs(ZD1-BD) <= 0.50 ATR14
```

### Validation A — 2020–2024 equities

n = 325.

10-bar absolute:
- mean +0.82%
- median +0.92%

At first glance this resembles the Discovery delayed-rebound hypothesis.

But controls reverse the interpretation:

- sector ETF excess: +0.58%
- same-DOWN-state excess: -1.69%
- nearest-neighbor matched excess: **-3.29%**

Matched controls use:
- same symbol;
- same DOWN state;
- matched MA20 deviation;
- matched prior-20 return;
- matched ATR/price.

Symbol-cluster 95% bootstrap:
- **-4.63% to -1.78%**

Month-cluster 95% bootstrap:
- **-4.68% to -1.60%**

Leave-one-symbol-out:
- every result remains negative;
- range approximately -3.42% to -2.91%.

This is strong evidence that the positive raw rebound was not unique to the rail confluence.

### Validation B — 2025H2 equities

n = 20.

10-bar:
- absolute mean -0.97%
- sector excess -1.10%
- matched excess -1.39% on 12 matchable events

Small sample, but not supportive.

### Combined equities

n = 345.

10-bar:
- absolute mean +0.72%
- SPY excess +0.52%
- sector excess +0.50%
- same-state excess -1.67%
- matched excess **-3.22%**

Symbol-cluster 95% bootstrap:
- **-4.56% to -1.74%**

Month-cluster:
- **-4.60% to -1.63%**

Max single-symbol event share ≈ 7.2%.

### Crypto

Lower confluence also fails the matched-control test:

Validation A:
- n=37
- raw 10-bar +2.29%
- matched excess **-6.17%**

Validation B:
- n=7
- raw +5.53%
- matched excess -2.02%

Thus even where absolute rebound exists, comparable DOWN-state controls rebound more.

### Decision

**REJECT AS A GENERAL EXCESS-RETURN BUY RULE.**

The event may describe "extreme/dislocated price" but it does not establish an incremental buy edge by itself.

---

## 3. Penetration / same-bar reclaim decomposition

The lower event was split using the frozen 0.25 ATR penetration rule.

### Shallow interaction

Combined:
- n=133
- raw 10-bar +1.15%
- matched excess -3.35%

### Deep pierce + reclaim

Combined:
- n=67
- raw 10-bar -0.26%
- matched excess -3.44%

### Deep pierce + no reclaim

Combined:
- n=145
- raw 10-bar +0.78%
- matched excess -2.99%

Therefore the earlier weak performance of same-bar reclaim is not explained only by one extreme outlier category.

Deep reclaim is not superior.

### Decision

- Current same-bar reclaim rule: **DROP**
- Deep penetration itself: **not a validated buy confirmation**
- Shallow interaction: **not validated**

---

## 4. Independent state-transition study

State transitions were tested independently from confluence.

### DOWN -> RANGE

Validation A:
- n=284
- 5-bar raw +0.43%
- matched excess -0.65%

Validation B:
- n=17
- 5-bar raw -0.36%
- matched excess -0.96%

No incremental advantage.

### RANGE -> UP

Validation A:
- n=367
- 5-bar raw +0.17%
- matched excess -0.29%

Validation B:
- n=33
- 5-bar raw +0.63%
- matched excess -0.19%

No meaningful standalone edge.

### UP -> RANGE

Validation A:
- n=338
- 5-bar raw +0.44%
- matched excess +0.37%

Validation B:
- n=33
- 5-bar raw +0.86%
- matched excess +0.41%

This does **not** behave like an automatic bearish transition.

### RANGE -> DOWN

Validation A:
- n=290
- 5-bar raw +0.06%
- matched excess -0.24%

Validation B:
- n=20
- 5-bar raw +0.17%
- matched excess +1.23%

Mixed.

### Direct jumps

DOWN -> UP:
- no observations in the equity validation sample.

UP -> DOWN:
- only n=2 in Validation A;
- both large negative outcomes;
- sample far too small to use.

### Decision

State color transitions are important descriptive state variables, but the common transitions are **not standalone directional signals**.

They remain lifecycle context.

---

## 5. FAST_MID_ANALYTIC independent study

Analytic midpoint:

`GZB18 = (ZK1+ZD1)/2`

It is still not claimed to be the visually observed middle white rail.

Large-sample independent crossings:

### Cross above

Validation A:
- n=2886
- 5-bar mean +0.33%
- 10-bar +0.94%
- 20-bar +1.73%

Validation B:
- n=304
- 5-bar +0.83%
- 10-bar +1.47%
- 20-bar +2.40%

### Cross below

Validation A:
- n=2905
- 5-bar +0.33%
- 10-bar +0.69%
- 20-bar +1.41%

Validation B:
- n=312
- 5-bar +0.74%
- 10-bar +1.53%
- 20-bar +2.90%

Both directions have positive absolute forward return because of underlying market drift.

Therefore midpoint crossing alone is not yet directional evidence.

### Decision

**Do not promote midpoint reclaim/loss as an independent signal.**

It should only be re-tested as a conditional lifecycle event after a preregistered precursor.

---

## 6. Event independence and concentration

Equity strict-event totals:
- upper: 438 episodes
- lower: 345 episodes

Discovery sample-size weakness has been removed.

No single symbol dominates:
- upper max symbol share ≈5.0%
- lower ≈7.2%

But time clustering is real:
- upper events collapse into ~151 broad event waves under a rough global-date grouping;
- lower into ~114 waves.

Therefore naive iid significance would still overstate certainty.

The clustered bootstrap and month/symbol sensitivity checks remain the preferred uncertainty measures.

---

## 7. What has actually survived

The following **did not** survive as general rules:

- upper strict confluence => top/decline
- lower strict confluence => delayed excess-return buy
- same-bar deep reclaim => better lower signal
- DOWN->RANGE => buy confirmation
- RANGE->UP => standalone trend confirmation
- UP->RANGE => automatic deterioration
- FAST_MID cross direction => standalone directional signal

This does not mean XMA geometry is useless.

It means the broad versions of the hypotheses were too general.

The research must now ask whether a **specific conditional sequence** has incremental information, rather than repairing the failed rule on the same holdout.

---

## 8. Still-open preregistered falsification tasks

Not yet promoted or rejected in this interim report:

1. lower confluence x BELOW_VAL interaction on the expanded holdout;
2. HYS2 2x2 interaction / logistic model;
3. Volume capitulation interaction with adequate n;
4. time-to-state-change and time-to-midpoint survival curves;
5. VIX rate / relative-MA / acceleration as descriptive dimensions;
6. exact visual mapping of the extra white rail.

These analyses must use the already-frozen protocol.

No geometry threshold may be changed.

---

## 9. Governance decision

The strongest research outcome is negative, and it is kept.

The Jan–Jun Discovery findings are not deleted.

They are reclassified:

- upper-confluence Discovery effect:
  `FAILED GENERALIZATION / REJECT GENERAL RULE`

- lower-confluence delayed-rebound effect:
  `ABSOLUTE MEAN REVERSION, NO MATCHED EXCESS / REJECT GENERAL BUY RULE`

The sealed 2026H1 window remains untouched for any future v2 hypothesis.

No portfolio sizing or trading-rule optimization begins from these failed general hypotheses.
