# SSSS V4 — Five Candidate OOS Validation Final Result

Status: **COMPLETE**
Date: 2026-10-02

## Existing validated core

The previously validated V3 conditions remain preserved and are not downgraded
or re-tuned by this round.

### Cross-asset validated core retained

- **BUY_BLUE_21P_LOWER** — BUY_CANDIDATE; stocks n=1049, p=70.6%; crypto n=139, p=80.6%
- **BUY_GRAY_4_10_LIGHT_SUPPORT** — BUY_SUPPORT_CANDIDATE; stocks n=263, p=74.1%; crypto n=55, p=80.0%
- **BUY_RECENT_BLUE_GRAY_LIGHT_SUPPORT** — BUY_SUPPORT_CANDIDATE; stocks n=117, p=81.2%; crypto n=27, p=85.2%
- **CONT_BLUE_11_20_UPPER** — HOLD_NOT_SELL; stocks n=165, p=85.5%; crypto n=20, p=65.0%
- **SELL_RECENT_BLUE_GRAY_LIGHT_RESIST** — SELL_TRIM_CANDIDATE; stocks n=160, p=71.9%; crypto n=21, p=85.7%

### Stock-validated / crypto-insufficient core retained

- **AVOID_GREEN_11_20_LOWER** — WAIT_FOR_BD; stocks n=135, p=70.4%; crypto remains INSUFFICIENT_BREADTH
- **CONT_BLUE_4_10_UPPER** — HOLD_NOT_SELL; stocks n=116, p=75.9%; crypto remains INSUFFICIENT_BREADTH
- **CONT_RECENT_GRAY_BLUE_UPPER** — HOLD_NOT_SELL; stocks n=106, p=77.4%; crypto remains INSUFFICIENT_BREADTH

## V4 untouched validation design

Track A:
- untouched nine stocks: MA, CAT, BA, GE, XOM, CVX, LIN, NEE, PLD
- 2018-2025
- never used to discover the five V4 candidates

Track B:
- all 39 stocks + BTC/ETH/BNB/SOL
- forward-time OOS beginning 2026-01-01
- only complete 20-bar outcomes counted

## Final status of the five new candidates

### NEW_BUY_1
- BLUE 11-20 + LOWER + WICK_ONLY -> MID before BD
- **Final: PENDING_MORE_OOS_DATA**
- Track A 9-stock OOS: MIXED; n=28; p=75.0%; support breadth=5/9
- Track B 2026 stocks: INSUFFICIENT_BREADTH; n=5; p=100.0%
- Track B 2026 crypto: INSUFFICIENT_BREADTH; n=0; p=—

### NEW_AVOID_BUY_1
- GREEN 11-20 + LOWER + CLOSE_BELOW -> BD before MID
- **Final: PENDING_MORE_OOS_DATA**
- Track A 9-stock OOS: INSUFFICIENT_BREADTH; n=16; p=93.8%; support breadth=4/5
- Track B 2026 stocks: INSUFFICIENT_BREADTH; n=10; p=100.0%
- Track B 2026 crypto: INSUFFICIENT_BREADTH; n=1; p=100.0%

### NEW_HOLD_1
- BLUE 11-20 + UPPER + CLOSE_ABOVE -> BS before MID
- **Final: PENDING_MORE_OOS_DATA**
- Track A 9-stock OOS: SUPPORTS_V3_DISCOVERY; n=25; p=92.0%; support breadth=6/6
- Track B 2026 stocks: INSUFFICIENT_BREADTH; n=11; p=81.8%
- Track B 2026 crypto: INSUFFICIENT_BREADTH; n=1; p=100.0%

### NEW_HOLD_2
- BLUE 21+ + UPPER + FULL_ABOVE -> BS before MID
- **Final: PENDING_MORE_OOS_DATA**
- Track A 9-stock OOS: INSUFFICIENT_BREADTH; n=13; p=76.9%; support breadth=3/3
- Track B 2026 stocks: INSUFFICIENT_BREADTH; n=4; p=100.0%
- Track B 2026 crypto: INSUFFICIENT_BREADTH; n=0; p=—

### NEW_SELL_1
- GREEN 4-10 + UPPER -> MID before BS
- **Final: PENDING_MORE_OOS_DATA**
- Track A 9-stock OOS: INSUFFICIENT_BREADTH; n=17; p=58.8%; support breadth=3/5
- Track B 2026 stocks: INSUFFICIENT_BREADTH; n=10; p=50.0%
- Track B 2026 crypto: INSUFFICIENT_BREADTH; n=0; p=—

## Interpretation

### Strongest replication, but not yet formally promotable

**NEW_HOLD_1 — BLUE 11-20 + UPPER + CLOSE_ABOVE**
- discovery: 96.1% BS-before-MID
- untouched 9-stock OOS: 23/25 = **92.0%**
- 6/6 eligible untouched stocks support
- 2026 stocks: 9/11 = **81.8%**
- 2026 forward breadth is still too sparse for the pre-frozen promotion rule

This is the strongest V4 candidate and remains the highest-priority candidate
for continued forward accumulation.

**NEW_AVOID_BUY_1 — GREEN 11-20 + LOWER + CLOSE_BELOW**
- discovery: 85.0% BD-before-MID
- untouched 9-stock OOS: 15/16 = **93.8%**
- 2026 stocks: 10/10 = **100%**
- both OOS tracks point in the same direction, but neither meets the pre-frozen
  minimum event/breadth requirement for formal promotion

This is also a very strong directional replication.

### Directionally positive but not broad enough

**NEW_BUY_1 — BLUE 11-20 + LOWER + WICK_ONLY**
- untouched 9-stock OOS: 21/28 = **75.0%**
- nine eligible symbols, but only 5/9 are strictly >50%; the other four are
  neutral at 50%, so Track A is MIXED under the frozen breadth rule
- 2026 stocks: 5/5, but very sparse

**NEW_HOLD_2 — BLUE 21+ + UPPER + FULL_ABOVE**
- untouched 9-stock OOS: 10/13 = **76.9%**
- 2026 stocks: 4/4
- event counts are too low for promotion

### Weakest current replication

**NEW_SELL_1 — GREEN 4-10 + UPPER**
- untouched 9-stock OOS: 10/17 = **58.8%**
- 2026 stocks: 5/10 = **50.0%**
- this does not currently reproduce the original 71.3% effect strongly
- status stays PENDING_MORE_OOS_DATA rather than FAILED because frozen breadth
  thresholds are not met

## Current research hierarchy

### VALIDATED_CORE_V3
Preserve unchanged.

### V4 HIGH-PRIORITY FORWARD CANDIDATES
1. NEW_HOLD_1 — BLUE 11-20 + UPPER + CLOSE_ABOVE
2. NEW_AVOID_BUY_1 — GREEN 11-20 + LOWER + CLOSE_BELOW

### V4 MEDIUM-PRIORITY
3. NEW_BUY_1 — BLUE 11-20 + LOWER + WICK_ONLY
4. NEW_HOLD_2 — BLUE 21+ + UPPER + FULL_ABOVE

### V4 LOW-PRIORITY / CURRENTLY WEAK
5. NEW_SELL_1 — GREEN 4-10 + UPPER

No V4 candidate is promoted to VALIDATED_V4 yet because the pre-registered
two-track promotion rule has not been satisfied.

`SSSS_V4_FIVE_CANDIDATE_OOS = COMPLETE`
