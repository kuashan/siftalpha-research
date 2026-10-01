# Strategy Family Registry v1

Status: FROZEN_ARCHITECTURE / STRATEGY_1_RULESETS_VERSIONED
Date: 2026-10-01

## Strategy 1 — 5s V1 Strategy Family

Strategy 1 is not Crypto-only.

It is the first cross-asset strategy family derived from the FIVEGZ5SE
three-buy / three-sell research lineage.

Family identity:

`STRATEGY_1_ID = 5s-v1`

The family has separate asset profiles. Profiles share the same research
lineage and BUY-A / BUY-B / BUY-C / SELL-A / SELL-B / SELL-C signal families,
but an asset profile may have different position-management rules when the
data supports that difference.

Do not force Stock and Crypto to use identical exits merely for naming symmetry.

### Profile 1A — 5s crypto v1

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

This profile must not be modified in place.
Any future Crypto change requires a new version.

### Profile 1B — 5s stock v1

Status:

`5S_STOCK_V1_RULESET = FROZEN_CANDIDATE`

`5S_STOCK_V1_OOS = PENDING`

Research basis:
39 frozen U.S. stocks, extended historical development sample.

Frozen candidate rules:

BUY:
- first BUY-A or BUY-B -> enter 60% at next session open;
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
- after an isolated A/B half-sale, the first later distinct SELL family
  exits the remaining position.

Risk layer:
- no independent fixed Risk Exit;
- previously tested fixed and State/Volatility-aware Risk Exit layers were not admitted.

Execution:
- signal confirmed at close;
- execute at next tradable session open;
- long/cash only in the frozen research candidate.

Evidence already recorded:
- BUY-C top-up versus static 60%: mean return delta +15.17 pp across 39 stocks;
- 24/39 stocks improve return;
- top-up increases expected return but worsens MDD/tail risk on average;
- isolated A/B half-exit improves mean MDD by about +2.14 pp versus immediate full exit;
- 29/39 stocks improve MDD under A/B half-exit;
- no defensible evidence supports different A and B exit fractions.

Important boundary:
The stock rules are now frozen as the Strategy-1 Stock candidate profile,
but the historical 39-stock sample has already influenced development.
Therefore formal production validation still requires genuine forward OOS or
a separately frozen untouched universe.

Do not tune the frozen Stock v1 rules on the already-seen 39-stock development history.

## Strategy 2 — SSSS Structure Strategy

`STRATEGY_2_ID = ssss-structure`

Status:

`SSSS_STRUCTURE_STRATEGY = RESEARCH_IN_PROGRESS`

Strategy 2 is intentionally different from Strategy 1.

Core structure:
- five rails: BD / ZD1 / analytical MID / ZK1 / BS;
- three-color fast state;
- light-gray slow structure;
- state transitions;
- conditional path confirmation.

It does not have to use three BUY labels and three SELL labels.

Candidate action vocabulary may include:
WATCH / PROBE_ENTRY / CONFIRM_ENTRY / ADD / HOLD / REDUCE / EXIT / INVALIDATE.

Strategy 2 remains unfrozen until the conditional XMA research and validation
gates are closed.

## Multi-strategy architecture rule

Trading Console should expose:
- strategy_id;
- asset_profile;
- symbol;
- independent strategy state.

Recommended identity:

`strategy_id + asset_profile + symbol`

Examples:
- 5s-v1 / crypto-v1 / BTCUSDT
- 5s-v1 / stock-v1 / AMZN
- ssss-structure / future-profile / AMZN

A running strategy or open position must never be silently switched to another
strategy/profile.

## Freeze decision

`STRATEGY_1_FAMILY = FROZEN`

`STRATEGY_1_CRYPTO_PROFILE = FROZEN_BASELINE`

`STRATEGY_1_STOCK_PROFILE = FROZEN_CANDIDATE_RULESET_OOS_PENDING`

`STRATEGY_2_SSSS = RESEARCH_IN_PROGRESS`
