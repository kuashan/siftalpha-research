# SLTD V7 Profit Protection Study v1

Status: **COMPLETE**

Frozen V7 BUY/HOLD/WAIT / ordinary SELL / C2: **UNCHANGED**.

Representation: **FIRST_OBSERVED**. Window: **2020-01-02..2026-09-30**.

Universe: **89 stocks = prior79 + OOS10**. Primary friction: **5 bps**; stress: **10 bps**.

Frozen V7 89-stock parity: **PASS**.

## All-89 equal-weight portfolio — 5 bps

| Variant | Return | CAGR | MaxDD | Calmar | Time | Capture | Giveback ratio | Classification |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| V7_BASELINE | 186.13% | 16.87% | -19.81% | 0.851 | 88.41% | 27.3% | 72.7% | FROZEN_BASELINE |
| P1_STRUCT_TREND_FAILURE | 67.92% | 7.99% | -10.56% | 0.756 | 67.14% | 61.0% | 39.0% | MIXED_NOT_ADMITTED |
| P2_CHANDELIER_22_3_PROFIT | 23.85% | 3.22% | -6.75% | 0.477 | 42.36% | 11.4% | 88.6% | REJECTED_NOT_ADMITTED |
| P3_BS_SCALEOUT_25 | 121.01% | 12.48% | -15.01% | 0.832 | 88.43% | 30.7% | 69.3% | MIXED_NOT_ADMITTED |
| P4_BS25_PLUS_CHANDELIER | 21.76% | 2.96% | -6.12% | 0.484 | 42.19% | 20.9% | 79.1% | REJECTED_NOT_ADMITTED |

## OOS10 — 5 bps

| Variant | Return | MaxDD | Calmar | Capture | Giveback ratio |
|---|---:|---:|---:|---:|---:|
| V7_BASELINE | 87.73% | -16.43% | 0.596 | -11.0% | 111.0% |
| P1_STRUCT_TREND_FAILURE | 59.24% | -11.48% | 0.622 | 62.3% | 37.7% |
| P2_CHANDELIER_22_3_PROFIT | 12.83% | -8.16% | 0.221 | 6.6% | 93.4% |
| P3_BS_SCALEOUT_25 | 87.08% | -15.53% | 0.627 | 18.2% | 81.8% |
| P4_BS25_PLUS_CHANDELIER | 14.87% | -7.88% | 0.264 | 16.3% | 83.7% |

## Breadth vs V7 — 5 bps

| Variant | Better Return | Better MaxDD | Better Calmar | Better giveback / eligible |
|---|---:|---:|---:|---:|
| P1_STRUCT_TREND_FAILURE | 29/89 | 86/89 | 52/89 | 75/84 |
| P2_CHANDELIER_22_3_PROFIT | 19/89 | 83/89 | 30/89 | 34/84 |
| P3_BS_SCALEOUT_25 | 37/89 | 84/89 | 56/89 | 66/83 |
| P4_BS25_PLUS_CHANDELIER | 17/89 | 84/89 | 32/89 | 43/84 |

## Admission gates

### P1_STRUCT_TREND_FAILURE — **MIXED_NOT_ADMITTED**
- Return retention vs V7: **36.5%**
- all89_calmar_improves: **FAIL**
- all89_maxdd_improves: **PASS**
- all89_return_retention_ge_90pct: **FAIL**
- all89_giveback_ratio_improves: **PASS**
- oos10_maxdd_not_worse: **PASS**
- oos10_giveback_ratio_improves: **PASS**

### P2_CHANDELIER_22_3_PROFIT — **REJECTED_NOT_ADMITTED**
- Return retention vs V7: **12.8%**
- all89_calmar_improves: **FAIL**
- all89_maxdd_improves: **PASS**
- all89_return_retention_ge_90pct: **FAIL**
- all89_giveback_ratio_improves: **FAIL**
- oos10_maxdd_not_worse: **PASS**
- oos10_giveback_ratio_improves: **PASS**

### P3_BS_SCALEOUT_25 — **MIXED_NOT_ADMITTED**
- Return retention vs V7: **65.0%**
- all89_calmar_improves: **FAIL**
- all89_maxdd_improves: **PASS**
- all89_return_retention_ge_90pct: **FAIL**
- all89_giveback_ratio_improves: **PASS**
- oos10_maxdd_not_worse: **PASS**
- oos10_giveback_ratio_improves: **PASS**

### P4_BS25_PLUS_CHANDELIER — **REJECTED_NOT_ADMITTED**
- Return retention vs V7: **11.7%**
- all89_calmar_improves: **FAIL**
- all89_maxdd_improves: **PASS**
- all89_return_retention_ge_90pct: **FAIL**
- all89_giveback_ratio_improves: **FAIL**
- oos10_maxdd_not_worse: **PASS**
- oos10_giveback_ratio_improves: **PASS**

## AAPL diagnostic — 5 bps

| Variant | Return | MaxDD | Calmar | Capture | Giveback ratio |
|---|---:|---:|---:|---:|---:|
| V7_BASELINE | 249.63% | -33.43% | 0.610 | 71.2% | 28.8% |
| P1_STRUCT_TREND_FAILURE | 172.69% | -18.36% | 0.873 | 64.4% | 35.6% |
| P2_CHANDELIER_22_3_PROFIT | 23.48% | -7.92% | 0.401 | -3.1% | 103.1% |
| P3_BS_SCALEOUT_25 | 160.90% | -32.43% | 0.471 | 77.7% | 22.3% |
| P4_BS25_PLUS_CHANDELIER | 18.29% | -7.44% | 0.339 | -3.1% | 103.1% |

## Trigger totals — 5 bps

- V7 baseline: BUY 1306 / ordinary SELL 430 / C2 205.
- P1: trend-failure full exits 1365.
- P2: Chandelier full exits 2119.
- P3: BS 25%-of-current scale-outs 3022.
- P4: Chandelier full exits 2116 + BS scale-outs 1605.

## Interpretation

- P1 proves that structural trend-failure can materially reduce drawdown and profit giveback, but it exits/re-enters too often and destroys too much trend return.
- Canonical Chandelier 22,3 is too aggressive for this SLTD/V7 position process. It sharply cuts exposure and does not improve the all-89 giveback ratio.
- P3 is the closest candidate: it improves MaxDD on 84/89 symbols, Calmar on 56/89, and giveback on 66/83 eligible symbols, while OOS10 stays close to V7 return. However all-89 return retention is only 65.0% and all-89 Calmar remains below V7, so it is not admitted.
- No tested protection layer meets the frozen admission gate.

## Closure

No additional SELL hypothesis is generated from this run.

`P1_STRUCT_TREND_FAILURE = MIXED_NOT_ADMITTED`

`P2_CHANDELIER_22_3_PROFIT = REJECTED_NOT_ADMITTED`

`P3_BS_SCALEOUT_25 = MIXED_NOT_ADMITTED`

`P4_BS25_PLUS_CHANDELIER = REJECTED_NOT_ADMITTED`

`SLTD_V7_PROFIT_PROTECTION_STUDY_V1 = COMPLETE`
