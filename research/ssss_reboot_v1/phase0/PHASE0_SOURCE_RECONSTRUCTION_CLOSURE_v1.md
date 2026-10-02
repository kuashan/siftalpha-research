# SSSS Reboot v1 — Phase 0 Source Reconstruction Closure v1

Status: **PHASE 0 COMPLETE / PASS**
Date: 2026-10-02

## Scope

Phase 0 reconstructs the source formulas only.

It does not evaluate profitability and does not promote any BUY / SELL policy.

## Closed gates

### 1. Raw source recovery

PASS:
- SSSS original preserved;
- ADKBY-E original preserved;
- source hashes recorded.

### 2. Author-confirmed source corrections

PASS:
- low weighted line uses L, not the erroneous H term;
- weighted channel is 20 terms, weights 20..1;
- total weight = 210;
- final intended lag = 19;
- stray lag-20 source entries are not part of the canonical reconstruction.

### 3. Double-XMA25 numerical calibration

ABT 2025-01-15:

Expected:
- ZD1 = 110.99182102887214
- MID = 113.48360999503367
- ZK1 = 115.9753989611952

Independent reconstruction error:
approximately 1e-12.

PASS.

### 4. Canonical slow structure numerical calibration

ABT 2025-01-15:

- slow lower = 109.59853789543602
- slow upper = 118.6054818597041

Matches independent formula reference to approximately 1e-6.

PASS.

### 5. Regime/color reconstruction

Five real Futu examples:
- CRSP
- PG
- WMT
- AAPL
- ARM

Corrected reconstruction independently reproduces the major visible BLUE /
GREEN / GRAY state blocks.

PASS.

### 6. SSSS / ADKBY-E core mapping

PASS:
- same intended XMA25 core;
- ADKBY 20k = SSSS ZD1;
- ADKBY 50k = SSSS MID;
- ADKBY 80k = SSSS ZK1;
- same intended state topology;
- same lower/upper cross event geometry;
- ADKBY adds semantic text and warning/star presentation.

### 7. XMA60 and outer rails

PASS:
- exact 60-sample even-period centered window identified from independent
  implementation evidence;
- 59/61 substitutions rejected;
- BS / BD formulas implemented;
- five Futu screenshot rail locations cross-checked.

### 8. Repainting boundary

PASS:
Two representations are permanently separated:

- RENDER_ASOF = reproduce a Futu chart as rendered at one as-of date;
- FIRST_OBSERVED = causal historical ledger using only information available at t.

Current screenshots may validate RENDER_ASOF.
They must never be substituted for FIRST_OBSERVED history.

## Non-blocking visual detail

Exact date-level matching for every historical icon in a static screenshot
remains difficult because the screenshots do not expose a cursor/date for each
icon.

This does not block source reconstruction.

Exact event dates will be generated and audited in Phase 1 when the structural
inventory/event ledger is built.

## Closure

`PHASE0_SOURCE_RECONSTRUCTION = PASS`

`PHASE0_CLOSED = TRUE`

Authorized next phase:

`PHASE1_STRUCTURAL_INVENTORY`

Phase 1 remains descriptive only:
- no forward returns;
- no profitability ranking;
- no BUY/SELL promotion;
- no position sizing.
