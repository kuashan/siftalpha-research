# Falsification v1 — Auxiliary Feature Data Availability Audit

Status: TERMINAL DATA-AVAILABILITY CLASSIFICATION  
Date: 2026-09-28

## Purpose

Determine whether the preregistered expanded-holdout tests for:
- Below-VAL;
- HYS2;
- Volume;
- Breadth;
- VIX

can be completed from the preserved v1 repository artifacts without changing data provenance after outcome inspection.

## What is preserved

The repository contains Discovery / exploratory auxiliary studies from Jan–Jun 2025, including:

- canonical_geometry_2025_01_06/HYS2_CONFIRMATION_RESULTS.*
- canonical_geometry_2025_01_06/ORTHOGONAL_CONFIRMATION_RESULTS.*
- orthogonal_2025_03_06/*

Those studies are explicitly labelled Discovery / exploratory, not Validation A/B OOS.

They cannot be substituted for:
- Validation A: 2020–2024;
- Validation B: 2025H2.

## What the v1 holdout artifacts contain

The persisted Falsification v1 event files contain:
- XMA geometry/state;
- dev20;
- prior20 return;
- ATR/close;
- returns;
- MFE/MAE;
- matched-control results;
- benchmark-relative returns.

They do not contain expanded-holdout:
- HYS2 oscillator/fire features;
- rolling Value Area / BELOW_VAL labels;
- Volume Structure labels;
- Breadth series/features;
- VIX rate/MA-relative/acceleration features.

The repository also does not persist the full 39-symbol raw daily OHLCV panel used to generate these holdout events.

## Why the features are not rebuilt now

Re-downloading 2020–2025H2 history from a new or current external vendor after inspecting the holdout outcomes would create:
- data-vendor drift;
- adjustment drift;
- timestamp/revision ambiguity;
- new post-outcome implementation degrees of freedom.

Therefore v1 does not reconstruct missing auxiliary features post hoc.

## Terminal v1 classifications

### Lower BELOW_VAL interaction
**INCONCLUSIVE / DATA NOT AVAILABLE**

Discovery evidence exists, but expanded Validation A/B feature labels were not preserved.

### HYS2 2x2 / logistic interaction
**INCONCLUSIVE / DATA NOT AVAILABLE**

Discovery HYS2 feature results exist, but the required expanded-holdout HYS2 feature panel is not preserved.

### Volume capitulation interaction
**INCONCLUSIVE / DATA NOT AVAILABLE**

### Breadth interaction
**INCONCLUSIVE / DATA NOT AVAILABLE**

### VIX expanded descriptive dimensions
**INCONCLUSIVE / DATA NOT AVAILABLE**

## HYS2 redundancy wording

Discovery showed:
- fire-bottom present in all strict lower episodes in that discovery sample;
- fire-top present in all strict upper episodes in that discovery sample.

Therefore the strongest allowed statement remains:

**REDUNDANT WITHIN STRICT XMA EVENT SAMPLE**

Reverse containment is not available on the expanded holdout, so:
**global redundancy is not established.**

## v2 requirement

If these features are studied in v2, before any outcome is inspected the repository must freeze and persist:
- exact raw-data source/version;
- point-in-time feature code;
- per-date feature snapshots for the full frozen universe;
- HYS2 raw components, not only binary labels;
- Volume/Profile/Breadth/VIX feature values;
- source hashes.

No v1 result is retroactively rewritten.
