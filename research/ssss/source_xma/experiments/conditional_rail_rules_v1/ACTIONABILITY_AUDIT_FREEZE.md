# SSSS Conditional Rail Rules v1 — Actionability Audit Freeze

Status: FROZEN_BEFORE_ACTIONABILITY_OUTCOME
Date: 2026-10-02

## Purpose
Round 3 showed three transition-conditioned effects that were measured from the
original rail-event date. A transition is only known when the transition bar
actually closes. Therefore B2/S1/S2 cannot be promoted to executable rules until
their remaining edge is measured from the actual detection time.

## Frozen candidates
B2:
- source event = LOWER_FAST
- required first transition in frozen Round-2 ledger = RANGE->UP

S1:
- source event = UPPER_FAST
- required first transition = UP->RANGE

S2:
- source event = UPPER_FAST
- required first transition = RANGE->DOWN

No new transition definition is introduced.

## Source of truth
Use the already persisted Round-2 strict first-observed XMA event ledgers.
The fields event date, transition string and transition_bars are authoritative.
Do not recompute or relabel transitions using finalized/repainted XMA.

## Detection time
For each retained event:
- detection_index = event_index + transition_bars
- detection_date = trading date at detection_index
- signal becomes known only after detection_date close

## Two outcome anchors

### A. Detection-close diagnostic
Anchor = detection-date close.
Measure underlying asset return after 5/10/20 trading bars plus MFE/MAE.
This measures whether any directional effect remains once the transition is
actually observable.

### B. Next-open executable diagnostic
Execution = next tradable session open after detection date.
No same-close execution is allowed.
Measure:
- 5/10/20-bar close return from execution open
- 20-bar MFE and MAE from execution open
- positive/negative outcome rate
- temporal blocks A/B/C
- symbol breadth
- leave-one-symbol-out sign stability

No slippage/commission is applied in this gate because the purpose is signal
actionability rather than portfolio PnL. If a later strategy freeze uses costs,
costs must be frozen separately before backtest.

## Direction
B2 expected direction = bullish.
S1 expected direction = bearish underlying return after signal.
S2 expected direction = bearish underlying return after signal.

For S1/S2, negative asset return after next-open means an exit/reduce action
would have avoided subsequent decline. This audit does not create a short rule.

## Validity
Exclude:
- events whose detection bar cannot be mapped to the symbol's trading calendar;
- events with no next tradable open;
- horizons extending beyond available data for that specific metric.

Do not substitute dates.

## Promotion gate
A transition-conditioned candidate may move to candidate strategy freeze only if:
1. expected direction remains after detection close;
2. expected direction remains after next-open execution;
3. mean and median do not materially contradict each other;
4. effect survives multiple temporal blocks where sample exists;
5. leave-one-symbol-out does not flip the pooled sign;
6. sample-size limitations remain explicitly recorded.

No BUY/SELL production labels or sizing are frozen in this audit.
