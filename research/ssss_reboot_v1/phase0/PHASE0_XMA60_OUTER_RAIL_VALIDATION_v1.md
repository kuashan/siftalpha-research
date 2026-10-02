# SSSS Reboot v1 — Phase 0 XMA60 / Outer Rail Validation v1

Status: **PASS**
Date: 2026-10-02

## Question

The SSSS source uses:

`XMA(XMA(H,60),60)`

and:

`XMA(XMA(L,60),60)`

Because 60 is even, Phase 0 initially refused to silently replace it with 59 or
61.

## Independent implementation evidence

Audited public implementation:

Repository:
`liaoqifeng/fex-wallet-app`

Pinned source commit:
`330e04d3557403364ce0c40d8e50a059a9ab0155`

Path:
`static/js/umychart.complier.wechat.js`

The XMA implementation is:

```text
p = parseInt((n - 2) / 2)
start = i - p - 1
end   = i + (n - p) - 1
for j = start; j < end; ++j
    average available values
```

Therefore:

### N = 25

`p = 11`

full window:

`i-12 .. i+12`

= 25 observations.

### N = 60

`p = 29`

full window:

`i-30 .. i+29`

= exactly 60 observations.

At the right edge of a finite chart, unavailable future observations are
truncated. The value therefore repaints as later bars arrive.

Decision:

`XMA60_IS_NOT_NORMALIZED_TO_59_OR_61`

`XMA60_WINDOW = i-30 .. i+29`

## SSSS outer rails

Define:

`VH60 = XMA(XMA(H,60),60)`

`VL60 = XMA(XMA(L,60),60)`

`D60 = VH60 - VL60`

Source rails:

`BS = VH60 + 2.2*D60`

`BD = VL60 - 2.8*D60`

## Five Futu screenshot cross-checks

Independent U.S. daily OHLCV through 2026-10-01 was used to render the same
latest chart state.

Latest computed rails:

| Symbol | BS | BD |
|---|---:|---:|
| CRSP | 61.3347 | 46.8459 |
| PG | 151.7207 | 138.3454 |
| WMT | 114.1620 | 101.7576 |
| AAPL | 340.6341 | 299.8124 |
| ARM | 307.8115 | 217.2119 |

These values align with the positions of the outer upper/lower dashed rails in
all five user-supplied Futu screenshots.

The cross-symbol visual agreement is particularly useful because the five
symbols have materially different prices and price histories.

Decision:

`PHASE0_XMA60_SEMANTICS = PASS`

`PHASE0_BS_BD_VISUAL_MAPPING = PASS`

The reconstruction engine may now compute XMA(60), BS and BD directly.
