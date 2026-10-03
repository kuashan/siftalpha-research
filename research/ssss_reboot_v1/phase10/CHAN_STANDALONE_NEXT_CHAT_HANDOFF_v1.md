# Chan Standalone v2 — Next Chat Audit Handoff

Status: **MANDATORY_NEXT_CHAT_AUDIT**
Recorded at: 2026-10-03
Repository: `kuashan/siftalpha-research`
Branch: `feature/chan-standalone-v2`
Recorded remote HEAD: `e438ac9310beda084e547411d41b463c8459ba49`

---

## 0. NEXT CHAT — FIRST ACTION ONLY

Before continuing any Chan work:

1. `git fetch` / read the true remote HEAD of:
   `origin/feature/chan-standalone-v2`
2. Compare it with the recorded HEAD above.
3. If the branch advanced, audit **every new commit first**.
4. Read and audit this handoff file completely.
5. Re-read the current `chan_strategy.py` and relevant tests from the real remote.
6. Do **not** continue from conversation memory alone.
7. Do **not** modify Chan formulas until the theory-first audit below is completed.

Repository is the source of truth.

---

## 1. USER'S HARD BOUNDARY

The standalone Chan strategy must be developed from Chan theory itself.

**Never modify Chan definitions because one stock does not show a desired signal.**

A stock is allowed to:
- expose a bug;
- falsify an implementation;
- validate that a structure can appear;
- provide a visual regression case.

A stock is **not allowed** to define or loosen:
- fractal;
- Bi;
- segment;
- Zhongshu;
- trend level;
- divergence;
- B1/B2/B3;
- S1/S2/S3.

The governing order is:

1. original `教你炒股票` source;
2. later original corrections / replies;
3. cross-check of multiple mature Chan implementations / community summaries;
4. frozen mathematical definition;
5. broad-market validation;
6. single-stock visual examples last.

**THEORY FIRST, DATA SECOND, SINGLE STOCK LAST.**

If source theory and a desired chart result conflict, keep the theory and accept that the signal does not exist.

---

## 2. STRATEGY INDEPENDENCE

The `缠论` tab is a standalone strategy / structure engine.

It must **not** read or depend on:

- SLTD BLUE / GRAY / GREEN;
- ZD1 / ZK1 / BS / BD;
- V7 BUY / SELL rules;
- V7 C2;
- E strategy;
- 5s Stocks;
- any SLTD position state.

It may share only:
- normalized OHLCV;
- market-data router;
- web-page shell;
- chart container.

Current integrated page still exposes:
`12条策略 | E | 5s Stocks | 缠论`

But the Chan engine itself is independent.

---

## 3. CURRENT PRODUCT VERSION

Current candidate:
`独立缠论 v2.2`

Current implementation:
`integrations/sltd_v7_siftalpha_v1/chan_strategy.py`

Current tests:
`integrations/sltd_v7_siftalpha_v1/tests/test_chan_strategy.py`

Current CI:
`.github/workflows/chan-standalone-v2.yml`

Last known successful packaging CI before this handoff:
- Run: `37092520343`
- Result: **SUCCESS**

Last generated package:
`SLTD-独立缠论-v2.2.zip`

Do not call v2.2 a final canonical Chan implementation yet.

Correct status:

`CHAN_V2_2 = CANDIDATE_PENDING_THEORY_AUDIT`

---

## 4. WHY THE THEORY-FIRST AUDIT WAS STARTED

User correctly raised a critical boundary concern:

> Chan cannot be changed because one stock lacks B1/B2/S1/S2. Otherwise the implementation becomes overfit and is no longer Chan.

This concern came after ABNB visually showed mainly B3/S3.

The investigation found two categories:

### A. Genuine implementation defects

Some prior formulas were too restrictive or structurally wrong.

### B. Legitimate scarcity

Standard B1/S1 are intrinsically rarer because they require a same-level trend and divergence.

Therefore:
- "not visible on ABNB" is not itself a bug;
- a rule is changed only when source theory supports the change.

---

## 5. V2.2 CHANGES THAT ALREADY HAVE SOURCE-THEORY SUPPORT

These changes must be re-audited, but current evidence supports them.

### 5.1 Removed proprietary `0.25 × DIF` hard gate from B1/S1

Older code required a numerical MACD pull-to-zero threshold:
`0.25 * enter_DIF`.

That number was an engineering filter, not a canonical Chan rule.

Current direction:
- trend structure first;
- MACD only assists force comparison;
- do not use the private 0.25 constant as a mandatory eligibility gate.

### 5.2 B1/S1 no longer require C to make a new extreme

Source lesson 38 was used to correct this.

Current intended logic:

same-level trend exists
+
C leaves the final Zhongshu
+
(
  C fails to make a new high/low
  OR
  C makes a new high/low but force is weaker than B
)

This is important:
- "cannot even make a new extreme" is itself evidence that C is weaker;
- do not require `new_extreme AND weaker`.

### 5.3 Keep strict same-level trend relation using GG/DD

Do **not** casually loosen this to ZD/ZG just to create more B1/S1.

The audit rechecked lesson 20:

- later Zhongshu `GG < previous DD` -> downward trend relationship;
- later Zhongshu `DD > previous GG` -> upward trend relationship;
- ZD/ZG separation with overlapping outer ranges can instead imply a higher-level Zhongshu / expansion case.

So the strict GG/DD relationship is currently considered source-consistent.

### 5.4 B2/S2 are not hard-dependent on emitted B1/S1

This was corrected using lessons 53 / 101.

Reason:
- small-level-to-large-level transitions can lack a standard same-level B1/S1;
- a valid second-class point may still appear.

Current intended B2/S2 structure:
- a confirmed structural high/low;
- one opposite movement away;
- the first return;
- no new extreme, **or** an allowed consolidation-divergence case.

### 5.5 B2/S2 consolidation-divergence case

A parallel commit admitted:
- B2 can still exist if the return makes a slightly lower low but has consolidation divergence;
- S2 can still exist if the return makes a slightly higher high but has consolidation divergence.

This was reviewed against lesson 53 and is provisionally considered source-supported.

This still requires full canonical audit.

---

## 6. CURRENT SIGNAL DISTRIBUTION IS NOT A RULE-DEFINITION TARGET

Do not optimize toward equal counts.

Latest broad historical diagnostic after the repairs reported roughly:

- B1: 32
- B2: 530
- B3: 841
- S1: 118
- S2: 551
- S3: 510

Earlier v2.1 counts were approximately:
- B1: 25
- B2: 527
- B3: 841
- S1: 103
- S2: 544
- S3: 510

These numbers are **diagnostic only**.

They must never be used as a reason to loosen/tighten definitions.

A rare B1/S1 is acceptable if the theory says it is rare.

---

## 7. REAL-MARKET CASES — VALIDATION ONLY

These symbols were used only to verify that code paths can emit visible classes:

- ADBE: visible B1 sample
- NVDA: visible S1 sample
- ABNB: visible B2 / S2 / B3 / S3 sample

Do not treat these symbols as formula-design sources.

ABNB specifically must not be used as:
"ABNB has no B1 -> change B1."

Correct interpretation:
"If ABNB does not satisfy canonical B1, no B1 should be displayed."

---

## 8. CAUSALITY CONTRACT

This remains non-negotiable.

For every structure, store separately:

- `anchor_time` / anchor index:
  where the structure belongs visually;
- `confirm_time` / first-observed index:
  when the structure first becomes knowable.

Trading / event timing must use:
`FIRST_OBSERVED confirm_time`.

Never:
- use final historical B/S labels as if they were known at the anchor;
- use BACKSET-like historical placement as a trade timestamp;
- use future-completed structure to rewrite an earlier trading decision.

The current implementation contains:
`replay_first_observed_signals`

This must itself be audited, especially:
- provisional structure invalidation;
- disappearing/reassigned segment endpoints;
- Zhongshu evolution;
- recursive-level changes.

---

## 9. IMPORTANT CURRENT ENGINE COMPONENTS

Current chain aims to implement:

```
Raw K
-> inclusion handling
-> fractal
-> valid Bi endpoint
-> strict Bi
-> feature-sequence segment
-> L0 Bi-level Zhongshu
-> L1 segment-level Zhongshu
-> trend / consolidation type
-> recursive higher levels
-> divergence
-> B1/B2/B3/S1/S2/S3
-> FIRST_OBSERVED signal ledger
```

Current default chart display:
- only valid Bi endpoints are shown as top/bottom;
- all raw fractals are not displayed by default;
- Bi lines;
- segment lines;
- Zhongshu boxes;
- multi-level labels;
- B1/B2/B3/S1/S2/S3 markers.

---

## 10. THEORY-FIRST AUDIT — CURRENT STATUS

Audit is **NOT COMPLETE**.

Do not claim canonical closure yet.

Already revisited:
- B1/S1 trend relation;
- lesson-38 non-new-extreme divergence case;
- B2/S2 independence;
- B2/S2 consolidation-divergence case;
- GG/DD vs ZG/ZD trend relationship.

Still must be audited carefully:

### 10.1 Inclusion handling
- exact direction determination at sequence start;
- containment merge rules;
- whether current engineering start-direction convention is acceptable.

### 10.2 Fractal
- strict top/bottom after inclusion;
- anchor/confirm timing.

### 10.3 Bi
Current implementation uses a strict lesson-77-style convention.

Need re-audit:
- lesson 77 vs later lesson 106 discussion;
- exact minimum separation;
- same-type fractal replacement;
- endpoint price overlap constraints.

Do not choose Bi variant by PnL.

### 10.4 Segment
Need re-audit:
- lesson 67 feature sequence;
- first / second segment-break situations;
- lessons 71 / 78 clarification;
- lesson 81 corrected example;
- cancellation/recovery of an unfinished segment.

This is high priority.

### 10.5 Zhongshu
Need re-audit:
- canonical definition = overlap of at least three consecutive lower-level trend units;
- distinguish canonical Zhongshu from engineering Bi-overlap proxy;
- extension;
- expansion;
- level upgrade;
- departure / return boundary;
- whether current v2.2 L0 Bi-level Zhongshu should be labeled a proxy rather than fully canonical.

This is **very important**.

### 10.6 Structural level / recursion
Need re-audit:
- timeframe is not structural level;
- trend type recursion;
- same-level decomposition;
- combination law / uniqueness;
- whether current `build_trend_types` and `build_levels` are faithful enough.

Do not assume current recursive implementation is canonical just because it runs.

### 10.7 Divergence
Need re-audit:
- trend divergence;
- consolidation divergence;
- structural prerequisite;
- B-vs-C force comparison;
- MACD as auxiliary measurement only;
- no accidental conversion of ordinary MACD divergence into canonical Chan divergence.

### 10.8 B1 / S1
Re-audit full `a+A+b+B+c` context:
- same-level trend;
- final Zhongshu;
- C movement;
- non-new-extreme case;
- force comparison;
- exact first-observed confirmation.

### 10.9 B2 / S2
Re-audit:
- standard B1/S1-following form;
- small-to-large transition without B1/S1;
- consolidation-divergence form;
- exact relation to the structural high/low;
- whether current `parent_turns` abstraction matches the source definition.

### 10.10 B3 / S3
This has **not yet received the same depth of theory audit** as B1/B2/S1/S2.

Must re-audit:
- full lower-level departure;
- first lower-level return;
- "not re-enter Zhongshu";
- distinction between "last absorbed unit already leaves" vs "explicit next departure";
- current two-form engineering implementation;
- source support for both forms;
- whether current B3/S3 frequency is inflated.

Do not change B3/S3 based on count alone.

---

## 11. OPEN-SOURCE COMPARISON POLICY

Use several implementations only as cross-checks:

- `Vespa314/chan.py`
- `waditu/czsc`
- `yijixiuxin/chanlun-pro`
- `mikonos/chanlun-kline`

Never treat any one repository as canonical truth.

For every disagreement record:

- original-source definition;
- implementation A;
- implementation B;
- current SiftAlpha choice;
- why the choice was made;
- whether it is canonical or engineering.

---

## 12. NEXT CHAT REQUIRED DELIVERABLE

The next chat should first produce:

### `CHAN_CANONICAL_THEORY_AUDIT_v1`

It must classify every major rule as one of:

- `CANONICAL_SOURCE_CONFIRMED`
- `LATER_SOURCE_CLARIFICATION`
- `ENGINEERING_CHOICE_EXPLICIT`
- `COMMUNITY_VARIANT_NOT_CANONICAL`
- `NEEDS_CORRECTION`

Then audit the current v2.2 implementation against that document.

Only after this audit:

- if v2.2 changes are source-supported -> keep them;
- if something was over-modified -> correct only that part;
- if no over-modification is found -> leave it alone.

Do not rewrite working code merely to "clean it up."

---

## 13. NO-PNL / NO-OPTIMIZATION DURING THEORY AUDIT

During canonical audit:

- no PnL optimization;
- no parameter sweep;
- no per-symbol tuning;
- no signal-count target;
- no requirement that every chart show all six BSP classes;
- no SLTD/V7 interaction;
- no strategy-performance admission decision.

The sole question is:

> "Does the implementation faithfully represent the selected Chan-theory definition in a causal, reproducible form?"

---

## 14. RESEARCH DISCIPLINE

Always:

1. read real remote HEAD;
2. audit branch drift first;
3. use repository state, not memory;
4. preserve exact commit SHA;
5. write important conclusions back to repository;
6. distinguish theory definition from trading policy;
7. distinguish anchor from confirm time;
8. close each phase explicitly;
9. reply in Chinese;
10. do not claim COMPLETE until the defined closure gate passes.

---

## 15. NEXT CHAT COPYABLE START INSTRUCTION

Use this exact instruction in the new conversation:

> 继续独立缠论研究。不要根据旧对话记忆直接继续，也不要先改代码。先读取私有仓库 `kuashan/siftalpha-research` 的真实远端分支 `feature/chan-standalone-v2`，核对真实 HEAD；然后首先审计：
> `research/ssss_reboot_v1/phase10/CHAN_STANDALONE_NEXT_CHAT_HANDOFF_v1.md`
> 如果远端 HEAD 已经超过日志记录的 SHA，先审计所有新增提交。之后按日志要求继续 `CHAN_CANONICAL_THEORY_AUDIT_v1`，完成原典优先的标准化审计，再回头判断 v2.2 是否有过度修改。任何单只股票都只能用于验证，不能用于定义或放宽缠论公式。

---

`CHAN_NEXT_CHAT_HANDOFF = READY_FOR_AUDIT`
