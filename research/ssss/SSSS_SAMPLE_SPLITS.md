# SSSS Research Sample Splits

Last updated: 2026-09-19

Purpose: preserve exact ticker membership for Discovery, OOS, Frozen OOS, and later independent validation cohorts.

This file is an audit record. A cohort appearing here does **not** automatically mean it belongs to the official 45-stock baseline.

## 1. Official baseline cohorts

| Research block | Role | Cohort | Tickers | Count | In official 45? |
|---|---|---|---|---:|---|
| Core lifecycle | Initial / Discovery | A | AAPL, MSFT, NVDA, JPM, XOM | 5 | Yes |
| Core lifecycle | Discovery / failure-heavy | B | ADBE, WFC, MRK, FDX, NEE | 5 | Yes |
| Core lifecycle | Validation | C | ORCL, WMT, GS, TMO, RTX | 5 | Yes |
| Relative-structure / OOS expansion | OOS 1 | O1 | AVGO, PEP, C, MDT, UNP | 5 | Yes |
| Relative-structure / OOS expansion | OOS 2 | O2 | IBM, CVX, HD, AMGN, MCD | 5 | Yes |
| Relative-structure / OOS expansion | OOS 3 | O3 | LLY, GE, V, TGT, COP | 5 | Yes |
| Relative-structure / OOS expansion | OOS 4 | O4 | QCOM, NKE, SCHW, GILD, CSX | 5 | Yes |
| Broad-universe extension | New cohort | N1 | META, AMD, CRM, TXN, AMZN | 5 | Yes |
| Failure-sell validation | Frozen OOS | OOS | COST, DE, SPGI, CI, DUK | 5 | Yes |

These 9 cohorts form the current official 45-stock baseline.

---

## 2. PriceNearWhite / Qualified GRB historical frozen OOS

These were used in earlier BUY-quality validation and should not be forgotten even when they overlap later cohorts.

| Research block | Role | Tickers | Count | Notes |
|---|---|---|---:|---|
| PriceNearWhite | Frozen OOS 6 | QCOM, MCD, TMO, RTX, SCHW | 5 | Exact frozen stock OOS set recorded in research |
| PriceNearWhite | Frozen OOS 7 | CRM, PM, CVS, UPS, DUK | 5 | Exact frozen stock OOS set recorded in research |
| GRB third OOS diagnostic | Third OOS | TMO, RTX, LMT, C, XLP | 5 | Included XLP ETF; 22 signals across 4 assets were reported in one diagnostic summary |

Important: these sets overlap the later official baseline but were separate experiments at the time.

---

## 3. Corrected lifecycle / BUY->SELL research cohorts

| Research block | Role | Cohort | Tickers |
|---|---|---|---|
| Lifecycle analysis | Initial cohort | A | AAPL, MSFT, NVDA, JPM, XOM |
| Lifecycle analysis | Failure-heavy cohort | B | ADBE, WFC, MRK, FDX, NEE |
| Lifecycle analysis | Later OOS/validation | C | ORCL, WMT, GS, TMO, RTX |

Key lifecycle labels:
- MATURE = Qualified BUY -> RED before renewed Green confirmation.
- FAIL = Qualified BUY -> Gray -> newly confirmed Green before any RED.
- UNRESOLVED = neither condition completed by sample end.

---

## 4. Relative-structure / WhiteCompact / path-score OOS sequence

| Role | Cohort | Tickers | Count |
|---|---|---|---:|
| OOS 1 | O1 | AVGO, PEP, C, MDT, UNP | 5 |
| OOS 2 | O2 | IBM, CVX, HD, AMGN, MCD | 5 |
| OOS 3 | O3 | LLY, GE, V, TGT, COP | 5 |
| OOS 4 | O4 | QCOM, NKE, SCHW, GILD, CSX | 5 |

These cohorts were used repeatedly for relative-own-history structure, path-score, MA30/A8, and later robustness checks.

---

## 5. Two-day multi-timeframe SSSS confirmation round

This round is especially important because the hard 2D confirmation rule was **rejected** after true frozen OOS reversal.

| Role | Tickers | Count | Result |
|---|---|---:|---|
| Discovery / failure-heavy | ADBE, WFC, MRK, FDX, NEE | 5 | Suggested possible higher-timeframe discrimination |
| OOS 1 | AVGO, PEP, C, MDT, UNP | 5 | Looked excellent; removed all 3 fails but lost 1 mature |
| **True Frozen OOS 2** | TSLA, KO, BK, CAT, CVS | 5 | Reversed; filtered out 4 real mature signals and invalidated hard MTF filter |

Frozen rule tested before OOS 2:

```text
MTF_PASS =
    2D effective state in {GRAY, RED}
    OR
    (2D effective state = GREEN AND 2D dsep > 0)
```

Official decision: **REJECT as BUY hard filter**.

---

## 6. Broad 50-stock BUY-quality-model round

At one stage, a 50-stock pool was assembled for grouped-stock and walk-forward validation.

### Prior 35-stock base

```text
A + B + C + O1 + O2 + O3 + O4
```

= 35 equities.

### Three added 5-stock blocks

| Block | Tickers | Count | In current official 45? |
|---|---|---:|---|
| Broad tech/consumer | META, AMD, CRM, TXN, AMZN | 5 | Yes, as N1 |
| Broad financial | BAC, MS, BLK, CME, USB | 5 | No |
| Broad health | JNJ, ABBV, PFE, UNH, ISRG | 5 | No |

Total pool in that round: 50 stocks.

The tested BUY Quality Model failed grouped-stock and walk-forward validation and was rejected. The 50-stock pool should therefore not be confused with the later official 45-stock baseline.

---

## 7. Failure SELL frozen OOS

| Role | Tickers | Count | Later status |
|---|---|---:|---|
| Frozen OOS | COST, DE, SPGI, CI, DUK | 5 | Later incorporated into official 45-stock baseline as cohort OOS |

This cohort was used when validating Gray failure behavior and early-exit candidates.

---

## 8. Mature SELL / RTE later independent OOS

These were added **after** the official 45-stock baseline and therefore are not part of the 59.2% baseline.

| Research block | Role | Tickers | Count | Status |
|---|---|---|---:|---|
| Mature SELL refinement | Frozen OOS 2 | NFLX, AXP, ABT, HON, SO | 5 | Tested |
| RTE refinement | Frozen OOS 3 | GOOG, MU, DIS, MA, BMY | 5 | Tested |
| RTE refinement | Planned Frozen OOS 4 | UPS, LIN, T, SBUX, PLD | 5 | Cohort defined; no final retained result in current research record |

Important: the last row is preserved as **planned/attempted**, not falsely marked as completed.

---

## 9. Crypto validation sets

Not part of the equity 45-stock baseline.

| Role | Assets |
|---|---|
| Crypto frozen validation | BTC, ETH, SOL, BNB |

BNB had no strict usable GRB in the available ~2-year window in the recorded analysis.

---

## 10. Known historical gaps — do not fabricate

Some very early aggregate summaries survive without a complete exact ticker-membership record in the current retained research context.

Known examples:
- "Discovery12" aggregate GRB diagnostic
- "Validation5" aggregate GRB diagnostic

The exact ticker composition of those earliest named aggregate sets is **not reconstructed here** because the retained context does not support a reliable exact list.

If the original conversation/export containing those lists is later recovered, update this file and the CSV ledger with the exact membership. Until then, do not infer or substitute tickers.

---

## 11. Sample-split governance rule

Going forward, every new research round must be **pre-registered and committed to `main` before any result is computed or inspected**.

Before the round starts, record:

1. experiment ID
2. research question / hypothesis
3. exact candidate rule or feature definition
4. Discovery tickers
5. OOS tickers
6. Frozen OOS tickers
7. date range for each cohort
8. whether a ticker overlaps prior research
9. whether the cohort is part of the official baseline
10. execution convention
11. primary evaluation / rejection criteria
12. status = PRE-REGISTERED

Required order:

```text
write Discovery / OOS / Frozen OOS lists
-> commit to main
-> run Discovery
-> freeze candidate
-> run OOS
-> if it survives, freeze again
-> open Frozen OOS
-> final decision
```

Changing any cohort after results are viewed requires a new experiment ID and a new pre-registration commit.

No future result should be called "Frozen OOS" unless both the cohort and the tested rule were frozen before viewing the outcome.

See `SSSS_RESEARCH_PROTOCOL.md` for the full governing protocol.
