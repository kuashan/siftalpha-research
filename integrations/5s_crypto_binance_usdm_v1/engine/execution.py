from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from threading import RLock
import time
from typing import Any

from engine.scheduler import TerminalDecisionError
from exchange.binance_usdm_testnet import floor_to_step
from strategy.registry import STRATEGY_5S, StrategyStep, get_spec


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
    """Strategy-agnostic Binance execution.

    Strategy adapters decide target position fractions. This class only turns
    target-position deltas into Binance orders and persists the resulting state.
    """

    def __init__(self, store, *, pnl_refresh_seconds: float = 60.0):
        self.store = store
        self.pnl_refresh_seconds = max(10.0, float(pnl_refresh_seconds))
        self._last_pnl_refresh: dict[str, float] = {}
        self._lock = RLock()

    @property
    def operation_lock(self) -> RLock:
        return self._lock

    @staticmethod
    def _client_order_id(symbol: str, bar_open_time: int, action: str) -> str:
        """Backward-compatible 5s V1 ID helper retained for old ledgers/tests."""
        base = symbol[:-4] if symbol.endswith("USDT") else symbol
        code = {"BUY_60": "B60", "TOPUP_TO_100": "B40", "SELL_ALL": "S100"}[action]
        value = f"5sv1-{base}-{int(bar_open_time)}-{code}"
        if len(value) > 36:
            raise RuntimeError("clientOrderId too long")
        return value

    @staticmethod
    def _strategy_client_order_id(
        strategy_id: str,
        symbol: str,
        bar_open_time: int,
        order_code: str,
    ) -> str:
        spec = get_spec(strategy_id)
        base = symbol[:-4] if symbol.endswith("USDT") else symbol
        value = f"{spec.order_prefix}-{base}-{int(bar_open_time)}-{order_code}"
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
        strategy_id: str,
        target_fraction_after: float,
        strategy_state_after: dict[str, object],
    ) -> dict[str, Any]:
        existing = self._recover_existing(adapter, symbol, client_id)
        if existing is not None:
            return existing

        inserted = self.store.begin_order(
            symbol,
            client_id,
            side=side,
            quantity=float(quantity),
            price=float(reference_price),
            strategy_id=strategy_id,
            target_fraction_after=target_fraction_after,
            strategy_state_after=strategy_state_after,
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

    def _buy_quantity(
        self,
        *,
        adapter,
        symbol: str,
        margin_usdt: Decimal,
        leverage: int,
        reference_price: Decimal,
    ) -> Decimal:
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

    @staticmethod
    def _legacy_steps(decision, runtime: dict[str, Any]) -> tuple[StrategyStep, ...]:
        """Convert the old 5s-only M3Decision for compatibility with frozen tests."""
        fraction = float(runtime.get("current_fraction") or 0.0)
        state = dict(runtime.get("strategy_state") or {})
        if not state:
            if runtime.get("entry_signal_open_time") is not None:
                state["entry_signal_open_time"] = int(runtime["entry_signal_open_time"])
            if runtime.get("entry_family"):
                state["entry_family"] = runtime["entry_family"]
            state["c_confirmed"] = bool(runtime.get("c_confirmed"))

        out: list[StrategyStep] = []
        for action in getattr(decision, "actions", ()):
            if action == "BUY_60":
                family = "A" if str(decision.signal).startswith("BUY_A") else "B"
                state = {
                    "c_confirmed": False,
                    "entry_signal_open_time": int(decision.bar_open_time),
                    "entry_family": family,
                }
                fraction = 0.60
                out.append(StrategyStep("5S_BUY_60", "B60", fraction, (f"BUY_{family}",), dict(state)))
            elif action == "TOPUP_TO_100":
                state["c_confirmed"] = True
                fraction = 1.0
                out.append(StrategyStep("5S_TOPUP_TO_100", "B40", fraction, ("BUY_C",), dict(state)))
            elif action == "SELL_ALL":
                fraction = 0.0
                state = {}
                out.append(StrategyStep("5S_SELL_ALL", "S100", fraction, (str(decision.signal),), {}))
            else:
                raise RuntimeError(f"unknown legacy action: {action}")
        return tuple(out)

    def execute(self, symbol: str, decision, config: dict[str, Any], runtime: dict[str, Any], adapter, context: dict[str, Any]) -> ExecutionOutcome:
        with self._lock:
            fresh_config = self.store.get_symbol_configs().get(symbol)
            if not fresh_config or not bool(fresh_config["enabled"]):
                raise ExecutionBlocked("该币种已经停止，取消本次自动交易")

            strategy_id = str(getattr(decision, "strategy_id", None) or STRATEGY_5S)
            if str(fresh_config.get("strategy_id") or STRATEGY_5S) != strategy_id:
                raise ExecutionBlocked("策略已经切换，取消旧策略的待执行动作")

            signal_bar = int(getattr(decision, "bar_open_time", None) or context["signal_bar_open_time"])
            execution_bar = int(context["execution_bar_open_time"])
            reference_price = Decimal(str(context["reference_price"]))
            leverage = int(fresh_config["leverage"])
            budget = Decimal(str(fresh_config["capital_budget_usdt"]))
            steps = tuple(getattr(decision, "steps", ()) or self._legacy_steps(decision, runtime))
            order_ids: list[str] = []

            for step in steps:
                fresh_runtime = self.store.get_runtime_states()[symbol]
                current_fraction = min(max(float(fresh_runtime.get("current_fraction") or 0.0), 0.0), 1.0)
                target_fraction = min(max(float(step.target_fraction), 0.0), 1.0)
                delta = target_fraction - current_fraction
                client_id = self._strategy_client_order_id(
                    strategy_id, symbol, signal_bar, str(step.order_code)
                )

                recovered = self._recover_existing(adapter, symbol, client_id)
                if recovered is not None:
                    order_id = str(_first(recovered, "orderId", "order_id", "binance_order_id", default=client_id))
                    if target_fraction > current_fraction:
                        self.store.set_accounting_start_if_missing(symbol, execution_bar)
                    self.store.set_strategy_execution_state(
                        symbol,
                        current_fraction=target_fraction,
                        strategy_state=dict(step.state_after),
                        last_order_id=order_id,
                    )
                    order_ids.append(order_id)
                    continue

                if abs(delta) <= 1e-12:
                    self.store.set_strategy_execution_state(
                        symbol,
                        current_fraction=target_fraction,
                        strategy_state=dict(step.state_after),
                        last_order_id=fresh_runtime.get("last_order_id"),
                    )
                    continue

                position_amount = Decimal(str(adapter.position_amount(symbol)))
                if position_amount < 0:
                    raise ExecutionBlocked("检测到空头持仓；当前框架只允许做多，已阻止自动交易")

                if delta > 0:
                    if current_fraction <= 1e-12 and position_amount != 0:
                        raise ExecutionBlocked("策略记录为空仓，但币安已有持仓；等待恢复对账，不自动加仓")
                    if current_fraction > 1e-12 and position_amount <= 0:
                        raise ExecutionBlocked("策略准备加仓，但币安没有对应多头持仓；已阻止自动交易")
                    self._validate_buy_environment(adapter, symbol, leverage)
                    margin = budget * Decimal(str(delta))
                    quantity = self._buy_quantity(
                        adapter=adapter,
                        symbol=symbol,
                        margin_usdt=margin,
                        leverage=leverage,
                        reference_price=reference_price,
                    )
                    side = "BUY"
                else:
                    if current_fraction <= 1e-12:
                        raise ExecutionBlocked("策略准备减仓，但本地策略仓位已经为空")
                    if position_amount <= 0:
                        if target_fraction <= 1e-12:
                            self.store.set_strategy_execution_state(
                                symbol,
                                current_fraction=0.0,
                                strategy_state=dict(step.state_after),
                                last_order_id=fresh_runtime.get("last_order_id"),
                            )
                            continue
                        raise ExecutionBlocked("策略准备减仓，但币安没有对应多头持仓；已阻止自动交易")
                    rules = adapter.symbol_rules(symbol)
                    if rules.step_size is None:
                        raise ExecutionBlocked("交易所没有返回有效的平仓数量规则")
                    if target_fraction <= 1e-12:
                        raw_quantity = abs(position_amount)
                    else:
                        current_d = Decimal(str(current_fraction))
                        target_d = Decimal(str(target_fraction))
                        ratio = (current_d - target_d) / current_d
                        raw_quantity = abs(position_amount) * ratio
                    quantity = floor_to_step(raw_quantity, rules.step_size)
                    if quantity <= 0:
                        raise ExecutionBlocked("当前减仓数量小于交易所最小可执行数量")
                    side = "SELL"

                order = self._submit_market(
                    adapter=adapter,
                    symbol=symbol,
                    client_id=client_id,
                    side=side,
                    quantity=quantity,
                    reference_price=reference_price,
                    strategy_id=strategy_id,
                    target_fraction_after=target_fraction,
                    strategy_state_after=dict(step.state_after),
                )
                order_id = str(_first(order, "orderId", "order_id", default=client_id))
                if delta > 0:
                    self.store.set_accounting_start_if_missing(symbol, execution_bar)
                self.store.set_strategy_execution_state(
                    symbol,
                    current_fraction=target_fraction,
                    strategy_state=dict(step.state_after),
                    last_order_id=order_id,
                )
                order_ids.append(order_id)

            self.refresh_accounting(symbol, adapter, force=True)
            action_codes = tuple(step.code for step in steps)
            self.store.append_audit(
                "M3_EXECUTION_PASS",
                symbol,
                f"strategy={strategy_id};signal={decision.signal};actions={'+'.join(action_codes)};orders={','.join(order_ids) or 'NONE'}",
            )
            return ExecutionOutcome(symbol=symbol, actions=action_codes, order_ids=tuple(order_ids))

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
            symbol,
            realized_pnl=realized,
            unrealized_pnl=unrealized,
            funding_fee=funding,
            trading_fee=-commission_income,
        )
        self._last_pnl_refresh[symbol] = now
