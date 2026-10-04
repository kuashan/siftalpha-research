# SLTD A-share 50 Integrated Risk v1 — Stage B Holdout Result

Status: **REJECTED_NOT_ADMITTED**

- DEVELOPMENT symbols: **35**
- Holdout: **2025-01-02..2026-09-30**
- Fresh15 performance read: **NO**
- Severe threshold: **-1.32665**
- A-share stable negative states: **28**

## Primary costs

| System | Total Return | CAGR | MaxDD | Calmar | Mean Exposure | BUY | Ordinary SELL | C2 exits | Severe exits |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SLTD_12_RULES_ONLY | -0.27% | -0.16% | -9.73% | -0.016 | 61.92% | 161 | 44 | 0 | 0 |
| SLTD_V7_12_RULES_PLUS_C2 | -0.00% | -0.00% | -8.36% | -0.000 | 53.63% | 166 | 31 | 16 | 0 |
| SLTD_V7_12_RULES_PLUS_C2_PLUS_SEVERE_RISK | 0.51% | 0.29% | -7.51% | 0.039 | 50.42% | 172 | 31 | 14 | 8 |
| BUY_AND_HOLD | 1.98% | 1.13% | -13.32% | 0.085 | 100.00% | 35 | 0 | 0 | 0 |
| SMA200 | -3.65% | -2.12% | -7.92% | -0.267 | 48.24% | 301 | 288 | 0 | 0 |

## Attribution

| Comparison | Return Δ | CAGR Δ | MaxDD Δ | Calmar Δ | Exposure Δ | Median stock return Δ | Better DD | Better Calmar |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| C2: B-A | 0.27% | 0.15% | 1.37% | 0.016 | -8.29% | 0.00% | 13/35 | 9/35 |
| Severe Risk: C-B | 0.51% | 0.29% | 0.85% | 0.039 | -3.21% | 0.00% | 4/35 | 5/35 |
| Combined: C-A | 0.78% | 0.45% | 2.22% | 0.055 | -11.49% | 0.00% | 16/35 | 13/35 |

## Gate diagnostics

- Candidate/Baseline return retention: **-inf%**
- Candidate/Baseline exposure retention: **94.02%**
- Symbols with Severe Risk full exits: **6/35**
- Worst baseline per-stock MaxDD: **-47.82%**
- Worst candidate per-stock MaxDD: **-47.82%**

## Gates

- aggregate_maxdd_improves_ge_2pp: **FAIL**
- aggregate_calmar_improves: **PASS**
- aggregate_return_retention_ge_95pct: **FAIL**
- median_per_stock_return_delta_ge_minus_1pp: **PASS**
- better_maxdd_ge_60pct_symbols: **FAIL**
- better_calmar_ge_50pct_symbols: **FAIL**
- worst_per_stock_maxdd_improves_or_equal: **PASS**
- sensitivity_calmar_gt_baseline: **PASS**
- severe_full_exits_on_ge_10_symbols: **FAIL**
- mean_exposure_retention_ge_90pct: **PASS**

`SLTD_ASHARE50_INTEGRATED_RISK_V1_STAGE_B = REJECTED_NOT_ADMITTED`
