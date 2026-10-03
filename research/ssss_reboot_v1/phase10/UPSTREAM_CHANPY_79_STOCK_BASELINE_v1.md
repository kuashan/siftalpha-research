# Upstream chan.py 79-Stock Baseline v1

Status: BASELINE_RUN_COMPLETE_NO_PRODUCTION_CHANGE  
Branch: `feature/chan-standalone-v2`  
Our workflow HEAD: `e2a4994a915bda81dac0b89f3f6a3e130f7e6940`  
CI Run: `37110485784` — PASS  
Upstream repository: `Vespa314/chan.py`  
Pinned upstream commit: `429d6ed3043e27c93a003ba2b10e70a05575e1f5`  
Mode: upstream default configuration, single daily level, `trigger_load`, one bar at a time  
Population: same 79 stock snapshots used by the current Chan diagnostics  
Production strategy changed: NO

## 1. Aggregate structure

Across 79 stocks / 330,566 daily bars:

- Bi: 17,810
- Confirmed Bi: 17,777
- Segments: 2,677
- Confirmed segments: 2,408
- Virtual / not-yet-sure segments at the final frame: 269
- Zhongshu: 2,101
- Unique Bi-level BSP points: 4,306
- Unique segment-level BSP points: 429
- Symbols with at least one Bi-level BSP: 79 / 79
- Symbols with at least one segment-level BSP: 79 / 79

## 2. Bi-level BSP type memberships

A single BSP point may carry more than one type, so these memberships do not sum to the unique-point count.

- 1: 1,017
- 1p: 412
- 2: 1,399
- 2s: 1,110
- 3a: 293
- 3b: 302

## 3. Segment-level BSP type memberships

- 1: 117
- 1p: 57
- 2: 147
- 2s: 84
- 3a: 14
- 3b: 26

## 4. Example stocks

### AAPL
- Bars: 4,211
- Bi: 217
- Segments: 31 (27 sure + 4 virtual)
- Zhongshu: 24
- Unique BSP: 41
- Type memberships: 1=10, 1p=4, 2=14, 2s=9, 3a=3, 3b=3
- Segment-level BSP: 1

### ABT
- Bars: 4,211
- Bi: 222
- Segments: 36 (33 sure + 3 virtual)
- Zhongshu: 28
- Unique BSP: 41
- Type memberships: 1=9, 1p=7, 2=16, 2s=6, 3a=3, 3b=1
- Segment-level BSP: 8

### AMZN
- Bars: 4,211
- Bi: 235
- Segments: 39 (34 sure + 5 virtual)
- Zhongshu: 25
- Unique BSP: 44
- Type memberships: 1=12, 1p=6, 2=18, 2s=5, 3a=2, 3b=3
- Segment-level BSP: 4

### NVDA
- Bars: 4,211
- Bi: 238
- Segments: 33 (29 sure + 4 virtual)
- Zhongshu: 30
- Unique BSP: 53
- Type memberships: 1=16, 1p=1, 2=17, 2s=15, 3a=2, 3b=5
- Segment-level BSP: 1

## 5. Direct contrast with current in-house Chan engine

Current in-house 79-stock diagnostic:
- Bi: 9,967
- Segments: 1,134
- L1+ units: 1,128
- L0 Zhongshu: 1,317
- L1+ Zhongshu: 140
- Formal L1+ BSP: 118 total
- Recent 300-bar L1+ static anchors: 28 across only 25 / 79 symbols

Pinned upstream chan.py:
- Bi: 17,810
- Segments: 2,677
- Zhongshu: 2,101
- Unique Bi-level BSP: 4,306
- Unique segment-level BSP: 429
- Every one of 79 symbols has both Bi-level BSP and segment-level BSP at the final frame.

The upstream engine therefore preserves much more intermediate structure and maintains virtual (not-yet-sure) segments instead of discarding them until full confirmation.

## 6. Interpretation

This baseline does NOT prove every upstream signal is tradable or non-repainting. The upstream project explicitly maintains current-frame uncertain structures and permits BSPs to disappear later if later bars invalidate them.

However, it does prove that our current in-house engine is substantially more structurally compressed and sparse than a mature Chan implementation under the same market data.

The next required audit is causal:
1. record when each upstream BSP first appears,
2. record whether it later disappears or changes type,
3. separate sure-structure BSP from virtual-structure BSP,
4. measure first-observed delay from its plotted anchor,
5. compare those results to our current engine.

No production adoption is authorized by this baseline alone.
