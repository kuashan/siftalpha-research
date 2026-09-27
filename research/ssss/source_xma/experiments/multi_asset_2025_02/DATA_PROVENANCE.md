# February 2025 Multi-Asset Data Provenance

Run date: 2026-09-28  
Study window: 2025-02-03 through 2025-02-28

## Primary OHLCV source

Repository: `Devesh176/Replicating_portfolio`

| Symbol | Blob SHA |
|---|---|
| ABT | e9071f4a01e8f50cdab0155b0779ef09ef85e1d4 |
| AAPL | 5b722f4ab77fe3dad0afc4d83163c16732bca352 |
| AMZN | 8103be5ce8a065e2f753a4738b4b74a35361b291 |
| ORCL | 09ac3f0ada8c73f16758a0ef34b5afaa327a9a1c |
| INTC | 1e6b806f9c86dfc3d6e45eb87384b4e816bef442 |
| MSFT | ff6c2f3fe35add1a815855badf4ec4dc221aa86c |
| NVDA | 0181202463fd062000e23d332c04ac486bd25e9a |
| GOOGL | 8af3a5f957af8c8efd7f3f24fb6d6b34d7af9027 |
| META | 7c4a6dfe89f68a96491fafd8b326e4e1cfcc915b |
| JPM | 448829ca757707e1720562977314fbca879510e6 |
| XOM | 5fdf45e182d2e8d589fe368de8cdccf26fa173a1 |

## VIX context

Repository: `curingd/risk-factor-decomposition`  
Path: `Data/VIX.csv`  
Blob SHA: `fcc62747dabcfbcfb1ac8a76904f14b6bfdf57cf`

## ARM status

ARM remains in the Discovery universe.

It is not included in this February batch because the common OHLCV repository above has no ARM file and no second GitHub source was accepted merely to fill the gap.

Research rule:
**missing verified data => exclude and log, never fabricate.**

## Reproducibility notes

- Source-XMA is recomputed point-in-time for every study date.
- FIVEGZ5SE US-market branch is reproduced with `SCTYPE=1`.
- HYS2 US-market branch is reproduced with `SCQH=1`.
- `FORCAST` reproduction follows the public TongDaXin-style MyTT convention already documented in the FIVEGZ5SE evaluation.
