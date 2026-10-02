from __future__ import annotations

import argparse
from decimal import Decimal
import json
import sys
import time

from config import Settings
from exchange.binance_usdm_testnet import BinanceUsdMTestnetAdapter, floor_to_step
from storage import StateStore


def main() -> int:
    parser = argparse.ArgumentParser(description="M2 Binance USDⓈ-M Futures Demo acceptance")
    parser.add_argument("--apply-account-settings", action="store_true")
    parser.add_argument("--order-probe", choices=("BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT"))
    args = parser.parse_args()

    settings = Settings.from_env()
    if settings.mode != "DEMO":
        print(json.dumps({"status": "BLOCKED", "reason": "FIVES_MODE must be DEMO"}))
        return 2
    if not settings.testnet_credentials_present:
        print(json.dumps({"status": "BLOCKED", "reason": "Demo API credentials missing"}))
        return 2

    store = StateStore(settings.db_path)
    store.seed(settings.symbols, settings.default_leverage, settings.default_capital_budget_usdt, settings.default_timeframe)
    configs = store.get_symbol_configs()
    adapter = BinanceUsdMTestnetAdapter(
        mode=settings.mode,
        api_key=settings.testnet_api_key,
        api_secret=settings.testnet_api_secret,
        allowed_symbols=settings.symbols,
        allowed_timeframes=settings.allowed_timeframes,
    )

    result = {"status": "M2_DEMO_PROBE", "credentials_present": True, "one_way": adapter.is_one_way(), "symbols": {}}

    for symbol in settings.symbols:
        cfg = configs[symbol]
        timeframe = str(cfg["timeframe"])
        leverage = int(cfg["leverage"])
        rules = adapter.symbol_rules(symbol)
        bars = adapter.klines(symbol, timeframe, limit=3)
        brackets = adapter.leverage_brackets(symbol)
        positions = adapter.positions(symbol)
        result["symbols"][symbol] = {
            "enabled": bool(cfg["enabled"]),
            "capital_budget_usdt": float(cfg["capital_budget_usdt"]),
            "timeframe": timeframe,
            "requested_leverage": leverage,
            "status": rules.status,
            "contract_type": rules.contract_type,
            "quote_asset": rules.quote_asset,
            "tick_size": str(rules.tick_size) if rules.tick_size else None,
            "step_size": str(rules.step_size) if rules.step_size else None,
            "min_qty": str(rules.min_qty) if rules.min_qty else None,
            "min_notional": str(rules.min_notional) if rules.min_notional else None,
            "kline_rows": len(bars) if isinstance(bars, list) else None,
            "leverage_brackets_received": bool(brackets),
            "margin_type": adapter.margin_type(symbol),
            "positions_received": positions is not None,
        }

    result["balances_received"] = adapter.balances() is not None
    result["open_orders_received"] = adapter.open_orders() is not None

    if args.apply_account_settings:
        result["one_way_apply"] = adapter.ensure_one_way()
        result["symbol_apply"] = {}
        for symbol in settings.symbols:
            cfg = configs[symbol]
            result["symbol_apply"][symbol] = {
                "isolated": adapter.ensure_isolated(symbol),
                "leverage": adapter.set_leverage(symbol, int(cfg["leverage"])),
            }

    if args.order_probe:
        symbol = args.order_probe
        cfg = configs[symbol]
        rules = adapter.symbol_rules(symbol)
        bars = adapter.klines(symbol, str(cfg["timeframe"]), limit=1)
        if not isinstance(bars, list) or not bars:
            raise RuntimeError("no kline available for order probe")
        row = bars[-1]
        close = Decimal(str(row[4] if isinstance(row, list) else row["close"]))
        if not rules.tick_size or not rules.step_size or not rules.min_qty:
            raise RuntimeError("missing symbol filters")

        price = floor_to_step(close * Decimal("0.99"), rules.tick_size)
        min_notional = rules.min_notional or Decimal("5")
        qty_by_notional = (min_notional * Decimal("1.20")) / price
        quantity = floor_to_step(max(rules.min_qty, qty_by_notional), rules.step_size)
        if quantity <= 0:
            raise RuntimeError("computed invalid probe quantity")

        client_id = f"5sv1m2-{int(time.time())}"
        order = adapter.submit_limit_buy(symbol, quantity=quantity, price=price, client_order_id=client_id)
        result["order_probe_submit"] = order
        order_id = order.get("orderId") if isinstance(order, dict) else None
        try:
            result["order_probe_cancel"] = adapter.cancel_order(
                symbol,
                order_id=int(order_id) if order_id is not None else None,
                client_order_id=None if order_id is not None else client_id,
            )
        except Exception as exc:
            result["order_probe_cancel_error"] = str(exc)
            result["order_probe_query"] = adapter.query_order(symbol, client_order_id=client_id)

    print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
