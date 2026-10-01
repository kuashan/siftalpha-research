# Crypto SELL-C Partial Exit Study Final Report v1

Status: **IMPLEMENTED_AND_VERIFIED / CLOSED**

Date: 2026-10-01
Branch: `research/source-xma-walkforward`

## 1. Purpose

Resolve the remaining Crypto SELL-C action question using only BTC / ETH / BNB / SOL and the already-frozen daily Binance windows.

Tested exactly:
- SELL-C 25%
- SELL-C 50%
- SELL-C 75%
- SELL-C 100% current control

No BUY rule changed.
SELL-A / SELL-B remained full exit.
No post-result percentage was added.

## 2. Baseline reproduction

The 100% SELL-C control reproduced the prior Crypto refinement baseline exactly within 1e-9 tolerance.

- BTC trades difference: 0
- ETH trades difference: 0
- BNB trades difference: 0
- SOL trades difference: 0
- return differences: floating-point noise only

`CRYPTO_SELL_C_BASELINE_REPRODUCTION = PASS`

## 3. Corrected computation audit

The first computation pass contained an MDD-improvement sign-direction bug in the summary layer only.
The underlying per-coin portfolio paths, returns, P5, CVaR and MDD values were not affected.

The sign was corrected before interpretation and the complete official Binance computation was rerun.

Final corrected compute commit:
`5c260af95d249d1b666728f45bcd9d59becd47b2`

## 4. Four-coin aggregate

Current SELL-C 100% control:
- mean cumulative return: **+68.74%**
- mean intraday-low MDD: **-65.90%**
- mean P5: **-16.16%**
- mean CVaR10: **-18.85%**

| SELL-C action | Mean return | Return delta | Return improved | Mean MDD | MDD improvement | MDD improved | P5 delta | CVaR delta | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Sell 25% | +233.09% | +164.35pp | 4/4 | -64.86% | +1.04pp | 2/4 | -3.50pp | -1.94pp | FAIL |
| Sell 50% | +154.96% | +86.21pp | 3/4 | -63.11% | +2.79pp | 3/4 | -2.07pp | -1.41pp | FAIL |
| Sell 75% | +91.02% | +22.27pp | 3/4 | -61.77% | +4.12pp | 4/4 | -1.48pp | -0.93pp | FAIL |
| Sell 100% | +68.74% | control | — | -65.90% | control | — | control | control | RETAINED |

Bootstrap, 5000 deterministic resamples:

SELL 25%:
- return delta 95% CI: **[+43.82pp, +297.89pp]**
- MDD improvement CI: **[-3.16pp, +5.23pp]**
- P5 delta CI: **[-6.14pp, -0.86pp]**
- CVaR delta CI: **[-2.72pp, -1.16pp]**

SELL 50%:
- return delta 95% CI: **[+14.82pp, +154.09pp]**
- MDD improvement CI: **[-0.47pp, +6.04pp]**
- P5 delta CI: **[-4.63pp, -0.62pp]**
- CVaR delta CI: **[-1.82pp, -0.99pp]**

SELL 75%:
- return delta 95% CI: **[-20.96pp, +55.29pp]**
- MDD improvement CI: **[+1.81pp, +6.69pp]**
- P5 delta CI: **[-3.41pp, -0.26pp]**
- CVaR delta CI: **[-1.04pp, -0.83pp]**

All three partial policies worsen mean P5 and mean CVaR10.
For all three, the bootstrap intervals for P5 and CVaR deterioration are fully below zero.

## 5. Per-coin return result

| Coin | Sell 25% | Sell 50% | Sell 75% | Sell 100% |
|---|---:|---:|---:|---:|
| BTC | +144.93% | +79.27% | +29.59% | +7.24% |
| ETH | +380.69% | +210.84% | +92.33% | +29.39% |
| BNB | +260.15% | +202.62% | +142.83% | +95.19% |
| SOL | +146.58% | +127.09% | +99.32% | +143.14% |

The very high historical return of partial SELL-C is real in this frozen development sample, especially BTC / ETH / BNB.

However:
- SELL 50% and SELL 75% reduce SOL cumulative return;
- all partial policies worsen the pooled P5 / CVaR tail metrics;
- SELL 25% worsens MDD on BNB and SOL;
- SELL 50% worsens MDD on SOL.

## 6. SELL-C event evidence

First isolated SELL-C events:
- total n = **166**
- BUY-C-confirmed n = **19**

Wait-to-next-A/B mean return:
- all confirmed events: **+6.42%**
- pre-confirmation: **+5.18%**

By era:
- 2017-2020: **+7.04%**
- 2021-2023: **+7.31%**
- 2024-2026: **+1.44%**

This confirms the original diagnosis:
SELL-C often occurs before later upside is exhausted.

But the partial-exit portfolio tests show that monetizing that right-tail opportunity by mechanically retaining 25%-75% also degrades the loss tail.

## 7. Decision

No partial SELL-C policy passed all preregistered gates.

Therefore:

`CRYPTO_SELL_C_25 = REJECTED_NOT_ADMITTED`

`CRYPTO_SELL_C_50 = REJECTED_NOT_ADMITTED`

`CRYPTO_SELL_C_75 = REJECTED_NOT_ADMITTED`

`CRYPTO_SELL_C_FULL = RETAINED`

`CRYPTO_SELL_C_PARTIAL_STUDY_V1 = IMPLEMENTED_AND_VERIFIED`

Current Crypto operating control remains:

```
BUY-A / BUY-B -> 60%
BUY-C within W3 -> +40% to 100%

SELL-A -> 100%
SELL-B -> 100%
SELL-C -> 100%
same-bar multi SELL -> 100%
```

The important interpretation is not that SELL-C is identical to A/B.
It is still structurally different.
The result is narrower: **the tested fixed partial-retention fractions do not improve the full portfolio robustly enough to replace 100% SELL-C.**

## 8. Closure

`ROUND = CLOSED`

Do not continue tuning SELL-C percentages on these same BTC / ETH / BNB / SOL development data.
A future change requires genuinely untouched forward data or a materially different preregistered mechanism.
