# SLTD V7 Fresh 10-Stock OOS Validation v1

Status: **FROZEN BEFORE DATA FETCH / RUN**

Purpose:
Perform the first fresh-stock validation of the two V7 simplification candidates using
exactly 10 mainstream U.S. stocks that were not present in the prior 79-stock universe.

Frozen rollback baseline:
- branch: `baseline/sltd-v6-15rules-position-v1`
- commit: `05be43e350d9193ba01a2748ef4c0267438a84b1`

Parent robustness result:
- commit: `678c55c8082e2871f786e76068cd1a1aa8d9e38c`

## Frozen OOS10 universe

1. WFC — Wells Fargo
2. LMT — Lockheed Martin
3. PM — Philip Morris International
4. ADP — Automatic Data Processing
5. WM — Waste Management
6. UNP — Union Pacific
7. SO — Southern Company
8. VZ — Verizon Communications
9. PANW — Palo Alto Networks
10. CVS — CVS Health

Selection discipline:
- none of these symbols appears in the prior frozen 79-stock Batches 1-8;
- all are established mainstream U.S. large-cap equities;
- no penny stocks / microcaps;
- the list is frozen before downloading or inspecting their SLTD backtest results;
- no symbol replacement is allowed after seeing results unless data is genuinely unavailable,
  in which case the run must stop and report the issue rather than substitute post hoc.

## Systems under test

### BASELINE_ALL_15
Frozen 15-rule SLTD V6 baseline.

### CANDIDATE_A_DROP_S1_S3
Remove:
- `SELL_RECENT_BLUE_GRAY_LIGHT_RESIST`
- `NEW_V5_D_GREEN_11_20_UPPER_WICK_ONLY`

### CANDIDATE_B_DROP_B3_S1_S3
Remove:
- `BUY_RECENT_BLUE_GRAY_LIGHT_SUPPORT`
- `SELL_RECENT_BLUE_GRAY_LIGHT_RESIST`
- `NEW_V5_D_GREEN_11_20_UPPER_WICK_ONLY`

Everything else remains fixed:
- XMA / signal definitions unchanged;
- `I25_AADD_25_TO_CAP_S25_WHOLD_RNO_CHANGE_MIXED`;
- C2 Hard Exit `C2_FULL_CANDLE_BELOW_SLOW_BAND`;
- FIRST_OBSERVED;
- signal close -> next available open;
- long/cash only;
- 5 bps baseline and 10 bps stress.

## Data convention

Use the same stock convention as the prior Phase 7 study:
- Yahoo Finance via yfinance;
- daily bars;
- fetch start: 2010-01-04;
- fetch end exclusive: 2026-10-01;
- formal window: 2020-01-02 through 2026-09-30;
- `auto_adjust=False`;
- `actions=False`;
- `repair=False`.

Persist the downloaded OHLCV snapshots, manifests, hashes, and generated FIRST_OBSERVED
signal ledgers so the OOS run is auditable and reproducible.

## Required outputs

For BASELINE / Candidate A / Candidate B at 5 bps and 10 bps:
- equal-weight 10-stock total return;
- CAGR;
- MaxDD;
- Calmar;
- turnover;
- position changes;
- time in market;
- C2 Hard Exit count;
- per-symbol metrics.

Breadth:
- symbols with higher total return than baseline;
- symbols with higher CAGR than baseline;
- symbols with better MaxDD than baseline;
- symbols with higher Calmar than baseline;
- median per-symbol deltas.

Also report whether Candidate A and Candidate B preserve the direction of improvement
seen in the reused 79-stock study.

No candidate is promoted automatically by this run; results are evidence for the next decision.

`SLTD_V7_FRESH_OOS10_VALIDATION_V1_PROTOCOL = FROZEN`
