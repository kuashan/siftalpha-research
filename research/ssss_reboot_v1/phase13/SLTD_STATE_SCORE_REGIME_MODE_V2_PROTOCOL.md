# SLTD State Score Regime Mode v2 — Protocol

Status: **PRE-REGISTERED / NOT YET RUN**

## User boundary

This is a standalone SLTD mode.

It is **not**:
- V7 plus filters,
- V7 plus score gates,
- V7 plus score sizing.

V7 is comparison-only.

Architecture:

`SLTD state -> frozen score -> regime state machine -> LONG/CASH`

No V7 BUY/HOLD/WAIT/SELL rule is used.
No V7 C2 exit is used.
No Chan/缠论 is used.

## Why this mode exists

Phase12 already proved that the standalone SLTD score has real directional separation on untouched stocks:

- 25% score bucket: negative forward excess
- 100% score bucket: positive forward excess

But the Phase12 exposure-map implementation failed because it:
- stayed invested all the time,
- rebalanced too often,
- created very high turnover,
- and converted every score change into a position change.

Therefore v2 keeps the frozen score itself, but changes the trading mechanics completely.

## Frozen score source

Use exactly the Phase12 score construction from:

`research/sltd-state-score-exposure-map-v1`
@ `29ceeeb73328e0f1b1108f01ab14179e858c7e5e`

Score inputs remain the 20 OOS-confirmed pure-SLTD states from Phase11.

The Phase12 score component logic remains frozen:
- REGIME
- INNER
- SLOW
- EVENT

The Phase12 calibration remains frozen:
- positive scale from original 79 discovery
- negative scale from original 79 discovery

No Fresh24 outcome is used to change score weights or scales.

## Regime-state trading logic

Two position states only:

- CASH = 0%
- LONG = 100%

At each completed bar close, calculate the frozen Phase12 score bucket:

- 25%
- 50%
- 75%
- 100%

State transition:

### CASH -> LONG
Only when the completed bar is in the **100% score bucket**.

Execution:
- buy to 100% at next bar open.

### LONG -> CASH
Only when the completed bar is in the **25% score bucket**.

Execution:
- sell to 0% at next bar open.

### 50% / 75% score buckets
No position change.

This creates explicit hysteresis:

- strong positive score is required to enter;
- strong negative score is required to exit;
- neutral/intermediate states preserve the current regime.

There is:
- no partial exposure,
- no daily rebalancing,
- no stop-loss,
- no take-profit,
- no minimum hold,
- no cooldown,
- no V7 logic.

## Causal execution

Score known at close t.
Transition executed at open t+1.

No future information.
No historical backfill.

## Fresh v2 universe

Must not overlap any prior research universe:
- original 79
- Phase11 OOS10
- R2 Fresh20
- R3 Fresh20
- Phase12 Fresh24

Fresh30 v2:

Financial:
- TFC, AON, MET

Technology:
- ANET, MSI, NXPI

Healthcare:
- ELV, MCK, RMD

Industrials:
- GWW, CMI, NSC

Materials:
- STLD, CF, LYB

Consumer discretionary:
- RCL, DHI, NVR

Consumer staples:
- CPB, TSN, ADM

Utilities:
- PEG, ES, ETR

Energy:
- HAL, DVN, FANG

Real estate:
- VICI, SPG, DLR

The script must assert zero overlap before any result is accepted.

## Window

Daily bars.

Warm-up:
- fetch from 2010-01-04 where available

Formal:
- 2020-01-02 .. 2026-09-30

Raw unadjusted OHLC, matching the frozen US-stock research protocol.

## Friction

- 5 bps primary
- 10 bps
- 20 bps stress

## Comparison systems

1. `SLTD_SCORE_REGIME_V2`
2. `SLTD_SCORE_EXPOSURE_V1` — old continuous exposure implementation
3. `V7_BASE`
4. `BUY_HOLD`
5. `SMA200_TREND`

Comparators do not contribute signals to v2.

## Required diagnostics

Report:

- total return
- CAGR
- MaxDD
- Calmar
- turnover
- position changes
- time in market
- average holding duration
- number of entries
- number of exits

Also report forward excess of:
- entry-trigger 100% bucket
- exit-trigger 25% bucket

using 10d and 20d horizons.

## Primary admission gates

At 5 bps, v2 must:

- Total Return > Phase12 continuous score exposure v1;
- Calmar > Phase12 continuous score exposure v1;
- Turnover < Phase12 continuous score exposure v1;
- Total Return > V7_BASE;
- Calmar > V7_BASE;
- Total Return >= BUY_HOLD;
- Calmar > BUY_HOLD;
- MaxDD less severe than BUY_HOLD;
- per-symbol Total Return > V7 in >= 16/30;
- per-symbol Total Return > BUY_HOLD in >= 16/30.

Signal sanity:
- 100% entry-trigger bucket 10d excess > 0;
- 100% entry-trigger bucket 20d excess > 0;
- 25% exit-trigger bucket 10d excess < 0;
- 25% exit-trigger bucket 20d excess < 0.

Durability:
- at 10 bps, v2 Total Return > V7;
- at 20 bps, v2 Calmar > V7.

## Decision

All gates pass:
`PROMOTE_STANDALONE_SCORE_REGIME_TO_ENGINEERING_CANDIDATE`

Beats Phase12 score exposure and V7 but fails Buy & Hold:
`RESEARCH_ONLY_SCORE_REGIME_HAS_VALUE`

Fails to improve over Phase12 score exposure or V7:
`REJECTED_SCORE_REGIME_V2`

No thresholds or universe members may be changed after Fresh30 is observed.

`SLTD_STATE_SCORE_REGIME_MODE_V2_PROTOCOL = FROZEN`
