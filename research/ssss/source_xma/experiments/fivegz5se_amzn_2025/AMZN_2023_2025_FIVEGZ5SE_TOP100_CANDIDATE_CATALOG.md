# AMZN 2023-2025 FIVEGZ5SE Top-100 Buy / Top-100 Sell Candidate Catalog

Status: **CANDIDATE_CATALOG_FROZEN_FOR_NEXT_PRUNING**

Date: 2026-09-29

## Scope

This catalog deliberately returns to the original broad AMZN development data
and combination grammar.

It does **not** use ABT or ORCL outcomes to create or rank candidates.

Development data:
- AMZN
- 2023-01-01 through 2025-12-31
- SCTYPE=1
- five dimensions included
- W1/W3/W5 are temporal features inside the combination grammar

Current V2 is preserved separately:
- BUY-A
- BUY-B
- SELL-A
- SELL-B
- SELL-C

The catalog does not replace V2.

## Search grammar

Interpretable atomic predicates: **109**

Candidate generation included:
- singles;
- all valid pairs;
- beam-expanded triples;
- beam-expanded four-condition rules;
- beam-expanded five-condition rules.

Minimum gate:
- >=15 de-duplicated events;
- >=3 events in each of 2023, 2024, 2025.

Exact duplicate event sets are collapsed, preferring the simpler logical rule.

## Ranking principle

Candidates are not ranked by raw historical return alone.

The conservative ranking emphasizes:
1. 90% lower confidence bound of 10-day mean (buy) / upper bound (sell);
2. worst-year mean across 2023/2024/2025;
3. overall 10-day mean;
4. median 10-day result;
5. simpler rules;
6. current-five-state matched incremental effect;
7. year-stratified random-date comparison.

Reported permutation p / BH q values are **post-selection diagnostics only**.
They do not correct the full combinatorial winner's-curse.

## Preserved V2 rules

- BUY-A: Trend W3 slope>0 + Momentum SHORT + Momentum W5 slope<0
- BUY-B: Capital GRAY + Capital W1 down + Acceleration W3 slope>0
- SELL-A: Trend GRAY + Acceleration positive >=3/5 + bullish dimensions >=3 on >=2/3 bars
- SELL-B: Capital W5 slope<0 + Momentum >= LIGHT_LONG + Anomaly W1 down
- SELL-C: Momentum LONG + Anomaly W3 up + bullish dimensions >=3 on >=2/3 bars

## Top 15 buy candidates

1. **B001** — trend.net5<0 + trend.slope3>0 + trend.neg5>=3 + accel.neg3>=2 | n=15 | 10d=6.641% | win=93.333% | 2023/24/25=7.526/5.556/6.841% | matched Δ=3.905 pp
2. **B002** — trend.net5<0 + trend.slope3>0 + momentum<=LS + accel.neg3>=2 | n=16 | 10d=6.376% | win=93.750% | 2023/24/25=6.671/5.556/6.841% | matched Δ=3.905 pp
3. **B003** — trend.net5<0 + trend.slope3>0 + accel.neg3>=2 + accel.neg5>=3 | n=15 | 10d=6.367% | win=93.333% | 2023/24/25=6.671/5.319/6.841% | matched Δ=3.905 pp
4. **B004** — capital=GRAY + capital.net1<0 + accel.slope3>0 + anomaly=GRAY | n=16 | 10d=5.575% | win=93.750% | 2023/24/25=4.690/6.492/5.565% | matched Δ=6.712 pp
5. **B005** — capital.slope3>0 + capital.slope5<0 + momentum.neg5>=3 + accel.net1>0 | n=15 | 10d=5.755% | win=93.333% | 2023/24/25=5.574/7.678/2.972% | matched Δ=8.526 pp
6. **B006** — trend.net5<0 + trend.slope3>0 + accel.neg3>=2 + bear_now>=2 | n=15 | 10d=5.919% | win=93.333% | 2023/24/25=5.360/5.556/6.841% | matched Δ=3.905 pp
7. **B007** — trend=GRAY + capital.net3>0 + capital.pos3>=2 + capital.slope5>0 + anomaly=GRAY | n=15 | 10d=4.922% | win=93.333% | 2023/24/25=7.694/4.407/3.875% | matched Δ=8.550 pp
8. **B008** — trend.slope3>0 + momentum<=LS + momentum.slope5<0 + accel<=LS + accel.neg5>=3 | n=16 | 10d=5.525% | win=100.000% | 2023/24/25=6.706/4.564/5.537% | matched Δ=4.286 pp
9. **B009** — capital=GRAY + capital.net1<0 + accel.slope3>0 | n=17 | 10d=4.911% | win=88.235% | 2023/24/25=4.690/6.492/4.539% | matched Δ=6.712 pp
10. **B010** — trend=GRAY + capital.slope3>0 + capital.pos3>=2 + capital.slope5>0 + anomaly=GRAY | n=16 | 10d=4.690% | win=93.750% | 2023/24/25=7.694/4.051/3.875% | matched Δ=7.769 pp
11. **B011** — trend.net5<0 + trend.slope3>0 + accel.neg3>=2 | n=17 | 10d=5.696% | win=88.235% | 2023/24/25=6.671/5.556/4.839% | matched Δ=3.011 pp
12. **B012** — trend.slope3>0 + momentum=SHORT + momentum.slope5<0 + bear_now>=2 | n=17 | 10d=5.257% | win=94.118% | 2023/24/25=5.079/5.041/5.537% | matched Δ=3.609 pp
13. **B013** — trend<=LS + trend.slope3>0 + trend.slope5<0 + momentum=SHORT | n=16 | 10d=5.366% | win=93.750% | 2023/24/25=4.912/5.488/5.537% | matched Δ=3.609 pp
14. **B014** — trend.slope3>0 + momentum=SHORT + momentum.slope5<0 + accel.neg3>=2 | n=17 | 10d=5.549% | win=94.118% | 2023/24/25=6.437/3.881/5.740% | matched Δ=4.012 pp
15. **B015** — trend.slope3>0 + momentum=SHORT + momentum.slope5<0 + accel<=LS | n=15 | 10d=5.407% | win=100.000% | 2023/24/25=6.706/3.881/5.537% | matched Δ=4.287 pp

## Top 15 sell candidates

1. **S001** — anomaly.net5>0 + anomaly.slope3>0 + impbars3>=2 | n=15 | 10d=-3.515% | win=33.333% | 2023/24/25=-3.517/-0.680/-7.288% | matched Δ=-8.328 pp
2. **S002** — trend.net1>0 + capital.pos5>=3 + anomaly>=L + bullbars5>=3 | n=20 | 10d=-2.145% | win=40.000% | 2023/24/25=-1.981/-1.363/-4.103% | matched Δ=-7.758 pp
3. **S003** — trend.net5<0 + momentum>=L + accel.pos3>=2 + accel.slope5<0 + accel.pos5>=3 | n=16 | 10d=-2.823% | win=31.250% | 2023/24/25=-2.184/-3.451/-2.205% | matched Δ=-3.955 pp
4. **S004** — trend.slope5<0 + momentum>=L + accel.pos3>=2 + accel.slope5<0 + accel.pos5>=3 | n=17 | 10d=-2.719% | win=29.412% | 2023/24/25=-2.017/-2.685/-3.334% | matched Δ=-3.795 pp
5. **S005** — trend.net1>0 + capital.pos5>=3 + anomaly=LONG + bullbars5>=3 | n=19 | 10d=-2.098% | win=42.105% | 2023/24/25=-1.885/-1.363/-4.103% | matched Δ=-7.758 pp
6. **S006** — trend=GRAY + accel.pos5>=3 + bullbars3>=2 | n=15 | 10d=-2.066% | win=40.000% | 2023/24/25=-4.013/-1.825/-1.497% | matched Δ=-5.756 pp
7. **S007** — trend.net3<0 + momentum>=L + accel.net1<0 + accel.pos5>=3 + bullbars3>=2 | n=21 | 10d=-2.094% | win=42.857% | 2023/24/25=-1.235/-2.842/-2.204% | matched Δ=-5.570 pp
8. **S008** — trend.net5<0 + momentum>=L + accel.net1<0 + accel.pos5>=3 | n=16 | 10d=-2.504% | win=31.250% | 2023/24/25=-4.013/-1.606/-3.035% | matched Δ=-3.931 pp
9. **S009** — trend.net1>0 + capital.pos5>=3 + anomaly>=L + anomaly.net1>0 | n=22 | 10d=-1.882% | win=45.455% | 2023/24/25=-1.591/-1.363/-4.103% | matched Δ=-6.456 pp
10. **S010** — trend.net3<0 + momentum>=L + accel.net1<0 + accel.pos5>=3 + anomaly=GRAY | n=19 | 10d=-2.159% | win=42.105% | 2023/24/25=-2.658/-0.966/-3.054% | matched Δ=-5.570 pp
11. **S011** — momentum.slope3>0 + anomaly.net5>0 + anomaly.slope3>0 + anomaly.slope5>0 | n=16 | 10d=-2.502% | win=37.500% | 2023/24/25=-3.479/-0.232/-2.816% | matched Δ=-6.723 pp
12. **S012** — trend.slope5<0 + accel=GRAY + accel.pos5>=3 | n=16 | 10d=-2.238% | win=31.250% | 2023/24/25=-1.935/-2.635/-1.787% | matched Δ=-4.171 pp
13. **S013** — trend.net1>0 + capital.pos5>=3 + anomaly.net1>0 + bull_now>=4 | n=22 | 10d=-1.763% | win=45.455% | 2023/24/25=-1.404/-1.363/-4.103% | matched Δ=-6.456 pp
14. **S014** — trend.net3<0 + capital>=L + accel.net1<0 + anomaly=GRAY + bullbars5>=3 | n=15 | 10d=-2.420% | win=33.333% | 2023/24/25=-1.166/-3.231/-3.286% | matched Δ=-4.553 pp
15. **S015** — trend.net1>0 + capital.pos5>=3 + anomaly=LONG + anomaly.net1>0 | n=21 | 10d=-1.827% | win=47.619% | 2023/24/25=-1.480/-1.363/-4.103% | matched Δ=-6.456 pp

## Full catalogs

- `AMZN_2023_2025_FIVEGZ5SE_TOP100_BUY_CANDIDATES.csv`
- `AMZN_2023_2025_FIVEGZ5SE_TOP100_SELL_CANDIDATES.csv`

Each row includes:
- full logical conditions;
- complexity;
- total and per-year sample counts;
- 5/10/20-day mean;
- 10-day median and win rate;
- MFE / MAE;
- 2023/2024/2025 means;
- conservative confidence bounds;
- exact-current-five-state matched incremental effect;
- year-stratified permutation diagnostic;
- displayed-catalog BH q;
- ranking score;
- V2 tag if the exact logical rule matches a preserved V2 family.

## Next use

Do not merge all top-100 rules into one strategy.

The next pruning stage should:
1. cluster highly overlapping event sets;
2. identify recurring logical motifs across the top ranks;
3. compare parent/child incremental information;
4. select a smaller diversified set of buy and sell families;
5. keep V2 intact as a fixed reference branch.

Closure:

`AMZN_2023_2025_TOP100_BUY_SELL_CATALOG = COMPLETE`
