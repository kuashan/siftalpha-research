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


---

## 12. E030 — Progress → Controlled Pullback → Re-acceleration ADD

Pre-registered before any E030 result was inspected.

| Role | Cohort | Tickers | Count | Prior SSSS exposure | Official 45? | Status |
|---|---|---|---:|---|---|---|
| Discovery | E030_D | AAPL, MSFT, NVDA, JPM, XOM, ADBE, WFC, MRK, FDX, NEE, ORCL, WMT, GS, TMO, RTX, AVGO, PEP, C, MDT, UNP, IBM, CVX, HD, AMGN, MCD | 25 | Yes | Yes | COMPLETED — REJECTED |
| OOS | E030_OOS | LLY, GE, V, TGT, COP, QCOM, NKE, SCHW, GILD, CSX | 10 | Yes | Yes | NOT OPENED |
| Frozen OOS | E030_FOOS | LOW, BA, PGR, ADP, MDLZ | 5 | No appearance in retained split ledger; unknown earliest aggregate membership cannot be ruled out | No | NOT OPENED |

Fixed evaluation window: 2024-09-01 through 2026-09-18. Warm-up data may begin 2024-01-01.

The Frozen OOS cohort must not be queried for E030 outcomes until one exact rule survives OOS and is frozen.

Full rule family, metrics, and pass/fail criteria are frozen in `preregistrations/E030.md`.


E030 status update:
- Discovery completed and failed the pre-registered eligibility gate.
- OOS was not opened.
- Frozen OOS was not opened.
- The Frozen OOS tickers remain unqueried for E030 outcomes.


---

## 13. E031 — Structural Confirmation ADD

Pre-registered before any E031 result was inspected.

| Role | Cohort | Tickers | Count | Prior SSSS exposure | Official 45? | Status |
|---|---|---|---:|---|---|---|
| Discovery | E031_D | AAPL, MSFT, NVDA, JPM, XOM, ADBE, WFC, MRK, FDX, NEE, ORCL, WMT, GS, TMO, RTX, AVGO, PEP, C, MDT, UNP, IBM, CVX, HD, AMGN, MCD, LLY, GE, V, TGT, COP | 30 | Yes | Yes | COMPLETED — REJECTED |
| OOS | E031_OOS | QCOM, NKE, SCHW, GILD, CSX, META, AMD, CRM, TXN, AMZN | 10 | Yes | Yes | NOT OPENED |
| Frozen OOS | E031_FOOS | LOW, BA, PGR, ADP, MDLZ | 5 | No appearance in retained pre-E030 split ledger; earliest unknown aggregate membership cannot be ruled out | No | NOT OPENED |

Fixed evaluation window: 2024-09-01 through 2026-09-18.

E031 tests StructuralSep = (FastMid - WhiteMid) / WhiteWidth at fixed 0.50 / 1.00 / 1.50 crossings with two confirmation modes.

Full rule family and gates are frozen in `preregistrations/E031.md`.


E031 execution checkpoint:
- 10/30 Discovery tickers were retrieved successfully.
- Market-data retrieval then stopped because the provider returned an explicit RATE_LIMIT error.
- No Discovery eligibility decision has been made.
- OOS remains unopened.
- Frozen OOS remains unopened.
- No cohort substitution or rule change is permitted.


E031 final status:
- all 30 Discovery tickers were eventually retrieved despite intermittent provider rate limits;
- every pre-registered variant had negative median ADD-leg return;
- no variant passed Discovery eligibility;
- OOS was not opened;
- Frozen OOS was not opened.


---

## 14. E032 — ADD Opportunity Map

Pre-registered before any E032 outcome was inspected.

| Role | Cohort | Tickers | Count | Status |
|---|---|---|---:|---|
| Discovery | E032_D | AAPL, MSFT, NVDA, JPM, XOM, ADBE, WFC, MRK, FDX, NEE, ORCL, WMT, GS, TMO, RTX, AVGO, PEP, C, MDT, UNP, IBM, CVX, HD, AMGN, MCD, LLY, GE, V, TGT, COP | 30 | COMPLETED — CANDIDATE ZONES FOUND |
| Reserved OOS | E032_OOS | QCOM, NKE, SCHW, GILD, CSX, META, AMD, CRM, TXN, AMZN | 10 | NOT OPENED |
| Reserved Frozen OOS | E032_FOOS | LOW, BA, PGR, ADP, MDLZ | 5 | NOT OPENED |

E032 is Discovery-only by design.

It maps hypothetical next-open ADD economics across five fixed causal maps and cannot validate an ADD trigger.

Any rule inspired by the map requires a new experiment before OOS.

Full definition:
`preregistrations/E032.md`


E032 final status:
- all 30 Discovery stocks completed from Massive;
- 40 resolved trades produced 3332 all-bar opportunity observations;
- 15 pre-defined cells passed the candidate-zone gate;
- OOS was not opened;
- Frozen OOS was not opened;
- no ADD trigger was accepted.


---

## 15. E033 — Selective Early Second Entry

Pre-registered before any E033 result was viewed.

| Role | Cohort | Tickers | Count | Status |
|---|---|---|---:|---|
| Discovery | E033_D | AAPL, MSFT, NVDA, JPM, XOM, ADBE, WFC, MRK, FDX, NEE, ORCL, WMT, GS, TMO, RTX, AVGO, PEP, C, MDT, UNP, IBM, CVX, HD, AMGN, MCD, LLY, GE, V, TGT, COP | 30 | COMPLETED — REJECTED |
| OOS | E033_OOS | QCOM, NKE, SCHW, GILD, CSX, META, AMD, CRM, TXN, AMZN | 10 | NOT OPENED |
| Frozen OOS | E033_FOOS | LOW, BA, PGR, ADP, MDLZ | 5 | NOT OPENED |

E033 compares four exact selective early-second-entry rules against:
- BASE_1U
- IMMEDIATE_2U
- NEXTDAY_2ND

Full definition:
`preregistrations/E033.md`


E033 final status:
- 30/30 Discovery stocks completed;
- all four candidates had positive ADD-leg mean and median;
- none passed Mature-vs-Failure path-selectivity requirements;
- OOS was not opened;
- Frozen OOS was not opened;
- no ADD trigger was accepted.


---

## 16. E034 — Orthogonal Feature Diagnostic

Duplication audit completed before pre-registration.

Equity Discovery:
AAPL, MSFT, NVDA, JPM, XOM,
ADBE, WFC, MRK, FDX, NEE,
ORCL, WMT, GS, TMO, RTX,
AVGO, PEP, C, MDT, UNP,
IBM, CVX, HD, AMGN, MCD,
LLY, GE, V, TGT, COP

Equity OOS:
QCOM, NKE, SCHW, GILD, CSX, META, AMD, CRM, TXN, AMZN

Equity Frozen OOS:
LOW, BA, PGR, ADP, MDLZ

Crypto Discovery:
BTC, ETH, SOL, BNB
using Massive composite USD daily tickers.

Crypto OOS reserved:
XRP, ADA, DOGE, TRX

Crypto Frozen OOS reserved:
LINK, AVAX, LTC, BCH

E034 tests only:
- ER10
- CHOP14
- CMF20
- OBVImpulse10

Snapshots:
- Qualified GRB signal close
- original OPEN execution-day close

E034 is Discovery-only.
No equity or crypto holdout may be queried.

Full definition:
`preregistrations/E034.md`


E034 final status:
- equity Discovery: 40 resolved lifecycles, 31 Mature / 9 Failure;
- no ER10 / CHOP14 / CMF20 / OBVImpulse10 snapshot passed the pre-registered diagnostic gate;
- crypto Discovery: 7 resolved lifecycles, 4 Mature / 3 Failure;
- crypto diagnostics were too sparse for formal interpretation;
- all equity and crypto holdouts remained unopened.


---

## 17. E035 — BTC 15m Dynamic Position Engine Discovery Map

Duplication audit completed before pre-registration.

E035 is NEW at the 15-minute timeframe and PARTIAL_OVERLAP at the action-architecture level.

Temporal split:

| Role | Period | Status |
|---|---|---|
| Discovery | BTC / X:BTCUSD / 2024-09-18 through 2025-08-31 | PRE-REGISTERED |
| OOS | BTC / X:BTCUSD / 2025-09-01 through 2026-03-31 | RESERVED — DO NOT OPEN |
| Frozen OOS | BTC / X:BTCUSD / 2026-04-01 through 2026-09-17 | RESERVED — DO NOT OPEN |

Cross-asset 15m holdouts:
ETH, SOL, BNB — DO NOT OPEN in E035.

E035 Phase A freezes exactly three 15m structural baselines:
- B0 LEGACY_COUNT_REFERENCE
- B1 NATIVE_12H
- B2 NATIVE_24H

Only if one baseline passes the pre-registered viability gate may Phase B map:
- OPEN
- ADD
- REDUCE
- RE-ADD
- CLOSE

E035 is Discovery-only and cannot validate a production action.

Full definition:
`preregistrations/E035.md`


E035 final status:
- Phase A completed;
- no B0/B1/B2 baseline passed eligibility;
- B2 was strongest economically but had negative base-friction median return;
- Phase B dynamic action maps were not opened;
- BTC OOS / Frozen OOS remained unopened;
- ETH / SOL / BNB 15m remained unopened.


---

## 18. E036 — BTC 15m Multi-Open Dynamic Engine Repair Map

Repository duplication audit re-run after E035 closure.

Discovery:
same immutable BTC 15m snapshot already seen in E035.

B2 NATIVE_24H is fixed as a diagnostic structural reference, not a validated baseline.

Exactly four OPEN modes:
- O1 GRB
- O2 FAST_BREAKOUT
- O3 GREEN_TRANSITION
- O4 FASTMID_RECLAIM

At least two modes must independently pass before a Multi-Open Reference can be built.

Only if the Multi-Open Reference passes may ADD / REDUCE / RE-ADD / CLOSE maps be opened.

BTC OOS / Frozen OOS and ETH / SOL / BNB 15m remain untouched.

Full definition:
`preregistrations/E036.md`


---

## 19. E037 — BTC 15m Starter-to-Dynamic Action Map

Repository duplication audit re-run after E036.

Fixed Discovery starter:
GREEN_TRANSITION.

GRB / FAST_BREAKOUT / FASTMID_RECLAIM are no longer OPEN competitors in this round.
They are post-entry ADD candidates only.

E037 maps:
- discrete ADD evidence
- ADD opportunity zones
- REDUCE zones
- RE-ADD recovery zones
- CLOSE zones

Discovery only.

BTC OOS / Frozen OOS and ETH / SOL / BNB 15m remain unopened.

Full definition:
`preregistrations/E037.md`
