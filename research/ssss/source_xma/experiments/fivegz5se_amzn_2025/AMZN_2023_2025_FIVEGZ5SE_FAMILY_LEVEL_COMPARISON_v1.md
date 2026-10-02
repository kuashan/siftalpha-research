# AMZN 2023-2025 FIVEGZ5SE Family-Level Comparison v1

Status: **FAMILY_LEVEL_COMPARISON_COMPLETE**

Date: 2026-09-29

Starting HEAD:
`e9cc0d90154c1f13ff8b647a0faa65e0f325aee1`

## 1. Purpose

This stage compares the already-classified mechanism families.

It does **not** create new predicates and does not modify V2.

Hard constraints remain:
- AMZN 2023-2025 development data only;
- SCTYPE=1;
- W1/W3/W5 path context retained;
- original formula operation prompts are not used;
- no arbitrary time cap;
- current V2 remains frozen as baseline.

## 2. Baseline

Signal-only V2 on AMZN 2023-2025:

- return: **+280.26%**
- MDD: **-13.88%**
- closed trades: **18**
- closed-trade win rate: **94.44%**
- exposure: **51.06%**
- one position still open at 2025-12-31

V2 entry events:
- BUY-A: 20
- BUY-B: 17
- exact union: 37

V2 sell events:
- SELL-A: 15
- SELL-B: 15
- SELL-C: 20
- exact union: 47

## 3. Comparison method

For every family representative:

1. exact event overlap with V2;
2. near overlap within ±3 trading sessions;
3. near overlap within ±5 trading sessions;
4. events remaining outside ±3 of all V2 events;
5. 5/10/20-day behavior of those novel events;
6. per-year direction of novel events;
7. complete trading-path re-run after adding only that family to V2.

Near-date overlap is necessary because W1/W3/W5 mechanisms may identify the
same formation a few sessions apart.

## 4. BUY family findings

### B-F1 — weak-state trend inflection

Representative: B001

- representative 10d mean: +6.64%
- ±3-day overlap with V2: **100%**
- novel events beyond V2: **0**
- V2 + B-F1 return: **+280.26%**

Conclusion:

`B-F1 = V2_VARIANT`

It is useful as a mechanism explanation, but does not add new opportunities
beyond the existing BUY-A / BUY-B union.

### B-F2 — capital repairs first

Representative: B005

- representative 10d mean: +5.76%
- ±3-day overlap with V2: 73.33%
- novel events: 4
- novel 10d mean: +2.28%
- novel win rate: 75%
- no novel 2025 event
- V2 + B-F2 return: **+265.79%**
- delta vs V2: **-14.47 pp**

Conclusion:

`B-F2 = DO_NOT_ADD_TO_PATH`

The family is statistically interesting, but its incremental events do not
improve the current trading path.

### B-F3 — capital weak / acceleration repairs first

Representative: B004

- exact overlap with V2: **100%**
- novel events: 0
- V2 + B-F3: **+280.26%**

Conclusion:

`B-F3 = V2_VARIANT`

This is already represented by BUY-B.

### B-F5 — neutral-zone recovery

Representative: B007

```
Trend = GRAY
AND Capital W3 net > 0
AND Capital positive on >=2 of last 3 bars
AND Capital W5 slope > 0
AND Anomaly = GRAY
```

Evidence:

- representative n=15
- representative 10d mean: +4.92%
- representative win rate: 93.33%
- exact overlap with V2: only 6.67%
- ±3 overlap with V2: 53.33%
- **7 genuinely novel events**
- novel-event 10d mean: **+4.37%**
- novel-event win rate: **85.71%**

Novel events by year:

- 2023: n=2, mean +6.20%
- 2024: n=4, mean +3.97%
- 2025: n=1, mean +2.32%

Complete path:

- V2: +280.26%
- V2 + B-F5: **+284.57%**
- delta: **+4.31 pp**
- MDD remains -13.88%
- trade count unchanged at 18
- exposure rises from 51.06% to 52.79%

Conclusion:

`B-F5 = PROMOTE_TO_V3_ENTRY_CANDIDATE`

This is the only new BUY mechanism in this comparison that shows both:
- meaningful novel events outside V2;
- positive incremental behavior when inserted into the full path.

This is still AMZN-development evidence, not final admission.

### B-F6 — multidimensional composite recovery

Representative: B077

- exact overlap with V2: 0%
- ±3 overlap: 59.09%
- novel events: 9
- novel mean: +2.33%
- novel win rate: 66.67%
- 2023 novel mean: -0.70%
- 2024 novel mean: +8.40%
- 2025 novel n=0
- V2 + B-F6: **+239.19%**
- delta: **-41.07 pp**

Conclusion:

`B-F6 = DO_NOT_ADD_TO_PATH`

It supplies more signals but materially worsens the complete strategy.

## 5. SELL family findings

No new SELL family improved the V2 complete path.

### S-F1 — trend weakens while momentum remains strong

- novel events: 5
- novel mean 10d: -1.08%
- mixed years
- V2 + S-F1: +272.74%
- delta: -7.52 pp

`S-F1 = DO_NOT_ADD`

### S-F2 — acceleration decay / high-level stall

- novel events: 9
- novel mean 10d: -0.08%
- V2 + S-F2: +263.95%
- delta: -16.31 pp

`S-F2 = DO_NOT_ADD`

### S-F3 — capital deterioration divergence

Representative is SELL-B itself.

`S-F3 = ALREADY_IN_V2`

### S-F4 — anomaly overheat / strong-end stage

- ±3 overlap with V2: 80%
- novel events: 3
- novel 10d mean: **+2.55%**, wrong direction for an exit
- V2 + S-F4: +278.03%

`S-F4_NEW_REP = DO_NOT_ADD`

The family remains represented by SELL-C in V2.

### S-F5 — failed continuation after broad strength

Representative is SELL-A itself.

`S-F5 = ALREADY_IN_V2`

### S-F8 — multidimensional composite deterioration

This is the most independent new SELL mechanism:

- exact overlap with V2: 12.5%
- ±3 overlap: 50%
- novel events: 8
- novel 10d mean: -1.00%

But novel years are inconsistent:

- 2023: +2.25% (wrong direction)
- 2024: -0.70%
- 2025: -4.87%

Complete path:

- V2 + S-F8: **+259.59%**
- delta: **-20.67 pp**
- win rate falls from 94.44% to 88.89%

Conclusion:

`S-F8 = EVENT_LEVEL_INTERESTING_BUT_PATH_REJECTED`

It should not be added to V2/V3 at this stage.

## 6. Adding all families is explicitly rejected

All BUY representative families together provide 15 events outside ±3 days of
V2, but their aggregate novel-event 10d mean is only **+1.85%** because weaker
families dilute B-F5.

All SELL representative families together provide 18 events outside ±3 days of
V2, but their aggregate novel-event 10d mean is **+0.21%**, which is the wrong
direction for an exit set.

Therefore:

`ADD_ALL_FAMILIES = REJECTED_NOT_ADMITTED`

The research must select mechanisms, not maximize signal count.

## 7. V3 implication

Current evidence supports only one incremental structural change for a future
candidate:

```
V3_ENTRY_CANDIDATE =
    BUY-A
    OR BUY-B
    OR B-F5 neutral-zone recovery
```

Current exit side remains unchanged:

```
V3_EXIT_CANDIDATE =
    SELL-A
    OR SELL-B
    OR SELL-C
```

No V3 is frozen yet.

This document only identifies the candidate structure to test next.

## 8. Combined B-F5 + S-F8 check

For completeness:

- V2 + B-F5 + S-F8: +272.70%
- delta vs V2: -7.56 pp
- trades: 22
- win rate: 86.36%

Thus S-F8 destroys the incremental benefit of B-F5.

## 9. Research state

`FAMILY_LEVEL_COMPARISON_V1 = COMPLETE`

`B-F5 = PROMOTED_TO_NEXT_ENTRY_TEST`

`NEW_SELL_FAMILY = NONE_PROMOTED`

`V2 = PRESERVED`

`V3 = NOT_YET_FROZEN`
