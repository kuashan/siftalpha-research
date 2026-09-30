# XMA Falsification v2 — Hypothesis Registry Review v2

Status: **PASS / DELTA REVIEW AFTER GUARD-BH CLARIFICATION**

Date: 2026-09-28

Reviewed registry commit:
`96bb62e90ffdb4602f7fded476c4b6ae4aec6988`

Delta from Review v1:
- removed residual wording that could be read as placing Guard controls inside family correction;
- explicitly states Guard p-values do not enter BH or any scientific FDR family;
- Guard pass/fail is based on sample sufficiency and `abs(effect) < linked MDE`;
- Guard failure/insufficiency blocks family promotion.

No change was made to:
- H1-H14 count;
- family membership;
- condition variables;
- primary statistics;
- horizons;
- directions;
- MDEs;
- sample floors;
- data fields.

Decision:

**REGISTRY REVIEW = PASS**

Protocol drafting may proceed.

Scientific experiment remains **NOT AUTHORIZED**.
