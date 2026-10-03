# SLTD V7 Exit Stack 79-Stock Study v1

Status: ROUND1_COMPLETE_DIRECT_ADMISSION_REJECTED  
Branch: `research/sltd-v7-exit-stack-v1`  
Base production HEAD: `e05919539328407cb7a67f8a995f6b90f0d4156b`  
Study HEAD: `22fdd4c5c07a013055d37def25ed3ba199747015`  
Run 1: `37113782770` — PASS  
Run 2: `37114015745` — PASS  
Population: 79 stock snapshots  
Policy start: existing SLTD `2020-01-02`  
Execution: completed-bar confirmation -> next-bar open  
Friction: 5 bps  
Production activation: NO

## 1. Deterministic UI / formula fixes retained

- Strategy tab label changed from `12条策略` to `SLTD`.
- Existing lower outer rail `BD` was already calculated in the SLTD ledger:
  `BD = VL60 - 2.8 * (VH60 - VL60)`.
- BD is now carried into chart payload and displayed as the lower outer rail.
- BS remains the upper outer rail.
- Shunshi long solid line width remains 1.

## 2. Exit layers tested

### Existing baseline
Frozen SLTD V7 entries and exits:
- BUY rules unchanged.
- Ordinary SLTD SELL: 25% of current position.
- C2 full exit unchanged.

### chan.py partial sell layer
Pinned upstream:
`Vespa314/chan.py@429d6ed3043e27c93a003ba2b10e70a05575e1f5`

Incremental `trigger_load` was used bar by bar.

Tested:
- L0 only vs L1 only vs L0+L1
- current-frame ANY signals vs SURE-only signals
- flat 25% sell vs graded sell:
  - S1 / S1P: 50% current position
  - S2 / S2S / S3A / S3B: 25% current position

Multiple Chan sell classes on one bar use the strongest fraction only; they do not stack on the same bar.

### Chandelier final full exit
Initial direct candidate:
- lookback: 22
- multiplier: 3
- long line: rolling highest high minus 3 * Wilder ATR
- stop ratchets upward while a position is open
- close below stop -> next bar open full exit

## 3. Baseline result

Across 79 stocks:

- mean total return: +198.58%
- median total return: +68.61%
- mean CAGR: +11.10%
- median CAGR: +8.06%
- mean max drawdown: -40.11%
- median max drawdown: -37.50%
- worst max drawdown: -74.99%
- positive-return symbols: 68 / 79
- mean exposure: 30.76%
- mean completed holding duration: 445.63 bars
- mean exit giveback: 14.80%

Executions:
- BUY: 1,131
- SLTD ordinary SELL: 364
- C2 full exit: 179

## 4. Chandelier 22/3 direct result

### Chandelier only
- mean total return: +4.42%
- median total return: -0.15%
- mean CAGR: +0.48%
- mean max drawdown: -9.29%
- positive-return symbols: 39 / 79
- mean exposure: 1.92%
- mean holding duration: 7.47 bars
- Chandelier full exits: 2,678

Vs baseline:
- lower drawdown: 79 / 79
- higher return: only 8 / 79
- mean return delta: -194.16 percentage points

Interpretation:
The direct 22/3 implementation dominates the strategy and repeatedly ejects new SLTD positions. It solves drawdown by almost eliminating exposure, not by improving sell timing.

Decision:
`CHANDELIER_22_3_DIRECT = REJECTED_NOT_ADMITTED`

It requires a position-aware/armed design before further consideration, e.g. use highest-high-since-entry, profit activation, or activation after a top/de-risk signal.

## 5. chan.py only results

### L0 ANY, flat 25%
- mean return: +40.29%
- median return: +24.06%
- mean max DD: -28.71%
- median max DD: -26.83%
- positive: 66 / 79
- Chan sells: 9,613
- higher return vs baseline: 11 / 79
- lower DD: 73 / 79

### L0 ANY, graded
- mean return: +38.22%
- median return: +22.46%
- mean max DD: -28.15%
- Chan sells: 9,552

### L1 ANY, graded
This was the best return-retention among the tested Chan-only variants:
- mean return: +83.33%
- median return: +44.67%
- mean CAGR: +6.36%
- median CAGR: +5.63%
- mean max DD: -29.82%
- median max DD: -25.18%
- positive: 65 / 79
- mean exposure: 16.36%
- Chan sells: 6,877
- higher return vs baseline: 12 / 79
- lower DD: 63 / 79
- both return and DD improved: 11 / 79

### L0+L1 ANY, graded
- mean return: +25.30%
- median return: +15.41%
- mean max DD: -23.91%
- Chan sells: 11,873
- higher return vs baseline: 9 / 79

### L0+L1 SURE only, graded
- mean return: +40.97%
- median return: +26.10%
- mean max DD: -28.54%
- Chan sells: 3,941
- higher return vs baseline: 11 / 79

Interpretation:
All direct Chan variants reduce drawdown, but the current sell frequency is too high and materially cuts long-run return. Current-frame virtual signals are especially noisy. L1 is materially better than L0/all-level use, but still too aggressive in the tested sizing.

Decision:
`CHAN_DIRECT_ALL_SELL_TYPES = REJECTED_NOT_ADMITTED`

## 6. Combined Chan + Chandelier

Representative L1 ANY graded + Chandelier:
- mean return: +3.16%
- mean max DD: -7.93%
- Chandelier full exits: 2,678
- Chan sells: 2,117

All-level ANY graded + Chandelier:
- mean return: +1.74%
- mean max DD: -7.21%
- Chandelier full exits: 2,678

Chandelier dominates the combined stack, so this round does not support direct production admission.

## 7. What the data actually says

1. The original problem is real: baseline drawdown and profit giveback are large, and SLTD ordinary sells are sparse.
2. More sell signals by itself is not the solution.
3. L0/current-frame Chan signals are far too frequent for direct position reduction.
4. L1 Chan signals are the most promising structural exit source tested, but sizing/frequency must be reduced.
5. Default Chandelier 22/3 cannot be attached blindly to each SLTD position.
6. A protective full-exit layer needs to be armed under a state/position condition rather than active immediately after every entry.

## 8. Next bounded study

Do not change SLTD BUY rules.

Only investigate:
- L1 SURE-only or selected high-value Chan sell classes;
- smaller partial reductions than the current 50%/25% mapping;
- position-aware Chandelier:
  - highest-high-since-entry, and/or
  - activate only after profit threshold / Chan top signal / first partial sell;
- compare against baseline on the same 79 stocks.

No new rule is admitted until it improves the return/drawdown tradeoff broadly rather than merely suppressing market exposure.
