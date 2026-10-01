# SSSS Reboot v1 — ABT Single-Symbol Pilot Amendment

Status: **FROZEN BEFORE PILOT RUN**
Date: 2026-10-02

## Purpose

Reduce the first Rail Support / Resistance Study run from the full 39-stock
discovery universe to one calibrated symbol so that event definitions and
statistics can be validated quickly before scaling.

## Pilot symbol

ABT

Reason:
- ABT already passed the Phase-0 XMA25 numerical calibration;
- the corrected slow structure was also independently calibrated on ABT;
- therefore ABT is the lowest-risk symbol for validating the event engine itself.

## Pilot window

Daily bars:
2020-01-02 through 2025-12-31

Warm-up:
history beginning 2018-01-02 where available.

## Rules unchanged

All event definitions, XMA immutability constraints, FIRST_OBSERVED replay,
episode de-clustering, horizons, target-hit logic, MFE/MAE, and reporting rules
remain exactly as frozen in:

`RAIL_SUPPORT_RESISTANCE_PROTOCOL_v1.md`

Only the universe changes for this pilot.

## Scaling rule

Do not run the remaining 38 stocks until:

1. ABT pilot completes;
2. all four user questions have interpretable outputs;
3. event counts and first-hit logic reconcile;
4. no definition bug is found.

If the pilot reveals a definition bug, create a versioned protocol correction
before any multi-symbol run.

If the pilot passes, reuse the same frozen definitions for the broader universe.

## Status

`ABT_RAIL_STUDY_PILOT = READY`
