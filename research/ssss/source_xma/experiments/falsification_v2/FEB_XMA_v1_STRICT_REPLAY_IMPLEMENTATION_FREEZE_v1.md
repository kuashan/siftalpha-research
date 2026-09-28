# FEB_XMA_v1 Strict Replay Implementation Freeze v1

Status: **FROZEN BEFORE CORRECTED STRICT REPLAY**

Date: 2026-09-29

Purpose:
close implementation ambiguity without changing any FEB_XMA_v1 trading
threshold, indicator formula, direction rule, or position target.

This freeze is an engineering correction after
`FEB_XMA_v1_FULLHISTORY_INTEGRITY_AUDIT_v1.md`.

## 1. Strategy identity is unchanged

Normative strategy:
`experiments/multi_asset_2025_02/PROTOCOL_FROZEN_BEFORE_RUN.md`

Do not add:
- cooldown;
- Transition Override;
- HYS2;
- FIVEGZ;
- BEAR counter-regime probe;
- VIX/Breadth/Sector gates;
- v2 synthetic rules;
- shorts.

## 2. Formula readiness gate

A bar is strategy-ready only when the inputs required by the applicable rule
exist from historical observations available at that bar.

Mandatory for any FEB action:
- FastLower / FastMid / FastUpper exist;
- raw ADKBY-E SlowLower / SlowUpper exist;
- regime is one of BULL / BEAR / RANGE / EXPANSION;
- DEA3_RAW and DEA33B_RAW current/prior deltas exist;
- fast-channel width is positive and normalized positions are defined.

The raw ADKBY-E slow weighted input contains `REF(...,20)`.

Therefore when the input source begins on 2020-01-02:
- bars before lag 20 exists are `NOT_READY`;
- `NOT_READY != BEAR` is **not** a valid entry test;
- no trade is permitted merely because regime is missing.

RVOL20 must additionally exist for breakout entry/add.

## 3. Point-in-time XMA

Use the already verified centered/truncated point-in-time Source-XMA behavior.

For each as-of bar t:
- only data through t exists;
- calculate first-observed double XMA(25);
- never backfill prior signal decisions with later revised XMA values.

This implementation has already reproduced the ABT January fast rails.

## 4. Legacy raw slow structure

Preserve FEB historical ADKBY-E raw weighting exactly:

```text
WeightedH =
(20*H + 19*REF(H,1) + ... + 2*REF(H,18)
 + REF(H,19) + REF(H,20)) / 210

WeightedL =
(20*L + 19*REF(L,1) + ... + 2*REF(L,18)
 + REF(L,19) + REF(L,20)) / 210

D90H = EMA(WeightedH,90)
D90L = EMA(WeightedL,90)

SlowUpper = D90H + 2*(D90H-D90L)
SlowLower = D90L - 2*(D90H-D90L)
```

Do not replace with the later canonical corrected 20-observation channel.

## 5. Momentum and normalized position

Unchanged:

```text
DEA3_RAW =
EMA((EMA(C,3)-EMA(C,6)),9)

DEA33B_RAW =
EMA(
  EMA(EMA(C,3)-EMA(C,9),3)
  - EMA(EMA(C,3)-EMA(C,9),9),
  9
)

fast_delta = DEA3_RAW(t)-DEA3_RAW(t-1)
slow_delta = DEA33B_RAW(t)-DEA33B_RAW(t-1)

BOTH_UP   iff fast_delta>0 AND slow_delta>0
BOTH_DOWN iff fast_delta<0 AND slow_delta<0
otherwise CONFLICT

POS(X) =
(X-FastLower)/(FastUpper-FastLower)*100000
```

## 6. WATCH_LONG semantics

A probe signal on session t opens WATCH_LONG through:
- t+1;
- t+2;
- t+3 trading sessions.

The position itself is entered at t+1 open.

Failure to confirm by the end of t+3:
- removes confirmation eligibility;
- does not itself create an exit;
- existing-long rules continue normally.

## 7. Deterministic same-bar priority

This closes a mechanical ambiguity using the archived ABT January decisions.

### Flat

Evaluate:
1. lower-extreme probe;
2. if no probe, independent breakout entry.

This follows the frozen FEB rule ordering.

### Existing long

Priority is:

```text
1. hard EXIT
2. extreme-deceleration REDUCE
3. breakout ADD
4. WATCH_LONG confirmation
```

Why reduce must outrank add:
on 2025-01-28 ABT simultaneously had:
- close > FastUpper;
- BOTH_UP;
- RVOL20 >= 1.50;
- normalized close > 120,000;
- decelerating fast+slow momentum.

The archived January decision is REDUCE, not ADD.

Why exit must outrank reduce:
the FEB protocol defines the exit block as a hard exit if any listed exit
condition is true.

No threshold is changed by this ordering.

## 8. Execution

Unchanged:
- signal at daily close;
- execute next tradable open;
- fractional shares;
- commission $0;
- adverse slippage 5 bps one way;
- long-only.

If a signal occurs on the final dataset bar with no next open, it is not
executed.

Any open terminal position is liquidated for final reporting at the last close
with 5 bps adverse slippage and is recorded separately as
`TERMINAL_LIQUIDATION`.

## 9. Historical FEB position-target accounting

To reproduce the January/FEB research convention rather than silently replace
it with a modern portfolio rebalance:

When target increases from old_target to new_target:
```text
buy notional =
(new_target-old_target) * initial_sleeve_capital
```

When target decreases but remains >0:
```text
sell fraction of current shares =
(old_target-new_target) / old_target
```

When target becomes 0:
sell all current shares.

For the January discovery this convention exactly explains the archived
$3,000 / $4,000 / $3,000 acquisition tranches for 30% -> 70% -> 100%.

This is a historical research replay convention, not a production portfolio
leverage rule.

Report both:
- average lifecycle target exposure;
- average actual marked gross exposure.

## 10. Metrics

Per symbol:
- initial/final capital;
- cumulative return;
- CAGR;
- max drawdown;
- annualized Sharpe from daily equity returns (252-day scaling, sample standard deviation);
- executed action count;
- action-type counts;
- average target exposure;
- average actual gross exposure;
- annual returns.

Aggregate equal-capital sleeves:
- arithmetic sum/mean of the 39 independently funded sleeves;
- cumulative return;
- CAGR;
- max drawdown;
- annualized Sharpe;
- mean/median sleeve return;
- positive sleeve count;
- best/worst sleeve;
- annual returns.

SPY:
report passive buy-and-hold comparison using the existing benchmark dataset
when directly comparable.

## 11. Shared $10,000 portfolio gate

FEB_XMA_v1 contains no cross-symbol ranking or capital-priority rule.

If simultaneous independent targets exceed a shared 100% gross cap, choosing
which symbols receive capital requires an additional portfolio rule.

Therefore:

```text
SHARED_CAPITAL_REPLAY =
BLOCKED_BY_PORTFOLIO_ALLOCATION_RULE
```

Do not invent a ranking rule in this replay.

Complete the independent $10,000 sleeves first.

## 12. Closure condition

The corrected strict replay can close when:
1. ABT reproduction remains PASS;
2. all 39 symbols complete;
3. requested per-symbol metrics are persisted;
4. daily per-symbol/aggregate equity is sufficient to recompute Sharpe/DD;
5. no FEB rule/threshold changes occur after viewing results;
6. legacy replay remains preserved separately.
