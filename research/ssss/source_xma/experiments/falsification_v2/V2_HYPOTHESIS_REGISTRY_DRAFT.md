# XMA Falsification v2 — Hypothesis Registry Draft

Status: **REGISTRY DRAFT / PRE-PROTOCOL / NOT FROZEN**

Experiment authorization: **NOT AUTHORIZED**  
Data access for v2 outcomes: **NOT AUTHORIZED**  
Sealed window: **NOT SELECTED**

This document registers the complete H1-H14 draft structure for review. It contains no results and does not authorize testing.

Governing design documents:
- `V2_PROTOCOL_DESIGN_ONEPAGER.md`
- `V2_PROTOCOL_DESIGN_ONEPAGER_AMENDMENT_v2.md`
- prior Scope / Checklist documents

The 14-hypothesis budget in Amendment v2 supersedes the earlier 12-hypothesis line in Amendment v1.

---

# 0. Global Frozen Definitions

## 0.1 Event unit

An **event** means an **Episode** after continuous-event deduplication.

Episode anchor = first qualifying bar of the deduplicated Episode.

Single qualifying bars inside the same Episode are not independent events.

Market-wave clustering uses the frozen **±2 trading-day linkage** definition and is reported separately from raw Episode count.

## 0.2 Default sample floor

For every formal hypothesis:

- raw Episodes >=100;
- market-wave clusters >=30;
- symbol clusters >=20.

For a multi-arm hypothesis, the floor applies to **each hypothesis-defining event arm**. A larger comparison arm cannot compensate for a smaller arm below floor.

Matched-control rows do not substitute for event-arm sample floors.

## 0.3 Matched-control distance variables

Where matched controls are required, standardized distance variables are:

1. `dev20 = close / MA20(close) - 1`
2. prior 20-bar return
3. `ATR14 / close`

No additional matching variable may be added without Amendment.

All selected controls must be persisted with:
- symbol;
- date;
- matching covariates;
- standardized distance;
- eligibility/exclusion reason;
- pool size;
- selected rank.

## 0.4 Test direction convention

A hypothesis may be one-sided or two-sided, but the choice is fixed below.

For two-sided hypotheses, MDE is applied to absolute effect size.

## 0.5 Formal hypothesis budget

- F1 Risk: H1-H2
- F2 Lifecycle: H3-H4
- F3 Cross-sectional: H5-H6
- F4 Conditional: H7-H10
- F5 Risk-Off: H11-H14

Total formal hypotheses: **14**.

Guards G-F1 through G-F5 are separate methodological controls.

---

# 1. F1 Risk

## H1 — XMA state difference in ATR-normalized MAE

**Title:** DOWN_STATE versus UP_STATE long-exposure adverse excursion  
**Family:** F1 Risk  
**Condition variable:** discrete XMA state  
**Condition definition:** Episode anchor is DOWN_STATE versus Episode anchor is UP_STATE  
**Control variables:** SPY cumulative return over the same 10-bar horizon; anchor `ATR14/close`  
**Outcome:** long-exposure maximum adverse excursion over bars 1-10, divided by anchor ATR14  
**Primary statistic:** coefficient on `I(DOWN_STATE)` in a tau=0.50 median quantile regression of ATR-normalized MAE on `I(DOWN_STATE)`, SPY 10-bar return, and anchor `ATR14/close`; UP_STATE is the reference  
**Horizon:** 10 bars  
**Direction:** positive  
**Test type:** one-sided  
**MDE:** coefficient >= +0.50 ATR  
**Sample floor:** each state arm raw >=100, waves >=30, symbols >=20  
**Data required:** OHLCV, ATR14, XMA state, SPY close/return series  
**Guard:** G-F1

## H2 — XMA state difference in ATR-normalized maximum drawdown

**Title:** DOWN_STATE versus UP_STATE path drawdown  
**Family:** F1 Risk  
**Condition variable:** discrete XMA state  
**Condition definition:** Episode anchor is DOWN_STATE versus Episode anchor is UP_STATE  
**Control variables:** SPY cumulative return over the same 10-bar horizon; anchor `ATR14/close`  
**Outcome:** maximum peak-to-trough price drawdown observed from anchor through bar 10, divided by anchor ATR14  
**Primary statistic:** coefficient on `I(DOWN_STATE)` in a tau=0.50 median quantile regression of ATR-normalized maximum drawdown on `I(DOWN_STATE)`, SPY 10-bar return, and anchor `ATR14/close`; UP_STATE is the reference  
**Horizon:** 10 bars  
**Direction:** positive  
**Test type:** one-sided  
**MDE:** coefficient >= +0.50 ATR  
**Sample floor:** each state arm raw >=100, waves >=30, symbols >=20  
**Data required:** OHLCV, ATR14, XMA state, SPY close/return series  
**Guard:** G-F1

---

# 2. F2 Lifecycle

## H3 — Distance-to-midpoint and midpoint-touch probability

**Title:** Signed distance-to-mid and 20-bar midpoint-touch probability inside DOWN_STATE  
**Family:** F2 Lifecycle  
**Condition variable:** signed distance to midpoint  
**Condition definition:** at DOWN_STATE Episode anchor, Group A has `distance_to_mid < 0`; Group B has `distance_to_mid >= 0`; signed distance is `(close - midpoint) / ATR14`; a midpoint touch occurs when `abs(close - midpoint) <= 0.25 * ATR14` on any of bars 1-20  
**Control variables:** none beyond restriction to DOWN_STATE Episodes and ATR-normalized midpoint definition  
**Outcome:** midpoint-touch indicator by bar 20  
**Primary statistic:** `P(touch by 20 | Group A) - P(touch by 20 | Group B)`  
**Horizon:** 20 bars  
**Direction:** non-zero difference  
**Test type:** two-sided  
**MDE:** absolute probability difference >=10 percentage points  
**Sample floor:** each sign group raw >=100, waves >=30, symbols >=20  
**Data required:** OHLCV, ATR14, midpoint series, XMA state  
**Guard:** G-F2

## H4 — Extreme distance and time-to-midpoint-touch

**Title:** Extreme versus neutral distance-to-mid and first-touch timing  
**Family:** F2 Lifecycle  
**Condition variable:** symbol-level distance-to-mid quantile  
**Condition definition:** signed `distance_to_mid = (close - midpoint)/ATR14`; Extreme arm = symbol-level <=P10 or >=P90; Neutral arm = symbol-level P40-P60; quantiles are computed independently per symbol from the frozen historical/pre-sealed dataset; midpoint touch uses `abs(close - midpoint) <= 0.25 * ATR14`  
**Control variables:** none; symbol-level quantile construction is part of the condition definition  
**Outcome:** time from Episode anchor to first midpoint touch, right-censored at bar 20 if no touch occurs  
**Primary statistic:** difference in Kaplan-Meier estimated median first-touch waiting time, `Extreme - Neutral`  
**Horizon:** 20 bars  
**Direction:** non-zero difference  
**Test type:** two-sided  
**MDE:** absolute median waiting-time difference >=3 bars  
**Sample floor:** each distance arm raw >=100, waves >=30, symbols >=20  
**Data required:** OHLCV, ATR14, midpoint series, XMA state, symbol identifier  
**Guard:** G-F2

---

# 3. F3 Cross-sectional

## H5 — Sector relative-strength bucket ranking effect

**Title:** High versus low Sector RS and future cross-sectional rank  
**Family:** F3 Cross-sectional  
**Condition variable:** Sector relative strength  
**Condition definition:** within each trading date and identical XMA state cross-section, High = top 20% of Sector RS rank and Low = bottom 20%; middle 60% is not part of H5  
**Control variables:** same-day market return; same-day industry return; same-day volatility level  
**Outcome:** 10-bar future return rank after market/industry return adjustment and volatility adjustment  
**Primary statistic:** rank-biserial correlation between High/Low Sector RS membership and adjusted 10-bar future-return rank  
**Horizon:** 10 bars  
**Direction:** positive  
**Test type:** one-sided  
**MDE:** correlation >= +0.03  
**Sample floor:** High and Low arms each raw >=100, waves >=30, symbols >=20  
**Data required:** OHLCV, XMA state, Sector RS field, market return, industry return, volatility level  
**Guard:** G-F3

## H6 — Incremental continuous Sector RS rank information

**Title:** Continuous Sector RS incremental cross-sectional information  
**Family:** F3 Cross-sectional  
**Condition variable:** continuous Sector relative-strength rank  
**Condition definition:** within each trading date and identical XMA state cross-section, use the full continuous Sector RS rank without bucket selection  
**Control variables:** same-day market return; same-day industry return; same-day volatility level  
**Outcome:** 10-bar future cross-sectional return rank  
**Primary statistic:** partial Spearman rank correlation between Sector RS rank and 10-bar future-return rank conditional on market return, industry return, and volatility level  
**Horizon:** 10 bars  
**Direction:** positive  
**Test type:** one-sided  
**MDE:** partial rank correlation >= +0.03  
**Sample floor:** raw >=100, waves >=30, symbols >=20  
**Data required:** OHLCV, XMA state, Sector RS field, market return, industry return, volatility level  
**Guard:** G-F3

---

# 4. F4 Conditional

## F4 matched-control eligibility

For H7-H10, each event is an Episode satisfying the specified XMA state plus external condition.

Eligible controls:
- same symbol;
- same exclusive XMA state;
- same frozen analysis window;
- do **not** satisfy the tested external condition;
- not inside ±20 bars of a same-hypothesis event;
- 5 nearest eligible controls by standardized Euclidean distance on dev20, prior20, and ATR14/close.

Matched excess for one event:
`event 10-bar return - mean(10-bar return of 5 selected controls)`.

All control rows are persisted.

## H7 — High volatility × DOWN_STATE

**Title:** High Volatility z-score condition inside DOWN_STATE  
**Family:** F4 Conditional  
**Condition variable:** Volatility z-score  
**Condition definition:** Episode anchor is DOWN_STATE and Volatility z-score > +1  
**Control variables:** dev20; prior 20-bar return; ATR14/close; same-state control eligibility above  
**Outcome:** 10-bar matched excess return  
**Primary statistic:** mean 10-bar matched excess return across matchable H7 Episodes  
**Horizon:** 10 bars  
**Direction:** positive  
**Test type:** one-sided  
**MDE:** matched excess >= +0.50 percentage points  
**Sample floor:** event arm raw >=100, waves >=30, symbols >=20; controls must satisfy the frozen 5-control rule  
**Data required:** OHLCV, XMA state, Volatility z-score, dev20, prior20, ATR14  
**Guard:** G-F4

## H8 — High volatility × UP_STATE

**Title:** High Volatility z-score condition inside UP_STATE  
**Family:** F4 Conditional  
**Condition variable:** Volatility z-score  
**Condition definition:** Episode anchor is UP_STATE and Volatility z-score > +1  
**Control variables:** dev20; prior 20-bar return; ATR14/close; same-state control eligibility above  
**Outcome:** 10-bar matched excess return  
**Primary statistic:** mean 10-bar matched excess return across matchable H8 Episodes  
**Horizon:** 10 bars  
**Direction:** negative  
**Test type:** one-sided  
**MDE:** matched excess <= -0.50 percentage points  
**Sample floor:** event arm raw >=100, waves >=30, symbols >=20; controls must satisfy the frozen 5-control rule  
**Data required:** OHLCV, XMA state, Volatility z-score, dev20, prior20, ATR14  
**Guard:** G-F4

## H9 — High volume × DOWN_STATE

**Title:** High Volume z-score condition inside DOWN_STATE  
**Family:** F4 Conditional  
**Condition variable:** Volume z-score  
**Condition definition:** Episode anchor is DOWN_STATE and Volume z-score > +1  
**Control variables:** dev20; prior 20-bar return; ATR14/close; same-state control eligibility above  
**Outcome:** 10-bar matched excess return  
**Primary statistic:** mean 10-bar matched excess return across matchable H9 Episodes  
**Horizon:** 10 bars  
**Direction:** positive  
**Test type:** one-sided  
**MDE:** matched excess >= +0.50 percentage points  
**Sample floor:** event arm raw >=100, waves >=30, symbols >=20; controls must satisfy the frozen 5-control rule  
**Data required:** OHLCV, XMA state, Volume z-score, dev20, prior20, ATR14  
**Guard:** G-F4

## H10 — High volume × UP_STATE

**Title:** High Volume z-score condition inside UP_STATE  
**Family:** F4 Conditional  
**Condition variable:** Volume z-score  
**Condition definition:** Episode anchor is UP_STATE and Volume z-score > +1  
**Control variables:** dev20; prior 20-bar return; ATR14/close; same-state control eligibility above  
**Outcome:** 10-bar matched excess return  
**Primary statistic:** mean 10-bar matched excess return across matchable H10 Episodes  
**Horizon:** 10 bars  
**Direction:** negative  
**Test type:** one-sided  
**MDE:** matched excess <= -0.50 percentage points  
**Sample floor:** event arm raw >=100, waves >=30, symbols >=20; controls must satisfy the frozen 5-control rule  
**Data required:** OHLCV, XMA state, Volume z-score, dev20, prior20, ATR14  
**Guard:** G-F4

---

# 5. F5 Risk-Off

## 5.1 Four-cell design

Every F5 hypothesis uses four cells:

| Cell | Definition |
| --- | --- |
| A | tested XMA-state Episode under Risk-Off |
| B | tested XMA-state Episode under Normal environment |
| C | matched non-tested-state controls for A |
| D | matched non-tested-state controls for B |

B is deterministically one-to-one matched to A on:
- identical symbol;
- identical calendar quarter;
- nearest Episode-anchor date within that quarter;
- tie-break: earlier date.

If no valid B exists for an A Episode, that A Episode is not matchable for the F5 primary statistic and the missingness is reported.

C and D:
- same symbol as their source event;
- same Risk-Off/Normal environment as their source event;
- do not belong to the tested XMA state;
- are not within ±20 bars of a tested-state Episode;
- use 5 nearest eligible controls by standardized Euclidean distance over dev20, prior20, ATR14/close.

Direction-normalized XMA effect:
- DOWN_STATE multiplier `s = +1`;
- UP_STATE multiplier `s = -1`.

Primary F5 statistic:
`DiD = s * [(A - C) - (B - D)]`.

Thus negative DiD means the direction-normalized XMA state effect is weaker in Risk-Off than in Normal conditions.

## H11 — Breadth stress × DOWN_STATE

**Title:** Breadth stress attenuation of DOWN_STATE information  
**Family:** F5 Risk-Off  
**Condition variable:** Market Breadth level  
**Condition definition:** Risk-Off when Market Breadth level is below its own trailing 20-trading-day 10th percentile; Normal otherwise; tested XMA state = DOWN_STATE  
**Control variables:** dev20; prior 20-bar return; ATR14/close; four-cell matching rules above  
**Outcome:** direction-normalized 10-bar XMA matched effect under Risk-Off versus Normal  
**Primary statistic:** `DiD = +(A-C) - +(B-D)`  
**Horizon:** 10 bars  
**Direction:** negative  
**Test type:** one-sided  
**MDE:** DiD <= -0.50 percentage points  
**Sample floor:** A and B event arms each raw >=100, waves >=30, symbols >=20; C/D must satisfy the 5-control rule  
**Data required:** OHLCV, XMA state, Market Breadth level, dev20, prior20, ATR14  
**Guard:** G-F5

## H12 — Breadth stress × UP_STATE

**Title:** Breadth stress attenuation of UP_STATE information  
**Family:** F5 Risk-Off  
**Condition variable:** Market Breadth level  
**Condition definition:** Risk-Off when Market Breadth level is below its own trailing 20-trading-day 10th percentile; Normal otherwise; tested XMA state = UP_STATE  
**Control variables:** dev20; prior 20-bar return; ATR14/close; four-cell matching rules above  
**Outcome:** direction-normalized 10-bar XMA matched effect under Risk-Off versus Normal  
**Primary statistic:** `DiD = -[(A-C) - (B-D)]`  
**Horizon:** 10 bars  
**Direction:** negative  
**Test type:** one-sided  
**MDE:** DiD <= -0.50 percentage points  
**Sample floor:** A and B event arms each raw >=100, waves >=30, symbols >=20; C/D must satisfy the 5-control rule  
**Data required:** OHLCV, XMA state, Market Breadth level, dev20, prior20, ATR14  
**Guard:** G-F5

## H13 — VIX shock × DOWN_STATE

**Title:** VIX shock attenuation of DOWN_STATE information  
**Family:** F5 Risk-Off  
**Condition variable:** VIX change  
**Condition definition:** Risk-Off when VIX 5-trading-day percentage change > +20%; Normal when <= +20%; tested XMA state = DOWN_STATE  
**Control variables:** dev20; prior 20-bar return; ATR14/close; four-cell matching rules above  
**Outcome:** direction-normalized 10-bar XMA matched effect under Risk-Off versus Normal  
**Primary statistic:** `DiD = +(A-C) - +(B-D)`  
**Horizon:** 10 bars  
**Direction:** negative  
**Test type:** one-sided  
**MDE:** DiD <= -0.50 percentage points  
**Sample floor:** A and B event arms each raw >=100, waves >=30, symbols >=20; C/D must satisfy the 5-control rule  
**Data required:** OHLCV, XMA state, VIX close series, dev20, prior20, ATR14  
**Guard:** G-F5

## H14 — VIX shock × UP_STATE

**Title:** VIX shock attenuation of UP_STATE information  
**Family:** F5 Risk-Off  
**Condition variable:** VIX change  
**Condition definition:** Risk-Off when VIX 5-trading-day percentage change > +20%; Normal when <= +20%; tested XMA state = UP_STATE  
**Control variables:** dev20; prior 20-bar return; ATR14/close; four-cell matching rules above  
**Outcome:** direction-normalized 10-bar XMA matched effect under Risk-Off versus Normal  
**Primary statistic:** `DiD = -[(A-C) - (B-D)]`  
**Horizon:** 10 bars  
**Direction:** negative  
**Test type:** one-sided  
**MDE:** DiD <= -0.50 percentage points  
**Sample floor:** A and B event arms each raw >=100, waves >=30, symbols >=20; C/D must satisfy the 5-control rule  
**Data required:** OHLCV, XMA state, VIX close series, dev20, prior20, ATR14  
**Guard:** G-F5

---

# 6. Guard Registry

Guards do not count toward H1-H14.

One deterministic guard realization is used per family. No seed searching and no alternate-seed reporting are allowed.

A guard passes only when:
1. it satisfies the same raw/wave/symbol sample floor as its linked family test; and
2. its absolute effect remains below the linked MDE.

Guard p-values, if reported diagnostically, do not enter BH or any scientific FDR family.

If a guard is INSUFFICIENT or fails, the entire linked family is **NOT ELIGIBLE FOR PROMOTION** until a formal Amendment resolves the methodological problem.

## G-F1 — XMA-state null label guard

**Linked family:** F1 Risk  
**Generation:** within symbol × calendar quarter, deterministically permute UP_STATE/DOWN_STATE Episode labels while preserving the original state-label counts; fixed seed = `2026092801`; if exact wave-cluster count is not preserved, deterministic rejection sampling continues under the same seed stream until symbol distribution, time range, raw count, and wave-cluster count match the real F1 sample  
**Sample matching:** same symbol distribution; same calendar-quarter distribution; same raw Episode count; same ±2-day wave-cluster count; same SPY/ATR adjustment specification  
**Primary statistic:** H1-form median-quantile-regression DOWN-label coefficient for ATR-normalized MAE  
**Horizon:** 10 bars  
**Null direction:** zero  
**MDE/pass band:** `abs(effect) < 0.50 ATR`  
**Sample floor:** raw >=100, waves >=30, symbols >=20 in each pseudo-state arm  
**Bootstrap/repeats:** none; one deterministic accepted guard realization only  
**Insufficient handling:** G-F1 = INSUFFICIENT; F1 cannot be promoted

## G-F2 — Distance-to-mid null permutation guard

**Linked family:** F2 Lifecycle  
**Generation:** within symbol × calendar quarter, deterministically permute anchor distance-to-mid values across eligible lifecycle Episodes; fixed seed = `2026092802`; derive H3 sign groups from permuted values; rejection sampling under the same seed stream is used only to restore the real sample's raw and ±2-day wave counts  
**Sample matching:** same symbol distribution; same time range; same raw Episode count; same wave-cluster count  
**Primary statistic:** H3-form 20-bar midpoint-touch probability difference  
**Horizon:** 20 bars  
**Null direction:** zero  
**MDE/pass band:** `abs(effect) < 10 percentage points`  
**Sample floor:** each pseudo-group raw >=100, waves >=30, symbols >=20  
**Bootstrap/repeats:** none; one deterministic accepted guard realization only  
**Insufficient handling:** G-F2 = INSUFFICIENT; F2 cannot be promoted

## G-F3 — Sector RS null permutation guard

**Linked family:** F3 Cross-sectional  
**Generation:** within each trading date × XMA state cross-section, deterministically permute Sector RS values across symbols; fixed seed = `2026092803`; this preserves the exact date/state sample and symbol count while removing Sector RS information  
**Sample matching:** same dates; same XMA-state cross-sections; same symbol count; same raw Episodes and wave structure  
**Primary statistic:** H6-form partial Spearman rank correlation after the frozen market/industry/volatility controls  
**Horizon:** 10 bars  
**Null direction:** zero  
**MDE/pass band:** `abs(effect) < 0.03`  
**Sample floor:** raw >=100, waves >=30, symbols >=20  
**Bootstrap/repeats:** none; one deterministic permutation only  
**Insufficient handling:** G-F3 = INSUFFICIENT; F3 cannot be promoted

## G-F4 — External-condition null permutation guard

**Linked family:** F4 Conditional  
**Generation:** separately for Volatility and Volume tests, within symbol × XMA state × calendar quarter, deterministically permute the `z-score > +1` condition labels while preserving positive-label counts; fixed seed = `2026092804`; run the identical F4 matched-control pipeline afterward  
**Sample matching:** same symbol distribution; same state distribution; same calendar-quarter distribution; same raw event count; same wave-cluster count; same 5-control matching pipeline  
**Primary statistic:** H7-H10 form mean 10-bar matched excess return  
**Horizon:** 10 bars  
**Null direction:** zero  
**MDE/pass band:** `abs(effect) < 0.50 percentage points`  
**Sample floor:** raw >=100, waves >=30, symbols >=20; 5 controls per event  
**Bootstrap/repeats:** none; one deterministic accepted permutation per tested external field  
**Insufficient handling:** G-F4 = INSUFFICIENT; F4 cannot be promoted

## G-F5 — Risk-Off date-label null permutation guard

**Linked family:** F5 Risk-Off  
**Generation:** separately for Breadth and VIX tests, permute Risk-Off/Normal labels at the trading-date level within calendar quarter, applying each permuted date label to all symbols on that date; fixed seed = `2026092805`; preserve the count of Risk-Off dates; deterministic rejection sampling under the same seed stream continues until the linked real hypothesis symbol distribution, raw A/B event counts, and ±2-day wave counts are matched; then apply the identical F5 four-cell and matched-control pipeline  
**Sample matching:** same date range; same symbol distribution; same A/B event counts; same wave-cluster counts; same B-to-A deterministic pairing; same C/D 5-control pipeline  
**Primary statistic:** F5 direction-normalized 10-bar DiD  
**Horizon:** 10 bars  
**Null direction:** zero  
**MDE/pass band:** `abs(DiD) < 0.50 percentage points`  
**Sample floor:** A and B each raw >=100, waves >=30, symbols >=20; C/D satisfy 5-control rule  
**Bootstrap/repeats:** none; one deterministic accepted guard realization per Risk-Off field  
**Insufficient handling:** G-F5 = INSUFFICIENT; F5 cannot be promoted

---

# 7. Registry Freeze Rule

This file is still a **DRAFT**, not the final Protocol.

After Registry review approval:
- no formal hypothesis may be added;
- no candidate variable may be added or substituted;
- deletion is allowed only before Protocol freeze and must be recorded;
- wording clarification may not change primary statistic, direction, MDE, sample floor, family, or condition variable without Amendment.

No v2 outcome data may be inspected under authority of this Registry Draft.

Experiment remains **NOT AUTHORIZED**.
