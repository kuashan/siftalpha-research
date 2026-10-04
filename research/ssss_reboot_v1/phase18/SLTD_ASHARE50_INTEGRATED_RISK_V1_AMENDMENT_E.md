# SLTD A-share 50 Integrated Risk v1 — Amendment E

Status: **FROZEN BEFORE STAGE B HOLDOUT RESULTS**

Parent protocol:
`SLTD_ASHARE50_INTEGRATED_RISK_V1_PROTOCOL.md`

Comparator amendment:
`SLTD_ASHARE50_INTEGRATED_RISK_V1_AMENDMENT_D.md`

Stage A:
`PROMOTED_TO_INTEGRATED_HOLDOUT`

## 1. Stage B window and symbols

Only:
- 35 frozen DEVELOPMENT symbols
- formal evaluation: 2025-01-02 .. 2026-09-30

Pre-2025 bars are warmup/state context only.
No Fresh15 strategy result may be read.

## 2. Pending-order execution under A-share locked limits

Every signal is confirmed at close t and creates an intended order for the next available stock bar open.

A BUY is blocked if the execution bar is a one-price locked limit-up bar:
- Open == High == Low within price tolerance
- Open / previous Close - 1 >= +9.5%

A SELL / C2 / Severe Risk full exit is blocked if the execution bar is a one-price locked limit-down bar:
- Open == High == Low within price tolerance
- Open / previous Close - 1 <= -9.5%

When blocked:
- the exact intended action remains pending;
- no partial synthetic fill is allowed;
- it retries at each subsequent stock open until fillable.

While any order is pending:
- no later lower-priority ordinary action may replace it;
- a pending BUY can be cancelled only by a later hard-exit condition if a position already exists;
- a pending ordinary SELL can be upgraded to a hard full exit if C2 or Severe Risk becomes eligible;
- C2 has attribution priority over Severe Risk on the same signal bar.

Risk-state changes occur only after actual fills:
- executed ordinary SELL -> ARMED
- executed BUY -> NORMAL
- executed hard full exit -> NORMAL

This prevents an unfilled order from changing the C2 state.

## 3. A-share transaction cost accounting

Primary:
- BUY execution friction: 5 bps
- SELL execution friction on/after 2023-08-28: 10 bps total

The 2025-2026 holdout lies entirely after 2023-08-28, therefore Stage B primary executed:
- BUY = 5 bps
- SELL = 10 bps

Sensitivity:
- BUY = 10 bps
- SELL = 15 bps

Costs apply to absolute executed notional.

## 4. Per-stock metrics

For each system and symbol:
- Total Return
- CAGR
- MaxDD
- Calmar
- mean exposure
- executed BUY count
- ordinary SELL count
- C2 full-exit count
- Severe Risk full-exit count
- blocked BUY attempts
- blocked SELL / hard-exit attempts

## 5. Aggregate metrics

Primary aggregate is an **equal-weight portfolio of the 35 per-stock strategy equity curves**.

At 2025-01-02:
- allocate 1/35 of portfolio NAV to each symbol strategy;
- no cross-symbol capital transfer afterward;
- portfolio NAV each day = arithmetic mean of the 35 normalized symbol-strategy NAVs.

Aggregate report:
- Total Return
- CAGR
- MaxDD
- Calmar
- mean exposure = arithmetic mean of symbol exposure
- daily p1 and p5 returns

Per-stock breadth statistics remain separate and cannot be inferred from the portfolio curve.

## 6. Buy & Hold context

BUY_AND_HOLD:
- each symbol buys 100% at its first fillable 2025 holdout open;
- then never rebalances or sells;
- portfolio aggregate uses the same equal-weight 35-sleeve construction.

SMA200:
- close t above SMA200 -> target long 100% at next fillable open
- close t below/equal SMA200 -> target cash at next fillable open
- same A-share blocked-limit execution and friction model

These are context-only and cannot alter the B-vs-C admission gates.

## 7. Gate interpretation

For the preregistered Stage B gates:
- "aggregate" means the equal-weight 35-sleeve portfolio defined above.
- MaxDD improvement of >= 2.0 percentage points means:
  `Candidate MaxDD - Baseline MaxDD >= +0.020`
  because less-negative MaxDD is better.
- Total Return retention:
  `Candidate Total Return / Baseline Total Return >= 0.95`
  when baseline return > 0.
- median per-stock return delta:
  median(Candidate return - Baseline return) >= -0.010.
- exposure retention:
  Candidate mean exposure / Baseline mean exposure >= 0.90.

## 8. Freeze

`SLTD_ASHARE50_INTEGRATED_RISK_V1_AMENDMENT_E = FROZEN`
