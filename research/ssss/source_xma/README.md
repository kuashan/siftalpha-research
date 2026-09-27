# SSSS Source-XMA Research Track

Status: ACTIVE / EXPLORATORY  
Started: 2026-09-27  
Branch baseline: main @ 512375038ba794536d785e51ad29fa14b9897d4b

## Purpose

This track studies the original Futu indicator logic using the source XMA formulas without replacing XMA with DEMA, EMA, SMA, or another causal approximation.

It is deliberately separate from the current causal SSSS implementation documented in `research/ssss/SSSS_CURRENT_STATE.md`.

Nothing in this directory supersedes the validated causal model unless a later official research round explicitly promotes a finding.

## Source indicators

- SSSS.ftindex
- ADKBY-E.ftindex

The two indicators share the same core 25-period double-XMA price structure.

This track treats the author's displayed money-bag/person icons, 多/空/平 labels, star, and warning symbols as observations only. They are not the target labels for our own trading logic.

## Research question

Can the information contained in the original XMA structure be reorganized into a clearer decision process based on:

1. market regime,
2. price location,
3. XMA-band behavior,
4. momentum transition,
5. confirmation / failure,

without simply copying the source indicator's existing signals?

## First study

Instrument: ABT (Abbott Laboratories)  
Timeframe: Daily  
Replay start anchor: 2025-01-01  
First tradable US session after anchor: 2025-01-02  
End: latest available session at the time the study is run.

Method: point-in-time walk-forward replay, not a conventional return-optimization backtest.

## Important evidence classification

ABT and a later full-history screenshot have already been inspected before this track was created.

Therefore the ABT 2025-present study is **exploratory / previously seen data**.

It must not be described as OOS or Frozen OOS evidence, and it cannot by itself promote a new production rule.

The purpose of ABT is to reconstruct and understand the source-XMA behavior and design a candidate decision language. A later official validation round must use properly pre-registered untouched data under `SSSS_RESEARCH_PROTOCOL.md`.

## Non-negotiable rule

Do not silently replace XMA.

If the study is computed outside Futu, the implementation must first establish and document the exact XMA behavior being reproduced. Any approximation must be labeled as an approximation and kept outside this track.
