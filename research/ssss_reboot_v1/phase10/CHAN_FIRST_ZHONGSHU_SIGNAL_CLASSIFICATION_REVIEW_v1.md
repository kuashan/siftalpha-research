# Chan First-Zhongshu Signal Classification Review v1

Status: THEORY_REVIEW_COMPLETE_NO_PRODUCTION_CHANGE  
Branch: `feature/chan-standalone-v2`  
Base HEAD: `437876a6c45675890d9c72dc4e25f53071328a19`

## Question

The 79-stock funnel shows 17 L1+ B1/S1 candidates already satisfy:
- completed Zhongshu context,
- same-direction enter/leave,
- leave outside Zhongshu,
- required new extreme,
- weaker force,

but only 1 survives the same-level Zhongshu directional-link requirement. Of the 17:
- 14 have `link=None`,
- 2 have `link=overlap`,
- 1 has matching `link=up`.

Should the `link` requirement be removed so these candidates become standard B1/S1?

## Source review

### Original lesson 27
Core point: a trend requires at least two same-level Zhongshu. A divergence immediately after the first Zhongshu is not a standard trend divergence; it is a consolidation divergence. Therefore a first-Zhongshu case must not be automatically promoted to standard B1/S1.

### Original lesson 37
Core point: "no trend, no divergence" in the strict trend-divergence sense. In the standard a+A+b+B+c structure, A and B must be same-level Zhongshu and together form a trend context before c can be evaluated as standard trend divergence.

### Original lessons 53 and 101
Core point: small-level-to-large-level transitions may have no same-level B1/S1. In those cases B2/S2 is the formal supplement; B2/S2 must not be hard-dependent on a previously emitted B1/S1. This supports the current independent B2/S2 architecture.

### Original lesson 60
Core point: a consolidation-divergence point can be analogized to a first-class buy/sell point for interpretation, but strictly speaking it is not the standard first-class point. This argues for a separate classification rather than relabeling it B1/S1.

### Original lessons 20 and 24
Core point: same-level Zhongshu relationships define trend/continuation; MACD is auxiliary and should not replace structural classification.

## Mature implementation comparison

The mature open-source `Vespa314/chan.py` implementation explicitly distinguishes:
- `1`: standard first-class buy/sell point,
- `1p`: consolidation-divergence first-class-like point,
- `2`, `2s`, `3a`, `3b` as separate structural classes.

It also keeps configurable minimum Zhongshu count for standard B1/S1 and does not collapse consolidation-divergence directly into standard B1/S1.

## Decision

1. DO NOT remove the same-level Zhongshu link requirement from standard B1/S1 merely to increase signal count.
2. DO NOT relabel the 14 first-Zhongshu `link=None` candidates as standard B1/S1.
3. The theory-supported next research target is a separate class:
   - `B1P`: consolidation-divergence first-class-like buy
   - `S1P`: consolidation-divergence first-class-like sell
   These are auxiliary / diagnostic until broad validation passes.
4. Keep current standard B1/S1 semantics unchanged.
5. Keep B2/S2 independent of emitted B1/S1, consistent with small-level-to-large-level cases.
6. Before any production admission, run 79-stock broad validation for B1P/S1P:
   - count and distribution,
   - first-observed confirmation behavior,
   - MFE/MAE and forward-return distributions,
   - whether they mostly lead to center return, B2/S2, or continued trend,
   - compare against standard B1/S1 and L0 auxiliary signals.

## Practical interpretation

The current signal scarcity is real, but the correct fix is not to weaken standard B1/S1. The missing responsiveness should be studied through a separate consolidation-divergence signal class and lower-level auxiliary signals while preserving the canonical trend-divergence definition.
