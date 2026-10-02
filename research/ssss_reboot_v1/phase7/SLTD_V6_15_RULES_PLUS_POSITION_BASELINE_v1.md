# SLTD V6 Frozen Research Baseline v1

Status: **FROZEN / ROLLBACK BASELINE**

Purpose:
This baseline is the exact research rollback point before any subsequent SLTD rule optimization work.

Rollback branch:
`baseline/sltd-v6-15rules-position-v1`

Rollback commit:
`05be43e350d9193ba01a2748ef4c0267438a84b1`

This baseline consists of:

## A. 15 formal SLTD V6 trading rules

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

Frozen taxonomy source:
`research/ssss_reboot_v1/phase6/SSSS_FORMAL_15_ACTION_TAXONOMY_v1.md`

Blob SHA:
`c20e5b98516acd3f21577207a07dd8520e93a88e`

## B. Unified position / exit execution policy

Policy ID:
`I25_AADD_25_TO_CAP_S25_WHOLD_RNO_CHANGE_MIXED`

Hard Exit:
`C2_FULL_CANDLE_BELOW_SLOW_BAND`

Rules:
- first BUY from flat -> 25%;
- later BUY -> +25 percentage points, capped at 100%;
- ordinary SELL -> reduce 25% of current remaining position;
- WAIT while long -> hold;
- WAIT while flat -> no entry;
- conflicting same-bar action classes -> NO_CHANGE_MIXED;
- executed ordinary SELL -> Hard Exit risk state ARMED;
- later executed BUY -> reset ARMED;
- while ARMED, if state=GREEN and `High < GZB4` -> next available open liquidate to 0%;
- after Hard Exit -> wait for a new valid BUY and restart from 25%.

Frozen policy sources:
- `research/ssss_reboot_v1/phase7/SLTD_V6_INTEGRATED_POSITION_POLICY_v1.md`
  - blob SHA: `e48c630b56b363e1a8fcfca01ce209e480dd3c21`
- `research/ssss_reboot_v1/phase7/SLTD_V6_INTEGRATED_POSITION_POLICY_v1.json`
  - blob SHA: `ceae5f58ab1b7e87eeaf80c6a48a64ed04d0a68d`

## Governance

From this point forward, any Rule Contribution / Ablation / Redundancy / SLTD V7 research must be treated as a new research layer.

Do not silently overwrite this baseline.

If later research fails, overfits, or is rejected, restore:
`baseline/sltd-v6-15rules-position-v1`
or exact commit:
`05be43e350d9193ba01a2748ef4c0267438a84b1`

`SLTD_V6_15_RULES_PLUS_POSITION_BASELINE_V1 = FROZEN`
