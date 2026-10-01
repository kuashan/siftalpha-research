# State / Volatility-Aware Risk Exit Statistical Audit v1

Status: **IMPLEMENTED_AND_VERIFIED**

Bootstrap: 5000 deterministic asset-level resamples, seed 20261001.

## Stock baseline

- assets: 39
- mean cumulative return: 154.92%
- mean intraday-low MDD: -30.65%
- mean P5: -6.95%
- mean CVaR10: -8.22%

## Formal candidates

| Candidate | Return | Retain | MDD imp | MDD n | P5 d | CVaR d | Killed/Saved | Confirm d | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| LOSS2_MOD | 101.52% | 65.5% | +2.13pp | 20/39 | +1.21pp | +1.80pp | 321/331 | -1.23pp | FAIL |
| LOSS3_MOD | 122.48% | 79.1% | +0.34pp | 19/39 | +0.07pp | +0.67pp | 130/233 | -0.93pp | FAIL |
| LOSS2_SEV | 104.84% | 67.7% | +1.82pp | 24/39 | +1.03pp | +1.51pp | 289/300 | -1.05pp | FAIL |
| PEAK2_MOD | 81.08% | 52.3% | +1.78pp | 22/39 | +1.68pp | +2.28pp | 732/434 | -0.75pp | FAIL |
| PEAK3_MOD | 111.37% | 71.9% | +0.91pp | 22/39 | +0.71pp | +1.20pp | 426/327 | -1.01pp | FAIL |
| HYBRID25_MOD | 94.47% | 61.0% | +1.75pp | 24/39 | +1.31pp | +1.93pp | 566/386 | -1.04pp | FAIL |
| CONFIRM_ADAPT | 81.45% | 52.6% | +2.43pp | 25/39 | +1.81pp | +2.36pp | 725/434 | -0.87pp | FAIL |
| LOSS4_SEV | 138.07% | 89.1% | -0.28pp | 18/39 | -0.51pp | -0.19pp | 41/139 | -1.00pp | FAIL |

## Crypto baseline

- assets: 4
- mean cumulative return: 68.74%
- mean intraday-low MDD: -65.90%
- mean P5: -16.16%
- mean CVaR10: -18.85%

## Formal candidates

| Candidate | Return | Retain | MDD imp | MDD n | P5 d | CVaR d | Killed/Saved | Confirm d | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| LOSS2_MOD | 45.03% | 65.5% | -0.95pp | 1/4 | +2.15pp | +3.93pp | 10/34 | +14.37pp | FAIL |
| LOSS3_MOD | 59.60% | 86.7% | -0.90pp | 2/4 | +1.20pp | +1.98pp | 2/16 | +5.01pp | FAIL |
| LOSS2_SEV | 46.94% | 68.3% | -0.72pp | 1/4 | +2.70pp | +4.32pp | 8/33 | +14.37pp | FAIL |
| PEAK2_MOD | 38.46% | 55.9% | -2.13pp | 1/4 | +2.93pp | +4.96pp | 25/39 | -7.61pp | FAIL |
| PEAK3_MOD | 43.20% | 62.8% | -1.22pp | 1/4 | +0.56pp | +2.14pp | 9/23 | +5.01pp | FAIL |
| HYBRID25_MOD | 29.72% | 43.2% | -1.40pp | 1/4 | +1.92pp | +3.83pp | 17/32 | +2.61pp | FAIL |
| CONFIRM_ADAPT | 46.28% | 67.3% | +1.55pp | 2/4 | +3.12pp | +4.72pp | 23/40 | +6.89pp | FAIL |
| LOSS4_SEV | 77.87% | 113.3% | +0.53pp | 2/4 | -0.53pp | +0.60pp | 1/9 | +6.89pp | FAIL |

## Decision

- STOCK_RISK_EXIT = NOT_USED_RETAIN_BASELINE
- CRYPTO_RISK_EXIT = NOT_USED_RETAIN_BASELINE
- UNIVERSAL_STATE_VOL_RISK_EXIT = REJECTED_NOT_ADMITTED
- RISK_EXIT_LAYER = NOT_USED_RETAIN_BASELINES

Formal candidates only are eligible for promotion. ATR2_ONLY / ATR3_ONLY are diagnostic controls.
