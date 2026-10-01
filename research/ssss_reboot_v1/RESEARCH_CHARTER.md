# SSSS Reboot v1 — Research Charter

Status: **FROZEN BEFORE OUTCOME ANALYSIS**

## Central research question

What information is actually contained in the original SSSS formula, and can any
of that information support an executable trading process when evaluated strictly
with information available at each historical bar?

The project must answer this in order:

1. What does the source formula compute?
2. Which displayed structures are causal and which repaint?
3. What was observable at each bar in real time?
4. Which observable events have repeatable forward behavior?
5. Which effects remain after the signal is actually detectable and executable?
6. Only then: can a trading strategy be formed?

## Research discipline

Do not begin by inventing BUY-A / BUY-B / SELL-A / SELL-B labels.

Do not begin with position sizing.

Do not optimize thresholds before understanding the source structure.

Do not convert a post-event path classification into a trade signal unless the
classification was actually knowable at that time.

Do not promote a condition because its mean return is large if:
- the median contradicts it;
- sample size is small;
- symbol concentration is high;
- time blocks disagree;
- execution delay destroys the effect;
- MFE/MAE shows unacceptable adverse excursion.

## Separation from 5s

5s-v1 is an independent frozen strategy family.

During SSSS discovery:
- 5s signals are not explanatory variables;
- 5s outcomes are not labels;
- 5s rules are not used to rescue or tune SSSS.

Only after an SSSS candidate is independently frozen may 5s be used as an external
comparison benchmark.
