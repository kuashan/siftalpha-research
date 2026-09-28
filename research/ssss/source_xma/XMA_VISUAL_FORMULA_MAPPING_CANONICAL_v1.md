# XMA Visual-to-Formula Mapping — Canonical v1

Status: PHASE 0 / PARTIALLY RESOLVED  
Date: 2026-09-28

## Canonical source files

The research baseline is now:
- SSSS_CANONICAL_v1
- ADKBY-E_CANONICAL_v1

Weighted slow channel is unified to lags 0..19 with weights 20..1 / 210.
GZB2 lag-11 is corrected to LOW.

## Formula-defined rails

### Fast 25-XMA channel

Let:

```text
A25 = XMA(XMA(H,25),25)
B25 = XMA(XMA(L,25),25)
D25 = A25 - B25
```

Then:

```text
ZK1 = GZB10 = A25 + D25 = 2*A25 - B25
ZD1 = GZB11 = B25 - D25 = 2*B25 - A25
GZB18 = (ZK1 + ZD1)/2 = (A25+B25)/2
```

Canonical SSSS explicitly draws:
- ZK1: white dotted line
- ZD1: white dotted line

GZB18 is calculated but is **not explicitly output as a plotted line** in the canonical source text.

Therefore the user's observed additional thin white middle rail is NOT yet proven to be GZB18.
It is a strong candidate, but requires visual/version confirmation.

### Slow corrected 20-weight / EMA90 structure

```text
W20_H = sum_{k=0..19} (20-k)*H[t-k] / 210
W20_L = sum_{k=0..19} (20-k)*L[t-k] / 210

GZB3 = EMA(W20_H,90)
GZB4 = EMA(W20_L,90)
D90  = GZB3-GZB4

GZB8 = GZB3 + 2*D90
GZB9 = GZB4 - 2*D90
```

The source fills the band GZB3..GZB4 in light gray.

### Outer 60-XMA rails

Let:

```text
A60 = XMA(XMA(H,60),60)
B60 = XMA(XMA(L,60),60)
D60 = A60-B60
```

Then the explicit outer rails are:

```text
BS = A60 + 2.2*D60
BD = B60 - 2.8*D60
```

Canonical source declares:
- BS = COLORRED
- BD = COLORGREEN

By formula geometry, BS is always the **upper** outer rail and BD the **lower** outer rail.

This conflicts with the user's verbal visual description of a lower red rail and upper green rail.

Research rule:
- never identify an outer rail only by perceived color;
- store formula id (BS / BD), price level, and rendered color separately;
- the visual color discrepancy must be resolved before naming events "red-rail" or "green-rail".

## Three-color band

The colored band itself spans:
- upper = GZB10 / ZK1
- lower = GZB11 / ZD1

State source conditions:
- GZB12
- GZB13
- GZB14

For research, use an exclusive four-state geometry:
- UP_STATE
- DOWN_STATE
- RANGE_STATE
- EXPANSION_STRADDLE

The original visual three-color conditions remain preserved separately.

## Phase-0 unresolved items

1. Which formula variable corresponds to the user's additional thin white middle rail?
2. Why does the user's perceived outer-rail color orientation appear opposite to BS/BD source declarations?
3. Does the currently installed Futu formula contain a visual-only output not present in the extracted canonical text?

Until resolved:
- analysis uses formula ids, not color names;
- GZB18 may be studied analytically as fast midpoint but not claimed as the visible middle white rail.
