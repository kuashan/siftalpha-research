# FEB_XMA_v1 Full-History Replay Integrity Audit v1

Status: **EXISTING REPLAY NOT VERIFIED — CORRECTED STRICT REPLAY REQUIRED**

Date: 2026-09-29

Audit base:
- branch: `research/source-xma-walkforward`
- pre-audit HEAD: `8734bae3ca6029b2892f9138ba2bfe19d3c8bfd2`

Artifacts audited:
- `FEB_XMA_v1_FULLHISTORY_PROTOCOL.md`
- `FEB_XMA_v1_REPLAY_BATCH1.json`
- `FEB_XMA_v1_REPLAY_BATCH2.json`
- `FEB_XMA_v1_REPLAY_BATCH3.json`
- `FEB_XMA_v1_FULLHISTORY_RESULTS.json`
- `FEB_XMA_v1_FULLHISTORY_EQUITY.csv`
- `FEB_XMA_v1_FULLHISTORY_REPORT.md`

The existing result commit is:
`f47965a68064d6c1b15fc58ea3551944006eed10`

The later aggregate-equity commit is:
`5dd1440862bf9f47c71c488039eaaa7e961ddc5a`

## 1. What remains valid

The existing replay did preserve the intended high-level identity:
- strategy name: `FEB_XMA_v1`;
- 39 frozen equities;
- 2020-01-02 through 2025-12-30;
- next-open execution;
- 5 bps one-way slippage;
- long-only;
- legacy raw ADKBY-E slow formula family;
- original FEB thresholds;
- no HYS2/FIVEGZ/v2 synthetic hard gates.

Its reported headline result is therefore retained as historical evidence:
- cumulative return: +12.00%;
- CAGR: +1.91%;
- aggregate max drawdown: -4.69%;
- Sharpe: 0.76;
- positive sleeves: 23/39;
- SPY buy-and-hold: +112.13%.

It is **not deleted or overwritten**.

## 2. Material warm-up integrity failure

All three persisted replay batches show non-flat aggregate equity by
2020-01-06.

Examples:

Batch 1:
```text
2020-01-02  1.0000000000
2020-01-03  1.0000000000
2020-01-06  1.0001246307
```

Batch 2:
```text
2020-01-02  1.0000000000
2020-01-03  1.0000000000
2020-01-06  1.0002597984
```

Batch 3:
```text
2020-01-02  1.0000000000
2020-01-03  1.0000000000
2020-01-06  1.0004322754
```

The final aggregate equity file likewise moves on 2020-01-06.

However the replay source files checked across all three batches begin at
2020-01-02. Confirmed examples include:
- AAPL
- MSFT
- NVDA
- AMD
- AVGO
- ORCL
- INTC
- QCOM
- MU
- GOOGL
- META
- NFLX
- AMZN
- TSLA
- ABT
- JPM
- XOM
- PLD

The raw ADKBY-E slow weighted structure requires:
`REF(...,20)`.

Therefore the slow weighted input cannot be fully defined on 2020-01-02,
2020-01-03, or 2020-01-06 from these source files.

A valid FEB regime cannot exist before the required lagged observations exist.

The early equity movement is therefore incompatible with strict
formula-readiness semantics.

Most likely implementation failure mode:
```text
regime is missing / undefined
but code evaluates:
regime != BEAR
as true
```

That would allow lower-extreme probes before the slow regime exists.

This is an engineering/replay integrity failure, not a trading-rule finding.

## 3. Executable implementation was not persisted with the result

Comparing the frozen protocol commit:

`6e6c015c91a7fe8ee6e703e9fdab86f8aa986e67`

to the result commit:

`f47965a68064d6c1b15fc58ea3551944006eed10`

shows four result-side commits/files:
- `FEB_XMA_v1_REPLAY_BATCH1.json`
- `FEB_XMA_v1_REPLAY_BATCH2.json`
- `FEB_XMA_v1_REPLAY_BATCH3.json`
- `FEB_XMA_v1_FULLHISTORY_RESULTS.json`

No dedicated executable FEB_XMA_v1 full-history replay source was persisted
with those results.

The batch JSON schema contains only:
- symbols;
- per-symbol summary;
- batch aggregate index.

It does not contain:
- per-trade event ledger;
- per-symbol daily equity curve;
- action-priority trace;
- readiness trace.

Therefore the old headline result cannot be independently reproduced exactly
from persisted artifacts alone.

## 4. Requested per-symbol output is incomplete

The existing `per_symbol` result object contains:
- final capital;
- total return;
- max drawdown;
- average exposure;
- action counts;
- execution count.

It does **not** persist:
- per-symbol CAGR;
- per-symbol Sharpe;
- per-symbol daily equity curve sufficient to reconstruct Sharpe exactly.

The aggregate equity CSV contains only:
```text
date,equal_capital_index
```

Therefore missing per-symbol Sharpe values must not be fabricated from the
existing artifact.

## 5. ABT calibration remains PASS

The separate
`FEB_XMA_v1_ABT_2025_01_REPRODUCTION_AUDIT.md`
shows that the Source-XMA formulas and the five critical January ABT actions
are reproducible.

So the problem is not:
- XMA formula recovery;
- DEA formula recovery;
- normalized position recovery;
- January signal timing.

The problem is the full-history replay implementation/audit trail.

## 6. Integrity decision

```text
EXISTING_FEB_XMA_v1_FULLHISTORY_REPLAY
= LEGACY_DEVELOPMENT_RESULT
= NOT STRICTLY VERIFIED
```

Do not use the existing +12.00% as the final strict answer.

Do not delete it.

A corrected strict replay is required with:
1. explicit indicator readiness;
2. deterministic action priority consistent with the January calibration;
3. persisted executable implementation;
4. per-symbol daily equity;
5. per-symbol CAGR and Sharpe;
6. full event ledger;
7. no change to FEB_XMA_v1 thresholds or logic.

No result-based threshold tuning is permitted.
