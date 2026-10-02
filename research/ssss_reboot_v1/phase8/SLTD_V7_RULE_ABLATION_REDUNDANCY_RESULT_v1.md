# SLTD V7 Rule Ablation + Redundancy Study v1

Status: **COMPLETE**

Research status: **EXPLORATORY — reused 79-stock universe**

Frozen baseline: `baseline/sltd-v6-15rules-position-v1` @ `05be43e350d9193ba01a2748ef4c0267438a84b1`

Frozen position / exit policy:
- `I25_AADD_25_TO_CAP_S25_WHOLD_RNO_CHANGE_MIXED`
- Hard Exit `C2_FULL_CANDLE_BELOW_SLOW_BAND`

Baseline reproduction against the previously frozen C2 study: **PASS (5 bps and 10 bps)**.

## Frozen baseline — all 79 stocks, 5 bps

- Total return: **153.45%**
- CAGR: **14.79%**
- MaxDD: **-18.30%**
- Calmar: **0.808**
- C2 Hard Exits: **305**

## 15-rule one-at-a-time ablation — all-79 delta vs baseline, 5 bps

| Rule removed | Class | ΔCAGR | ΔMaxDD | ΔCalmar | ΔTurnover | Calmar better batches | Calmar worse batches | Resolved bars changed |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| BUY_BLUE_21P_LOWER | BUY | -7.28% | 5.77% | -0.209 | -3.14 | 3/8 | 5/8 | 2347 |
| BUY_GRAY_4_10_LIGHT_SUPPORT | BUY | -2.54% | 3.40% | +0.014 | -0.73 | 2/8 | 6/8 | 553 |
| BUY_RECENT_BLUE_GRAY_LIGHT_SUPPORT | BUY | -0.09% | 0.11% | -0.000 | -0.08 | 2/8 | 6/8 | 156 |
| BLUE_11_20_LOWER_WICK_ONLY | BUY | -0.41% | -0.03% | -0.024 | -0.16 | 2/8 | 6/8 | 167 |
| NEW_V5_C_GRAY_4_10_LOWER_WICK_ONLY | BUY | -1.22% | 1.28% | -0.011 | -0.21 | 3/8 | 5/8 | 218 |
| CONT_BLUE_11_20_UPPER | HOLD | 0.00% | 0.00% | +0.000 | +0.00 | 0/8 | 0/8 | 381 |
| CONT_BLUE_4_10_UPPER | HOLD | 0.00% | 0.00% | +0.000 | +0.00 | 0/8 | 0/8 | 199 |
| CONT_RECENT_GRAY_BLUE_UPPER | HOLD | 0.00% | 0.00% | +0.000 | +0.00 | 0/8 | 0/8 | 160 |
| NEW_V5_B_BLUE_21P_UPPER_CLOSE_ABOVE | HOLD | 0.00% | 0.00% | +0.000 | +0.00 | 0/8 | 0/8 | 1188 |
| AVOID_GREEN_11_20_LOWER | WAIT | 0.00% | 0.00% | +0.000 | +0.00 | 0/8 | 0/8 | 194 |
| GREEN_11_20_LOWER_CLOSE_BELOW | WAIT | 0.00% | 0.00% | +0.000 | +0.00 | 0/8 | 0/8 | 0 |
| SELL_RECENT_BLUE_GRAY_LIGHT_RESIST | SELL | 1.69% | -1.82% | +0.011 | -2.27 | 4/8 | 4/8 | 416 |
| GREEN_4_10_UPPER | SELL | 0.54% | -1.64% | -0.040 | -0.91 | 6/8 | 2/8 | 181 |
| NEW_V5_D_GREEN_11_20_UPPER_WICK_ONLY | SELL | 0.93% | -0.88% | +0.011 | -0.75 | 5/8 | 3/8 | 137 |
| NEW_V5_E_GREEN_11_20_LIGHT_RESIST | SELL | 0.04% | -1.28% | -0.051 | -0.76 | 5/8 | 3/8 | 255 |

Interpretation of ΔMaxDD: positive means drawdown became less severe after removing the rule; negative means worse.

## Rule overlap / redundancy

| Rule | Class | Occurrences | Sole bars | Same-class overlap | Cross-class overlap | Resolved bars changed if dropped |
|---|---|---:|---:|---:|---:|---:|
| BUY_BLUE_21P_LOWER | BUY | 2347 | 2347 | 0 | 0 | 2347 |
| BUY_GRAY_4_10_LIGHT_SUPPORT | BUY | 659 | 553 | 106 | 0 | 553 |
| BUY_RECENT_BLUE_GRAY_LIGHT_SUPPORT | BUY | 251 | 156 | 95 | 0 | 156 |
| BLUE_11_20_LOWER_WICK_ONLY | BUY | 167 | 167 | 0 | 0 | 167 |
| NEW_V5_C_GRAY_4_10_LOWER_WICK_ONLY | BUY | 233 | 210 | 15 | 8 | 218 |
| CONT_BLUE_11_20_UPPER | HOLD | 381 | 381 | 0 | 0 | 381 |
| CONT_BLUE_4_10_UPPER | HOLD | 279 | 199 | 80 | 0 | 199 |
| CONT_RECENT_GRAY_BLUE_UPPER | HOLD | 240 | 160 | 80 | 0 | 160 |
| NEW_V5_B_BLUE_21P_UPPER_CLOSE_ABOVE | HOLD | 1188 | 1188 | 0 | 0 | 1188 |
| AVOID_GREEN_11_20_LOWER | WAIT | 336 | 194 | 142 | 0 | 194 |
| GREEN_11_20_LOWER_CLOSE_BELOW | WAIT | 142 | 0 | 142 | 0 | 0 |
| SELL_RECENT_BLUE_GRAY_LIGHT_RESIST | SELL | 416 | 408 | 0 | 8 | 416 |
| GREEN_4_10_UPPER | SELL | 181 | 181 | 0 | 0 | 181 |
| NEW_V5_D_GREEN_11_20_UPPER_WICK_ONLY | SELL | 202 | 137 | 65 | 0 | 137 |
| NEW_V5_E_GREEN_11_20_LIGHT_RESIST | SELL | 320 | 255 | 65 | 0 | 255 |

Bars with any formal rule: **6937**
Mixed action-class bars: **8**
Multi-rule same-class bars: **393**

## Subset / near-subset relationships

| Relationship | Rule A | Rule B | Co-occurrence | Jaccard | P(B|A) | P(A|B) |
|---|---|---|---:|---:|---:|---:|
| GREEN_11_20_LOWER_CLOSE_BELOW_SUBSET_OF_AVOID_GREEN_11_20_LOWER | AVOID_GREEN_11_20_LOWER | GREEN_11_20_LOWER_CLOSE_BELOW | 142 | 0.423 | 0.423 | 1.000 |

## Governance

This run measures contribution and redundancy only. It does **not** change the frozen V6 baseline.
Any rule deletion / merge / weakening / strengthening must be frozen separately and validated on fresh OOS data.

`SLTD_V7_RULE_ABLATION_REDUNDANCY_STUDY_V1 = COMPLETE`
