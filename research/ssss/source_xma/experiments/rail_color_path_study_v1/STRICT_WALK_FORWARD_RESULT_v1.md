# SSSS Rail + Color Path Study v1 — Strict Walk-Forward Result

Status: STRICT_DISCOVERY_COMPLETE / NOT_OOS / NOT_PRODUCTION
Date: 2026-10-01

This report supersedes `DISCOVERY_RESULT_v1.md` for numerical conclusions.
The earlier file is retained only as audit history.

## Method

Hard rule:
for each bar t, use only data <= t, recompute the right-edge XMA25/XMA60,
save first-observed rails/state, then advance to t+1.

No later XMA repaint is allowed to rewrite an earlier event.

Strict implementation baseline:
`experiments/falsification_v2/feb_xma_v1_strict_replay.py`

Universe:
- 11 equities: ABT, AAPL, AMZN, ORCL, INTC, MSFT, NVDA, GOOGL, META, JPM, XOM
- Crypto: BTC, ETH, BNB, SOL

Evaluation:
2025-01 through 2025-06.
Earlier bars are warm-up.

Primary rendered-color authority:
raw SSSS state formulas.
- UP = source dark red
- DOWN = source dark green (user theme may visually differ)
- RANGE = source dark gray
- EXPANSION stored separately

## Reproduction gate

Historical strict confluence events reproduced exactly:
- lower confluence: 28 expected / 28 reproduced / 0 missing / 0 extra
- upper confluence: 10 expected / 10 reproduced / 0 missing / 0 extra

Therefore the strict right-edge XMA path is aligned with the archived Source-XMA event study.

## Five-rail model

- BD = lower outer rail
- ZD1 = fast lower rail
- GZB18 = (ZD1 + ZK1)/2 analytical midpoint
- ZK1 = fast upper rail
- BS = upper outer rail
- GZB3..GZB4 = separate light-gray slow band

GZB18 is mathematically present in the source but is not explicitly plotted as a separate source line.

---

## A. Fast lower-rail excursion: low < ZD1

### UP / red state
n=30

Forward:
- +5 mean -0.62%, median -1.15%, positive 43.3%
- +10 mean -1.05%, median -1.83%
- +20 mean -3.41%, median -4.14%, positive 33.3%

20-bar path:
- reach upper ZK1: 11/30 = 36.7%
- reach midpoint only: 14/30 = 46.7%
- continue lower without midpoint: 5/30 = 16.7%
- made a new low at some point: 93.3%

Interpretation:
A lower-rail break while the band is still UP/red is not a reliable buy.
It behaves more like structural deterioration / pullback risk.

### DOWN state
n=43

Forward:
- +5 mean +2.01%, median +2.21%, positive 62.8%
- +10 mean +5.22%, median +3.90%, positive 68.3%
- +20 mean +8.92%, median +6.48%, positive 74.4%

20-bar path:
- reach upper ZK1: 26/43 = 60.5%
- reach midpoint only: 16/43 = 37.2%
- continue lower without midpoint: 1/43 = 2.3%
- made a new low at some point: 76.7%

Interpretation:
This is the strongest lower-side rebound family in this Discovery window,
but path risk remains high. It is a reversal precursor, not evidence for an immediate full-size entry.

### RANGE / gray state
n=24

Forward:
- +5 mean +1.10%, median -0.43%, positive 50.0%
- +10 mean +0.75%, median -1.07%
- +20 mean +2.71%, median +4.87%, positive 63.6%

20-bar path:
- reach upper ZK1: 17/24 = 70.8%
- reach midpoint only: 7/24 = 29.2%
- continue lower without midpoint: 0
- made a new low at some point: 87.5%

Interpretation:
Strong mean-reversion / traversal tendency, but not low-risk timing.
A lower touch in RANGE is a candidate reversal zone, not an automatic entry.

---

## B. Fast upper-rail excursion: high > ZK1

### UP / red state
n=38

Forward:
- +5 usable n=34, mean -1.85%, median -1.21%, positive 38.2%
- +10 usable n=30, mean -2.87%, median -2.24%
- +20 usable n=28, mean -5.20%, median -5.00%, positive 28.6%

20-bar path:
- reach lower ZD1: 20/38 = 52.6%
- reach midpoint but not lower: 11/38 = 28.9%
- continue upward without midpoint/lower: 6/38 = 15.8%
- unresolved: 1/38
- made a new high at some point: 76.3%

Midpoint after the upper event:
- midpoint touched: 31
- strict 3-bar midpoint hold: 19.4%
- among resolved upper-vs-lower first decisions after midpoint,
  upper reached first: 42.9%

Interpretation:
This is an exhaustion / reduce-warning family, but not an instant full exit or short.
Many events still make a later higher high before the eventual weakness.

### DOWN state
n=31

Forward:
- +5 mean +1.98%, median +1.55%, positive 61.3%
- +10 mean +3.60%, median +3.53%
- +20 mean +7.83%, median +6.59%, positive 63.3%

20-bar path:
- reach lower ZD1: 48.4%
- midpoint only: 22.6%
- continue upward without midpoint/lower: 29.0%
- made a new high: 93.5%

Interpretation:
Upper-rail interaction in DOWN is not a generic sell signal.

### RANGE / gray state
n=26

Forward:
- +5 usable n=24, mean +0.68%, median +0.13%, positive 50.0%
- +10 usable n=23, mean +0.22%, median +0.86%
- +20 usable n=20, mean +2.61%, median +3.81%, positive 60.0%

20-bar path:
- reach lower ZD1: 42.3%
- midpoint only: 34.6%
- continue upward: 19.2%
- made a new high: 88.5%

Interpretation:
Mixed/pivot behavior. Not a standalone sell.

---

## C. Outer rails

### Lower outer BD

UP/red:
- n=13
- +20 mean -3.82%, median -3.33%

DOWN:
- n=36
- +5 mean +1.20%, median +2.62%
- +20 mean +2.14%

RANGE:
- n=9
- +10 mean +7.42%, median +8.54%
- +20 mean +2.27%

Conclusion:
BD alone is not a universal support.
State conditioning is mandatory.

### Upper outer BS

UP/red:
- n=22
- +5 mean -1.17%
- +20 mean -3.90%, median -4.81%

DOWN:
- n=12
- +5 mean +2.79%
- +20 mean +6.45%

RANGE:
- n=17
- usable +5 n=15, mean +2.61%, positive 73.3%
- usable +20 n=12, mean +3.54%, positive 83.3%

Conclusion:
BS alone is not a universal resistance.
The stricter ZK1+BS confluence geometry is more informative.

Archived strict upper confluence, whose exact event dates were reproduced here:
- n=10
- +5 mean -4.32%, median -5.16%
- +10 mean -6.36%, median -6.48%
- +20 mean about -9.12% in lifecycle diagnostic

This remains a stronger exhaustion structure than BS alone.

---

## D. Midpoint GZB18

The midpoint is a meaningful path pivot, not a universal support line.

After UP/red upper-rail excursion:
- only 19.4% of midpoint touches passed the strict 3-bar hold definition
- 42.9% of resolved first decisions returned to upper before falling to lower

Therefore:
- midpoint loss after high-side extension is a useful risk-confirmation candidate;
- midpoint touch alone is not strong enough to call support.

For lower-side events, midpoint recovery is common:
- UP lower event: 83.3% reached midpoint
- DOWN lower event: 97.7%
- RANGE lower event: 100%

But this run does not yet prove that midpoint reclaim itself is the optimal entry timing.
That must be tested as a separate sequential event.

---

## E. Light-gray band GZB3..GZB4

The light-gray band is not a simple support/resistance strip.

Approach from above ("support-side"):

UP/red:
- n=56
- +5 mean -1.24%
- +20 mean -3.24%, median -4.44%
- entering the band: +20 mean -4.62%
- touch/reclaim: +20 mean -2.53%

RANGE:
- n=40
- results mixed
- entering the band: +20 mean -5.45%
- touch/reclaim: +20 mean +6.90% (smaller usable subset)

Approach from below ("resistance-side"):

UP/red:
- n=17
- +20 mean -5.81%
- strict touch/reject subtype n=11:
  +20 mean -8.52%, median -5.45%, positive 27.3%

DOWN:
- n=45
- +20 mean +3.97%, median +4.63%

RANGE:
- n=49
- +20 mean +2.48%, median +5.24%

Interpretation:
The gray band is a slow structural/regime layer.
Its meaning reverses with fast-band state and penetration pattern.
It must not be encoded as "touch from above = buy, touch from below = sell".

---

## F. Raw vs canonical sensitivity

Most event-state assignments were unchanged.
Observed mismatch rates were generally low:
- fast lower UP: 6.7%
- fast upper UP: 5.3%
- other major RANGE groups: 0%
- some outer/gray subgroups had modestly higher mismatch due to small n

Primary strategy semantics should therefore keep raw SSSS state ids for fidelity,
while canonical state remains a research sensitivity field.

---

## Discovery closure

Supported:
1. five-rail decomposition is valid;
2. state changes the meaning of the same rail event;
3. lower-fast in DOWN/RANGE is a reversal candidate family;
4. lower-fast in UP/red is not a generic buy;
5. upper-fast in UP/red is an exhaustion/reduce-warning family;
6. ZK1+BS strict upper confluence is stronger than BS alone;
7. midpoint is a pivot/confirmation candidate, not hard support;
8. outer rails alone are weak without state/confluence context;
9. light-gray band is a slow structural layer, not a simple support/resistance rule.

Not yet validated:
- production entry timing;
- position size;
- stop loss;
- add rules;
- exact midpoint-confirmation rule;
- short-entry rule.

No production rule is promoted from this Discovery run alone.
