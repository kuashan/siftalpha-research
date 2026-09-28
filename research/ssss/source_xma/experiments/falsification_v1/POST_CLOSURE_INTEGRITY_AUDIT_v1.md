# Falsification v1 — Post-Closure Integrity Audit

Status: **TERMINAL INTEGRITY CORRECTION / NO SIGNAL RESCUE**  
Date: 2026-09-28  
Audited branch: `research/source-xma-walkforward`  
Pre-audit branch HEAD: `98ce8ec7e357ed6cf8774cf68cafe7355bd4ce70`  
Earlier frozen-baseline reference: `a827b995f4325263a47c74f00beb81b9d1eb9160`

## Purpose

This audit does **not** reopen failed trading hypotheses and does not search for a favorable result.

It checks whether the repository state that marked Falsification v1 CLOSED is fully consistent with the previously frozen governance rules.

The core trading classifications remain unchanged:

- Upper strict confluence => general top / decline rule: **REJECT**
- Lower strict confluence => incremental buy / rebound rule: **REJECT**
- common state transitions / midpoint / transition paths: **OBSERVE / NOT PROMOTED**
- unavailable auxiliary holdout tests: **INCONCLUSIVE / DATA NOT AVAILABLE**
- HYS2 fire-bottom / fire-top: **REDUNDANT WITHIN STRICT XMA EVENT SAMPLE** only

However, the previous statement that v1 was a clean closure with 2026H1 still fully sealed is not supportable.

---

## 1. Sealed-window boundary breach

The frozen protocol states:

> 2026-01-01 through 2026-06-30 is NOT used in Validation A/B.

The previous closure check verified only that no **event date** was in 2026.

That check is insufficient because Validation B events near the end of 2025 can have forward-return outcome dates in 2026.

### Confirmed equity confluence examples

Across the persisted 783 equity confluence events:

Validation B Upper:
- raw n = 46
- one 5-bar outcome crosses into 2026:
  - BAC event 2025-12-29 -> date5 2026-01-06
- three persisted 20-bar outcomes cross into 2026:
  - AVGO 2025-12-11 -> 2026-01-12
  - MU 2025-12-09 -> 2026-01-08
  - PLD 2025-12-10 -> 2026-01-09

Validation B Lower:
- raw n = 20
- one 10-bar outcome crosses into 2026:
  - COST 2025-12-17 -> date10 2026-01-02
- four 20-bar outcomes cross into 2026:
  - MSFT 2025-12-03 -> 2026-01-02
  - MSFT 2025-12-16 -> 2026-01-15
  - NFLX 2025-12-03 -> 2026-01-02
  - COST 2025-12-17 -> 2026-01-16

Therefore 2026H1 outcome data were persisted and used by at least some Validation B forward-return calculations.

### Event-horizon-only sensitivity

If events whose **own required horizon** crosses 2025-12-31 are removed, without changing any threshold:

- Upper B 5-bar raw:
  - original n=46, mean about -0.631%
  - within-2025 event horizon n=45, mean about -0.721%

- Lower B 10-bar raw:
  - original n=20, mean about -0.966%
  - within-2025 event horizon n=19, mean about -0.967%

- Lower B 20-bar raw:
  - original n=20, mean about -1.694%
  - within-2025 event horizon n=16, mean about -1.748%

These checks do **not** rescue either hypothesis.

### Matched-control limitation

For the matched artifacts, event-horizon-only exclusion gives:

- Upper B 5-bar:
  - original matchable n=39, mean matchEx about -1.668%
  - event-horizon-safe n=38, about -1.878%

- Lower B 10-bar:
  - original matchable n=12, about -1.393%
  - event-horizon-safe n=11, about -1.531%

- Lower B 20-bar:
  - original matchable n=12, about -2.757%
  - event-horizon-safe n=11, about -4.238%

These are **not promoted as corrected matched estimates**.

Reason:
v1 did not persist the identities/dates of the five selected controls. Therefore it is impossible to verify that every matched-control forward horizon also remained inside 2025.

Required classification for clean boundary compliance of B matched estimates:

**NOT CLEANLY AUDITABLE FROM PERSISTED CONTROL-LEVEL DATA.**

This does not create a positive result. It weakens provenance, not the REJECT decision.

---

## 2. Midpoint / transition forward-return leakage

`TRANS_MID_CHUNK3.json` alone contains at least eight Validation B records whose stored forward-outcome date enters 2026:

- MID_UP: 3
- MID_DOWN: 4
- TRANSITION: 1

Example:
- PLD MID_DOWN on 2025-12-31
- date5 = 2026-01-08
- date10 = 2026-01-15

`TRANSITION_MIDPOINT_SUMMARY.json` reports Validation B midpoint forward-return summaries using the persisted transition/midpoint chunks.

Therefore the B midpoint return summaries are not cleanly isolated from the sealed 2026H1 outcome period.

Important distinction:
`TIME_TO_CONFIRM_SURVIVAL_STOCK_v1.json` explicitly right-censors at the frozen validation-window end. That survival analysis is governed differently and is not automatically invalidated by this finding.

Decision:
midpoint remains **OBSERVE / NOT PROMOTED**.
No directional rule is rescued.

---

## 3. State Density Validation B coverage inconsistency

`STATE_DENSITY_AUDIT_v1` reports:

- Validation B bounds ending 2025-12-30
- 127 trading bars x 39 symbols = 4,953 state bars

But the frozen Validation B end is 2025-12-31, and the persisted transition/midpoint artifacts contain 2025-12-31 records.

Therefore the State Density B reconstruction is short by one trading day relative to the frozen window.

This is an integrity / denominator issue, not evidence of a trading edge.

The existing density conclusion remains descriptive only:
**OBSERVE / CONTEXT ONLY.**

The B percentages should not be represented as full-window 2025-07-01..2025-12-31 occupancy until the missing final day is reconstructed from preserved point-in-time state data.

---

## 4. Transition Path protocol drift after the documented freeze

At commit `a827b995...`, the file
`TRANSITION_PATH_PROTOCOL_FROZEN_BEFORE_ANALYSIS.md`
was already marked frozen before outcome analysis.

The later repository version materially changes that protocol.

Substantive changes include:

1. waiting-window semantics:
   - earlier frozen text: one 60-bar waiting window from the anchor RANGE entry to the next RANGE exit;
   - later text: 60 bars **per transition step**, so a random control may receive up to 60 bars to enter RANGE and then another 60 bars after RANGE entry;

2. control eligibility:
   - earlier: control bar is not itself the anchor transition;
   - later: control bar is not **any** state-transition bar;

3. added random-control categories:
   - NO_RANGE_ENTRY_60
   - DIRECT_EXIT_NO_RANGE

4. added unconditional and RANGE-entry-conditional baseline reporting.

These are methodological changes, not wording-only edits.

No separate numbered protocol amendment is preserved in the audited artifact set proving these changes were frozen before path outcomes were computed.

Therefore the transition-path result must carry:

**PROTOCOL-INTEGRITY CAVEAT / OBSERVE / NOT PROMOTED.**

Do not rerun or subdivide the same holdout to search for a better path effect.

The negative/non-promotional interpretation remains conservative.

---

## 5. BH-FDR preregistration was not fully executable

The original frozen protocol required the primary family to be controlled with:

**Benjamini-Hochberg FDR q=0.10.**

The final Hypothesis Ledger correctly documents that a complete BH vector cannot be reconstructed without post-hoc choices because:

- some expanded-holdout feature tests are DATA NOT AVAILABLE;
- some family items did not freeze one unique scalar p-like statistic.

Therefore:

- no BH-adjusted positive claim exists;
- no result is promoted;
- but it is inaccurate to say that the preregistered BH-FDR computation was completed.

Terminal integrity classification:

**BH-FDR FAMILY: INCONCLUSIVE / NOT FULLY COMPUTABLE AS PREREGISTERED.**

This is a v1 protocol-design limitation to fix prospectively, not a reason to mine another statistic.

---

## 6. Effect on core v1 decisions

### Upper strict confluence

Still **REJECT**.

Reason:
- Validation A is approximately neutral/slightly positive;
- Validation B remains negative on raw 5-bar return even after removing the one event whose own 5-bar horizon crosses into 2026;
- A/B direction consistency therefore still fails.

No Regime rescue is allowed.

### Lower strict confluence

Still **REJECT**.

Reason:
- Validation A matched excess is strongly negative relative to the registered positive incremental-buy proposition;
- Validation B raw returns remain negative under within-2025 event-horizon restriction;
- the boundary issue does not create positive incremental evidence.

### Transition / midpoint

Remain:
**OBSERVE / NOT PROMOTED.**

The integrity findings reduce confidence in exact B estimates; they do not justify a trading rule.

---

## 7. Correct closure status

The appropriate terminal status is:

**FALSIFICATION v1 = CLOSED WITH INTEGRITY QUALIFICATIONS**

Meaning:

- no v1 failed hypothesis is reopened or repaired;
- no new favorable split is searched;
- no v1 trading rule is promoted;
- the closure keeps all negative / non-promotional terminal decisions;
- known protocol/data-boundary defects are explicitly preserved rather than hidden.

Most importantly:

**2026H1 must no longer be described or used as an untouched sealed v2 holdout.**

It has been exposed through persisted forward outcomes.

Any future v2 needs:
- a new prospectively preregistered independent time window; or
- a new frozen universe with independently protected outcomes.

No new v2 hypothesis is opened by this audit.
