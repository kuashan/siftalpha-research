from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from threading import RLock
import time
from typing import Any

from engine.scheduler import M3Decision, TerminalDecisionError
from exchange.binance_usdm_testnet import floor_to_step


class ExecutionBlocked(TerminalDecisionError):
    pass


@dataclass(frozen=True)
class ExecutionOutcome:
    symbol: str
    actions: tuple[str, ...]
    order_ids: tuple[str, ...]


def _first(mapping: dict[str, Any], *keys: str, default: Any = None) -> Any:
    for key in keys:
        if key in mapping:
            return mapping[key]
    return default


def _float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


class M3Executor:
    def __init__(self, store, *, pnl_refresh_seconds: float = 60.0):
        self.store = store
        self.pnl_refresh_seconds = max(10.0, float(pnl_refresh_seconds))
        self._last_pnl_refresh: dict[str, float] = {}
        self._lock = RLock()

    @staticmethod
    def _client_order_id(symbol: str, bar_open_time: int, action: str) -> str:
        base = symbol[:-4] if symbol.endswith("USDT") else symbol
        code = {"BUY_60": "B60", "TOPUP_TO_100": "B40", "SELL_ALL": "S100"}[action]
        value = f"5sv1-{base}-{int(bar_open_time)}-{code}"
        if len(value) > 36:
            raise RuntimeError("clientOrderId too long")
        return value

    @staticmethod
    def _is_not_found(exc: Exception) -> bool:
        text = str(exc).lower()
        return "-2013" in text or "order does not exist" in text or "order not found" in text

    @staticmethod
    def _status(order: dict[str, Any]) -> str:
        return str(_first(order, "status", default="")).upper()

    def _recover_existing(self, adapter, symbol: str, client_id: str) -> dict[str, Any] | None:
        local = self.store.get_order(symbol, client_id)
        if local is None:
            return None
        if str(local.get("status") or "").upper() == "FILLED":
            return local
        try:
            remote = adapter.query_order(symbol, client_order_id=client_id)
        except Exception as exc:
            if self._is_not_found(exc):
                return None
            raise
        if not isinstance(remote, dict):
            raise RuntimeError("订单查询返回格式异常")
        self.store.complete_order(
            symbol,
            client_id,
            binance_order_id=str(_first(remote, "orderId", "order_id", default="") or ""),
            status=self._status(remote) or "UNKNOWN",
            quantity=_float(_first(remote, "executedQty", "executed_qty", "origQty", "orig_qty", default=0)),
            price=_float(_first(remote, "avgPrice", "avg_price", "price", default=0)),
        )
        if self._status(remote) != "FILLED":
            raise RuntimeError(f"existing market order is not FILLED: {self._status(remote)}")
        return remote

    def _submit_market(
        self,
        *,
        adapter,
        symbol: str,
        client_id: str,
        side: str,
        quantity: Decimal,
        reference_price: Decimal,
    ) -> dict[str, Any]:
        existing = self._recover_existing(adapter, symbol, client_id)
        if existing is not None:
            return existing
        inserted = self.store.begin_order(
            symbol, client_id, side=side, quantity=float(quantity), price=float(reference_price)
        )
        if not inserted:
            existing = self._recover_existing(adapter, symbol, client_id)
            if existing is not None:
                return existing

        order = (
            adapter.submit_market_buy(symbol, quantity=quantity, client_order_id=client_id)
            if side == "BUY"
            else adapter.submit_market_sell_reduce_only(symbol, quantity=quantity, client_order_id=client_id)
        )
        if not isinstance(order, dict):
            raise RuntimeError("币安订单返回格式异常")
        status = self._status(order)
        self.store.complete_order(
            symbol,
            client_id,
            binance_order_id=str(_first(order, "orderId", "order_id", default="") or ""),
            status=status or "UNKNOWN",
            quantity=_float(_first(order, "executedQty", "executed_qty", "origQty", "orig_qty", default=float(quantity))),
            price=_float(_first(order, "avgPrice", "avg_price", "price", default=float(reference_price))),
        )
        if status != "FILLED":
            raise RuntimeError(f"market order is not FILLED: {status}")
        return order

    def _validate_buy_environment(self, adapter, symbol: str, leverage: int) -> None:
        adapter.ensure_one_way()
        adapter.ensure_isolated(symbol)
        maximum = int(adapter.max_allowed_leverage(symbol))
        if leverage > maximum:
            raise ExecutionBlocked(f"请求杠杆 {leverage} 倍超过 {symbol} 当前允许的 {maximum} 倍")
        adapter.set_leverage(symbol, leverage)

    def _buy_quantity(self, *, adapter, symbol: str, margin_usdt: Decimal, leverage: int, reference_price: Decimal) -> Decimal:
        if reference_price <= 0:
            raise ExecutionBlocked("当前参考价格无效")
        available = Decimal(str(adapter.available_usdt()))
        if available < margin_usdt:
            raise ExecutionBlocked(f"可用保证金不足：需要 {margin_usdt} USDT，可用 {available} USDT")
        rules = adapter.symbol_rules(symbol)
        if rules.step_size is None or rules.min_qty is None:
            raise ExecutionBlocked("交易所没有返回有效的下单数量规则")
        notional = margin_usdt * Decimal(leverage)
        quantity = floor_to_step(notional / reference_price, rules.step_size)
        if quantity <= 0 or quantity < rules.min_qty:
            raise ExecutionBlocked("策略资金过小，无法达到最小下单数量")
        if rules.max_qty is not None and quantity > rules.max_qty:
            raise ExecutionBlocked("策略下单数量超过交易所最大限制")
        if rules.min_notional is not None and quantity * reference_price < rules.min_notional:
            raise ExecutionBlocked("策略资金过小，无法达到最小名义价值")
        return quantity

    def execute(self, symbol: str, decision: M3Decision, config: dict[str, Any], runtime: dict[str, Any], adapter, context: dict[str, Any]) -> ExecutionOutcome:
        with self._lock:
            fresh_config = self.store.get_symbol_configs().get(symbol)
            if not fresh_config or not bool(fresh_config["enabled"]):
                raise ExecutionBlocked("该币种已经停止，取消本次自动交易")

            signal_bar = int(decision.bar_open_time or context["signal_bar_open_time"])
            execution_bar = int(context["execution_bar_open_time"])
            reference_price = Decimal(str(context["reference_price"]))
            leverage = int(fresh_config["leverage"])
            budget = Decimal(str(fresh_config["capital_budget_usdt"]))
            order_ids: list[str] = []

            for action in decision.actions:
                fresh_runtime = self.store.get_runtime_states()[symbol]
                client_id = self._client_order_id(symbol, signal_bar, action)
                recovered = self._recover_existing(adapter, symbol, client_id)
                if recovered is not None:
                    order_id = str(_first(recovered, "orderId", "order_id", "binance_order_id", default=client_id))
                    if action == "BUY_60":
                        self.store.set_accounting_start_if_missing(symbol, execution_bar)
                        family = "A" if decision.signal.startswith("BUY_A") else "B"
                        self.store.set_execution_position_state(
                            symbol, current_fraction=0.60, c_confirmed=False,
                            entry_signal_open_time=signal_bar, entry_family=family, last_order_id=order_id,
                        )
                    elif action == "TOPUP_TO_100":
                        self.store.set_execution_position_state(
                            symbol, current_fraction=1.0, c_confirmed=True,
                            entry_signal_open_time=fresh_runtime.get("entry_signal_open_time"),
                            entry_family=fresh_runtime.get("entry_family"), last_order_id=order_id,
                        )
                    else:
                        self.store.set_execution_position_state(
                            symbol, current_fraction=0.0, c_confirmed=False,
                            entry_signal_open_time=None, entry_family=None, last_order_id=order_id,
                        )
                    order_ids.append(order_id)
                    continue

                position_amount = Decimal(str(adapter.position_amount(symbol)))
                if position_amount < 0:
                    raise ExecutionBlocked("检测到空头持仓；当前策略只允许做多，已阻止自动交易")

                if action in ("BUY_60", "TOPUP_TO_100"):
                    if action == "BUY_60" and position_amount != 0:
                        raise ExecutionBlocked("策略记录为空仓，但币安已有持仓；等待 M4 对账，不自动加仓")
                    if action == "TOPUP_TO_100" and position_amount <= 0:
                        raise ExecutionBlocked("策略准备补仓，但币安没有对应多头持仓；已阻止自动交易")
                    self._validate_buy_environment(adapter, symbol, leverage)
                    margin = budget * (Decimal("0.60") if action == "BUY_60" else Decimal("0.40"))
                    quantity = self._buy_quantity(
                        adapter=adapter, symbol=symbol, margin_usdt=margin,
                        leverage=leverage, reference_price=reference_price,
                    )
                    order = self._submit_market(
                        adapter=adapter, symbol=symbol, client_id=client_id,
                        side="BUY", quantity=quantity, reference_price=reference_price,
                    )
                    order_id = str(_first(order, "orderId", "order_id", default=client_id))
                    self.store.set_accounting_start_if_missing(symbol, execution_bar)
                    if action == "BUY_60":
                        family = "A" if decision.signal.startswith("BUY_A") else "B"
                        self.store.set_execution_position_state(
                            symbol, current_fraction=0.60, c_confirmed=False,
                            entry_signal_open_time=signal_bar, entry_family=family, last_order_id=order_id,
                        )
                    else:
                        self.store.set_execution_position_state(
                            symbol, current_fraction=1.0, c_confirmed=True,
                            entry_signal_open_time=fresh_runtime.get("entry_signal_open_time"),
                            entry_family=fresh_runtime.get("entry_family"), last_order_id=order_id,
                        )
                    order_ids.append(order_id)

                elif action == "SELL_ALL":
                    if position_amount == 0:
                        self.store.set_execution_position_state(
                            symbol, current_fraction=0.0, c_confirmed=False,
                            entry_signal_open_time=None, entry_family=None, last_order_id=None,
                        )
                        continue
                    rules = adapter.symbol_rules(symbol)
                    if rules.step_size is None:
                        raise ExecutionBlocked("交易所没有返回有效的平仓数量规则")
                    quantity = floor_to_step(abs(position_amount), rules.step_size)
                    if quantity <= 0:
                        raise ExecutionBlocked("当前持仓小于交易所最小可平数量")
                    order = self._submit_market(
                        adapter=adapter, symbol=symbol, client_id=client_id,
                        side="SELL", quantity=quantity, reference_price=reference_price,
                    )
                    order_id = str(_first(order, "orderId", "order_id", default=client_id))
                    self.store.set_execution_position_state(
                        symbol, current_fraction=0.0, c_confirmed=False,
                        entry_signal_open_time=None, entry_family=None, last_order_id=order_id,
                    )
                    order_ids.append(order_id)
                else:
                    raise RuntimeError(f"unknown M3 action: {action}")

            self.refresh_accounting(symbol, adapter, force=True)
            self.store.append_audit(
                "M3_EXECUTION_PASS", symbol,
                f"signal={decision.signal};actions={'+'.join(decision.actions)};orders={','.join(order_ids) or 'NONE'}",
            )
            return ExecutionOutcome(symbol=symbol, actions=decision.actions, order_ids=tuple(order_ids))

    def refresh_accounting(self, symbol: str, adapter, *, force: bool = False) -> None:
        now = time.monotonic()
        if not force and now - self._last_pnl_refresh.get(symbol, 0.0) < self.pnl_refresh_seconds:
            return
        runtime = self.store.get_runtime_states()[symbol]
        start_time = runtime.get("accounting_start_time_ms")
        positions = adapter.positions(symbol)
        rows = positions if isinstance(positions, list) else [positions]
        unrealized = 0.0
        for row in rows:
            if isinstance(row, dict) and str(_first(row, "symbol", default="")).upper() == symbol:
                unrealized += _float(_first(row, "unRealizedProfit", "unrealizedProfit", "unrealized_profit", default=0))

        realized = 0.0
        funding = 0.0
        commission_income = 0.0
        if start_time is not None:
            income = adapter.income_history(symbol, start_time=int(start_time), limit=1000)
            for row in (income if isinstance(income, list) else [income]):
                if not isinstance(row, dict):
                    continue
                kind = str(_first(row, "incomeType", "income_type", default="")).upper()
                value = _float(_first(row, "income", default=0))
                if kind == "REALIZED_PNL":
                    realized += value
                elif kind == "FUNDING_FEE":
                    funding += value
                elif kind == "COMMISSION":
                    commission_income += value

        self.store.set_pnl(
            symbol, realized_pnl=realized, unrealized_pnl=unrealized,
            funding_fee=funding, trading_fee=-commission_income,
        )
        self._last_pnl_refresh[symbol] = now
