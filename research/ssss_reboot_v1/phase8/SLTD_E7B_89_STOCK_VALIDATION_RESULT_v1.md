# SLTD E7B 89-Stock Validation v1

Status: **COMPLETE**

Universe: **89 unique stocks = prior79 + fresh OOS10**.

Window: **2020-01-02..2026-09-30**, timeframe **1d**.

Execution: completed-bar signal -> next available open. Primary friction **5 bps**, stress **10 bps**.

## Equal-weight portfolio — 5 bps

| Scope | System | Return | CAGR | MaxDD | Calmar | Time in market | Changes |
|---|---|---:|---:|---:|---:|---:|---:|
| all89 | E7B | 8.11% | 1.16% | -4.74% | 0.245 | 23.81% | 7566 |
| all89 | Frozen V7 | 186.13% | 16.87% | -19.81% | 0.851 | 88.41% | 1941 |
| all89 | Buy & Hold | 223.57% | 19.02% | -33.96% | 0.560 | 100.00% | 89 |
| prior79 | E7B | 8.40% | 1.20% | -4.76% | 0.253 | 23.65% | 6733 |
| prior79 | Frozen V7 | 198.58% | 17.61% | -20.91% | 0.842 | 88.58% | 1674 |
| prior79 | Buy & Hold | 235.14% | 19.64% | -33.95% | 0.579 | 100.00% | 79 |
| oos10 | E7B | 5.83% | 0.84% | -8.13% | 0.104 | 25.08% | 833 |
| oos10 | Frozen V7 | 87.73% | 9.79% | -16.43% | 0.596 | 87.04% | 267 |
| oos10 | Buy & Hold | 132.13% | 13.30% | -34.52% | 0.385 | 100.00% | 10 |

## Breadth — E7B vs frozen V7, 5 bps

- all89 better Return: **10/89**
- all89 better CAGR: **10/89**
- all89 better MaxDD: **89/89**
- all89 better Calmar: **19/89**
- all89 median ΔReturn: **-56.01%**
- all89 median ΔMaxDD: **22.87%**
- all89 median ΔCalmar: **-0.161**
- OOS10 better Return / MaxDD / Calmar: **2/10 / 10/10 / 3/10**

## Breadth — E7B vs Buy & Hold, 5 bps

- all89 better Return: **12/89**
- all89 better MaxDD: **89/89**
- all89 better Calmar: **21/89**

## E7B trigger totals — 5 bps

- ADAPTED_C2_FULL_EXIT_EXEC: **558**
- ADAPTED_C2_SIGNAL: **559**
- BS_FULL_EXIT_EXEC: **597**
- BUY_EXEC: **3738**
- LOW_BELOW_ZK1_FULL_EXIT_EXEC: **1038**
- ZK1_HALF_EXEC: **1635**
- ZK1_HALF_SIGNAL: **1635**

## Calendar-year equal-weight returns — 5 bps

| Year | E7B | V7 | Buy & Hold |
|---|---:|---:|---:|
| 2020 | 0.17% | 19.57% | 26.90% |
| 2021 | 4.39% | 27.07% | 33.45% |
| 2022 | -2.94% | -13.03% | -22.17% |
| 2023 | 1.16% | 19.63% | 31.63% |
| 2024 | 1.95% | 26.48% | 29.82% |
| 2025 | 2.22% | 18.43% | 21.64% |
| 2026 | 0.99% | 21.20% | 18.32% |

## Era Calmar — 5 bps

| Era | E7B | V7 | Buy & Hold |
|---|---:|---:|---:|
| EARLY_2020_2021 | 0.463 | 1.423 | 0.868 |
| MIDDLE_2022_2023 | -0.248 | 0.097 | 0.031 |
| LATE_2024_2026Q3 | 0.918 | 1.399 | 1.204 |

## Boundaries

- V7 remains frozen and unchanged.
- Prior79 is reused research data; OOS10 is shown separately.
- This run does not auto-promote E7B.
- Frozen V7 79-stock parity: **PASS**.

SLTD_E7B_89_STOCK_VALIDATION_V1 = COMPLETE
