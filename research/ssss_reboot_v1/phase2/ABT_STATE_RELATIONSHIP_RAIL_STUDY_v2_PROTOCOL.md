# SSSS Reboot — ABT State-Relationship Rail Study v2 Protocol

Status: **FROZEN BEFORE OUTCOME RUN**
Date: 2026-10-02

## Research goal

All SSSS research is ultimately intended to identify statistically defensible
BUY / SELL points.

This round does not assume that any rail touch is automatically a trade.
Instead it tests which **state context** makes a lower-rail event more suitable
as a BUY candidate and which context makes an upper-rail event more suitable as
a SELL candidate.

## Symbol / data

Pilot symbol: ABT
Interval: daily
Warm-up: from 2018-01-02
Main study window: 2020-01-02 through 2025-12-31 where returned data exist.

Historical representation:
**FIRST_OBSERVED** only.

At every bar t:
- only data <= t are visible;
- XMA25 and XMA60 are recalculated at the right edge;
- no finalized historical XMA is backfilled.

## XMA boundary

XMA structure is immutable.

Preserve exactly:
- XMA(XMA(L,25),25)
- XMA(XMA(H,25),25)
- XMA(XMA(L,60),60)
- XMA(XMA(H,60),60)

No causal substitute and no smoothing replacement.

## State vocabulary

Use source formula states:
- UP = COLOR000066 / deep blue
- DOWN = COLOR003300 / deep green
- RANGE = COLOR555555 / deep gray
- EXPANSION = recorded but excluded from primary three-state comparison

Candlestick UI color is NOT used as a research variable.

## State-context fields

For every rail event persist:

1. current_state
2. state_run_age
   - number of consecutive bars including the event bar in current_state
3. origin_state
   - the state immediately preceding the current state run
4. age_bucket
   - FRESH: 1-3 bars
   - EARLY: 4-10 bars
   - MATURE: 11-20 bars
   - LATE: 21+ bars
5. transition_pair
   - origin_state -> current_state
6. recent_transition
   - TRUE if state_run_age <= 5
   - FALSE otherwise

The run origin is computed strictly from prior FIRST_OBSERVED states.

## BUY-side primary event

A new lower-rail excursion episode:
- current Low < current ZD1
- prior bar was not already below its own first-observed ZD1

Outcome horizon: 20 bars.

BUY-relevant outcome fields:
- hit MID within 20
- hit upper rail ZK1 within 20
- hit outer lower BD within 20
- MID before BD
- BD before MID
- 20-bar median MFE
- 20-bar median MAE
- 20-bar close return

Interpretation:
- MID-before-BD = cleaner rebound path
- BD-before-MID = adverse continuation before rebound
- upper-rail hit = stronger recovery
- MFE/MAE measure reward/adverse path magnitude

These are research labels only, not execution rules.

## SELL-side primary event

A new upper-rail excursion episode:
- current High > current ZK1
- prior bar was not already above its own first-observed ZK1

Outcome horizon: 20 bars.

SELL-relevant outcome fields:
- hit MID within 20
- hit lower rail ZD1 within 20
- hit outer upper BS within 20
- MID before BS
- BS before MID
- 20-bar MFE
- 20-bar MAE
- 20-bar close return

Interpretation:
- MID-before-BS = cleaner downside mean reversion
- BS-before-MID = adverse continuation before decline
- lower-rail hit = stronger decline

## Secondary events

For state-context comparison also retain:
- outer lower BD episode
- outer upper BS episode
- MID support-from-above episode
- slow light-gray support-from-above
- slow light-gray resistance-from-below

These are secondary because ABT sample sizes are smaller.

## Minimum sample rule

Do not call a context statistically interesting unless n >= 5.

For n < 5:
- show it only as anecdotal / insufficient;
- do not rank it as a candidate BUY / SELL context.

## Reporting hierarchy

1. current state only — baseline from v1.1
2. current state x age bucket
3. transition pair for recent transitions only
4. compare whether state context materially changes the BUY/SELL path

No candlestick-color split in this round.

## Closure question

The round is complete when it can answer:

### BUY
Under which state relationship does a lower-rail excursion most often:
- rebound to MID before BD;
- reach ZK1;
- produce favorable MFE relative to MAE?

### SELL
Under which state relationship does an upper-rail excursion most often:
- fall to MID before BS;
- reach ZD1;
- produce favorable downside movement before adverse continuation?

The result remains an ABT pilot and must be validated on additional stocks
before becoming a frozen SSSS trading rule.
