# SLTD E7B 89-Stock Validation Protocol v1

Status: **FROZEN BEFORE RUN**

Purpose: test the user-confirmed E7B independent strategy against frozen V7 without changing V7.

Source:
- E7B spec: `SLTD_E7B_WICK_EXIT_STRATEGY_v1.md`
- V7 frozen commit: `5f9ea4d8fa434b54afdbf32a1cb21ef2f3cb4042`

Universe:
- prior frozen 79 stocks from Phase 7;
- fresh OOS10: WFC, LMT, PM, ADP, WM, UNP, SO, VZ, PANW, CVS;
- required total: 89 unique stocks.

Window:
- formal: 2020-01-02..2026-09-30;
- use archived warmup ledgers before formal window;
- daily selected timeframe.

Execution:
- signal on completed daily close;
- trade at next available daily open;
- 5 bps primary friction;
- 10 bps stress friction.

Systems:
1. frozen V7 candidate;
2. E7B;
3. Buy & Hold reference.

Required outputs:
- all89 / prior79 / OOS10 equal-weight Return, CAGR, MaxDD, Calmar;
- time in market, turnover, execution count;
- E7B trigger counts:
  - initial ZK1 wick crossing half-sale;
  - adapted C2 full exit;
  - BS full exit;
  - eligible gray-band full exit;
  - Low<ZK1 failed-breakout full exit;
- per-symbol metrics;
- breadth E7B vs V7;
- OOS10 separated from reused prior79;
- 2020..2026 yearly metrics;
- three-era metrics;
- 5bps and 10bps comparison;
- strict frozen V7 79-stock parity check.

No E7B rule may be changed after observing results in this run.

`SLTD_E7B_89_STOCK_VALIDATION_PROTOCOL_V1 = FROZEN`
