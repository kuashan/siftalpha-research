# SSSS Reboot v1 — ABT Rail Pilot v1.1 QA Correction

Status: **FROZEN BEFORE CLEAN RERUN**
Date: 2026-10-02

The first ABT pilot execution exposed two implementation/reporting issues.
The v1 raw execution is QA-only and must not be used for conclusions.

## Unchanged

No XMA formula or event hypothesis changes.

Unchanged:
- original XMA25 and XMA60;
- FIRST_OBSERVED replay;
- inner lower / upper definitions;
- MID support definition;
- outer rail definitions;
- slow-band directional approach definitions;
- all 5 / 10 / 20 / 40-bar horizons.

## Correction 1 — complete-horizon denominators

For every H-bar target-hit probability or first-hit race:
- denominator includes only events with at least H completed future bars;
- events near sample end without a complete H-bar future path are excluded from
  that H-bar probability.

They are not counted as failures.

## Correction 2 — slow-band episode de-clustering

Repeated consecutive bars satisfying the same directional slow-band contact
condition are one touch episode.

A new:
- SLOW_SUPPORT episode begins only when the support-from-above condition becomes
  true after being false on the prior bar;
- SLOW_RESIST episode begins only when the resistance-from-below condition
  becomes true after being false on the prior bar.

This applies the already-frozen episode principle consistently to the slow band.

## Governance

Because the correction was identified after seeing the first raw pilot output:
- the original v1 execution is marked QA_ONLY;
- all ABT pilot statistics are rerun from scratch under v1.1;
- only v1.1 may be cited as the ABT pilot result;
- no 39-stock scaling is allowed until v1.1 passes reconciliation.
