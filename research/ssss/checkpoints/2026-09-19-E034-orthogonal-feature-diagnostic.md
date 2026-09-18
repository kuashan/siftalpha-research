# Research Checkpoint — 2026-09-19 — E034 Orthogonal Feature Diagnostic

## Status

NO_DIAGNOSTIC_CANDIDATE

## Duplication audit

Completed before pre-registration.

Included:
- ER10 — NEW
- CHOP14 — NEW
- CMF20 — PARTIAL_OVERLAP but materially different from generic volume filtering
- OBVImpulse10 — PARTIAL_OVERLAP but materially different from generic volume filtering

Deferred:
- RVOL20
- Squeeze
- NATR regime

## Equity Discovery

Coverage:
- 30 / 30 stocks
- 40 resolved lifecycles
- 31 Mature
- 9 Failure

### Signal-close snapshot

| Feature | Mature median | Failure median | Cliff delta | Gate |
|---|---:|---:|---:|---|
| ER10 | 0.2697 | 0.2668 | -0.039 | Fail |
| CHOP14 | 53.38 | 55.45 | -0.090 | Fail |
| CMF20 | 0.0455 | 0.0462 | -0.147 | Fail |
| OBVImpulse10 | 0.2162 | 0.2603 | -0.082 | Fail |

### Entry-day-close snapshot

| Feature | Mature median | Failure median | Cliff delta | Gate |
|---|---:|---:|---:|---|
| ER10 | 0.2392 | 0.3037 | -0.061 | Fail |
| CHOP14 | 51.79 | 56.98 | -0.190 | Fail |
| CMF20 | 0.0335 | 0.0415 | -0.061 | Fail |
| OBVImpulse10 | 0.2730 | 0.2335 | +0.011 | Fail |

No feature/snapshot reached the fixed |Cliff delta| >= 0.33 threshold together with quartile consistency.

CHOP14 at entry-day close was the largest equity separation, but remained below threshold and showed non-monotonic quartile Mature rates:
90%, 80%, 60%, 80%.

## Crypto Discovery

Provider:
Massive composite USD daily aggregates.

Coverage:
- BTC: 730 bars
- ETH: 730 bars
- SOL: 729 bars
- BNB: 198 bars

Resolved lifecycles:
- 7 total
- 4 Mature
- 3 Failure

All crypto diagnostics = TOO_SPARSE.

Directional observations such as ER10 signal-close Cliff delta = -1.00 are not accepted as evidence because n=7.

## Decision

- no OPEN filter added
- no ADD rule added
- no REDUCE/CLOSE change
- equity OOS not opened
- equity Frozen OOS not opened
- crypto OOS not opened
- crypto Frozen OOS not opened

## Research lesson

The first four open-source-derived single-snapshot features did not materially separate Mature from Failure in equities.

The crypto daily track cannot yet answer the question because the current accessible history produces too few independent SSSS lifecycles.

The next crypto-focused round should increase independent sample size through:
- a longer-history provider snapshot, or
- a separately pre-registered lower-timeframe transfer study,

rather than optimizing thresholds on the seven observed crypto trades.
