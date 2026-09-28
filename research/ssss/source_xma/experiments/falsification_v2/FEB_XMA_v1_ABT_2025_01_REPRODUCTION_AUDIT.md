# FEB_XMA_v1 ABT 2025-01 Reproduction Audit

Status: **IMPLEMENTED_AND_VERIFIED — ABT CALIBRATION PASS**

Date: 2026-09-29

Branch:
`research/source-xma-walkforward`

Pre-audit branch HEAD:
`5f569f0ba5c3f34c2a84d79408d0ad1bf679a1e9`

Purpose:
verify that the frozen `FEB_XMA_v1` mechanical engine can reproduce the
January 2025 ABT Source-XMA sequence before relying on any 39-symbol
full-history replay.

This audit does **not** optimize or modify FEB_XMA_v1.

## 1. Source evidence

ABT OHLCV:
- repository: `Devesh176/Replicating_portfolio`
- path: `data/ABT.csv`
- blob SHA: `e9071f4a01e8f50cdab0155b0779ef09ef85e1d4`

This is the same ABT source/blob recorded by the original January report.

Raw formula evidence was re-read directly from the preserved binaries:
- `source_indicators/SSSS.ftindex.b64`
- `source_indicators/ADKBY-E.ftindex.b64`

No EMA/DEMA substitute was used for XMA.

## 2. Recovered FEB_XMA_v1 formula dependencies

### Fast point-in-time Source-XMA

```text
VH25_X = XMA(XMA(H,25),25)
VL25_X = XMA(XMA(L,25),25)
D = VH25_X - VL25_X

FastUpper = VH25_X + D
FastLower = VL25_X - D
FastMid = (VH25_X + VL25_X) / 2
```

XMA is evaluated point-in-time using the centered/truncated source behavior.
Past endpoint values are not backfilled with later revised XMA values.

### Legacy raw ADKBY-E slow structure

The FEB engine intentionally uses the historical raw ADKBY-E weighted channel:

```text
WeightedH =
(20*H + 19*REF(H,1) + ... + 2*REF(H,18)
 + REF(H,19) + REF(H,20)) / 210

WeightedL =
(20*L + 19*REF(L,1) + ... + 2*REF(L,18)
 + REF(L,19) + REF(L,20)) / 210

D90H = EMA(WeightedH,90)
D90L = EMA(WeightedL,90)
D90  = D90H - D90L

SlowUpper = D90H + 2*D90
SlowLower = D90L - 2*D90
```

This preserves the raw historical 211-weight numerator / 210 denominator
behavior. It is not replaced by the later canonical corrected slow channel.

### Regime

```text
BULL:
FastLower >= SlowLower
AND FastUpper >= SlowUpper

BEAR:
FastUpper <= SlowUpper
AND FastLower <= SlowLower

RANGE:
FastLower >= SlowLower
AND FastUpper <= SlowUpper

otherwise:
EXPANSION
```

### Normalized position

Recovered directly from ADKBY-E:

```text
POS(X) =
(X - FastLower) / (FastUpper - FastLower) * 100000
```

Therefore:
- normalized low position = `POS(L)`
- normalized close position = `POS(C)`

### Source momentum

Recovered directly from ADKBY-E:

```text
DEA3_RAW =
EMA((EMA(C,3) - EMA(C,6)), 9)

DEA33B_RAW =
EMA(
  EMA(EMA(C,3) - EMA(C,9), 3)
  - EMA(EMA(C,3) - EMA(C,9), 9),
  9
)
```

Research directions:

```text
momentum_fast_delta =
DEA3_RAW(t) - DEA3_RAW(t-1)

momentum_slow_delta =
DEA33B_RAW(t) - DEA33B_RAW(t-1)

BOTH_UP:
fast_delta > 0 AND slow_delta > 0

BOTH_DOWN:
fast_delta < 0 AND slow_delta < 0

otherwise:
CONFLICT
```

### Source lower cross

SSSS raw source contains:

```text
CROSS(ZD1, L)
```

where `ZD1 = FastLower`.

The frozen full-history protocol uses normalized low position < 20,000 as the
inclusive lower-extreme implementation; this covers the lower-boundary cross
case without adding a new threshold.

### Relative volume

```text
RVOL20 = Volume / MA20(Volume)
```

## 3. January checkpoint reproduction

The reconstructed point-in-time calculations reproduce the original January
observation values to rounding precision.

### 2025-01-15 — lower-extreme probe

Key reconstructed values:

```text
FastLower = 110.991821
FastMid   = 113.483610
FastUpper = 115.975399

POS(L)    = -2645.10
DEA3_RAW  = -0.193882
DEA33B_RAW= -0.023868

fast delta = -0.080162
slow delta = -0.039733
momentum   = BOTH_DOWN
regime     = RANGE
RVOL20     = 1.315775
```

Result:
- non-BEAR;
- normalized low < 20,000;
- probe condition is true;
- momentum is still BOTH_DOWN.

`FEB_XMA_v1 => PROBE_LONG`.

### 2025-01-16 — reversal confirmation

```text
close       = 113.91
FastMid     = 113.409718
fast delta  = +0.043432
slow delta  = +0.001590
momentum    = BOTH_UP
```

The Jan-15 WATCH_LONG is active.

`FEB_XMA_v1 => CONFIRM_LONG`.

### 2025-01-21 — breakout add

```text
close       = 116.79
FastUpper   = 116.140706
fast delta  = +0.188585
slow delta  = +0.090004
momentum    = BOTH_UP
RVOL20      = 1.652595
```

`FEB_XMA_v1 => BREAKOUT_ADD`.

### 2025-01-28 — extreme deceleration reduce

```text
POS(C) = 196524.16

current fast+slow delta
= 0.240964 + 0.158118
= 0.399082

prior-session fast+slow delta
approximately
= 0.471542 + 0.262439
= 0.733981
```

The normalized close is >120,000 and momentum acceleration decelerated.

`FEB_XMA_v1 => REDUCE`.

### 2025-01-30 — exit

```text
POS(C)     = 192898.99
slow delta = -0.057935
regime     = BULL
```

Slow momentum is negative while price remains >80,000 normalized position.

`FEB_XMA_v1 => EXIT`.

## 4. Signal-date gate result

The frozen FEB engine reproduces the same five critical January signal dates:

| Signal date | Reproduced action |
|---|---|
| 2025-01-15 | PROBE_LONG |
| 2025-01-16 | CONFIRM_LONG |
| 2025-01-21 | BREAKOUT_ADD |
| 2025-01-28 | REDUCE |
| 2025-01-30 | EXIT |

Execution remains next tradable open with 5 bps one-way adverse slippage.

## 5. Capital-path calibration

The original January discovery used:

```text
30% -> 70% -> 100% -> 70% -> 0%
```

with executions:

| Signal | Execution | Action | Execution price |
|---|---|---|---:|
| 2025-01-15 | 2025-01-16 | probe | 111.075507 |
| 2025-01-16 | 2025-01-17 | confirm | 113.676813 |
| 2025-01-21 | 2025-01-22 | add | 114.187062 |
| 2025-01-28 | 2025-01-29 | reduce | 128.095924 |
| 2025-01-30 | 2025-01-31 | exit | 128.305810 |

Replaying those original January targets reproduces the archived result:

```text
$10,000 -> $11,345.4916
return   -> +13.45%
```

The later frozen `FEB_XMA_v1` intentionally changed the early sizing to:

```text
25% -> 65% -> 100% -> 70% -> 0%
```

Using the same signal dates and same execution prices gives approximately:

```text
$10,000 -> $11,329.76
return   -> +13.30%
```

Difference versus the January discovery result:

```text
-$15.73
approximately -0.16 percentage point
```

This is a sizing difference, not a timing, XMA, momentum, or formula mismatch.

## 6. Gate decision

`ABT_2025_01_REPRODUCTION = PASS`

The formula/action calibration gate is satisfied.

It is therefore legitimate to evaluate the frozen FEB_XMA_v1 logic on the
39-equity 2020-2025 history.

## 7. Important full-history integrity follow-up

The repository already contains a later 39-equity full-history replay.

That replay must not be silently rerun or overwritten.

Before treating its headline results as the final strict answer, audit:
1. indicator warm-up / NOT_READY behavior at the beginning of 2020;
2. deterministic action-priority semantics;
3. WATCH_LONG expiry semantics;
4. position-sizing accounting;
5. whether the persisted artifacts are sufficient to reproduce per-symbol CAGR
   and Sharpe;
6. whether the executable replay implementation itself was persisted.

No FEB_XMA_v1 threshold or trading rule may be changed during that audit.
