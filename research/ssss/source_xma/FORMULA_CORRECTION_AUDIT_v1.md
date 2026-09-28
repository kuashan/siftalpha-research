# Formula Correction Audit v1
Date: 2026-09-28
Status: CANONICALIZATION REQUIRED BEFORE NEXT RUN

## Decision

Before any further XMA geometry / auxiliary-factor research, the weighted-channel definitions must be canonicalized.

Original files are preserved unchanged as raw source evidence.

A corrected research specification is introduced separately.

## 1. SSSS GZB2 lag-11 bug

Raw source:

```text
...+10*REF(L,10)+9*REF(H,11)+8*REF(L,12)+...
```

Canonical correction:

```text
...+10*REF(L,10)+9*REF(L,11)+8*REF(L,12)+...
```

Reason:
GZB2 is a low-price weighted channel and every other term is based on L.

Downstream propagation:

```text
GZB2
-> GZB4 = EMA(GZB2,90)
-> GZB7 = GZB3-GZB4
-> GZB8 = GZB3+2*GZB7
-> GZB9 = GZB4-2*GZB7
-> GZB12/GZB13/GZB14 state classification
```

If GZB4 is biased upward by delta:

```text
GZB8 shifts by -2*delta
GZB9 shifts by +3*delta
slow-structure width narrows by 5*delta
```

The EMA90 smooths the error but does not remove it.

## 2. Canonical weighted 20-bar channel

Authoritative research definition:

```text
W20_H =
(20*H
+19*REF(H,1)
+18*REF(H,2)
+...
+2*REF(H,18)
+REF(H,19))/210

W20_L =
(20*L
+19*REF(L,1)
+18*REF(L,2)
+...
+2*REF(L,18)
+REF(L,19))/210
```

Properties:
- exactly 20 observations: lag 0..19
- weights: 20..1
- weight sum: 210
- denominator: 210

### SSSS raw inconsistency

Raw SSSS skips lag 19 and uses lag 20 at weight 1.

For the high channel, relative to canonical:

```text
RAW - CANONICAL
= (H[t-20] - H[t-19]) / 210
```

Low side is analogous, plus the separate GZB2 H/L bug.

### ADKBY-E raw inconsistency

Raw ADKBY-E uses both:
- REF(...,19)
- REF(...,20)

while denominator remains 210.

Thus weight sum is 211.

Relative to canonical:

```text
RAW - CANONICAL
= Price[t-20] / 210
```

This produces an approximate +0.476% level inflation for a slowly moving series and contaminates the slow D90 structure.

## 3. Cross-file authority

Research code must use one common canonical implementation for:
- SSSS GZB1/GZB2
- SSSS duplicate GZB5/GZB6
- ADKBY-E 短高H/短低L

Separate indicator files may duplicate the formula text because Futu formulas are not being assumed to support a shared external function.

The duplicated text must be byte-for-byte equivalent in the weighted expression.

## 4. HYS2 SCQH parameter

Important correction to the TXT-only interpretation:

The original HYS2.ftindex binary contains a parameter metadata record named:

```text
SCQH
```

Therefore SCQH is not truly undeclared at the .ftindex level.

The extracted TXT contains only the formula-body field and does not include the external parameter metadata.

Consequences:

- Original HYS2.ftindex can legitimately reference SCQH through its stored parameter metadata.
- A standalone copied TXT is not self-contained unless the user recreates SCQH in Futu's indicator parameter settings.
- Do NOT add `SCQH:=0` to the canonical cross-market version because that would hard-code A-share mode and disable 1=US / 2=Crypto switching.

A standalone research TXT may carry a note explaining this requirement.

## 5. Three-color state machine: missing state + equality overlap

Raw source:

```text
GZB12 := fastLower >= slowLower AND fastUpper >= slowUpper
GZB13 := fastUpper <= slowUpper AND fastLower <= slowLower
GZB14 := fastLower >= slowLower AND fastUpper <= slowUpper
```

Two issues exist:

### Missing fourth topology

```text
fastLower < slowLower
AND
fastUpper > slowUpper
```

Research label:

`EXPANSION_STRADDLE`

### Boundary overlap

Because raw conditions use >= and <= on shared equality boundaries:
- GZB12 and GZB14 can both be true when fastUpper == slowUpper;
- GZB13 and GZB14 can both be true when fastLower == slowLower;
- all three can coincide in the exact double-equality case.

For research-state classification, use a mutually exclusive four-state partition:

```text
UP_STATE:
fastLower >= slowLower
AND fastUpper > slowUpper

DOWN_STATE:
fastLower < slowLower
AND fastUpper <= slowUpper

RANGE_STATE:
fastLower >= slowLower
AND fastUpper <= slowUpper

EXPANSION_STRADDLE:
fastLower < slowLower
AND fastUpper > slowUpper
```

This preserves equality inside RANGE rather than allowing ambiguous state labels.

The original visual formula remains preserved; this four-state classification is the canonical research state machine.

## 6. Research governance impact

All previously generated Source-XMA results used one of the raw historical definitions.

Therefore they remain useful as:
`LEGACY_RAW_SOURCE_EXPLORATORY`

but they cannot be treated as validation of the corrected canonical model.

Before the next research run:
1. freeze canonical formulas;
2. regenerate all point-in-time XMA rails;
3. regenerate three-color states;
4. rerun geometry/event statistics;
5. only then re-test HYS2 / Volume / Volume Profile / Breadth / VIX.

Do not delete old results.
Do not overwrite history.
Mark old runs as legacy and compare raw-vs-canonical differences explicitly.
