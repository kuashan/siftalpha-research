# SLTD E A-share 50 Validation v1

Status: **COMPLETE**

- Symbols: **50**
- Requested start: **2018-01-02**
- Actual common E-valid start after XMA/5d warmup: **2019-02-01**
- End: **2026-09-30**
- Primary timeframe: **1d**
- Higher timeframe: **completed 5d**
- XMA causal / no future backfill: **YES**

## Equal-weight 50-stock portfolio — primary costs

| System | Return | CAGR | MaxDD | Calmar | Time in market | Mean turnover | Changes |
|---|---:|---:|---:|---:|---:|---:|---:|
| E | 13.16% | 1.63% | -6.69% | 0.243 | 41.23% | 20.48 | 3274 |
| Buy & Hold | 114.08% | 10.45% | -38.79% | 0.269 | 100.00% | 1.00 | 50 |

## Breadth — E vs Buy & Hold

- Better Return: **9/50**
- Better MaxDD: **50/50**
- Better Calmar: **19/50**
- Median ΔReturn: **-57.79%**
- Median ΔMaxDD: **36.76%**
- Median ΔCalmar: **-0.055**

## E rule executions — primary costs

- E_BUY_1_PRIMARY_CLOSE_BREAK_BELOW_ZD1: **1161**
- E_BUY_2_HIGHER_CLOSE_BELOW_ZD1: **0**
- E_BUY_3_TOUCH_GZB_BAND: **907**
- E_SELL_1_PRIMARY_CLOSE_BREAK_ABOVE_ZK1_MINUS_50PP: **519**
- E_SELL_2_TOUCH_BS_MINUS_25PP: **148**
- E_SELL_3_TOUCH_GZB_BAND_FULL_EXIT: **517**
- E_SELL_4_CLOSE_BACK_BELOW_ZK1_FULL_EXIT: **22**
- blocked BUY attempts: **0**
- blocked SELL attempts: **2**

## Era Calmar — primary costs

| Era | E | Buy & Hold |
|---|---:|---:|
| EARLY | 1.521 | 3.241 |
| MIDDLE | -0.042 | -0.235 |
| LATE | 0.304 | 0.370 |

## Interpretation boundary

- E rules were not retuned.
- All 50 frozen A-share symbols were used.
- The previous Fresh15 is consumed for this separate E study only.
- No conclusion from prior U.S. E results was imported into this A-share result.

`SLTD_E_ASHARE50_VALIDATION_V1 = COMPLETE`
