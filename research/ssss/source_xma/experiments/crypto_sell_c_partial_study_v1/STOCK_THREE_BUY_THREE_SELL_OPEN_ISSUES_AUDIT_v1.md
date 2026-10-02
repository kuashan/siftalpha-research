# Stock Three-Buy / Three-Sell Open-Issues Audit v1

Status: **AUDITED / NO_NEW_STRUCTURAL_ISSUE**

Date: 2026-10-01
Branch: `research/source-xma-walkforward`

## 1. Question

After closing Risk Exit and Crypto SELL-C percentage refinement, does the current 39-stock three-buy / three-sell structure still contain a known unresolved trading-rule problem?

## 2. Current stock candidate

```
BUY-A / BUY-B -> 60%
BUY-C within W3 -> +40% to 100%

isolated SELL-A -> sell 50%
isolated SELL-B -> sell 50%
SELL-C -> sell 100%
same-bar multi SELL -> sell 100%
after A/B half sale, first later distinct SELL -> sell remaining position
```

## 3. Audit result

No additional stock rule is currently unresolved at the structural-definition level.

Already resolved:
- BUY-C independent opening: not admitted.
- W5 BUY-C top-up: not admitted.
- same-family repeat add: not admitted.
- A->B / B->A add: not admitted.
- A versus B different exit fractions: rejected.
- ignoring isolated A/B entirely: rejected.
- SELL-C / multi-family full exit: retained.
- fixed percentage Risk Exit: rejected.
- State / Volatility-Aware Risk Exit v1: rejected; no independent risk-exit layer is used.

Still requiring future validation, but not structurally undefined:
- `STOCK_BUY_60_W3_C_TOPUP = PROMOTED_TO_NEXT_VALIDATION`
- `STOCK_ISOLATED_SELL_A_B_HALF = PROMOTED_TO_NEXT_VALIDATION`

These have clear operating definitions already.

## 4. OOS boundary

The 39-stock history through 2026-09-29 has already influenced development and cannot be presented later as untouched OOS for these rules.

The remaining stock requirement is therefore:
- genuinely later forward data;
- or a separately frozen untouched asset/time universe;
- no parameter repair after observation.

## 5. Decision

`STOCK_THREE_BUY_THREE_SELL_STRUCTURAL_OPEN_ISSUES = NONE_IDENTIFIED`

`STOCK_THREE_BUY_THREE_SELL_OOS_VALIDATION = REQUIRED`

No new stock optimization round is opened by this audit.
