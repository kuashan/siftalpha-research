# M1.1 Acceptance — 2026-10-01

Status: **CLOSED**

Bounded change:
- added configurable K-line intervals only;
- persisted selected interval in SQLite;
- preserved PAPER-only hard lock;
- did not change the frozen 5s-crypto V1 BUY/SELL equations.

Supported selections:
`15m / 1h / 2h / 4h / 6h / 12h / 1d`

Validation labels:
- `1d = VALIDATED_V1`
- all sub-daily selections = `EXPERIMENTAL_UNVALIDATED`

The execution invariant remains:
`Close Confirmed -> Next Bar Open`

Next allowed milestone remains M2.
