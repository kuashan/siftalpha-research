# Conditional SSSS Rail Rules v1 — Round 1 Result

Status: ROUND1_COMPLETE / DISCOVERY_AND_ROBUSTNESS
Date: 2026-10-01

Universe:
- 39 frozen US equities
- 2019 warm-up only
- evaluation: 2020-01-01 through 2025-12-31
- strict literal point-in-time Source-XMA at every bar
- total classified events: 14,147

Event counts:
- LOWER_FAST 2,581
- UPPER_FAST 3,038
- LOWER_OUTER 1,026
- UPPER_OUTER 1,721
- GRAY_SUPPORT 3,110
- GRAY_RESIST 2,671

## Main finding 1 — DOWN + fast lower is the strongest stable lower-side candidate

DOWN + LOWER_FAST:
- n=629
- 20-bar mean +2.975%
- median +2.707%
- positive 61.6%
- 34/39 symbols have positive mean outcome
- block A 2020-2022 +2.513%
- block B 2023-2024 +3.332%
- block C 2025 +3.786%
- reaches midpoint within 40 bars: 99.5%
- reaches upper rail: 90.5%
- median time to midpoint: 5 bars
- median time to upper rail: 13 bars
- 20-bar MFE +9.62%
- 20-bar MAE -6.72%

This is materially stronger and more stable than UP or RANGE lower events.

UP + LOWER_FAST:
- n=1,343
- 20-bar mean +1.293%
- median +1.259%
- positive 57.6%
- positive symbol means 25/39

RANGE + LOWER_FAST:
- n=607
- 20-bar mean +1.099%
- median +1.185%
- positive 57.7%
- positive symbol means 24/39

Interpretation:
DOWN + lower rail survives all three time blocks and cross-symbol robustness.
It is a strong candidate for PROBE_ENTRY research, not yet an automatic full-size buy.

## Main finding 2 — fast lower events almost always recover midpoint, but new lows are also common

Across lower states:
- midpoint recovery is ~99%
- upper-rail recovery is ~89-90%
- but new-low occurrence is also very high (~87-91%)

Therefore:
A lower-rail touch alone has a large adverse path risk before recovery.
This strongly supports testing staged entry and midpoint confirmation rather than all-in entry.

## Main finding 3 — fast upper touch is NOT a generic sell signal

UP + UPPER_FAST:
- n=1,654
- 20-bar mean +1.241%
- median +0.893%
- positive 54.4%
- reaches midpoint 98.6%
- reaches lower rail 81.3%
- but also makes a new high 93.2%

DOWN + UPPER_FAST:
- n=742
- 20-bar mean +2.130%
- median +2.057%
- positive 60.0%
- 32/39 symbols positive mean

RANGE + UPPER_FAST:
- n=638
- 20-bar mean +1.024%
- median +1.263%
- positive 56.9%

Interpretation:
Upper-rail events frequently pull back to midpoint/lower, but also frequently make new highs.
Therefore upper touch itself should be WATCH/REDUCE candidate at most.
The stronger sell logic must be sought in path confirmation, such as midpoint loss plus state deterioration.

## Main finding 4 — DOWN + lower outer rail is a robust support/extreme candidate

DOWN + LOWER_OUTER:
- n=479
- 20-bar mean +3.159%
- median +2.414%
- positive 61.4%
- 32/39 symbols positive mean
- block A +3.085%
- block B +2.548%
- block C +4.413%

RANGE + LOWER_OUTER:
- n=263
- mean +1.808%
- median +0.888%

UP + LOWER_OUTER:
- n=282
- mean -0.120%
- median -0.290%
- unstable across blocks

Interpretation:
Lower outer rail is useful only conditionally.
DOWN + lower outer is a strong candidate for escalation/additional-entry research.
UP + lower outer is not robust.

## Main finding 5 — upper outer rail is NOT resistance

UP + UPPER_OUTER:
- n=1,146
- 20-bar mean +1.150%
- median +0.746%
- positive 53.7%

DOWN + UPPER_OUTER:
- n=197
- mean +1.854%
- median +1.976%

RANGE + UPPER_OUTER:
- n=377
- mean +0.324%
- median +0.567%

Interpretation:
The data contradict a simple "touch upper outer = sell" rule.
Upper outer must not be used as a standalone exit trigger.

## Main finding 6 — light-gray band is structural, not simple support/resistance

GRAY_SUPPORT from above:
UP:
- n=1,629
- 20-bar mean +0.903%
- positive symbol means only 20/39

DOWN:
- n=249
- mean +1.172%
- but 2025 block turns negative (-1.378%)

RANGE:
- n=1,220
- mean +0.912%
- median +0.830%
- stable positive across all three time blocks
- 27/39 symbols positive mean

Interpretation:
RANGE + approach-from-above gray-band interaction is the most stable support-like gray-band condition.
UP and DOWN versions are weaker/less stable.

GRAY_RESIST from below:
UP:
- n=436
- mean +0.698%
- unstable across blocks
- only 17/39 symbols positive mean

DOWN:
- n=1,025
- mean +1.438%
- not durable resistance

RANGE:
- n=1,196
- mean +0.930%

Interpretation:
The gray band is not a universal resistance area from below.

## Round 1 candidate map

Promote to Round 2 testing:
1. DOWN + LOWER_FAST -> PROBE_ENTRY candidate.
2. DOWN + LOWER_OUTER -> escalation / deeper-entry candidate.
3. Lower event -> midpoint reclaim -> CONFIRM_ENTRY candidate.
4. UPPER_FAST -> WATCH/REDUCE candidate only after additional confirmation.
5. UPPER_FAST + midpoint loss + adverse state transition -> EXIT candidate to test.
6. RANGE + gray-band touch from above -> support/re-entry candidate.
7. UPPER_OUTER alone -> rejected as sell trigger.

Not promoted:
- any-color lower = automatic buy
- any-color upper = automatic sell
- upper outer = sell
- gray band = universal support/resistance

Next:
Round 2 must test conditional paths and transitions without changing Round 1 definitions.
