# Canonical Geometry — Lifecycle Diagnostic

Status: SECONDARY DIAGNOSTIC  
Uses the already-frozen geometry thresholds.  
No threshold was changed after the first event-study result.

## Lower confluence as precursor

Strict lower episode:
- state = DOWN
- candle overlaps ZD1 and BD
- lower gap <= 0.5 ATR14
- repeated events within 3 bars deduplicated

Within the next 20 bars:
- total episodes: 28
- left DOWN state: 5
- remained DOWN through 20 bars / sample end: 23
- median lag to first non-DOWN state: 19.0 bars

This confirms that the color-state transition is often much slower than 5 bars.
Therefore the user's lower-confluence observation should be researched as a precursor rather than requiring same-day color reversal.

Current lifecycle hypothesis:

DOWN + lower confluence
=> WATCH / optional minimal probe

later:
DOWN -> RANGE/UP
=> confirmation candidate

later:
midpoint reclaim
=> stronger confirmation

The exact trade sizes are NOT defined in Phase 1.

## Upper confluence as warning

Strict upper episode:
- state = UP
- candle overlaps ZK1 and BS
- upper gap <= 0.25 ATR14
- episode-deduplicated

Within the next 20 bars:
- total episodes: 10
- left UP state: 6
- stayed UP: 4
- median lag to deterioration: 17.0 bars

This supports a two-step interpretation:

UP + strict upper confluence
=> EXTENDED / TOP WARNING

later:
UP -> RANGE/DOWN
=> exhaustion confirmation

It should not automatically open a short.

## Wick/body diagnostics

Lower reclaim at the strict lower episode:
- reclaim n=10
- 5-bar mean=-5.70%
- 5-bar median=-4.55%

No reclaim:
- n=18
- 5-bar mean=3.05%

Upper full rejection:
- n=3
- 5-bar mean=-2.50%

No full rejection:
- n=7
- 5-bar mean=-5.10%

Small subsamples are kept as INCONCLUSIVE rather than promoted.

## Next pure-XMA sequence to build

Priority sequence A:
lower confluence -> state improvement -> GZB18/midpoint reclaim

Priority sequence B:
upper confluence -> state deterioration -> GZB18/midpoint loss

Only after these sequences are quantified should HYS2 be tested as a confirmation layer.
