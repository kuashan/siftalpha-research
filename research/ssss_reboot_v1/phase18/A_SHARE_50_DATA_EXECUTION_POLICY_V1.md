# A-share 50 Data / Execution Policy v1

Status: **FROZEN BEFORE STRATEGY RESULTS**

Universe:
`A_SHARE_50_UNIVERSE_V1.json`

## 1. Market scope

Only Shanghai / Shenzhen **main-board ordinary A shares** in the frozen list.

Excluded by construction:
- ST / *ST
- STAR Market (688)
- ChiNext (300)
- Beijing Stock Exchange
- recent IPOs without enough pre-2018 warmup history

Formal research window:
- 2018-01-02 .. 2026-09-30

Download window:
- 2016-01-01 .. 2026-09-30

Purpose of pre-2018 data:
- causal SLTD warmup only
- no pre-2018 performance enters formal results

## 2. Price source

Primary source:
- Yahoo Finance via `yfinance`

Frozen request mode:
- daily bars
- `auto_adjust=True`
- `actions=False`
- no intraday data

Reason:
- adjusted OHLC reduces ex-right/dividend discontinuities that otherwise create artificial
  technical-state jumps in long A-share histories.
- every compared strategy uses the identical adjusted series.

Limitation:
- adjusted historical bars are a research normalization, not a literal reconstruction of
  every historical cash dividend/rights event.
- therefore the study is comparative strategy research, not brokerage-account tax accounting.

Raw downloaded adjusted snapshots must be archived with SHA-256 manifests before strategy results.

## 3. A-share causal execution

All signals:
- completed bar t only
- earliest action: next available bar open t+1

No same-bar execution.

This is compatible with A-share T+1 stock settlement because a position purchased at open t
cannot be sold until a later trading day; the earliest new sell signal based on bar t executes at open t+1.

## 4. Price-limit / unavailable-open rule

The frozen universe uses ordinary main-board stocks, so the research engine models the normal
10% daily price-limit regime.

If an intended BUY reaches a one-price locked limit-up bar:
- condition: Open == High == Low (within price tolerance)
- and Open / previous Close - 1 >= +9.5%
- BUY is not fillable at that open
- order remains pending to the next available open

If an intended SELL reaches a one-price locked limit-down bar:
- condition: Open == High == Low
- and Open / previous Close - 1 <= -9.5%
- SELL / hard exit is not fillable at that open
- order remains pending to the next available open

If the stock is suspended / no bar exists:
- pending order waits for the next available stock bar

No synthetic fill is allowed on a missing or locked bar.

## 5. Friction model

Primary normalized research friction:

BUY:
- 5 bps total execution friction

SELL before 2023-08-28:
- 15 bps total
- includes a 10 bps sell-side stamp-duty component plus 5 bps execution friction

SELL on/after 2023-08-28:
- 10 bps total
- includes the reduced 5 bps sell-side stamp-duty component plus 5 bps execution friction

Sensitivity:
- double the non-tax execution component from 5 bps to 10 bps
- historical stamp-duty schedule remains unchanged

Minimum brokerage commission is not modeled because portfolio capital is normalized and
position notionals are not mapped to a specific retail account size.

## 6. Development / Fresh split

Frozen:
- DEVELOPMENT = 35 symbols
- FRESH_OOS = 15 symbols

Fresh symbols may be downloaded and integrity-checked now, but:
- no signal performance
- no state performance
- no strategy return
- no risk-overlay result

may be computed on Fresh OOS before development admission gates pass.

Integrity audit does not consume Fresh OOS.

## 7. No US fitted weights

The new A-share study may reuse:
- SLTD state taxonomy
- XMA / FIRST_OBSERVED causal construction
- risk-adjusted scoring methodology
- MFE / MAE / return / probability / risk-reward research dimensions

It may **not** import US-fitted state utilities, thresholds, or 82-state live weights as A-share
risk parameters.

A-share risk parameters must be learned only from the frozen A-share DEVELOPMENT subset.

## 8. Freeze

`SLTD_ASHARE50_DATA_EXECUTION_POLICY_V1 = FROZEN`
