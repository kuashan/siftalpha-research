# FIVEGZ5SE staged-entry correction protocol v2

Status: FROZEN_BEFORE_CORRECTION_RUN
Date: 2026-09-30
Branch: research/source-xma-walkforward
Observed starting HEAD: f1b1cc6b512a1ff6a8ab1d913ef4d6d5d68a81b6

## Reason for correction

The v1 completion used crypto symbols:
BTC, ETH, BNB, SOL, XRP, DOGE, ADA, AVAX, LINK, TRX.

That does not match the pre-registered user-requested crypto universe:
BTC, ETH, BNB, XRP, SOL, TRX, ZEC, DOGE, LINK, XMR.

Therefore v1 crypto and combined conclusions are retained only as diagnostic history and are not admissible as the final result for this experiment.

## Frozen correction rules

- Stock batches 1-3 are not recomputed; their existing raw JSON results are reused.
- Crypto is recomputed for exactly:
  BTC, ETH, BNB, XRP, SOL, TRX, ZEC, DOGE, LINK, XMR.
- All 10 crypto assets use one common provider for this correction to avoid mixed-provider bias.
- Provider: Yahoo Finance, retrieved through yfinance.
- Requested raw interval: 2021-01-03 through 2024-04-09 inclusive.
- If a ticker has a shorter real history, use the real available interval and record it; do not fabricate rows.
- Exact downloaded OHLCV inputs are archived in this experiment directory with SHA-256 hashes.
- SCTYPE remains 1.
- Formula-native action labels are never used as trading truth.
- Entry parameters remain pre-registered: initial 50%, 60%, 70%; C confirmation W3 or W5.
- BUY-C never opens independently.
- Only A->C or B->C can top up to 100%.
- A->A, B->B, A->B, B->A do not add.
- No pyramiding above 100%.
- Execution remains next-session open with 5 bps adverse slippage per side.
- No time-based forced exit.
- Open positions at the sample end remain mark-to-market.
- Both FULL_FIRST and SELECTIVE exit controls are analyzed.
- Bootstrap uses asset-level resampling with a fixed seed and reports 95% intervals.

## Frozen code identities

- Base replay engine blob SHA: a1fbc3887c6894c611877b6ae38be75254ef14af
- Staged-entry experiment blob SHA: 0009e67d99f24ed1153461e0ef6c9edda356e27d

The engine and staged-entry signal definitions are not modified for the correction.

## Required v2 outputs

1. Corrected 10-crypto raw results.
2. Exact archived crypto OHLCV inputs + manifest.
3. All 49 assets × all 16 configs per-asset table.
4. FULL_FIRST and SELECTIVE grouped summaries.
5. Tail-risk table.
6. Confirmation-event table and confirmation-accuracy summary.
7. Bootstrap / robustness table.
8. Crypto provider-parity diagnostic for overlapping v1/v2 assets.
9. Final decision report that marks retained/rejected/diagnostic items and OOS status.

No 50/60/70 or W3/W5 winner is selected before these outputs are complete.
