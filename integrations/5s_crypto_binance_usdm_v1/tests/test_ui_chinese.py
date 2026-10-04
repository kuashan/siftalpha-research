import pathlib
import unittest


class ChineseUiTests(unittest.TestCase):
    def test_visible_template_uses_chinese_labels(self):
        text = (pathlib.Path(__file__).parents[1] / "templates" / "index.html").read_text(encoding="utf-8")
        banned_visible_phrases = [
            "Strategy Slot",
            "Environment（环境）",
            "API Key",
            "API Secret",
            "LIVE LOCKED",
            "ISOLATED",
            "ONE-WAY",
            "Experimental",
            "Binance Futures Testnet",
        ]
        for phrase in banned_visible_phrases:
            self.assertNotIn(phrase, text)

        required = [
            "虚拟测试",
            "逐仓",
            "单向持仓",
            "接口密钥",
            "接口私钥",
            "币种策略",
            "策略总盈亏",
            "5s crypto v 1",
        ]
        for phrase in required:
            self.assertIn(phrase, text)

    def test_mobile_layout_switches_one_coin_panel_at_a_time(self):
        text = (pathlib.Path(__file__).parents[1] / "templates" / "index.html").read_text(encoding="utf-8")
        self.assertIn(".coin-panel{display:none", text)
        self.assertIn(".coin-panel.active{display:block}", text)
        self.assertIn("__COIN_TABS__", text)
        self.assertIn("tab.dataset.symbol", text)
        self.assertIn("activate(symbol)", text)

    def test_chart_and_compact_layout_contract(self):
        text = (pathlib.Path(__file__).parents[1] / "templates" / "index.html").read_text(encoding="utf-8")
        self.assertIn("kline-canvas", text)
        app_text = (pathlib.Path(__file__).parents[1] / "app.py").read_text(encoding="utf-8")
        self.assertIn("红涨", app_text)
        self.assertIn("绿跌", app_text)
        self.assertIn("买入", app_text)
        self.assertIn("卖出", app_text)
        self.assertIn("清仓", app_text)
        self.assertIn("trade-settings", text)
        self.assertIn("__TOP_CONNECTION_STATUS__", text)
        self.assertIn("__TOP_RECOVERY_STATUS__", text)
        self.assertIn("grid-template-columns:repeat(4,minmax(0,1fr))", text)
        self.assertIn("live-price-value", text)
        self.assertIn("chart-ohlc", text)
        self.assertIn("@ticker", text)
        self.assertIn("data-ohlc", app_text)
        self.assertNotIn("最近 {DISPLAY_KLINE_LIMIT} 根", app_text)
        self.assertIn("U本位永续", app_text)
        self.assertIn("data-timeframe-picker", app_text)
        self.assertIn('type="hidden" name="timeframe"', app_text)
        self.assertNotIn('<select name="timeframe"', app_text)
        self.assertIn("data-timeframe-option", text)
        self.assertIn("chartViewStates", text)
        self.assertIn("onpointerdown", text)
        self.assertIn("onwheel", text)
        self.assertIn("ondblclick", text)
        self.assertIn("Math.min(1000, allCandles.length)", text)
        self.assertIn("up ? '#ff7b82' : '#52d49a'", text)
        self.assertIn("snapshot-above-chart", app_text)
        self.assertLess(app_text.index("snapshot-above-chart"), app_text.index('class="market-chart"'))


if __name__ == "__main__":
    unittest.main()
