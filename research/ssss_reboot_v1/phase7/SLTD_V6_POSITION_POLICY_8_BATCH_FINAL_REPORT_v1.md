# SLTD V6 Position Policy — 8-Batch Final Report v1

Status: **STOCK POSITION STUDY COMPLETE**

Crypto Batch 9: **CANCELLED BY USER — NOT PART OF THE FINAL POSITION-POLICY EVIDENCE**

Study: `SLTD_V6_POSITION_POLICY_STUDY_V1`

Formal stock window: **2020-01-02 through 2026-09-30**

Universe: **79 mainstream U.S. stocks across 8 batches**

Execution: **signal confirmed at close -> next available open**

Representation: **FIRST_OBSERVED causal XMA reconstruction**

Friction: **5 bps baseline; 10 bps stress**

Long/cash only; no leverage; no short selling.

---

## 1. Executive conclusion

The eight completed stock batches support one global position-execution policy:

`I25_AADD_25_TO_CAP_S25_WHOLD_RNO_CHANGE_MIXED`

Operational meaning:

- first valid BUY while flat -> target **25%** position;
- later valid BUY while already long -> add **25 percentage points**, capped at 100%;
- valid SELL -> reduce **25% of the current position** (multiplicative reduction, not minus 25 percentage points);
- WAIT while long -> **hold**;
- if more than one action class conflicts on the same bar -> **no position change**.

The policy was ranked first using Discovery Batches 1-4, frozen before Validation, and then passed every preregistered validation gate on Batches 5-8.

Final stock-policy status:

`SLTD_V6_STOCK_POLICY = PROMOTED`

The 15-rule SLTD V6 signal taxonomy itself was not retuned by the position study.

---

## 2. Study structure

### Discovery — Batches 1-4

Stocks: **39**

Purpose:
- evaluate the frozen 1,152-policy Stage A grid;
- merge the four discovery batches;
- rank using the preregistered lexicographic objective;
- remove only exact discovery-observed outcome duplicates before filling the shortlist;
- freeze Primary + four Backups before any Validation data are used.

Raw policies: **1,152**

Distinct discovery-observed outcome groups after exact deduplication: **688**

Frozen Primary discovery rank: **1**

### Validation — Batches 5-8

Stocks: **40 new stocks**

Purpose:
- test only the frozen five candidates;
- no parameter retuning;
- no validation reranking;
- promote the first frozen candidate that passes all preregistered gates.

This preserves the Discovery / Validation boundary.

---

## 3. Promoted Primary across all eight stock batches

The table below follows the final promoted Primary policy in every batch. Batches 1-4 are Discovery data; Batches 5-8 are Validation data.

| Batch | Stage | Stocks | Total Return | CAGR | MaxDD | Calmar | 10bps Calmar | Time in Market |
|---|---|---|---:|---:|---:|---:|---:|---:|
| B1 | Discovery | AAPL MSFT NVDA AMD AVGO ORCL INTC QCOM MU GOOGL | +805.98% | 38.66% | -41.32% | 0.935 | 0.934 | 97.92% |
| B2 | Discovery | META NFLX AMZN TSLA HD MCD WMT COST PG KO | +114.99% | 12.02% | -33.42% | 0.360 | 0.358 | 98.47% |
| B3 | Discovery | PEP ABT LLY UNH JNJ TMO JPM BAC GS V | +101.44% | 10.94% | -19.11% | 0.573 | 0.569 | 99.04% |
| B4 | Discovery | MA CAT BA GE XOM CVX LIN NEE PLD | +131.93% | 13.29% | -20.17% | 0.659 | 0.655 | 96.49% |
| B5 | Validation | IBM CSCO CRM ADBE TXN DIS NKE SBUX TGT LOW | +31.03% | 4.09% | -33.18% | 0.123 | 0.122 | 97.41% |
| B6 | Validation | MRK PFE ABBV AMGN GILD C MS BLK COP UPS | +78.15% | 8.94% | -15.77% | 0.567 | 0.561 | 98.29% |
| B7 | Validation | ACN NOW INTU AMAT LRCX BKNG TJX CMG ROST MAR | +189.87% | 17.10% | -34.91% | 0.490 | 0.488 | 98.15% |
| B8 | Validation | DHR SYK MDT BMY ISRG SCHW SPGI DE HON RTX | +61.30% | 7.35% | -22.74% | 0.323 | 0.320 | 98.99% |

Descriptive eight-batch medians for the promoted Primary:

- median Calmar: **0.528**
- median CAGR: **11.48%**
- median 10bps Calmar: **0.525**
- median MaxDD: **-27.96%**
- median Time in Market: **98.22%**
- median batch turnover metric: **6.17**
- all eight batch portfolios had positive total return, positive CAGR, and positive Calmar.

Important interpretation boundary: the eight-batch descriptive medians mix Discovery and Validation and therefore are **not** a new selection criterion. Formal promotion is based on the frozen Discovery ranking plus the preregistered Validation gates.

---

## 4. Discovery result

For the promoted Primary on Batches 1-4:

- median Discovery Calmar: **0.616**
- worst Discovery Calmar: **0.360**
- median Discovery CAGR: **12.65%**
- median Discovery MaxDD magnitude: **26.80%**
- median 10bps Discovery Calmar: **0.612**

The four Discovery batches did not have the same batch-local optimum. That is important: the final policy was not selected because it happened to win one particular batch. It emerged from the four-batch merged ranking.

The Discovery result strongly favored:

1. **25% initial entry**, rather than full initial exposure;
2. **incremental +25 percentage-point BUY additions**;
3. holding through WAIT rather than mechanically trimming;
4. a relatively gentle SELL reduction in the final Primary.

---

## 5. Validation result

The Primary's four independent Validation batches produced:

- positive Calmar batches: **4/4**
- median Validation Calmar: **0.406**
- median Validation CAGR: **8.14%**
- median 10bps Validation Calmar: **0.404**
- worst Validation MaxDD: **-34.91%**

Every preregistered gate passed:

- at least 3 of 4 validation batches Calmar > 0: **PASS**
- median validation Calmar > 0: **PASS**
- median validation CAGR > 0: **PASS**
- median 10bps validation Calmar > 0: **PASS**
- no validation batch MaxDD worse than -60%: **PASS**

The weakest validation environment was B5:
- CAGR **4.09%**
- Calmar **0.123**
- MaxDD **-33.18%**

B5 matters because it shows that the policy is not uniformly strong across every stock group. It remained positive, but the edge can become much weaker depending on the cross-section.

---

## 6. What the Backup policies tell us

All five frozen candidates passed the admission gates. Validation therefore did not falsify any of them, but protocol requires choosing the first passing policy in frozen Discovery order.

| Frozen candidate | Median Validation Calmar | Median Validation CAGR | Median 10bps Calmar | Worst Validation MaxDD |
|---|---:|---:|---:|---:|
| PRIMARY — SELL 25%, HOLD, NO_CHANGE_MIXED | **0.406** | **8.14%** | **0.404** | -34.91% |
| BACKUP 1 — SELL 25%, HOLD, SELL_FIRST | 0.406 | 8.14% | 0.404 | -34.91% |
| BACKUP 2 — SELL 75%, HOLD, SELL_FIRST | 0.262 | 4.48% | 0.256 | -26.29% |
| BACKUP 3 — SELL 75%, HOLD, NO_CHANGE_MIXED | 0.262 | 4.49% | 0.256 | -26.29% |
| BACKUP 4 — SELL 75%, TRIM_25, SELL_FIRST | 0.232 | 3.80% | 0.226 | **-24.49%** |

The main trade-off is clear.

A more aggressive SELL reduction (75%) reduced drawdown, but it also materially reduced CAGR and Calmar in Validation. The promoted 25%-reduction policy accepts more drawdown in exchange for retaining exposure to continued trends.

Mixed-action resolution had very little observed economic effect: Primary and Backup 1 were almost identical in Validation. This suggests same-bar cross-class conflicts were either uncommon or economically small in the tested sample. It should therefore not be treated as the main source of the strategy's performance.

WAIT trimming also reduced drawdown somewhat, but at a larger cost to return and Calmar. The current evidence therefore supports WAIT=HOLD for this global policy.

---

## 7. Most important quantitative findings

### A. Staged entry is the strongest stable structural result

The frozen top five distinct candidates all begin with **25% initial exposure** and then add **25 percentage points** on later BUY signals.

This is stronger evidence than any single SELL variation because it survived both the Discovery ranking and the Validation shortlist.

The practical meaning is that SLTD V6 should not treat a first BUY signal as an instruction to commit 100% immediately.

### B. Gentle exits preserve trend participation

The promoted policy reduces only **25% of current exposure** per SELL event.

This is intentionally slow. For example, if position exposure is 100%, sequential SELL actions without intervening BUYs produce approximately:

100% -> 75% -> 56.25% -> 42.19% -> 31.64% ...

This differs materially from subtracting 25 percentage points each time.

The data show why this matters: the 75%-reduction variants controlled drawdown better, but their Validation median CAGR fell from about **8.14%** to about **4.5%**, while median Calmar fell from about **0.406** to about **0.262**.

### C. Friction sensitivity is low at the tested levels

Primary Validation median Calmar:
- 5 bps: **0.406**
- 10 bps: **0.404**

The result is therefore not being held up by a tiny 5-bps transaction-cost assumption.

### D. Exposure is very high

The promoted policy's median Time in Market across all eight batches is **98.22%**.

This is a critical characteristic. The strategy is not a low-exposure market-timing system. Once the staged BUY process establishes a position, the gentle SELL behavior often leaves at least some long exposure in place for long periods.

Therefore the policy's risk should be understood as **dynamic long exposure management**, not frequent movement between fully invested and fully cash.

### E. Cross-batch dispersion is real

Calmar ranged from:
- **0.123** in B5
to
- **0.935** in B1.

This dispersion is large. The policy is robust in the sense that every batch remained positive, but its realized strength varies substantially by stock group and market path.

---

## 8. What is formally retained

The following position policy is retained for SLTD V6 stock research:

**BUY**
- flat + valid BUY -> 25%
- already long + later valid BUY -> +25 percentage points
- cap at 100%

**SELL**
- reduce 25% of current exposure per SELL event

**WAIT**
- hold current exposure
- while flat, WAIT blocks new entry on that bar

**Mixed action**
- more than one action class on the same bar -> no position change

**Execution**
- signal confirmed at close
- execute at next available open

**Risk / market constraints**
- long/cash only
- no leverage
- no shorting

The underlying 15 SLTD V6 BUY/HOLD/WAIT/SELL rule definitions remain frozen and unchanged.

---

## 9. What is not established by this study

This study does **not** establish that:

- the same position policy is optimal for crypto;
- the same policy is optimal on intraday bars;
- a -34.91% observed Validation drawdown is an upper bound on future drawdown;
- 98%+ Time in Market is suitable for every deployment objective;
- the policy is optimal under materially larger slippage, taxes, borrow costs, liquidity constraints, or portfolio concentration constraints;
- SELL 25% is universally superior to SELL 75% for every risk preference.

The study establishes a robust global stock execution policy under the frozen protocol and objective, not a universal trading optimum.

---

## 10. Batch 9 cancellation and study closure

Batch 9 crypto transfer testing was attempted twice, but both attempts failed before any crypto OHLCV was accepted because Binance public endpoints returned geographic-access HTTP 451 errors from GitHub-hosted runners.

Those failures are **infrastructure failures, not strategy results**.

At the user's instruction, Batch 9 is now cancelled. It contributes no positive or negative evidence to the final stock position-policy conclusion.

The automatic Batch 9 GitHub Actions workflow has been removed so it will not run again accidentally.

Final scope of evidence:

- **8 completed stock batches**
- **79 stocks**
- **39-stock Discovery**
- **40-stock independent Validation**
- **Primary promoted**
- **Crypto transfer test cancelled / excluded**

`SLTD_V6_POSITION_POLICY_8_BATCH_STOCK_STUDY = COMPLETE`
