# SLTD V6 Hard Exit Study v3 — C Confirmation Study

Status: **FROZEN BEFORE RUN**

Parent position policy:
`I25_AADD_25_TO_CAP_S25_WHOLD_RNO_CHANGE_MIXED`

Universe: the same frozen **79 U.S. stocks** in Batches 1-8.

Window: **2020-01-02 through 2026-09-30**.

Data / signals:
- reuse existing frozen Phase 7 OHLCV snapshots;
- reuse existing FIRST_OBSERVED ledgers;
- no market-data refetch;
- no retuning of the 15 SLTD V6 rules;
- signal close -> next available open execution.

Ordinary position policy stays fixed:
- first BUY while flat -> 25%;
- later BUY -> +25 percentage points, capped at 100%;
- ordinary SELL -> reduce 25% of current position;
- WAIT -> hold;
- mixed same-bar action classes -> no position change.

All C-family variants preserve the same risk arming rule:
1. an ordinary SELL is actually executed -> risk state becomes ARMED;
2. any later ordinary BUY execution resets ARMED to false;
3. a Hard Exit resets ARMED to false.

## Fixed candidates

### BASELINE
No Hard Exit.

### C0_IMMEDIATE
The current v2 C rule:
- while ARMED;
- signal bar is GREEN;
- Close < GZB4, where GZB4 is the lower edge of the slow light-gray band;
- next available open -> exit 100%.

### C1_ONE_BAR_NO_RECLAIM
Confirmation version:
1. while ARMED, signal bar t is GREEN and Close_t < GZB4_t;
2. do not exit yet;
3. on the next trading bar t+1, if Close_{t+1} is still below its own GZB4_{t+1},
   trigger a 100% Hard Exit at open t+2;
4. if Close_{t+1} >= GZB4_{t+1}, cancel the pending exit.

### C2_FULL_CANDLE_BELOW_SLOW_BAND
Stronger structural break:
- while ARMED;
- signal bar is GREEN;
- the entire candle is below the slow band lower edge: High < GZB4;
- next available open -> exit 100%.

### C3_FALLING_SLOW_BAND_CONFIRM
Trend-direction confirmation:
- while ARMED;
- signal bar is GREEN;
- Close < GZB4;
- GZB4_t < GZB4_{t-1}, i.e. the slow-band lower edge itself is falling;
- next available open -> exit 100%.

Hard Exit overrides ordinary actions on its execution open.

## Friction
- 5 bps baseline;
- 10 bps stress.

## Required outputs
For BASELINE / C0 / C1 / C2 / C3:
- all-79 equal-weight Return, CAGR, MaxDD, Calmar, turnover, Time in Market;
- per-batch metrics;
- per-symbol metrics;
- Hard Exit counts;
- batch improvements vs BASELINE;
- post-exit +5/+10/+20 trading-day forward returns from exit open.

Interpretation focus:
- whether confirmation reduces false exits versus C0;
- whether MaxDD improvement is preserved;
- whether CAGR / Calmar improve relative to C0;
- whether post-exit rebound rate falls.

This is an exploratory confirmation on the already-used 79-stock universe.
Any candidate selected from v3 must receive fresh out-of-sample validation before becoming
a final production Hard Exit rule.

`SLTD_V6_HARD_EXIT_STUDY_V3_PROTOCOL = FROZEN`
