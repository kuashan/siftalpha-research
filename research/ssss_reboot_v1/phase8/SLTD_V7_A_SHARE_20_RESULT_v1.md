# SLTD V7 A-share 20 Cross-Industry Study v1

Status: **COMPLETE**

- Strategy: original SLTD V7 12-rule candidate
- Chan integration: **none**
- Strategy source commit: `5f9ea4d8fa434b54afdbf32a1cb21ef2f3cb4042`
- Source base: `e05919539328407cb7a67f8a995f6b90f0d4156b`
- Window: 2020-01-02 .. 2026-09-30
- Execution: signal close -> next available open
- Friction: 5 bps
- Data: Yahoo Finance / yfinance, raw unadjusted OHLC, matching frozen US-stock research protocol
- Universe: 20 A-shares across 8 industries, 2-3 names per industry
- GitHub Actions run: `37175836448`

## Overall

- Positive SLTD return: **12 / 20**
- SLTD beats same-window raw-price buy-and-hold: **6 / 20**
- Mean SLTD return: **+40.22%**
- Median SLTD return: **+9.38%**
- Mean max drawdown: **-53.57%**
- Median max drawdown: **-56.65%**

## Per symbol

| Industry | Code | Name | SLTD | MaxDD | Raw-price B&H | SLTD-B&H |
|---|---|---|---:|---:|---:|---:|
| 新能源电力设备 | 300750 | 宁德时代 | +302.92% | -53.50% | +387.35% | -84.43 pp |
| 新能源电力设备 | 300274 | 阳光电源 | +268.96% | -66.62% | +933.89% | -664.94 pp |
| 能源资源 | 601088 | 中国神华 | +151.74% | -23.09% | +157.13% | -5.39 pp |
| 工业制造 | 000338 | 潍柴动力 | +140.51% | -39.82% | +55.32% | +85.18 pp |
| 能源资源 | 601857 | 中国石油 | +71.63% | -34.44% | +90.97% | -19.34 pp |
| 金融 | 601398 | 工商银行 | +62.84% | -26.60% | +38.69% | +24.14 pp |
| 家电 | 000333 | 美的集团 | +46.36% | -36.36% | +34.06% | +12.30 pp |
| 科技电子 | 000725 | 京东方A | +17.69% | -56.04% | +24.08% | -6.39 pp |
| 工业制造 | 600031 | 三一重工 | +15.26% | -71.83% | -2.56% | +17.83 pp |
| 工业制造 | 601766 | 中国中车 | +14.49% | -28.27% | -14.50% | +29.00 pp |
| 食品饮料 | 600519 | 贵州茅台 | +4.27% | -51.28% | +11.38% | -7.11 pp |
| 科技电子 | 002230 | 科大讯飞 | +2.23% | -57.81% | +6.22% | -3.99 pp |
| 金融 | 600036 | 招商银行 | -0.51% | -39.99% | +6.12% | -6.63 pp |
| 新能源电力设备 | 601012 | 隆基绿能 | -22.69% | -82.22% | -17.18% | -5.51 pp |
| 科技电子 | 002415 | 海康威视 | -33.02% | -57.96% | -4.28% | -28.74 pp |
| 金融 | 601318 | 中国平安 | -33.31% | -60.39% | -38.12% | +4.81 pp |
| 医药医疗 | 300760 | 迈瑞医疗 | -45.31% | -74.32% | -10.54% | -34.77 pp |
| 家电 | 000651 | 格力电器 | -46.53% | -57.26% | -43.62% | -2.90 pp |
| 医药医疗 | 600276 | 恒瑞医药 | -49.52% | -71.06% | -22.48% | -27.04 pp |
| 食品饮料 | 000858 | 五粮液 | -63.54% | -82.61% | -46.96% | -16.59 pp |

## Industry aggregates

| Industry | N | Mean SLTD | Median SLTD | Mean MaxDD | Beats B&H |
|---|---:|---:|---:|---:|---:|
| 新能源电力设备 | 3 | +183.06% | +268.96% | -67.45% | 0/3 |
| 能源资源 | 2 | +111.69% | +111.69% | -28.77% | 0/2 |
| 工业制造 | 3 | +56.75% | +15.26% | -46.64% | 3/3 |
| 金融 | 3 | +9.67% | -0.51% | -42.32% | 2/3 |
| 家电 | 2 | -0.09% | -0.09% | -46.81% | 1/2 |
| 科技电子 | 3 | -4.37% | +2.23% | -57.27% | 0/3 |
| 食品饮料 | 2 | -29.64% | -29.64% | -66.94% | 0/2 |
| 医药医疗 | 2 | -47.41% | -47.41% | -72.69% | 0/2 |

## Interpretation

This first A-share cross-industry run shows strong heterogeneity. Industrial manufacturing is the only sampled industry where all names beat raw-price buy-and-hold. New-energy and energy names can deliver large absolute SLTD gains, but the selected names still underperform raw-price buy-and-hold over the same window. Healthcare and food/beverage are weak in this sample.

Important limitation: raw unadjusted OHLC was intentionally used to preserve exact comparability with the frozen US-stock protocol. A-shares have ex-right/ex-dividend effects, so a future A-share-specific confirmation round should separately validate an adjusted-price representation before changing any SLTD rule.

`SLTD_V7_A_SHARE_20_V1 = COMPLETE`
