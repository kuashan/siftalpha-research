# AMZN 2023-2025 FIVEGZ5SE Top-100 Data-Driven Pruning v1

Status: **PRUNING_COMPLETE**

Date: 2026-09-29

Starting branch HEAD:
`2f122cb1cec1fd6a4efb11523cba9ca63d726330`

## Hard constraints

- AMZN 2023-2025 only.
- SCTYPE=1.
- Original formula operation prompts are not used as labels, targets, ranking inputs, or confirmation.
- W1 alone is not sufficient for promotion.
- W3/W5 formation context must be explicit or supported by matched longer-path separation.
- Current V2 BUY-A / BUY-B / SELL-A / SELL-B / SELL-C are preserved as fixed baselines.

## Evidence used for every candidate

1. de-duplicated event count and per-year counts;
2. 5/10/20-day forward returns;
3. 10-day median and win rate;
4. 10-day MFE / MAE;
5. 2023/2024/2025 direction consistency;
6. 90% conservative mean bound;
7. exact-current-five-state matched incremental return;
8. W1/W3/W5 temporal-path audit;
9. event-set Jaccard overlap;
10. parent-vs-child incremental Bootstrap test.

## Event-family pruning

Candidates with >=0.80 event-set overlap are treated as the same family for
representative selection.

- Buy Top100 formed **45** event families.
- Sell Top100 formed **49** event families.

>=0.90 overlap with a simpler/equal or more robust representative is marked
`REJECT_REDUNDANT_EVENT_SET`.

0.80-0.90 family overlap is marked `REJECT_SAME_FAMILY_NONREP` unless the
candidate is the chosen family representative or a frozen V2 baseline.

## Parent-child incremental rule

For each multi-condition candidate, each one-condition-deleted parent is rebuilt
from raw AMZN data.

The added condition must show meaningful directional incremental value.
A candidate can be rejected as `REJECT_NO_INCREMENTAL_VALUE` if a simpler
parent is not materially worse and the Bootstrap evidence does not support the
extra condition.

This prevents small-sample complexity from being rewarded merely because raw
historical return is slightly higher.

## Buy result

Top100 BUY -> **34 retained items**

Breakdown:

- RETAIN_FAMILY_REPRESENTATIVE: 32
- REJECT_REDUNDANT_EVENT_SET: 19
- REJECT_SAME_FAMILY_NONREP: 34
- RETAIN_V2_BASELINE: 2
- REJECT_NO_INCREMENTAL_VALUE: 10
- HOLD_MATCHED_DATA_LIMITED: 3

The 34 retained items include the two frozen V2 references.

Top retained buy families:

- **B001** — trend.net5<0 + trend.slope3>0 + trend.neg5>=3 + accel.neg3>=2; n=15; 10d=6.641%; win=93.333%; 2023/24/25=7.526/5.556/6.841%; matched Δ=3.905 pp; W3_W5_EXPLICIT
- **B004** — capital=GRAY + capital.net1<0 + accel.slope3>0 + anomaly=GRAY; n=16; 10d=5.575%; win=93.750%; 2023/24/25=4.690/6.492/5.565%; matched Δ=6.712 pp; LONGER_PATH_EXPLICIT
- **B005** — capital.slope3>0 + capital.slope5<0 + momentum.neg5>=3 + accel.net1>0; n=15; 10d=5.755%; win=93.333%; 2023/24/25=5.574/7.678/2.972%; matched Δ=8.526 pp; W3_W5_EXPLICIT
- **B007** — trend=GRAY + capital.net3>0 + capital.pos3>=2 + capital.slope5>0 + anomaly=GRAY; n=15; 10d=4.922%; win=93.333%; 2023/24/25=7.694/4.407/3.875%; matched Δ=8.550 pp; W3_W5_EXPLICIT
- **B008** — trend.slope3>0 + momentum<=LS + momentum.slope5<0 + accel<=LS + accel.neg5>=3; n=16; 10d=5.525%; win=100.000%; 2023/24/25=6.706/4.564/5.537%; matched Δ=4.286 pp; W3_W5_EXPLICIT
- **B009 (BUY_B)** — capital=GRAY + capital.net1<0 + accel.slope3>0; n=17; 10d=4.911%; win=88.235%; 2023/24/25=4.690/6.492/4.539%; matched Δ=6.712 pp; LONGER_PATH_EXPLICIT
- **B014** — trend.slope3>0 + momentum=SHORT + momentum.slope5<0 + accel.neg3>=2; n=17; 10d=5.549%; win=94.118%; 2023/24/25=6.437/3.881/5.740%; matched Δ=4.012 pp; W3_W5_EXPLICIT
- **B022 (BUY_A)** — trend.slope3>0 + momentum=SHORT + momentum.slope5<0; n=20; 10d=4.996%; win=90.000%; 2023/24/25=4.889/5.041/5.062%; matched Δ=3.609 pp; W3_W5_EXPLICIT
- **B018** — trend=GRAY + capital.net3>0 + capital.pos3>=2 + anomaly=GRAY; n=17; 10d=4.682%; win=94.118%; 2023/24/25=6.592/3.893/3.875%; matched Δ=6.054 pp; LONGER_PATH_EXPLICIT
- **B019** — trend.neg5>=3 + capital.net1<0 + accel.slope3>0; n=22; 10d=4.723%; win=95.455%; 2023/24/25=4.079/4.706/5.603%; matched Δ=5.639 pp; W3_W5_EXPLICIT
- **B029** — capital.slope3>0 + momentum=SHORT + momentum.net5<0 + accel.net3>0; n=17; 10d=5.107%; win=82.353%; 2023/24/25=5.304/7.261/2.790%; matched Δ=6.081 pp; W3_W5_EXPLICIT
- **B028** — trend<=LS + trend.slope3>0 + trend.slope5<0 + accel.neg3>=2; n=15; 10d=5.047%; win=93.333%; 2023/24/25=3.899/4.439/6.408%; matched Δ=4.766 pp; W3_W5_EXPLICIT
- **B037** — capital.slope3<0 + accel.neg3>=2 + accel.slope5>0 + bear_now>=2; n=15; 10d=5.209%; win=93.333%; 2023/24/25=4.226/7.109/4.339%; matched Δ=1.980 pp; W3_W5_EXPLICIT
- **B034** — trend.neg5>=3 + capital.net3<0 + accel.slope5>0 + bear_now>=3; n=18; 10d=4.697%; win=88.889%; 2023/24/25=4.463/5.164/4.115%; matched Δ=4.139 pp; W3_W5_EXPLICIT
- **B038** — capital.net3<0 + accel<=LS + accel.slope5>0 + bear_now>=2; n=16; 10d=4.795%; win=87.500%; 2023/24/25=4.503/5.304/4.469%; matched Δ=3.427 pp; W3_W5_EXPLICIT

## Sell result

Top100 SELL -> **27 retained items**

Breakdown:

- HOLD_MATCHED_DATA_LIMITED: 5
- RETAIN_FAMILY_REPRESENTATIVE: 24
- REJECT_REDUNDANT_EVENT_SET: 21
- RETAIN_V2_BASELINE: 3
- REJECT_SAME_FAMILY_NONREP: 30
- REJECT_NO_INCREMENTAL_VALUE: 6
- HOLD_STATISTICAL_UNCERTAINTY: 11

The 27 retained items include the three frozen V2 references.

Top retained sell families:

- **S003** — trend.net5<0 + momentum>=L + accel.pos3>=2 + accel.slope5<0 + accel.pos5>=3; n=16; 10d=-2.823%; win=31.250%; 2023/24/25=-2.184/-3.451/-2.205%; matched Δ=-3.955 pp; W3_W5_EXPLICIT
- **S004** — trend.slope5<0 + momentum>=L + accel.pos3>=2 + accel.slope5<0 + accel.pos5>=3; n=17; 10d=-2.719%; win=29.412%; 2023/24/25=-2.017/-2.685/-3.334%; matched Δ=-3.795 pp; W3_W5_EXPLICIT
- **S006 (SELL_A)** — trend=GRAY + accel.pos5>=3 + bullbars3>=2; n=15; 10d=-2.066%; win=40.000%; 2023/24/25=-4.013/-1.825/-1.497%; matched Δ=-5.756 pp; W3_W5_EXPLICIT
- **S020** — trend.net5<0 + momentum>=L + accel.pos3>=2 + accel.pos5>=3 + anomaly=GRAY; n=19; 10d=-2.327%; win=36.842%; 2023/24/25=-1.723/-2.506/-2.609%; matched Δ=-2.897 pp; W3_W5_EXPLICIT
- **S022** — capital.net5<0 + capital.pos3>=2 + accel>=L + accel.net5>0 + bullbars5>=3; n=15; 10d=-2.522%; win=33.333%; 2023/24/25=-1.785/-2.402/-3.257%; matched Δ=-1.784 pp; W3_W5_EXPLICIT
- **S019** — trend.net5<0 + accel.pos3>=2 + accel.slope5<0 + accel.pos5>=3 + anomaly=GRAY; n=22; 10d=-2.093%; win=40.909%; 2023/24/25=-2.082/-2.050/-2.236%; matched Δ=-3.056 pp; W3_W5_EXPLICIT
- **S023** — trend.slope5<0 + accel.pos3>=2 + accel.slope5<0 + accel.pos5>=3 + anomaly=GRAY; n=24; 10d=-2.102%; win=37.500%; 2023/24/25=-1.971/-1.680/-3.359%; matched Δ=-3.032 pp; W3_W5_EXPLICIT
- **S029** — capital.net5<0 + accel.net5>0 + accel.pos5>=3 + bullbars5>=3; n=19; 10d=-2.122%; win=31.579%; 2023/24/25=-1.486/-2.337/-2.372%; matched Δ=-2.887 pp; LONGER_PATH_EXPLICIT
- **S026** — accel.net3>0 + accel.pos3>=2 + anomaly.net3>0 + bullbars3>=2; n=15; 10d=-2.348%; win=40.000%; 2023/24/25=-1.468/-1.753/-5.585%; matched Δ=-3.879 pp; LONGER_PATH_EXPLICIT
- **S031 (SELL_B)** — capital.slope5<0 + momentum>=L + anomaly.net1<0; n=15; 10d=-1.969%; win=26.667%; 2023/24/25=-1.297/-1.919/-2.816%; matched Δ=-3.950 pp; LONGER_PATH_EXPLICIT
- **S047** — trend.pos3>=2 + capital.net5<0 + accel.net5>0 + bull_now>=2; n=17; 10d=-2.144%; win=35.294%; 2023/24/25=-1.785/-2.914/-1.485%; matched Δ=-2.072 pp; W3_W5_EXPLICIT
- **S037** — trend.net3<0 + capital>=L + momentum.slope5>0; n=16; 10d=-2.241%; win=31.250%; 2023/24/25=-0.584/-1.499/-6.068%; matched Δ=-4.266 pp; W3_W5_EXPLICIT
- **S024** — trend.net1>0 + capital.pos3>=2 + anomaly.net1>0 + bullbars5>=3; n=22; 10d=-2.208%; win=36.364%; 2023/24/25=-2.261/-1.259/-3.473%; matched Δ=-3.912 pp; W3_W5_EXPLICIT
- **S060** — momentum.slope3<0 + accel>=L + accel.slope3<0 + bull_now>=3; n=15; 10d=-2.130%; win=33.333%; 2023/24/25=-1.260/-3.160/-1.535%; matched Δ=-1.958 pp; LONGER_PATH_EXPLICIT
- **S069** — capital.net5<0 + momentum>=L + accel.pos3>=2 + anomaly.slope5<0; n=15; 10d=-2.396%; win=33.333%; 2023/24/25=-5.674/-0.857/-0.609%; matched Δ=-1.629 pp; W3_W5_EXPLICIT

## V2 preservation

Preserved regardless of new-family pruning:

- B009 = BUY-B
- B022 = BUY-A
- S006 = SELL-A
- S031 = SELL-B
- S075 = SELL-C

These are references, not automatically declared superior to every new family.

## Interpretation

This pruning is data-supported but remains development-sample pruning.

It does not prove generalization because the same AMZN 2023-2025 sample was
used for discovery and pruning.

ABT and ORCL outcomes were deliberately excluded from candidate creation and
pruning decisions.

The next step should not re-expand the search space. It should compare the
retained families as diversified mechanisms, quantify their cross-family event
overlap, and decide which small set deserves a separately versioned strategy
test while V2 stays frozen as a baseline.

Closure:

`TOP100_DATA_DRIVEN_PRUNING_V1 = COMPLETE`
