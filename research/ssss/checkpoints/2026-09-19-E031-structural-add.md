# Research Checkpoint — 2026-09-19 — E031 Structural ADD

## Experiment

E031 — Structural Confirmation ADD

Status: REJECT_DISCOVERY

## Governance

Pre-registered before results:
- Discovery: 30 stocks
- OOS: 10 stocks
- Frozen OOS: 5 stocks
- six fixed variants
- fixed metrics and gates

Intermittent market-data rate limits occurred during Discovery, but the original 30-stock cohort was eventually completed without substitutions.

OOS was not opened.
Frozen OOS was not opened.

## Structural variable

StructuralSep = (FastMid - WhiteMid) / WhiteWidth

Thresholds:
- 0.50
- 1.00
- 1.50

Modes:
- B: dsep > 0 and close >= FastMid
- X: dsep > 0 and close > FastUpper

## Discovery result

| Variant | Signals | Resolved | Stocks | Win rate | Avg | Median | PF | Median entry ATR distance | Median Red lead |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| S050B | 43 | 34 | 25 | 35.3% | +4.21% | -2.90% | 2.24 | 2.50 | 4 |
| S100B | 38 | 29 | 24 | 34.5% | +4.22% | -2.97% | 2.30 | 3.00 | 2 |
| S150B | 16 | 13 | 13 | 38.5% | +11.05% | -3.13% | 4.35 | 3.09 | 1 |
| S050X | 24 | 19 | 19 | 26.3% | +3.96% | -3.47% | 2.05 | 3.11 | 3 |
| S100X | 19 | 15 | 16 | 40.0% | +10.07% | -2.70% | 4.24 | 3.40 | 2 |
| S150X | 12 | 9 | 11 | 44.4% | +12.88% | -3.13% | 4.80 | 3.40 | 1 |

All six medians were negative.

## Decision

Reject E031 at Discovery.

Do not open OOS.
Do not open Frozen OOS.
Do not add an ADD transition.

## Main lesson

Structural separation becomes stronger and later, but the average is increasingly carried by a few major winners.

This is not a robust incremental-entry rule because the typical ADD leg remains negative.
