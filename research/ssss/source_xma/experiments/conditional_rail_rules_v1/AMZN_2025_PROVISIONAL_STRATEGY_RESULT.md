# AMZN 2025 Provisional SSSS Strategy Test — Result

Status: COMPLETE / PROVISIONAL ONLY
Date: 2026-10-01

Method:
- strict first-observed point-in-time XMA25/XMA60
- signal at close, execute next open
- 5 bps adverse slippage
- long-only, fractional shares
- initial capital $10,000

Frozen rules:
- DOWN + new lower-fast excursion => 50% probe
- midpoint reclaim within 20 bars => 100%
- UP + new upper-fast excursion while long => reduce to 50%
- midpoint loss within 20 bars after that upper event => exit
- year-end liquidation for reporting

Results:
- evaluation: 2025-01-02 to 2025-12-30
- final capital: $11373.78
- total return: 13.74%
- max drawdown: -12.28%
- time in market: 22.5%
- actions: 4
- qualifying raw signals: 11
- conflict days: 0

Buy-and-hold benchmark with the same 5 bps adverse entry/exit:
- final capital: $10462.44
- return: 4.62%

## Actions
- 2025-03-31 -> 2025-04-01: PROBE_DOWN_LOWER, target 50%, price 187.9539
- 2025-04-09 -> 2025-04-10: CONFIRM_MID_RECLAIM, target 100%, price 185.5327
- 2025-06-16 -> 2025-06-17: REDUCE_UP_UPPER, target 50%, price 215.0924
- 2025-06-20 -> 2025-06-23: EXIT_MID_LOSS, target 0%, price 209.6851

## Qualifying raw signals
- 2025-01-21: UPPER_FAST_UP, close=230.7100, state=UP
- 2025-03-31: LOWER_FAST_DOWN, close=190.2600, state=DOWN
- 2025-04-16: LOWER_FAST_DOWN, close=174.3300, state=DOWN
- 2025-04-21: LOWER_FAST_DOWN, close=167.3200, state=DOWN
- 2025-06-16: UPPER_FAST_UP, close=216.1000, state=UP
- 2025-06-27: UPPER_FAST_UP, close=223.3000, state=UP
- 2025-07-11: UPPER_FAST_UP, close=225.0200, state=UP
- 2025-07-21: UPPER_FAST_UP, close=229.3000, state=UP
- 2025-08-14: UPPER_FAST_UP, close=230.9800, state=UP
- 2025-08-28: UPPER_FAST_UP, close=231.6000, state=UP
- 2025-09-04: UPPER_FAST_UP, close=235.6800, state=UP

Governance:
This is a provisional one-symbol one-year test. It does not complete Round 2 and is not a production rule.


```json
{
  "status": "PASS",
  "symbol": "AMZN",
  "evaluation": [
    "2025-01-02",
    "2025-12-30"
  ],
  "rows_total": 1759,
  "trading_days_2025": 249,
  "method": "STRICT_FIRST_OBSERVED_XMA25_XMA60",
  "rules": "DOWN lower=50%; midpoint reclaim=100%; UP upper=50%; midpoint loss=0%",
  "initial_capital": 10000,
  "final_capital": 11373.775938670018,
  "total_return": 0.13737759386700188,
  "max_drawdown": -0.12277291730621398,
  "time_in_market": 0.2248995983935743,
  "action_count": 4,
  "signal_count": 11,
  "conflict_days": [],
  "actions": [
    {
      "signal_date": "2025-03-31",
      "execution_date": "2025-04-01",
      "reason": "PROBE_DOWN_LOWER",
      "target": 0.5,
      "raw_open": 187.86,
      "execution_price": 187.95393,
      "quantity": 26.60226365045945,
      "shares_after": 26.60226365045945,
      "cash_after": 5000,
      "equity_after_open": 9997.501249375313
    },
    {
      "signal_date": "2025-04-09",
      "execution_date": "2025-04-10",
      "reason": "CONFIRM_MID_RECLAIM",
      "target": 1,
      "raw_open": 185.44,
      "execution_price": 185.53271999999998,
      "quantity": 26.94942433873659,
      "shares_after": 53.55168798919604,
      "cash_after": -9.094947017729282e-13,
      "equity_after_open": 9930.625020716514
    },
    {
      "signal_date": "2025-06-16",
      "execution_date": "2025-06-17",
      "reason": "REDUCE_UP_UPPER",
      "target": 0.5,
      "raw_open": 215.2,
      "execution_price": 215.0924,
      "quantity": 26.77584399459802,
      "shares_after": 26.77584399459802,
      "cash_after": 5759.280546823674,
      "equity_after_open": 11521.442174461168
    },
    {
      "signal_date": "2025-06-20",
      "execution_date": "2025-06-23",
      "reason": "EXIT_MID_LOSS",
      "target": 0,
      "raw_open": 209.78999,
      "execution_price": 209.685095005,
      "quantity": 26.77584399459802,
      "shares_after": 0,
      "cash_after": 11373.775938670018,
      "equity_after_open": 11373.775938670018
    }
  ],
  "signals": [
    {
      "date": "2025-01-21",
      "type": "UPPER_FAST_UP",
      "close": 230.71001,
      "high": 231.78,
      "zk": 230.10022090725525,
      "mid": 223.35644254305805,
      "state": "UP"
    },
    {
      "date": "2025-03-31",
      "type": "LOWER_FAST_DOWN",
      "close": 190.25999,
      "low": 184.39999,
      "zd": 189.3046728374464,
      "mid": 198.0414768186589,
      "state": "DOWN"
    },
    {
      "date": "2025-04-16",
      "type": "LOWER_FAST_DOWN",
      "close": 174.33,
      "low": 171.41,
      "zd": 172.23377598374032,
      "mid": 186.35704019618382,
      "state": "DOWN"
    },
    {
      "date": "2025-04-21",
      "type": "LOWER_FAST_DOWN",
      "close": 167.32001,
      "low": 165.28999,
      "zd": 169.56471669633274,
      "mid": 183.52244501068532,
      "state": "DOWN"
    },
    {
      "date": "2025-06-16",
      "type": "UPPER_FAST_UP",
      "close": 216.10001,
      "high": 217.059998,
      "zk": 214.95775427407037,
      "mid": 208.68717298922803,
      "state": "UP"
    },
    {
      "date": "2025-06-27",
      "type": "UPPER_FAST_UP",
      "close": 223.3,
      "high": 223.3,
      "zk": 219.33251790507683,
      "mid": 212.57304107953436,
      "state": "UP"
    },
    {
      "date": "2025-07-11",
      "type": "UPPER_FAST_UP",
      "close": 225.020004,
      "high": 226.67999,
      "zk": 224.22648627732528,
      "mid": 217.90907770021954,
      "state": "UP"
    },
    {
      "date": "2025-07-21",
      "type": "UPPER_FAST_UP",
      "close": 229.3,
      "high": 229.69,
      "zk": 227.10795341320735,
      "mid": 221.59839753550636,
      "state": "UP"
    },
    {
      "date": "2025-08-14",
      "type": "UPPER_FAST_UP",
      "close": 230.98,
      "high": 233.11,
      "zk": 231.45217164196492,
      "mid": 225.04363445155883,
      "state": "UP"
    },
    {
      "date": "2025-08-28",
      "type": "UPPER_FAST_UP",
      "close": 231.60001,
      "high": 232.71001,
      "zk": 231.9200642051454,
      "mid": 225.55180879769603,
      "state": "UP"
    },
    {
      "date": "2025-09-04",
      "type": "UPPER_FAST_UP",
      "close": 235.67999,
      "high": 235.77,
      "zk": 232.80555975117107,
      "mid": 226.62084781422652,
      "state": "UP"
    }
  ],
  "buy_hold": {
    "first_open": 222.029999,
    "last_close": 232.53,
    "final_capital": 10462.441438235408,
    "total_return": 0.046244143823540806
  }
}
```
