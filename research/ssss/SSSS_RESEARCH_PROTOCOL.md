# SSSS Research Protocol

Last updated: 2026-09-19

Purpose: prevent sample leakage, post-hoc cohort selection, and accidental reuse of already-seen OOS data.

## Mandatory pre-registration before every new research round

Before any result for a new research round is computed, inspected, summarized, or used to change a rule, the round must be pre-registered in the repository.

The pre-registration must contain:

1. Experiment ID.
2. Research question / hypothesis.
3. Exact candidate rule or feature definition being tested.
4. Discovery ticker list.
5. OOS ticker list.
6. Frozen OOS ticker list.
7. Date range for each cohort.
8. Whether each ticker overlaps any prior research cohort.
9. Whether each cohort belongs to the official 45-stock baseline.
10. Execution convention, including signal timing and next-open execution where applicable.
11. Primary evaluation metrics and rejection / retention criteria.
12. Status = PRE-REGISTERED.

The pre-registration must be committed to `main` before results are viewed.

## Required sequence

The default sequence is:

```text
PRE-REGISTER
-> commit cohort lists and protocol to main
-> Discovery
-> freeze candidate rule
-> OOS
-> decide whether the candidate survives
-> freeze the surviving rule again if necessary
-> Frozen OOS
-> final decision
-> update research log, experiment ledger, state machine, current state, and checkpoint
```

## Discovery

Discovery may be used to generate or refine hypotheses.

Changes made after inspecting Discovery are allowed, but they create a new frozen candidate definition for OOS. The final OOS rule must be written down before OOS results are viewed.

## OOS

OOS is a validation stage, not a second Discovery stage.

Do not tune thresholds, add exceptions, remove inconvenient tickers, or alter execution rules after inspecting OOS and still call the same result OOS.

If the rule changes after OOS, create a new Experiment ID and pre-register a new split.

## Frozen OOS

Frozen OOS is the final untouched validation layer for that research round.

A result may be called Frozen OOS only if:

- the exact Frozen OOS ticker list was committed before any Frozen OOS result was viewed;
- the rule was frozen before Frozen OOS was opened;
- the date range and execution convention were frozen;
- no ticker was added, removed, or substituted after results were known.

If any of these conditions are violated, the result must be relabeled as exploratory / previously seen data and cannot be used as Frozen OOS evidence.

## Cohort mutation rule

Once a research round has been pre-registered, changing Discovery, OOS, or Frozen OOS membership invalidates the original pre-registration for the changed cohort.

Do not silently edit the cohort and continue under the same Experiment ID.

Create a new Experiment ID and commit the new split before running it.

## Data leakage rule

Previously inspected assets are not automatically eligible for a new Frozen OOS role.

Any overlap with prior research must be explicitly recorded. Previously seen tickers may still be useful for robustness analysis, but they must not be represented as untouched Frozen OOS.

## Repository records

Every new round must update or create, before results:

- `SSSS_SAMPLE_SPLITS.md`
- `SSSS_SAMPLE_SPLITS.csv`

The round should also create a dated checkpoint or pre-registration record when useful.

After results, update as applicable:

- `SSSS_EXPERIMENTS.csv`
- `SSSS_RESEARCH_LOG.md`
- `SSSS_CURRENT_STATE.md`
- `SSSS_STATE_MACHINE.md`
- `models/ssss_current.py`
- dated checkpoint

Do not modify `models/ssss_core_v0_1.py`.

## Governing principle

Sample assignment must be decided before outcome inspection.

No attractive result is allowed to change which data are called Discovery, OOS, or Frozen OOS after the fact.


## Mandatory pre-round duplication audit

Before assigning or pre-registering any new Experiment ID, perform a repository duplication audit.

At minimum re-read:

- `SSSS_EXPERIMENTS.csv`
- `SSSS_RESEARCH_LOG.md`
- `SSSS_CURRENT_STATE.md`
- `SSSS_STATE_MACHINE.md`
- `SSSS_SAMPLE_SPLITS.md`
- `SSSS_SAMPLE_SPLITS.csv`
- relevant prior preregistrations
- relevant prior checkpoints
- current mutable model notes

The new round must explicitly classify its relationship to prior work as one of:

- NEW: materially new hypothesis / feature family
- PARTIAL_OVERLAP: shares some ingredients but tests a materially different hypothesis
- REPLICATION: intentionally repeats a prior test for robustness
- DUPLICATE: substantially the same rule / feature / cohort question already tested

A DUPLICATE round must not be opened under a new Experiment ID merely by renaming an indicator or making cosmetic threshold changes.

For PARTIAL_OVERLAP or REPLICATION, the pre-registration must state:
- which prior experiment(s) overlap;
- what is materially different;
- why the new test is still informative;
- which previous failures or findings must remain constraints.

For indicator research, verify not only the indicator name but also whether the underlying information family has already been tested.
Examples:
- a new moving-average formula may still duplicate prior trend-direction research;
- a new volume indicator may overlap with a previously rejected generic volume hard filter, while still being materially different if it measures money-flow or divergence rather than raw volume;
- a new multi-timeframe feature must acknowledge the rejected hard 2D MTF filter and cannot silently recreate it.

Do not inspect new empirical outcomes until this duplication audit has been recorded in the pre-registration or research notes.
