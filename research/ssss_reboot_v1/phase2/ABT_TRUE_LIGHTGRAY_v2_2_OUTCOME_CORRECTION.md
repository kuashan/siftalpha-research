# SSSS Reboot — True Light-Gray Band Outcome Correction v2.2

Status: **FROZEN BEFORE CLEAN RERUN**
Date: 2026-10-02
Supersedes the light-gray outcome interpretation in v2.1.

## Why

The true visual light-gray band is GZB4..GZB3.

Using ZD1/ZK1 first-hit order to define light-gray support/resistance success is
geometrically confounded because the three SSSS states already encode the
relative placement of the fast colored band versus the slow structure.

Therefore the light-gray band must be judged first by its own boundaries.

## Support from above

Entry event remains:
- prior Close > prior GZB3;
- current bar intersects [GZB4,GZB3];
- de-cluster consecutive contacts.

Primary response:
- SUPPORT_HOLD if, after the contact, price first achieves a decisive close
  above the then-current FIRST_OBSERVED GZB3 before any decisive close below
  the then-current GZB4.
- SUPPORT_BREAK if a decisive close below GZB4 occurs first.
- UNRESOLVED if neither occurs within the horizon.

## Resistance from below

Entry event remains:
- prior Close < prior GZB4;
- current bar intersects [GZB4,GZB3];
- de-cluster consecutive contacts.

Primary response:
- RESIST_HOLD if price first achieves a decisive close below the then-current
  FIRST_OBSERVED GZB4 before any decisive close above GZB3.
- RESIST_BREAK if a decisive close above GZB3 occurs first.
- UNRESOLVED otherwise.

## Horizons

Report first-exit response within:
- 5 bars
- 10 bars
- 20 bars

Also report:
- forward close return at 5/10/20
- MFE at 5/10/20
- MAE at 5/10/20

## Context

Break down by:
- UP / DOWN / RANGE
- state age bucket
- recent transition pair where n >= 5

## Main window

ABT daily, 2018-01-02 through 2025-12-31.
Earlier data are warm-up only.

## Governance

The prior v2.1 light-gray first-hit-to-ZD1/ZK1 interpretation is QA-only.
It must not be used to judge light-gray support/resistance.

No XMA formula is changed.
