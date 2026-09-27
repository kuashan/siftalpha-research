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


## 2026-09-28 — HYS2 candidate + multi-asset expansion

A new source indicator, HYS2.ftindex, was received and inspected.

Source SHA-256:
`40936da053455c2e4d05d4bab3f28757e3c59c6cc92668e7c98dd443743799c3`

Decision:
- do NOT merge HYS2 into the XMA baseline;
- log it as CANDIDATE_FEATURE;
- evaluate low-side panic/new-low impulse and ★共振 separately;
- do NOT treat 火焰山顶 as an automatic sell or short;
- do NOT retroactively change January decisions.

ABT January post-hoc finding:
- HYS2 new-30-day-low / fire-bottom impulse occurred on Jan-15;
- HYS2 ★共振 occurred on Jan-16, aligning with the previously frozen XMA confirmation entry;
- HYS2 fire-top was active during Jan-21 onward breakout and would have been harmful if interpreted as an automatic short.

The research universe is expanded from a single ABT case to a multi-asset Discovery universe including ARM, ORCL, AAPL, AMZN, INTC and other widely recognized liquid names. See MULTI_ASSET_UNIVERSE.md.

No rule requires opening a short position. Exit and short-entry are separate decisions.


## 2026-09-28 — FIVEGZ5SE candidate state engine

User supplied FIVEGZ5SE.txt and explicitly warned that textual annotations, especially concepts labeled "清" and "抄", are not reliable semantics.

Source:
- SHA-256: 61bc9f7cad7a2efb6374a187c680fa75789b2468824885e5127c5f70333400c9
- size: 93,201 bytes

Research decision:
- evaluate actual boolean logic, not displayed names;
- do not merge into the XMA baseline;
- treat the five raw dimensions as auxiliary states;
- freeze prior January XMA decisions unchanged.

Key findings:
- "当下清仓" is actually trend-short AND capital-short AND momentum-short; record it as triple-bear confirmation, not mandatory liquidation.
- "底部双重背离" is not mathematical divergence; it is weak-trend + capital/momentum recovery.
- several COUNT-based comments overstate dimension counting; the code counts bars after OR aggregation.
- MOM_CONTINUOUS_DAYS=0 disables the intended continuity gate.
- ABT Jan-16 composite risk conflicts with the previously frozen XMA confirmation entry.
- ABT Jan-21 all five dimensions turn LONG and strongly confirm the breakout.
- ABT Jan-24 reduce-state is earlier than the later price peak; treat as caution, not mandatory reduction.
- Jan-30/31 triple-bear confirmation still does not occur, so it is too late as a primary exit rule in this case.

See FIVEGZ5SE_EVALUATION.md.


## 2026-09-28 — February 2025 multi-asset Discovery run

Protocol was frozen before execution:
`experiments/multi_asset_2025_02/PROTOCOL_FROZEN_BEFORE_RUN.md`

Universe:
ABT, AAPL, AMZN, ORCL, INTC, MSFT, NVDA, GOOGL, META, JPM, XOM.

ARM was not forced into the batch because a sufficiently verified common OHLCV source was not available.

Four variants:
- XMA_ONLY
- XMA_HYS2
- XMA_FIVEGZ
- XMA_HYS2_FIVEGZ

Cross-symbol result:
- combined had the highest mean return (+0.151%)
- XMA_FIVEGZ had the best downside profile (worst -1.271%, mean max DD -0.233%)
- HYS2 improved NVDA but worsened multiple losers when used as a global sizing boost
- FIVEGZ raw color states were the most consistent risk-control addition

Critical findings:
1. repeated XMA probes are too permissive in persistent declines (GOOGL/AMZN)
2. slow BEAR regime can miss fast transition rallies (INTC; weaker AAPL example)
3. next-open execution needs a gap-against-signal re-evaluation rule
4. FIVEGZ color transitions should be interpreted as a state continuum, not literal text commands
5. no automatic shorting rule was introduced

No February rule was retroactively changed.
Candidate fixes must be frozen before the next month.


## 2026-09-28 — March–June 2025 multi-asset run

Frozen protocol:
`experiments/multi_asset_2025_03_06/PROTOCOL_FROZEN_BEFORE_RUN.md`
commit:
`bd58431a8214c76549e624c49422c9a9850e6851`

Primary execution model changed from legacy next-open to:
`SAME_BAR_CLOSE_PROXY_V2`.

Reason:
the signal/action belongs to the current K bar once the full rule is satisfied.

Limitation:
daily bars cannot identify exact intraday first-confirm time; same-bar close is a causal execution proxy, not a minute replay.

Universe:
11 equities + BTC / ETH / BNB / SOL.

Major findings:
1. XMA + FIVEGZ had the highest equity mean return (+1.101%) but the result is strongly ORCL-driven; trimmed mean remains negative.
2. Combined HYS2+FIVEGZ was not robust and worsened median/worst outcomes.
3. Crypto SCTYPE=2 FIVEGZ was harmful in this window; do not promote it.
4. HYS2 was only selectively helpful in crypto.
5. Transition Override was too aggressive. On 2025-04-09 it fired across many assets simultaneously; first override exposure must be smaller in the next preregistered version.
6. Three-bar cooldown reduced but did not eliminate repeated failed probes.
7. No automatic shorting was introduced.
8. ARM remains excluded until verified daily OHLCV is available.

No March–June rule was retroactively changed.
