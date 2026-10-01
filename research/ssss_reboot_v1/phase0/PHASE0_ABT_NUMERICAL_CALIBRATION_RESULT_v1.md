# SSSS Reboot v1 — Phase 0 ABT Numerical Calibration Result v1

Status: **PARTIAL PHASE-0 PASS**
Date: 2026-10-02

No return, PnL, or trading-policy result is evaluated in this document.

## Data

Instrument: ABT
Interval: 1 day
Regular-session OHLCV
Independent provider query: Twelve Data
Calibration date: 2025-01-15

For fast-XMA calibration, data through 2025-01-15 only was supplied to the
point-in-time engine.

## Check A — point-in-time double-XMA25

Expected Futu/source calibration:

- ZD1 = `110.99182102887214`
- MID / GZB18 = `113.48360999503367`
- ZK1 = `115.9753989611952`

Independent reconstruction:

- VL25 = `112.65301367297714`
- VH25 = `114.31420631708596`
- ZD1 = `110.99182102886832`
- MID = `113.48360999503154`
- ZK1 = `115.97539896119478`

Absolute errors:

- ZD1: `3.82e-12`
- MID: `2.13e-12`
- ZK1: `4.12e-13`

Decision:

`PHASE0_DOUBLE_XMA25_NUMERIC_CALIBRATION = PASS`

## Check B — author-corrected 20..1 / 210 slow structure

Canonical formula:

`W_H = SUM((20-k)*H[t-k], k=0..19) / 210`

`W_L = SUM((20-k)*L[t-k], k=0..19) / 210`

followed by EMA90 and the SSSS slow structural expansion:

`slow_upper = EMA90(W_H) + 2*(EMA90(W_H)-EMA90(W_L))`

`slow_lower = EMA90(W_L) - 2*(EMA90(W_H)-EMA90(W_L))`

Using ABT history beginning 2019-01-02:

- W_H = `114.1274285714286`
- W_L = `112.48885714285714`
- EMA90(W_H) = `115.00270427399687`
- EMA90(W_L) = `113.20131548114325`
- slow_lower = `109.59853789543602`
- slow_upper = `118.6054818597041`

Formula-only reference values:

- slow_lower = `109.598537`
- slow_upper = `118.605482`

Absolute errors:

- slow_lower: `8.95e-7`
- slow_upper: `1.40e-7`

Decision:

`PHASE0_CANONICAL_SLOW_STRUCTURE_NUMERIC_CALIBRATION = PASS`

## Critical rendering distinction

A current Futu screenshot shows the indicator **rendered as of the screenshot's
latest bar**. Because XMA is centered/repainting, historical rails, colors and
icons near past right edges may have changed after later bars arrived.

Therefore Phase 0 uses two separate objects:

1. `RENDER_ASOF`
   - recompute the whole chart using data through one selected as-of date;
   - this is the correct object for comparison with a Futu screenshot.

2. `FIRST_OBSERVED`
   - for each historical t, recompute using only data <= t and persist the value
     visible then;
   - this is the correct object for later causal research.

Screenshot history must never be silently substituted for first-observed history.

## Remaining Phase 0 gates

Still open:

- Futu visual state-run reproduction on CRSP / PG / WMT / AAPL / ARM;
- lower/upper event timing reproduction;
- ADKBY 多/空/平 label timing reproduction;
- ADKBY star/warning timing reproduction;
- XMA(60) exact Futu period semantics and BS/BD numerical calibration.

Overall:

`PHASE0_SOURCE_RECONSTRUCTION = IN_PROGRESS`
