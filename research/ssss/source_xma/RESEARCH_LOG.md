# Source-XMA Research Log

## 2026-09-27 — Track initialization

Repository baseline inspected before changes:
- repository: kuashan/siftalpha-research
- visibility: private
- default branch: main
- main HEAD at inspection: 512375038ba794536d785e51ad29fa14b9897d4b

Existing official SSSS state was read before opening this track.

Important boundary:
- existing official research uses a causal DEMA rewrite for the current model;
- this new track deliberately restores the original XMA for source-behavior research;
- the existing causal conclusions and model files were not modified.

Source findings recorded at initialization:
1. SSSS and ADKBY-E share the same double-XMA(25) core fast structure.
2. ADKBY-E's normalized 20000/80000 levels map to the same lower/upper fast-band geometry.
3. SSSS low slow-structure formula contains REF(H,11) in the low-weighted series.
4. ADKBY-E uses REF(L,11).
5. SSSS omits lag 19 and includes lag 20 at weight 1.
6. ADKBY-E includes both lag 19 and lag 20 at weight 1 while retaining denominator 210.
7. Therefore the slow structures are not mathematically identical and must be recorded separately.
8. The original three regime states leave an unclassified/expansion geometry; the research vocabulary adds EXPANSION / REGIME_UNCLEAR.
9. The author's icons/text remain comparison observations, not our target decision labels.

First case study:
- ABT daily
- anchor 2025-01-01
- first tradable session 2025-01-02
- walk forward toward latest available data
- preserve XMA
- no conventional return-optimization backtest

Evidence warning:
A later ABT history chart was already viewed before this repository track was initialized. Therefore the ABT replay is exploratory / previously seen, not OOS or Frozen OOS.

Current next step:
Obtain point-in-time ABT daily OHLCV and establish an exact, documented XMA reproduction path before populating observations.csv and decisions.csv.
