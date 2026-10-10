# SSSS V2 execution / repaint audit policy

Status: IMPLEMENTED_IN_ISOLATED_BRANCH; MERGE_REQUIRES_ALL_CI_PASS.

## Unchanged formula
- Original `strategy/SSSS.ftindex.b64` stays SHA-256 locked. No smoothing
  period, XMA formula or color-zone condition was changed.
- Original icon 9 (💰) is the only B signal. Icon 15 (💥) is the only S
  signal. For the same latest closed bar, S takes priority.
- XMA is a future/repainting function. Old source-bar icons may appear
  later when the indicator is recomputed. This is **not** proof that the
  icon was present at the source candle's close.

## Causal eligibility and forensic display
- Run the evaluator against exactly the last 1000 CLOSED candles.
- ONLY a *newly detected icon on the latest closed candle* may cause
  an order in the immediately following bar.
- A first-time detection on a prior closed candle is persisted with
  `LATE_REPAINT_IGNORED`, never allowed to trade or consume sell_stage.
- Poll again on the SAME latest closed candle to allow late Binance OHLC
  finalization / idempotent retry. No repeated order for an already
  consumed (timeframe, icon, source-bar-time) key.
- On first start or tracker migration baseline the entire 1000 bar
  history, retain any prior sell_stage. If the next open is not exactly
  one timeframe after the signal bar, skip the stale signal.
- UI: `💰/💥` are recalculated present-formula icons. A distinct gray
  `记录💰/记录💥` represents an original detected event whose chart
  icon later disappeared due to repaint. `B/S/X` always means verified
  FILLED exchange orders and is drawn at execution-bar time.
- Existing records are never backfilled, fabricated or converted into
  unverified fills.

## Capital and profitable exits (same as ZBGE)
- The per-symbol user configurable `capital_budget_usdt` is **initial
  strategy margin**. Each 💰 spends EXACTLY 25% of this budget (at
  1x leverage 25% nominal), no conversion to 25% of remaining cash or
  compounding equity; skip if insufficient budget or exchange margin.
- Repeated 💰 can increase allocation 0→25→50→75→100%, and after
  reductions may reuse freed fraction.
- First successful 💥, if eligible, market-sells 75% of the **actual
  Binance long position** and advances `sell_stage` 0→1 ONLY after
  confirmed or recovered FILLED. Following B does not change this stage.
- Second successful 💥 fully exits remaining actual position, resets
  `sell_stage` to 0, ready for a new cycle.
- S eligibility: BOTH signal-bar closing price and next-bar execution
  reference open price strictly greater than Binance native weighted
  average position-entry price. At/below, cost missing, short position,
  quantity invalid or insufficient exchange margin => no sell; no stage
  advance. Profit is *not guaranteed* with a market order because of
  slippage/fees.
- Other strategies (5s Crypto V1 and ZBGE B/S) remain frozen.

## Deployment gate
- Deploy a successful exact ARM64 digest, only after full CI pass and
  initial backup / exchange position reconciliation.
- No LIVE auto-order enablement or production state reset as part of
  the branch merge. Test SSSS Demo (start, first-B, two S stages,
  re-buy between stages, restart recovery, insufficient margin).
