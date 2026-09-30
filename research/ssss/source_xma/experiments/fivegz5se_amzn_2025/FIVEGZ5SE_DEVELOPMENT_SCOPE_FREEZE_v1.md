# FIVEGZ5SE Development Scope Freeze v1

Status: **FROZEN**

Date: 2026-09-29

## Scope rule

Before the formal overall / cross-symbol validation stage, all exploratory
FIVEGZ5SE work is restricted to:

- Symbol: AMZN
- Market mode: SCTYPE=1
- Development window: 2023-01-01 through 2025-12-31
- Trading data actually used: available AMZN trading sessions inside those
  three calendar years

This development scope applies to:
- formula-engine reproduction checks;
- five-dimension combination discovery;
- W1 / W3 / W5 path-feature research;
- candidate buy/sell discovery;
- statistical comparisons;
- controlled rule iteration;
- sensitivity analysis;
- preliminary trading backtests.

## Primary research principle: combination-first

The primary task is **not** to optimize W1/W3/W5 as three standalone systems.

The primary task is to search for the strongest repeatable buy/sell structure
across combinations of the five dimensions:

- Trend
- Capital
- Momentum
- Acceleration
- Anomaly

Candidate rules may combine:
- current five-color states;
- cross-dimension combinations;
- internal numerical strength / distance-to-threshold variables;
- transition direction;
- persistence;
- weakening / strengthening;
- interaction effects.

W1/W3/W5 are temporal context features inside this broader combination search.

## Rationale

The purpose is to reduce repeated computation while the research framework is
still changing.

Do not repeatedly rerun the full 39-symbol / six-year universe during rule
development.

## Overall-validation gate

Only after a candidate rule is explicitly frozen may the research expand to:
- the frozen multi-symbol universe;
- longer history;
- cross-symbol robustness;
- final out-of-sample / holdout testing.

No rule may be modified in response to the overall-validation result without
creating a newly named research version.

## Window model

The development study retains:
- W1: t-1 -> t
- W3: t-3 ... t
- W5: t-5 ... t

These windows are **supporting context**, not the main optimization target.

A candidate may use one, multiple, or none of them if the broader
five-dimension combination is statistically stronger.

W1 is not treated as the sole causal boundary.

Closure:

`FIVEGZ5SE_DEVELOPMENT_SCOPE_AMZN_2023_2025 = FROZEN`
