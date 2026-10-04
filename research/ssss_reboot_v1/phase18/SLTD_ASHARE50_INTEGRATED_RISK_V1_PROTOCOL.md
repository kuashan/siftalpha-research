# SLTD A-share 50 Integrated Risk v1 — Protocol

Status: **PRE-REGISTERED / NO STRATEGY RESULT YET**

Branch:
`research/sltd-ashare50-integrated-risk-v1`

Parent research closeout:
`research/sltd-rank-long-hold-allocation-v1@36df566a67dc174a8d24d857ee19c0bd30c8af78`

Frozen A-share universe:
`A_SHARE_50_UNIVERSE_V1.json`

Frozen data/execution policy:
`A_SHARE_50_DATA_EXECUTION_POLICY_V1.md`

## 1. Purpose

This branch deliberately stops using US equities as the primary test market.

The integrated architecture contains three explicit layers:

1. **SLTD frozen 12-rule core**
2. **C2 hard-exit mechanism**
3. **A-share-learned SLTD risk-state layer**

The first two layers are imported unchanged from the frozen V7 candidate semantics.

The third layer imports only the **research method** from the recent Score / Risk work.
It does NOT import US-fitted state weights, thresholds, or the 82 US stable-state utilities.

## 2. Frozen 12-rule source

Source candidate:
- branch: `candidate/sltd-v7-12rules-position-v1`
- source commit declared by integration engine:
  `5f9ea4d8fa434b54afdbf32a1cb21ef2f3cb4042`

Frozen active taxonomy:

BUY:
1. `BUY_BLUE_21P_LOWER`
2. `BUY_GRAY_4_10_LIGHT_SUPPORT`
3. `BLUE_11_20_LOWER_WICK_ONLY`
4. `NEW_V5_C_GRAY_4_10_LOWER_WICK_ONLY`

HOLD:
5. `CONT_BLUE_11_20_UPPER`
6. `CONT_BLUE_4_10_UPPER`
7. `CONT_RECENT_GRAY_BLUE_UPPER`
8. `NEW_V5_B_BLUE_21P_UPPER_CLOSE_ABOVE`

WAIT:
9. `AVOID_GREEN_11_20_LOWER`
10. `GREEN_11_20_LOWER_CLOSE_BELOW`

SELL:
11. `GREEN_4_10_UPPER`
12. `NEW_V5_E_GREEN_11_20_LIGHT_RESIST`

Frozen position semantics:
- first BUY from flat -> 25%
- later executed BUY -> +25 percentage points, cap 100%
- ordinary SELL -> reduce 25% of current remaining position
- WAIT while long -> HOLD
- WAIT while flat -> NO ENTRY
- same-bar conflicting action classes -> NO_CHANGE_MIXED

No Phase18 research may change these 12 rules.

## 3. Frozen C2 layer

ID:
`C2_FULL_CANDLE_BELOW_SLOW_BAND`

Semantics:
- an actually executed ordinary SELL arms C2 risk state;
- an actually executed BUY resets C2 to NORMAL;
- while ARMED, if:
  - SLTD state = GREEN
  - whole candle is below slow band:
    `High < GZB4`
- then at the next fillable bar open liquidate the entire remaining position.

A-share locked-limit / suspension rules from the data policy apply.
C2 itself is not optimized in Phase18.

## 4. New A-share risk-state layer

The new risk layer re-learns the recent pure-SLTD risk-adjusted state methodology on A shares only.

Allowed imported methodology:
- FIRST_OBSERVED / XMA causal states
- F1..F8 state taxonomy
- horizons 5 / 10 / 20
- Return excess
- Up-probability lift
- MFE excess
- MAE safety lift
- Risk/Reward log lift
- robust Discovery-only normalization
- REGIME / INNER / SLOW / EVENT / TRANSITION component collapsing

Forbidden:
- US state utilities
- US stable-state IDs as live filters
- US thresholds
- US 82-state weights
- Score Momentum
- v4 favorable-probability calibration
- Chan/缠论
- Chandelier

## 5. A-share split

Frozen universe = 50 stocks.

DEVELOPMENT:
- 35 stocks

FRESH_OOS:
- 15 stocks
- no state-performance or strategy-performance read before development gates pass

Development time segmentation:

Discovery:
- 2018-01-02 .. 2022-12-30

Temporal stability:
- 2023-01-03 .. 2024-12-31

Development holdout:
- 2025-01-02 .. 2026-09-30

No forward label may cross its segment boundary.

## 6. A-share state utility

For each state and each horizon 5/10/20, relative to per-symbol Discovery unconditional baseline:

1. Return excess
2. Up-probability lift
3. MFE excess
4. MAE safety lift
5. RR log lift

Robust-normalize each dimension with Discovery-only scale.
Collapse horizons by median.
State utility = median of available normalized dimensions.

Support:
- dense F1-F5: n >= 250 and symbols >= 15
- event F6-F8: n >= 50 and symbols >= 8

Temporal-negative-stable state requires:
- Discovery utility < 0
- Temporal utility < 0
- at least 3/5 raw dimensions remain adverse
- 10-bar return-excess remains < 0
- Temporal support >= 50% of Discovery support floor

## 7. Bar-level risk score

Use the same non-redundant component construction:

- REGIME: F2 overrides F1
- INNER: F3
- SLOW: median F4/F5
- EVENT: F7 overrides corresponding F6; median independent events
- TRANSITION: median F8

Only A-share temporally-negative-stable states contribute to the risk score.

`RISK_LEVEL_t = median(non-zero matched negative component utilities)`

If no stable negative state matches:
`RISK_LEVEL_t = 0`

No positive state is allowed to cancel a negative state in this risk-only layer.

## 8. Severe-risk threshold

Learn on Discovery DEVELOPMENT bars only.

Take all bars where `RISK_LEVEL < 0`.

Frozen threshold:

`SEVERE_THRESHOLD = 25th percentile of negative Discovery RISK_LEVEL`

Thus `SEVERE_RISK` means:
- `RISK_LEVEL <= SEVERE_THRESHOLD`

The percentile is fixed before any Temporal / Holdout result.

## 9. Stage A — risk validation only

Stage A does not change positions.

Required Discovery / Temporal diagnostics for SEVERE_RISK:
- event count
- symbol breadth
- 5/10/20 return excess vs same-symbol unconditional baseline
- 5/10/20 MAE safety lift
- 5/10/20 MFE excess
- loss probability lift
- median forward max drawdown
- tail loss p10

Stage A passes only if Temporal satisfies all:

1. >= 500 Severe Risk observations
2. >= 20 DEVELOPMENT symbols represented
3. 10-bar return excess < 0
4. 20-bar return excess < 0
5. 10-bar MAE safety lift < 0
6. 20-bar MAE safety lift < 0
7. loss probability lift > 0 at 10 bars
8. loss probability lift > 0 at 20 bars
9. Severe Risk median forward max drawdown is worse than unconditional at 10 bars
10. Severe Risk median forward max drawdown is worse than unconditional at 20 bars

Pass:
`PROMOTED_TO_INTEGRATED_HOLDOUT`

Otherwise:
`REJECTED_NOT_ADMITTED`

## 10. Stage B — integrated architecture

Stage B is allowed only after Stage A passes.

Baseline:
`V7_12_RULES_PLUS_C2`

Candidate:
`V7_12_RULES_PLUS_C2_PLUS_ASHARE_SEVERE_RISK`

The new layer is deliberately **armed / position-aware**, not always active.

Candidate semantics:

- 12-rule BUY/HOLD/WAIT/SELL actions remain unchanged.
- ordinary SELL still arms C2.
- BUY still resets ARMED to NORMAL.
- while position > 0 and C2 is ARMED:
  - if C2 hard condition occurs -> full exit, as baseline
  - else if A-share `SEVERE_RISK` occurs -> full exit
- Severe Risk never creates a sell from NORMAL state.
- Severe Risk never changes entry sizing.
- Severe Risk never shorts.
- Severe Risk full exit and C2 full exit are mutually exclusive on a bar; C2 has priority for attribution.

All execution:
- close t confirmation
- next fillable open
- A-share locked-limit / suspension handling applies

## 11. Stage B development holdout

Only:
- DEVELOPMENT 35 stocks
- 2025-01-02 .. 2026-09-30

No Stage-B rule or threshold may be changed after this holdout is inspected.

Comparators:
1. 12 rules without C2 — attribution only
2. 12 rules + C2 — formal baseline
3. 12 rules + C2 + Severe Risk — candidate
4. Buy & Hold — context
5. SMA200 — context

Primary A-share friction:
- buy 5 bps
- sell 15 bps before 2023-08-28
- sell 10 bps on/after 2023-08-28

Sensitivity:
- double non-tax execution friction

## 12. Stage B admission gates

Candidate vs `12 rules + C2`, all required:

1. aggregate MaxDD improves by >= 2.0 percentage points
2. aggregate Calmar improves
3. aggregate Total Return retention >= 95%
4. median per-stock Total Return delta >= -1.0 percentage point
5. >= 60% of DEVELOPMENT symbols have better MaxDD
6. >= 50% of DEVELOPMENT symbols have better Calmar
7. worst per-stock MaxDD improves or is unchanged
8. sensitivity-cost aggregate Calmar still > baseline
9. Severe Risk full exits occur on >= 10 symbols
10. candidate mean exposure is >= 90% of baseline mean exposure

Pass:
`PROMOTED_TO_FRESH15`

Otherwise:
`REJECTED_NOT_ADMITTED`

This explicitly prevents "reducing drawdown by simply staying out of the A-share market."

## 13. Fresh15

Only if Stage B passes.

Fresh15 architecture and thresholds are completely frozen.
No retraining on Fresh15.
No symbol replacement after Fresh strategy outcomes are visible.

Final Fresh gates must be frozen in a separate amendment before running Fresh results.

## 14. Governance

This branch is a new integrated research line.

It does not rewrite:
- V6 rollback baseline
- frozen V7 12-rule source
- existing C2 definition
- previous US research conclusions

The A-share result may show market-specific behavior and is allowed to disagree with US evidence.

`SLTD_ASHARE50_INTEGRATED_RISK_V1_PROTOCOL = FROZEN`
