# Original SLTD V7 vs Buy & Hold — 79 Stocks v1

Status: **COMPLETE**

- Source base: `e05919539328407cb7a67f8a995f6b90f0d4156b`
- Strategy: original SLTD V7 12-rule candidate (`DROP_B3_S1_S3`)
- Chan integration: **none**
- Window: 2020-01-02 .. 2026-09-30
- Friction: 5 bps
- Execution: signal close -> next available open
- Universe: 79 stocks

## Breadth

- SLTD beats same-window buy-and-hold: **29 / 79**
- SLTD does not beat same-window buy-and-hold: **50 / 79**

Winner symbols:

`AMD, INTU, INTC, MU, NFLX, TGT, CVX, NKE, DIS, SBUX, GOOGL, BA, HON, RTX, CSCO, TXN, ISRG, SYK, BAC, ABT, BKNG, LOW, UPS, PEP, LIN, SCHW, ROST, AVGO, BMY`

Important: "beats buy-and-hold" means higher total return over the same window. It does **not** require SLTD itself to be positive. For example, NKE and BA both lost money under SLTD, but buy-and-hold lost more.

## Largest positive deltas (SLTD minus buy-and-hold)

| Symbol | SLTD | Buy & Hold | Delta |
|---|---:|---:|---:|
| AMD | +1580.06% | +1145.95% | +434.12 pp |
| INTU | +179.39% | +3.59% | +175.81 pp |
| INTC | +253.58% | +97.62% | +155.96 pp |
| MU | +1955.03% | +1822.93% | +132.10 pp |
| NFLX | +222.17% | +110.97% | +111.20 pp |

`SLTD_V7_ORIGINAL_VS_BUYHOLD_79_V1 = COMPLETE`
