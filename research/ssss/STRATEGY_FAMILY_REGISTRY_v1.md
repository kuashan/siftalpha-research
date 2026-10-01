# Strategy Family Registry v1

Status: **5S_V1_ONLY / FROZEN_ARCHITECTURE**
Date: 2026-10-02

## Active strategy family

`STRATEGY_1_ID = 5s-v1`

5s-v1 is the retained cross-asset strategy family derived from the FIVEGZ5SE
three-buy / three-sell research lineage.

The family contains separate frozen asset profiles.

### 5s crypto v1

Status:

`5S_CRYPTO_V1 = FROZEN_BASELINE`

Validated development universe:
BTC / ETH / BNB / SOL.

Frozen operating rules:
- BUY-A or BUY-B -> enter 60% at next bar open.
- BUY-C onset within W3 -> add remaining 40% to 100%.
- BUY-C cannot independently open.
- no A/A or B/B repeat add.
- no A->B or B->A add.
- no W5 BUY-C top-up.
- first SELL-A -> exit 100%.
- first SELL-B -> exit 100%.
- first SELL-C -> exit 100%.
- same-bar multi SELL -> exit 100%.
- no independent Risk Exit layer.
- close-confirmed signal -> next-bar-open execution.

This baseline must not be modified in place.

### 5s stocks v1

Status:

`5S_STOCKS_V1 = FROZEN_BASELINE`

Frozen operating rules:

BUY:
- first BUY-A or BUY-B -> enter 60% at next regular-session open;
- BUY-C onset within W3 -> add remaining 40% to 100%;
- BUY-C cannot independently open;
- no same-family repeat add;
- no A->B / B->A add;
- no W5 BUY-C top-up.

SELL:
- isolated SELL-A -> sell 50%;
- isolated SELL-B -> sell 50%;
- SELL-C -> sell 100%;
- same-bar multi-family SELL -> sell 100%;
- after an isolated A/B half-sale, the first later distinct SELL family exits the remainder.

Risk layer:
- no independent Risk Exit layer.

Execution:
- signal confirmed at close;
- execute at next regular-session open;
- long/cash only.

The 39-stock development sample has already influenced this baseline.
Formal production validation still requires genuine forward / untouched OOS evidence.

## Governance

Only the 5s-v1 family is registered in the active research architecture.

`5S_V1_FAMILY = FROZEN`

`5S_CRYPTO_V1 = FROZEN_BASELINE`

`5S_STOCKS_V1 = FROZEN_BASELINE`

Any future change must use a new version and preserve these baselines as controls.
