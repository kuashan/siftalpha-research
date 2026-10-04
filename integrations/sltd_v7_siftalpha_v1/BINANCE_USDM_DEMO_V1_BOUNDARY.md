# SLTD V7 Multi-Strategy · Binance USDM Demo v1

Status: **IMPLEMENTATION BOUNDARY FROZEN**

Base:
`feature/sltd-v7-multistrategy-overlay-v1@fbeb9063f5910887fb7ce547943abc85db99ae51`

Execution capability source:
`feature/5s-crypto-binance-usdm-v1@3290e345916337a663fc41370ac2f7407b6cc537`

## Scope

The complete V7 multi-strategy host keeps five analysis entries:

- SLTD
- E
- 5s Stocks
- 缠论
- 顺势

Binance USDⓈ-M Demo automatic execution is enabled only for:

- `v7`
- `e`
- `5s_stocks`

Display/signal only:

- `chan`
- `support_resistance`

No new trading rules are invented for Chan or 顺势.

## Symbols

Only:

- BTCUSDT
- ETHUSDT
- BNBUSDT
- SOLUSDT

Long-only, USDⓈ-M perpetual, ONE_WAY, ISOLATED.

## Per-symbol execution ownership

A Binance ONE_WAY position is a single net position.

Therefore each symbol has exactly one automatic execution strategy at a time.
The chart may overlay multiple strategies, but one symbol cannot have SLTD/E/5s
simultaneously owning the same Binance position.

Strategy switching is allowed only when:
- automatic execution is stopped;
- Binance position is flat;
- there are no open orders;
- local strategy fraction is zero.

## Live-start boundary

Enabling a symbol never executes historical/backfilled signals.

At enable:
- account/order reconciliation must PASS;
- current latest completed bar becomes the baseline;
- live strategy state starts flat/current-process from that baseline;
- only later newly completed bars may generate executable actions.

## Missed-bar boundary

If the process discovers that more than one completed strategy bar passed since
the last processed bar, it must not replay old orders.

Instead:
`RECOVERY_BLOCKED`

This prevents fake "next-open" execution after the intended open was missed.

## Execution timing

Signal:
- completed selected bar t only.

Execution:
- next selected bar opening window;
- market order is submitted when the scheduler observes bar t closed and bar t+1 forming.

No forming bar participates in signal calculation.

## Strategy preservation

SLTD:
- BUY: +25pp; cap 100%
- ordinary SELL: sell 25% of current holding
- actual SELL arms C2
- actual BUY resets C2
- armed C2 hard condition -> full exit

E:
- condition 1/2/3 each once per cycle
- each +25pp; condition1+2 same event may add 50pp
- cap 75%
- SELL1: -50pp
- SELL2: -25pp
- SELL3/SELL4: full exit

5s:
- A/B -> 60%
- eligible C -> +40pp, cap 100%
- first isolated SELL-A/B -> half current holding
- SELL-C / same-bar multi / later distinct SELL -> full exit

## Binance capability

Reuse the verified 5s Crypto implementation semantics:
- Binance USDM Demo only for authenticated mutation
- API key/secret kept in current Python process only
- server-time synchronization
- ONE_WAY check
- ISOLATED margin
- configurable leverage
- exchange quantity/notional filters
- idempotent clientOrderId
- reduce-only sells
- account/order reconciliation
- PnL/account inspection

## Market data

BTC/ETH/BNB/SOL:
- Binance USDⓈ-M public candles
- no credentials needed for chart/analysis

Other symbols:
- existing provider routing remains unchanged.

## Completion

This branch is complete only when:
- offline unit tests pass;
- original multi-strategy regression stays green;
- Binance Demo adapter tests pass;
- strategy switching guards pass;
- no-history-backfill guard passes;
- missed-bar guard passes;
- SLTD/E/5s action semantics tests pass.

`SLTD_V7_BINANCE_USDM_DEMO_V1_BOUNDARY = FROZEN`
