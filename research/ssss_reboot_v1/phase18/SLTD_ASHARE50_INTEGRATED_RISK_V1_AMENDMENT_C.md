# SLTD A-share 50 Integrated Risk v1 — Amendment C

Status: **FROZEN BEFORE ANY STRATEGY RESULT**

## 1. Data-source audit outcome

Two integrity-only source attempts were operationally unsuitable on the current GitHub runner:

- Yahoo/yfinance: repeated long-running / failed audit under the 50-symbol snapshot job.
- Eastmoney via AkShare: 0/50 downloaded; remote endpoints closed connections.

No strategy result was produced from either failed source attempt.

The repository's earlier A-share20 study demonstrates that Yahoo had worked in a separate earlier
run, so this amendment does not reinterpret any market result; it only chooses a deterministic
snapshot path that works for this new 50-symbol study.

## 2. Final Phase18 snapshot source

Use BaoStock:

- package: `baostock`
- one authenticated anonymous session per audit job
- function: `query_history_k_data_plus`
- frequency: daily
- adjustment: `adjustflag="2"` (前复权)
- start: 2016-01-01
- end: 2026-09-30

Snapshot directory:

`ashare50_data_snapshot_v3`

Only v3 is admissible for Phase18 strategy research.

## 3. Historical ST guard

BaoStock exposes `isST`.

For the frozen main-board universe:
- if any formal-window row has `isST == 1`, the audit fails for that symbol;
- no strategy result may proceed until a pre-result universe amendment resolves it.

This preserves the ordinary-main-board price-limit assumption.

## 4. Everything else unchanged

Universe, 35/15 split, all strategy rules, C2, causal execution, risk methodology,
and Fresh OOS boundaries remain unchanged.

`SLTD_ASHARE50_INTEGRATED_RISK_V1_AMENDMENT_C = FROZEN`
