# Falsification v1 — Crypto Robustness Closure

Status: COMPLETE / CRYPTO REPORTED SEPARATELY  
Date: 2026-09-28

## Governance

Crypto is not pooled with equities.

No stock+crypto combined mean, model, or trading rule is produced.

The purpose of this report is robustness and concentration, not promotion.

## Upper strict confluence — Validation A

n = 41

### 20-bar raw return robustness

- mean: 22.55%
- median: 5.18%
- 10% trimmed mean: 8.68%
- 10% winsorized mean: 11.08%
- drop largest winner: 11.27%
- drop largest 2 winners: 9.30%
- drop largest 5 winners: 5.00%

Absolute-movement contribution:
- largest event: 39.77%
- largest 2: 47.18%
- largest 5: 62.52%

Largest event:
- symbol: BNB
- date: 2021-02-01
- 20-bar return: 473.56%
- prior-20 return at event: 34.57%
- dev20: 20.40%
- ATR/close: 6.82%

The same event returned roughly +41.5% at 5 bars, +141.0% at 10 bars and +473.6% at 20 bars.

This is a major concentration warning.

### Symbol decomposition — 20 bars

| Symbol | n | Mean 20-bar |
| --- | ---: | ---: |
| BTC | 8 | 4.66% |
| ETH | 14 | 7.84% |
| BNB | 11 | 44.91% |
| SOL | 8 | 35.43% |

Leave-one-symbol-out raw 20-bar mean:
- remove BTC: 26.88%
- remove ETH: 30.17%
- remove BNB: 14.35%
- remove SOL: 19.42%

The positive raw sign survives leave-one-symbol-out, but magnitude is heavily influenced by BNB/SOL and the BNB 2021-02-01 extreme event.

### Matched control

20-bar matched-excess mean:
12.72%

Leave-one-symbol-out matched excess:
- remove BTC: 16.53%
- remove ETH: 19.22%
- remove BNB: 2.58%
- remove SOL: 12.82%

With only four crypto symbols, symbol-cluster inference remains structurally weak.

## Lower strict confluence — Validation A

n = 37

Raw:
- 10-bar mean 2.29%, median 2.95%
- 20-bar mean 7.66%, median 5.20%

But matched excess:
- 10-bar -6.17%
- 20-bar -9.37%

Therefore positive raw rebound does not establish incremental lower-confluence edge in crypto either.

## Validation B

Upper n = 5
Lower n = 7

Both are below the frozen minimum for validation interpretation.

They remain descriptive only.

## Decision

1. Crypto and equities remain fully separated.
2. Upper crypto raw means are extreme-value sensitive and not treated as evidence for an equity-like rule.
3. The Upper 2020–2024 positive sign directly contradicts a universal "upper confluence = top" interpretation.
4. Lower crypto raw rebound is not incremental versus matched controls.
5. No crypto trading rule is promoted from Falsification v1.
