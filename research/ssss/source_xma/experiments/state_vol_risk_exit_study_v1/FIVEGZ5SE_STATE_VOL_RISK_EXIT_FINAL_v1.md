# State / Volatility-Aware Risk Exit Study Final Report v1

Status: **IMPLEMENTED_AND_VERIFIED / CLOSED**

Date: 2026-10-01
Branch: `research/source-xma-walkforward`

## 1. Question

This study tested whether a causal State / Volatility-Aware Risk Exit（状态 / 波动率感知风险退出）layer can improve the already frozen stock and Crypto controls.

The user-required fallback was explicit: if no materially better risk-exit mechanism survives the preregistered gates, do not use the risk-exit layer.

No BUY-A / BUY-B / BUY-C / SELL-A / SELL-B / SELL-C definition changed.

## 2. Frozen universes

Stocks:
- 39 frozen stocks from Stock Risk Exit v1.1.

Crypto:
- BTC
- ETH
- BNB
- SOL

Baseline reproduction:
- stocks 39/39 PASS;
- Crypto BTC / ETH / BNB / SOL exact PASS;
- max absolute return difference = 0;
- max trades difference = 0.

`STATE_VOL_BASELINE_REPRODUCTION = PASS`

## 3. Tested mechanisms

Diagnostic controls:
- ATR2_ONLY
- ATR3_ONLY

Formal preregistered candidates:
- LOSS2_MOD
- LOSS3_MOD
- LOSS2_SEV
- PEAK2_MOD
- PEAK3_MOD
- HYBRID25_MOD
- CONFIRM_ADAPT
- LOSS4_SEV

The study did not add any threshold after seeing results.

## 4. Stock baseline

39-stock cross-sectional mean:
- cumulative return: **+154.92%**
- intraday-low MDD: **-30.65%**
- P5: **-6.95%**
- CVaR10: **-8.22%**

## 5. Stock results

| Candidate | Mean return | Return retained | MDD improvement | MDD improved stocks | P5 delta | CVaR delta | Killed / Saved | BUY-C confirmed delta | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| LOSS2_MOD | +101.52% | 65.5% | +2.13pp | 20/39 | +1.21pp | +1.80pp | 321 / 331 | -1.23pp | FAIL |
| LOSS3_MOD | +122.48% | 79.1% | +0.34pp | 19/39 | +0.07pp | +0.67pp | 130 / 233 | -0.93pp | FAIL |
| LOSS2_SEV | +104.84% | 67.7% | +1.82pp | 24/39 | +1.03pp | +1.51pp | 289 / 300 | -1.05pp | FAIL |
| PEAK2_MOD | +81.08% | 52.3% | +1.78pp | 22/39 | +1.68pp | +2.28pp | 732 / 434 | -0.75pp | FAIL |
| PEAK3_MOD | +111.37% | 71.9% | +0.91pp | 22/39 | +0.71pp | +1.20pp | 426 / 327 | -1.01pp | FAIL |
| HYBRID25_MOD | +94.47% | 61.0% | +1.75pp | 24/39 | +1.31pp | +1.93pp | 566 / 386 | -1.04pp | FAIL |
| CONFIRM_ADAPT | +81.45% | 52.6% | +2.43pp | 25/39 | +1.81pp | +2.36pp | 725 / 434 | -0.87pp | FAIL |
| LOSS4_SEV | +138.07% | 89.1% | -0.28pp | 18/39 | -0.51pp | -0.19pp | 41 / 139 | -1.00pp | FAIL |

No stock candidate passed all preregistered gates.

The strongest MDD candidate, CONFIRM_ADAPT, improved mean intraday MDD by +2.43pp and improved 25/39 stocks, but retained only 52.6% of baseline mean return and killed 725 baseline winners versus 434 saved baseline losers.

The least destructive formal candidate, LOSS4_SEV, retained 89.1% of return, but did not reach the 90% gate, worsened mean intraday MDD, worsened P5/CVaR, and improved MDD on only 18/39 stocks.

Therefore:
`STOCK_RISK_EXIT = NOT_USED_RETAIN_BASELINE`

## 6. Crypto baseline

Four-coin mean:
- cumulative return: **+68.74%**
- intraday-low MDD: **-65.90%**
- P5: **-16.16%**
- CVaR10: **-18.85%**

## 7. Crypto results

| Candidate | Mean return | Return retained | MDD improvement | MDD improved coins | P5 delta | CVaR delta | Killed / Saved | BUY-C confirmed delta | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| LOSS2_MOD | +45.03% | 65.5% | -0.95pp | 1/4 | +2.15pp | +3.93pp | 10 / 34 | +14.37pp | FAIL |
| LOSS3_MOD | +59.60% | 86.7% | -0.90pp | 2/4 | +1.20pp | +1.98pp | 2 / 16 | +5.01pp | FAIL |
| LOSS2_SEV | +46.94% | 68.3% | -0.72pp | 1/4 | +2.70pp | +4.32pp | 8 / 33 | +14.37pp | FAIL |
| PEAK2_MOD | +38.46% | 55.9% | -2.13pp | 1/4 | +2.93pp | +4.96pp | 25 / 39 | -7.61pp | FAIL |
| PEAK3_MOD | +43.20% | 62.8% | -1.22pp | 1/4 | +0.56pp | +2.14pp | 9 / 23 | +5.01pp | FAIL |
| HYBRID25_MOD | +29.72% | 43.2% | -1.40pp | 1/4 | +1.92pp | +3.83pp | 17 / 32 | +2.61pp | FAIL |
| CONFIRM_ADAPT | +46.28% | 67.3% | +1.55pp | 2/4 | +3.12pp | +4.72pp | 23 / 40 | +6.89pp | FAIL |
| LOSS4_SEV | +77.87% | 113.3% | +0.53pp | 2/4 | -0.53pp | +0.60pp | 1 / 9 | +6.89pp | FAIL |

No Crypto candidate passed all preregistered gates.

LOSS4_SEV is noteworthy because mean return exceeded baseline (+77.87% vs +68.74%), but it failed the cross-coin risk consistency gate: MDD improved on only 2/4 coins, mean P5 worsened, and leave-one-coin-out dominance checks failed. It is therefore not admitted.

CONFIRM_ADAPT improved pooled MDD and tails, but retained only 67.3% of baseline return and improved MDD on only 2/4 coins.

Therefore:
`CRYPTO_RISK_EXIT = NOT_USED_RETAIN_BASELINE`

## 8. Universal decision

No formal candidate passed both asset classes.

`UNIVERSAL_STATE_VOL_RISK_EXIT = REJECTED_NOT_ADMITTED`

The combined conclusion across fixed-percentage, ATR-only, and state/volatility-aware v1 studies is that the tested independent Risk Exit layer does not improve the frozen SSSS trading controls robustly enough to justify admission.

This does NOT prove that every conceivable emergency-risk mechanism is useless. It means the current evidence does not support adding one.

## 9. Final operating decision

Stocks retain the frozen selective SELL control:
- isolated SELL-A -> 50%
- isolated SELL-B -> 50%
- SELL-C / same-bar multi-SELL -> 100%
- after an A/B half sale, a later different SELL family -> exit remainder.

Crypto retains the frozen signal-only FULL_FIRST control:
- SELL-A -> 100%
- SELL-B -> 100%
- SELL-C -> 100% until a separate SELL-C study changes it.

No independent Risk Exit layer is added.

`RISK_EXIT_LAYER = NOT_USED_RETAIN_BASELINES`

## 10. Closure

`STATE_VOL_RISK_EXIT_STUDY_V1 = IMPLEMENTED_AND_VERIFIED`

`ROUND = CLOSED`

Do not tune these v1 thresholds after seeing results. Reopening Risk Exit requires genuinely new untouched validation data or a materially different preregistered hypothesis.
