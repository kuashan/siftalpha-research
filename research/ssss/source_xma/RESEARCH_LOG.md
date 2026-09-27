# Source-XMA Research Log

## 2026-09-27 — Track initialization

Repository baseline inspected before changes:
- repository: kuashan/siftalpha-research
- visibility: private
- default branch: main
- main HEAD at inspection: 512375038ba794536d785e51ad29fa14b9897d4b

Existing official SSSS state was read before opening this track.

Important boundary:
- existing official research uses a causal DEMA rewrite for the current model;
- this new track deliberately restores the original XMA for source-behavior research;
- the existing causal conclusions and model files were not modified.

Source findings recorded at initialization:
1. SSSS and ADKBY-E share the same double-XMA(25) core fast structure.
2. ADKBY-E's normalized 20000/80000 levels map to the same lower/upper fast-band geometry.
3. SSSS low slow-structure formula contains REF(H,11) in the low-weighted series.
4. ADKBY-E uses REF(L,11).
5. SSSS omits lag 19 and includes lag 20 at weight 1.
6. ADKBY-E includes both lag 19 and lag 20 at weight 1 while retaining denominator 210.
7. Therefore the slow structures are not mathematically identical and must be recorded separately.
8. The original three regime states leave an unclassified/expansion geometry; the research vocabulary adds EXPANSION / REGIME_UNCLEAR.
9. The author's icons/text remain comparison observations, not our target decision labels.

First case study:
- ABT daily
- anchor 2025-01-01
- first tradable session 2025-01-02
- walk forward toward latest available data
- preserve XMA
- no conventional return-optimization backtest

Evidence warning:
A later ABT history chart was already viewed before this repository track was initialized. Therefore the ABT replay is exploratory / previously seen, not OOS or Frozen OOS.

Current next step:
Obtain point-in-time ABT daily OHLCV and establish an exact, documented XMA reproduction path before populating observations.csv and decisions.csv.


## 2026-09-28 — ABT first-month walk-forward completed

Window:
- 2025-01-02 through 2025-01-31
- 20 trading sessions
- source XMA preserved
- point-in-time first-observed XMA values used for decisions
- $10,000 paper capital
- next-open execution
- 5 bps one-way slippage
- fractional shares

Key source-system events:
- 2025-01-15: SSSS LOW_ICON + ADKBY-E 多
- 2025-01-21: SSSS HIGH_ICON + ADKBY-E 空 while source state was still RANGE

Independent interpretation:
- Jan-15 lower extreme -> 30% probe only because both momentum components were still down
- Jan-16 XMA-mid reclaim + BOTH_UP -> target 70%
- Jan-21 FastUpper breakout + BOTH_UP + RVOL 1.65x -> override the source RANGE short signal; target 100%
- Jan-28 extreme extension + momentum deceleration -> reduce to 70%
- Jan-30 slow-momentum turn negative / conflict -> exit remaining position next open
- Jan-31 BULL regime prevented an automatic short reversal

Paper result:
- final capital: $11,345.49
- net return: +13.45%
- close-to-close equity max drawdown: about -1.58%
- result is exploratory, not OOS

Source-literal comparison:
- following Jan-15 long then Jan-21 high-side exit literally would have produced about +2.70% net under the same execution friction
- reversing the Jan-21 ADKBY-E 空 into a literal short and covering Jan-31 open would have lost about -12.59% before borrow cost

Auxiliary-factor ablation:
- volume as mandatory entry gate: harmful in this month
- volume as breakout confirmation: helpful
- VIX as a hard gate: not supported; retain as context only

Important XMA observation:
- XMA historical values near the right edge revise materially as later bars arrive
- decisions remain tied to the first-observed point-in-time XMA values
- revisions are stored in experiments/abt_2025_walkforward/revisions.csv

Artifacts:
- observations.csv
- decisions.csv
- paper_trades.csv
- revisions.csv
- FIRST_MONTH_REPORT.md
- visual_report.html

Next research step:
continue the same walk-forward method into February 2025 without retroactively rewriting January decisions.
