# February 2025 Multi-Asset Source-XMA Report

Status: DISCOVERY / EXPLORATORY  
Protocol: frozen before run in `PROTOCOL_FROZEN_BEFORE_RUN.md`

Universe:
ABT, AAPL, AMZN, ORCL, INTC, MSFT, NVDA, GOOGL, META, JPM, XOM.

ARM is pending a verified daily source.

## Executive result

Four pre-registered combinations were compared:

1. XMA_ONLY
2. XMA_HYS2
3. XMA_FIVEGZ
4. XMA_HYS2_FIVEGZ

### Cross-symbol summary

| Variant | Mean return | Median | Positive | Worst | Best | Mean max DD | Avg exposure |
|---|---:|---:|---:|---:|---:|---:|---:|
| XMA_ONLY | -0.063% | 0.000% | 3/11 | -3.087% | +4.897% | -0.670% | 5.00% |
| XMA_HYS2 | -0.019% | 0.000% | 3/11 | -3.548% | +6.276% | -0.770% | 6.15% |
| XMA_FIVEGZ | +0.106% | 0.000% | 3/11 | **-1.271%** | +2.938% | **-0.233%** | 2.30% |
| XMA_HYS2_FIVEGZ | **+0.151%** | 0.000% | 3/11 | -1.733% | +4.318% | -0.338% | 3.45% |

## Interpretation

### 1. FIVEGZ5SE raw color states improved risk control

The FIVEGZ sizing variant materially reduced losses in:
- AMZN
- MSFT
- GOOGL
- META

Its main contribution was not "buy/sell labels".

It was the **color-state severity**:
- red / long = +2
- light-red / light-long = +1
- gray = 0
- light-green / light-short = -1
- green / short = -2

When several dimensions deteriorated, exposure was automatically smaller.

This is the strongest cross-symbol contribution found in February.

### 2. HYS2 was asymmetric

HYS2 helped NVDA:
- XMA_ONLY: +4.90%
- XMA_HYS2: +6.28%

But it worsened:
- AMZN
- MSFT
- GOOGL

Therefore HYS2 should **not** be a universal position-size booster.

Its promising use remains:
- low-side reversal confirmation,
- especially when another independent internal-quality measure is also improving.

### 3. Combined variant had the best mean return, but not the cleanest risk

XMA_HYS2_FIVEGZ produced the highest mean return (+0.151%), but XMA_FIVEGZ had:
- smaller worst-symbol loss,
- much smaller mean max drawdown,
- lower exposure.

Therefore the February result does **not** justify saying "use everything".

The more robust provisional core is:

```text
Source-XMA
+ FIVEGZ raw color-state sizing
```

HYS2 remains selective, not global.

## Major failure mode discovered: repeated probes

GOOGL is the clearest example.

The XMA core repeatedly saw lower-extreme conditions while the slow regime was still BULL/RANGE and repeatedly generated small probes.

But the security was in a persistent decline.

FIVEGZ color states often remained negative, which reduced damage, but the repeated probe mechanism itself is too permissive.

Candidate fix for the NEXT month:
- failed probe -> cooldown
- no immediate re-probe unless internal state materially improves

Do not retroactively apply this to February.

## Major missed-opportunity mode: slow-regime veto

INTC is the clearest example.

On 2025-02-11:
- Source-XMA regime was still BEAR
- XMA momentum was BOTH_UP
- RVOL ≈ 1.90
- HYS2 resonance = TRUE
- FIVEGZ score jumped to +9

On 2025-02-12:
- FIVEGZ score = +10
- all five dimensions were strongly positive
- Source-XMA regime was still BEAR

The frozen February engine did not trade because it prohibited long probes in BEAR.

Price then continued materially higher.

This suggests a future **Transition Override** candidate:

```text
BEAR slow regime
+ HYS2 resonance
+ very rapid FIVEGZ green -> red transition
+ strong relative volume
=> allow a SMALL counter-regime probe
```

This is only a Discovery hypothesis and must be frozen before the next run.

AAPL shows a related but weaker example:
- HYS2 resonance on Feb-12
- FIVEGZ score +6 with +6 daily jump
- XMA slow regime still BEAR

## Event-gap finding

GOOGL generated a breakout condition on Feb-04.

The next session opened far below the signal close.

A close-based system that blindly places a next-open market order can enter **after the thesis has already changed overnight**.

Candidate execution rule for the next run:
- if next open gaps materially against the signal, re-evaluate rather than blindly execute.

This is an execution-layer issue, not an XMA formula issue.

## Color transition finding

Raw state transitions contain more useful information than the labels.

Examples:
- RED -> LIGHT_RED = deterioration, not immediate sell
- LIGHT_RED -> GRAY = further loss of internal strength
- GREEN -> LIGHT_GREEN -> GRAY -> LIGHT_RED = recovery sequence
- large total score delta is often more informative than one static state

February data supports using:
- total five-dimension score
- score delta
- count of improving/deteriorating dimensions

rather than the source text labels.

## Provisional February conclusion

For the next research month, the strongest candidate architecture is:

```text
PRIMARY:
Source-XMA structure / first-observed XMA

RISK & SIZE:
FIVEGZ raw color-state score and transitions

SELECTIVE LOW-SIDE CONFIRMATION:
HYS2 resonance / fire-bottom

CONTEXT:
relative volume
VIX

NOT AUTOMATIC:
shorting
high-side HYS2 fire state
FIVEGZ "清仓/抄底" text
```

No February result is production evidence.
