# SLTD A-share 50 Integrated Risk v1 — Amendment A

Status: **FROZEN BEFORE STAGE A RESULTS**

Parent:
`SLTD_ASHARE50_INTEGRATED_RISK_V1_PROTOCOL.md`

## 1. Loss probability

For horizon h:

`LOSS_PROB_h = P(RET_h < 0)`

Per-state / Severe Risk lift is computed relative to the same-symbol unconditional baseline
inside the same research segment.

Positive loss-probability lift = worse.

## 2. Forward maximum drawdown

Outcome entry:
- next bar open after signal close

Initialize running peak at the entry open.

For each future bar k=1..h:
- update running peak with that bar High
- drawdown candidate = Low_k / running_peak - 1

`FORWARD_MAX_DD_h = min(drawdown_candidate over k=1..h)`

More-negative = worse.

This is an adverse-path metric and is distinct from MAE:
- MAE measures the worst move below the entry price;
- FORWARD_MAX_DD measures the worst peak-to-subsequent-trough giveback during the horizon.

## 3. Cross-symbol aggregation

To prevent large/volatile symbols from dominating pooled event counts:

For each Severe Risk metric:
1. calculate the Severe Risk statistic within each symbol;
2. calculate that symbol's unconditional statistic in the same segment;
3. form symbol-level lift / difference;
4. report the cross-symbol median lift as the primary effect.

Pooled observation counts are support diagnostics only.

## 4. Segment boundary

For any h <= 20:
- the h-bar outcome must end on or before the segment end date.
- no Discovery label can enter Temporal;
- no Temporal label can enter Development Holdout.

## 5. Temporal support

Negative stable state Temporal minimum:

Dense F1-F5:
- n >= 125
- symbols >= 8

Event F6-F8:
- n >= 25
- symbols >= 4

This is approximately half of the preregistered Discovery support floor and is now numerically fixed.

## 6. Freeze

`SLTD_ASHARE50_INTEGRATED_RISK_V1_AMENDMENT_A = FROZEN`
