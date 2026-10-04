# SLTD E A-share 50 Validation v1 — Protocol

Status: **FROZEN BEFORE RUN**

Branch:
`research/sltd-e-ashare50-v1`

Parent A-share data source:
`research/sltd-ashare50-integrated-risk-v1@59b48fba486a16c8bd00e5694fbef111fe71ede9`

Frozen E implementation:
- `integrations/sltd_v7_siftalpha_v1/e_strategy.py`
- blob SHA: `722fc7cc716f39ee07e58bd2f57d112659a4499c`
- source strategy branch historically validated at:
  `feature/sltd-v7-e-strategy-v1@f990eb9d2d4567d8acdc617fb1b4b9dd01b45f1c`
- specification:
  `integrations/sltd_v7_siftalpha_v1/E_STRATEGY_SPEC_v1.md`

## 1. Purpose

Run the frozen SLTD E v1 strategy on the same frozen 50-stock China A-share main-board universe.

No E rule may be retuned or modified after seeing A-share results.

## 2. XMA / causal boundary

E is an XMA strategy.

The study must use the repository's causal SLTD ledger construction:
- double XMA25 inner structure;
- corrected canonical slow weighted structure;
- all states computed bar-by-bar from information available at that completed bar only;
- no future-value backfill;
- no centered/reconstructed XMA.

Daily E uses:
- primary timeframe: 1d
- higher timeframe: 5d
- 5d bars = fixed non-overlapping groups of 5 completed daily bars;
- a 5d bar is not visible to a primary bar until its 5th source daily bar has completed.

Signal execution:
- signal confirmed at close t;
- earliest execution at next fillable daily open t+1.

## 3. E rules — frozen

BUY:
1. BLUE/GRAY and primary close crosses below ZD1 -> +25pp
2. on the same C1 event, latest completed 5d close below its own ZD1 -> additional +25pp
3. after C1 has actually filled, later touch of GZB3-GZB4 -> +25pp

Constraints:
- C1/C2/C3 each at most once per holding cycle;
- maximum target exposure 75%;
- after exit sequence begins, unused buy conditions cannot fire;
- after complete exit, cycle state resets.

SELL:
1. primary close crosses above ZK1 -> -50pp
2. exit sequence active and BS touched -> -25pp
3. exit sequence active and GZB3-GZB4 touched -> full exit
4. exit sequence active and close falls back below ZK1 -> full exit

Same-bar sell priority:
- full exit > BS -25pp > ZK1 -50pp.

No shorting.
No leverage.

## 4. Universe and data

Use exactly the frozen 50 A-share symbols in:
`research/ssss_reboot_v1/phase18/A_SHARE_50_UNIVERSE_V1.json`

Price snapshot:
`research/ssss_reboot_v1/phase18/ashare50_data_snapshot_v3`

Source:
- BaoStock
- qfq / 前复权
- archived through 2026-09-30

All 50 symbols are evaluated.

This study intentionally uses the previously reserved 15 Fresh symbols as part of the requested
50-stock E test. Therefore they are no longer independent Fresh OOS for **this E study**.
This does not retroactively change the Phase18 integrated-risk closeout.

## 5. Warmup and formal window

Requested market window:
- 2018-01-02 .. 2026-09-30

E requires:
- >=120 completed primary bars;
- >=120 completed 5d bars.

Because the frozen snapshots start in 2016, the formal E portfolio starts on the first common
trading date on which all 50 symbols have sufficient primary + completed-5d warmup.

No symbol may start earlier than its valid E warmup point.
No incomplete warmup signals are counted.

End:
- 2026-09-30

## 6. A-share fill constraints

Ordinary main-board 10% price-limit handling:

BUY blocked when execution bar is one-price limit-up:
- Open == High == Low within tolerance
- Open / previous Close - 1 >= +9.5%

SELL/full exit blocked when execution bar is one-price limit-down:
- Open == High == Low within tolerance
- Open / previous Close - 1 <= -9.5%

Blocked action:
- remains pending;
- retries at later opens until fillable;
- does not update E cycle-state until actual fill.

Suspension / missing stock bar:
- no synthetic fill.

## 7. Friction

Primary:
- BUY: 5 bps
- SELL before 2023-08-28: 15 bps
- SELL on/after 2023-08-28: 10 bps

Sensitivity:
- BUY: 10 bps
- SELL before 2023-08-28: 20 bps
- SELL on/after 2023-08-28: 15 bps

Costs apply to absolute executed notional.

## 8. Comparator

Primary context comparator:
- BUY_AND_HOLD on the same 50 stocks
- buy 100% at the first common formal open
- hold to 2026-09-30

E is not changed based on comparator outcomes.

## 9. Required output

At primary and sensitivity friction:

Equal-weight 50-stock portfolio:
- Total Return
- CAGR
- MaxDD
- Calmar
- mean time in market
- mean turnover
- total position changes

Per-symbol:
- Return
- CAGR
- MaxDD
- Calmar
- time in market
- turnover
- E rule execution counts

Breadth vs Buy & Hold:
- E better Return count
- E better MaxDD count
- E better Calmar count
- median per-symbol deltas

E rule totals:
- C1
- C2
- C3
- SELL1
- SELL2
- SELL3
- SELL4
- blocked BUY attempts
- blocked SELL attempts

Era portfolio metrics:
- EARLY: formal_start .. 2020-12-31
- MIDDLE: 2021-01-01 .. 2023-12-31
- LATE: 2024-01-01 .. 2026-09-30

## 10. Interpretation

This is an evaluation, not a tuning round.

No admission threshold is required to run the test.
After results:
- E may be described as strong/weak on A shares;
- no E condition may be altered inside v1 to rescue performance.

`SLTD_E_ASHARE50_VALIDATION_V1_PROTOCOL = FROZEN`
