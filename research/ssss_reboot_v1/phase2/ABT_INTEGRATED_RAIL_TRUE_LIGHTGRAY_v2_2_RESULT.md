# SSSS Reboot — ABT Integrated Rail + True Light-Gray Band Study v2.2

Status: **COMPLETE / SINGLE-SYMBOL PILOT**
Date: 2026-10-02

## Scope

- ABT daily
- Main statistical window: 2018-01-02 through 2025-12-30 returned by provider
- Main-window bars: 2010
- Earlier history from 2010-01-04 used only for warm-up
- FIRST_OBSERVED bar-by-bar XMA reconstruction
- Original XMA25/XMA60 unchanged
- True visual light-gray band: GZB4..GZB3
- GZB9/GZB8 are state thresholds, not the visible light-gray band

Earlier results that treated GZB9/GZB8 as the light-gray support/resistance band are superseded.

## True light-gray support from above

- **UP**: n=47; hold 5/10/20 = 72.3% / 72.3% / 72.3%; break20=27.7%; median ret20=2.4%; MFE20=5.2%; MAE20=-3.2%
- **RANGE**: n=42; hold 5/10/20 = 88.1% / 88.1% / 88.1%; break20=11.9%; median ret20=2.9%; MFE20=5.2%; MAE20=-2.2%

### By state age, n>=5

- **UP|LATE_21_PLUS**: n=42; hold20=71.4%; break20=28.6%; ret20=2.2%; MFE20=5.3%; MAE20=-3.2%
- **RANGE|EARLY_4_10**: n=17; hold20=88.2%; break20=11.8%; ret20=4.7%; MFE20=7.1%; MAE20=-1.8%
- **RANGE|MATURE_11_20**: n=12; hold20=91.7%; break20=8.3%; ret20=3.6%; MFE20=7.2%; MAE20=-2.4%
- **RANGE|LATE_21_PLUS**: n=9; hold20=88.9%; break20=11.1%; ret20=-0.9%; MFE20=1.8%; MAE20=-5.4%

## True light-gray resistance from below

- **UP**: n=8; hold 5/10/20 = 75.0% / 75.0% / 75.0%; break20=25.0%; median ret20=2.0%; MFE20=3.8%; MAE20=-4.2%
- **RANGE**: n=21; hold 5/10/20 = 76.2% / 76.2% / 76.2%; break20=23.8%; median ret20=1.3%; MFE20=2.9%; MAE20=-3.4%
- **DOWN**: n=27; hold 5/10/20 = 66.7% / 66.7% / 66.7%; break20=33.3%; median ret20=2.9%; MFE20=4.7%; MAE20=-2.6%

### By state age, n>=5

- **UP|LATE_21_PLUS**: n=7; hold20=71.4%; break20=28.6%; ret20=2.2%; MFE20=4.5%; MAE20=-3.2%
- **RANGE|EARLY_4_10**: n=8; hold20=62.5%; break20=37.5%; ret20=-2.5%; MFE20=1.6%; MAE20=-5.2%
- **RANGE|MATURE_11_20**: n=8; hold20=87.5%; break20=12.5%; ret20=6.4%; MFE20=7.0%; MAE20=-2.5%
- **DOWN|LATE_21_PLUS**: n=17; hold20=64.7%; break20=35.3%; ret20=3.1%; MFE20=4.7%; MAE20=-4.7%

## Inner lower rail by state age, n>=5

- **UP|LATE_21_PLUS**: n=42; MID-first=73.8%; BD-first=26.2%; hit upper=47.6%; MFE20=4.2%; MAE20=-3.6%
- **UP|MATURE_11_20**: n=7; MID-first=57.1%; BD-first=42.9%; hit upper=57.1%; MFE20=6.1%; MAE20=-2.3%
- **RANGE|EARLY_4_10**: n=6; MID-first=33.3%; BD-first=66.7%; hit upper=50.0%; MFE20=2.8%; MAE20=-4.3%
- **DOWN|MATURE_11_20**: n=11; MID-first=9.1%; BD-first=90.9%; hit upper=54.5%; MFE20=4.7%; MAE20=-4.1%
- **DOWN|LATE_21_PLUS**: n=12; MID-first=58.3%; BD-first=41.7%; hit upper=83.3%; MFE20=7.3%; MAE20=-2.6%

## Inner upper rail by state age, n>=5

- **UP|LATE_21_PLUS**: n=39; MID-first=46.2%; BS-first=51.3%; hit lower=59.0%; MFE20=2.6%; MAE20=-4.3%
- **RANGE|MATURE_11_20**: n=13; MID-first=30.8%; BS-first=69.2%; hit lower=15.4%; MFE20=6.1%; MAE20=-2.0%
- **UP|EARLY_4_10**: n=9; MID-first=0.0%; BS-first=100.0%; hit lower=33.3%; MFE20=5.6%; MAE20=-1.5%
- **UP|MATURE_11_20**: n=7; MID-first=0.0%; BS-first=100.0%; hit lower=57.1%; MFE20=4.0%; MAE20=-3.6%
- **DOWN|LATE_21_PLUS**: n=15; MID-first=60.0%; BS-first=40.0%; hit lower=53.3%; MFE20=3.0%; MAE20=-6.3%

## Interpretation boundary

This study is explicitly directed toward identifying future BUY/SELL points, but
ABT alone is not sufficient to freeze a trading rule.

The next validation should reuse these exact definitions on additional symbols.
