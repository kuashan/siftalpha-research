# SLTD V6 — Formal 15-Rule Action Taxonomy

Official strategy name: **SLTD V6**

Status: **ORGANIZED / FORMAL RULE SET**
Date: 2026-10-02

Source:
- V5 optimized rulebook
- V6 independent validation

Representation:
- FIRST_OBSERVED
- XMA unchanged

**SLTD V6** is the official name of the current strategy represented by this rule set.

This document reorganizes the current **15 formal rules** into four direct
operation categories:

- BUY
- HOLD
- WAIT
- SELL

Excluded from these 15:
- prior MIXED rules
- V5 WATCH-only rules
- V6-A GREEN→GRAY 1-3 + LIGHT_SUPPORT, which remains HOLD_FOR_MORE_DATA

---

# 1. BUY（买入候选）— 5 条

## BUY-1｜蓝色 21+ + 跌破内下轨

Original ID:
`BUY_BLUE_21P_LOWER`

Condition:
- current state = BLUE
- state age >= 21
- new LOWER event

Expected path:
- MID before BD

Interpretation:
- 蓝色长期持续后出现内下轨跌破，优先视为反弹型 BUY 候选。

Evidence:
- V5 stock: STRONG_REPEAT
- n=515
- p=69.9%
- 19/20 eligible stocks supported direction
- V5 crypto: STRONG_REPEAT
- n=124
- p=82.3%
- 4/4 crypto supported direction

Action:
**BUY candidate**

---

## BUY-2｜灰色 4–10 + 从上方触碰浅灰带

Original ID:
`BUY_GRAY_4_10_LIGHT_SUPPORT`

Condition:
- current state = GRAY
- state age = 4-10
- new LIGHT_SUPPORT event from above

Expected outcome:
- SUPPORT_HOLD

Evidence:
- V5 stock: STRONG_REPEAT
- n=167
- p=75.4%
- support fraction 100%
- V5 crypto: STRONG_REPEAT
- n=53
- p=81.1%

Action:
**BUY / support candidate**

---

## BUY-3｜最近蓝→灰 + 从上方触碰浅灰带

Original ID:
`BUY_RECENT_BLUE_GRAY_LIGHT_SUPPORT`

Condition:
- recent transition BLUE -> GRAY
- current GRAY age <= 5
- new LIGHT_SUPPORT

Expected outcome:
- SUPPORT_HOLD

Evidence:
- V5 stock: STRONG_REPEAT
- n=57
- p=75.4%
- V5 crypto: STRONG_REPEAT
- n=28
- p=85.7%

Action:
**BUY / support candidate**

---

## BUY-4｜蓝色 11–20 + 内下轨仅影线跌破

Original ID:
`BLUE_11_20_LOWER_WICK_ONLY`

Condition:
- current state = BLUE
- state age = 11-20
- new LOWER
- subtype = WICK_ONLY

Expected path:
- MID before BD

Evidence:
- V5 stock: STRONG_REPEAT
- n=53
- p=84.9%
- support fraction 100%
- promoted in V5
- crypto breadth insufficient but direction supportive

Action:
**BUY candidate**

---

## BUY-5｜灰色 4–10 + 内下轨仅影线跌破

Original V6 ID:
`NEW_V5_C_GRAY_4_10_LOWER_WICK_ONLY`

Condition:
- current state = GRAY
- state age = 4-10
- new LOWER
- subtype = WICK_ONLY

Expected path:
- MID before BD

Evidence:
- V5 discovery: n=45, p=82.2%
- V6 independent stock:
  - n=58
  - p=75.9%
  - 9/12 eligible stocks supported
  - VALIDATED_V6_STRONG
- V6 crypto:
  - n=26
  - p=57.7%
  - MIXED

Action:
**BUY candidate for stocks**
Crypto should be treated more cautiously.

---

# 2. HOLD（持有 / 不急卖）— 4 条

## HOLD-1｜蓝色 11–20 + 突破内上轨

Original ID:
`CONT_BLUE_11_20_UPPER`

Condition:
- current state = BLUE
- state age = 11-20
- new UPPER event

Expected path:
- BS before MID

Evidence:
- V5 stock: STRONG_REPEAT
- n=86
- p=83.7%
- V5 crypto: STRONG_REPEAT
- n=20
- p=70.0%

Action:
**HOLD**
Do not mechanically sell at inner upper rail.

---

## HOLD-2｜蓝色 4–10 + 突破内上轨

Original ID:
`CONT_BLUE_4_10_UPPER`

Condition:
- current state = BLUE
- state age = 4-10
- new UPPER event

Expected path:
- BS before MID

Evidence:
- V5 stock: STRONG_REPEAT
- n=66
- p=81.8%
- crypto sample insufficient but direction supportive

Action:
**HOLD**
Prefer to observe BS before selling.

---

## HOLD-3｜最近灰→蓝 + 突破内上轨

Original ID:
`CONT_RECENT_GRAY_BLUE_UPPER`

Condition:
- recent GRAY -> BLUE
- current BLUE age <= 5
- new UPPER event

Expected path:
- BS before MID

Evidence:
- V5 stock: STRONG_REPEAT
- n=61
- p=70.5%
- crypto sample insufficient

Action:
**HOLD**
A fresh BLUE state breaking the upper rail often has continuation potential.

---

## HOLD-4｜蓝色 21+ + 收盘突破内上轨

Original V6 ID:
`NEW_V5_B_BLUE_21P_UPPER_CLOSE_ABOVE`

Condition:
- current state = BLUE
- state age >= 21
- new UPPER
- subtype = CLOSE_ABOVE

Expected path:
- BS before MID

Evidence:
- V5 discovery:
  - n=228
  - p=82.9%
- V6 independent stock:
  - n=320
  - p=80.0%
  - 20/20 eligible stocks supported
  - VALIDATED_V6_STRONG
- V6 crypto:
  - n=35
  - p=80.0%
  - 4/4 supported
  - SUPPORTS_V6_STOCK

Action:
**HOLD / continuation**
This is one of the strongest confirmed upper-rail continuation rules.

---

# 3. WAIT（等待 / 不急买）— 2 条

## WAIT-1｜绿色 11–20 + 跌破内下轨

Original ID:
`AVOID_GREEN_11_20_LOWER`

Condition:
- current state = GREEN
- state age = 11-20
- new LOWER event

Expected path:
- BD before MID

Evidence:
- V5 stock: STRONG_REPEAT
- n=85
- p=78.8%
- 15/16 eligible stocks supported
- crypto sample insufficient but direction supportive

Action:
**WAIT**
Do not rush to buy at the inner lower rail.
Prefer to wait for BD or a clearer reversal.

---

## WAIT-2｜绿色 11–20 + 收盘跌破内下轨

Original ID:
`GREEN_11_20_LOWER_CLOSE_BELOW`

Condition:
- current state = GREEN
- state age = 11-20
- new LOWER
- subtype = CLOSE_BELOW

Expected path:
- BD before MID

Evidence:
- V5 stock: STRONG_REPEAT
- n=39
- p=92.3%
- support fraction 100%
- promoted in V5
- crypto breadth insufficient but observed direction consistent

Action:
**STRONG WAIT**
This is a stronger warning than WAIT-1 because price actually closes below the
inner lower rail.

---

# 4. SELL（卖出 / 减仓候选）— 4 条

## SELL-1｜最近蓝→灰 + 从下方触碰浅灰带

Original ID:
`SELL_RECENT_BLUE_GRAY_LIGHT_RESIST`

Condition:
- recent BLUE -> GRAY
- current GRAY age <= 5
- new LIGHT_RESIST event from below

Expected outcome:
- RESIST_HOLD

Evidence:
- V5 stock: STRONG_REPEAT
- n=100
- p=76.0%
- V5 crypto: STRONG_REPEAT
- n=20
- p=85.0%

Action:
**SELL / trim candidate**

---

## SELL-2｜绿色 4–10 + 突破内上轨

Original ID:
`GREEN_4_10_UPPER`

Condition:
- current state = GREEN
- state age = 4-10
- new UPPER event

Expected path:
- MID before BS

Evidence:
- V5 stock: REPEAT
- n=52
- p=63.5%
- 8/10 eligible stocks supported
- promoted in V5
- crypto sample insufficient

Action:
**SELL / trim candidate**
Evidence is weaker than the strongest HOLD rules, so use as a tactical exit
candidate rather than an absolute full-exit rule.

---

## SELL-3｜绿色 11–20 + 内上轨仅影线突破

Original V6 ID:
`NEW_V5_D_GREEN_11_20_UPPER_WICK_ONLY`

Condition:
- current state = GREEN
- state age = 11-20
- new UPPER
- subtype = WICK_ONLY

Expected path:
- MID before BS

Evidence:
- V5 discovery:
  - n=49
  - p=77.6%
- V6 independent stock:
  - n=48
  - p=64.6%
  - 8/11 eligible stocks supported
  - VALIDATED_V6
- V6 crypto:
  - n=11
  - p=90.9%
  - insufficient breadth

Action:
**SELL / trim candidate**

---

## SELL-4｜绿色 11–20 + 从下方触碰浅灰带

Original V6 ID:
`NEW_V5_E_GREEN_11_20_LIGHT_RESIST`

Condition:
- current state = GREEN
- state age = 11-20
- new LIGHT_RESIST event

Expected outcome:
- RESIST_HOLD

Evidence:
- V5 discovery:
  - n=88
  - p=78.4%
- V6 independent stock:
  - n=74
  - p=70.3%
  - 10/12 eligible stocks supported
  - VALIDATED_V6_STRONG
- V6 crypto:
  - n=18
  - p=88.9%
  - breadth insufficient but direction highly consistent

Action:
**SELL / trim candidate**

---

# 5. Final 15-rule action map

## BUY — 5
1. BLUE 21+ + LOWER
2. GRAY 4-10 + LIGHT_SUPPORT
3. recent BLUE->GRAY + LIGHT_SUPPORT
4. BLUE 11-20 + LOWER WICK_ONLY
5. GRAY 4-10 + LOWER WICK_ONLY

## HOLD — 4
6. BLUE 11-20 + UPPER
7. BLUE 4-10 + UPPER
8. recent GRAY->BLUE + UPPER
9. BLUE 21+ + UPPER CLOSE_ABOVE

## WAIT — 2
10. GREEN 11-20 + LOWER
11. GREEN 11-20 + LOWER CLOSE_BELOW

## SELL — 4
12. recent BLUE->GRAY + LIGHT_RESIST
13. GREEN 4-10 + UPPER
14. GREEN 11-20 + UPPER WICK_ONLY
15. GREEN 11-20 + LIGHT_RESIST

Total = **15 formal rules**

---

# 6. Operational interpretation

A useful high-level simplification is:

### BLUE lower-side
- long BLUE / wick-type lower breaks tend to belong to BUY.

### BLUE upper-side
- BLUE upper-rail breaks tend to belong to HOLD, not SELL.
- especially CLOSE_ABOVE in BLUE 21+.

### GREEN lower-side
- GREEN 11-20 lower breaks tend to belong to WAIT.
- CLOSE_BELOW strengthens the WAIT signal.

### GREEN upper-side
- GREEN upper-side events tend to belong more to SELL / trim.
- especially 4-10 UPPER, 11-20 UPPER WICK_ONLY, and 11-20 LIGHT_RESIST.

### GRAY
- GRAY support structures tend to be BUY-side.
- recent BLUE->GRAY from below at light-gray resistance tends to be SELL-side.

---

# 7. Not included in the formal 15

The following are intentionally excluded:

- GREEN 21+ + LOWER
- recent GRAY->GREEN + LOWER
- GREEN 21+ + UPPER

Reason:
- previous MIXED status / insufficient robustness.

Also excluded:

- BLUE 11-20 + UPPER CLOSE_ABOVE
- BLUE 21+ + UPPER FULL_ABOVE

Reason:
- V5 WATCH status and not promoted into the formal V5 set.

Also excluded:

- GREEN->GRAY 1-3 + LIGHT_SUPPORT

Reason:
- V6 stock direction was strong, but breadth was insufficient.
- final V6 disposition = HOLD_FOR_MORE_DATA.

`SLTD_V6 = OFFICIAL`

`SSSS_FORMAL_15_ACTION_TAXONOMY_v1 = COMPLETE`
