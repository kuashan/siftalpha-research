# AMZN 2025 FIVEGZ5SE SCTYPE=1 Small-Sample Reproduction v1

Status: **IMPLEMENTED_FOR_SMALL_SAMPLE_REPRODUCTION**

## Scope
- Symbol: AMZN
- Period: 2025-01-01 through 2025-12-31
- Trading sessions: 250
- SCTYPE: 1 (HK/US)
- Source blob: `8103be5ce8a065e2f753a4738b4b74a35361b291`

## Purpose
This run is an engine-reproduction exercise, not a signal-optimization exercise.
The original FIVEGZ5SE thresholds are unchanged.

For every 2025 trading session the replay stores:
- five rendered dimension states;
- t-1 -> t transition for all five dimensions;
- ordinal state deltas;
- selected underlying continuous calculations;
- original formula action-layer signal.

## Current findings
Formula action counts:
- NONE: 160
- RISK_SELL: 44
- HIGH_SELL: 16
- WARN: 10
- REDUCE: 6
- LOW_BUY: 6
- OPEN: 4
- WATCH: 3
- CLEAR: 1

Most frequent five-dimensional current states:
- LIGHT_LONG|LIGHT_LONG|LONG|LONG|GRAY: 24
- LIGHT_LONG|LIGHT_LONG|LIGHT_LONG|LONG|GRAY: 15
- SHORT|GRAY|SHORT|SHORT|GRAY: 13
- LIGHT_SHORT|GRAY|SHORT|SHORT|GRAY: 11
- LIGHT_LONG|LIGHT_LONG|LIGHT_LONG|LIGHT_LONG|GRAY: 9
- LIGHT_SHORT|LIGHT_SHORT|SHORT|SHORT|GRAY: 7
- GRAY|GRAY|LIGHT_LONG|GRAY|GRAY: 7
- SHORT|GRAY|LIGHT_SHORT|GRAY|GRAY: 6
- LIGHT_LONG|LONG|LONG|LONG|GRAY: 6
- GRAY|LIGHT_LONG|LIGHT_SHORT|SHORT|GRAY: 5
- SHORT|LIGHT_SHORT|SHORT|SHORT|GRAY: 5
- SHORT|GRAY|LIGHT_SHORT|LIGHT_SHORT|GRAY: 5
- LIGHT_LONG|LIGHT_LONG|LONG|LIGHT_LONG|GRAY: 4
- LIGHT_SHORT|GRAY|SHORT|GRAY|GRAY: 4
- LIGHT_SHORT|GRAY|LIGHT_SHORT|GRAY|GRAY: 4

Most frequent exact five-dimensional transitions:
- LIGHT_LONG>LIGHT_LONG|LIGHT_LONG>LIGHT_LONG|LONG>LONG|LONG>LONG|GRAY>GRAY: 9
- SHORT>SHORT|GRAY>GRAY|SHORT>SHORT|SHORT>SHORT|GRAY>GRAY: 4
- LIGHT_LONG>LIGHT_LONG|LIGHT_LONG>LIGHT_LONG|LIGHT_LONG>LIGHT_LONG|LIGHT_LONG>LONG|GRAY>GRAY: 4
- LIGHT_LONG>LIGHT_LONG|LIGHT_LONG>LIGHT_LONG|LIGHT_LONG>LIGHT_LONG|LONG>LONG|GRAY>GRAY: 4
- LIGHT_SHORT>SHORT|LIGHT_SHORT>GRAY|SHORT>SHORT|SHORT>SHORT|GRAY>GRAY: 3
- LIGHT_LONG>LIGHT_LONG|LONG>LIGHT_LONG|LONG>LONG|LONG>LONG|GRAY>GRAY: 3
- LIGHT_LONG>LIGHT_LONG|LIGHT_LONG>LIGHT_LONG|LONG>LONG|LONG>LIGHT_LONG|GRAY>GRAY: 3
- LIGHT_LONG>LIGHT_LONG|GRAY>LIGHT_LONG|LONG>LONG|LONG>LONG|GRAY>GRAY: 3
- SHORT>LIGHT_SHORT|GRAY>LIGHT_SHORT|LIGHT_SHORT>SHORT|SHORT>SHORT|GRAY>GRAY: 2
- SHORT>SHORT|GRAY>LIGHT_SHORT|SHORT>SHORT|SHORT>LIGHT_SHORT|GRAY>GRAY: 2
- SHORT>LIGHT_SHORT|LIGHT_SHORT>GRAY|SHORT>SHORT|SHORT>SHORT|GRAY>GRAY: 2
- SHORT>SHORT|GRAY>GRAY|LIGHT_SHORT>LIGHT_SHORT|LIGHT_SHORT>GRAY|GRAY>GRAY: 2
- GRAY>GRAY|GRAY>LIGHT_SHORT|LIGHT_LONG>LIGHT_LONG|GRAY>GRAY|GRAY>GRAY: 2
- GRAY>LIGHT_SHORT|LIGHT_SHORT>GRAY|LIGHT_LONG>SHORT|GRAY>SHORT|GRAY>GRAY: 2
- LIGHT_LONG>LONG|LIGHT_LONG>LONG|LONG>LONG|LONG>LONG|GRAY>GRAY: 2

## Interpretation boundary
No buy/sell edge is admitted from this single-symbol single-year reproduction.
This dataset is intended to:
1. inspect engine behavior;
2. identify state/transition coverage;
3. spot-check against Futu;
4. prepare the first descriptive transition statistics.

## Known source caveats retained
- `MOM_CONTINUOUS_DAYS=0` is kept unchanged.
- COUNT/label semantic issues are not silently repaired.
- "capital" remains a derived price/volume state, not literal institutional flow.
- `FORCAST` uses only data available through the current bar in the replay.

## Next acceptance gate
Spot-check selected AMZN dates in Futu against the generated five-dimension states.
If parity is confirmed, this implementation can proceed to preliminary 2025 transition/outcome statistics.

Closure:
`AMZN_2025_FIVEGZ5SE_SMALL_SAMPLE_REPRODUCTION = IMPLEMENTED`
