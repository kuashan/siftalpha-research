# AMZN 2023-2025 FIVEGZ5SE Cycle 3 — Trading Path Integration

Status: **CYCLE3_COMPLETE / V2_PATH_CANDIDATE_IDENTIFIED**

Date: 2026-09-29

Development scope:
- AMZN only
- 2023-01-01 through 2025-12-31
- SCTYPE=1
- next-session-open execution
- 5 bps adverse slippage on each side
- long/cash only
- original formula action labels are not used

Cycle 3 starts from the Cycle-2 pruned families only.

No new five-dimension predictor is introduced.

---

## 1. Frozen Cycle-2 families

### BUY-A — early transition

```
Trend W3 slope > 0
AND Momentum = SHORT
AND Momentum W5 slope < 0
```

### BUY-B — capital cooling + acceleration recovery

```
Capital = GRAY
AND Capital W1 net change < 0
AND Acceleration W3 slope > 0
```

### SELL-A — failed bullish continuation

```
Trend = GRAY
AND Acceleration positive on >=3 of last 5 bars
AND >=3 bullish dimensions on >=2 of last 3 bars
```

### SELL-B — internal deterioration

```
Capital W5 slope < 0
AND Momentum >= LIGHT_LONG
AND Anomaly W1 net change < 0
```

### SELL-C — short-horizon over-extension

```
Momentum = LONG
AND Anomaly W3 net change > 0
AND >=3 bullish dimensions on >=2 of last 3 bars
```

All five families are used as **event onsets**:
the first bar of a new qualifying cluster is the signal.

---

## 2. Cycle-3 interaction grid

Test dimensions:

### Entry interaction
- BUY-A only
- BUY-B only
- BUY-A OR BUY-B
- BUY-A / BUY-B confirmation within 3 bars
- confirmation within 5 bars

### Exit interaction
- SELL-A full exit
- SELL-B full exit
- SELL-C full exit
- ANY SELL full exit
- SELL-A/B full, ignore C
- SELL-A full, B/C half
- SELL-A/B full, C half
- first sell halves, second sell fully exits

### Time cap
Initial grid:
- 10
- 15
- 20
- 30 trading sessions

### Re-entry cooldown
- 0 sessions
- 3 sessions

Initial complete-path grid:
**320 variants**

Ranking emphasizes:
- positive results in all three years;
- worst-year result;
- overall return;
- drawdown;
- adequate trade count.

It is not a raw-return-only ranking.

---

## 3. Main interaction result

The strongest complete interaction family is:

### ENTRY

```
BUY-A onset
OR
BUY-B onset
```

### ENTRY CONFLICT VETO

If any SELL-A/B/C onset occurs on the same signal bar:

```
DO NOT OPEN
```

Risk signal has priority over a new buy.

### EXIT

While holding:

```
SELL-A onset
OR
SELL-B onset
OR
SELL-C onset
```

causes a **full exit at the next-session open**.

### TIME CAP

Cycle-3 conservative default:

```
30 trading sessions
```

This is an operational default, **not** a claim that 30 is the statistically
optimal horizon.

---

## 4. Why BUY-A and BUY-B should be unioned

With the same ANY-SELL full-exit logic and 30-session cap:

### BUY-A only
- cumulative return: +150.43%
- MDD: -13.88%
- trades: 16
- win rate: 93.8%
- mean trade: +5.98%
- exposure: 35.2%

Calendar-year portfolio returns:
- 2023: +41.02%
- 2024: +29.39%
- 2025: +39.16%

### BUY-B only
- cumulative return: +128.17%
- MDD: -8.47%
- trades: 12
- win rate: 83.3%
- mean trade: +7.26%
- exposure: 18.9%

Calendar-year returns:
- 2023: +27.84%
- 2024: +24.72%
- 2025: +43.18%

### BUY-A OR BUY-B
- cumulative return: **+259.67%**
- MDD: **-13.88%**
- trades: 20
- win rate: **95.0%**
- mean trade: +6.71%
- median trade: +5.45%
- exposure: 43.4%

Calendar-year returns:
- 2023: **+39.16%**
- 2024: **+55.56%**
- 2025: **+68.46%**

The two entry families are complementary.

Requiring confirmation dramatically reduces participation:

- 3-bar confirmation best variant: only 3 trades
- 5-bar confirmation best variant: only 7 trades

Therefore confirmation is rejected for the core path.

Decision:

`ENTRY = BUY_A_OR_BUY_B`

---

## 5. Why full exit is preferred to partial reduction

With UNION entry and 30-session cap:

### ANY SELL full exit
- +259.67%
- MDD -13.88%
- 20 trades
- win 95.0%
- exposure 43.4%

### SELL-A/B full, ignore SELL-C
- +213.61%
- MDD -13.88%
- 18 trades
- win 94.4%

### SELL-A/B full, SELL-C half
- +205.77%
- MDD -13.88%

### SELL-A full, SELL-B/C half
- +175.24%
- MDD -13.88%

### first sell half, second sell full
- +192.43%
- MDD -13.88%

Partial-reduction logic did not improve drawdown and reduced return.

SELL-C also adds useful exit information:

Ignoring SELL-C:
- +213.61%

Using SELL-C as an equal full-exit trigger:
- **+259.67%**

with the same measured MDD.

Decision:

`EXIT = FIRST_OF_SELL_A_SELL_B_SELL_C_FULL_EXIT`

---

## 6. Exit logic contribution

UNION entry with 30-session **time-only** exits:

- return +157.03%
- MDD -20.64%
- win rate 80.0%
- exposure 57.2%

Adding SELL-A/B/C event exits:

- return **+259.67%**
- MDD **-13.88%**
- win rate **95.0%**
- exposure **43.4%**

Thus the pruned SELL families improve both:
- return capture;
- downside control.

Exit-trigger counts in the selected 30-session path:

- SELL-A: 6 completed trade exits
- SELL-B: 1
- SELL-C: 8
- time cap: 4
- final-period close: 1

SELL-C contributes the largest number of signal exits in this development
sample.

---

## 7. Time-cap sensitivity

Using the same:
- BUY-A OR BUY-B entry;
- ANY SELL full exit;

results are:

| Max hold | Return | MDD | Trades | Win | Exposure |
|---:|---:|---:|---:|---:|---:|
| 10 | +191.94% | -12.93% | 24 | 87.5% | 29.1% |
| 15 | +180.91% | -13.88% | 22 | 86.4% | 33.8% |
| 20 | +193.19% | -13.88% | 21 | 85.7% | 38.6% |
| 25 | +223.97% | -13.88% | 20 | 90.0% | 40.7% |
| 30 | +259.67% | -13.88% | 20 | 95.0% | 43.4% |
| 35 | +256.60% | -13.88% | 19 | 94.7% | 44.9% |
| 40 | +255.62% | -13.88% | 19 | 94.7% | 47.6% |
| 60 | +280.07% | -13.88% | 19 | 94.7% | 51.1% |

Important interpretation:

- the strategy is not a knife-edge at exactly 30 days;
- 25-60 days remain in the same high-performing region;
- 60 days has higher raw development return;
- choosing 60 because it now looks best would be a new post-hoc optimization.

Therefore Cycle 3 does **not** promote 60.

30 sessions is retained only as a conservative, pre-grid operational default.

The time-cap question remains open for a later controlled validation.

---

## 8. Re-entry cooldown

0-day and 3-day cooldown variants are often identical or nearly identical.

For the selected 30-session ANY-SELL logic:
- cooldown 0: +259.67%
- cooldown 3: +259.67%

Therefore no cooldown is needed in the core logic.

Decision:

`COOLDOWN = NONE`

---

## 9. Development benchmark

AMZN buy-and-hold over 2023-2025 with the same 5 bps entry/exit slippage:

- cumulative return: +169.82%
- MDD: -30.88%

Calendar-year buy-and-hold:
- 2023: +77.79%
- 2024: +44.77%
- 2025: +3.96%

Cycle-3 selected path:

- cumulative: **+259.67%**
- final value from $10,000: **$35,967.26**
- MDD: **-13.88%**
- exposure: **43.4%**

Approximate three-year annualized return is about 53% for the development
strategy versus about 39% for AMZN buy-and-hold.

This is a **development-sample comparison**, not out-of-sample proof.

---

## 10. Trade robustness

Selected path:
- trades: 20
- winners: 19
- losers: 1
- win rate: 95.0%
- mean trade: +6.71%
- median trade: +5.45%

Trade-level bootstrap 95% interval:
- mean trade: **+4.76% to +8.79%**
- compounded resample: **+149.45% to +428.69%**

Leave-one-trade-out compounded return:
- worst case after removing one trade: **+205.65%**
- median leave-one-out: +241.08%
- maximum: +267.75%

Therefore the result is not dependent on one exceptional winning trade.

However:
trade-level bootstrap does not correct for:
- Cycle-1 search selection;
- Cycle-2 pruning selection;
- Cycle-3 path selection;
- serial dependence.

It is supportive robustness evidence only.

---

## 11. Selected 20-trade ledger

| Signal | Entry | Exit | Hold | Return | Exit |
|---|---|---|---:|---:|---|
| 2023-03-10 | 2023-03-13 | 2023-03-17 | 4 | +10.80% | SELL-C |
| 2023-04-28 | 2023-05-01 | 2023-05-17 | 12 | +9.36% | SELL-C |
| 2023-07-12 | 2023-07-13 | 2023-08-24 | 30 | +1.66% | TIME |
| 2023-09-25 | 2023-09-26 | 2023-11-07 | 30 | +7.91% | TIME |
| 2023-12-06 | 2023-12-07 | 2023-12-19 | 8 | +5.54% | SELL-C |
| 2023-12-28 | 2023-12-29 | 2024-02-13 | 30 | +9.45% | TIME |
| 2024-02-20 | 2024-02-21 | 2024-03-04 | 8 | +4.98% | SELL-B |
| 2024-03-20 | 2024-03-21 | 2024-05-03 | 30 | +3.79% | TIME |
| 2024-06-18 | 2024-06-20 | 2024-06-27 | 5 | +6.51% | SELL-C |
| 2024-07-18 | 2024-07-19 | 2024-08-23 | 25 | **-2.20%** | SELL-A |
| 2024-10-28 | 2024-10-29 | 2024-11-07 | 7 | +9.89% | SELL-C |
| 2024-11-20 | 2024-11-21 | 2024-12-09 | 11 | +11.54% | SELL-C |
| 2025-01-03 | 2025-01-06 | 2025-02-06 | 21 | +4.85% | SELL-A |
| 2025-03-07 | 2025-03-10 | 2025-03-26 | 12 | +5.13% | SELL-C |
| 2025-04-03 | 2025-04-04 | 2025-04-16 | 8 | +5.36% | SELL-A |
| 2025-05-05 | 2025-05-06 | 2025-06-11 | 25 | +17.67% | SELL-C |
| 2025-06-18 | 2025-06-20 | 2025-07-09 | 12 | +2.87% | SELL-A |
| 2025-08-01 | 2025-08-04 | 2025-08-21 | 13 | +2.31% | SELL-A |
| 2025-09-25 | 2025-09-26 | 2025-10-31 | 25 | +14.05% | SELL-A |
| 2025-12-16 | 2025-12-17 | 2025-12-31 | 9 | +2.64% | final close |

---

## 12. Cycle-3 candidate trading logic V2

### Flat -> Long

At close t:

```
IF onset(BUY-A) OR onset(BUY-B)
AND NOT onset(SELL-A OR SELL-B OR SELL-C)
THEN
    BUY at next-session open
```

Position:
- 100% long for the development simulation.

### Long -> Cash

At close t:

```
IF onset(SELL-A)
OR onset(SELL-B)
OR onset(SELL-C)
THEN
    EXIT 100% at next-session open
```

Otherwise:

```
IF holding time reaches 30 trading sessions
THEN
    EXIT 100% at next-session open
```

### While already long

- ignore new BUY-A / BUY-B signals;
- no pyramiding in Cycle 3.

### Same-bar conflict

SELL wins.

No new position is opened.

### Re-entry

No artificial cooldown is required.

A later new BUY-A or BUY-B onset may open a new trade once flat.

---

## 13. What Cycle 3 establishes

Within the AMZN 2023-2025 development sample:

1. BUY-A and BUY-B should remain separate setup families but operate as an
   **OR entry union**.
2. Waiting for mutual confirmation loses too many useful opportunities.
3. SELL-A/B/C work better as equal full-exit events than as partial-reduction
   events.
4. SELL-C should not be discarded despite being classified as short-horizon
   de-risk in Cycle 2.
5. The exit families add substantial value beyond a fixed holding period.
6. The result is stable across 2023, 2024 and 2025.
7. The time-cap region is broad; 30 is not proven uniquely optimal.

---

## 14. What Cycle 3 does NOT establish

This is still a development-sample result.

The same AMZN 2023-2025 data were used to:
- discover combinations;
- prune combinations;
- choose their interaction.

Therefore +259.67% is **not an unbiased estimate of future return**.

The unusually high 95% trade win rate must be treated cautiously.

The next valid step is not to add more indicator predicates.

Cycle 4 should:
- stress-test this exact V2 path;
- test neighboring time-cap policy without changing entry/exit families;
- use year-block perturbation / delayed execution / higher slippage;
- test alternative conflict timing;
- assess signal overlap and opportunity cost;
- then decide whether V2 is stable enough to freeze for overall validation.

Research state:

`AMZN_2023_2025_FIVEGZ5SE_CYCLE3 = COMPLETE`

Candidate:

`FIVEGZ5SE_TRADING_PATH_V2 = IDENTIFIED_NOT_FINAL`
