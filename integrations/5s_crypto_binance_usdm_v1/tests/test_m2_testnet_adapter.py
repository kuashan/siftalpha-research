from __future__ import annotations

from decimal import Decimal
import unittest

from exchange.binance_usdm_testnet import (
    BinanceUsdMTestnetAdapter,
    TestnetGuardError,
    compute_clock_offset_ms,
    floor_to_step,
)


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def data(self):
        return self.payload


class FakeRest:
    def __init__(self):
        self.calls = []
        self.dual = False
        self.margin = "CROSSED"
        self.position_amt = "0"
        self.isolated_wallet = "250"
        self.unrealized_profit = "10"
        self.maint_margin = "12.5"

    def exchange_information(self):
        return FakeResponse({
            "symbols": [{
                "symbol": "BTCUSDT",
                "status": "TRADING",
                "contractType": "PERPETUAL",
                "quoteAsset": "USDT",
                "filters": [
                    {"filterType": "PRICE_FILTER", "tickSize": "0.10"},
                    {"filterType": "MARKET_LOT_SIZE", "minQty": "0.001", "maxQty": "1000", "stepSize": "0.001"},
                    {"filterType": "MIN_NOTIONAL", "notional": "5"},
                ],
            }]
        })

    def kline_candlestick_data(self, **kwargs):
        self.calls.append(("klines", kwargs))
        return FakeResponse([[1, "100", "101", "99", "100.5", "10"]])

    def notional_and_leverage_brackets(self, **kwargs):
        return FakeResponse([{"symbol": kwargs["symbol"], "brackets": [{"initialLeverage": 20}]}])

    def get_current_position_mode(self):
        return FakeResponse({"dualSidePosition": self.dual})

    def change_position_mode(self, **kwargs):
        self.dual = kwargs["dual_side_position"] == "true"
        self.calls.append(("change_position_mode", kwargs))
        return FakeResponse({"code": 200})

    def futures_account_balance_v3(self):
        return FakeResponse([{"asset": "USDT", "balance": "10000"}])

    def position_information_v2(self, **kwargs):
        symbol = kwargs.get("symbol") or "BTCUSDT"
        return FakeResponse([{
            "symbol": symbol,
            "marginType": self.margin,
            "positionAmt": self.position_amt,
            "entryPrice": "50000",
            "liquidationPrice": "42000",
            "isolatedWallet": self.isolated_wallet,
            "unRealizedProfit": self.unrealized_profit,
        }])

    def account_information_v3(self):
        return FakeResponse({
            "positions": [{
                "symbol": "BTCUSDT",
                "maintMargin": self.maint_margin,
                "isolatedWallet": self.isolated_wallet,
            }]
        })

    def modify_isolated_position_margin(self, **kwargs):
        self.calls.append(("modify_isolated_position_margin", kwargs))
        return FakeResponse({
            "symbol": kwargs["symbol"],
            "amount": str(kwargs["amount"]),
            "type": kwargs["type"],
        })

    def current_all_open_orders(self, **kwargs):
        return FakeResponse([])

    def query_order(self, **kwargs):
        return FakeResponse({"symbol": kwargs["symbol"], "status": "NEW"})

    def change_margin_type(self, **kwargs):
        self.margin = kwargs["margin_type"]
        self.calls.append(("change_margin_type", kwargs))
        return FakeResponse({"code": 200})

    def change_initial_leverage(self, **kwargs):
        self.calls.append(("change_initial_leverage", kwargs))
        return FakeResponse({"symbol": kwargs["symbol"], "leverage": kwargs["leverage"]})

    def new_order(self, **kwargs):
        self.calls.append(("new_order", kwargs))
        return FakeResponse({"symbol": kwargs["symbol"], "orderId": 123, "clientOrderId": kwargs["new_client_order_id"]})

    def cancel_order(self, **kwargs):
        self.calls.append(("cancel_order", kwargs))
        return FakeResponse({"symbol": kwargs["symbol"], "status": "CANCELED"})


class AdapterTests(unittest.TestCase):
    def adapter(self, rest=None):
        return BinanceUsdMTestnetAdapter(
            mode="DEMO",
            api_key="x",
            api_secret="y",
            allowed_symbols=("BTCUSDT",),
            allowed_timeframes=("15m", "1h", "1d"),
            client=rest or FakeRest(),
        )

    def test_hard_guard(self):
        a = BinanceUsdMTestnetAdapter(mode="PAPER", api_key="x", api_secret="y", client=FakeRest())
        with self.assertRaises(TestnetGuardError):
            a.balances()

    def test_symbol_rules(self):
        rules = self.adapter().symbol_rules("BTCUSDT")
        self.assertEqual(rules.contract_type, "PERPETUAL")
        self.assertEqual(rules.quote_asset, "USDT")
        self.assertEqual(rules.tick_size, Decimal("0.10"))
        self.assertEqual(rules.step_size, Decimal("0.001"))
        self.assertEqual(rules.min_notional, Decimal("5"))

    def test_selected_timeframe_reaches_sdk(self):
        rest = FakeRest()
        self.adapter(rest).klines("BTCUSDT", "1h", 3)
        self.assertEqual(rest.calls[-1][1]["interval"], "1h")

    def test_one_way_and_isolated(self):
        rest = FakeRest()
        rest.dual = True
        a = self.adapter(rest)
        self.assertTrue(a.ensure_one_way()["changed"])
        self.assertTrue(a.is_one_way())
        self.assertTrue(a.ensure_isolated("BTCUSDT")["changed"])
        self.assertEqual(a.margin_type("BTCUSDT"), "ISOLATED")

    def test_isolated_margin_add_reduce_and_metrics(self):
        rest = FakeRest()
        rest.margin = "ISOLATED"
        rest.position_amt = "0.005"
        a = self.adapter(rest)

        added = a.modify_isolated_position_margin("BTCUSDT", 25.0)
        self.assertEqual(added["type"], 1)
        self.assertEqual(rest.calls[-1][0], "modify_isolated_position_margin")
        self.assertEqual(rest.calls[-1][1]["position_side"], "BOTH")

        reduced = a.modify_isolated_position_margin("BTCUSDT", 10.0, reduce=True)
        self.assertEqual(reduced["type"], 2)

        metrics = a.position_metrics("BTCUSDT")
        self.assertEqual(metrics["entry_price"], 50000.0)
        self.assertEqual(metrics["liquidation_price"], 42000.0)
        self.assertEqual(metrics["isolated_margin_usdt"], 250.0)
        self.assertAlmostEqual(
            metrics["margin_ratio_percent"],
            12.5 / (250.0 + 10.0) * 100.0,
        )

    def test_isolated_margin_change_requires_open_isolated_position(self):
        rest = FakeRest()
        a = self.adapter(rest)
        with self.assertRaises(RuntimeError):
            a.modify_isolated_position_margin("BTCUSDT", 10.0)
        rest.margin = "ISOLATED"
        with self.assertRaises(RuntimeError):
            a.modify_isolated_position_margin("BTCUSDT", 10.0)

    def test_leverage_and_order_round_trip(self):
        rest = FakeRest()
        a = self.adapter(rest)
        leverage = a.set_leverage("BTCUSDT", 7)
        self.assertEqual(leverage["leverage"], 7)
        order = a.submit_limit_buy(
            "BTCUSDT",
            quantity=Decimal("0.001"),
            price=Decimal("100"),
            client_order_id="5sv1-test",
        )
        self.assertEqual(order["orderId"], 123)
        canceled = a.cancel_order("BTCUSDT", order_id=123)
        self.assertEqual(canceled["status"], "CANCELED")

    def test_clock_offset_uses_round_trip_midpoint(self):
        self.assertEqual(
            compute_clock_offset_ms(
                server_time_ms=10_500,
                local_before_ms=9_900,
                local_after_ms=10_100,
            ),
            500,
        )

    def test_floor_to_step(self):
        self.assertEqual(floor_to_step(Decimal("1.23456"), Decimal("0.001")), Decimal("1.234"))


if __name__ == "__main__":
    unittest.main()
