# SSSS Reboot — ABT State-Relationship Rail Study v2 Result

Status: **COMPLETE / SINGLE-SYMBOL PILOT**
Date: 2026-10-02

## Objective

Identify which state relationships make lower-rail events better BUY candidates
and upper-rail events better SELL candidates.

No XMA structure was modified.
All history was replayed FIRST_OBSERVED bar-by-bar.

## BUY side — lower rail

Candidate contexts with n >= 5, ordered by MID-before-BD rate:

- **UP|LATE_21_PLUS** — n=26; MID-first 61.5%; BD-first 38.5%; hit upper 50.0%; median MFE 2.7%; median MAE -4.0%; median 20d return -0.2%
- **DOWN|LATE_21_PLUS** — n=12; MID-first 58.3%; BD-first 41.7%; hit upper 83.3%; median MFE 7.3%; median MAE -2.6%; median 20d return 5.1%
- **UP|MATURE_11_20** — n=6; MID-first 50.0%; BD-first 50.0%; hit upper 50.0%; median MFE 5.4%; median MAE -3.3%; median 20d return 2.7%
- **DOWN|MATURE_11_20** — n=11; MID-first 9.1%; BD-first 90.9%; hit upper 54.5%; median MFE 4.7%; median MAE -4.1%; median 20d return 0.8%

### Recent state transitions, n >= 5

- **RANGE->DOWN** — n=5; MID-first 0.0%; BD-first 100.0%; hit upper 20.0%; MFE 2.2%; MAE -6.3%

## SELL side — upper rail

Candidate contexts with n >= 5, ordered by MID-before-BS rate:

- **DOWN|LATE_21_PLUS** — n=15; MID-first 60.0%; BS-first 40.0%; hit lower 53.3%; median upside adverse excursion 3.0%; median downside excursion 6.3%; median 20d return 0.8%
- **UP|LATE_21_PLUS** — n=24; MID-first 54.2%; BS-first 41.7%; hit lower 58.3%; median upside adverse excursion 2.6%; median downside excursion 4.4%; median 20d return -2.6%
- **RANGE|MATURE_11_20** — n=8; MID-first 25.0%; BS-first 75.0%; hit lower 25.0%; median upside adverse excursion 8.0%; median downside excursion 2.0%; median 20d return 6.7%
- **UP|MATURE_11_20** — n=5; MID-first 0.0%; BS-first 100.0%; hit lower 60.0%; median upside adverse excursion 4.0%; median downside excursion 5.3%; median 20d return -3.6%
- **UP|EARLY_4_10** — n=8; MID-first 0.0%; BS-first 100.0%; hit lower 25.0%; median upside adverse excursion 5.7%; median downside excursion 1.4%; median 20d return 3.5%

### Recent state transitions, n >= 5

No recent-transition upper-rail group reached n>=5.

## Interpretation rule

This result is used to identify candidate BUY / SELL locations, but no context
is frozen as a trading rule from ABT alone.

Contexts with n < 5 are retained in the JSON ledger but are not promoted.

The next validation step should use one additional stock with the same frozen
definitions before broad scaling.
