# HYS2 Candidate Indicator Evaluation

Status: CANDIDATE FEATURE / NOT PROMOTED  
Added: 2026-09-28  
Source file SHA-256: `40936da053455c2e4d05d4bab3f28757e3c59c6cc92668e7c98dd443743799c3`  
Source size: 4713 bytes

## Role

HYS2 is **not** merged into the SSSS + ADKBY-E core.

The current core remains the original source-XMA structure.

HYS2 is evaluated as a candidate auxiliary indicator. It may be:
- HELPFUL,
- NEUTRAL,
- HARMFUL,
and can be used only in the situations where it demonstrates incremental value.

For US equities the source parameter is `SCQH=1`.

## Internal structure

HYS2 actually contains two largely independent families.

### A. 15-bar stochastic-style oscillator

```text
O00 = (C - LLV(L,15)) / (HHV(H,15) - LLV(L,15)) * 100
L1  = SMA(O00,3,1)
L2  = SMA(L1,3,1)
L3  = 3*L1 - 2*L2
```

Signals:
- bullish cross: CROSS(L1,L2) and L2 < 55
- bearish cross: CROSS(L2,L1) and L2 > 70
- "★共振": bullish cross + MACD histogram rising + L2 < 45

### B. 火焰山 extreme/panic layer

US mode uses long structural windows:
- HHV/LLV 250
- HHV/LLV 120
- HHV/LLV 60
- 30-bar extreme gate

The low-side event is gated by a new 30-bar low.

The high-side event is gated by a new 30-bar high.

## Important code findings

### 1. "★共振" does NOT include 火焰山

Despite the label, the resonance condition is only:

```text
CROSS(L1,L2)
AND MACD histogram rising
AND L2 < 45
```

It does not reference `火焰山底` or `火焰山顶`.

Therefore it should be recorded as:
**stochastic/MACD resonance**, not fire-mountain resonance.

### 2. High-side calculation is structurally suspect

The source computes a separate high-side chain:
- O06
- O07
- O08
- O09

but O05/O09 are never used by the final fire-mountain output.

The US `B_顶` instead reuses the same low-side panic variable `B_VD` used by `B_底`, with only the new-30-day-high gate changed.

This asymmetry may be intentional, but it is not assumed to be correct.

Research implication:
**火焰山顶 must not be treated as an automatic sell or short signal.**

### 3. VAR7H is effectively an availability gate

```text
VAR7H := IF(MA(CLOSE,58),1,0)
```

It does not compare the moving average with anything.

For ordinary positive-priced securities after sufficient history it is effectively 1.

### 4. Numerical edge cases

Potential denominator issues exist in:
- O00 if HHV(H,15) == LLV(L,15)
- O02 when its denominator collapses to zero
- O06 when its non-positive denominator collapses to zero

O06/O07 are currently dead for the final output, but the source behavior is preserved.

## Post-hoc ABT January 2025 evaluation

This evaluation was performed **after** the original January XMA decisions were frozen.

It must not modify the recorded January decisions or the +13.45% paper result.

### What HYS2 showed

- 2025-01-15:
  - new 30-day low
  - 火焰山底 jumped sharply
  - no bullish oscillator cross yet
  - no ★共振
- 2025-01-16:
  - L1 crossed above L2
  - L2 < 45
  - MACD histogram turned/rising
  - ★共振 = TRUE
- This aligns closely with the existing XMA sequence:
  - Jan-15 = PROBE_LONG
  - Jan-16 = ENTER_LONG confirmation

Therefore the **low-side + resonance family is promising as a confirmation layer**.

### False/noisy early bullish crosses

Generic HYS2 bullish crosses also occurred earlier in January without producing a complete XMA setup.

Therefore:
**generic L1/L2 bullish cross is not promoted as a standalone entry.**

### High-side behavior

火焰山顶 activated during the Jan-21 onward series of new 30-day highs.

But that was the same period in which the correct action under the XMA/momentum interpretation was to remain long and add, not short.

Therefore:
**火焰山顶 is HARMFUL if interpreted as an automatic short trigger in this month.**

It may still be useful as:
- extension warning,
- profit-protection context,
- "do not add blindly" context,
but it requires future evidence.

### Current candidate decision

Promote only to **CANDIDATE_FEATURE**:

1. HYS2 low-side event strength / new-30-day-low impulse
2. HYS2 ★共振

Do not promote:
1. generic bullish cross as standalone entry
2. 火焰山顶 as standalone sell/short
3. generic bearish cross as standalone short

## Forward rule

Beginning with future exploratory rounds, HYS2 is logged in parallel with the XMA core.

It may influence position size only after its incremental effect is explicitly recorded.

The baseline comparison must remain:

```text
XMA core decision
vs
XMA + HYS2 candidate
```

No retroactive rewrite of earlier decisions is allowed.
