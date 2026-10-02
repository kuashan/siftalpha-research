# SSSS Reboot — 30 Stocks + 4 Crypto Full Combination Validation v3 Protocol

Status: **FROZEN BEFORE OUTCOME RUN**
Date: 2026-10-02

## Purpose

Run a broad cross-symbol validation and exhaustive observed-combination scan for
the SSSS rail / color / true light-gray-band structure.

This round has two simultaneous goals:

1. **Formal cross-symbol validation** of the ABT/AAPL candidate structures.
2. **Full possibility-combination scan** across the frozen feature dimensions
   below, without changing definitions after outcomes are seen.

## Frozen universe

The historical material contains a frozen ordered 39-stock universe but no
recoverable old rule defining a 30-stock subset. To avoid outcome-driven stock
selection, this round deterministically takes the **first 30 symbols in that
frozen order**:

1. AAPL
2. MSFT
3. NVDA
4. AMD
5. AVGO
6. ORCL
7. INTC
8. QCOM
9. MU
10. GOOGL
11. META
12. NFLX
13. AMZN
14. TSLA
15. HD
16. MCD
17. WMT
18. COST
19. PG
20. KO
21. PEP
22. ABT
23. LLY
24. UNH
25. JNJ
26. TMO
27. JPM
28. BAC
29. GS
30. V

Crypto:
1. BTC/USD
2. ETH/USD
3. BNB/USD
4. SOL/USD

Total: **34 instruments**.

ABT and AAPL remain in the full 34-instrument descriptive matrix because the
user requested the 30-stock universe as a whole.

For **formal validation of candidates discovered on ABT/AAPL**, ABT and AAPL are
excluded from the validation cohort. Formal stock validation therefore uses the
other **28 stocks**, plus a separate 4-crypto validation table.

## Data windows

Stocks:
- Main event window: 2018-01-02 through 2025-12-31 where returned data exist.
- Request history from 2010-01-04 for warm-up.
- Bars before 2018 are warm-up only.

Crypto:
- Target main window: 2018-01-02 through 2025-12-31 where data exist.
- Request earlier history where the provider supplies it.
- If an instrument lacks enough pre-2018 history, its first **180 returned
  daily bars are warm-up only**.
- Therefore an asset such as SOL may enter the statistical sample later than
  2018 because it did not exist for the full period.

All coverage dates and usable bar counts must be reported.

## Historical representation

**FIRST_OBSERVED** only.

At bar t:
- use data <= t;
- recompute right-edge XMA structures;
- persist what was observable then;
- never backfill finalized/repainted historical XMA.

## Immutable XMA

No formula changes:

- XMA(XMA(L,25),25)
- XMA(XMA(H,25),25)
- XMA(XMA(L,60),60)
- XMA(XMA(H,60),60)

## Source states

- BLUE = GZB12 / COLOR000066
- GREEN = GZB13 / COLOR003300
- GRAY = GZB14 / COLOR555555

State thresholds remain GZB9 / GZB8.

True visual light-gray band:
- upper = GZB3
- lower = GZB4

GZB8/GZB9 must not be substituted for the true light-gray band.

## Frozen predictor dimensions

For every inner-rail event, store all of the following:

### 1. Current color
- BLUE
- GREEN
- GRAY

### 2. State age
- 1-3
- 4-10
- 11-20
- 21+

### 3. Origin state of current run
- BLUE
- GREEN
- GRAY
- OTHER (including EXPANSION / unavailable)

### 4. Recent transition pair
If state age <= 5:
- origin -> current state

### 5. Inner-rail break subtype

Lower:
- WICK_ONLY: Low < ZD1 and Close >= ZD1
- CLOSE_BELOW: Close < ZD1 and High >= ZD1
- FULL_BELOW: High < ZD1

Upper:
- WICK_ONLY: High > ZK1 and Close <= ZK1
- CLOSE_ABOVE: Close > ZK1 and Low <= ZK1
- FULL_ABOVE: Low > ZK1

### 6. Event close position versus true light-gray band
- ABOVE: Close > GZB3
- INSIDE: GZB4 <= Close <= GZB3
- BELOW: Close < GZB4

### 7. Event-bar true light-gray intersection
- YES / NO

## Frozen event types

### LOWER
New inner-lower break:
- current Low < current ZD1
- prior bar not already below prior FIRST_OBSERVED ZD1

### UPPER
New inner-upper break:
- current High > current ZK1
- prior bar not already above prior FIRST_OBSERVED ZK1

### LIGHT_SUPPORT
New de-clustered approach from above to true band [GZB4,GZB3].

### LIGHT_RESIST
New de-clustered approach from below to true band [GZB4,GZB3].

## Outcomes

Report at 5 / 10 / 20 bars.

LOWER:
- re-enter ZD1
- touch true light-gray band
- hit MID
- hit ZK1
- hit BD
- MID vs BD first-hit
- ZK1 vs BD first-hit
- true light-gray vs BD first-hit
- true light-gray vs MID first-hit
- forward close return
- MFE
- MAE

UPPER:
- re-enter ZK1
- touch true light-gray band
- hit MID
- hit ZD1
- hit BS
- MID vs BS first-hit
- ZD1 vs BS first-hit
- true light-gray vs BS first-hit
- true light-gray vs MID first-hit
- forward close return
- MFE
- MAE

LIGHT_SUPPORT:
- HOLD if price decisively closes back above GZB3 before closing below GZB4
- BREAK if close below GZB4 occurs first
- 5 / 10 / 20 return, MFE, MAE

LIGHT_RESIST:
- HOLD if price decisively closes back below GZB4 before closing above GZB3
- BREAK if close above GZB3 occurs first
- 5 / 10 / 20 return, MFE, MAE

## Full combination levels

All **observed** combinations are generated at these levels:

- L1: color
- L2: color × state-age
- L3: origin × color × state-age
- L4: color × state-age × break-subtype
- L5: origin × color × state-age × break-subtype
- L6: origin × color × state-age × break-subtype × light-gray close-zone
- L7: L6 × event-bar light-gray intersection

For light-gray support/resistance:
- color
- color × state-age
- origin × color × state-age
- above/inside/below event close-zone where applicable
- recent transition pair

Sparse combinations are retained but never promoted.

## Breadth / sample rules

A combination may be discussed as cross-symbol evidence only when:

Stocks:
- pooled events n >= 30;
- at least 8 eligible stock symbols have >= 3 events each.

Crypto:
- pooled events n >= 20;
- at least 3 crypto symbols have >= 3 events each.

For a symbol-level direction to count as support, its primary path probability
must be > 50%. Exactly 50% is neutral.

Report both:
- pooled event probability;
- median per-symbol probability;
- number and fraction of eligible symbols supporting the direction.

Do not let one high-event symbol stand in for breadth.

## Formal validation of ABT/AAPL candidates

Use only the 28 new stocks for the formal stock-validation status.
Crypto is reported separately.

Prespecified candidates:

BUY-side:
1. GREEN 21+ + LOWER behaves as a BUY candidate.
2. BLUE 21+ + LOWER behaves relatively cleanly.
3. GREEN 11-20 + LOWER tends to reach BD first.
4. recent GRAY->GREEN + LOWER tends to reach BD first.
5. GRAY 4-10 + LIGHT_SUPPORT tends to hold.
6. recent BLUE->GRAY + LIGHT_SUPPORT tends to hold.

SELL-side:
7. BLUE 11-20 + UPPER tends to reach BS first.
8. BLUE 4-10 + UPPER tends to reach BS first.
9. recent GRAY->BLUE + UPPER tends to reach BS first.
10. GREEN 21+ + UPPER tends to revert toward MID before BS.
11. recent BLUE->GRAY + LIGHT_RESIST tends to hold as resistance.

## Multiple-combination discipline

The exhaustive L1-L7 scan is **discovery / robustness mapping**, not independent
confirmation of any newly discovered rule.

Only the 11 prespecified candidates above are formal validations in this round.

Any newly strong combination found in L1-L7 must be labeled:
**NEW_DISCOVERY_REQUIRES_FUTURE_VALIDATION**.

## Asset-class reporting

Never mix stocks and crypto into one headline probability without also showing
them separately.

20 bars means:
- approximately four trading weeks for stocks;
- twenty calendar days for 24/7 crypto.

Therefore stock and crypto behavior must be interpreted separately before any
combined robustness statement.

## No result-driven changes

Once this protocol is committed:
- no universe changes;
- no bucket changes;
- no event-definition changes;
- no threshold changes;
- no XMA changes;
until the whole 34-instrument run is complete.
