# Contrarian Alpha Confirmation v0

Status: **NO-GO / CLOSED**

Branch baseline audited before study:
- branch: `research/source-xma-walkforward`
- pre-study HEAD: `0ba050de73704d639ed30a06d3dc8ac19dffd724`
- latest message: `research: remove SSSS strategy and preserve 5s lineage`

## Purpose

This is the final independent confirmation step after `Causal Alpha Discovery v0` showed an unexpected inverse ordering: low original model scores often had higher future returns than high scores.

The hypothesis was frozen **before** opening the older validation period:

`Contrarian Score = - Original Model Score`

No feature selection, threshold tuning, symbol-specific parameters, or extra model search was allowed.

## Frozen protocol

- Symbols: ABT, AMD, AMZN
- Evaluation period: 2018-01-02 through 2021-10-04
- Pre-evaluation training history: from 2015-01-02
- Bar: 1 day
- Signal timing: T close
- Execution convention: T+1 open
- Targets: future 5 / 10 / 20 bars
- Features: same 18 causal price / EMA / ATR / volatility / channel / volume / candle features used in the discovery phase
- Main model: Ridge Regression
- Review model: Logistic Regression
- Retrain cadence: every 20 bars, expanding walk-forward
- Label embargo: equal to prediction horizon
- Score buckets: fixed Top 10% vs Bottom 10%

## Pre-registered pass rule

PASS required all of the following:
1. pooled contrarian Top 10% must clearly outperform pooled Bottom 10% for 5, 10 and 20 bars;
2. 20-bar direction must agree in at least 2 of 3 symbols;
3. the independent review model must show the same overall direction.

## Independent validation results

### Main model: Ridge Regression

| Horizon | Pooled Top 10% | Pooled Bottom 10% | Top-Bottom Spread | Result |
|---|---:|---:|---:|---|
| 5 bars | +0.93% | +1.32% | -0.38% | FAIL |
| 10 bars | +1.47% | +2.12% | -0.65% | FAIL |
| 20 bars | +1.93% | +1.84% | +0.09% | weak / not sufficient |

20-bar by symbol:
- ABT: +3.57% vs +3.71%, spread -0.14%
- AMD: +11.24% vs -3.31%, spread +14.55%
- AMZN: +6.73% vs -0.49%, spread +7.22%

The 20-bar symbol-direction condition is met by AMD and AMZN, but the pooled 5- and 10-bar requirements fail.

### Review model: Logistic Regression

| Horizon | Pooled Top 10% | Pooled Bottom 10% | Top-Bottom Spread |
|---|---:|---:|---:|
| 5 bars | +1.00% | +0.27% | +0.72% |
| 10 bars | +1.84% | +0.71% | +1.13% |
| 20 bars | +2.63% | +1.09% | +1.55% |

20-bar by symbol:
- ABT: +0.50% vs +4.81%, spread -4.31%
- AMD: +9.87% vs +0.57%, spread +9.29%
- AMZN: +7.30% vs -1.60%, spread +8.90%

The review model is directionally more supportive, but the pre-registered rule requires the main model to pass as well. It does not.

## Verdict

`CONTRARIAN_ALPHA_CONFIRMATION_V0 = NO-GO`

`STATUS = CLOSED`

The inverse effect discovered in 2021-2026 does not reproduce with sufficient consistency in the independent 2018-2021 period under the frozen main model. It is therefore rejected as a basis for a new trading indicator.

## Governance consequence

- Do not invert the old score and promote it as an indicator.
- Do not tune the threshold after seeing these results.
- Do not add a third model to rescue the hypothesis.
- Do not add more symbols to this confirmation round.
- Do not reopen SSSS/XMA direct-migration work from this result.

This research line is closed unless a future project is explicitly authorized with a new hypothesis and a new pre-registered protocol.
