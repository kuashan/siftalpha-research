# FIVEGZ5SE staged-entry crypto scope amendment v2a

Status: FROZEN_BEFORE_CORRECTION_RUN
Date: 2026-09-30
Parent protocol: FIVEGZ5SE_STAGED_ENTRY_CORRECTION_PROTOCOL_v2.md
Observed starting HEAD: 5e61c6c6b82224fd73e8449e355af932621853d8

## User-directed scope change

The user clarified the intended live-trading focus before the correction run:

- BTC: primary future trading asset.
- ETH: secondary candidate.
- BNB: secondary candidate.
- SOL: secondary candidate.

Therefore the crypto research universe for this staged-entry decision is reduced to exactly:

BTC, ETH, BNB, SOL.

ZEC, XMR, XRP, TRX, DOGE, LINK and all other cryptocurrencies are outside this decision scope.

## Consequences

- No new crypto provider is needed.
- Reuse the already-computed raw crypto results for BTC, ETH, BNB and SOL from crypto_batch_v1.json because all four were run under the same source and the same frozen staged-entry engine.
- The incorrect inclusion of ADA/AVAX and the prior broader 10-crypto aggregate remain diagnostic history only.
- Final decision universe becomes:
  - 39 U.S. stocks
  - 4 cryptocurrencies
  - 43 total assets
- All 16 configs per asset must still be included:
  - W3 and W5
  - BASE / INIT 50 / INIT 60 / INIT 70
  - FULL_FIRST and SELECTIVE
- Tail-risk, confirmation, open-position, stock-vs-crypto, combined, and bootstrap analyses are recomputed for the 43-asset universe.
- No parameter is selected before the 43-asset outputs are complete.

This amendment supersedes only the crypto-universe section of the parent correction protocol. All other frozen rules remain unchanged.
