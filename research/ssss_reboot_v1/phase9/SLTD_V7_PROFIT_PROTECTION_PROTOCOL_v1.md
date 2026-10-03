# SLTD V7 Profit Protection Study v1 — Protocol

Status: **FROZEN_BEFORE_RUN**
Date: 2026-10-03

## 1. Purpose

This study does **not** redesign SLTD V7 BUY / HOLD / WAIT logic.

It asks one question only:

> Can a separate profit-protection layer preserve more of an already-earned trend profit
> without destroying the return advantage of frozen V7?

Frozen reference:
- V7 candidate commit: `5f9ea4d8fa434b54afdbf32a1cb21ef2f3cb4042`
- 12-rule candidate: `DROP_B3_S1_S3`
- position policy: flat BUY 25%; later BUY +25pp to 100%; ordinary SELL -25% of current holding;
- C2 unchanged;
- FIRST_OBSERVED XMA only;
- signal on completed bar -> next available open execution.

## 2. External design anchors

This protocol is intentionally derived from established quantitative / trend-management ideas
instead of open-ended SELL-condition enumeration.

1. **Trend following / let profits run**
   - AQR: Hurst, Ooi, Pedersen, *A Century of Evidence on Trend-Following Investing*.
   - Design implication: avoid fixed early full-profit targets that mechanically cut strong trends.

2. **Stop rules are strategy-dependent**
   - Kaminski & Lo, *When Do Stop-Loss Rules Stop Losses?*
   - Design implication: evaluate protection inside the momentum/trend context rather than assume
     a generic stop always helps.

3. **Separate alpha from risk management**
   - QuantConnect Algorithm Framework risk-management architecture.
   - Design implication: frozen V7 signals remain the alpha/position source; the protection layer
     can override exposure without rewriting the signal taxonomy.

4. **Volatility-adjusted trailing exit**
   - Charles Le Beau / Chandelier Exit convention: 22-period high minus 3 x ATR(22).
   - This exact canonical 22,3 setting is used; no ATR-multiplier sweep is allowed.

## 3. Universe and representation

Universe:
- prior frozen 79 mainstream U.S. stocks;
- fresh OOS10: WFC, LMT, PM, ADP, WM, UNP, SO, VZ, PANW, CVS;
- total = **89 unique stocks**.

Window:
- 2020-01-02 through 2026-09-30;
- daily bars only.

Representation:
- **FIRST_OBSERVED only**;
- no RENDER_ASOF values may drive a historical action.

Execution:
- completed bar t confirms;
- order executes at t+1 available open;
- 5 bps primary friction;
- 10 bps stress friction.

## 4. Frozen baseline

### V7_BASELINE

Exactly reproduce frozen V7:
- 12-rule candidate entry/action resolution;
- 25pp pyramiding;
- ordinary SELL removes 25% of current holding;
- ordinary SELL arms C2;
- later BUY resets C2;
- C2 full exit unchanged.

No protection overlay.

## 5. Finite candidate set

There are exactly four candidates. No additional variant may be introduced after results are seen.

### P1 — STRUCT_TREND_FAILURE

Purpose:
- let BLUE trend profits run;
- exit only after a previously demonstrated upper-rail trend loses the inner upper rail.

Arm:
- position exists;
- completed bar state = BLUE;
- completed bar has a new UPPER event;
- current close is above the current weighted average entry cost.

After arming:
- on a **later** completed bar, if `Close < ZK1` and close remains above weighted average entry cost,
  schedule a full exit for next open.

Rules:
- same-bar arm + exit is forbidden;
- any executed BUY resets the P1 arm;
- full flat resets the P1 arm;
- frozen V7 C2 keeps higher priority than P1.

### P2 — CHANDELIER_22_3_PROFIT

Canonical long Chandelier:
- `ATR22` = causal Wilder ATR(22);
- `HH22` = rolling highest High of the latest 22 completed bars;
- `STOP = HH22 - 3 * ATR22`.

Profit-protection guard:
- apply only when `STOP > weighted_average_entry_cost`.

Signal:
- completed-bar `Close < STOP` -> full exit next open.

No 2x / 2.5x / 3.5x / 4x sweep is permitted.

Frozen V7 C2 keeps higher priority.

### P3 — BS_SCALEOUT_25

Purpose:
- use SLTD's own upper XMA60 extreme as a partial profit-taking location,
  while preserving trend participation.

New BS event:
- current completed bar `High >= BS`;
- previous completed bar `High < previous BS`.

Guard:
- `BS > weighted_average_entry_cost`.

Action:
- next open sell **25% of current holding**;
- not 25 percentage points;
- each distinct recross can fire again;
- being continuously above BS does not repeatedly sell.

Frozen V7 C2 keeps higher priority.

### P4 — BS25_PLUS_CHANDELIER

Combination of:
- P3 BS 25%-of-current scale-out;
- P2 canonical Chandelier 22,3 full exit.

Priority:
1. frozen V7 C2 full exit;
2. Chandelier full exit;
3. BS 25% scale-out;
4. ordinary frozen V7 action.

This combination is pre-specified because mature risk frameworks commonly combine a profit-taking
component with a trailing-risk component. No other combination is allowed in v1.

## 6. Cycle profit-protection metrics

Portfolio Return / CAGR / MaxDD / Calmar remain mandatory.

Additionally, for every completed position cycle (flat -> invested -> flat):

- `peak_gain`: maximum mark-to-market cycle equity gain, using each bar High;
- `exit_gain`: realized cycle equity gain after the full-exit execution;
- `giveback = max(0, peak_gain - exit_gain)`;
- `capture_ratio = exit_gain / peak_gain` for cycles with positive peak_gain;
- `giveback_ratio = giveback / peak_gain` for cycles with positive peak_gain.

Report:
- median capture ratio;
- median giveback ratio;
- median absolute giveback;
- cycle count;
- positive-peak cycle count.

Open cycles at 2026-09-30 are excluded from capture/giveback statistics.

## 7. Required comparisons

For each candidate vs V7:
- all89 equal-weight portfolio;
- prior79;
- OOS10;
- per-symbol breadth:
  - Return better;
  - MaxDD better;
  - Calmar better;
  - giveback-ratio better;
- 2020..2026 calendar slices;
- early / middle / late eras;
- 5bps and 10bps;
- AAPL diagnostic output.

## 8. Admission gate

A candidate can be labeled `ADMIT_CANDIDATE` only if, at 5 bps:

1. all89 Calmar improves vs V7;
2. all89 MaxDD is less severe vs V7;
3. all89 total return remains at least 90% of V7 total return;
4. median completed-cycle giveback ratio improves;
5. OOS10 does not contradict the direction:
   - OOS10 MaxDD is no worse, and
   - OOS10 giveback ratio improves.

If risk/giveback improves but return or Calmar gate fails:
- `MIXED_NOT_ADMITTED`.

If protection does not materially improve risk/giveback:
- `REJECTED_NOT_ADMITTED`.

V7 remains frozen regardless of the result. Promotion requires a separate explicit user decision.

## 9. Closure

This study ends with exactly one result per candidate:
- ADMIT_CANDIDATE
- MIXED_NOT_ADMITTED
- REJECTED_NOT_ADMITTED

No new SELL hypothesis is generated from the same run.

`SLTD_V7_PROFIT_PROTECTION_PROTOCOL_V1 = FROZEN_BEFORE_RUN`
