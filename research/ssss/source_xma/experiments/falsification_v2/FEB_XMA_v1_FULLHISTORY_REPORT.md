# FEB_XMA_v1 Full-History Replay Report

Status: **DEVELOPMENT / CONTAMINATED / LEGACY RAW SOURCE REPLAY**

Date: 2026-09-28

Protocol frozen before returns:
- `FEB_XMA_v1_FULLHISTORY_PROTOCOL.md`
- commit: `6e6c015c91a7fe8ee6e703e9fdab86f8aa986e67`

Result artifact:
- `FEB_XMA_v1_FULLHISTORY_RESULTS.json`
- result commit: `f47965a68064d6c1b15fc58ea3551944006eed10`

Equity curve:
- `FEB_XMA_v1_FULLHISTORY_EQUITY.csv`
- commit: `5dd1440862bf9f47c71c488039eaaa7e961ddc5a`

## Replay identity

This replay reproduces the earliest frozen multi-asset Source-XMA engine derived
from the successful ABT January discovery:

`FEB_XMA_v1`

It intentionally uses the legacy raw Source-XMA formula family that the
February engine actually used, rather than later canonical-corrected slow-channel
definitions.

ABT January formula checkpoints were reproduced before the batch run.

## Data

- 39 frozen equities
- 2020-01-02 through 2025-12-30
- same Devesh176/Replicating_portfolio OHLCV family used by v1/ABT
- all pre-2020 history available in each file used only for indicator warm-up

## Capital model

Preserves the original multi-asset research convention:

- $10,000 independent sleeve per symbol
- 39 sleeves = $390,000 initial aggregate capital
- no monthly reset
- equal-capital aggregate = arithmetic mean of sleeve equity curves
- next-open execution
- 5 bps one-way slippage
- long-only

## Aggregate result

- initial aggregate capital: **$390,000.00**
- final aggregate capital: **$436,788.95**
- cumulative return: **+12.00%**
- CAGR: **+1.91%**
- aggregate max drawdown: **-4.69%**
- annualized Sharpe: **0.76**
- average sleeve exposure: **11.42%**
- positive sleeves: **23 / 39**
- mean sleeve return: **+12.01%**
- median sleeve return: **+3.66%**

## Annual equal-capital aggregate returns

- 2020: **-0.19%**
- 2021: **+2.39%**
- 2022: **-3.11%**
- 2023: **+2.58%**
- 2024: **+6.16%**
- 2025: **+3.87%**

## Best / worst sleeves

Best:
- AVGO: **+120.76%**
- ORCL: **+102.11%**
- AMD: **+94.48%**
- NVDA: **+64.93%**
- META: **+41.89%**

Worst:
- AMZN: **-27.51%**
- MCD: **-22.37%**
- TMO: **-20.83%**
- BA: **-19.01%**
- KO: **-16.65%**

## Activity

- total executions: **13,856**
- probes: **5,631**
- confirmations: **677**
- independent breakout entries: **426**
- breakout adds: **321**
- reductions: **744**
- exits: **6,057**

The very high event count combined with low average exposure shows that the
legacy engine repeatedly opened small probes and exited them.

## SPY comparison

SPY buy-and-hold over the replay span after 5 bps entry and exit:

**+112.13%**

Therefore FEB_XMA_v1 is nominally profitable but does not beat passive SPY in
absolute wealth creation.

## Comparison with current v2 synthetic map

Current v2 synthetic development backtest:
- cumulative return: **+7.98%**
- CAGR: **+1.39%**
- max drawdown: **-30.95%**
- Sharpe: **0.17**
- average gross exposure: **71.31%**

FEB_XMA_v1 full-history replay:
- cumulative return: **+12.00%**
- CAGR: **+1.91%**
- max drawdown: **-4.69%**
- Sharpe: **0.76**
- average exposure: **11.42%**

The legacy FEB_XMA_v1 therefore performed better than the current synthetic v2
translation on this contaminated history in:
- total return;
- CAGR;
- drawdown;
- Sharpe.

The comparison is not a scientific head-to-head because the capital models are
different:
- FEB_XMA_v1 uses independent equal-capital sleeves;
- v2 synthetic uses one shared active-position portfolio.

The result is still practically informative: the v2 synthetic translation is
not automatically superior merely because the v2 research protocol is more
sophisticated.

## Interpretation

The old engine's key strength was not high absolute return.

Its defining property was **very low market exposure with controlled aggregate
drawdown**.

The weak points are also clear:
- huge number of probe/exit events;
- return concentration in a few technology winners;
- 16/39 sleeves were negative;
- substantial underperformance versus SPY;
- legacy raw formulas are exploratory and not OOS validated.

The replay therefore supports keeping FEB_XMA_v1 as a serious trading baseline
for future comparison, not promoting it directly to live trading.
