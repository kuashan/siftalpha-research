# SSSS Reboot v1 — ABT Calibration Anchor

Status: **CALIBRATION TARGET / NOT A TRADING RESULT**

Instrument: ABT
Date: 2025-01-15

Known calibration values:

- ZD1 = `110.99182102887214`
- GZB18 = `113.48360999503367`
- ZK1 = `115.9753989611952`

Relationship:

`GZB18 = (ZK1 + ZD1) / 2`

Before large-sample research, the rebuilt source engine should reproduce these
values to an explicitly documented numerical tolerance.

Passing this calibration does not validate a strategy.
It only validates a key source reconstruction checkpoint.
