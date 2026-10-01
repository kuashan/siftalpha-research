from pathlib import Path
import tempfile
import unittest

from storage import StateStore


class SignalMarkerTests(unittest.TestCase):
    def test_buy_and_sell_signal_markers_are_exposed_for_chart(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = StateStore(Path(tmp) / "state.db")
            store.seed(("BTCUSDT",), 1, 100, "15m")
            store.append_audit(
                "M3_SIGNAL_BAR",
                "BTCUSDT",
                "bar_open_time=1000;signal=BUY_A;pending=BUY_60",
            )
            store.append_audit(
                "M3_SIGNAL_BAR",
                "BTCUSDT",
                "bar_open_time=2000;signal=SELL_C;pending=SELL_ALL",
            )
            markers = store.list_signal_markers("BTCUSDT")
            self.assertEqual(markers[0]["side"], "B")
            self.assertEqual(markers[1]["side"], "S")
            self.assertEqual(markers[0]["open_time"], 1000)
            self.assertEqual(markers[1]["open_time"], 2000)


if __name__ == "__main__":
    unittest.main()
