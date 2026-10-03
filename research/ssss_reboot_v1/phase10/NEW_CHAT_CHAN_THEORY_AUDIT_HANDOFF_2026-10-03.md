# NEW CHAT HANDOFF — Chan Theory-First Audit

Date: 2026-10-03  
Status: **MANDATORY_AUDIT_BEFORE_CONTINUING**

Repository:
`kuashan/siftalpha-research`

Primary working branch:
`feature/chan-standalone-v2`

Remote HEAD observed immediately before writing this handoff:
`e438ac9310beda084e547411d41b463c8459ba49`

---

## 0. Mandatory first action in the next conversation

Do **not** continue from conversational memory alone.

Before any research or code change:

1. Fetch / read the real remote HEAD of:
   `origin/feature/chan-standalone-v2`
2. Read this handoff file completely.
3. If remote HEAD has advanced beyond the commit that created this handoff,
   audit every new commit before continuing.
4. Re-read the current:
   - `integrations/sltd_v7_siftalpha_v1/chan_strategy.py`
   - `integrations/sltd_v7_siftalpha_v1/tests/test_chan_strategy.py`
   - `.github/workflows/chan-standalone-v2.yml`
5. Continue the **Theory-First canonical audit** before modifying any Chan formula.

The next conversation should begin by explicitly reporting:
- real remote HEAD;
- whether new commits appeared;
- whether this handoff was audited;
- the exact next audit step.

---

## 1. User's hard boundary — do not violate

The Chan strategy must be developed from Chan theory itself.

**Never modify the theory definition because one stock does not show B1/B2/B3/S1/S2/S3.**

Stocks are verification samples, not definition sources.

The rule hierarchy is frozen as:

1. Original `教你炒股票` source text;
2. later lessons / corrections / author replies inside the original corpus;
3. cross-comparison of multiple mature implementations / long-running community summaries;
4. explicit engineering choices where the original source is not uniquely machine-specifiable;
5. broad-sample validation;
6. individual stock examples only for debugging / verification.

A single stock, a screenshot, or signal frequency must never redefine Chan theory.

---

## 2. Chan is independent from SLTD/V7/E/5s

The `缠论` tab shares the existing web shell and market-data entry only.

The Chan engine itself must not use:
- SLTD BLUE / GRAY / GREEN;
- ZD1 / ZK1 / BS / BD;
- V7 rules;
- E rules;
- 5s rules;
- SLTD position state;
- SLTD C2.

Conceptually and computationally:

`CHAN = standalone structure strategy`

Do not optimize Chan to complement V7 during this audit.

---

## 3. Current product state

The current branch contains an independent Chan implementation shown in the same web package.

Current candidate version:
`独立缠论 v2.2`

The most recent successful package before this handoff was produced from the v2.2 line.

Important:
**v2.2 must NOT be treated as canonical-final merely because CI passed.**

Current correct status:

`CHAN_V2_2 = CANDIDATE_PENDING_THEORY_AUDIT`

The current task is to determine whether recent B1/B2/S1/S2 changes faithfully follow Chan theory
or over-modified the theory to increase visible signals.

---

## 4. Why this audit exists

The user noticed that early Chan builds showed mostly B3/S3 and few/no B1/B2/S1/S2.

That exposed real implementation issues, but it also created a dangerous temptation:
"change formulas until every stock shows all six labels."

That is explicitly forbidden.

The correct question is:

> Is each current formula justified by original Chan theory and later canonical clarification?

NOT:

> Does ABNB / AAPL / NVDA show enough labels?

---

## 5. Recent changes that MUST be theory-audited

### A. B1 / S1 no longer require C to make a new extreme

Current idea:
- valid same-level trend structure exists;
- C / leaving movement is outside the last Zhongshu;
- if C fails to make a new high/low, that itself represents weaker force;
- if C makes a new extreme, then compare force vs the prior same-direction movement.

Source basis cited during work:
- lesson 38 discussion that failure to make a new extreme itself indicates weakness.

Audit requirement:
- verify original wording and surrounding context;
- ensure "outside Zhongshu" and "trend structure" are correctly represented;
- confirm this is not being overgeneralized.

Current preliminary assessment:
`LIKELY_SOURCE_SUPPORTED`, but must be formally audited.

### B. Removed proprietary `0.25 × DIF` hard gate from B1/S1

An earlier implementation required a numerical MACD/DIF reset threshold that was not sourced to the original theory.

Current idea:
- MACD is an auxiliary force measure;
- no unsourced fixed `0.25 × DIF` eligibility threshold.

Audit requirement:
- verify original source treatment of MACD / zero-axis return;
- distinguish structural definition from indicator assistance.

Current preliminary assessment:
`LIKELY_CORRECT_REMOVAL`.

### C. B2 / S2 no longer require an emitted B1 / S1

Current idea:
- second-class points can exist in cases where a standard same-level first-class point is absent,
  especially small-level-to-large-level transitions;
- detect the first rebound / retracement after a confirmed structural low/high.

Source basis cited during work:
- lessons 53 and 101.

Audit requirement:
- verify the exact structural sequence and level relationship;
- make sure current code does not classify every ordinary pullback as B2/S2.

Current preliminary assessment:
`SOURCE_SUPPORTED_IN_PRINCIPLE`, implementation details still need audit.

### D. B2 / S2 may still exist after a new low/high if consolidation divergence exists

Current idea:
- no-new-low/high is one case;
- new low/high plus valid consolidation divergence is another possible B2/S2 case.

Source basis cited:
- lesson 53 / later summary of second-class point cases.

Audit requirement:
- verify exact original definition and whether the code's force comparison truly represents
  the required consolidation divergence;
- inspect both BUY and SELL symmetry.

Current preliminary assessment:
`NEEDS_DEEP_AUDIT`.

### E. Same-level trend relationship remains strict GG/DD

Do **not** loosen this merely to increase B1/S1 counts.

Original relation already rechecked during this work:
- later center `GG < prior DD` -> downward relation;
- later center `DD > prior GG` -> upward relation;
- weaker ZG/ZD separation with outer-range overlap can imply higher-level center formation rather than same-level trend continuation.

Source basis:
- lesson 20.

Current preliminary assessment:
`CONFIRMED_DO_NOT_LOOSEN_FOR_SIGNAL_COUNT`.

### F. B3 / S3

Current B3/S3 frequency is much larger than B1/S1.

Do **not** automatically conclude B3/S3 are wrong only because they are frequent.

But perform a canonical audit of:
- what counts as leaving a Zhongshu;
- what exactly is the "first" lower-level return;
- whether the return must be a completed lower-level trend type rather than merely a Bi / engineering unit;
- whether current L0 Bi-level Zhongshu use is canonical or an engineering proxy.

Status:
`REQUIRES_THEORY_AUDIT`.

---

## 6. Structural chain that must be audited before calling the engine canonical

Audit in this order:

1. raw K inclusion handling;
2. top/bottom fractal;
3. Bi;
4. feature sequence;
5. segment;
6. Zhongshu;
7. consolidation vs trend;
8. structural level recursion;
9. consolidation divergence vs trend divergence;
10. B1 / S1;
11. B2 / S2;
12. B3 / S3;
13. multi-level linkage / interval nesting;
14. anchor time vs first-observed confirmation time.

Do not skip directly to B/S.

---

## 7. Original-source lessons to prioritize

At minimum re-audit:

- 17
- 20
- 21
- 24
- 27
- 31
- 38
- 44
- 53
- 61
- 62
- 65
- 67
- 71
- 72
- 77
- 78
- 79
- 80
- 81
- 91
- 93
- 101
- 105
- 106

Also inspect replies / corrections around those lessons.

Important known principle:
later strict definitions / corrections override earlier loose descriptions where the source explicitly revises them.

---

## 8. Open-source implementations to compare, not blindly copy

Cross-check at least:

- `Vespa314/chan.py`
- `waditu/czsc`
- `yijixiuxin/chanlun-pro`
- `mikonos/chanlun-kline`
- `neil-pan-s/one-quant-doc`

For each disputed rule, classify:

- `ORIGINAL_CANONICAL`
- `LATER_SOURCE_CLARIFICATION`
- `COMMON_ENGINEERING_INTERPRETATION`
- `IMPLEMENTATION_SPECIFIC_OPTION`
- `UNSUPPORTED_EXTENSION`

Do not use GitHub stars as a definition authority.

---

## 9. Important causal / repaint rule

The Chan chart can display a structural anchor at the historical turning point.

But strategy research must separately preserve:

- `ANCHOR_TIME`
- `CONFIRM_TIME`

A signal may only be considered known at its first real confirmation time.

Historical final labels must not be backdated into a trading signal.

The intended discipline remains:

`completed bar confirms -> next selected-timeframe bar open may execute`

This is the Chan equivalent of the existing FIRST_OBSERVED discipline.

---

## 10. Current empirical diagnostics — validation only, NOT theory evidence

These numbers were used only to detect implementation imbalance.

At one v2.2 diagnostic point across the 79-stock data snapshot:

- B1: 32
- B2: 530
- B3: 841
- S1: 118
- S2: 551
- S3: 510

Do not optimize these counts toward equal frequencies.

B1/S1 are structurally stricter and may naturally be rarer.

Real-stock examples were used only to verify the UI / engine can emit classes:
- ADBE used to verify B1 visibility;
- NVDA used to verify S1 visibility;
- ABNB used to verify B2/S2 and B3/S3 visibility.

These examples must never become formula-definition evidence.

---

## 11. Current theory-audit task that was IN PROGRESS when chat ended

The user instructed:

> First perform the canonical theory audit.
> After the audit, check whether the recent changes were over-modifications.
> If they were not over-modified, leave them alone.

Therefore the next work is:

### Step T1 — Freeze a canonical Chan definition matrix

Produce a source-backed matrix for:
- Zhongshu relation;
- trend divergence;
- consolidation divergence;
- B1/S1;
- B2/S2;
- B3/S3;
- recursive level semantics.

For every rule record:
- source lesson;
- exact conceptual condition;
- later clarification;
- implementation ambiguity;
- chosen engineering interpretation;
- confidence.

### Step T2 — Audit v2.2 against the matrix

For every recent change, label:
- `KEEP_AS_CANONICAL`
- `KEEP_AS_ENGINEERING_CHOICE`
- `REVISE_OVERMODIFIED`
- `REJECT_UNSUPPORTED`

### Step T3 — Only if T2 finds a real mismatch, modify code

No code changes merely to alter signal counts.

### Step T4 — Regression after theory correction

Only after source-driven corrections:
- unit fixtures;
- broad-stock structural diagnostic;
- FIRST_OBSERVED replay;
- UI visibility;
- package CI.

---

## 12. Files to read first in the next conversation

Mandatory:

1. this file;
2. `research/ssss_reboot_v1/phase10/CHAN_THEORY_ENGINEERING_BOUNDARY_v1.md`
3. `research/ssss_reboot_v1/phase10/CHAN_SLTD_RESEARCH_PROTOCOL_v1.md`
4. `research/ssss_reboot_v1/phase10/CHAN_C0A_RECONSTRUCTION_CLOSURE_v1.md`
5. `integrations/sltd_v7_siftalpha_v1/chan_strategy.py`
6. `integrations/sltd_v7_siftalpha_v1/tests/test_chan_strategy.py`
7. `.github/workflows/chan-standalone-v2.yml`

Also inspect any newer phase10 Chan audit / diagnostic files that appeared after this handoff.

---

## 13. Do not conflate these two projects

There are two related but distinct research directions:

### Standalone Chan product
Current immediate focus.
Goal:
build a faithful independent Chan strategy / structure engine in the `缠论` tab.

### CHAN × SLTD complementarity research
Separate research protocol.
Do not resume it until the standalone Chan canonical audit is stable.

The user currently wants the standalone Chan theory to remain faithful first.

---

## 14. Required next-conversation opening response

After reading real remote state and this handoff, the next assistant should begin approximately with:

> 已读取真实远端和续接审计日志。
> 当前 HEAD = <real sha>.
> 我已审计从日志基准到当前 HEAD 的新增提交。
> 当前任务不是继续调股票信号，而是完成 Theory-First 缠论原典标准化审计。
> 先冻结定义矩阵，再判断 v2.2 最近修改是否属于过度修改；没有问题的部分保持不动。

Do not ask the user to repeat this history unless the repository no longer contains the required files.

---

## 15. Closure marker

`NEW_CHAT_CHAN_THEORY_AUDIT_HANDOFF = READY`

Next conversation must audit this file before continuing.
