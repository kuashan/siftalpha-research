# SLTD V6 Hard Exit Study v1 — 79 Stock Protocol

Status: **FROZEN BEFORE RUN**

Parent stock position policy:
`I25_AADD_25_TO_CAP_S25_WHOLD_RNO_CHANGE_MIXED`

Universe: the same **79 stocks** and the same frozen Batches 1-8 used by the completed
SLTD V6 position-policy study.

Window: **2020-01-02 through 2026-09-30**

Data / signals:
- reuse the already frozen Phase 7 stock OHLCV snapshots;
- reuse the already generated FIRST_OBSERVED signal ledgers;
- do not refetch or retune market data;
- signal confirmed at close -> any action executes at the next available open.

Ordinary position policy remains unchanged:
- first BUY while flat -> 25%;
- later BUY -> add 25 percentage points, capped at 100%;
- ordinary SELL -> reduce 25% of current position;
- WAIT -> hold;
- mixed same-bar action classes -> no position change.

## Hard Exit candidates

### BASELINE
No Hard Exit. This is the already promoted stock position policy.

### H1_GREEN_LOWER_FULL_BELOW
At signal close t:
- color = GREEN;
- LOWER event = true;
- LOWER subtype = FULL_BELOW.

Then at the next available open t+1:
- Hard Exit overrides ordinary BUY/HOLD/WAIT/SELL;
- liquidate the entire remaining position to 0%.

### H2_GREEN_TWO_CLOSES_BELOW_ZD1
At signal close t:
- current bar color = GREEN and Close < ZD1;
- immediately preceding trading bar is also GREEN and Close < ZD1.

Then at the next available open t+1:
- Hard Exit overrides ordinary BUY/HOLD/WAIT/SELL;
- liquidate the entire remaining position to 0%.

### H3_H1_OR_H2
Hard Exit when either H1 or H2 is true.

After a Hard Exit, the strategy remains flat until a later ordinary BUY is permitted.
If a Hard Exit condition and another action conflict on the same execution open, Hard Exit wins.

## Friction

Run both:
- 5 bps baseline friction per position turnover;
- 10 bps stress friction per position turnover.

## Required comparison

For BASELINE / H1 / H2 / H3:
- per-batch equal-weight total return, CAGR, MaxDD, Calmar, turnover, changes, time in market;
- all-79 equal-weight portfolio metrics;
- per-symbol metrics;
- Hard Exit trigger/execution counts;
- batch-level Calmar / CAGR / MaxDD change versus BASELINE;
- number of batches with improved Calmar;
- number of batches with improved MaxDD;
- number of batches with improved CAGR.

This study tests Hard Exit only. It does not alter the frozen 15-rule SLTD V6 signal taxonomy
or the ordinary position policy.

`SLTD_V6_HARD_EXIT_STUDY_V1_PROTOCOL = FROZEN`
