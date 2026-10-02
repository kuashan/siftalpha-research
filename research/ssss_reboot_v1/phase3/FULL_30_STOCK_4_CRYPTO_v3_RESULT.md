# SSSS Reboot — 30 Stocks + 4 Crypto Full Combination Validation v3

Status: **COMPLETE**
Date: 2026-10-02

## Coverage

- 30/30 stocks complete
- 4/4 crypto complete
- Formal stock validation excludes discovery symbols ABT and AAPL: 28 stocks
- FIRST_OBSERVED bar-by-bar
- XMA unchanged
- True light-gray band = GZB4..GZB3

Stock events:
- LOWER 2609
- UPPER 3135
- LIGHT_SUPPORT 2331
- LIGHT_RESIST 1956

Crypto events:
- LOWER 415
- UPPER 401
- LIGHT_SUPPORT 351
- LIGHT_RESIST 308

## Prespecified formal validation — 28 new stocks

- **BUY_GREEN_21P_LOWER** — MIXED; n=299; pooled=43.8%; breadth=9/27; median-symbol=44.4%
- **BUY_BLUE_21P_LOWER** — SUPPORTS_ABT; n=1049; pooled=70.6%; breadth=28/28; median-symbol=71.2%
- **AVOID_GREEN_11_20_LOWER** — SUPPORTS_ABT; n=135; pooled=70.4%; breadth=21/25; median-symbol=66.7%
- **AVOID_RECENT_GRAY_GREEN_LOWER** — MIXED; n=64; pooled=56.3%; breadth=4/11; median-symbol=33.3%
- **BUY_GRAY_4_10_LIGHT_SUPPORT** — SUPPORTS_ABT; n=263; pooled=74.1%; breadth=25/28; median-symbol=76.4%
- **BUY_RECENT_BLUE_GRAY_LIGHT_SUPPORT** — SUPPORTS_ABT; n=117; pooled=81.2%; breadth=21/22; median-symbol=80.0%
- **CONT_BLUE_11_20_UPPER** — SUPPORTS_ABT; n=165; pooled=85.5%; breadth=26/27; median-symbol=83.3%
- **CONT_BLUE_4_10_UPPER** — SUPPORTS_ABT; n=116; pooled=75.9%; breadth=19/23; median-symbol=75.0%
- **CONT_RECENT_GRAY_BLUE_UPPER** — SUPPORTS_ABT; n=106; pooled=77.4%; breadth=17/20; median-symbol=78.9%
- **SELL_GREEN_21P_UPPER** — MIXED; n=404; pooled=55.4%; breadth=14/28; median-symbol=51.3%
- **SELL_RECENT_BLUE_GRAY_LIGHT_RESIST** — SUPPORTS_ABT; n=160; pooled=71.9%; breadth=22/23; median-symbol=71.4%

## Prespecified transfer check — BTC / ETH / BNB / SOL

- **BUY_GREEN_21P_LOWER** — MIXED; n=69; pooled=49.3%; breadth=1/4; median-symbol=43.2%
- **BUY_BLUE_21P_LOWER** — SUPPORTS_STOCK_HYPOTHESIS; n=139; pooled=80.6%; breadth=4/4; median-symbol=82.7%
- **AVOID_GREEN_11_20_LOWER** — INSUFFICIENT_BREADTH; n=15; pooled=73.3%; breadth=2/3; median-symbol=80.0%
- **AVOID_RECENT_GRAY_GREEN_LOWER** — INSUFFICIENT_BREADTH; n=15; pooled=73.3%; breadth=2/3; median-symbol=71.4%
- **BUY_GRAY_4_10_LIGHT_SUPPORT** — SUPPORTS_STOCK_HYPOTHESIS; n=55; pooled=80.0%; breadth=3/4; median-symbol=79.4%
- **BUY_RECENT_BLUE_GRAY_LIGHT_SUPPORT** — SUPPORTS_STOCK_HYPOTHESIS; n=27; pooled=85.2%; breadth=3/3; median-symbol=90.9%
- **CONT_BLUE_11_20_UPPER** — SUPPORTS_STOCK_HYPOTHESIS; n=20; pooled=65.0%; breadth=2/3; median-symbol=62.5%
- **CONT_BLUE_4_10_UPPER** — INSUFFICIENT_BREADTH; n=13; pooled=84.6%; breadth=2/2; median-symbol=83.3%
- **CONT_RECENT_GRAY_BLUE_UPPER** — INSUFFICIENT_BREADTH; n=6; pooled=100.0%; breadth=0/0; median-symbol=—
- **SELL_GREEN_21P_UPPER** — SUPPORTS_STOCK_HYPOTHESIS; n=90; pooled=60.0%; breadth=4/4; median-symbol=59.9%
- **SELL_RECENT_BLUE_GRAY_LIGHT_RESIST** — SUPPORTS_STOCK_HYPOTHESIS; n=21; pooled=85.7%; breadth=3/3; median-symbol=85.7%

## Full combination scan — stock top breadth-qualified observations

### Lower rail: cleaner MID-before-BD
- L4 `BLUE|11_20|WICK_ONLY`: n=67, pooled=85.1%, breadth=12/12, median-symbol=100.0%, ret20=1.3%
- L5 `GRAY|BLUE|11_20|WICK_ONLY`: n=66, pooled=84.8%, breadth=11/11, median-symbol=100.0%, ret20=1.4%
- L7 `GRAY|BLUE|21_PLUS|WICK_ONLY|ABOVE|LG_Y`: n=75, pooled=81.3%, breadth=14/14, median-symbol=87.5%, ret20=1.4%
- L6 `GRAY|BLUE|21_PLUS|WICK_ONLY|ABOVE`: n=531, pooled=80.4%, breadth=30/30, median-symbol=81.8%, ret20=0.9%
- L7 `GRAY|BLUE|21_PLUS|WICK_ONLY|ABOVE|LG_N`: n=456, pooled=80.3%, breadth=30/30, median-symbol=82.0%, ret20=0.7%

### Lower rail: deeper BD-before-MID
- L4 `GREEN|11_20|CLOSE_BELOW`: n=60, pooled=85.0%, breadth=9/9, median-symbol=100.0%, ret20=0.5%
- L5 `GRAY|GREEN|11_20|CLOSE_BELOW`: n=59, pooled=84.7%, breadth=9/9, median-symbol=100.0%, ret20=0.4%
- L6 `GRAY|GREEN|11_20|CLOSE_BELOW|BELOW`: n=59, pooled=84.7%, breadth=9/9, median-symbol=100.0%, ret20=0.4%
- L7 `GRAY|GREEN|11_20|CLOSE_BELOW|BELOW|LG_N`: n=59, pooled=84.7%, breadth=9/9, median-symbol=100.0%, ret20=0.4%
- L6 `BLUE|GRAY|4_10|CLOSE_BELOW|BELOW`: n=52, pooled=75.0%, breadth=8/9, median-symbol=66.7%, ret20=1.4%

### Upper rail: MID-before-BS
- L2 `GREEN|4_10`: n=80, pooled=71.3%, breadth=14/16, median-symbol=66.7%, ret20=0.9%
- L3 `GRAY|GREEN|4_10`: n=77, pooled=72.7%, breadth=12/14, median-symbol=66.7%, ret20=0.9%
- L5 `BLUE|GRAY|21_PLUS|WICK_ONLY`: n=57, pooled=73.7%, breadth=7/9, median-symbol=100.0%, ret20=-2.6%
- L6 `BLUE|GRAY|21_PLUS|WICK_ONLY|ABOVE`: n=48, pooled=72.9%, breadth=6/8, median-symbol=83.3%, ret20=-2.4%
- L6 `GRAY|GREEN|11_20|WICK_ONLY|BELOW`: n=52, pooled=65.4%, breadth=6/8, median-symbol=83.3%, ret20=1.3%

### Upper rail: continuation BS-before-MID
- L4 `BLUE|11_20|CLOSE_ABOVE`: n=77, pooled=96.1%, breadth=12/12, median-symbol=100.0%, ret20=3.4%
- L5 `GRAY|BLUE|11_20|CLOSE_ABOVE`: n=77, pooled=96.1%, breadth=12/12, median-symbol=100.0%, ret20=3.4%
- L6 `GRAY|BLUE|11_20|CLOSE_ABOVE|ABOVE`: n=77, pooled=96.1%, breadth=12/12, median-symbol=100.0%, ret20=3.4%
- L7 `GRAY|BLUE|11_20|CLOSE_ABOVE|ABOVE|LG_N`: n=77, pooled=96.1%, breadth=12/12, median-symbol=100.0%, ret20=3.4%
- L4 `BLUE|21_PLUS|FULL_ABOVE`: n=66, pooled=89.4%, breadth=13/13, median-symbol=100.0%, ret20=2.9%

### True light-gray support
- L4 `BLUE|21_PLUS|ABOVE`: n=440, pooled=100.0%, breadth=30/30, median-symbol=100.0%, ret20=1.5%
- L5 `GRAY|BLUE|21_PLUS|ABOVE`: n=435, pooled=100.0%, breadth=30/30, median-symbol=100.0%, ret20=1.5%
- L4 `GRAY|4_10|ABOVE`: n=153, pooled=100.0%, breadth=26/26, median-symbol=100.0%, ret20=1.2%
- L4 `GRAY|21_PLUS|ABOVE`: n=129, pooled=100.0%, breadth=21/21, median-symbol=100.0%, ret20=0.7%
- L4 `GRAY|11_20|ABOVE`: n=122, pooled=100.0%, breadth=18/18, median-symbol=100.0%, ret20=1.9%

### True light-gray resistance
- L4 `GREEN|21_PLUS|BELOW`: n=159, pooled=100.0%, breadth=26/26, median-symbol=100.0%, ret20=1.0%
- L5 `GRAY|GREEN|21_PLUS|BELOW`: n=141, pooled=100.0%, breadth=22/22, median-symbol=100.0%, ret20=1.0%
- L4 `GRAY|4_10|BELOW`: n=129, pooled=100.0%, breadth=22/22, median-symbol=100.0%, ret20=1.4%
- L4 `BLUE|21_PLUS|BELOW`: n=119, pooled=100.0%, breadth=27/27, median-symbol=100.0%, ret20=2.3%
- L5 `GRAY|BLUE|21_PLUS|BELOW`: n=118, pooled=100.0%, breadth=27/27, median-symbol=100.0%, ret20=2.4%

## Full combination scan — crypto top breadth-qualified observations

### Lower rail: cleaner MID-before-BD
- L6 `GRAY|BLUE|21_PLUS|CLOSE_BELOW|ABOVE`: n=26, pooled=96.2%, breadth=4/4, median-symbol=100.0%, ret20=5.4%
- L7 `GRAY|BLUE|21_PLUS|CLOSE_BELOW|ABOVE|LG_N`: n=24, pooled=95.8%, breadth=4/4, median-symbol=100.0%, ret20=5.4%
- L7 `GRAY|BLUE|21_PLUS|WICK_ONLY|ABOVE|LG_Y`: n=21, pooled=90.5%, breadth=3/3, median-symbol=100.0%, ret20=-1.8%
- L4 `BLUE|21_PLUS|WICK_ONLY`: n=87, pooled=82.8%, breadth=4/4, median-symbol=85.7%, ret20=-1.4%
- L5 `GRAY|BLUE|21_PLUS|WICK_ONLY`: n=87, pooled=82.8%, breadth=4/4, median-symbol=85.7%, ret20=-1.4%

### Lower rail: deeper BD-before-MID
- L4 `GREEN|21_PLUS|CLOSE_BELOW`: n=35, pooled=71.4%, breadth=4/4, median-symbol=69.7%, ret20=1.2%
- L5 `GRAY|GREEN|21_PLUS|CLOSE_BELOW`: n=35, pooled=71.4%, breadth=4/4, median-symbol=69.7%, ret20=1.2%
- L6 `GRAY|GREEN|21_PLUS|CLOSE_BELOW|BELOW`: n=35, pooled=71.4%, breadth=4/4, median-symbol=69.7%, ret20=1.2%
- L7 `GRAY|GREEN|21_PLUS|CLOSE_BELOW|BELOW|LG_N`: n=35, pooled=71.4%, breadth=4/4, median-symbol=69.7%, ret20=1.2%
- L3 `BLUE|GRAY|11_20`: n=21, pooled=57.1%, breadth=2/4, median-symbol=58.3%, ret20=-3.3%

### Upper rail: MID-before-BS
- L3 `BLUE|GRAY|11_20`: n=20, pooled=75.0%, breadth=3/3, median-symbol=71.4%, ret20=0.6%
- L6 `GRAY|GREEN|21_PLUS|WICK_ONLY|BELOW`: n=42, pooled=71.4%, breadth=4/4, median-symbol=70.0%, ret20=-1.9%
- L7 `GRAY|GREEN|21_PLUS|WICK_ONLY|BELOW|LG_N`: n=39, pooled=69.2%, breadth=4/4, median-symbol=70.0%, ret20=-1.4%
- L4 `GREEN|21_PLUS|WICK_ONLY`: n=45, pooled=68.9%, breadth=4/4, median-symbol=68.3%, ret20=-1.4%
- L5 `GRAY|GREEN|21_PLUS|WICK_ONLY`: n=45, pooled=68.9%, breadth=4/4, median-symbol=68.3%, ret20=-1.4%

### Upper rail: continuation BS-before-MID
- L4 `BLUE|21_PLUS|CLOSE_ABOVE`: n=84, pooled=89.3%, breadth=4/4, median-symbol=90.9%, ret20=2.5%
- L5 `GRAY|BLUE|21_PLUS|CLOSE_ABOVE`: n=84, pooled=89.3%, breadth=4/4, median-symbol=90.9%, ret20=2.5%
- L6 `GRAY|BLUE|21_PLUS|CLOSE_ABOVE|ABOVE`: n=84, pooled=89.3%, breadth=4/4, median-symbol=90.9%, ret20=2.5%
- L7 `GRAY|BLUE|21_PLUS|CLOSE_ABOVE|ABOVE|LG_N`: n=84, pooled=89.3%, breadth=4/4, median-symbol=90.9%, ret20=2.5%
- L2 `BLUE|21_PLUS`: n=142, pooled=78.9%, breadth=4/4, median-symbol=78.6%, ret20=4.7%

### True light-gray support
- L4 `BLUE|21_PLUS|ABOVE`: n=72, pooled=100.0%, breadth=4/4, median-symbol=100.0%, ret20=-3.1%
- L5 `GRAY|BLUE|21_PLUS|ABOVE`: n=72, pooled=100.0%, breadth=4/4, median-symbol=100.0%, ret20=-3.1%
- L4 `GRAY|4_10|ABOVE`: n=24, pooled=100.0%, breadth=3/3, median-symbol=100.0%, ret20=-7.4%
- L4 `GRAY|11_20|ABOVE`: n=23, pooled=100.0%, breadth=3/3, median-symbol=100.0%, ret20=-6.1%
- L4 `GRAY|21_PLUS|ABOVE`: n=23, pooled=100.0%, breadth=4/4, median-symbol=100.0%, ret20=3.1%

### True light-gray resistance
- L4 `GRAY|21_PLUS|BELOW`: n=36, pooled=100.0%, breadth=4/4, median-symbol=100.0%, ret20=-2.1%
- L4 `GRAY|11_20|BELOW`: n=27, pooled=100.0%, breadth=4/4, median-symbol=100.0%, ret20=-4.3%
- L4 `GRAY|4_10|BELOW`: n=26, pooled=100.0%, breadth=3/3, median-symbol=100.0%, ret20=-2.3%
- L4 `GREEN|21_PLUS|BELOW`: n=22, pooled=100.0%, breadth=3/3, median-symbol=100.0%, ret20=0.3%
- L5 `GRAY|GREEN|21_PLUS|BELOW`: n=22, pooled=100.0%, breadth=3/3, median-symbol=100.0%, ret20=0.3%

## Interpretation boundary

The 11 prespecified candidates are the only formal confirmations in this round.

All L1-L7 combinations surfaced by the exhaustive scan are discovery /
robustness observations and are labeled
NEW_DISCOVERY_REQUIRES_FUTURE_VALIDATION.

No newly surfaced combination becomes a frozen trading rule from this dataset.
