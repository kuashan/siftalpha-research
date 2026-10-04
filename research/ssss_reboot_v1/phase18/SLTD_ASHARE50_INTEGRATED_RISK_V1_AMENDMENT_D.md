# SLTD A-share 50 Integrated Risk v1 — Amendment D

Status: **FROZEN BEFORE INTEGRATED HOLDOUT RESULTS**

Purpose:
Freeze the strategy comparison requested before entering the integrated
`12 rules + C2 + Severe Risk` holdout.

## 1. Comparator set

The 2025-01-02 .. 2026-09-30 DEVELOPMENT holdout must report all of:

### A. SLTD_12_RULES_ONLY
Frozen 12-rule taxonomy and frozen position sizing:
- first BUY from flat -> 25%
- later BUY -> +25 percentage points, cap 100%
- ordinary SELL -> reduce 25% of remaining position
- WAIT while long -> HOLD
- WAIT while flat -> NO ENTRY
- conflicting action classes -> NO_CHANGE_MIXED

C2 is disabled.
Severe Risk is disabled.

This isolates the 12-rule core.

### B. SLTD_V7_12_RULES_PLUS_C2
Frozen current SLTD V7 execution baseline:
- same 12 rules
- same position sizing
- frozen C2 hard-exit mechanism enabled
- Severe Risk disabled

This is the **formal SLTD baseline** for judging the new Severe Risk layer.

### C. SLTD_V7_12_RULES_PLUS_C2_PLUS_SEVERE_RISK
Candidate:
- same frozen 12 rules
- same frozen C2
- A-share-learned Severe Risk layer
- Severe Risk can full-exit only while C2 risk state is ARMED
- C2 has attribution priority when both conditions occur on the same signal bar

No other execution rule may differ from B.

### Context only
- BUY_AND_HOLD
- SMA200

## 2. Required pairwise attribution

Report:

1. B - A:
   `C2 contribution`

2. C - B:
   `Severe Risk incremental contribution`

3. C - A:
   `combined exit-stack contribution`

For each pair report:
- Total Return delta
- CAGR delta
- MaxDD delta
- Calmar delta
- mean exposure delta
- median per-symbol return delta
- symbols with better MaxDD
- symbols with better Calmar

This prevents a good/bad combined result from hiding which layer caused it.

## 3. Formal admission baseline

Candidate C is admitted or rejected against **B**, not against A.

Reason:
C2 already belongs to the frozen current SLTD V7 execution policy.
The Phase18 research question is whether Severe Risk adds value beyond the existing SLTD baseline.

A remains mandatory for attribution.

## 4. Terminology

Repository audit found no separate strategy named `STLD`.
The only exact `STLD` object in the repository is the US stock ticker
`STLD` (Steel Dynamics) data file.

Therefore this amendment interprets the requested "STLD comparison" as comparison against the
existing frozen **SLTD** system.

If a distinct strategy named STLD is introduced later, it must be separately identified and cannot
silently replace these frozen comparators.

## 5. Freeze

`SLTD_ASHARE50_INTEGRATED_RISK_V1_AMENDMENT_D = FROZEN`
