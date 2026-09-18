# SSSS Official 45-Stock Baseline Universe

Last updated: 2026-09-19

This file freezes the exact 45-equity universe used by the corrected official baseline:

- 96 independent Qualified BUY lifecycles
- 88 resolved lifecycles
- 69 Mature
- 19 Fail
- 71 completed BUY->SELL trades
- 59.2% win rate
- +8.84% average net return per completed trade

Important: this is the **official 45-stock baseline universe**. Other historical discovery/OOS cohorts are documented separately in `SSSS_SAMPLE_SPLITS.md`.

## Cohort composition

| Cohort | Tickers | Count | Role in current 45-stock baseline |
|---|---|---:|---|
| A | AAPL, MSFT, NVDA, JPM, XOM | 5 | Core / initial lifecycle cohort |
| B | ADBE, WFC, MRK, FDX, NEE | 5 | Failure-heavy discovery cohort |
| C | ORCL, WMT, GS, TMO, RTX | 5 | Later validation cohort |
| O1 | AVGO, PEP, C, MDT, UNP | 5 | OOS cohort 1 |
| O2 | IBM, CVX, HD, AMGN, MCD | 5 | OOS cohort 2 |
| O3 | LLY, GE, V, TGT, COP | 5 | OOS cohort 3 |
| O4 | QCOM, NKE, SCHW, GILD, CSX | 5 | OOS cohort 4 |
| N1 | META, AMD, CRM, TXN, AMZN | 5 | Broad-universe extension cohort |
| OOS | COST, DE, SPGI, CI, DUK | 5 | Frozen later OOS cohort, subsequently included in official baseline |

Total: **45 unique equities**.

## Flat ticker list

```text
AAPL
MSFT
NVDA
JPM
XOM
ADBE
WFC
MRK
FDX
NEE
ORCL
WMT
GS
TMO
RTX
AVGO
PEP
C
MDT
UNP
IBM
CVX
HD
AMGN
MCD
LLY
GE
V
TGT
COP
QCOM
NKE
SCHW
GILD
CSX
META
AMD
CRM
TXN
AMZN
COST
DE
SPGI
CI
DUK
```

## Sorted unique ticker list

```text
AAPL
ADBE
AMD
AMGN
AMZN
AVGO
C
CI
COP
COST
CRM
CSX
CVX
DE
DUK
FDX
GE
GILD
GS
HD
IBM
JPM
LLY
MCD
MDT
META
MRK
MSFT
NEE
NKE
NVDA
ORCL
PEP
QCOM
RTX
SCHW
SPGI
TGT
TMO
TXN
UNP
V
WFC
WMT
XOM
```

## Baseline membership rule

A stock is part of the official baseline only if it appears in the 45-ticker list above.

Do not silently add historical research tickers such as TSLA, KO, BK, CAT, CVS, NFLX, AXP, HON, GOOG, MU, etc. to the official 45-stock baseline. Those belong to separate historical OOS/frozen-OOS experiments and are documented in `SSSS_SAMPLE_SPLITS.md`.
