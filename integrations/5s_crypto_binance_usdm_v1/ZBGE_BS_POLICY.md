# ZBGE B/S independent strategy — execution contract

Status: IMPLEMENTED_IN_ISOLATED_BRANCH / NOT_LIVE_VALIDATED

This strategy **replaces MatrixQuant PAI** in the selectable strategies of
`integrations/5s_crypto_binance_usdm_v1`. Frozen 5s Crypto V1 and SSSS must
not change.

## Pure signal conditions (on the current fully CLOSED candle)

- `trend = ZBGE2 - 10`, where ZBGE2 uses the owner-provided nested SMA/EMA.
- `yellow = (ZBGE14 > 1) AND (ZBGE18 > REF(ZBGE18,1)) AND (REF(ZBGE18,1) < REF(ZBGE18,2))`.
- `B = yellow AND trend < 20 AND ZBGE8 > 15`.
- `smile = ZBGE2 > 85 AND ZBGE2 > REF(ZBGE2,1)`.
- `S_A = follow_main > 0 AND trend > 75`. Follow-main uses
  `CROSS(ZBGE28,ZBGE27) AND ZBGE27>50 AND BARSLAST(CROSS(ZBGE27,ZBGE28)) >= 4`.
- `S_B = BARSLASTCOUNT(smile) == 3`; only the **third** bar in a
  continuously true smile run signals once. A later separated run can signal again.
- `S = S_A OR S_B`, not a requirement for both signals.

## Trading policy

- `capital_budget_usdt` is the **user-configured initial strategy margin
  budget** for this symbol, independent of total exchange account balance.
  The original default (1000) remains unchanged; users can configure 10000.
- Each completed B order uses **exactly 25% of that initial margin budget**,
  independent of subsequent equity or remaining cash (subject to exchange
  quantity step, minNotional, price drift and available margin). Skip if
  insufficient budget remains for a full 25% order or available exchange
  margin fails the safety check. Do not issue a smaller partial 25% tranche.
- First successful S sells **75% of the actual currently held position**.
  Its `sell_stage` becomes 1 *only after FILLED/recovered FILLED*.
- Second successful S sells all remaining held quantity and resets stage to 0.
- A new B after the first S is allowed and DOES NOT reset the sell stage;
  it updates the Binance-native weighted average entry price.
- For any S, the closed-bar signal price and next-bar reference open price
  must **both be strictly higher** than the Binance-native average entry
  price. At/below average means no sale and **no stage advance**.
  If the native entry price is unavailable, fail closed. The actual market
  fill price may move after submission, so this is **not a guaranteed profitable
  fill / stop-limit order**.
- Closed-bar signal, next bar open action. Stale delayed bars are skipped.
  B/S/X deal markers are emitted from confirmed filled orders, never from
  unfilled chart suggestions.
- Existing strategy slots are isolated by strategy ID + symbol and cannot
  switch while running or with an open position. A legacy PAI slot is blocked
  from further trading and must be stopped and manually switched after
  orders/positions are reconciled; the retired `mfra-` order identifier is
  retained **solely** to safely recover old ledger activity.

## Boundaries still to verify before live trading

1. Exact live Binance BTCUSDT/other-symbol closed candles vs exported
   original FuTu indicator on same timestamps and timeframes.
2. PAPER / Binance USD-M Demo integration tests plus test-order confirmation,
   partial quantity rounding, fees, and intermittent exchange errors.
3. Crash/restart recovery with a first-S fill and a subsequent B before
   final S. Never infer successful fills from mere signal detection.

No previous research returns or win-rate numbers constitute production
acceptance.
