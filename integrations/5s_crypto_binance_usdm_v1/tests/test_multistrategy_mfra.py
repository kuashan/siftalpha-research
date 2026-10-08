from __future__ import annotations

import csv
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import math
import unittest

from engine.execution import M3Executor
from storage import StateStore
from strategy import matrixquant_strategy as mq
from strategy.registry import (
    STRATEGY_5S, STRATEGY_SSSS, STRATEGY_MFRA,
    decide_mfra, strategy_ids, strategy_signal_label,
)
from tests.test_multistrategy_ssss import FakeAdapter

_FIXTURE = Path(__file__).parent / "fixtures" / "MatrixQuant_BTC_4H_TV_REAL_400.csv"


def _real_chart_bars():
    rows = []
    for item in csv.DictReader(_FIXTURE.open(encoding="utf-8-sig")):
        fields = item["消息"].split("|")
        assert fields[0] == "TVR3" and len(fields) == 20
        timestamp = fields[1].replace(" ", "T") + "+00:00"
        from datetime import datetime
        ts = int(datetime.fromisoformat(timestamp).timestamp() * 1000)
        o, h, l, c = (float(z) for z in fields[2:6])
        rows.append((ts, o, h, l, c, 1.0, fields))
    return rows


class MatrixQuantFormulaParityTests(unittest.TestCase):
    def test_user_exported_real_tradingview_400_bar_pai(self):
        bars = _real_chart_bars()
        self.assertEqual(len(bars), 400)
        values = mq.evaluate_pai(bars)
        for k in range(250, 400):
            ref = bars[k][6]
            self.assertIsNotNone(values[k].raw)
            self.assertAlmostEqual(values[k].raw, float(ref[6]), delta=0.0001)
            self.assertEqual(values[k].buy, bool(int(ref[18])), (k, "BUY", ref[1]))
            self.assertEqual(values[k].sell, bool(int(ref[19])), (k, "SELL", ref[1]))
        print("REAL_TV_MFRA_PAI_150_BAR_PARITY_PASS")

    def test_invalid_ohlc_and_duplicate_time_rejected(self):
        with self.assertRaises(ValueError):
            mq.evaluate_pai([(1, 3, 2, 1, 2), (1, 3, 2, 1, 2)])
        with self.assertRaises(ValueError):
            mq.evaluate_pai([(1, 2, 1, 3, 2)])


    def test_indicator_signals_from_real_tradingview_history_are_not_fills(self):
        bars = _real_chart_bars()
        closed = mq.evaluate_pai(bars)
        markers = mq.chart_signal_markers(closed)
        self.assertTrue(markers, "400 historical BTC 4h candles should contain PAI threshold signals")
        self.assertEqual(
            len(markers), sum(int(p.buy) + int(p.sell) for p in closed)
        )
        for marker in markers:
            self.assertEqual(set(marker), {"open_time", "kind", "text"})
            self.assertIn(marker["kind"], {"MFRA_PAI_BUY", "MFRA_PAI_SELL"})
            self.assertEqual(marker["text"], "BUY" if marker["kind"] == "MFRA_PAI_BUY" else "SELL")
        # Previous TradingView/Pine R3 export established parity on indices 250:400.
        expected = {
            (bars[i][0], "MFRA_PAI_BUY" if bool(int(bars[i][6][18])) else "MFRA_PAI_SELL")
            for i in range(250, 400)
            if bool(int(bars[i][6][18])) or bool(int(bars[i][6][19]))
        }
        actual = {(m["open_time"], m["kind"]) for m in markers
                  if m["open_time"] >= bars[250][0]}
        self.assertEqual(actual, expected)

    def test_mfra_chart_payload_has_historical_signals_without_filled_orders(self):
        import app
        rows = _real_chart_bars()
        # Last returned candle is still forming. Intentionally make it extreme:
        # neither the indicator curve nor signals may include this candle.
        time_delta = rows[-1][0] - rows[-2][0]
        last = rows[-1]
        still_open = (
            last[0] + time_delta, last[4], last[4] * 1.50,
            last[4] * 0.50, last[4] * 1.40, 1.0
        )
        rows_with_open = [row[:6] for row in rows] + [still_open]
        cfg = {"BTCUSDT": {"strategy_id": STRATEGY_MFRA, "timeframe": "4h"}}
        rt = {"BTCUSDT": {"run_state": "STOPPED", "current_fraction": 0.0, "last_signal": "HOLD"}}
        with patch.object(app.store, "get_symbol_configs", return_value=cfg), \
             patch.object(app.store, "get_runtime_states", return_value=rt), \
             patch.object(app.store, "list_trade_markers", return_value=[]), \
             patch.object(app.testnet_session, "credentials", return_value=("", "")), \
             patch.object(app.probe, "klines", return_value=rows_with_open):
            payload = app.chart_payload("BTCUSDT")
        self.assertEqual(payload["strategy_id"], STRATEGY_MFRA)
        self.assertEqual(payload["markers"], [], "zero FILLED orders means zero execution B/X")
        self.assertTrue(payload["strategy_indicator_markers"], "PAI signal labels should appear even while stopped")
        observed = {(m["open_time"], m["kind"]) for m in payload["strategy_indicator_markers"]}
        expected = {(m["open_time"], m["kind"]) for m in mq.chart_signal_markers(mq.evaluate_pai(rows))}
        self.assertEqual(observed, expected)
        self.assertNotIn(still_open[0], [m["open_time"] for m in payload["strategy_indicator_markers"]])
        self.assertEqual(payload["strategy_overlay"][-1]["open_time"], rows[-1][0])
        self.assertEqual(payload["candles"][-1]["open_time"], still_open[0])


class MatrixQuantChartContractTests(unittest.TestCase):
    def test_js_distinguishes_unfilled_mfra_signal_from_filled_order(self):
        template = (Path(__file__).parents[1] / "templates" / "index.html").read_text(encoding="utf-8")
        app_source = (Path(__file__).parents[1] / "app.py").read_text(encoding="utf-8")
        self.assertIn("mfra_chart_signal_markers(points)", app_source)
        self.assertIn("kind === 'MFRA_PAI_BUY' || kind === 'MFRA_PAI_SELL'", template)
        self.assertIn("shape: isMfra ? (isBuy ? 'arrowUp' : 'arrowDown') : 'circle'", template)
        self.assertIn("BUY/红色SELL=PAI收盘确认的指标信号", template)
        self.assertIn("B/X=仅成交成功后显示", template)




class MatrixQuantDecisionTests(unittest.TestCase):
    def setUp(self):
        self.rows = [(i * 900000, 100, 110, 90, 100, 1) for i in range(260)]

    def test_registration_preserves_5s_ssss(self):
        self.assertEqual(strategy_ids(), (STRATEGY_5S, STRATEGY_SSSS, STRATEGY_MFRA))
        self.assertIn("25%", strategy_signal_label(STRATEGY_MFRA, "MFRA_BUY_PLUS5"))

    def _decide(self, fraction, buy=False, sell=False):
        fake = [mq.PAIPoint(i * 900000, -7.0 if sell else 8.0, False, False) for i in range(259)]
        fake.append(mq.PAIPoint(259 * 900000, -8.0 if sell else 9.0, buy, sell))
        with patch("strategy.registry.matrixquant_strategy.evaluate_pai", return_value=fake):
            return decide_mfra(self.rows, {"current_fraction": fraction, "strategy_state": {}}, "15m")

    def test_ssss_buy25_progression_no_overbuy_and_full_sell(self):
        for fraction,target in [(0, .25),(.25,.5),(.5,.75),(.75,1.0),(1.0,1.0)]:
            d=self._decide(fraction,buy=True)
            self.assertEqual(d.signal,"MFRA_BUY_PLUS5")
            if target==fraction:
                self.assertEqual(d.steps, ())
            else:
                self.assertEqual(len(d.steps),1)
                self.assertAlmostEqual(d.steps[0].target_fraction,target)
                self.assertEqual(d.steps[0].order_code,"B25")
        d=self._decide(.75,sell=True)
        self.assertEqual(d.steps[0].target_fraction,0.0)
        self.assertEqual(d.steps[0].order_code,"X100")
        self.assertEqual(self._decide(0,sell=True).steps,())

    def test_sell_takes_priority_if_both_flags(self):
        self.assertEqual(self._decide(.5,buy=True,sell=True).signal,"MFRA_SELL_MINUS5")


class MatrixQuantExecutionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory()
        self.store=StateStore(Path(self.tmp.name)/"mfra.db")
        self.store.seed(("BTCUSDT",),2,100,"15m")
        self.store.set_symbol_strategy("BTCUSDT",STRATEGY_MFRA,"15m")
        self.store.set_symbol_enabled("BTCUSDT",True)
        self.adapter=FakeAdapter()
        self.executor=M3Executor(self.store)

    def tearDown(self):
        self.tmp.cleanup()

    def _execute(self,dec,execution_open):
        return self.executor.execute(
            "BTCUSDT",dec,self.store.get_symbol_configs()["BTCUSDT"],
            self.store.get_runtime_states()["BTCUSDT"],self.adapter,
            {"signal_bar_open_time":dec.bar_open_time,
             "execution_bar_open_time":execution_open,
             "reference_price":100.0,"timeframe":"15m"},
        )

    def test_buy25_then_buy25_then_sell_all_and_only_filled_markers(self):
        self.assertEqual(self.store.list_trade_markers("BTCUSDT",STRATEGY_MFRA),[])
        for i in range(2):
            fraction=i*.25
            fake = [
                mq.PAIPoint(n*900000, 7.0, False, False)
                for n in range(259)
            ]+[mq.PAIPoint((260+i)*900000, 8.0, True, False)]
            with patch("strategy.registry.matrixquant_strategy.evaluate_pai",return_value=fake):
                dec=decide_mfra([(n*900000,100,110,90,100,1) for n in range(260)],
                                self.store.get_runtime_states()["BTCUSDT"],"15m")
            self.assertAlmostEqual(dec.steps[0].target_fraction,fraction+.25)
            self._execute(dec,(261+i)*900000)
        self.assertAlmostEqual(float(self.store.get_runtime_states()["BTCUSDT"]["current_fraction"]),.5)
        fake = [mq.PAIPoint(n*900000, -7,False,False) for n in range(259)]
        fake.append(mq.PAIPoint(262*900000, -8,False,True))
        with patch("strategy.registry.matrixquant_strategy.evaluate_pai",return_value=fake):
            dec=decide_mfra([(n*900000,100,110,90,100,1) for n in range(260)],
                            self.store.get_runtime_states()["BTCUSDT"],"15m")
        self._execute(dec,263*900000)
        self.assertEqual([m["side"] for m in self.store.list_trade_markers("BTCUSDT",STRATEGY_MFRA)],["B","B","X"])
        self.assertEqual(self.adapter.position,Decimal("0"))
        order_list=self.store.list_orders("BTCUSDT")
        self.assertEqual(len(order_list),3)
        self.assertTrue(all(o["status"]=="FILLED" for o in order_list))
        self.assertTrue(all(str(o["client_order_id"]).startswith("mfra-BTC-") for o in order_list))

if __name__=="__main__":
    unittest.main()
