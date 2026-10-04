from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
import time
from typing import Any

from binance_demo_exchange import floor_to_step
from binance_demo_live_strategies import LivePlan


class DemoExecutionBlocked(RuntimeError):
    pass


@dataclass(frozen=True)
class DemoExecutionResult:
    symbol: str
    strategy_id: str
    actions: tuple[str, ...]
    order_ids: tuple[str, ...]
    fraction_after: float


def _first(mapping: dict[str, Any], *keys: str, default=None):
    for k in keys:
        if k in mapping:
            return mapping[k]
    return default


def _f(value, default=0.0):
    try: return float(value)
    except Exception: return float(default)


class DemoExecutor:
    BUY_MARGIN = {
        "SLTD_BUY25": Decimal("0.25"),
        "E_BUY25": Decimal("0.25"),
        "E_BUY50": Decimal("0.50"),
        "5S_BUY60": Decimal("0.60"),
        "5S_TOPUP40": Decimal("0.40"),
    }

    def __init__(self, store):
        self.store=store

    @staticmethod
    def _code(action: str) -> str:
        codes={
            "SLTD_BUY25":"SB25","SLTD_SELL25_CURRENT":"SS25","SLTD_C2_EXIT":"SC2",
            "E_BUY25":"EB25","E_BUY50":"EB50","E_SELL50PP":"ES50","E_SELL25PP":"ES25","E_EXIT":"EX",
            "5S_BUY60":"5B60","5S_TOPUP40":"5B40","5S_HALF_EXIT":"5H","5S_FULL_EXIT":"5X",
        }
        return codes[action]

    @classmethod
    def client_id(cls, symbol: str, signal_open_time: int, action: str, index: int) -> str:
        base=symbol[:-4] if symbol.endswith("USDT") else symbol
        # Binance open_time is ms; seconds keep IDs compact and deterministic.
        sec=int(signal_open_time)//1000
        value=f"sv7-{base}-{sec}-{cls._code(action)}-{index}"
        if len(value)>36:
            raise RuntimeError("clientOrderId too long")
        return value

    @staticmethod
    def _status(order: dict) -> str:
        return str(_first(order,"status",default="")).upper()

    @staticmethod
    def _not_found(exc: Exception) -> bool:
        t=str(exc).lower()
        return "-2013" in t or "order does not exist" in t or "order not found" in t

    def _recover(self, adapter, symbol: str, client_id: str):
        local=self.store.order(symbol,client_id)
        if not local:
            return None
        if str(local.get("status") or "").upper()=="FILLED":
            return local
        try:
            remote=adapter.query_order(symbol,client_order_id=client_id)
        except Exception as exc:
            if self._not_found(exc):
                return None
            raise
        if not isinstance(remote,dict):
            raise RuntimeError("订单查询返回格式异常")
        status=self._status(remote) or "UNKNOWN"
        self.store.finish_order(
            symbol,client_id,
            order_id=str(_first(remote,"orderId","order_id",default="") or ""),
            status=status,
            qty=_f(_first(remote,"executedQty","executed_qty","origQty","orig_qty",default=0)),
            price=_f(_first(remote,"avgPrice","avg_price","price",default=0)),
        )
        if status!="FILLED":
            raise DemoExecutionBlocked(f"已有订单状态不是 FILLED：{status}")
        return remote

    def _submit(self, adapter, *, symbol: str, strategy_id: str, client_id: str,
                side: str, qty: Decimal, ref_price: Decimal):
        existing=self._recover(adapter,symbol,client_id)
        if existing is not None:
            return existing
        self.store.begin_order(symbol,client_id,strategy_id,side,float(qty),float(ref_price))
        order=(
            adapter.submit_market_buy(symbol,quantity=qty,client_order_id=client_id)
            if side=="BUY"
            else adapter.submit_market_sell_reduce_only(symbol,quantity=qty,client_order_id=client_id)
        )
        if not isinstance(order,dict):
            raise RuntimeError("币安订单返回格式异常")
        status=self._status(order) or "UNKNOWN"
        self.store.finish_order(
            symbol,client_id,
            order_id=str(_first(order,"orderId","order_id",default="") or ""),
            status=status,
            qty=_f(_first(order,"executedQty","executed_qty","origQty","orig_qty",default=float(qty))),
            price=_f(_first(order,"avgPrice","avg_price","price",default=float(ref_price))),
        )
        if status!="FILLED":
            raise DemoExecutionBlocked(f"市价单未完成：{status}")
        return order

    @staticmethod
    def _sell_ratio(action: str, fraction: float) -> float:
        if action=="SLTD_SELL25_CURRENT": return 0.25
        if action=="5S_HALF_EXIT": return 0.50
        if action=="E_SELL50PP": return min(1.0,0.50/max(fraction,1e-12))
        if action=="E_SELL25PP": return min(1.0,0.25/max(fraction,1e-12))
        if action in {"SLTD_C2_EXIT","E_EXIT","5S_FULL_EXIT"}: return 1.0
        raise ValueError(action)

    @staticmethod
    def _next_fraction(action: str, fraction: float) -> float:
        if action=="SLTD_BUY25": return min(1.0,fraction+0.25)
        if action=="SLTD_SELL25_CURRENT": return max(0.0,fraction*0.75)
        if action=="SLTD_C2_EXIT": return 0.0
        if action=="E_BUY25": return min(0.75,fraction+0.25)
        if action=="E_BUY50": return min(0.75,fraction+0.50)
        if action=="E_SELL50PP": return max(0.0,fraction-0.50)
        if action=="E_SELL25PP": return max(0.0,fraction-0.25)
        if action=="E_EXIT": return 0.0
        if action=="5S_BUY60": return 0.60
        if action=="5S_TOPUP40": return min(1.0,fraction+0.40)
        if action=="5S_HALF_EXIT": return max(0.0,fraction*0.50)
        if action=="5S_FULL_EXIT": return 0.0
        raise ValueError(action)

    def _validate_buy(self, adapter, symbol: str, leverage: int):
        adapter.ensure_one_way()
        adapter.ensure_isolated(symbol)
        maximum=int(adapter.max_allowed_leverage(symbol))
        if leverage>maximum:
            raise DemoExecutionBlocked(f"{symbol} 杠杆上限 {maximum}x，当前请求 {leverage}x")
        adapter.set_leverage(symbol,leverage)

    def _buy_qty(self, adapter, symbol: str, margin: Decimal, leverage: int, ref: Decimal) -> Decimal:
        if ref<=0: raise DemoExecutionBlocked("参考价格无效")
        available=Decimal(str(adapter.available_usdt()))
        if available<margin:
            raise DemoExecutionBlocked(f"USDT 可用保证金不足：需要 {margin}，可用 {available}")
        rules=adapter.symbol_rules(symbol)
        if rules.step_size is None or rules.min_qty is None:
            raise DemoExecutionBlocked("交易所下单数量规则缺失")
        qty=floor_to_step(margin*Decimal(leverage)/ref,rules.step_size)
        if qty<=0 or qty<rules.min_qty:
            raise DemoExecutionBlocked("预算不足以达到最小下单数量")
        if rules.max_qty is not None and qty>rules.max_qty:
            raise DemoExecutionBlocked("下单数量超过交易所上限")
        if rules.min_notional is not None and qty*ref<rules.min_notional:
            raise DemoExecutionBlocked("预算不足以达到最小名义价值")
        return qty

    def execute(self, symbol: str, plan: LivePlan, config: dict, runtime: dict,
                adapter, reference_price: float) -> DemoExecutionResult:
        if not bool(config.get("enabled")):
            raise DemoExecutionBlocked("当前币种未启用自动执行")
        if str(config["strategy_id"])!=plan.strategy_id:
            raise DemoExecutionBlocked("实时策略与配置策略不一致")

        fraction=float(runtime.get("current_fraction") or 0.0)
        state=dict(runtime.get("state") or {})
        leverage=int(config["leverage"])
        budget=Decimal(str(config["capital_budget_usdt"]))
        ref=Decimal(str(reference_price))
        order_ids=[]

        for idx,item in enumerate(plan.actions):
            action=item.code
            cid=self.client_id(symbol,plan.signal_open_time,action,idx)
            if action in self.BUY_MARGIN:
                self._validate_buy(adapter,symbol,leverage)
                qty=self._buy_qty(adapter,symbol,budget*self.BUY_MARGIN[action],leverage,ref)
                order=self._submit(
                    adapter,symbol=symbol,strategy_id=plan.strategy_id,client_id=cid,
                    side="BUY",qty=qty,ref_price=ref,
                )
            else:
                pos=Decimal(str(adapter.position_amount(symbol)))
                if pos<0:
                    raise DemoExecutionBlocked("检测到空头仓位；本版本只允许做多")
                ratio=Decimal(str(self._sell_ratio(action,fraction)))
                rules=adapter.symbol_rules(symbol)
                if rules.step_size is None:
                    raise DemoExecutionBlocked("交易所减仓数量规则缺失")
                qty=floor_to_step(abs(pos)*ratio,rules.step_size)
                if qty<=0:
                    # If already flat, full exits are idempotent; partial exits are blocked.
                    if action in {"SLTD_C2_EXIT","E_EXIT","5S_FULL_EXIT"} and pos==0:
                        fraction=0.0
                        continue
                    raise DemoExecutionBlocked("当前持仓小于最小可减数量")
                order=self._submit(
                    adapter,symbol=symbol,strategy_id=plan.strategy_id,client_id=cid,
                    side="SELL",qty=qty,ref_price=ref,
                )

            oid=str(_first(order,"orderId","order_id","binance_order_id",default=cid))
            order_ids.append(oid)
            fraction=self._next_fraction(action,fraction)

        # Strategy state changes only after all required orders for this signal are filled.
        state=dict(plan.next_state)
        if fraction<=1e-12:
            fraction=0.0
            if plan.strategy_id in {"e","5s_stocks"}:
                state={}
            if plan.strategy_id=="v7":
                state["risk_armed"]=False

        current=self.store.runtimes()[symbol]
        accounting=current.get("accounting_start_time_ms")
        if plan.actions and accounting is None:
            accounting=int(time.time()*1000)
        self.store.set_runtime(
            symbol,fraction=fraction,state=state,
            last_order_id=order_ids[-1] if order_ids else current.get("last_order_id"),
            accounting_start_time_ms=accounting,
        )
        self.store.audit(
            "DEMO_EXECUTION_PASS",symbol,
            f"strategy={plan.strategy_id};signal={plan.signal_date};actions={'+'.join(a.code for a in plan.actions) or 'NONE'};"
            f"fraction={fraction:.6f};orders={','.join(order_ids) or 'NONE'}"
        )
        return DemoExecutionResult(
            symbol=symbol,strategy_id=plan.strategy_id,
            actions=tuple(a.code for a in plan.actions),
            order_ids=tuple(order_ids),fraction_after=fraction,
        )
