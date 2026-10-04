from pathlib import Path
import tempfile
import unittest

from storage import StateStore


class SignalMarkerTests(unittest.TestCase):
    def test_only_filled_orders_are_exposed_as_chart_labels(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = StateStore(Path(tmp) / "state.db")
            store.seed(("BTCUSDT",), 1, 100, "15m")

            store.begin_order(
                "BTCUSDT", "5sv1-BTC-1000-B60",
                side="BUY", quantity=1, price=100,
                strategy_id="5s_crypto_v1",
                target_fraction_after=0.60,
                strategy_state_after={},
                signal_bar_open_time=1000,
                execution_bar_open_time=2000,
                marker_side="B",
                strategy_signal="BUY_A",
            )
            self.assertEqual(store.list_trade_markers("BTCUSDT"), [])

            store.complete_order(
                "BTCUSDT", "5sv1-BTC-1000-B60",
                binance_order_id="1",
                status="FILLED",
                quantity=1,
                price=101,
            )

            store.begin_order(
                "BTCUSDT", "5sv1-BTC-3000-S100",
                side="SELL", quantity=1, price=102,
                strategy_id="5s_crypto_v1",
                target_fraction_after=0.0,
                strategy_state_after={},
                signal_bar_open_time=3000,
                execution_bar_open_time=4000,
                marker_side="X",
                strategy_signal="SELL_C",
            )
            store.complete_order(
                "BTCUSDT", "5sv1-BTC-3000-S100",
                binance_order_id="2",
                status="REJECTED",
                quantity=0,
                price=0,
            )

            markers = store.list_trade_markers("BTCUSDT")
            self.assertEqual(len(markers), 1)
            self.assertEqual(markers[0]["side"], "B")
            self.assertEqual(markers[0]["open_time"], 2000)
            self.assertEqual(markers[0]["signal"], "BUY_A")
            self.assertEqual(markers[0]["source"], "FILLED_ORDER")

    def test_partial_sell_is_s_and_full_exit_is_x(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = StateStore(Path(tmp) / "state.db")
            store.seed(("BTCUSDT",), 1, 100, "15m")
            for cid, execution, side in [
                ("ev1-BTC-1000-S50", 2000, "S"),
                ("ev1-BTC-3000-X100", 4000, "X"),
            ]:
                store.begin_order(
                    "BTCUSDT", cid,
                    side="SELL", quantity=1, price=100,
                    strategy_id="e",
                    target_fraction_after=0.25 if side == "S" else 0.0,
                    strategy_state_after={},
                    signal_bar_open_time=execution - 1000,
                    execution_bar_open_time=execution,
                    marker_side=side,
                    strategy_signal="E_SELL_1" if side == "S" else "E_SELL_3",
                )
                store.complete_order(
                    "BTCUSDT", cid,
                    binance_order_id=cid,
                    status="FILLED",
                    quantity=1,
                    price=100,
                )
            markers = store.list_trade_markers("BTCUSDT", "e")
            self.assertEqual([m["side"] for m in markers], ["S", "X"])


if __name__ == "__main__":
    unittest.main()
