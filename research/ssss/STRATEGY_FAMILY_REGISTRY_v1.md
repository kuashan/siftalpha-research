# Strategy Family Registry v1

Status: **CONSOLIDATED / THREE_STRATEGY_DEFINITIONS**
Date: 2026-10-02

## Registered strategy definitions

The current repository contains three formal strategy definitions:

1. **5s crypto v1** — frozen Crypto profile in the 5s-v1 cross-asset family.
2. **5s stocks v1** — frozen U.S.-stock profile in the 5s-v1 cross-asset family.
3. **SLTD V6** — official 15-rule structure strategy produced by the SSSS research lineage.

The two 5s strategies share signal-family lineage but keep separate asset-specific
position-management profiles. SLTD V6 is a separate strategy and must not be
forced into the 5s three-buy / three-sell operating template.

---

## Strategy 1A — 5s crypto v1

Family:

`STRATEGY_FAMILY_ID = 5s-v1`

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

Reference:
`research/ssss/5S_CRYPTO_V1_BASELINE.md`

---

## Strategy 1B — 5s stocks v1

Family:

`STRATEGY_FAMILY_ID = 5s-v1`

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

Reference:
`research/ssss/5S_STOCKS_V1_BASELINE.md`

---

## Strategy 2 — SLTD V6

Strategy ID:

`STRATEGY_2_ID = sltd-v6`

Status:

`SLTD_V6 = OFFICIAL`

SLTD V6 is the official strategy name for the current formal rule set produced
through V5 optimization and V6 independent validation.

Formal action taxonomy:
- BUY: 5 rules
- HOLD: 4 rules
- WAIT: 2 rules
- SELL: 4 rules
- Total: 15 formal rules

Research identity:
- historical representation: FIRST_OBSERVED
- XMA structure: unchanged
- research lineage: SSSS
- operational strategy name: SLTD V6

The formal V6 rule set excludes prior MIXED / WATCH / insufficient-breadth
rules. The five V5 discoveries were independently validated before final V6
promotion decisions.

References:
- `research/ssss_reboot_v1/phase6/SLTD_V6_OFFICIAL_NAMING.md`
- `research/ssss_reboot_v1/phase6/SSSS_FORMAL_15_ACTION_TAXONOMY_v1.md`
- `research/ssss_reboot_v1/phase6/SSSS_V6_FIVE_V5_DISCOVERY_INDEPENDENT_RESULT.md`

SLTD V6 currently has a formal research rule set but does not yet have the same
completed Trading Console execution integration as 5s crypto v1.

---

## Governance

Current registered strategy state:

`5S_V1_FAMILY = FROZEN`

`5S_CRYPTO_V1 = FROZEN_BASELINE`

`5S_STOCKS_V1 = FROZEN_BASELINE`

`SLTD_V6 = OFFICIAL`

Rules:
1. Do not modify frozen baselines in place.
2. Any future strategy change must use a new experiment / version.
3. Preserve the current baselines as controls.
4. Keep research status separate from runtime-integration status.
5. Do not describe a strategy as production-ready solely because its research rules are frozen or official.
