# SSSS V2 execution / repaint audit policy

Status: NEW_SSSS_POLICY_UNDER_CI_REVIEW; NO_LIVE_ENABLEMENT.

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

## Buy colors (runtime display policy, NOT an alteration to original .ftindex)
- `GZB12` = BLUE (same UI blue as before), `GZB13` = GREEN (previous UI
  incorrectly rendered this band red), `GZB14` = GRAY. These are the
  current product labels and have priority GRAY > BLUE > GREEN.
- A 💰 icon on BLUE may buy.
- A 💰 icon on GREEN **cannot** buy.
- A 💰 icon on GRAY may buy **only if the latest earlier non-gray band
  was GREEN** (including a continuous gray segment).
- A 💰 icon on GRAY after BLUE, or without an identifiable previous
  GREEN parent, is prohibited. Other/unclassified bands are prohibited.
- A prohibited 💰 remains a visible *indicator* signal, with no FILLED
  B marker and no change to any sell state.
- All original 💥 icons, from BLUE/GREEN/GRAY, may attempt selling;
  each must separately pass the average-cost safeguard.

## Capital and staged exits — supersedes the original fixed-25% policy
- The per-symbol user-configurable `capital_budget_usdt` remains the
  **initial strategy margin budget** (not account-wide exchange cash).
- First 💰 while flat buys 25% of initial budget.
- Any subsequent allowed 💰 in an uninterrupted accumulation phase
  buys 25% of the **unallocated portion** of the same initial budget:
  e.g. 10,000 -> 2,500 -> 1,875 -> 1,406.25 (assuming 1x, ignoring
  fees and price movement). The fraction converges toward 100%.
- When Binance's minimum quantity/notional or available margin makes
  a valid tranche impossible, skip without a synthetic fill, without
  resetting sell stage and without blocking the whole strategy.
- A qualifying 💥 sells 75% of the current actual Binance long holding
  on the FIRST successful exit, advancing `sell_stage=1` **only after
  FILLED**. The NEXT qualifying 💥 sells all remaining quantity and
  resets to stage zero *if no successful B intervened*.
- If an allowed 💰 appears AFTER that first 75% exit, buy exactly
  25% of **initial** budget again (only when sufficient unallocated
  budget is available). Only a successful FILLED buy resets the
  `sell_stage` back to 0; the next qualifying 💥 then sells **75%**
  again, not 100%. Subsequent buys within that cycle again use 25%
  of the remaining budget.
- Skipped/rejected 💰 never resets sell stage.
- A sell qualifies only if BOTH the signal-bar CLOSE and the next-bar
  OPEN reference price strictly exceed Binance native weighted-average
  position entry price. Otherwise skip this S without advancing stage.
- No new rule changes for 5s Crypto V1 or ZBGE B/S. Original source
  formula is unchanged and XMA retrospective-repaint trading remains
  forbidden.
- Market orders have slippage and fees; positive reference prices vs.
  average entry do NOT guarantee net-profit fills.

## Deployment gate
- Deploy a successful exact ARM64 digest, only after full CI pass and
  initial backup / exchange position reconciliation.
- No LIVE auto-order enablement or production state reset as part of
  the branch merge. Test SSSS Demo (start, first-B, two S stages,
  re-buy between stages, restart recovery, insufficient margin).
