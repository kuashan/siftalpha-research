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


if __name__ == "__main__":
    unittest.main()
