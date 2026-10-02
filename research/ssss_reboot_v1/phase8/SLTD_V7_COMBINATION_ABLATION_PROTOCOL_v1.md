# SLTD V7 Combination Ablation Study v1

Status: **FROZEN BEFORE RUN**

Parent frozen rollback baseline:
- branch: `baseline/sltd-v6-15rules-position-v1`
- commit: `05be43e350d9193ba01a2748ef4c0267438a84b1`

Parent single-rule ablation result:
- branch: `research/sltd-v7-rule-ablation-v1`
- result commit: `d303a2a961eb9adeeb224bf0bef16725919be591`

This study does not modify the frozen V6 baseline.

## Scope

Universe:
- same frozen 79 U.S. stocks;
- same Batches 1-8.

Formal window:
**2020-01-02 through 2026-09-30**

Execution / data:
- reuse frozen Phase 7 OHLCV snapshots;
- reuse FIRST_OBSERVED signal ledgers;
- no refetch;
- XMA unchanged;
- signal close -> next available open;
- 5 bps baseline and 10 bps stress.

Frozen position / exit policy:
- `I25_AADD_25_TO_CAP_S25_WHOLD_RNO_CHANGE_MIXED`
- Hard Exit: `C2_FULL_CANDLE_BELOW_SLOW_BAND`

## Candidate rules for combination study

The prior one-at-a-time ablation identified three trade-active rules with
potential simplification / interaction value:

- B3 = `BUY_RECENT_BLUE_GRAY_LIGHT_SUPPORT`
- S1 = `SELL_RECENT_BLUE_GRAY_LIGHT_RESIST`
- S3 = `NEW_V5_D_GREEN_11_20_UPPER_WICK_ONLY`

`GREEN_11_20_LOWER_CLOSE_BELOW` (WAIT-2) is not included as a trade-active
combination dimension because the prior study proved it is a strict subset of
WAIT-1 and deleting it changes zero resolved actions. It remains a semantic
strength label in the frozen baseline during this round.

## Fixed variants

Run exactly these 8 systems:

1. BASELINE_ALL_15
2. DROP_B3
3. DROP_S1
4. DROP_S3
5. DROP_B3_S1
6. DROP_B3_S3
7. DROP_S1_S3
8. DROP_B3_S1_S3

No other rule changes are permitted.

For every variant:
- recompute rule presence;
- recompute action classes;
- recompute NO_CHANGE_MIXED resolution;
- keep position sizing and C2 Hard Exit unchanged.

## Required outputs

At 5 and 10 bps:
- all-79 equal-weight Total Return, CAGR, MaxDD, Calmar, turnover,
  position changes, time in market, C2 Hard Exit count;
- per-batch metrics;
- per-symbol metrics.

Versus baseline:
- delta CAGR;
- delta MaxDD;
- delta Calmar;
- delta turnover;
- batch counts improved / worsened for CAGR, MaxDD, Calmar;
- median batch deltas.

Versus the corresponding single-rule deletions:
- interaction delta for each pair / triple;
- identify whether combined deletion is additive, better-than-additive,
  or worse-than-additive in CAGR and Calmar.

## Decision discipline

This is still an **exploratory reused-universe study**.
It may identify candidates for simplification, but it cannot replace the frozen
V6 baseline.

A combination may advance to fresh OOS only if:
- its all-79 Calmar is not worse than baseline;
- its all-79 CAGR is not materially worse than baseline;
- and it does not worsen Calmar in more than 4 of 8 batches.

No automatic deletion is allowed from this study.

`SLTD_V7_COMBINATION_ABLATION_STUDY_V1_PROTOCOL = FROZEN`
