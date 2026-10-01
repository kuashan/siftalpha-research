# SSSS Reboot v1 — Futu Visual Ground Truth v1

Status: **REAL FUTU DISPLAY EVIDENCE / VISUAL CALIBRATION**
Date: 2026-10-02

## Evidence supplied

Five real Futu NiuNiu screenshots showing SSSS on the main price chart and
ADKBY-E in the lower panel:

- CRSP
- PG
- WMT
- AAPL
- ARM

These images are treated as display-layer evidence. They do not by themselves
establish profitability or optimal trading rules.

## 1. Regime color mapping is visually confirmed

Across the five screenshots, the SSSS fast-band color and ADKBY-E background
regime align consistently.

Canonical visual mapping:

- **BLUE = UP / 多头状态**
- **GREEN = DOWN / 空头状态**
- **GRAY = RANGE / 震荡状态**

Examples visible in the supplied screenshots:

- AAPL: sustained rising phase -> SSSS blue band; ADKBY-E background blue.
- WMT: earlier rising phase -> blue; later declining phase -> green in both.
- ARM: earlier blue trend state -> later gray range state in both.
- PG: blue -> green -> gray transitions are visible in both displays.
- CRSP: mixed regime transitions also show corresponding SSSS/ADKBY state blocks.

This visual evidence resolves the intended display semantics of the three
regime colors.

## 2. SSSS and ADKBY-E regime displays are the same intended state family

The screenshots support the source-level result that the two indicators share
the same intended state topology.

SSSS displays the state as the color of the fast price band.

ADKBY-E displays the state as the lower-panel background.

Therefore, after applying the author-confirmed weighted-channel corrections,
these two visual layers should be expected to align bar-for-bar when the
reconstruction is correct.

This becomes a Phase-0 reconstruction check.

## 3. SSSS icon semantics are conditional, not absolute

The main-chart SSSS icons are visibly tied to rail interactions:

- money-bag icon appears at lower-rail events;
- person icon appears at upper-rail events.

However the same icon appears under different background regimes.

Therefore:

**money-bag != unconditional BUY**

and:

**person != unconditional SELL**

The semantic action depends on regime.

Using the shared event topology:

| SSSS rail event | Regime | ADKBY-E semantic label |
|---|---|---|
| lower-rail event | UP / blue | 多 |
| upper-rail event | UP / blue | 平 |
| upper-rail event | DOWN / green | 空 |
| lower-rail event | DOWN / green | 平 |
| lower-rail event | RANGE / gray | 多 |
| upper-rail event | RANGE / gray | 空 |

The screenshots visually support this conditional interpretation.

This table records source/display semantics only.
It is **not** accepted as a validated trading policy.

## 4. ADKBY-E is a semantic decoder for the inner SSSS structure

The images support the following relationship:

SSSS main chart:
- fast XMA25 band;
- blue/green/gray regime color;
- lower/upper event icons;
- slow gray structure;
- additional outer rails.

ADKBY-E lower panel:
- the same intended regime state as background;
- the inner XMA25 geometry normalized around 20k / 50k / 80k;
- explicit 多 / 空 / 平 text for regime-conditioned inner-rail events;
- additional star / warning annotations.

Therefore ADKBY-E is useful as a **display/semantic interpretation of the SSSS
inner XMA25 state/event system**, but it is not a complete replacement for SSSS.

## 5. Outer rails remain SSSS-specific

The screenshots show additional outer dashed rails on the SSSS main chart that
are not represented as equivalent outer rails in ADKBY-E.

Their exact rendered colors should be calibrated separately from their
mathematical identities; visual color alone must not be used to relabel BS/BD.

The mathematical reconstruction remains authoritative for rail identity.

## 6. Research consequences

Phase 0 must now pass both numerical and visual checks.

Required checks:

1. reproduce ABT 2025-01-15 numerical anchor;
2. reproduce corrected 210-weight slow structure;
3. reproduce blue / green / gray regime blocks;
4. verify SSSS and ADKBY-E regime alignment on representative bars;
5. reproduce lower-event / upper-event icon timing;
6. reproduce ADKBY-E 多 / 空 / 平 labels from the same regime-conditioned event
   topology;
7. keep ADKBY star / warning annotations separate from SSSS core events.

No forward-return research should begin until these reconstruction checks pass.

## 7. Important boundary

The screenshots are authoritative evidence of how the formulas render in Futu.

They are not evidence that:
- 多 must be bought;
- 空 must be shorted;
- 平 must be exited;
- money-bag is always bullish;
- person is always bearish.

Those questions belong to later empirical outcome research.
