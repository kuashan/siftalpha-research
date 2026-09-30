# E034 Implementation / Causality Audit

Date: 2026-09-19

This audit was written during Discovery retrieval and before any aggregate E034 feature-outcome interpretation.

## Core lifecycle

The E034 implementation reuses the causal SSSS core semantics:

- DEMA fast band
- preserved slow-white-band lag anomalies
- ATR14 rolling mean
- dsep = sep - REF(sep, 5)
- Effective State changes only after three identical consecutive Raw State bars
- Qualified GRB requires Effective GREEN, FastUpper high-cross, dsep > 0, and PriceNearWhite
- signal is known after close
- execution occurs next bar open

No centered window is used.

## Feature audit

### ER10

Uses:
- C[t]
- C[t-10]
- absolute close-to-close path from t-9 through t

No future bars.

### CHOP14

Uses:
- TR[t-13..t]
- HH[t-13..t]
- LL[t-13..t]

No future bars.

### CMF20

Uses:
- H/L/C/V from t-19 through t

If H = L:
money-flow multiplier is set to 0 for that bar.

No future bars.

### OBVImpulse10

Uses:
- sign(C[i] - C[i-1]) * Volume[i]
- i = t-9..t
- divided by volume sum over the same 10 bars

No arbitrary full-history OBV starting value is needed.

No future bars.

## Snapshot audit

S0:
feature value on the Qualified GRB signal close.

S1:
feature value at the close of the OPEN execution bar, only if the trade remains active through that close.

No later bars are used to calculate the feature values.

The Mature / Failure label is outcome data used only after feature values are fixed.

## Missing-data rule

A feature is missing only when its pre-registered denominator or rolling history is unavailable.

Provider rate-limit responses are NOT missing market observations and must never be converted to zero-valued features or zero-event tickers.

## Current retrieval note

Equity batches 1 and 2 completed successfully.

A later batch encountered explicit provider RATE_LIMIT responses.

Those tickers remain pending and cannot be interpreted until retrieved.
