# FIVEGZ5SE Candidate Evaluation

Status: CANDIDATE_FEATURE / NOT PROMOTED  
Added: 2026-09-28  
Source: user-supplied FIVEGZ5SE.txt  
Source SHA-256: `61bc9f7cad7a2efb6374a187c680fa75789b2468824885e5127c5f70333400c9`  
Source size: 93,201 bytes

## Research boundary

The source's comments and display labels are **not accepted as semantic truth**.

In particular, labels containing words such as:
- 清仓
- 抄底
- 底部
- 主升
- 逃顶

are treated only as author-written annotations.

Our evaluation uses the actual boolean conditions.

FIVEGZ5SE is not merged into the Source-XMA baseline. It is logged as a candidate auxiliary state engine.

## What the formula actually contains

Five main dimensions:
1. trend
2. capital/volume
3. momentum
4. acceleration
5. candlestick/anomaly

It also contains:
- volatility filters
- relative-volume rules
- bias/overheat filters
- dynamic high-volume / suspected-distribution rules
- range-mode logic
- multi-stage state-transition annotations

This makes it potentially useful as a **context decomposition layer** around XMA.

## Important semantic corrections

### 1. "清仓" is really triple-bear confirmation

```text
当下清仓 = 趋势空 AND 资金空 AND 动能空
```

This is better interpreted as:
`TRIPLE_BEAR_CONFIRMATION`

It does not by itself prove that a full liquidation is optimal.

It is also repeated later as `补充_三空共振`.

### 2. "底部双重背离" is not a mathematical divergence

```text
补充_底部双重背离 =
  (趋势浅绿 OR 趋势灰)
  AND (资金浅红 OR 资金多)
  AND (动能浅红 OR 动能多)
```

There is:
- no price lower-low test,
- no oscillator higher-low comparison,
- no XMA lower-extreme condition.

A better name is:
`WEAK_TREND_INTERNAL_RECOVERY`

### 3. "多维度同步拐头" does not count dimensions

```text
COUNT(趋势浅红 OR 资金浅红 OR 动能浅红, 2) >= 2
```

Because the OR expression is evaluated before COUNT, this means:
- both of the last two bars had at least one light-red condition,

not:
- at least two dimensions turned up.

The annotation overstates what the code measures.

### 4. "阶梯减仓预警" has the same dimension-count issue

```text
COUNT(资金浅绿 OR 动能浅绿 OR 加速浅绿, 3) >= 3
```

This means all of the last three bars had at least one weak dimension.

It does not prove that three different dimensions weakened sequentially.

### 5. Momentum continuous confirmation is disabled

```text
MOM_CONTINUOUS_DAYS := 0
连续向上 := BARSLASTCOUNT(动能向上) >= 0
连续向下 := BARSLASTCOUNT(动能向下) >= 0
```

Both continuity conditions are always true once evaluated.

Therefore the current momentum state depends on:
- trend background
- VAR26 slope vs dynamic threshold

but not on a real minimum continuity requirement.

### 6. Several US filters are intentionally broad

For `SCTYPE=1`:
- volatility activity threshold = 0.35 on ATR14 / ATR-MA50
- relative-volume healthy range = 0.4 to 12

These behave more like broad sanity gates than strong discriminators in many liquid US equities.

## Reproduction assumption

The post-hoc ABT reproduction uses common TongDaXin-style functions.

For `FORCAST(X,6)`, the implementation follows the public MyTT convention:
rolling linear regression over the latest 6 values, evaluated at the current endpoint.

This is adequate for candidate research but selected Futu dates should still be spot-checked before claiming exact engine identity.

## ABT January 2025 post-hoc result

This test is performed **after** the original Source-XMA January decisions were frozen.

It does not alter:
- the January decisions,
- the January paper trades,
- the reported +13.45% result.

### Low/reversal area

2025-01-15:
- XMA system: PROBE_LONG
- FIVEGZ5SE: trend SHORT, momentum SHORT, acceleration SHORT
- no bottom-dual or sync-turn candidate fired

2025-01-16:
- XMA system: ENTER_LONG confirmation
- FIVEGZ5SE internal states already flipped to light-long / acceleration-long
- but its composite risk layer emitted RISK_REDUCE_STATE

This is a clear negative example:
the formula's risk controller can become bearish/cautious exactly when the XMA reversal is confirming.

Therefore its "clear/bottom" wording must not control our trade.

### Breakout area

2025-01-21:
- XMA system: ADD_LONG
- FIVEGZ5SE:
  - trend LONG
  - capital LONG
  - momentum LONG
  - acceleration LONG
  - anomaly LONG
  - five-dimension extreme-main confirmation TRUE
  - no comprehensive risk

This is a **strong positive auxiliary confirmation**.

It independently supports our earlier conclusion that the source SSSS/ADKBY upper-band short signal should be overridden during a genuine breakout.

2025-01-22 / 2025-01-23:
- FIVEGZ5SE core open-state turns on
- this is later than our XMA breakout recognition

Therefore it is more useful as:
- confirmation / position-confidence,
than as the primary timing engine.

### Exit area

2025-01-24:
- FIVEGZ5SE issues a reduce-state after capital falls from LONG to LIGHT_LONG
- ABT still continues higher into Jan-27

So mandatory use of this reduce signal would be early.

2025-01-30 / Jan-31:
- FIVEGZ5SE remains mostly LIGHT_LONG and does not produce a full bearish confirmation
- our XMA/momentum process already chose EXIT_LONG

Therefore the triple-bear "清仓" condition is **too late to be our primary exit rule** in this case.

## Candidate value

### HELPFUL
- five-dimension agreement as breakout / continuation confidence
- capital-state deterioration as an early caution feature
- anomaly/candlestick state as contextual evidence
- dynamic relative-volume information
- internal transition path (strong -> light -> gray -> weak)

### NEUTRAL / NEEDS MORE DATA
- range-mode low/high signals
- suspected-distribution logic
- bias/overheat layer

### HARMFUL IF USED LITERALLY
- treating "清仓" as mandatory full liquidation semantics
- treating "抄底"/"底部" names as proof of a bottom
- letting the composite risk layer veto the Jan-16 XMA confirmation
- treating the Jan-24 reduce-state as a mandatory large reduction

## Decision

Keep FIVEGZ5SE as **CANDIDATE_STATE_ENGINE**.

Do not import its displayed instructions into the trading state machine.

For future multi-asset replay, log the following raw feature groups:
- TREND_STATE
- CAPITAL_STATE
- MOMENTUM_STATE
- ACCEL_STATE
- ANOMALY_STATE
- COMPOSITE_RISK_STATE
- FIVE_DIMENSION_ALIGNMENT
- INTERNAL_DETERIORATION

Compare:
```text
XMA baseline
vs XMA + HYS2
vs XMA + FIVEGZ5SE raw states
vs XMA + HYS2 + FIVEGZ5SE raw states
```

Each add-on can be HELPFUL, NEUTRAL, or HARMFUL.

No retroactive rewrite of earlier decisions is allowed.
