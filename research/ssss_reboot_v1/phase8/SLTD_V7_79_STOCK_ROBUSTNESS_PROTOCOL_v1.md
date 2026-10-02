# SLTD V7 79-Stock Robustness Check v1

Status: **FROZEN BEFORE RUN**

Purpose:
Use the already available 79-stock dataset for a deeper robustness check of the two candidates selected by the combination-ablation study before any fresh OOS expansion.

Frozen rollback baseline:
- branch: `baseline/sltd-v6-15rules-position-v1`
- commit: `05be43e350d9193ba01a2748ef4c0267438a84b1`

Parent combination-ablation result:
- commit: `73493097a6d0bcc35a101869a01414e8470188fb`

Candidates:
- BASELINE_ALL_15
- CANDIDATE_A_DROP_S1_S3
  - remove `SELL_RECENT_BLUE_GRAY_LIGHT_RESIST`
  - remove `NEW_V5_D_GREEN_11_20_UPPER_WICK_ONLY`
- CANDIDATE_B_DROP_B3_S1_S3
  - remove `BUY_RECENT_BLUE_GRAY_LIGHT_SUPPORT`
  - remove `SELL_RECENT_BLUE_GRAY_LIGHT_RESIST`
  - remove `NEW_V5_D_GREEN_11_20_UPPER_WICK_ONLY`

Everything else remains fixed:
- existing 15-rule definitions except the candidate deletions;
- `I25_AADD_25_TO_CAP_S25_WHOLD_RNO_CHANGE_MIXED`;
- C2 Hard Exit `C2_FULL_CANDLE_BELOW_SLOW_BAND`;
- FIRST_OBSERVED;
- signal close -> next available open;
- 5 bps baseline and 10 bps stress.

Universe:
- same frozen 79 U.S. stocks;
- same Batches 1-8;
- no data refetch.

Formal full window:
**2020-01-02 through 2026-09-30**

## Robustness slices

### Calendar-year slices
- 2020
- 2021
- 2022
- 2023
- 2024
- 2025
- 2026 through 2026-09-30

### Multi-year eras
- EARLY: 2020-01-02 through 2021-12-31
- MIDDLE: 2022-01-01 through 2023-12-31
- LATE: 2024-01-01 through 2026-09-30

## Required outputs

For BASELINE / Candidate A / Candidate B:
- full-window all-79 Return, CAGR, MaxDD, Calmar;
- calendar-year all-79 Return and MaxDD;
- era Return, annualized CAGR, MaxDD, Calmar;
- per-batch full-window metrics;
- per-symbol full-window metrics;
- count of symbols where candidate beats baseline in total return;
- count of symbols where candidate beats baseline in Calmar;
- count of years with better return than baseline;
- count of eras with better Calmar than baseline;
- 5 bps and 10 bps results.

This is still **not independent OOS**, because the same 79 stocks were used to discover the candidates.
It is a stability / robustness check only.

No rule change is allowed from this run alone.

`SLTD_V7_79_STOCK_ROBUSTNESS_CHECK_V1_PROTOCOL = FROZEN`
