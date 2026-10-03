# Chan B1P / S1P 79-Stock Causal Validation v1

Status: CURRENT_FORM_REJECTED_NOT_ADMITTED  
Branch: `feature/chan-standalone-v2`  
Validation HEAD: `37d36d83385fba33c76c54dedfc0a57aef259b22`  
CI Run: `37108891637` — PASS  
Population: 79 stock snapshots  
Production strategy changed: NO

## 1. Candidate definition

This study does not relax standard B1/S1.

A diagnostic B1P/S1P candidate must first satisfy the same local structural predicates as current standard B1/S1:
- completed same-level Zhongshu,
- completed same-direction enter/leave movements,
- leave moves outside Zhongshu,
- leave creates the required new low/high,
- leave force is weaker.

It is then classified by the same-level Zhongshu relationship:
- FIRST_CENTER: `link=None`
- OVERLAP_CENTER: `link=overlap`
- STANDARD: link matches expected trend direction
- OPPOSITE_LINK: rejected context

B1P/S1P use prefix replay to determine the first bar on which the final candidate is actually observable. Evaluation starts at the next bar open.

## 2. Counts

Across 79 stocks:

- B1P/S1P candidates: 16
- Symbols represented: 16
- B1P: 3
- S1P: 13
- FIRST_CENTER: 14
- OVERLAP_CENTER: 2
- opposite-link rejected cases: 0

The sample is strongly asymmetric toward S1P.

## 3. Causal confirmation delay

All 16 B1P/S1P candidates were replayed bar-by-bar.

Delay between the structure's internal source-confirm bar and the actual first-observed bar:
- mean: 32.0 bars
- median: 29.0 bars
- p75: 45.25 bars
- max: 94 bars

FIRST_CENTER only:
- mean: 33.29 bars
- median: 29 bars
- max: 94 bars

This is the central failure of the current form. These events can look like earlier turning points on a final historical chart, but the causal signal is often not observable until many bars later.

## 4. Forward performance from true next-bar execution

Directional returns are signed so positive means favorable to the B/S direction.

### All B1P/S1P, n=16

5 bars:
- win rate: 43.75%
- mean: +0.12%
- median: -0.38%

10 bars:
- win rate: 43.75%
- mean: +0.75%
- median: -0.54%

20 bars:
- win rate: 43.75%
- mean: +0.43%
- median: -0.64%

40 bars:
- win rate: 75.00%
- mean: +3.11%
- median: +4.74%
- mean MFE: +9.88%
- mean MAE: -7.40%

The apparent 40-bar improvement does not rescue the signal as a responsive reversal signal because first observation is already delayed by a median 29 bars.

### FIRST_CENTER, n=14

5 bars:
- win rate: 50.00%
- mean: +0.19%

10 bars:
- win rate: 50.00%
- mean: +1.05%

20 bars:
- win rate: 50.00%
- mean: +1.41%

40 bars:
- win rate: 85.71%
- mean: +4.74%
- median: +5.93%

This is interesting as a medium-horizon descriptive effect, but the sample is small and dominated by S1P (13 S1P vs 1 B1P).

### OVERLAP_CENTER, n=2

5 / 10 / 20 / 40-bar win rate: 0%

40-bar mean directional return: -8.28%

The sample is too small for a broad conclusion, but there is no evidence to admit this subtype.

## 5. Structural outcomes over 40 bars

All B1P/S1P:
- return to old Zhongshu: 6.25%
- create another adverse new extreme: 37.50%
- same-level B2/S2 within 40 bars: 0%
- path counts:
  - CENTER_ONLY: 1
  - EXTREME_ONLY: 6
  - NEITHER: 9

Therefore the current B1P/S1P form does not behave like a prompt "return to Zhongshu -> B2/S2" sequence.

## 6. Comparators

Current L1+ standard B1/S1 has only one event in this population, so its performance is not statistically usable as a comparator.

L0 standard-like B1/S1 has 127 static events, but that comparator is measured from the structure's source-confirm time rather than causal first observation. It must not be used as a direct performance comparison against the causal B1P/S1P test.

## 7. Decision

1. Do not add B1P/S1P to production in the current form.
2. Do not remove the standard B1/S1 same-level trend-link requirement.
3. Do not admit OVERLAP_CENTER.
4. FIRST_CENTER remains a research observation only.
5. The next technical/theory issue is not "more signals"; it is why L1 segment/Zhongshu structures become first-observable 29 bars late on median.
6. Before any new signal class is admitted, the segment/Zhongshu confirmation state machine must be audited for earlier causal confirmation that is theoretically justified and does not repaint.

This preserves the standard B1/S1 definition and avoids converting a historically attractive anchor into a late, hindsight-driven trading signal.
