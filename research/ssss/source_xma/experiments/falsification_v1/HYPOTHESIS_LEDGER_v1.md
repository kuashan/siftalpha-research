# Falsification v1 — Final Hypothesis Ledger

Status: FINAL  
Date: 2026-09-28

This ledger is the terminal classification table for Falsification v1.

It supersedes provisional interpretation language in earlier Stage 1 / Interim reports without deleting those historical artifacts.

## Primary / closure-relevant hypotheses

| Hypothesis | Raw n | Wave n | Matched / incremental result | Clustered uncertainty | FDR p | Final status |
| --- | ---: | ---: | --- | --- | --- | --- |
| Upper confluence => general top/decline | 438 | 192 | 5-bar matched +0.08%; sector +0.11% | symbol CI -0.41%..+0.51%; month -0.57%..+0.69% | N/A: A/B direction criterion already fails | **REJECT** |
| Lower confluence => incremental buy/rebound | 345 | 130 | 10-bar -3.22%; 20-bar -3.77% matched excess | 10-bar symbol CI -4.56%..-1.74%; month -4.60%..-1.63% | N/A: effect opposite preregistered direction | **REJECT** |
| Lower penetration subtype rescue | 345 total | 130 | shallow -3.35%; deep-reclaim -3.44%; deep-no-reclaim -2.99% at 10 bars | no subtype promoted | N/A | **REJECT** |
| Independent common state transitions | large | see transition audits | small/mixed matched excess | no directional promotion | N/A | **OBSERVE / NOT PROMOTED** |
| Transition path progression | A: 284 / 338 anchors | 104 / 143 | target rates ~62.3% vs random 61.6%; 49.7% vs 47.7% | close to random baseline | N/A | **OBSERVE / NOT PROMOTED** |
| FAST_MID_ANALYTIC direction | thousands | N/A | cross-up and cross-down both inherit positive market drift | no standalone separation | N/A | **OBSERVE / NOT PROMOTED** |
| Time-to-confirm / time-stop | Upper 438; Lower 345 | 192 / 130 | midpoint changes faster than state departure | descriptive survival only | N/A | **OBSERVE / NOT PROMOTED** |
| Lower BELOW_VAL interaction | unavailable | N/A | Discovery only | N/A | N/A | **INCONCLUSIVE / DATA NOT AVAILABLE** |
| HYS2 2x2 / logistic interaction | unavailable | N/A | Discovery only | N/A | N/A | **INCONCLUSIVE / DATA NOT AVAILABLE** |
| HYS2 fire bottom/top global redundancy | Discovery strict sample | N/A | near-universal inside strict XMA events | reverse containment unavailable | N/A | **REDUNDANT WITHIN STRICT XMA EVENT SAMPLE** |
| Volume expanded holdout interaction | unavailable | N/A | Discovery only | N/A | N/A | **INCONCLUSIVE / DATA NOT AVAILABLE** |
| Breadth expanded holdout interaction | unavailable | N/A | Discovery only | N/A | N/A | **INCONCLUSIVE / DATA NOT AVAILABLE** |
| VIX expanded holdout dimensions | unavailable | N/A | Discovery rule neutral | N/A | N/A | **INCONCLUSIVE / DATA NOT AVAILABLE** |
| Crypto upper => general top | A 41; B 5 | separate market | A 5-bar raw +2.95%; opposite universal-top sign | 4 symbols only | N/A | **REJECT** |
| Crypto lower => incremental buy | A 37; B 7 | separate market | A 10-bar raw +2.29%, matched -6.17% | 4 symbols only | N/A | **REJECT** |

## Multiple-testing family closure

The frozen protocol requested BH-FDR q=0.10.

A complete BH-adjusted vector cannot be produced without post-hoc choices because:

1. BELOW_VAL and expanded auxiliary feature tests do not have preserved Validation A/B feature data.
2. "lower 10/20-bar matched excess" was registered as a joint directional requirement, not one uniquely specified scalar p-value.
3. "later state deterioration/improvement" did not freeze one scalar horizon or survival statistic for FDR input.

Choosing those scalar tests now would be a post-outcome specification change.

Therefore the v1 multiple-testing family is closed as:

**NO RESULT PROMOTED; COMPLETE BH VECTOR NOT COMPUTABLE AS PREREGISTERED.**

This is a protocol limitation, not permission to search for an alternative statistic.

v2 must preregister exactly one scalar primary statistic per FDR-family item before outcomes are inspected.

## Interpretation hierarchy

Final status meanings:

- REJECT:
  the registered trading/directional proposition failed its frozen criteria.

- OBSERVE / NOT PROMOTED:
  descriptive/lifecycle information may remain, but no trading rule is established.

- INCONCLUSIVE / DATA NOT AVAILABLE:
  v1 cannot test the registered proposition from preserved holdout data without post-outcome reconstruction.

- REDUNDANT WITHIN STRICT XMA EVENT SAMPLE:
  redundancy is demonstrated only inside the strict XMA sample; global redundancy is not claimed.

## Hard boundary

No REJECT result may be rescued inside v1 by:
- Regime mining;
- new matching variables;
- threshold retuning;
- new midpoint waiting thresholds;
- deeper path subdivisions;
- renamed same-window hypotheses.
