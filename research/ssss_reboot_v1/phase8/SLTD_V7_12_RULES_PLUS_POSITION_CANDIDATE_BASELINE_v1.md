# SLTD V7 Candidate Baseline v1

Status: **FROZEN CANDIDATE BASELINE**

This does **not** replace the frozen SLTD V6 rollback baseline.

V6 rollback baseline:
- branch: `baseline/sltd-v6-15rules-position-v1`
- commit: `05be43e350d9193ba01a2748ef4c0267438a84b1`

Fresh OOS10 evidence commit:
- `1b2e97cdbfdb1705556f210fe3f80f3a1cb9395c`

## Decision

Advance **Candidate B** as the formal SLTD V7 candidate baseline:

Remove these three rules from active execution:

1. `BUY_RECENT_BLUE_GRAY_LIGHT_SUPPORT` (B3 / old BUY-3)
2. `SELL_RECENT_BLUE_GRAY_LIGHT_RESIST` (S1 / old SELL-1)
3. `NEW_V5_D_GREEN_11_20_UPPER_WICK_ONLY` (S3 / old SELL-3)

All other SLTD V6 rules remain active.

## Active 12-rule taxonomy

### BUY
1. `BUY_BLUE_21P_LOWER`
2. `BUY_GRAY_4_10_LIGHT_SUPPORT`
3. `BLUE_11_20_LOWER_WICK_ONLY`
4. `NEW_V5_C_GRAY_4_10_LOWER_WICK_ONLY`

### HOLD
5. `CONT_BLUE_11_20_UPPER`
6. `CONT_BLUE_4_10_UPPER`
7. `CONT_RECENT_GRAY_BLUE_UPPER`
8. `NEW_V5_B_BLUE_21P_UPPER_CLOSE_ABOVE`

### WAIT
9. `AVOID_GREEN_11_20_LOWER`
10. `GREEN_11_20_LOWER_CLOSE_BELOW`

### SELL
11. `GREEN_4_10_UPPER`
12. `NEW_V5_E_GREEN_11_20_LIGHT_RESIST`

WAIT-2 remains in the taxonomy for semantic / confidence information even though prior overlap analysis showed it is a strict subset of WAIT-1 and changes zero resolved actions under the current execution policy.

## Unified position / exit execution policy

Unchanged from the frozen V6 baseline:

`I25_AADD_25_TO_CAP_S25_WHOLD_RNO_CHANGE_MIXED`

- first BUY from flat -> 25%;
- later BUY -> +25 percentage points, capped at 100%;
- ordinary SELL -> reduce 25% of current remaining position;
- WAIT while long -> HOLD;
- WAIT while flat -> NO ENTRY;
- same-bar conflicting action classes -> NO_CHANGE_MIXED;
- actually executed ordinary SELL -> Hard Exit risk state ARMED;
- actually executed BUY -> reset ARMED;
- while ARMED, if state=GREEN and `High < GZB4` -> next available open liquidate to 0%;
- after Hard Exit -> wait for the next BUY and restart from 25%.

Hard Exit:
`C2_FULL_CANDLE_BELOW_SLOW_BAND`

## Evidence supporting advancement

### Reused 79-stock robustness study

Frozen V6 baseline:
- Total Return: +153.45%
- CAGR: 14.79%
- MaxDD: -18.30%
- Calmar: 0.808

Candidate B:
- Total Return: +198.58%
- CAGR: 17.61%
- MaxDD: -20.91%
- Calmar: 0.842

Breadth:
- 59/79 stocks higher total return than baseline
- 58/79 stocks higher Calmar than baseline
- 7/7 calendar years higher return than baseline
- 3/3 eras higher Calmar than baseline

### Fresh 10-stock OOS validation

OOS symbols:
WFC, LMT, PM, ADP, WM, UNP, SO, VZ, PANW, CVS

Frozen V6 baseline:
- Total Return: +64.43%
- CAGR: 7.65%
- MaxDD: -16.34%
- Calmar: 0.468

Candidate B:
- Total Return: +87.73%
- CAGR: 9.79%
- MaxDD: -16.43%
- Calmar: 0.596

Breadth:
- 7/10 stocks higher total return
- 7/10 stocks higher CAGR
- 5/10 stocks better MaxDD
- 7/10 stocks higher Calmar
- median per-stock Return delta: +11.85%
- median per-stock CAGR delta: +1.77 percentage points
- median per-stock Calmar delta: +0.071

## Interpretation

The evidence is now consistent across:
- the original 79-stock reused universe;
- all 7 calendar-year slices;
- all 3 multi-year eras;
- a fresh 10-stock OOS universe.

Therefore B3, S1, and S3 are removed from the **V7 candidate execution taxonomy**.

However, the V6 15-rule baseline remains the official rollback point and is not overwritten.

## Governance

From this point:

- V6 frozen baseline = immutable rollback baseline.
- V7 12-rule system = current candidate baseline for subsequent research.
- Any further V7 optimization must branch from this candidate baseline and must not rewrite V6.
- If later V7 work fails, rollback to V6 remains available.

`SLTD_V7_12_RULES_PLUS_POSITION_CANDIDATE_BASELINE_V1 = FROZEN`
