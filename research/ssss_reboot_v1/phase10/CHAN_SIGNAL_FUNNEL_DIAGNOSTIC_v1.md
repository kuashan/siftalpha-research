# Chan Signal Funnel Diagnostic v1

Status: DIAGNOSTIC_COMPLETE_NO_PRODUCTION_CHANGE  
Branch: `feature/chan-standalone-v2`  
Diagnostic HEAD: `85d98ce83f5dd1fc986173af426808ee60ad797a`  
Population: 79 stock snapshots under `research/ssss_reboot_v1/phase7/data_snapshot/batch_*_stocks`  
Purpose: explain why canonical L1+ B/S signals are sparse without changing Chan production equations.

## 1. Final signal counts

### L0 raw / diagnostic-only
- B1: 25
- B2: 519
- B3: 774
- S1: 102
- S2: 536
- S3: 485
- Total: 2441
- Symbols with at least one L0 signal: 79 / 79

### L1+ canonical
- B1: 0
- B2: 10
- B3: 67
- S1: 1
- S2: 15
- S3: 25
- Total: 118
- Symbols with at least one L1+ signal over the full analysis window: 68 / 79

### L1+ signals whose static anchor is inside the latest 300 displayed bars
- B1: 0
- B2: 0
- B3: 17
- S1: 1
- S2: 2
- S3: 8
- Total: 28
- Symbols with at least one such signal: 25 / 79
- Therefore 54 / 79 symbols have no L1+ static signal anchor in the current 300-bar display window.

## 2. Structural compression funnel

Across 79 stocks:

- Bi units: 9967
- Segments: 1134 total / 1055 completed
- L0 Zhongshu: 1317 total / 1259 completed
- L1+ levels: 78
- L1+ units: 1128
- L1+ Zhongshu: 140 total / 92 completed
- L1+ trend-type groups: 124 total / 46 completed
- L1+ directional trend groups: 16 total / only 2 completed

This shows that the major loss of sensitivity begins before the final B/S predicates: the current segment -> L1 Zhongshu -> trend chain is very coarse.

## 3. Exact current-production B1/S1 funnel

The exact current B1/S1 predicates were replayed as a sequential funnel on L1+:

1. Complete Zhongshu: 92
2. Has completed enter + leave movement: 92
3. Enter/leave same direction: 69
4. Leave is outside the Zhongshu: 53
5. Leave makes required new extreme: 39
6. Leave force is weaker: 17
7. Previous/current Zhongshu directional link matches expected trend: 1
8. Final B1/S1: 1 = B1 0 + S1 1

The largest collapse is stage 6 -> 7: 17 candidates become 1.

For those 17 already-qualified divergence candidates, the current `link_zhongshus` state is:
- link = None: 14
- link = overlap: 2
- link = up: 1
- link = down: 0

The 14 `None` cases are primarily first-Zhongshu cases: `link_zhongshus` intentionally assigns the first Zhongshu no incoming trend link. Under the current definition they cannot become standard trend B1/S1 because a prior same-level Zhongshu relationship is required.

## 4. Comparison with L0 B1/S1 funnel

L0 has much denser structure:

- Complete Zhongshu: 1259
- Same-direction enter/leave: 788
- Outside Zhongshu: 606
- New extreme: 528
- Weaker force: 271
- Matching Zhongshu link: 127
- Final B1/S1: B1 25 + S1 102 = 127

This is why the older display, which allowed L0 signals, appeared much more responsive.

## 5. Interpretation

1. The current sparse display is not caused by the newly added Shunshi overlay.
2. It is not explained by one overly strict MACD threshold; no proprietary fixed MACD eligibility threshold is used here.
3. The main cause is structural granularity:
   - only L1+ may emit formal signals;
   - L1+ creates few same-level Zhongshu sequences;
   - most otherwise-qualified B1/S1 candidates occur at a first Zhongshu and therefore have no prior same-level link;
   - only 25/79 stocks even have an L1+ static signal anchored inside the latest 300 bars.
4. Therefore blindly relaxing B1/S1 predicates would be the wrong first fix. The bottleneck exists upstream in level construction / formal-signal level policy.

## 6. Boundary for the next study

No production change is admitted by this diagnostic.

The next study should compare, without changing the six B/S equations:
- Track A: current L1+ formal signals;
- Track B: L0 signals exposed as explicitly lower-level/auxiliary Chan signals;
- Track C: investigate whether first-Zhongshu reversal / consolidation-divergence cases have a theory-supported classification distinct from standard trend B1/S1.

Any admission must be based on theory consistency plus broad-market validation, not on increasing signal count for a particular stock.
