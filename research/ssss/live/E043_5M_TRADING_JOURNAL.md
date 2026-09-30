# E043 5m Forward Paper Trading Journal

Status: ACTIVE FORWARD PAPER RESEARCH

Start rule:
Only 5m data from 2026-09-18 00:00 UTC or later may be used in this journal.

Assets:
BTC / ETH / BNB.

Instrument leverage:
10x.

This is paper trading. No live exchange order-routing connector is attached.

## Research discipline

Every OPEN / ADD / REDUCE / RE-ADD / CLOSE must document:
1. what was known at the decision bar;
2. which independent indicator families supported or opposed the action;
3. risk and stop state;
4. what later happened;
5. whether the rule or interpretation should change.

Losing trades remain in the journal.

## Indicator families

F1:
LMD2 / LMD3 structure.

F2:
causalized support/resistance / cost / SAR structure.

F3:
DXBD oscillator.

F4:
KDJ + accumulation/distribution + MACD resonance.

F5:
existing SSSS persistent structural state.

## Version history

v0.1-forward:
initial combined-indicator causal paper-trading scaffold.

## Observations

No order record is created until a causal OPEN condition is actually satisfied.

## Observation — 2026-09-20 18:09 UTC API activation audit

API source:
Massive Custom Bars API（市场数据接口）.

Data availability at activation:
- BTC latest completed 5m bar available: 2026-09-19 23:55 UTC;
- ETH latest completed 5m bar available: 2026-09-19 23:55 UTC;
- BNB latest completed 5m bar available: 2026-09-19 23:55 UTC.

Massive real-time Snapshot（实时快照）endpoint:
NOT_ENTITLED（当前套餐无权限）.

Freshness consequence:
latest market data are too stale for an executable leveraged decision.

Action:
WAIT_STALE_DATA for BTC / ETH / BNB.

No paper OPEN（开仓） is created.
No row is appended to E043_5M_PAPER_TRADES.csv because there is no executed paper order.

### Calibration-only last-bar states

BTC:
- close 81,233.91;
- ATR14 / close about 0.0955%;
- manual ADX about 74.03;
- EMA60 about 81,233.37;
- LMD2 / LMD3 trend-up = true;
- no B_GOLD / B_START;
- DXBD about -23.12;
- K/D about 55.83 / 68.67;
- decision = WAIT.

ETH:
- close 2,631.55;
- ATR14 / close about 0.1324%;
- manual ADX about 52.19;
- EMA60 about 2,632.06;
- LMD2 / LMD3 trend-down = true;
- no S_GOLD / S_START;
- DXBD about -1.76;
- K/D about 63.20 / 72.90;
- decision = WAIT.

BNB:
- close 761.82;
- ATR14 / close about 0.1034%;
- manual ADX about 52.83;
- EMA60 about 761.78;
- LMD2 / LMD3 trend-up = true;
- no B_GOLD / B_START;
- DXBD about -47.95;
- K/D about 53.12 / 67.27;
- decision = WAIT.

Lesson:
Directional regime alone is insufficient for OPEN（开仓）. At 10x instrument leverage, stale data are themselves an execution-risk veto.

## Correction — E043-ERRATA-001

The original journal start rule was too broad.
BTC / ETH / BNB 5m bars from 2026-09-18 00:00 UTC through 2026-09-19 23:55 UTC were already inspected before forward execution activation.

Therefore:
- this interval = SEEN_CALIBRATION_ONLY（已查看校准数据）;
- it can be used for warm-up / implementation verification only;
- it is not Forward（前瞻） or OOS（样本外） evidence;
- genuine forward evidence begins strictly after 2026-09-20 18:09 UTC;
- no historical trade will be backfilled from the seen interval.


## 2026-09-20T18:23:00Z infrastructure status

E043 forward-paper engine has been created and scheduled.

Data/API findings:
- Massive historical 5m data is available through 2026-09-19 23:55 UTC for BTC / ETH / BNB.
- Massive near-real-time 2026-09-20 5m data is NOT_ENTITLED under the current connected plan.
- Binance Public REST API is therefore configured as the intended forward 5m source in the E043 engine.

Cloud-run finding:
- GitHub Actions run #2 started for commit 4a186c3e5acac1655458eb12e463473b88a55246.
- It failed before any workflow step executed.
- runner_id = 0.
- steps = [].
- Therefore this is an infrastructure/runner-availability failure, not a strategy, indicator, or API-computation failure.

Trading consequence:
- no paper trade has been created;
- no historical trade is backfilled;
- the forward boundary remains unchanged;
- E043 remains ACTIVE but AUTOMATION_BLOCKED until a runner or another sub-hour execution service is available.
