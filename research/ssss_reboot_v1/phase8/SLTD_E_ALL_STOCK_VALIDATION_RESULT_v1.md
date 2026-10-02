# SLTD E All-Stock Validation v1

Status: **COMPLETE**

Universe: **89 unique mainstream U.S. stocks** = prior 79 + fresh OOS10.

Formal window: **2020-01-02 through 2026-09-30**.

Selected timeframe: **1d**; E higher timeframe: **5d**.

Execution: signal close -> next available open. Primary friction 5 bps; stress 10 bps.

## Equal-weight portfolio — 5 bps

| Scope | System | Return | CAGR | MaxDD | Calmar | Time in market | Changes |
|---|---|---:|---:|---:|---:|---:|---:|
| all89 | E | 17.60% | 2.43% | -12.98% | 0.187 | 39.58% | 6004 |
| all89 | V7 12-rule | 186.13% | 16.87% | -19.81% | 0.851 | 88.41% | 1941 |
| all89 | Buy & Hold | 223.57% | 19.02% | -33.96% | 0.560 | 100.00% | 89 |
| prior79 | E | 18.98% | 2.61% | -12.81% | 0.204 | 39.27% | 5357 |
| prior79 | V7 12-rule | 198.58% | 17.61% | -20.91% | 0.842 | 88.58% | 1674 |
| prior79 | Buy & Hold | 235.14% | 19.64% | -33.95% | 0.579 | 100.00% | 79 |
| oos10 | E | 6.71% | 0.97% | -14.50% | 0.067 | 42.04% | 647 |
| oos10 | V7 12-rule | 87.73% | 9.79% | -16.43% | 0.596 | 87.04% | 267 |
| oos10 | Buy & Hold | 132.13% | 13.30% | -34.52% | 0.385 | 100.00% | 10 |

## Breadth — E vs V7, 5 bps

- all89 better Return: **17/89**
- all89 better MaxDD: **86/89**
- all89 better Calmar: **22/89**
- all89 median ΔReturn: **-52.54%**
- all89 median ΔMaxDD: **19.28%**
- all89 median ΔCalmar: **-0.123**
- OOS10 better Return / MaxDD / Calmar: **2/10 / 10/10 / 3/10**

## Breadth — E vs Buy & Hold, 5 bps

- all89 better Return: **14/89**
- all89 better MaxDD: **89/89**
- all89 better Calmar: **26/89**
- all89 median ΔReturn: **-64.73%**
- all89 median ΔMaxDD: **28.04%**
- all89 median ΔCalmar: **-0.107**
- OOS10 better Return / MaxDD / Calmar: **1/10 / 10/10 / 1/10**

## E execution counts — 5 bps

- E_BUY_1_PRIMARY_CLOSE_BREAK_BELOW_ZD1: **2119**
- E_BUY_2_HIGHER_CLOSE_BELOW_ZD1: **3**
- E_BUY_3_TOUCH_GZB_BAND: **1660**
- E_SELL_1_PRIMARY_CLOSE_BREAK_ABOVE_ZK1_MINUS_50PP: **1114**
- E_SELL_2_TOUCH_BS_MINUS_25PP: **423**
- E_SELL_3_TOUCH_GZB_BAND_FULL_EXIT: **651**
- E_SELL_4_CLOSE_BACK_BELOW_ZK1_FULL_EXIT: **37**

## Calendar-year equal-weight returns — 5 bps

| Year | E | V7 | Buy & Hold |
|---|---:|---:|---:|
| 2020 | 2.17% | 19.57% | 26.90% |
| 2021 | 6.62% | 27.07% | 33.45% |
| 2022 | -3.67% | -13.03% | -22.17% |
| 2023 | 3.95% | 19.63% | 31.63% |
| 2024 | 3.57% | 26.48% | 29.82% |
| 2025 | 3.23% | 18.43% | 21.64% |
| 2026 | 0.91% | 21.20% | 18.32% |

## Era Calmar — 5 bps

| Era | E | V7 | Buy & Hold |
|---|---:|---:|---:|
| EARLY_2020_2021 | 0.335 | 1.423 | 0.868 |
| MIDDLE_2022_2023 | 0.002 | 0.097 | 0.031 |
| LATE_2024_2026Q3 | 0.624 | 1.399 | 1.204 |

## Interpretation boundary

- Prior 79 are reused research data, not fresh OOS.
- OOS10 is reported separately.
- No E rule is changed or promoted by this run.
- Frozen V7 79-stock parity check: **PASS**.

SLTD_E_ALL_STOCK_VALIDATION_V1 = COMPLETE
