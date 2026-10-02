# v3 Validation Status Addendum

Status: **FROZEN BEFORE OUTCOME RUN**
Date: 2026-10-02

This addendum defines status labels before the 34-instrument outcomes are read.

## Stocks

For each prespecified candidate, use the 28-stock validation cohort
(excluding ABT and AAPL).

An eligible symbol must contribute >= 3 candidate events.

Breadth-qualified:
- pooled n >= 30; and
- >= 8 eligible symbols.

If breadth-qualified:

- **SUPPORTS_ABT** when:
  - pooled primary-direction probability >= 55%; and
  - >= 65% of eligible symbols have primary-direction probability > 50%.

- **CONTRADICTS_ABT** when:
  - pooled primary-direction probability <= 45%; and
  - >= 65% of eligible symbols have the opposite direction > 50%.

- **MIXED** otherwise.

If breadth is not met:
- **INSUFFICIENT_BREADTH**.

## Crypto

Eligible crypto asset:
- >= 3 candidate events.

Breadth-qualified:
- pooled n >= 20; and
- >= 3 eligible crypto assets.

If breadth-qualified:

- **SUPPORTS_STOCK_HYPOTHESIS** when:
  - pooled primary-direction probability >= 55%; and
  - at least 2/3 eligible crypto assets are > 50% in that direction.

- **CONTRADICTS_STOCK_HYPOTHESIS** when:
  - pooled primary-direction probability <= 45%; and
  - at least 2/3 eligible crypto assets favor the opposite direction.

- **MIXED** otherwise.

If breadth is not met:
- **INSUFFICIENT_BREADTH**.

No threshold may be changed after results are observed.
