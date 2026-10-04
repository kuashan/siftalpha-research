# SLTD A-share 50 Integrated Risk v1 — Closeout

Status: **CLOSED / REJECTED_NOT_ADMITTED**

Branch:
`research/sltd-ashare50-integrated-risk-v1`

Data audit:
- `A_SHARE_50_DATA_AUDIT_V3 = PASS`
- BaoStock qfq
- 50/50 symbols
- 35 DEVELOPMENT / 15 FRESH_OOS
- formal ST rows: 0 for all 50

Stage A archive:
`b793688479095bf737961b64b3f81194cf042ee7`

Stage B archive:
`7ef0b06b4e14ac4a26ffbb0d72212015b132aaec`

Fresh15 performance read: **NO**

Fresh OOS consumed: **NO**

## 1. Architecture tested

A:
`SLTD_12_RULES_ONLY`

B:
`SLTD_V7_12_RULES_PLUS_C2`

C:
`SLTD_V7_12_RULES_PLUS_C2_PLUS_SEVERE_RISK`

Context:
- BUY_AND_HOLD
- SMA200

The 12-rule taxonomy was unchanged.
C2 was unchanged.
The Severe Risk layer used only A-share DEVELOPMENT learning.

No US-fitted state weights were imported.

## 2. Stage A result — Severe Risk itself is real

Stage A:
`PROMOTED_TO_INTEGRATED_HOLDOUT`

A-share DEVELOPMENT:
- Discovery state keys: 290
- Discovery support-pass: 191
- temporally stable negative states: 28
- negative components: EVENT / INNER / REGIME / SLOW
- Severe threshold: -1.32665

Temporal Severe Risk:
- observations: 2,182
- symbol breadth: 35 / 35
- 10d return excess: -0.013%
- 20d return excess: -0.317%
- 10d MAE safety lift: -0.226%
- 20d MAE safety lift: -0.249%
- 10d loss-probability lift: +3.459%
- 20d loss-probability lift: +0.618%
- 10d forward-MaxDD difference: -0.390%
- 20d forward-MaxDD difference: -0.525%

All 10 preregistered Stage-A gates passed.

Interpretation:
the A-share Severe Risk state layer contains genuine adverse-forward-risk information.

## 3. Stage B holdout

Holdout:
- DEVELOPMENT 35 only
- 2025-01-02 .. 2026-09-30
- primary A-share costs: BUY 5 bps / SELL 10 bps

### Aggregate results

A — 12 rules only:
- Total Return: -0.27%
- CAGR: -0.16%
- MaxDD: -9.73%
- Calmar: -0.016
- mean exposure: 61.92%

B — 12 rules + C2:
- Total Return: approximately 0.00%
- CAGR: approximately 0.00%
- MaxDD: -8.36%
- Calmar: approximately 0.000
- mean exposure: 53.63%

C — 12 rules + C2 + Severe Risk:
- Total Return: +0.51%
- CAGR: +0.29%
- MaxDD: -7.51%
- Calmar: 0.039
- mean exposure: 50.42%

Buy & Hold:
- Total Return: +1.98%
- CAGR: +1.13%
- MaxDD: -13.32%
- Calmar: 0.085
- exposure: 100%

SMA200:
- Total Return: -3.65%
- CAGR: -2.12%
- MaxDD: -7.92%
- Calmar: -0.267

## 4. Attribution

### C2 contribution: B - A

- Return delta: +0.27 percentage points
- CAGR delta: +0.15 pp
- MaxDD improvement: +1.37 pp
- Calmar delta: +0.016
- exposure delta: -8.29 pp
- better MaxDD: 13 / 35
- better Calmar: 9 / 35

C2 helped the aggregate portfolio, but the improvement was not broad across stocks.

### Severe Risk incremental contribution: C - B

- Return delta: +0.51 pp
- CAGR delta: +0.29 pp
- MaxDD improvement: +0.85 pp
- Calmar delta: +0.039
- exposure delta: -3.21 pp
- median per-stock return delta: 0.00 pp
- better MaxDD: 4 / 35
- better Calmar: 5 / 35
- Severe Risk full exits: 8
- symbols with Severe Risk full exits: 6 / 35

Severe Risk improved the aggregate curve but affected too few symbols and lacked breadth.

### Combined contribution: C - A

- Return delta: +0.78 pp
- CAGR delta: +0.45 pp
- MaxDD improvement: +2.22 pp
- Calmar delta: +0.055
- exposure delta: -11.49 pp
- better MaxDD: 16 / 35
- better Calmar: 13 / 35

## 5. Gate result

PASS:
- aggregate Calmar improves
- median per-stock return delta >= -1 pp
- worst per-stock MaxDD no worse
- sensitivity-cost Calmar > baseline
- exposure retention >= 90%

FAIL:
- C vs B aggregate MaxDD improvement >= 2 pp
  - actual: +0.85 pp
- return-retention gate
  - B return was slightly negative / approximately zero, so the preregistered ratio is not economically meaningful;
  - it is nevertheless recorded as FAIL under the frozen implementation.
- >=60% symbols improve MaxDD
  - actual: 4 / 35 for C vs B
- >=50% symbols improve Calmar
  - actual: 5 / 35
- Severe Risk full exits on >=10 symbols
  - actual: 6 / 35

Even if the return-retention gate were treated as not-applicable because B was approximately zero,
the candidate would still fail multiple independent breadth / effect-size gates.

Decision:
`SLTD_ASHARE50_INTEGRATED_RISK_V1_STAGE_B = REJECTED_NOT_ADMITTED`

Therefore:
`SLTD_ASHARE50_INTEGRATED_RISK_V1 = CLOSED`

## 6. Correct interpretation

The study does **not** show that Severe Risk is useless.

It shows:

1. Severe Risk is a real A-share adverse-state descriptor.
2. C2 improves the aggregate A-share holdout modestly.
3. Severe Risk adds another modest aggregate improvement beyond C2.
4. But the added benefit is concentrated in too few stocks and is not broad enough to justify
   admission as a general rule.
5. Buy & Hold still produced the highest aggregate return and higher Calmar than the candidate in
   this specific 2025-2026Q3 holdout.
6. The combined system improves drawdown relative to the 12-rule core, but does so partly by
   reducing exposure, and not with sufficient breadth.

## 7. Frozen status

`A_SHARE_50_DATA_AUDIT_V3 = PASS`

`SLTD_ASHARE50_INTEGRATED_RISK_V1_STAGE_A = PROMOTED_TO_INTEGRATED_HOLDOUT`

`SLTD_ASHARE50_INTEGRATED_RISK_V1_STAGE_B = REJECTED_NOT_ADMITTED`

`SLTD_ASHARE50_INTEGRATED_RISK_V1 = CLOSED`

Fresh15 remains untouched.

No threshold retuning, percentile change, state pruning, or symbol-specific rescue is allowed inside v1.
