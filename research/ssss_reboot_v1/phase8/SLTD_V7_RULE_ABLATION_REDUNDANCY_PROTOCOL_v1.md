# SLTD V7 Rule Contribution & Redundancy Study v1

Status: **FROZEN BEFORE RUN**

Parent rollback baseline:
- branch: `baseline/sltd-v6-15rules-position-v1`
- commit: `05be43e350d9193ba01a2748ef4c0267438a84b1`

This study does **not** modify the frozen SLTD V6 baseline.
It creates a new research layer only.

Universe:
- same frozen 79 U.S. stocks used in the Phase 7 position-policy study;
- Batches 1-8 unchanged.

Formal window:
**2020-01-02 through 2026-09-30**

Data / representation:
- reuse existing frozen Phase 7 OHLCV snapshots;
- reuse existing FIRST_OBSERVED signal ledgers;
- no market-data refetch;
- XMA unchanged;
- no retuning of rule thresholds.

Execution:
**signal close -> next available open**

Friction:
- 5 bps baseline;
- 10 bps stress.

## Frozen baseline system

### 15 SLTD V6 rules

BUY:
1. `BUY_BLUE_21P_LOWER`
2. `BUY_GRAY_4_10_LIGHT_SUPPORT`
3. `BUY_RECENT_BLUE_GRAY_LIGHT_SUPPORT`
4. `BLUE_11_20_LOWER_WICK_ONLY`
5. `NEW_V5_C_GRAY_4_10_LOWER_WICK_ONLY`

HOLD:
6. `CONT_BLUE_11_20_UPPER`
7. `CONT_BLUE_4_10_UPPER`
8. `CONT_RECENT_GRAY_BLUE_UPPER`
9. `NEW_V5_B_BLUE_21P_UPPER_CLOSE_ABOVE`

WAIT:
10. `AVOID_GREEN_11_20_LOWER`
11. `GREEN_11_20_LOWER_CLOSE_BELOW`

SELL:
12. `SELL_RECENT_BLUE_GRAY_LIGHT_RESIST`
13. `GREEN_4_10_UPPER`
14. `NEW_V5_D_GREEN_11_20_UPPER_WICK_ONLY`
15. `NEW_V5_E_GREEN_11_20_LIGHT_RESIST`

### Unified position / exit policy

`I25_AADD_25_TO_CAP_S25_WHOLD_RNO_CHANGE_MIXED`

- first BUY from flat -> 25%;
- subsequent BUY -> +25 percentage points, cap 100%;
- ordinary SELL -> reduce 25% of current remaining position;
- WAIT while long -> HOLD;
- WAIT while flat -> NO ENTRY;
- mixed same-bar action classes -> NO_CHANGE_MIXED;
- actually executed ordinary SELL -> C2 risk state ARMED;
- actually executed BUY -> reset ARMED;
- while ARMED, if state=GREEN and `High < GZB4` -> next available open liquidate to 0%;
- after Hard Exit -> wait for a new BUY and restart from 25%.

## Ablation design

Run 16 systems with all other logic fixed:

1. `BASELINE_ALL_15`
2. `DROP_BUY_BLUE_21P_LOWER`
3. `DROP_BUY_GRAY_4_10_LIGHT_SUPPORT`
4. `DROP_BUY_RECENT_BLUE_GRAY_LIGHT_SUPPORT`
5. `DROP_BLUE_11_20_LOWER_WICK_ONLY`
6. `DROP_NEW_V5_C_GRAY_4_10_LOWER_WICK_ONLY`
7. `DROP_CONT_BLUE_11_20_UPPER`
8. `DROP_CONT_BLUE_4_10_UPPER`
9. `DROP_CONT_RECENT_GRAY_BLUE_UPPER`
10. `DROP_NEW_V5_B_BLUE_21P_UPPER_CLOSE_ABOVE`
11. `DROP_AVOID_GREEN_11_20_LOWER`
12. `DROP_GREEN_11_20_LOWER_CLOSE_BELOW`
13. `DROP_SELL_RECENT_BLUE_GRAY_LIGHT_RESIST`
14. `DROP_GREEN_4_10_UPPER`
15. `DROP_NEW_V5_D_GREEN_11_20_UPPER_WICK_ONLY`
16. `DROP_NEW_V5_E_GREEN_11_20_LIGHT_RESIST`

For each DROP variant:
- remove only that exact rule ID from every signal row;
- then recompute action classes and `NO_CHANGE_MIXED` resolution;
- run the same position policy and C2 Hard Exit unchanged.

This means an ablated rule can affect:
- an ordinary BUY / WAIT / SELL action directly;
- whether a same-bar mixed conflict exists;
- whether an actual SELL arms C2;
- later C2 Hard Exit timing.

HOLD is operationally no-order, but removing a HOLD rule can still matter on a
same-bar mixed event because mixed resolution is recomputed after ablation.

## Required performance outputs

For BASELINE and every DROP variant, at both 5 and 10 bps:
- all-79 equal-weight total return;
- CAGR;
- MaxDD;
- Calmar;
- turnover;
- position changes;
- time in market;
- C2 Hard Exit count;
- per-batch metrics;
- per-symbol metrics.

For every DROP variant versus BASELINE:
- delta total return;
- delta CAGR;
- delta MaxDD;
- delta Calmar;
- delta turnover;
- number of batches with improved / worsened CAGR;
- number of batches with improved / worsened MaxDD;
- number of batches with improved / worsened Calmar;
- median batch metric deltas.

No rule will be removed from the frozen baseline solely because it looks better
on this already-used 79-stock universe.

## Required overlap / redundancy outputs

Across all formal-window signal bars:
- occurrence count per rule;
- number of bars where the rule is the only one of the 15 present;
- number of bars with at least one other same-action-class rule;
- number of bars with at least one rule from a different action class;
- number of baseline resolved-action bars changed by ablating the rule;
- pairwise rule co-occurrence counts;
- pairwise Jaccard overlap;
- conditional overlap A|B and B|A;
- identify exact / near subset relationships;
- identify same-class overlap versus cross-class mixed conflicts.

The overlap analysis is descriptive only and does not itself change the action map.

## Governance

This 79-stock run is an **exploratory contribution / redundancy study** because
the universe has already been used in earlier SLTD research.

Any rule deletion, weakening, strengthening, merge, or signal-strength redesign
must be frozen as a separate candidate and validated on fresh independent OOS
data before replacing the V6 rollback baseline.

`SLTD_V7_RULE_ABLATION_REDUNDANCY_STUDY_V1_PROTOCOL = FROZEN`
