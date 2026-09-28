# Falsification v1 — Independence Audit

Status: COMPLETE FOR EVENT-WAVE COUNTS; ICC-ESS REPORTED AS SENSITIVITY  
Date: 2026-09-28

## Definitions

Primary market-wave definition is the already-frozen rule:
events linked within <=2 trading days across symbols are grouped into one connected market wave.

A <=5 trading-day linkage is added only as an independence sensitivity check.
It does not replace the frozen primary definition and does not change any hypothesis status.

Important:
**market-wave cluster count != Effective Sample Size (ESS).**

## Raw episodes vs market waves

| Window | Event | Raw n | ±2-day waves | ±5-day sensitivity waves |
| --- | --- | ---: | ---: | ---: |
| A | Upper | 392 | 173 | 65 |
| A | Lower | 325 | 118 | 50 |
| B | Upper | 46 | 19 | 7 |
| B | Lower | 20 | 12 | 10 |
| Combined | Upper | 438 | 192 | 72 |
| Combined | Lower | 345 | 130 | 60 |

Frozen ±2-day interpretation:
- 438 Upper episodes correspond to 192 market-wave clusters.
- 345 Lower episodes correspond to 130 market-wave clusters.

The widened linkage is much more aggressive:
- Upper: 192 -> 72 waves.
- Lower: 130 -> 60 waves.

This large change means wave counts are definition-sensitive.

It does **not** imply that 72 or 60 is the true ESS.
The widened connected-component rule can chain neighboring episodes into long waves and is therefore reported only as sensitivity.

## Approximate ICC-based ESS

The following is supplemental, not the primary inferential method.

Primary v1 uncertainty remains symbol/month clustered bootstrap.

Approximate ESS is calculated on frozen matched-excess outcomes using a one-way random-effects ICC and unequal-cluster effective cluster size.

### Upper — 5-bar matched excess

| Window | Matchable N | Symbol ESS | Month ESS |
| --- | ---: | ---: | ---: |
| A | 392 | 318.2 | 228.4 |
| B | 39 | 36.0 | 18.4 |
| Combined | 431 | 374.0 | 238.9 |

### Lower — 10-bar matched excess

| Window | Matchable N | Symbol ESS | Month ESS |
| --- | ---: | ---: | ---: |
| A | 325 | 107.7 | 181.6 |
| B | 12 | 7.0 | 12.0 |
| Combined | 337 | 109.0 | 203.7 |

### Lower — 20-bar matched excess

| Window | Matchable N | Symbol ESS | Month ESS |
| --- | ---: | ---: | ---: |
| A | 325 | 147.0 | 137.3 |
| B | 12 | 7.1 | 9.1 |
| Combined | 337 | 146.8 | 150.3 |

Validation B Lower ESS estimates are especially unstable because only 12 events are matchable.
A negative month ICC on the 10-bar B subset is truncated to zero for ESS, so the reported month ESS=N is not evidence of true independence.

## Interpretation

1. Raw episode n materially overstates the number of distinct market contexts.
2. Frozen ±2-day market-wave counts must be reported next to raw n in major v1 conclusions.
3. ±5-day counts are a sensitivity warning, not a replacement event count.
4. Approximate ICC-based ESS is metric- and clustering-dimension-specific; it is not a single universal sample size.
5. Symbol/month clustered bootstrap remains the primary uncertainty measure.
6. No trading hypothesis status is changed by choosing a wider wave window.
