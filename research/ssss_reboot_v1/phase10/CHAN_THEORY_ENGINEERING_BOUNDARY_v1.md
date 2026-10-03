# Chan Theory × SLTD — Theory / Engineering Boundary v1

Status: **FROZEN_FOR_RESEARCH_DESIGN**
Date: 2026-10-03

## 1. Purpose

This document separates:

1. Chan theory rules that are explicit in the original 108 lessons;
2. later clarifications / corrections inside the original corpus;
3. engineering choices made by modern open-source implementations;
4. point-in-time rules required for causal quantitative research.

It is not a trading strategy.

## 2. Primary source hierarchy

Highest priority:
- original `教你炒股票` corpus and later corrections / replies;
- local public mirror used for source audit:
  `stockServ/chzhshch-108-plus`.

Important lessons for the quantitative core:
- 17 / 20 / 21 / 24 / 27 / 33 / 35 / 44 / 53 / 61;
- 62 / 65 / 67 / 71 / 72 / 77 / 78 / 79 / 80 / 81;
- 91 / 93 / 101 / 105 / 106.

Secondary engineering references:
- `Vespa314/chan.py`
- `waditu/czsc`
- `yijixiuxin/chanlun-pro`
- `mikonos/chanlun-kline`
- `neil-pan-s/one-quant-doc`

Secondary repositories are implementation evidence only. They are not treated as the definition source.

## 3. Canonical conceptual chain

```
Raw K
-> inclusion handling
-> fractal
-> stroke / Bi
-> feature sequence
-> segment
-> lower-level trend unit
-> Zhongshu
-> consolidation / trend
-> consolidation divergence / trend divergence
-> BSP1 / BSP2 / BSP3
-> recursive levels / multi-level linkage
```

## 4. Original-definition objects

### 4.1 Inclusion handling

Source basis: lessons 62 / 65.

Direction-aware merge is required before strict fractal construction.

Research requirement:
- merge is causal and left-to-right;
- every merged K object stores its raw-bar span;
- no future raw bar may alter already-confirmed history except the current unfinished merged object.

### 4.2 Fractal

A top / bottom fractal is defined on three adjacent inclusion-adjusted K units.

Two times must be stored:
- `anchor_time`: center K location;
- `confirm_time`: first time the required right-side K is actually observable.

A trading study may only use `confirm_time`.

### 4.3 Stroke / Bi

Original corpus contains an evolution in the stroke discussion.

The research engine must not silently mix variants.

Required v1 comparison:
- `BI_STRICT_77`: use the stricter lesson-77 style separation rule;
- `BI_LATE_106`: preserve the later minimum-extension interpretation as a separate candidate.

Before any performance study, one canonical variant must be frozen from:
- original examples;
- lesson-81 corrected examples;
- reproducibility;
- point-in-time stability.

No PnL is allowed to choose between the two.

### 4.4 Segment

Canonical source basis:
- lesson 67 feature-sequence definition;
- lessons 71 / 78 clarification;
- lesson 81 correction.

Required:
- feature sequence;
- standard feature sequence after inclusion handling;
- no-gap case;
- gap case;
- cancellation / continuation when later structure invalidates an unconfirmed split.

A segment endpoint has:
- `anchor_time`;
- `confirm_time`;
- `is_confirmed`.

Only the first-observed confirmed state can enter causal backtests.

### 4.5 Zhongshu

Canonical theoretical definition:
- overlap of at least three consecutive lower-level trend units.

Research boundary:
- a simple three-stroke overlap is **not automatically called canonical Zhongshu**;
- if a stroke-based overlap is used for diagnostics, it must be labeled
  `BI_OVERLAP_PROXY`.

### 4.6 Trend / consolidation

Canonical:
- consolidation contains one Zhongshu;
- trend requires at least two same-direction, non-overlapping Zhongshu at the same structural level.

Chart timeframe and structural level are not treated as synonyms.

### 4.7 Divergence

`TREND_DIVERGENCE` requires a valid trend structure first.

A plain MACD price divergence is not automatically Chan trend divergence.

MACD / volume / amplitude may be stored as strength measurement features, but the structural prerequisite is mandatory.

Separate labels:
- `PZ_DIVERGENCE` = consolidation divergence;
- `QS_DIVERGENCE` = trend divergence;
- `INDICATOR_DIVERGENCE_ONLY` = technical-indicator divergence without canonical Chan structure.

### 4.8 BSP1 / BSP2 / BSP3

The three classes are stored separately.

They must never be collapsed into a generic `SELL` or `BUY` label in the structural ledger.

For every BSP:
- structural level;
- direction;
- anchor time;
- first observed time;
- provisional / confirmed / invalidated state.

## 5. Point-in-time state model

Every object may occupy:

- `PROVISIONAL`
- `CONFIRMED`
- `INVALIDATED`

Historical plotting may show the object at its anchor.

Trading research must use:
- the state known at each bar;
- the first bar on which a transition became observable.

No final historical object list may be retroactively joined to old bars.

This is the Chan equivalent of SLTD `FIRST_OBSERVED`.

## 6. Hard causal rules

1. No BACKSET-like historical placement may create an earlier trade timestamp.
2. No final chart BSP may be assigned to its anchor date for backtesting.
3. If a provisional Bi / segment / BSP later disappears, that invalidation is part of the ledger.
4. A confirmed signal at completed bar t executes no earlier than t+1 available open.
5. SLTD and Chan must use the same normalized OHLC source, session policy and adjustment policy in any joint study.
6. A historical visualization layer and a causal trading layer must remain separate.

## 7. What may complement SLTD

Potentially independent Chan information:
- confirmed top / bottom fractal;
- unfinished vs completed up/down Bi;
- confirmed segment turn;
- Zhongshu position and exit / re-entry;
- consolidation divergence;
- trend divergence;
- BSP1 / BSP2 / BSP3;
- structural-level escalation or recovery.

These are hypotheses only.

None is admitted to SLTD by this document.

## 8. What is explicitly forbidden

Before structural validation is complete:
- no parameter sweep;
- no choosing the Bi definition by return;
- no optimizing a MACD threshold for profit;
- no adding Chan signals into V7;
- no changing V7 BUY rules;
- no changing V7 C2;
- no calling a technical-indicator divergence a canonical Chan divergence;
- no using final historical labels as if they were visible at the time.

## 9. Research terminology

Use:

- `SLTD_STATE_LAYER`
- `CHAN_STRUCTURE_LAYER`
- `POSITION_LAYER`

Do not describe Chan as a replacement for SLTD.

The working hypothesis is:

> SLTD describes trend / regime state; Chan describes structural progression and exhaustion.

This hypothesis must be tested, not assumed.

## 10. Closure

`CHAN_THEORY_ENGINEERING_BOUNDARY_V1 = FROZEN_FOR_RESEARCH_DESIGN`
