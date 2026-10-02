# SLTD V6 Hard Exit Study v2 — 79 Stock Confirmation Protocol

Status: **FROZEN BEFORE RUN**

Parent position policy:
`I25_AADD_25_TO_CAP_S25_WHOLD_RNO_CHANGE_MIXED`

Universe: the same frozen **79 U.S. stocks** in Batches 1-8.

Window: **2020-01-02 through 2026-09-30**.

Data and signal source:
- reuse the existing frozen Phase 7 OHLCV snapshots;
- reuse the existing FIRST_OBSERVED signal ledgers;
- no market-data refetch;
- no retuning of the 15 SLTD V6 rules;
- signal at close -> action at next available open.

Ordinary position policy stays fixed:
- first BUY while flat -> 25%;
- later BUY -> +25 percentage points, capped at 100%;
- ordinary SELL -> reduce 25% of current position;
- WAIT -> hold;
- mixed same-bar action classes -> no position change.

## Fixed Hard Exit candidates

### BASELINE
No Hard Exit.

### A_SELL_ARMED_THEN_GREEN_FULL_BELOW
Stateful confirmation:
1. an ordinary SELL is actually executed -> risk state becomes ARMED;
2. any later ordinary BUY execution resets ARMED to false;
3. while ARMED, a signal bar with GREEN + LOWER + FULL_BELOW
   triggers a 100% Hard Exit at the next available open;
4. Hard Exit resets ARMED to false.

The same-bar SELL that first arms the state cannot also trigger the Hard Exit.

### B_GREEN_FULL_BELOW_THEN_NO_RECLAIM
Two-stage structural confirmation:
1. signal bar t has GREEN + LOWER + FULL_BELOW;
2. wait exactly one trading bar;
3. if bar t+1 closes below its own current ZD1, trigger 100% Hard Exit
   at the next available open t+2;
4. if bar t+1 closes at or above ZD1, the pending Hard Exit is cancelled.

No prior SELL is required.

### C_SELL_ARMED_GREEN_CLOSE_BELOW_SLOW_BAND
Stateful slow-band break:
1. ordinary SELL execution arms risk;
2. later BUY execution resets risk;
3. while ARMED, if a signal bar is GREEN and Close < GZB4
   (the lower edge of the slow light-gray band), trigger 100% Hard Exit
   at the next available open;
4. Hard Exit resets risk.

### D_SELL_ARMED_GREEN_ZD1_MINUS_1ATR
Stateful volatility-buffered lower-rail break:
1. ordinary SELL execution arms risk;
2. later BUY execution resets risk;
3. while ARMED, if a signal bar is GREEN and:
   - Close < ZD1; and
   - ZD1 - Close >= ATR14,
   trigger 100% Hard Exit at the next available open;
4. Hard Exit resets risk.

ATR14 is the causal Wilder ATR(14):
- True Range = max(High-Low, abs(High-prevClose), abs(Low-prevClose));
- initial ATR = SMA of the first 14 TR observations;
- thereafter ATR_t = (13 * ATR_{t-1} + TR_t) / 14.

Hard Exit overrides ordinary actions on its execution open.

## Friction

- 5 bps baseline;
- 10 bps stress.

## Required outputs

For BASELINE / A / B / C / D:
- per-batch equal-weight Return / CAGR / MaxDD / Calmar / turnover /
  time in market;
- all-79 equal-weight portfolio metrics;
- per-symbol metrics;
- Hard Exit count;
- batch improvements versus BASELINE.

For every executed Hard Exit in A/B/C/D:
- exit symbol/date/open price;
- +5 / +10 / +20 trading-day forward close return from the exit open,
  when enough future observations exist;
- aggregate mean, median, positive-return rate at each horizon.

Interpretation:
- positive forward return after exit = the exit was followed by a rebound / possible sell-too-early event;
- negative forward return after exit = the asset continued lower after exit.

This is a fixed-hypothesis comparison, not a parameter search. Any preferred v2
candidate must be treated as a new research result and should later receive fresh
out-of-sample validation before becoming a final production rule.

`SLTD_V6_HARD_EXIT_STUDY_V2_PROTOCOL = FROZEN`
