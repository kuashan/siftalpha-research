# FIVEGZ5SE Operation Logic Governance v1

Status: **FROZEN_RESEARCH_CONSTRAINT**

Date: 2026-09-29

## 1. Purpose

This document freezes two non-negotiable rules for all future FIVEGZ5SE
buy/sell research.

The rules apply to:
- Top-100 candidate pruning;
- candidate-family clustering;
- complete trading-path construction;
- future V3/V4 revisions;
- later cross-symbol validation.

## 2. Temporal-context rule

A trading decision must not be inferred only from the immediately previous bar.

The research must jointly consider:

- W1: t-1 -> t, for immediate transition / inflection;
- W3: t-3 ... t, for short formation path;
- W5: t-5 ... t, for persistence / deterioration / recovery context.

W1 is a useful feature, but it is **not the sole causal boundary**.

A candidate that contains only a W1 predicate may remain in the discovery
catalog, but it cannot be promoted to an operating buy/sell rule until its
W3/W5 context has been analyzed.

Examples of valid path questions:

- W5 still bearish, but W3 has already turned upward;
- W1 weakens, but W3/W5 remain strongly positive;
- W3 acceleration recovers while W5 capital deteriorates;
- current color is unchanged, but W3/W5 slopes materially change;
- short-term reversal conflicts with longer persistence.

The objective is to identify the **formation process**, not only the latest
color change.

## 3. Original formula prompts are prohibited as trading labels

The original FIVEGZ5SE formula action prompts must not be used to define,
train, rank, validate, or confirm the research trading logic.

Examples include, but are not limited to:

- OPEN
- CLEAR
- REDUCE
- RISK
- 抄
- 清
- 高抛
- 减仓
- any other author-provided operation annotation

They may be retained only as archival annotations for source-formula study.

They are not:
- ground truth;
- labels;
- validation targets;
- confirmation signals;
- ranking inputs.

## 4. Allowed source of operating logic

Buy/sell rules may only be promoted from empirical comparisons of real market
data.

The admissible evidence includes:

- current five-dimension states;
- W1/W3/W5 transition paths;
- state persistence;
- slopes / deltas / threshold distances;
- cross-dimension combinations;
- matched-control comparisons;
- forward-return distributions;
- MFE / MAE;
- per-year stability;
- statistical pruning;
- later untouched-symbol validation.

The operating logic is therefore **research-derived**, not copied from the
formula author's operation prompts.

## 5. Implication for the Top-100 catalogs

The existing Top-100 BUY and Top-100 SELL catalogs remain valid as discovery
catalogs.

However, the next pruning stage must add a temporal-context audit for every
surviving family:

1. What does W1 say?
2. What does W3 say?
3. What does W5 say?
4. Is the signal an inflection, continuation, exhaustion, or divergence?
5. Does adding W3/W5 context materially improve robustness over a W1-only
   expression?
6. Is a W1-only predicate merely a proxy for an underlying 3/5-bar process?

No W1-only candidate is automatically rejected, but no W1-only candidate is
promoted without this audit.

## 6. V2 preservation

Current V2 remains preserved exactly as a historical reference:

- BUY-A
- BUY-B
- SELL-A
- SELL-B
- SELL-C

This governance rule does not silently modify V2.

Future revisions must be versioned separately.

## 7. Closure

`FIVEGZ5SE_OPERATION_LOGIC_GOVERNANCE_V1 = FROZEN`

Hard constraints:

`TEMPORAL_CONTEXT = W1 + W3 + W5`

`ORIGINAL_OPERATION_PROMPTS = NOT_ALLOWED_AS_TRADING_LOGIC`
