# SSSS Historical Feature Audit

Date: 2026-09-19

Purpose:
prevent duplicated research by reconstructing which information families and feature ideas have already been tested in retained SSSS research.

This document is a duplication audit, not a new experiment result.

## Evidence sources checked

- SSSS_EXPERIMENTS.csv
- SSSS_RESEARCH_LOG.md
- SSSS_CURRENT_STATE.md
- SSSS_STATE_MACHINE.md
- retained preregistrations and checkpoints referenced by the above files
- main-branch commit history
- current mutable model notes

Repository limitation discovered:
the retained repository records some early research conclusions without preserving every exact historical feature formula.

Therefore this audit distinguishes:
- exact prior test known
- prior information-family test known but exact formula unrecovered
- no retained evidence of prior test

## 1. Already tested — do not reopen under a new name

### Price/trend confirmation family

Previously tested and rejected/downgraded:
- MA30 location / slope
- A8 yellow confirmation
- A8 turn-up confirmation
- active SAR confirmation
- strong close above FastUpper
- fast-width expansion
- white-slope-up
- absolute white-width threshold
- fixed cycle-age threshold

Interpretation:
another ordinary trend-direction / moving-average confirmation is likely DUPLICATE unless its information content is materially different.

### Multi-timeframe hard-filter family

Previously tested:
- 2-day higher-timeframe hard confirmation

Decision:
rejected.

Constraint:
future multi-timeframe research may be PARTIAL_OVERLAP only if used as context / interaction / sizing information rather than silently recreating a mandatory hard gate.

### Market / sector / relative-strength hard-filter family

Previously tested and rejected:
- SPY bull filter
- sector bull filter
- stock > SPY relative-strength filter
- stock > sector relative-strength filter

Constraint:
future BTC-context research for crypto must acknowledge this family.
It may still be materially different because:
- asset class differs;
- BTC can be a market micro-regime driver for crypto;
- future use is proposed as context first, not hard filtering.

### Generic volume hard-filter family

Previously tested:
- volume hard filter

Decision:
rejected/downgraded.

Critical evidence gap:
the exact historical volume formula is not retained in the currently available repository.

Therefore:
- do NOT call any simple volume threshold automatically NEW;
- RVOL-style research is duplication-risk until the old formula is recovered or the new test is explicitly treated as PARTIAL_OVERLAP / replication;
- money-flow and signed-volume path features may still be materially different.

### Machine-learned BUY-quality family

Previously tested:
- machine-learned BUY quality model from the then-tested feature set

Decision:
rejected/downgraded.

Critical evidence gap:
the exact historical feature matrix and model specification are not fully retained in current repository notes.

Constraint:
do not start another generic ML classifier until the feature layer itself shows new out-of-sample information.

## 2. Current proposed open-source-derived features — duplication classification

### CMF20 — PARTIAL_OVERLAP

Information family:
volume / money flow.

Overlap:
generic volume hard filter previously failed.

Material difference:
CMF uses close location within the high-low range, weighted by volume, and accumulates signed money-flow pressure.

It is not equivalent to a simple raw-volume or volume-above-average threshold.

Allowed next use:
diagnostic feature screen only, not a hard BUY gate.

### OBVImpulse10 — PARTIAL_OVERLAP

Information family:
signed volume path.

Overlap:
generic volume hard filter previously failed.

Material difference:
OBVImpulse measures whether volume has been associated with up-closes vs down-closes over a path; proposed normalization reduces cross-asset scale dependence.

Allowed next use:
diagnostic feature screen.

### RVOL20 — UNRESOLVED_OVERLAP / DEFER

Information family:
relative volume.

Problem:
the old volume-hard-filter formula is unrecovered.

Because a typical historical volume filter could have been equivalent or very close to volume / moving-average-volume, RVOL20 cannot currently be claimed as a materially new feature.

Decision:
defer from the first new experiment unless exact old formula is recovered or the new study is explicitly registered as replication.

### ER10 — NEW

Information family:
trend efficiency.

Definition:
absolute net 10-bar movement divided by total absolute 10-bar path length.

No retained evidence of an equivalent efficiency-ratio test.

Materially different from:
- MA slope
- dsep
- fast-width
- relative strength
- higher-timeframe confirmation

Reason:
ER measures directional efficiency / path straightness rather than direction alone.

Allowed next use:
priority diagnostic.

### CHOP14 — NEW

Information family:
choppiness / path efficiency.

Definition:
rolling total true range relative to rolling high-low range, logarithmically normalized.

No retained evidence of Choppiness Index or equivalent path-efficiency test.

Allowed next use:
priority diagnostic.

### Squeeze state — PARTIAL_OVERLAP

Information family:
volatility compression / expansion.

Overlap:
- fast-width expansion
- absolute white-width threshold
- ATR-based model components

Material difference:
Bollinger-inside-Keltner compression is a relative volatility-compression state, not just widening of the existing SSSS fast band.

Allowed next use:
diagnostic only; must not be framed as a wholly new volatility concept.

### NATR regime — PARTIAL_OVERLAP

Information family:
normalized volatility.

Overlap:
ATR is already deeply embedded in SSSS:
- PriceNearWhite
- EntryATR progress
- tail-risk research

Material difference:
NATR / rolling relative-volatility regime is proposed as market-state context rather than price-distance measurement.

Allowed next use:
lower-priority diagnostic.

## 3. First safe next-feature set

The first new diagnostic round should NOT test all seven proposed indicators at once.

Recommended first set:

1. ER10 — NEW
2. CHOP14 — NEW
3. CMF20 — PARTIAL_OVERLAP, materially different
4. OBVImpulse10 — PARTIAL_OVERLAP, materially different

Deferred:
- RVOL20 — unresolved duplication risk
- Squeeze — overlaps prior volatility expansion research
- NATR regime — overlaps existing ATR family

This keeps the first round focused on genuinely orthogonal information.

## 4. Required interpretation

The purpose of the next round is NOT:
- to add four new hard filters;
- to maximize in-sample BUY accuracy;
- to tune textbook thresholds.

The purpose is:
test whether these features contain incremental information about SSSS path quality.

Primary questions:
- do feature distributions differ between Mature and Failure lifecycles?
- do they explain early-path quality beyond current SSSS state?
- do relationships have the same sign in equities and crypto?
- are effects concentrated in a few outliers?

Any exact trading rule requires a later, separately pre-registered experiment.

## 5. Crypto overlap rule

Equity and crypto tracks must remain independent.

For crypto:
- BTC / ETH / SOL / BNB may be Discovery because they have prior SSSS exposure.
- XRP / ADA / DOGE / TRX remain reserved OOS candidates.
- LINK / AVAX / LTC / BCH remain reserved Frozen OOS candidates.

Do not consume crypto OOS or Frozen OOS during exploratory feature diagnostics.

## 6. Historical evidence that remains unrecovered

The following early details are not fully preserved in current retained repository notes:
- exact formula of the rejected volume hard filter
- exact feature matrix of the rejected machine-learned BUY quality model
- exact historical Discovery12 membership
- exact historical Validation5 membership

Do not fabricate them.

If an older source artifact is later recovered, update this audit before relying on it.
