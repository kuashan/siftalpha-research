from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from decimal import Decimal
from threading import RLock
import time
from typing import Any

from exchange.binance_usdm_testnet import floor_to_step


TERMINAL_ORDER_STATES = {"FILLED", "CANCELED", "EXPIRED", "REJECTED", "NOT_FOUND"}
ACTIVE_ORDER_STATES = {"NEW", "PARTIALLY_FILLED", "PENDING"}
STRATEGY_PREFIX = "5sv1-"


class RecoveryBlocked(RuntimeError):
    pass


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


def _client_id(order: dict[str, Any]) -> str:
    return str(_first(order, "clientOrderId", "client_order_id", default="") or "")


def _status(order: dict[str, Any]) -> str:
    return str(_first(order, "status", default="") or "").upper()


def _order_action(client_id: str) -> str | None:
    if client_id.endswith("-B60"):
        return "BUY_60"
    if client_id.endswith("-B40"):
        return "TOPUP_TO_100"
    if client_id.endswith("-S100"):
        return "SELL_ALL"
    if client_id.endswith("-EMG"):
        return "EMERGENCY_FLAT"
    return None


def _signal_bar_from_client_id(client_id: str) -> int | None:
    parts = client_id.split("-")
    if len(parts) < 4:
        return None
    try:
        return int(parts[-2])
    except (TypeError, ValueError):
        return None


@dataclass(frozen=True)
class SymbolRecovery:
    symbol: str
    status: str
    remote_position: float
    ledger_position: float
    local_fraction: float
    canceled_strategy_orders: int
    recovered_local_orders: int
    baseline_bar_open_time: int | None
    reason: str | None = None


class M4Recovery:
    """Restart/reconciliation boundary for M3 automatic Demo execution.

    Binance Demo position + local filled-order ledger must agree before the
    scheduler is allowed to resume. Unknown external state is never guessed.
    """

    def __init__(self, store, *, execution_lock: RLock | None = None):
        self.store = store
        self._lock = execution_lock or RLock()

    @staticmethod
    def _is_not_found(exc: Exception) -> bool:
        text = str(exc).lower()
        return "-2013" in text or "order does not exist" in text or "order not found" in text

    def _recover_local_orders(self, adapter, symbol: str) -> int:
        recovered = 0
        for row in self.store.list_orders(symbol):
            state = str(row.get("status") or "").upper()
            if state in TERMINAL_ORDER_STATES:
                continue
            client_id = str(row.get("client_order_id") or "")
            if not client_id.startswith(STRATEGY_PREFIX):
                continue
            try:
                remote = adapter.query_order(symbol, client_order_id=client_id)
            except Exception as exc:
                if self._is_not_found(exc):
                    self.store.mark_order_status(symbol, client_id, "NOT_FOUND")
                    recovered += 1
                    continue
                raise
            if not isinstance(remote, dict):
                raise RecoveryBlocked("订单恢复返回格式异常")
            remote_status = _status(remote) or "UNKNOWN"
            self.store.complete_order(
                symbol,
                client_id,
                binance_order_id=str(_first(remote, "orderId", "order_id", default="") or ""),
                status=remote_status,
                quantity=_float(_first(remote, "executedQty", "executed_qty", "origQty", "orig_qty", default=row.get("quantity", 0))),
                price=_float(_first(remote, "avgPrice", "avg_price", "price", default=row.get("price", 0))),
            )
            recovered += 1
        return recovered

    def _cancel_strategy_open_orders(self, adapter, symbol: str) -> tuple[int, list[str]]:
        rows = adapter.open_orders(symbol)
        open_rows = rows if isinstance(rows, list) else ([rows] if rows else [])
        canceled = 0
        external: list[str] = []
        for row in open_rows:
            if not isinstance(row, dict):
                continue
            cid = _client_id(row)
            if cid.startswith(STRATEGY_PREFIX):
                order_id = _first(row, "orderId", "order_id")
                adapter.cancel_order(
                    symbol,
                    order_id=int(order_id) if order_id not in (None, "") else None,
                    client_order_id=None if order_id not in (None, "") else cid,
                )
                if self.store.get_order(symbol, cid):
                    self.store.mark_order_status(symbol, cid, "CANCELED")
                canceled += 1
            else:
                external.append(cid or "UNKNOWN")
        return canceled, external

    def _ledger_position(self, symbol: str) -> Decimal:
        net = Decimal("0")
        for row in self.store.list_orders(symbol):
            if str(row.get("status") or "").upper() != "FILLED":
                continue
            qty = Decimal(str(row.get("quantity") or 0))
            side = str(row.get("side") or "").upper()
            if side == "BUY":
                net += qty
            elif side == "SELL":
                net -= qty
        return net

    def _derive_position_state(self, symbol: str) -> tuple[float, bool, int | None, str | None, str | None]:
        fraction = 0.0
        confirmed = False
        entry_signal: int | None = None
        entry_family: str | None = None
        last_order_id: str | None = None
        runtime = self.store.get_runtime_states()[symbol]
        preserved_family = runtime.get("entry_family")

        for row in self.store.list_orders(symbol):
            if str(row.get("status") or "").upper() != "FILLED":
                continue
            cid = str(row.get("client_order_id") or "")
            action = _order_action(cid)
            if not action:
                continue
            last_order_id = str(row.get("binance_order_id") or cid)
            if action == "BUY_60":
                fraction = 0.60
                confirmed = False
                entry_signal = _signal_bar_from_client_id(cid)
                entry_family = str(preserved_family or "UNKNOWN")
            elif action == "TOPUP_TO_100":
                fraction = 1.0
                confirmed = True
            elif action in {"SELL_ALL", "EMERGENCY_FLAT"}:
                fraction = 0.0
                confirmed = False
                entry_signal = None
                entry_family = None
        return fraction, confirmed, entry_signal, entry_family, last_order_id

    def reconcile_symbol(self, adapter, symbol: str) -> SymbolRecovery:
        with self._lock:
            cfg = self.store.get_symbol_configs()[symbol]
            recovered = self._recover_local_orders(adapter, symbol)
            canceled, external = self._cancel_strategy_open_orders(adapter, symbol)
            if external:
                reason = "检测到非本策略未成交订单：" + ",".join(external[:3])
                self.store.set_run_state(symbol, "RECOVERY_BLOCKED")
                self.store.append_audit("M4_RECONCILE_BLOCKED", symbol, reason)
                return SymbolRecovery(symbol, "BLOCKED", 0.0, 0.0, 0.0, canceled, recovered, None, reason)

            remote = Decimal(str(adapter.position_amount(symbol)))
            if remote < 0:
                reason = "检测到空头仓位；当前策略只允许做多"
                self.store.set_run_state(symbol, "RECOVERY_BLOCKED")
                self.store.append_audit("M4_RECONCILE_BLOCKED", symbol, reason)
                return SymbolRecovery(symbol, "BLOCKED", float(remote), 0.0, 0.0, canceled, recovered, None, reason)

            ledger = self._ledger_position(symbol)
            rules = adapter.symbol_rules(symbol)
            tolerance = (rules.step_size or Decimal("0.00000001")) / Decimal("2")
            if abs(remote - ledger) > tolerance:
                reason = f"本地订单账本仓位 {ledger} 与币安模拟仓位 {remote} 不一致"
                self.store.set_run_state(symbol, "RECOVERY_BLOCKED")
                self.store.append_audit("M4_RECONCILE_BLOCKED", symbol, reason)
                return SymbolRecovery(symbol, "BLOCKED", float(remote), float(ledger), 0.0, canceled, recovered, None, reason)

            fraction, confirmed, entry_signal, entry_family, last_order_id = self._derive_position_state(symbol)
            if remote > tolerance and fraction <= 0:
                reason = "币安存在多头仓位，但本地没有可验证的策略开仓记录"
                self.store.set_run_state(symbol, "RECOVERY_BLOCKED")
                self.store.append_audit("M4_RECONCILE_BLOCKED", symbol, reason)
                return SymbolRecovery(symbol, "BLOCKED", float(remote), float(ledger), fraction, canceled, recovered, None, reason)
            if remote <= tolerance:
                fraction, confirmed, entry_signal, entry_family = 0.0, False, None, None

            bars = adapter.klines(symbol, str(cfg["timeframe"]), limit=2)
            baseline: int | None = None
            if isinstance(bars, list) and len(bars) >= 2:
                baseline = int(bars[-2][0])

            run_state = "MONITORING" if bool(cfg["enabled"]) else "STOPPED"
            self.store.set_recovery_runtime(
                symbol,
                current_fraction=fraction,
                c_confirmed=confirmed,
                entry_signal_open_time=entry_signal,
                entry_family=entry_family,
                last_order_id=last_order_id,
                last_closed_bar_open_time=baseline,
                run_state=run_state,
            )
            self.store.append_audit(
                "M4_RECONCILE_PASS",
                symbol,
                f"remote={remote};ledger={ledger};fraction={fraction};baseline={baseline};canceled={canceled};recovered={recovered}",
            )
            return SymbolRecovery(
                symbol=symbol,
                status="PASS",
                remote_position=float(remote),
                ledger_position=float(ledger),
                local_fraction=fraction,
                canceled_strategy_orders=canceled,
                recovered_local_orders=recovered,
                baseline_bar_open_time=baseline,
            )

    def reconcile_all(self, adapter, symbols: tuple[str, ...]) -> dict[str, Any]:
        results: dict[str, Any] = {}
        all_pass = True
        for symbol in symbols:
            try:
                item = self.reconcile_symbol(adapter, symbol)
            except Exception as exc:
                all_pass = False
                self.store.set_run_state(symbol, "RECOVERY_BLOCKED")
                self.store.append_audit("M4_RECONCILE_ERROR", symbol, f"{type(exc).__name__}:{exc}")
                item = SymbolRecovery(symbol, "BLOCKED", 0.0, 0.0, 0.0, 0, 0, None, str(exc))
            if item.status != "PASS":
                all_pass = False
            results[symbol] = asdict(item)
        summary = {
            "status": "PASS" if all_pass else "BLOCKED",
            "checked_at": datetime.now(timezone.utc).isoformat(),
            "symbols": results,
        }
        self.store.append_audit("M4_RECONCILE_ALL", None, f"status={summary['status']}")
        return summary

    def cancel_strategy_orders(self, adapter, symbol: str) -> int:
        with self._lock:
            canceled, external = self._cancel_strategy_open_orders(adapter, symbol)
            if external:
                raise RecoveryBlocked("存在非本策略挂单，不会自动取消")
            self.store.append_audit("M4_CANCEL_STRATEGY_ORDERS", symbol, f"count={canceled}")
            return canceled

    def emergency_flatten(self, adapter, symbol: str) -> dict[str, Any]:
        with self._lock:
            self.store.set_symbol_enabled(symbol, False)
            amount = Decimal(str(adapter.position_amount(symbol)))
            if amount < 0:
                raise RecoveryBlocked("检测到空头仓位，当前程序不会自动处理")
            if amount == 0:
                self.store.set_recovery_runtime(
                    symbol,
                    current_fraction=0.0,
                    c_confirmed=False,
                    entry_signal_open_time=None,
                    entry_family=None,
                    last_order_id=None,
                    last_closed_bar_open_time=None,
                    run_state="STOPPED",
                )
                return {"status": "ALREADY_FLAT", "order_id": None}

            rules = adapter.symbol_rules(symbol)
            if rules.step_size is None:
                raise RecoveryBlocked("交易所没有返回有效的平仓数量规则")
            quantity = floor_to_step(amount, rules.step_size)
            if quantity <= 0:
                raise RecoveryBlocked("当前仓位小于交易所可平最小数量")

            base = symbol[:-4] if symbol.endswith("USDT") else symbol
            client_id = f"5sv1-{base}-{int(time.time() * 1000)}-EMG"
            self.store.begin_order(symbol, client_id, side="SELL", quantity=float(quantity), price=0.0)
            order = adapter.submit_market_sell_reduce_only(
                symbol, quantity=quantity, client_order_id=client_id
            )
            if not isinstance(order, dict):
                raise RecoveryBlocked("紧急平仓订单返回格式异常")
            status = _status(order)
            self.store.complete_order(
                symbol,
                client_id,
                binance_order_id=str(_first(order, "orderId", "order_id", default="") or ""),
                status=status or "UNKNOWN",
                quantity=_float(_first(order, "executedQty", "executed_qty", default=quantity)),
                price=_float(_first(order, "avgPrice", "avg_price", default=0)),
            )
            if status != "FILLED":
                raise RecoveryBlocked(f"紧急平仓未完成：{status}")

            self.store.set_recovery_runtime(
                symbol,
                current_fraction=0.0,
                c_confirmed=False,
                entry_signal_open_time=None,
                entry_family=None,
                last_order_id=str(_first(order, "orderId", "order_id", default=client_id)),
                last_closed_bar_open_time=None,
                run_state="STOPPED",
            )
            self.store.append_audit("M4_EMERGENCY_FLAT", symbol, f"qty={quantity};client_id={client_id}")
            return {"status": "FILLED", "order_id": _first(order, "orderId", "order_id")}
