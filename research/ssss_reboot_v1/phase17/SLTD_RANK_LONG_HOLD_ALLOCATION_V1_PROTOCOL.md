# SLTD Rank -> Long-Hold Allocation v1 — Protocol

Status: **PRE-REGISTERED / NOT YET RUN**

Branch:
`research/sltd-rank-long-hold-allocation-v1`

Parent closeout:
`research/sltd-score-level-relative-ranking-v1@4b19c5b3b3a328eef25239142a3dd357118ca318`

## 1. Why Phase17 exists

Phase16 established two facts:

1. frozen SLTD LEVEL has weak but repeatable same-date cross-sectional ranking value;
2. translating that rank into **daily full rebalancing** failed because the ranking edge was too small relative to turnover and drawdown.

However, the development data also showed that simple long-hold portfolios produced higher total return than repeatedly traded rank allocation.

Therefore Phase17 does **not** ask whether lower trading frequency itself creates alpha.

It asks a different question:

> Can the already-validated SLTD relative rank improve **initial capital allocation for a long holding period**, while leaving positions untouched after entry?

The intended interpretation is stock selection / capital placement, not market timing and not turnover control.

## 2. Frozen boundaries

- no Chan/缠论
- no V7 signal input
- no V7 C2 input
- no Score Momentum
- no v4 probability calibration
- no daily re-ranking after formation
- no stop loss
- no take profit
- no rank-triggered selling
- no rebalance during the evaluation holding period
- no leverage
- no shorting
- FIRST_OBSERVED / causal state semantics
- ranking observed at close t; cohort buys occur at open t+1
- only the 82 frozen Stage-A stable states may contribute
- each state uses its frozen **Discovery utility** weight
- Fresh OOS is not consumed in Stage A

Frozen score source:
`research/sltd-state-score-risk-exposure-v3@e996e4344e5c40425bc93253d2e00501bacb3eb8`

## 3. Core allocation rule

At each cohort formation close t:

1. compute frozen LEVEL for all 79 development stocks;
2. rank LEVEL cross-sectionally using average rank for ties;
3. convert to:

`RANK_i = (average_rank_i - 1) / (N - 1)`

4. define one-time static target:

`RAW_i = RANK_i`

`WEIGHT_i = RAW_i / sum(RAW)`

If all RAW values are zero, use equal weights.

At open t+1:
- invest 100% of cohort capital according to WEIGHT;
- after purchase, **do not rebalance and do not sell because ranks change**.

Comparator:
- `EQUAL_STATIC`: equal-weight all available stocks at the same open, then also never rebalance.

This isolates whether SLTD ranking helps **where capital is initially placed**.

## 4. Cohort formation schedule

Development universe:
- original 79 stocks

Formation schedule:
- one cohort per calendar month;
- use the **last valid trading close of the prior month** as the ranking observation;
- buy at the next available common trading open;
- require all 79 stocks to have valid open/close and finite frozen LEVEL;
- no result-driven skipping of cohorts.

Development calendar:
- 2020-01 through the latest month that supports the required full holding horizon inside 2026-09-30.

## 5. Holding horizons

Primary:
- **252 trading bars** (~1 trading year)

Secondary:
- 126 trading bars
- 504 trading bars

The horizon endpoint is an evaluation endpoint only.
It is **not** proposed as a sell rule.

For each cohort and horizon:
- buy once at cohort open;
- hold unchanged;
- evaluate at the close of the horizon endpoint.

## 6. Transaction costs

Primary:
- 5 bps one-time entry friction on invested notional

Sensitivity:
- 20 bps one-time entry friction

Because neither RANK_STATIC nor EQUAL_STATIC rebalances after entry, both have one initial purchase only.

No exit friction is charged because the horizon endpoint is an evaluation mark, not a proposed liquidation rule.

## 7. Cohort metrics

For each cohort and horizon report:

- RANK_STATIC total return
- EQUAL_STATIC total return
- excess return = RANK_STATIC - EQUAL_STATIC
- RANK_STATIC MaxDD
- EQUAL_STATIC MaxDD
- MaxDD difference
- RANK_STATIC Calmar
- EQUAL_STATIC Calmar
- Calmar difference

Aggregate separately for:

### Early development formations
- 2020-01 through 2023-12

### Late consistency formations
- 2024-01 onward, where the full horizon fits before 2026-09-30

Late is not independent Fresh OOS because Temporal data participated in prior state stability work.

## 8. Required diagnostics

For each horizon and segment report:

- cohort count
- median excess return
- mean excess return
- fraction of cohorts with excess return > 0
- p25 / p50 / p75 excess return
- median MaxDD difference
- median Calmar difference

Also report a single **full-window static diagnostic**:

- rank at the final close before 2020-01-02
- buy at 2020-01-02 open
- hold untouched through 2026-09-30
- compare RANK_STATIC vs EQUAL_STATIC

This full-window diagnostic is descriptive only and cannot override cohort gates.

## 9. Stage A promotion gates

Primary evidence is the 252-bar horizon.

All must pass at 5 bps:

1. Early 252-bar median excess return > 0
2. Late 252-bar median excess return > 0
3. Early 252-bar positive-cohort fraction > 50%
4. Late 252-bar positive-cohort fraction > 50%
5. Late 252-bar median Calmar difference > 0
6. Late 252-bar median MaxDD difference >= -0.01
7. 126-bar late median excess return > 0
8. 20 bps late 252-bar median excess return > 0

If all pass:
`PROMOTED_TO_LONG_HOLD_FRESH_OOS`

Otherwise:
`REJECTED_NOT_ADMITTED`

No failed gate may be rescued inside v1 by:

- changing cohort months;
- choosing only favorable formation dates;
- changing the rank transform;
- adding top-k selection;
- adding sector filters;
- adding volatility scaling;
- adding momentum;
- adding probability calibration;
- adding any sell or rebalance rule.

## 10. Fresh boundary

The previously reserved Fresh30 remains **unconsumed**.

Fresh30 may only be used if Stage A passes and a separate Fresh protocol is frozen first.

## 11. Research interpretation boundary

A Stage-A pass would mean:

> SLTD rank may be useful for **initial allocation / selection before a long hold**.

It would **not** mean:
- SLTD should trade frequently;
- SLTD should sell low-ranked positions;
- lower trading frequency is the source of alpha;
- V7 should be changed.

A Stage-A failure would mean:
- the cross-sectional rank signal is statistically descriptive,
- but it is not strong enough to improve long-hold capital placement under this frozen linear allocation.

## 12. Freeze

`SLTD_RANK_LONG_HOLD_ALLOCATION_V1_PROTOCOL = FROZEN`
