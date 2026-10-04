# SLTD Relative Ranking v1 — Stage B Amendment A

Status: **FROZEN BEFORE STAGE B RESULTS**

Parent protocol:
`SLTD_SCORE_LEVEL_RELATIVE_RANKING_V1_PROTOCOL.md`

Stage A result:
`SLTD_SCORE_LEVEL_RELATIVE_RANKING_V1_STAGE_A = PROMOTED_TO_ALLOCATION_TEST`

Stage A archive commit:
`beb8f377e25417390ac38c2b2a86fa98ab04e04d`

## 1. Purpose

Stage A established that frozen SLTD LEVEL has positive same-date cross-sectional ordering value.

Stage B asks whether that ordering can create a usable **fully-invested long-only allocation tilt**
without probability calibration, thresholds, momentum, or V7 rules.

This is development evidence only.
It is not independent Fresh OOS.

## 2. Frozen development window

Universe:
- original 79 stocks only

Formal window:
- 2020-01-02 .. 2026-09-30

Data:
- repository-frozen raw unadjusted OHLC snapshots
- repository-frozen FIRST_OBSERVED ledgers
- no new external market data

The whole 2020-2026Q3 window is explicitly treated as **development** because:
- Discovery created the state utilities;
- Temporal participated in state-stability selection and Stage-A consistency checking.

No claim of independent OOS is allowed from Stage B.

## 3. Frozen rank allocation

For every close t:
- compute frozen v3 LEVEL for all available original-79 stocks;
- compute same-date average-tie cross-sectional RANK in [0,1];
- require at least 60 stocks.

At open t+1:

`RAW_WEIGHT_i = RANK_i`

`TARGET_WEIGHT_i = RAW_WEIGHT_i / sum(RAW_WEIGHT)`

If all RAW_WEIGHT values are zero:
- use equal weights.

Properties:
- long only
- no leverage
- fully invested
- no cash timing rule
- no threshold
- no rank exponent
- no top-k cutoff
- no sector constraint
- no volatility scaling
- no momentum
- no v4 probability
- no V7 signal input

No parameter may be tuned after seeing Stage B.

## 4. Transaction-cost accounting

Rebalance occurs at each open from the target computed at the previous close.

At each rebalance:
- mark current holdings at the open;
- gross traded notional is the sum of absolute target-vs-current position notional;
- transaction cost = gross traded notional * friction rate;
- cost is deducted before establishing the post-trade target holdings.

Friction:
- primary: 5 bps
- sensitivity: 10 bps and 20 bps

Report cumulative gross turnover and rebalance count.

## 5. Comparators

Required:

1. `SLTD_RANK_LINEAR`
2. `EQUAL_WEIGHT_DAILY` — same daily rebalance engine, target 1/N
3. `EQUAL_WEIGHT_BUY_HOLD` — equal-weight initial purchase, no subsequent rebalance
4. `V7_BASE` — existing frozen V7 aggregate benchmark only
5. `SMA200_TREND` — existing aggregate benchmark only

V7 and SMA200 are report-only in Stage B.
They become formal admission guards only in an independently preregistered Fresh stage.

## 6. Required metrics

For each friction level where applicable:
- Total Return
- CAGR
- MaxDD
- Calmar
- cumulative gross turnover
- rebalance count
- daily return p1 / p5
- annual returns

Also report:
- number of calendar years/partial years where SLTD_RANK_LINEAR beats EQUAL_WEIGHT_DAILY.

## 7. Stage B promotion gates

All must pass:

At 5 bps:
1. Rank Linear Total Return > Equal Weight Daily
2. Rank Linear Calmar > Equal Weight Daily
3. Rank Linear Total Return > Equal Weight Buy & Hold
4. Rank Linear Calmar > Equal Weight Buy & Hold
5. Rank Linear MaxDD is no worse than Equal Weight Buy & Hold

Durability:
6. at 10 bps, Rank Linear Total Return > Equal Weight Daily
7. at 20 bps, Rank Linear Calmar > Equal Weight Daily

Path quality:
8. Rank Linear beats Equal Weight Daily in at least **4 of the 7** calendar/partial years 2020-2026
9. Rank Linear 5bps daily-return p1 is no worse than Equal Weight Buy & Hold 5bps p1

If all pass:
`PROMOTED_TO_FRESH_OOS`

Otherwise:
`REJECTED_NOT_ADMITTED`

No failed gate may be rescued inside v1 by:
- changing the rank transform;
- adding a top-k rule;
- adding smoothing;
- adding sector neutralization;
- changing rebalance frequency;
- adding momentum;
- adding probability calibration.

## 8. Fresh boundary

The previously reserved v4 Fresh30 remains unconsumed.

Stage B may only authorize a separately frozen Fresh-stage protocol.
Stage B itself may not read Fresh30 results.

`SLTD_RELATIVE_RANKING_V1_STAGE_B_AMENDMENT_A = FROZEN`
