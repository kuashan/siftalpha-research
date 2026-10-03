# External Chan Implementations Audit — Round 1

Status: EXTERNAL_AUDIT_ROUND1_COMPLETE_NO_PRODUCTION_CHANGE  
Branch: `feature/chan-standalone-v2`  
Internal base HEAD before audit: `978003325d8eb76e0c76ebfb7085d39a17fc9bcd`

This review deliberately selects mature implementations using community evidence
(stars/forks/issues/discussions/activity) before studying code. Popularity is
used only as a maturity signal, never as proof that an interpretation is
theoretically correct.

## 1. Candidate selection

### A. Vespa314/chan.py
Pinned external HEAD: `429d6ed3043e27c93a003ba2b10e70a05575e1f5`
GitHub snapshot at audit time:
- Stars: 2188
- Forks: 815
- Watchers: 60
- Open issues: 11
- Active issue discussions include segment confirmation, disappearing BSPs,
  trigger-step performance, Zhongshu drawing and theory-standardization.
- Bilibili author content also has non-trivial usage/community engagement.

Why selected:
- full K-line inclusion / fractal / Bi / segment / Zhongshu / BSP framework;
- multiple segment algorithms;
- multi-level linkage;
- incremental trigger mode;
- explicit B1 / B1P / B2 / B2S / B3A / B3B classes;
- real issue discussions overlap directly with our confirmation-latency problem.

### B. yijixiuxin/chanlun-pro
Pinned external HEAD: `8324088626815938464e0b43ade963a28203c075`
GitHub snapshot:
- Stars: 1047
- Forks: 379
- Watchers: 31
- Open issues: 1
- Active through 2026-09.
External usage evidence:
- Bilibili project series has about 2.5k followers and about 7.9w series plays;
  individual tutorials have thousands to tens of thousands of plays.

Why selected:
- incremental per-Bar engine;
- multi-market charting, monitoring, backtest and live-trading integration;
- explicit docs for Bi/segment/Zhongshu/trend divergence/B1-B3;
- multiple Zhongshu construction and relation modes.

Limitation:
- current core dispatches into protected/compiled platform-specific modules, so
  the newest core algorithm cannot be audited line-by-line from all source.
  Public docs/interfaces are still useful as a design reference.

### C. waditu/czsc
Pinned external HEAD: `701e480a545004f945bb1721e510ae610ad90c4c`
GitHub snapshot:
- Stars: 6352
- Forks: 1762
- Watchers: 160
- Open issues: 18
- large active test/refactor history.

Why selected:
- strongest engineering/community maturity in the group;
- active Rust/Python core and tests;
- useful modern quantitative interpretation of Chan-derived structure.

Boundary:
- CZSC is not a canonical-original-Chan reference implementation. Historical
  issues explicitly describe divergence/Zhongshu ideas being folded into
  pattern signals; current first-buy/sell helpers use Bi sequence extremes and
  price/volume/length power rather than requiring the canonical two-same-level-
  Zhongshu trend-divergence chain.

### Secondary projects not used as primary theory references
- YuYuKunKun/chanlun.py: 154 stars / 62 forks, active, web + Backtrader, but
  smaller community and visibly mixes aggressive / after-the-fact labels.
- dogfun/chanlun: 100 stars / 51 forks, but main development is much older.

## 2. Vespa314/chan.py — theory / engineering audit

### 2.1 Strong matches with our theory review
- Keeps B1 and `1p` separate.
  - `T1`: center-related first-class point.
  - `T1P`: consolidation-divergence-like first-class point.
  This supports our earlier decision not to relabel first-center
  consolidation divergence as standard B1/S1.
- B2 and B3 dependence on B1 is configurable. The documentation explicitly
  mentions small-level-to-large-level cases where B1 may not appear.
  This supports our current independent B2/S2 architecture.
- Uses feature-sequence based segment implementation and exposes the feature
  sequence for visual inspection.
- Supports incremental K-line triggering to avoid future-data access.

### 2.2 Crucial difference from our current implementation: provisional state
The framework explicitly separates:
- confirmed segments: `is_sure=True`;
- virtual/provisional segments: `is_sure=False`.

Its guide says segment confirmation is strongly lagging, therefore the current
frame contains inferred/virtual segments which can change as new bars arrive.

It also explicitly states that morphology BSPs can disappear when later bars
invalidate them. Therefore a historical BSP plotted at an old anchor is not the
same thing as an irreversible, executable signal known at that anchor.

The project distinguishes:
- `bsp`: morphology point calculated from Chan structure, may later disappear;
- `cbsp`: custom strategy point evaluated on the current incremental frame.

This is directly relevant to our problem. Our current production path waits for
very stable L1+ structures and therefore sacrifices responsiveness.

### 2.3 Important non-canonical / aggressive defaults
At the pinned HEAD, `CChanConfig.set_bsp_config` defaults include:
- `divergence_rate = inf`
- `min_zs_cnt = 1`
- `bs_type = "1,1p,2,2s,3a,3b"`
- `bsp2_follow_1 = True`
- `bsp3_follow_1 = True`

In `CZS.is_divergence`, `divergence_rate > 100` directly returns divergence
true once the outgoing movement breaks the Zhongshu. Thus the default
`divergence_rate=inf` effectively bypasses the weaker-force threshold.

Classification:
- useful as an engineering / responsiveness choice;
- NOT a canonical reason for us to weaken standard B1/S1;
- important explanation for why chan.py can visibly produce many more BSPs.

### 2.4 Community issues confirm the same hard problem we have
Issue #104: a user reports a segment-level third sell does not appear until the
down segment is fully confirmed. The author explains the behavior is tied to
higher segment/center structure and says cross-segment handling is complex.

Issue #103: users debate feature-sequence segment ending where later price makes
a new extreme. The author explicitly accepts that a confirmed segment endpoint
does not have to be the absolute extreme of all later bars. Other users dispute
the exact feature-sequence handling.

Issue #116: a user requests a 100%-original-theory mode, arguing current
Zhongshu/BSP logic is coupled to segments. This remains open.

Conclusion:
chan.py is mature and extremely useful, but its popularity does not make every
structural choice canonical. Its strongest lesson for us is the explicit
provisional-vs-confirmed architecture.

## 3. chanlun-pro — theory / engineering audit

### 3.1 Rules that strongly agree with our research
Its public rule documentation defines:
- standard B1/S1: trend divergence with two same-level Zhongshu;
- trend divergence: two or more same-direction same-level non-overlapping
  Zhongshu plus a new extreme and weaker force;
- consolidation divergence as a separate concept;
- B2/S2 includes cases after trend structure and cases where a third sell/buy
  transition can lead to B2/S2 without a standard B1/S1;
- B3/S3: departure from Zhongshu followed by a return that does not re-enter.

These are broadly consistent with our theory audit.

### 3.2 It does not demand irreversible structures before showing information
The project states it calculates incrementally per Bar. It can output current
divergence/BSP information which may later be confirmed, extended, invalidated
or disappear. Confirmed structures are more stable, but current-frame
information is still exposed.

Again the architectural lesson is:
- current/provisional morphology;
- later confirmation;
- strategy/backtest layer consumes incremental state.

### 3.3 Multiple Zhongshu semantics are explicit, not hidden
It exposes several Zhongshu modes and relationship modes:
- standard / within-segment / directional / classified Zhongshu;
- first-three overlap vs all-lines overlap;
- loose / medium / strict center relationship comparisons.

This is not evidence that all modes are canonical. It is, however, better
engineering than silently baking one ambiguous interpretation into the only
possible calculation. It lets theory variants be compared explicitly.

## 4. CZSC — what to learn and what not to copy

### 4.1 Engineering value
- largest community of the reviewed group;
- strong tests and ongoing refactors;
- fast Rust/Python core;
- rich signal/event/position abstractions;
- current code exposes finished-Bi Zhongshu sequence helpers.

### 4.2 Not a canonical B1/S1 baseline
Current `check_first_buy/check_first_sell`:
- requires an odd Bi sequence and endpoint extreme geometry;
- compares last Bi power with prior/key Bis;
- uses price power plus volume or length power;
- does not implement the canonical requirement "two same-level non-overlapping
  Zhongshu -> trend -> departing movement divergence" as the standard B1 gate.

Therefore:
- use CZSC for engineering, causal signal composition, testing and execution;
- do NOT use its first-buy/sell helper as proof of original Chan semantics.

## 5. Cross-project finding that matters most for SiftAlpha

Our current design conflates two distinct questions:

1. **Where does the final Chan morphology say the buy/sell point belongs?**
2. **What information was actually available on the current Bar for trading?**

Mature systems do not solve this simply by waiting until every upper-level
structure becomes irreversible. Instead they expose provisional/current-frame
structure and later allow confirmation, modification or invalidation.

That means our current 29-bar median delay is not necessarily evidence that
Chan itself is inherently that late. It is partly a consequence of our policy:
`only canonical L1+ + fully stable structure -> emit formal signal`.

## 6. Direction for Round 2

Do NOT copy external formulas wholesale.

Next audit should build a common state model and then replay the same 79 stocks:

- CANDIDATE: current-frame structural BSP is present but the parent segment or
  Zhongshu is not irreversible.
- CONFIRMED: structure is confirmed under its own theory rule.
- INVALIDATED: a previous candidate is disproved by later bars.

For each external implementation, map:
- how early candidate B1/B2/B3 appears;
- what later invalidates it;
- how long confirmation takes;
- candidate survival rate;
- false candidate rate;
- next-bar performance from first appearance vs final confirmed appearance.

The comparison should specifically test:
A. our current strict L1+ confirmed-only logic;
B. chan.py-style provisional segment/BSP architecture;
C. chanlun-pro-style incremental current-frame BSP architecture.

The goal is not to maximize count. The goal is to find the earliest
theory-supported causal state whose invalidation rate and trading behavior are
acceptable.

No production change is admitted by Round 1.
