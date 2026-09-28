# Canonical XMA Geometry — Phase 1–5 Synthesis

Status: DISCOVERY SYNTHESIS  
Date: 2026-09-28  
Formula baseline: corrected canonical v1

## 1. The user's upper-confluence observation has strong preliminary support

Strict event:
- state = UP
- candle overlaps fast upper ZK1 and outer upper BS
- rail distance <= 0.25 ATR14
- repeated observations deduplicated into episodes

Episode-deduplicated result:
- n = 10
- +5 bar mean = -4.32%
- +5 bar median = -5.16%
- +10 bar mean = -6.36%
- +10 bar median = -6.48%
- +5 positive rate = 30%

Stocks alone:
- n = 8
- +5 mean ≈ -2.96%

Crypto:
- n = 2
- +5 mean ≈ -9.75%

This is materially different from ordinary UP-state rail riding when BS remains >0.5 ATR away:
- n = 53
- +5 mean = +0.40%
- +5 median = +0.50%
- +5 positive rate = 54.7%

Interpretation:
**outer/fast rail convergence is a different market geometry from normal upper-rail riding.**

This is the most important discovery so far.

Status:
`KEEP AS PRIORITY HYPOTHESIS`

It is not yet an automatic short rule.

## 2. Lower confluence is not an unconditional buy

Strict lower precursor:
- state = DOWN
- candle overlaps ZD1 + BD
- gap <= 0.5 ATR
- deduplicated

Result:
- n = 28
- +5 mean ≈ -0.07%
- +5 median ≈ +0.04%
- +10 mean ≈ +1.50%
- +10 median ≈ +2.54%
- +20 mean ≈ +4.52%

This looks more like an **early precursor** than an immediate timing signal.

Only 5/28 episodes left DOWN state within the next 20 bars.
Median lag among those transitions was 19 bars.

Therefore:
```text
lower confluence in DOWN
!= immediate confirmed buy

better interpretation:
WATCH / early reversal candidate
```

## 3. Full same-bar lower reclaim did not improve the event

A very strict same-bar reclaim definition produced worse short-horizon results.

This is important negative evidence:
the strategy should NOT assume:
`deep wick below both rails + close back above both = automatically better`.

The exact candle-shape rule remains open.

Status:
`DROP CURRENT RECLAIM DEFINITION`

## 4. HYS2 did not improve the strict lower XMA episode in this window

Recent HYS2 ★ resonance (previous 3 bars through event):
- present n = 9
- +5 mean ≈ -2.95%
- absent n = 19
- +5 mean ≈ +1.29%

Ordinary HYS bullish cross produced the same split in this sample.

Fire-bottom was active in all 28 strict lower episodes, so it provided no discrimination.

Interpretation:
- HYS2 fire-bottom may be detecting the same extreme condition already encoded by the XMA lower geometry;
- HYS2 resonance is NOT promoted as a lower-confluence confirmation.

Status:
- Fire-bottom: `REDUNDANT / OBSERVE`
- ★ resonance: `HARMFUL IN THIS EVENT DEFINITION / DO NOT PROMOTE`

This does not mean HYS2 has no value elsewhere.

## 5. HYS2 did not add clear upper-top discrimination

Fire-top was present in all 10 strict upper episodes, so it added no separation.

Bear cross:
- present n = 4
- absent n = 6
- both groups remained negative on average
- sample too small for promotion

Interpretation:
strict XMA upper geometry itself carried most of the signal in this window.

## 6. Orthogonal factors — lower precursor

### Volume Structure

Lower episodes:
- NEUTRAL n=16, +5 mean ≈ -0.29%
- NEGATIVE n=8, +5 mean ≈ +4.50%
- POSITIVE n=4, +5 mean ≈ -8.33%

The negative-volume subgroup is interesting:
it may represent capitulation rather than healthy trend participation.

But positive-volume n=4 is too small and may be event-specific.

Status:
`OBSERVE CAPITULATION HYPOTHESIS`

Do NOT use "more volume = better buy".

### Volume Profile

Lower episodes:
- BELOW_VAL n=22, +5 mean ≈ +0.90%, positive rate ≈59%
- INSIDE_VALUE n=6, +5 mean ≈ -3.65%, positive rate ≈17%

This is the cleanest auxiliary separation on the lower-side event so far.

Interpretation:
a DOWN-state lower XMA confluence occurring **below the rolling value area** may represent a more meaningful price-dislocation setup than the same geometry inside accepted value.

Status:
`PRIORITY CANDIDATE`

Exact intraday Volume Profile is still required for a stronger claim.

### Breadth

Lower episodes during negative breadth:
- n=8
- +5 mean ≈ +3.50%
- median ≈ +4.79%

Neutral breadth:
- n=20
- +5 mean ≈ -1.50%

This suggests lower-confluence reversals may benefit from broad panic / washout rather than broad strength.

But the breadth source is only a frozen 15-name proxy.

Status:
`OBSERVE`

### VIX

Frozen VIX rule was neutral for all strict lower and upper episodes.

Status:
`NULL RESULT FOR THIS RULE`

## 7. Orthogonal factors — upper warning

No tested auxiliary clearly improved the strict upper-confluence event.

Volume, Profile, Breadth and HYS2 all had small subgroups without a robust separator.

This strengthens a key research principle:
**the upper geometry itself may be the important information.**

The next refinement should focus on:
- duration of prior UP state
- rail convergence speed
- candle body/wick placement
- midpoint loss after the event

rather than adding more indicators.

## 8. Current research architecture

### Lower side

```text
DOWN + lower outer/fast confluence
=> WATCH / dislocation candidate

Priority context:
BELOW_VAL Volume Profile
possible capitulation volume
broad negative breadth

Not promoted:
HYS2 resonance
same-bar full reclaim
```

### Upper side

```text
UP + strict upper outer/fast confluence
=> EXTENDED / TOP WARNING

not:
automatic short

then observe:
state deterioration
midpoint loss
failure to resume rail ride
```

### Trend continuation

```text
UP + fast upper interaction
+ outer upper rail still materially far away
+ positive rail slopes
=> ordinary rail ride / continuation candidate
```

This is distinctly different from strict upper confluence.

## 9. Highest-priority next work

1. Resolve the exact visual mapping of the extra thin white rail.
2. Quantify:
   `upper confluence -> midpoint loss`
   versus
   `upper confluence -> resume rail ride`.
3. Quantify:
   `lower confluence below VAL -> later midpoint reclaim`.
4. Add exact Volume-at-Price when intraday data are available.
5. Keep HYS2 recorded but do not let it override the current XMA geometry result.
