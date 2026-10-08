from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from decimal import Decimal
import json
from threading import RLock
import time
from typing import Any

from exchange.binance_usdm_testnet import floor_to_step
from strategy.registry import STRATEGY_5S, get_spec, strategy_ids


TERMINAL_ORDER_STATES = {"FILLED", "CANCELED", "EXPIRED", "REJECTED", "NOT_FOUND"}
ACTIVE_ORDER_STATES = {"NEW", "PARTIALLY_FILLED", "PENDING"}
STRATEGY_PREFIXES = tuple(f"{get_spec(sid).order_prefix}-" for sid in strategy_ids())


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


def _is_framework_client_id(client_id: str) -> bool:
    return str(client_id).startswith(STRATEGY_PREFIXES)


def _legacy_5s_action(client_id: str) -> str | None:
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


def _json_dict(value: object) -> dict[str, Any]:
    if isinstance(value, dict):
        return dict(value)
    try:
        parsed = json.loads(str(value or "{}"))
        return dict(parsed) if isinstance(parsed, dict) else {}
    except Exception:
        return {}


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
    """Reconcile one Binance net position with the selected strategy owner."""

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
            if not _is_framework_client_id(client_id):
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
            if _is_framework_client_id(cid):
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

    def _derive_position_state(
        self,
        symbol: str,
        strategy_id: str,
    ) -> tuple[float, dict[str, Any], str | None]:
        runtime = self.store.get_runtime_states()[symbol]
        fraction = float(runtime.get("current_fraction") or 0.0)
        strategy_state = _json_dict(runtime.get("strategy_state"))
        last_order_id: str | None = None

        selected_rows = [
            row for row in self.store.list_orders(symbol)
            if str(row.get("status") or "").upper() == "FILLED"
            and str(row.get("strategy_id") or STRATEGY_5S) == strategy_id
        ]

        for row in selected_rows:
            cid = str(row.get("client_order_id") or "")
            last_order_id = str(row.get("binance_order_id") or cid)
            target = row.get("target_fraction_after")
            if target is not None:
                fraction = float(target)
                strategy_state = _json_dict(row.get("strategy_state_after_json"))
                continue

            # Backward compatibility with frozen 5s V1 ledgers created before
            # multi-strategy metadata existed.
            if strategy_id != STRATEGY_5S:
                continue
            action = _legacy_5s_action(cid)
            if action == "BUY_60":
                fraction = 0.60
                strategy_state = {
                    "c_confirmed": False,
                    "entry_signal_open_time": _signal_bar_from_client_id(cid),
                    "entry_family": runtime.get("entry_family") or "UNKNOWN",
                }
            elif action == "TOPUP_TO_100":
                fraction = 1.0
                strategy_state["c_confirmed"] = True
            elif action in {"SELL_ALL", "EMERGENCY_FLAT"}:
                fraction = 0.0
                strategy_state = {}

        return fraction, strategy_state, last_order_id

    def reconcile_symbol(self, adapter, symbol: str) -> SymbolRecovery:
        with self._lock:
            cfg = self.store.get_symbol_configs()[symbol]
            strategy_id = str(cfg.get("strategy_id") or STRATEGY_5S)
            recovered = self._recover_local_orders(adapter, symbol)
            canceled, external = self._cancel_strategy_open_orders(adapter, symbol)
            if external:
                reason = "检测到非本交易框架挂单；为避免误操作已阻止自动交易"
                self.store.set_run_state(symbol, "RECOVERY_BLOCKED")
                self.store.append_audit("M4_RECONCILE_BLOCKED", symbol, reason)
                return SymbolRecovery(symbol, "BLOCKED", 0.0, 0.0, 0.0, canceled, recovered, None, reason)

            remote = Decimal(str(adapter.position_amount(symbol)))
            if remote < 0:
                reason = "检测到空头仓位；当前框架只允许做多"
                self.store.set_run_state(symbol, "RECOVERY_BLOCKED")
                self.store.append_audit("M4_RECONCILE_BLOCKED", symbol, reason)
                return SymbolRecovery(symbol, "BLOCKED", float(remote), 0.0, 0.0, canceled, recovered, None, reason)

            raw_ledger = self._ledger_position(symbol)
            baseline = self.store.get_reconciliation_baseline(symbol, strategy_id)
            ledger = raw_ledger - baseline
            rules = adapter.symbol_rules(symbol)
            tolerance = (rules.step_size or Decimal("0.00000001")) / Decimal("2")
            if abs(remote - ledger) > tolerance:
                if remote <= tolerance and baseline == 0:
                    created = self.store.set_reconciliation_baseline(
                        symbol,
                        strategy_id,
                        raw_ledger,
                        reason="REMOTE_ZERO_TERMINAL_LEDGER",
                    )
                    if created:
                        baseline = raw_ledger
                        ledger = Decimal("0")
                        self.store.append_audit(
                            "M4_AUTO_BASELINE",
                            symbol,
                            f"strategy={strategy_id};raw_ledger={raw_ledger};remote={remote};baseline={baseline}",
                        )

                if abs(remote - ledger) > tolerance:
                    reason = f"本地订单账本仓位 {ledger} 与币安模拟仓位 {remote} 不一致"
                    self.store.set_run_state(symbol, "RECOVERY_BLOCKED")
                    self.store.append_audit("M4_RECONCILE_BLOCKED", symbol, reason)
                    return SymbolRecovery(symbol, "BLOCKED", float(remote), float(ledger), 0.0, canceled, recovered, None, reason)

            fraction, strategy_state, last_order_id = self._derive_position_state(symbol, strategy_id)
            if remote > tolerance and fraction <= 0:
                reason = "币安存在多头仓位，但当前策略没有可验证的开仓记录"
                self.store.set_run_state(symbol, "RECOVERY_BLOCKED")
                self.store.append_audit("M4_RECONCILE_BLOCKED", symbol, reason)
                return SymbolRecovery(symbol, "BLOCKED", float(remote), float(ledger), fraction, canceled, recovered, None, reason)
            if remote <= tolerance:
                fraction, strategy_state = 0.0, {}

            bars = adapter.klines(symbol, str(cfg["timeframe"]), limit=2)
            baseline: int | None = None
            if isinstance(bars, list) and len(bars) >= 2:
                baseline = int(bars[-2][0])

            run_state = "MONITORING" if bool(cfg["enabled"]) else "STOPPED"
            self.store.set_recovery_strategy_state(
                symbol,
                current_fraction=fraction,
                strategy_state=strategy_state,
                last_order_id=last_order_id,
                last_closed_bar_open_time=baseline,
                run_state=run_state,
            )
            self.store.append_audit(
                "M4_RECONCILE_PASS",
                symbol,
                f"strategy={strategy_id};remote={remote};ledger={ledger};fraction={fraction};baseline={baseline};canceled={canceled};recovered={recovered}",
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
                raise RecoveryBlocked("存在非本交易框架挂单，不会自动取消")
            self.store.append_audit("M4_CANCEL_STRATEGY_ORDERS", symbol, f"count={canceled}")
            return canceled

    def emergency_flatten(self, adapter, symbol: str) -> dict[str, Any]:
        with self._lock:
            self.store.set_symbol_enabled(symbol, False)
            cfg = self.store.get_symbol_configs()[symbol]
            strategy_id = str(cfg.get("strategy_id") or STRATEGY_5S)
            amount = Decimal(str(adapter.position_amount(symbol)))
            if amount < 0:
                raise RecoveryBlocked("检测到空头仓位，当前程序不会自动处理")
            if amount == 0:
                self.store.set_recovery_strategy_state(
                    symbol,
                    current_fraction=0.0,
                    strategy_state={},
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
            prefix = get_spec(strategy_id).order_prefix
            client_id = f"{prefix}-{base}-{int(time.time() * 1000)}-EMG"
            bars = adapter.klines(symbol, str(cfg["timeframe"]), limit=2)
            execution_bar = int(bars[-1][0]) if isinstance(bars, list) and bars else int(time.time() * 1000)
            self.store.begin_order(
                symbol,
                client_id,
                side="SELL",
                quantity=float(quantity),
                price=0.0,
                strategy_id=strategy_id,
                target_fraction_after=0.0,
                strategy_state_after={},
                signal_bar_open_time=execution_bar,
                execution_bar_open_time=execution_bar,
                marker_side="X",
                strategy_signal="EMERGENCY_FLAT",
            )
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

            self.store.set_recovery_strategy_state(
                symbol,
                current_fraction=0.0,
                strategy_state={},
                last_order_id=str(_first(order, "orderId", "order_id", default=client_id)),
                last_closed_bar_open_time=None,
                run_state="STOPPED",
            )
            self.store.append_audit(
                "M4_EMERGENCY_FLAT",
                symbol,
                f"strategy={strategy_id};qty={quantity};client_id={client_id}",
            )
            return {"status": "FILLED", "order_id": _first(order, "orderId", "order_id")}
