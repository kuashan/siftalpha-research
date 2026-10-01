# SSSS Strategy Draft v0 — Structure-Driven Candidate

Status: DISCOVERY_DRAFT / NOT_FROZEN / NOT_PRODUCTION
Date: 2026-10-01

Purpose:
Translate the strict Source-XMA rail/color evidence into a strategy-specific
decision language without forcing the FIVEGZ three-buy/three-sell template.

## Core identity

SSSS is a structure strategy:

PRICE LOCATION
+ FIVE RAILS
+ THREE-COLOR FAST STATE
+ SLOW GRAY STRUCTURE
+ STATE/PATH CONFIRMATION

It is not defined by a fixed number of BUY/SELL labels.

## Candidate decision vocabulary

### 1. LOWER_REVERSAL_WATCH

Condition family:
- price pierces fast lower ZD1
- state is DOWN or RANGE

Evidence:
- DOWN: n=43, +20 mean +8.92%, 74.4% positive, 60.5% reaches upper
- RANGE: n=24, 70.8% reaches upper

Action status:
WATCH / possible small probe candidate only.

Reason:
new-low risk remains high (DOWN 76.7%, RANGE 87.5%).
Do not promote to full-size entry from this event alone.

### 2. LOWER_UPTREND_BREAK_RISK

Condition:
- price pierces ZD1
- state is UP/red

Evidence:
- n=30
- +20 mean -3.41%
- only 36.7% reaches upper
- 93.3% makes a new low

Action status:
RISK WARNING / avoid treating it as the standard dip-buy setup.

### 3. MIDPOINT_RECOVERY_CONFIRMATION_CANDIDATE

Condition family:
- after lower-side reversal watch,
- price later reclaims analytical midpoint GZB18
- preferably with state improvement

Evidence:
midpoint is reached in 83%–100% of lower events depending on state.

Action status:
CONFIRMATION CANDIDATE, not yet an accepted entry/add rule.

Required next test:
measure post-reclaim return/MFE/MAE and whether state transition adds information.

### 4. UPPER_EXTENSION_WARNING

Condition:
- price pierces fast upper ZK1
- state remains UP/red

Evidence:
- n=38
- +20 mean -5.20%, median -5.00%
- 52.6% later reaches fast lower
- but 76.3% also makes a later new high

Action status:
REDUCE/WARNING candidate, not automatic full exit and not short.

### 5. UPPER_CONFLUENCE_EXHAUSTION

Condition:
- UP/red state
- candle overlaps ZK1 and BS
- upper rail gap <= 0.25 ATR
- strict archived event definition

Evidence:
- exact event dates reproduced by current strict replay
- n=10
- +5 mean -4.32%
- +10 mean -6.36%
- +20 mean about -9.12%

Action status:
STRONGER REDUCE / EXIT CANDIDATE.

Still preferred as a two-step structure:
UP + confluence => WARNING
then midpoint loss and/or state deterioration => EXIT confirmation candidate.

### 6. MIDPOINT_LOSS_AFTER_EXTENSION

Condition family:
- after UP/red upper extension
- price falls to/through GZB18

Evidence:
strict midpoint hold after upper event was only 19.4%.

Action status:
RISK CONFIRMATION candidate.
A close-through / failed reclaim should be tested as a stronger exit trigger.

### 7. GRAY_BAND_STRUCTURAL_FAILURE

Condition family:
- fast state UP/red
- price falls from above into GZB3..GZB4

Evidence:
- support-side UP n=56, +20 mean -3.24%
- ENTER_BAND subtype +20 mean -4.62%

Action status:
STRUCTURAL RISK / REDUCE candidate, not a buy-support assumption.

### 8. GRAY_BAND_UP_REJECTION

Condition family:
- fast state UP/red
- price approaches slow gray band from below and is rejected

Evidence:
- n=17, +20 mean -5.81%
- TOUCH_REJECT n=11, +20 mean -8.52%

Action status:
EXIT / trend-failure candidate.

Important:
the same gray-band event in DOWN or RANGE does not behave as generic resistance,
so this signal is state-specific.

### 9. OUTER_RAIL_CONTEXT_ONLY

BD/BS touch alone:
do not use as universal buy/sell.

Use outer rails as:
- confluence amplifier;
- extension measurement;
- risk context.

### 10. EXPANSION / UNCLEAR

If state is EXPANSION_STRADDLE or source color is not defined:
default WATCH / NO NEW POSITION until a dedicated sample exists.

## Current draft state machine

FLAT
  -> LOWER_REVERSAL_WATCH
  -> optional future CONFIRMED_ENTRY rule
  -> HOLD

HOLD
  -> normal rail movement: continue observe
  -> UPPER_EXTENSION_WARNING: consider reduce
  -> UPPER_CONFLUENCE_EXHAUSTION: stronger reduce/exit candidate
  -> MIDPOINT_LOSS / GRAY structural failure: exit confirmation candidate
  -> FLAT

This draft intentionally has no fixed "three buys / three sells".

## What is still missing before a frozen SSSS strategy

1. sequential test:
   lower event -> midpoint reclaim -> state improvement -> upper reach;
2. sequential test:
   upper event -> midpoint loss -> state deterioration -> lower reach;
3. exact entry sizing;
4. exact reduce sizing;
5. risk stop / invalidation;
6. untouched OOS / Frozen OOS validation;
7. crypto vs equity parameter portability;
8. no short rule until separately supported.

Until those gates close, this is a research strategy draft, not a deployable production strategy.
