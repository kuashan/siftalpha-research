# SSSS Reboot v1 — Phase 1 Data Provenance v1

Status: **RECORDED**
Date: 2026-10-02

Provider:
Twelve Data

Query type:
daily OHLCV time series

Market:
U.S. equities

Session handling:
regular-session bars; pre/post-market disabled.

Requested history:
2018-01-02 through 2026-10-02.

Structural counting window:
2020-01-02 through 2026-10-01 where returned history exists.

Symbols:
- ABT
- CRSP
- PG
- WMT
- AAPL
- ARM

ARM returned history begins 2023-09-14 and becomes Phase-1 ready after its
required warm-up.

No additional local price adjustment was applied beyond provider-returned OHLCV.

The raw provider payload is not treated as an immutable OOS dataset. Phase 1 is
a reconstruction/structure inventory, not an outcome-validation experiment.

All main historical counts use the FIRST_OBSERVED representation:
for each bar t, XMA values are recomputed with data available through t only.
