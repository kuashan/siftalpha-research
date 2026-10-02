# SSSS V6 — Five V5 Discoveries Independent Validation Result

Status: **COMPLETE**
Date: 2026-10-02

## Scope

- Frozen before outcome run: commit `4804d81b3baa077be4c720bfa356d196ec9c0cb0`
- 20 completely independent stocks:
  ACN, NOW, INTU, AMAT, LRCX,
  BKNG, TJX, CMG, ROST, MAR,
  DHR, SYK, MDT, BMY, ISRG,
  SCHW, SPGI, DE, HON, RTX
- Independent crypto transfer:
  XRP, ADA, DOGE, LTC
- Main window: 2020-01-02 through 2026-09-30
- FIRST_OBSERVED only
- XMA unchanged
- 20-bar primary outcome horizon

## Final validation

- **V6_A — GREEN→GRAY 1–3 + LIGHT_SUPPORT**
  - V5: n=48, 87.5%
  - V6 independent stocks: n=41, 80.5%, eligible=6, support=5/6, median-symbol=66.7%, **INSUFFICIENT_BREADTH**
  - V6 independent crypto: n=12, 83.3%, eligible=2, support=2/2, **INSUFFICIENT_BREADTH**
  - Final: **HOLD_FOR_MORE_DATA**

- **V6_B — BLUE 21+ + UPPER CLOSE_ABOVE**
  - V5: n=228, 82.9%
  - V6 independent stocks: n=320, 80.0%, eligible=20, support=20/20, median-symbol=79.3%, **VALIDATED_V6_STRONG**
  - V6 independent crypto: n=35, 80.0%, eligible=4, support=4/4, **SUPPORTS_V6_STOCK**
  - Final: **PROMOTE_TO_FORMAL**

- **V6_C — GRAY 4–10 + LOWER WICK_ONLY**
  - V5: n=45, 82.2%
  - V6 independent stocks: n=58, 75.9%, eligible=12, support=9/12, median-symbol=70.8%, **VALIDATED_V6_STRONG**
  - V6 independent crypto: n=26, 57.7%, eligible=4, support=2/4, **MIXED**
  - Final: **PROMOTE_TO_FORMAL**

- **V6_D — GREEN 11–20 + UPPER WICK_ONLY**
  - V5: n=49, 77.6%
  - V6 independent stocks: n=48, 64.6%, eligible=11, support=8/11, median-symbol=66.7%, **VALIDATED_V6**
  - V6 independent crypto: n=11, 90.9%, eligible=2, support=2/2, **INSUFFICIENT_BREADTH**
  - Final: **PROMOTE_TO_FORMAL**

- **V6_E — GREEN 11–20 + LIGHT_RESIST**
  - V5: n=88, 78.4%
  - V6 independent stocks: n=74, 70.3%, eligible=12, support=10/12, median-symbol=64.6%, **VALIDATED_V6_STRONG**
  - V6 independent crypto: n=18, 88.9%, eligible=4, support=4/4, **INSUFFICIENT_BREADTH**
  - Final: **PROMOTE_TO_FORMAL**

## Interpretation

The stock result is the formal V6 decision source. Crypto is a transfer check
and does not override the stock status.

A rule is promoted only if it passes the pre-registered independent-stock
breadth and probability thresholds.

## Batch closure

- Batch 1 Technology: COMPLETE
- Batch 2 Consumer: COMPLETE
- Batch 3 Healthcare: COMPLETE
- Batch 4 Financial / Industrial: COMPLETE
- Batch 5 independent Crypto: COMPLETE

`SSSS_V6_FIVE_V5_DISCOVERY_INDEPENDENT_VALIDATION = COMPLETE`
