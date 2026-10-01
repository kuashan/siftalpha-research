# SSSS Reboot v1 — SSSS vs ADKBY-E Formula Audit v1

Status: **SOURCE-LEVEL COMPARISON COMPLETE / AUTHOR CORRECTIONS APPLIED**
Date: 2026-10-02

## Source identity

SSSS original:
- size: 5,118 bytes
- SHA-256: `25f8c56075c0021dd2d0567401d37def25d6a9b895f139b3a8a9abc376fecaa7`

ADKBY-E original:
- size: 6,328 bytes
- SHA-256: `7bbd62e04e0f529ff2040919f028416f5c892e9a00193d326556e36497d8ca5c`

The uploaded ADKBY-E checksum matches the preserved historical original.

## Author correction authority

The user/author has explicitly clarified two source typos:

1. the low weighted series must use `L`, including the lag-11 term;
2. the intended weighted average is a 20-term 20..1 series whose weights sum to
   exactly `210`.

Therefore the research engine must use the corrected canonical form:

`W_H = (20*H + 19*REF(H,1) + ... + 2*REF(H,18) + REF(H,19)) / 210`

`W_L = (20*L + 19*REF(L,1) + ... + 2*REF(L,18) + REF(L,19)) / 210`

The raw source files remain preserved byte-for-byte as archival evidence, but the
known typos above are **not** treated as alternative research variants.

Specifically:
- SSSS `9*REF(H,11)` in the low line is corrected to `9*REF(L,11)`;
- the stray `REF(...,20)` term is not part of the intended 20-term weighted
  average;
- ADKBY-E's simultaneous `REF(...,19)+REF(...,20)` is also treated as a source
  typo because it produces numerator weight 211 while the intended denominator
  and weight total are 210.

## Executive result

ADKBY-E is not an unrelated strategy.

It shares the same core double-XMA25 high/low channel as SSSS. Its 20,000 /
50,000 / 80,000 normalized levels map exactly to the SSSS lower rail, analytical
midpoint and upper rail.

After applying the author-confirmed weighted-channel corrections, the slow
weighted inputs of SSSS and ADKBY-E should be treated as the **same intended
20-term weighted construction**.

Remaining material differences are:
1. ADKBY-E has no SSSS XMA60 outer-rail system;
2. ADKBY-E normalizes price into a fixed oscillator-like coordinate system;
3. its red/green candle classification is not exactly the same as the SSSS
   momentum-overlay logic;
4. ADKBY-E adds explicit 多/空/平 semantics and divergence warnings.

## 1. Shared double-XMA25 core

Define:

`VL25 = XMA(XMA(L,25),25)`

`VH25 = XMA(XMA(H,25),25)`

`D = VH25 - VL25`

SSSS:

`ZK1 = VH25 + D`

`ZD1 = VL25 - D`

ADKBY-E:

`高0 = VH25 + D`

`低0 = VL25 - D`

Therefore:

`ADKBY 高0 == SSSS ZK1`

`ADKBY 低0 == SSSS ZD1`

This is an exact algebraic identity before considering XMA point-in-time behavior.

## 2. ADKBY normalized 20k / 50k / 80k mapping

ADKBY-E defines:

`短顶 = VH25 + 2D`

`短底 = VL25 - 2D`

and maps price P to:

`N(P) = (P - 短底) / (短顶 - 短底) * 100000`

Since the span is `5D`:

- `N(ZD1) = 20000`
- `N((ZK1+ZD1)/2) = 50000`
- `N(ZK1) = 80000`

Therefore:

- ADKBY 20,000 买线 == SSSS ZD1
- ADKBY 50,000 中线 == SSSS GZB18
- ADKBY 80,000 卖线 == SSSS ZK1

## 3. Corrected canonical slow weighted structure

The canonical intended high series is:

`W_H = (20*H + 19*REF(H,1) + 18*REF(H,2) + ... + 2*REF(H,18) + REF(H,19)) / 210`

The canonical intended low series is:

`W_L = (20*L + 19*REF(L,1) + 18*REF(L,2) + ... + 2*REF(L,18) + REF(L,19)) / 210`

Weight total:

`20 + 19 + ... + 2 + 1 = 210`

Then:

`SLOW_TOP = EMA(W_H,90)`

`SLOW_BOTTOM = EMA(W_L,90)`

This corrected canonical form is authoritative for the reboot research.

The malformed raw-source terms are retained only in the archived original files,
not in the rebuilt research engine.

## 4. Three regime states

Using the corrected common slow structure:

`UP = ZD1 >= SLOW_BOTTOM AND ZK1 >= SLOW_TOP`

`DOWN = ZK1 <= SLOW_TOP AND ZD1 <= SLOW_BOTTOM`

`RANGE = ZD1 >= SLOW_BOTTOM AND ZK1 <= SLOW_TOP`

SSSS and ADKBY-E use the same logical topology for these three states after the
known weighted-channel typos are corrected.

Both also leave a fourth topology outside the three labels:

`ZD1 < SLOW_BOTTOM AND ZK1 > SLOW_TOP`

This is an expansion/straddle state.

## 5. XMA60 outer rails — SSSS only

SSSS contains a second double-XMA family using period 60.

Define:

`VL60 = XMA(XMA(L,60),60)`

`VH60 = XMA(XMA(H,60),60)`

`D60 = VH60 - VL60`

SSSS plots:

`BS = VH60 + 2.2*D60`

`BD = VL60 - 2.8*D60`

ADKBY-E contains no equivalent double-XMA60 outer-rail family.

Therefore ADKBY-E's visible 顶/底 or extended 25-XMA references must not be
equated with SSSS BS/BD.

## 6. Light-gray slow band

SSSS explicitly draws the corrected:

`SLOW_TOP ~ SLOW_BOTTOM`

as the light-gray structural band.

ADKBY-E uses the same intended slow weighted construction primarily as a regime
reference in its normalized sub-chart rather than exposing the same price-chart
band.

## 7. Momentum core

Both formulas use the same two raw momentum components:

`M1 = EMA(EMA(C,3)-EMA(C,6),9)`

`M2 = EMA(EMA(EMA(C,3)-EMA(C,9),3)-EMA(EMA(C,3)-EMA(C,9),9),9)`

SSSS defines:
- rising if either component rises;
- falling if either component falls.

ADKBY-E defines:

`ISRED = component1_rising OR component2_rising`

and green as:

`NOT(ISRED)`

These are not completely equivalent in mixed-direction or flat edge cases.

## 8. Rail-cross event topology

Under a common regime classification and positive XMA25 channel width:

ADKBY:

`CROSS(20000, normalized_low)`

corresponds to SSSS:

`CROSS(ZD1, L)`

and:

ADKBY:

`CROSS(normalized_high, 80000)`

corresponds to SSSS:

`CROSS(H, ZK1)`

The six regime-conditioned event families therefore align structurally.

## 9. Additional ADKBY-E semantics

ADKBY-E adds:
- normalized 0..100000 visualization;
- explicit 多 / 空 / 平 labels;
- momentum/price divergence warning semantics.

Those semantic labels are useful for understanding intended presentation, but
they are not automatically accepted as optimal trading rules.

## 10. Reboot implication

For SSSS Reboot v1:

- SSSS is the primary source.
- ADKBY-E is a related derived presentation of the same XMA25 core.
- the author-confirmed H/L and 210-weight corrections are now canonical;
- raw typo behavior must not be backtested as if it were intentional;
- SSSS XMA60 outer rails remain a genuine SSSS-only structural component;
- trading conclusions remain unfrozen.

No trading rule is promoted by this source audit.
