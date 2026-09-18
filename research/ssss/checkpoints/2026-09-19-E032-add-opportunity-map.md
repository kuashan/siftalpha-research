# Research Checkpoint — 2026-09-19 — E032 ADD Opportunity Map

## Experiment

E032 — ADD Opportunity Map

Status: CANDIDATE_ZONES_FOUND

This is a Discovery-only diagnostic round.

No OOS data were queried.
No Frozen OOS data were queried.
No ADD trigger was accepted.

## Coverage

Discovery:
- 30 / 30 pre-registered stocks completed
- 40 resolved trades contributed opportunity observations
- 3332 all-bar hypothetical ADD observations
- primary statistics use first-entry-per-trade per map cell

Provider:
Massive only.

Intermittent rate limits occurred but missing tickers were later retrieved from the same provider. No provider mixing occurred.

## Fixed formal maps

1. lifecycle phase x bars since entry
2. current progress x giveback
3. running MFE x current progress
4. StructuralSep x fast-band location
5. effective state x dsep sign

## Qualified opportunity zones

15 cells passed the pre-registered CANDIDATE_ZONE gate.

Per pre-registration, only the top 5 are formally highlighted:

1. m4 / S_LT_0|F_BELOW_MID: 30 events, 22 stocks, win 70.00%, avg 4.65%, median 2.97%, PF 3.67, median entry distance -0.87 EntryATR, median timing 8.5 bars
2. m3 / M_LT_1|P_LE_0: 34 events, 22 stocks, win 64.71%, avg 9.59%, median 2.57%, PF 8.49, median entry distance -0.38 EntryATR, median timing 1 bars
3. m1 / PRE_RED|B00_04: 40 events, 24 stocks, win 62.50%, avg 8.45%, median 2.57%, PF 7.19, median entry distance -0.04 EntryATR, median timing 1 bars
4. m2 / P_LE_0|G_GE_2: 25 events, 17 stocks, win 60.00%, avg 5.45%, median 2.78%, PF 5.48, median entry distance -1.43 EntryATR, median timing 9 bars
5. m5 / GREEN|D_POS: 38 events, 24 stocks, win 63.16%, avg 5.99%, median 2.57%, PF 5.43, median entry distance -0.03 EntryATR, median timing 1 bars

## Main finding

The highest-quality opportunity zones cluster early in the trade, before Effective Red and before material price extension.

The strongest formal cell was:

- StructuralSep < 0
- close below FastMid
- 30 first-entry trade events
- 22 stocks
- 70.0% positive hypothetical ADD legs
- +4.65% average
- +2.97% median
- PF 3.67
- median ADD execution about -0.87 EntryATR vs original entry
- median timing 8.5 bars from original entry

However, several other top zones occur almost immediately after the original OPEN:
- PRE_RED during bars 0-4
- Effective Green with dsep > 0
- running MFE < 1 ATR while current progress <= 0

These are economically close to increasing initial exposure rather than waiting for a distinct later confirmation.

## Interpretation

E032 changes the ADD research direction.

Previous rounds searched for stronger confirmation later in the trade.

E032 shows that the marginal-return surface is generally strongest earlier, before large price extension. Later confirmation zones often have negative typical returns even when their average is lifted by rare major winners.

This does NOT mean "add immediately" is validated.

It means the next hypothesis should distinguish between:

- simply increasing the original starter size;
- a genuinely selective early second entry that improves exposure without duplicating the original OPEN.

## Decision

E032 = CANDIDATE_ZONES_FOUND.

Do not modify the state machine.
Do not add an ADD trigger.
Do not open E032 OOS or Frozen OOS.

Any trigger built from this map requires a new Experiment ID and new pre-registration.
