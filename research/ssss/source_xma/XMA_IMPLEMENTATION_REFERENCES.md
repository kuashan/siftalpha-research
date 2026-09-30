# XMA Implementation References

Recorded: 2026-09-28

Purpose: document independent public implementations used to understand and cross-check the source XMA behavior. These references do not replace Futu as the target behavior; they are implementation evidence.

## Reference A — HQChart-family implementation

Repository example:
- liaoqifeng/fex-wallet-app
- path: static/js/umychart.complier.wechat.js

Observed implementation:

```text
p = parseInt((n - 2) / 2)
start = i - p - 1
end   = i + (n - p) - 1
XMA[i] = average(data[start:end])
```

For N=25 this produces a centered 25-bar window around the current index when both sides exist, and truncates the window at the available left/right boundary.

Important walk-forward implication:
at the newest bar, the right side of the centered window is unavailable, so the endpoint value is calculated from the partial available window. As future bars arrive, previously observed XMA values can revise.

## Reference B — Guiyi Quant Workstation

Repository:
- firehell/guiyi-quant-workstation
- path: apps/quant-web/src/utils/indicators.ts

Its `tdxXma` normalizes the period to an odd number and computes the average of a symmetric radius around each point, truncating at series boundaries.

It also explicitly uses:

```text
xmaHigh = tdxXma(tdxXma(high, period), period)
xmaLow  = tdxXma(tdxXma(low, period), period)

upper = xmaHigh + (xmaHigh - xmaLow)
lower = xmaLow  - (xmaHigh - xmaLow)
```

This is the same double-XMA fast-band geometry present in SSSS / ADKBY-E.

## Cross-check result

The two independent public implementations agree on the key behavior needed for the ABT walk-forward study:

1. XMA is centered / uses observations on both sides when available.
2. At the right edge of a finite series it uses only currently available data.
3. As the series grows, historical values near the prior right edge can change.
4. Applying XMA twice compounds the revision horizon.

## Research rule

The initial ABT replay will implement the centered/truncated XMA behavior above and will explicitly record revision snapshots.

Before treating the local implementation as an exact Futu clone, compare selected reconstructed values/lines against the supplied Futu screenshots or direct Futu observations.

Do not substitute DEMA/EMA/SMA in this source-XMA track.
