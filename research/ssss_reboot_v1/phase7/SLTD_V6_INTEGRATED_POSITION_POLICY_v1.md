# SLTD V6 Integrated Position Policy v1

Status: **FROZEN AS CURRENT POSITION POLICY BY USER DECISION**

Parent ordinary position policy:
`I25_AADD_25_TO_CAP_S25_WHOLD_RNO_CHANGE_MIXED`

Hard Exit rule:
`C2_FULL_CANDLE_BELOW_SLOW_BAND`

Research window used for the supporting 79-stock study:
**2020-01-02 through 2026-09-30**

Execution convention:
**signal confirmed at close -> execute at next available open**

Representation:
**FIRST_OBSERVED**

Friction convention used in research:
- 5 bps baseline
- 10 bps stress

Long/cash only. No leverage. No short selling.

---

## 1. Complete position policy

### A. Initial BUY
When flat and a valid SLTD V6 BUY action is produced:

- target position = **25%**

Do not enter 100% on the first BUY.

### B. Subsequent BUY
When already long and a later valid BUY action is produced:

- add **25 percentage points** of portfolio exposure;
- cap total target position at **100%**.

Examples:
- 25% -> 50%
- 50% -> 75%
- 75% -> 100%
- 100% -> remain 100%

### C. Ordinary SELL
When a valid ordinary SLTD V6 SELL action is produced:

- sell **25% of the current remaining position**.

This is multiplicative reduction, not minus 25 percentage points.

Example from 100%:
- 100% -> 75%
- 75% -> 56.25%
- 56.25% -> 42.1875%
- 42.1875% -> 31.640625%

Any actually executed ordinary SELL sets the Hard Exit risk state to **ARMED**.

### D. WAIT
When long and a WAIT action is produced:

- **hold current position unchanged**.

When flat:

- WAIT does not open a position.

### E. Mixed same-bar action classes
If more than one action class conflicts on the same signal bar:

- **NO_CHANGE_MIXED**
- do not change position for that mixed action bar.

### F. Hard Exit — C2
Hard Exit may occur only after risk has been ARMED by an actually executed ordinary SELL.

While ARMED, if the signal bar satisfies all of the following:

1. SLTD state = **GREEN**;
2. the **entire candle is below the slow light-gray band's lower edge**;
3. formally: **High < GZB4**;

then:

- at the **next available open**, liquidate **100% of the remaining position**;
- resulting position = **0%**;
- Hard Exit overrides ordinary BUY / HOLD / WAIT / SELL on that execution open;
- after Hard Exit, ARMED resets to **false**.

### G. Hard Exit reset
If, after risk is ARMED, a valid BUY is actually executed before C2 fires:

- ARMED resets to **false**.

This means a renewed BUY cancels the prior deterioration warning.

### H. Re-entry after Hard Exit
After a C2 Hard Exit:

- remain flat until a later valid ordinary BUY appears;
- the next valid BUY restarts from **25%**, not from the previous position size.

---

## 2. Integrated lifecycle

The complete position lifecycle is:

**Flat**
-> valid BUY
-> **25%**

Then each later BUY:
**+25 percentage points**
-> up to **100%**

Ordinary SELL:
**reduce 25% of current remaining position**
-> simultaneously set **risk ARMED**

If risk ARMED and a later BUY executes:
**cancel ARMED**

If risk ARMED and:
**GREEN + High < GZB4**
-> next available open
-> **Hard Exit to 0%**

Then wait for the next valid BUY and restart from 25%.

---

## 3. Relationship to the 15 SLTD V6 action rules

The 15 frozen SLTD V6 BUY / HOLD / WAIT / SELL rules are unchanged.

This integrated policy changes only **position execution and exit behavior**:

- BUY signals control staged entry / add;
- SELL signals control ordinary partial reduction and arm the risk state;
- WAIT means hold;
- C2 adds a separate full-liquidation layer after deterioration has already been signaled by an ordinary SELL.

---

## 4. Research evidence for C2

On the reused 79-stock research universe, 5 bps:

- total return: **+153.45%**
- CAGR: **14.79%**
- MaxDD: **-18.30%**
- Calmar: **0.808**
- Hard Exit executions: **305**

For comparison, the same ordinary position policy without Hard Exit:

- total return: **+190.06%**
- CAGR: **17.11%**
- MaxDD: **-24.56%**
- Calmar: **0.697**

C2 therefore traded some CAGR for materially lower drawdown and higher Calmar in that research sample.

Governance note:
C2 was selected after repeated use of the same 79-stock universe. It is now frozen by explicit user decision as the current integrated position policy. Its research support should not be described as fresh independent OOS validation.

---

`SLTD_V6_INTEGRATED_POSITION_POLICY_V1 = FROZEN`
