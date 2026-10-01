# SSSS Reboot v1 — SSSS vs ADKBY-E Formula Audit v1

Status: **SOURCE-LEVEL COMPARISON COMPLETE / NO TRADING CONCLUSION**
Date: 2026-10-02

## Source identity

SSSS:
- original size: 5,118 bytes
- SHA-256: `25f8c56075c0021dd2d0567401d37def25d6a9b895f139b3a8a9abc376fecaa7`

ADKBY-E:
- uploaded size: 6,328 bytes
- uploaded SHA-256: `7bbd62e04e0f529ff2040919f028416f5c892e9a00193d326556e36497d8ca5c`

The uploaded ADKBY-E checksum matches the preserved historical original.

## Executive result

ADKBY-E is not an unrelated strategy.

It shares the same core double-XMA25 high/low channel as SSSS and its 20,000 /
50,000 / 80,000 normalized levels map exactly to the SSSS lower rail, analytical
midpoint and upper rail.

However ADKBY-E is **not a formula-equivalent copy of SSSS**.

Material differences:
1. the slow weighted 90 structure is different;
2. ADKBY-E has no SSSS XMA60 outer-rail system;
3. ADKBY-E normalizes price into a fixed oscillator-like coordinate system;
4. its red/green candle classification is not exactly the same as the SSSS
   momentum-overlay logic;
5. ADKBY-E adds explicit 多/空/平 semantics and divergence warnings that are not
   present as equivalent text semantics in SSSS.

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

This is an exact algebraic identity before considering XMA repainting behavior.

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

This is one of the most important source-level equivalences.

## 3. Slow weighted structure — material difference

### SSSS actual state-driving slow input

SSSS `GZB1` high series:
- uses weights 20..2 for lag 0..18;
- omits lag 19;
- uses lag 20 with weight 1;
- denominator = 210.

SSSS `GZB2` low series:
- same lag-19 omission;
- uses lag 20 with weight 1;
- critically, the lag-11 term is `9*REF(H,11)`, not `9*REF(L,11)`.

Then:

`GZB3 = EMA(GZB1,90)`

`GZB4 = EMA(GZB2,90)`

These are the actual slow values used by SSSS state classification.

SSSS also computes `GZB5/GZB6`, where the low lag-11 term uses L correctly,
but those variables do not drive `GZB3/GZB4` and therefore do not repair the
actual displayed/state slow band.

### ADKBY-E slow input

ADKBY-E `短高H` and `短低L`:
- include both lag 19 and lag 20 with weight 1;
- use `REF(L,11)` in the low series;
- still divide by 210.

Because both lag 19 and lag 20 are included, the listed ADKBY numerator weights
sum to 211 while the denominator remains 210.

Therefore ADKBY-E does **not** reproduce the SSSS slow band exactly.

This can alter regime classification near slow-boundary transitions.

## 4. Three regime states — same logical form, different slow inputs

SSSS:

`UP = ZD1 >= slow_bottom AND ZK1 >= slow_top`

`DOWN = ZK1 <= slow_top AND ZD1 <= slow_bottom`

`RANGE = ZD1 >= slow_bottom AND ZK1 <= slow_top`

ADKBY-E uses the same logical inequalities for:
- 多头定位
- 空头定位
- 震荡定位

So the topology is the same.

But because the slow structure differs, the resulting labels are not guaranteed
to match bar-for-bar.

Both formulas also leave a fourth topology outside the three labels:

`lower < slow_bottom AND upper > slow_top`

This is the expansion/straddle case and is not one of the three named states.

## 5. XMA60 outer rails — SSSS only

SSSS contains a second double-XMA family using period 60.

It computes 60-XMA structures and explicitly plots:

`BS = VH60 + 2.2 * (VH60 - VL60)`

`BD = VL60 - 2.8 * (VH60 - VL60)`

ADKBY-E contains no double-XMA60 rail family.

Therefore ADKBY-E's visible 顶/底 or stop references must not be equated with
SSSS BS/BD.

ADKBY-E instead defines 25-XMA-based reference values such as:
- `VL25 - 3.5D`
- `VH25 + 3.5D`

These are a different construction.

## 6. Light-gray slow band — explicit in SSSS, implicit in ADKBY-E

SSSS explicitly draws the `GZB3 ~ GZB4` slow band in light gray.

ADKBY-E does not expose the same band as a price-chart band.
It uses its D90-derived top/bottom primarily to determine background regime.

Thus ADKBY-E preserves the idea of a slow structural regime but changes the
presentation and, because of the input differences above, changes the exact values.

## 7. Momentum core — same raw components

Both formulas use:

`EMA(EMA(C,3)-EMA(C,6),9)`

and:

`EMA(EMA(EMA(C,3)-EMA(C,9),3)-EMA(EMA(C,3)-EMA(C,9),9),9)`

SSSS defines:
- rising if either component rises;
- falling if either component falls.

ADKBY-E defines:

`ISRED = component1_rising OR component2_rising`

and then green as:

`NOT(ISRED)`

These are **not fully equivalent**.

Example:
- component A rises;
- component B falls.

SSSS:
- rising condition = true;
- falling condition = true.

ADKBY-E:
- ISRED = true;
- NOT(ISRED) = false;
- result is red only.

Also, if both components are exactly flat:
- SSSS rising=false and falling=false;
- ADKBY-E classifies the candle as green because NOT(ISRED)=true.

Therefore the raw momentum series are shared, but the binary color collapse in
ADKBY-E changes edge cases and mixed-direction cases.

## 8. Rail-cross event topology

Under a common regime classification and positive channel width:

ADKBY:

`CROSS(20000, normalized_low)`

is equivalent in inequality topology to:

SSSS:

`CROSS(ZD1, L)`

Likewise:

ADKBY:

`CROSS(normalized_high, 80000)`

corresponds to:

SSSS:

`CROSS(H, ZK1)`

The six regime-conditioned event families align structurally:

| SSSS event | ADKBY semantic text |
|---|---|
| UP + lower crossing | 多头多定位 = 多 |
| UP + upper crossing | 多头平定位 = 平 |
| DOWN + upper crossing | 空头空定位 = 空 |
| DOWN + lower crossing | 空头平定位 = 平 |
| RANGE + lower crossing | 震荡多定位 = 多 |
| RANGE + upper crossing | 震荡空定位 = 空 |

The event geometry is therefore strongly shared.

The semantic interpretation is not: SSSS draws lower/upper icons, while ADKBY-E
explicitly assigns 多/空/平 text according to regime.

## 9. Additional ADKBY-E logic not present as equivalent SSSS semantics

ADKBY-E adds a normalized sub-chart and explicit divergence warnings.

It compares actual candle-body direction with its momentum color:

- main candle up + ADKBY momentum green near/above the 80k sell region -> warning;
- main candle down + ADKBY momentum red near/below the 20k buy region -> star.

These warning semantics are additional ADKBY behavior.

SSSS has white/magenta rail interaction overlays, but those are not formula-identical
to the ADKBY warning system.

## 10. Research implication for SSSS Reboot

For the reboot:

- SSSS remains the primary source under study.
- ADKBY-E should be treated as a **related derived formulation / interpretation**.
- ADKBY-E can help reveal intended meanings of the SSSS inner XMA25 geometry.
- It must not be used to silently "correct" SSSS source anomalies.
- The SSSS slow-band source behavior must first be reproduced exactly as written.
- A separate variant may later test whether the ADKBY slow implementation is a
  deliberate correction, but that must be preregistered and compared separately.

No trading rule is promoted by this source audit.
