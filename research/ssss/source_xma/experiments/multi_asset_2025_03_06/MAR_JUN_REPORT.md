# March–June 2025 Multi-Asset Source-XMA Research Report

Status: DISCOVERY / EXPLORATORY  
Protocol commit: `bd58431a8214c76549e624c49422c9a9850e6851`

## Execution model changed

This run uses `SAME_BAR_CLOSE_PROXY_V2`.

Signal and action belong to the same current daily bar.

The fill proxy is:
- same bar close
- plus 5 bps adverse slippage

This implements the new research principle:
**do not mechanically wait one more K bar after the current K has already satisfied the trading rule.**

Important limitation:
daily OHLCV cannot identify the exact intraday minute when all rules first became true.

Therefore this is a same-bar execution proxy, not a minute-level first-confirm replay.

## Capital

Each symbol starts with a nominal $10,000 sleeve.

Capital is continuous from March through June.

No monthly reset.

This remains signal research, not one shared $10,000 cross-asset portfolio.

## Universe

11 equities:
ABT, AAPL, AMZN, ORCL, INTC, MSFT, NVDA, GOOGL, META, JPM, XOM.

4 crypto:
BTC, ETH, BNB, SOL.

ARM remains pending because a verified daily dataset was not forced into the run.

## Main cross-asset result

### Equities

| Variant | Mean | Median | Positive | Worst | Best | Mean DD |
|---|---:|---:|---:|---:|---:|---:|
| XMA_ONLY | +0.485% | +0.197% | 6/11 | -5.232% | +15.965% | -2.708% |
| XMA_HYS2 | +0.380% | +0.197% | 6/11 | -5.889% | +15.474% | -2.972% |
| XMA_FIVEGZ | +1.101% | +0.159% | 6/11 | -8.170% | +25.449% | -2.799% |
| XMA_HYS2_FIVEGZ | +0.245% | -0.931% | 4/11 | -9.268% | +24.920% | -3.974% |

### Crypto

| Variant | Mean | Median | Positive | Worst | Best | Mean DD |
|---|---:|---:|---:|---:|---:|---:|
| XMA_ONLY | -2.996% | -1.824% | 2/4 | -9.687% | +1.349% | -6.893% |
| XMA_HYS2 | -2.928% | -1.867% | 2/4 | -9.687% | +1.709% | -7.046% |
| XMA_FIVEGZ | -3.193% | -2.331% | 2/4 | -10.647% | +2.537% | -7.699% |
| XMA_HYS2_FIVEGZ | -4.462% | -3.164% | 1/4 | -13.832% | +2.312% | -8.649% |

## Important finding 1 — stock and crypto should not share one auxiliary stack

For equities, FIVEGZ color-state sizing produced the highest mean return.

But this mean is strongly influenced by ORCL:
- ORCL XMA_ONLY: +15.97%
- ORCL XMA_FIVEGZ: +25.45%

After removing the single best and single worst equity, the trimmed mean is still negative:
- XMA_ONLY ≈ -0.60%
- XMA_FIVEGZ ≈ -0.57%

Therefore:
**FIVEGZ shows some equity value, but the evidence is not robust enough to call it a universally superior strategy.**

For crypto, FIVEGZ made the aggregate result worse.

This directly supports the user's warning that the built-in 0/1/2 market branches are not necessarily correctly calibrated.

Current conclusion:
- equities: FIVEGZ raw color state remains a useful candidate
- crypto: FIVEGZ SCTYPE=2 is HARMFUL in this window and should not be blindly adopted

## Important finding 2 — HYS2 is selective, not universal

For crypto:
- XMA_ONLY mean: -2.996%
- XMA_HYS2 mean: -2.928%

This is only a small improvement.

At symbol level:
- SOL improved from +1.35% to +1.71%
- BTC improved slightly
- BNB worsened slightly
- ETH unchanged

Therefore HYS2 may help some low-side reversals but does not solve the crypto problem.

## Important finding 3 — the February Transition Override was too aggressive

The frozen rule allowed:

```text
BEAR regime
+ HYS2 resonance
+ FIVEGZ score >= +6
+ FIVEGZ daily jump >= +6
+ RVOL >= 1.5
=> small counter-regime probe
```

In practice the sizing modifiers could expand the nominal 15% probe to 40%.

On 2025-04-09 this fired simultaneously in:
- AMZN
- MSFT
- NVDA
- GOOGL
- META
and in crypto examples including ETH/SOL.

This looks like a broad market rebound signature rather than a symbol-specific high-confidence reversal.

It helped MSFT, but the combined variant underperformed in AMZN/NVDA/GOOGL/META.

Therefore:
**Transition Override itself is worth keeping as a concept, but 40% is too large for first confirmation.**

Candidate next rule:
- first override seed = 10–15% max
- no auxiliary boost on the first override bar
- only add if the next bar preserves internal improvement

## Important finding 4 — cooldown helped, but repeated probes still exist

The 3-bar cooldown reduced immediate re-entry loops.

But failed-probe counts remain high:
- stocks XMA_ONLY: 25 failed probes
- crypto XMA_ONLY: 12 failed probes

Therefore lower-extreme alone remains too permissive.

Candidate next rule:
- after failed probe, require **state improvement**, not just time expiration.

Possible re-arm condition:
- FIVEGZ total score improves by >= 3 from the failed-exit state,
OR
- HYS2 resonance,
OR
- XMA momentum transitions to BOTH_UP.

## Important finding 5 — no automatic shorting remains correct

Bearish states often appeared during volatile reversals.

Nothing in this window justifies:
`sell signal => immediately short`.

The model continues to separate:
- reduce
- exit
- remain flat
- short

Short remains disabled.

## Symbol observations

### ORCL
The strongest equity case.
FIVEGZ reinforced a May-30 breakout and materially increased the research sleeve outcome.

### JPM
Consistent positive contribution from XMA + FIVEGZ.

### ABT
March–June was a negative case under all four variants.
This is important because the January success did not generalize automatically.

### INTC
The February missed-opportunity lesson did not translate into a robust March–June rule.
All variants were negative, and FIVEGZ worsened results.

### BTC / ETH
The crypto stack needs separate work.
The existing XMA/FIVEGZ/HYS2 combinations do not yet produce acceptable robustness.

### BNB / SOL
These were the stronger crypto cases, but still with large drawdown volatility.

## Provisional architecture after June

Do NOT use one universal combined stack.

### Equities candidate

```text
Source-XMA = timing / structure
FIVEGZ color transitions = selective sizing/risk
HYS2 = optional low-side confirmation only
```

### Crypto candidate

```text
Source-XMA = keep as baseline
HYS2 = selective low-side candidate
FIVEGZ SCTYPE=2 = do not promote
```

The next crypto research should compare:
- SCTYPE=2 source branch
- SCTYPE=1-like thresholds
- independently normalized volatility/volume thresholds

without rewriting March–June results.
