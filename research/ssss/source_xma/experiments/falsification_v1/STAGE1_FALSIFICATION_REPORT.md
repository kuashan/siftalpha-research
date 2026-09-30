# Falsification v1 — Stage 1 Report

Status: PARTIAL / PRIMARY CONFLUENCE FALSIFICATION COMPLETE  
Date: 2026-09-28

This report covers:
- expanded sample,
- MFE/MAE,
- distribution quantiles,
- matched same-state controls,
- unconditional random controls,
- SPY / sector-relative returns,
- clustered bootstrap,
- concentration / leave-one-cluster diagnostics,
- post-event path shape.

It does NOT yet close:
- independent state-transition study,
- midpoint reclaim/loss study,
- HYS2 interaction regression,
- Below-VAL interaction on the expanded sample,
- Volume / Breadth / VIX interaction re-tests.

Those remain frozen next steps.

## 1. Expanded sample

Equities:
39-symbol frozen universe.

Crypto:
BTC / ETH / BNB / SOL.

Holdouts:

Validation A:
- equities 2020-01-02 to 2024-12-31
- crypto 2020-01-01 to 2024-12-31

Validation B:
- 2025-07-01 to 2025-12-31

Sealed:
2026 H1 remains unused.

## 2. Upper strict confluence — the Jan–Jun discovery does NOT generalize universally

Frozen event:
- exclusive XMA state = UP
- candle overlaps ZK1 and BS
- gap <= 0.25 ATR14
- 3-bar episode deduplication

### Equities — Validation A

n = 201

5-bar absolute:
- mean +0.34%
- median +0.60%
- positive rate 54.7%
- trimmed mean +0.21%

MFE / MAE over 5 bars:
- mean MFE +3.15%
- median MFE +2.09%
- mean MAE -3.06%
- median MAE -2.06%

Matched overextension/state control:
- mean excess +0.14%
- median excess +0.04%

Relative:
- SPY excess +0.38%
- sector ETF excess +0.31%

Cluster bootstrap intervals all include zero for the primary 5-bar effect.

Interpretation:
the large negative Jan–Jun 2025 discovery is NOT present in 2020–2024.
The event is not a universal top signal.

### Equities — Validation B

n = 28

5-bar absolute:
- mean -1.54%
- median -1.21%
- positive rate 32.1%
- trimmed mean -1.64%

MFE / MAE:
- mean MFE +2.50%
- median MFE +1.66%
- mean MAE -4.36%
- median MAE -2.84%

Matched-control excess:
- n=21 with valid same-state matches
- mean -3.52%
- median -2.78%

SPY excess:
- mean -1.63%
- median -2.21%

Sector excess:
- mean -1.16%
- median -1.78%

Leave-one-symbol and leave-one-month signs remain negative.

Matched-control cluster bootstrap:
- symbol 95% interval: about -7.08% to -0.57%
- symbol-month interval: about -6.61% to -0.47%

But:
- sector-relative cluster intervals still cross zero;
- only 28 events, below the frozen >=30 SUPPORT threshold;
- top symbol PLD contributes 25% of events;
- October 2025 contributes 35.7%.

Path shape:
- immediate decline: 6
- spike then decline: 13
- slow fade: 4
- continuation: 5

Interpretation:
the effect reappears in 2025 H2, but it is regime-dependent and temporally concentrated.

### Frozen falsification conclusion — upper event

The pre-registered universal hypothesis FAILS because Validation A and B do not have consistent direction.

Classification:
**REJECT AS UNIVERSAL TOP RULE**

Retain only as:
**REGIME-DEPENDENT CANDIDATE / OBSERVE**

It must not become an automatic sell or short rule.

## 3. Lower strict confluence — absolute rebound is mostly NOT geometry-specific

Frozen event:
- exclusive state = DOWN
- candle overlaps ZD1 and BD
- gap <= 0.50 ATR14
- episode deduplication

### Equities — Validation A

n = 134

Absolute:
- 5-bar mean +0.10%
- 10-bar mean +0.74%
- 20-bar mean +2.56%

This superficially resembles the Jan–Jun "delayed rebound" shape.

But matched controls overturn the interpretation:

Matched same-state / overextension excess:
- 5-bar -2.18%
- 10-bar remains negative
- 20-bar remains negative

Same-state random excess:
- 5-bar -1.53%

Unconditional random excess:
- 5-bar -0.87%

SPY excess:
+0.73%

Sector excess:
+0.69%

Interpretation:
the stock often rebounds in absolute terms, but comparable DOWN-state / similarly extended days rebound more.
The XMA lower-confluence geometry itself did not add positive timing information.

### Equities — Validation B

n = 12

Absolute:
- 5-bar mean -1.66%
- 10-bar mean -2.69%
- 20-bar mean -4.58%

SPY excess:
-2.75% at 5 bars

Sector excess:
-2.15% at 5 bars

This directly contradicts a universal delayed-bullish interpretation.

### Frozen falsification conclusion — lower event

Classification:
**REJECT AS STANDALONE BUY / REBOUND RULE**

The useful object is no longer:
"lower confluence => future rebound"

The remaining research question is:
whether lower confluence can serve as a context marker that becomes useful only after an independent state transition / midpoint confirmation / Volume Profile condition.

## 4. Crypto directly rejects the universal upper-top interpretation

Validation A upper strict confluence:
n = 41

5-bar:
- mean +2.95%
- median +0.52%
- positive rate 63.4%

Matched-control excess:
+0.87% mean

Crypto reference excess:
+1.51% mean

Validation B upper:
n = 5 only, unusable for confirmation, but mean is also positive.

Interpretation:
the same upper geometry is NOT a universal top condition in crypto.

Classification:
**DO NOT TRANSFER THE EQUITY TOP HYPOTHESIS TO CRYPTO**

## 5. MFE / MAE changes the interpretation

The upper event does not imply an immediate clean decline.

Even in 2025 H2 equities:
- 5-bar mean MFE is +2.50%
- 5-bar mean MAE is -4.36%
- 13/28 cases are spike-then-decline

Therefore:
even in the window where the event works bearishly, the path frequently rallies first.

This is another reason it must not be used as an immediate short trigger.

## 6. Extreme-value robustness

Validation A equity upper:
- largest absolute 5-bar event contributes ~3.3% of total absolute return movement
- top two ~5.7%

So the null result is not caused by one outlier.

Validation B equity upper:
- largest event ~17.6%
- top two ~34.8%

Thus the forward bearish sample is much more sensitive to individual events.

Lower Validation A:
large sample concentration is low by symbol/month; its matched-control underperformance is not a one-event artifact.

## 7. What Stage 1 falsified

### Rejected

1. "Upper strict confluence is generally a top."
2. "Lower strict confluence is generally a delayed buy/rebound signal."
3. "The 2025 discovery-window effects can be promoted directly to rules."

### Still alive

1. Upper strict confluence may be a **regime-dependent warning** in specific equity regimes.
2. Lower confluence may still be useful as a **context marker** when followed by independent confirmation.
3. Midpoint / state-transition logic may carry more information than raw confluence.
4. Below-VAL may still be incremental, but must be re-tested on expanded holdouts.
5. HYS2 may still have interaction value, but not by simple subgroup means.

## 8. Next frozen tests

Next Stage 2 must complete, without changing the confluence thresholds:

1. independent state-transition event study:
   DOWN->RANGE, RANGE->UP, UP->RANGE, RANGE->DOWN, DOWN->UP, UP->DOWN;

2. analytic midpoint event study:
   FAST_MID_ANALYTIC reclaim/loss independently and conditional on confluence;

3. time-to-confirm survival:
   3 / 5 / 10 / 20 / 40 bars;

4. lower penetration decomposition:
   shallow vs deep-reclaim vs deep-no-reclaim;

5. Below-VAL interaction on the expanded holdout;

6. HYS2 2x2 logistic interaction;

7. Volume capitulation interaction;

8. multiple-testing adjustment after the registered family is complete.

## 9. Research governance conclusion

The falsification discipline materially changed the interpretation.

The strongest Jan–Jun finding did not survive as a universal rule.

This is a successful falsification outcome, not a research failure.

No position sizing, portfolio logic, or short strategy is introduced.
