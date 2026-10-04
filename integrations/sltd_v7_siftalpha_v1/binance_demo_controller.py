from __future__ import annotations

import os
import threading
import time
from pathlib import Path
from typing import Any

from binance_demo_executor import DemoExecutionBlocked, DemoExecutor
from binance_demo_live_strategies import make_plan
from binance_demo_session import TestnetSession
from binance_demo_store import DEFAULT_SYMBOLS, EXECUTABLE_STRATEGIES, DemoStore
from data_provider import TIMEFRAMES, fetch_bars


def _first(mapping: dict[str, Any], *keys: str, default=None):
    for k in keys:
        if k in mapping:
            return mapping[k]
    return default


class BinanceDemoController:
    def __init__(self):
        root=Path(__file__).resolve().parent
        db=Path(os.environ.get("SLTD_BINANCE_DEMO_DB", str(root/"data"/"sltd_v7_binance_demo.db")))
        self.store=DemoStore(db)
        # Never auto-resume mutations after a Python process restart.
        for symbol in DEFAULT_SYMBOLS:
            self.store.set_enabled(symbol,False)
            self.store.set_runtime(symbol,run_state="STOPPED")

        self.session=TestnetSession(
            allowed_symbols=DEFAULT_SYMBOLS,
            allowed_timeframes=tuple(TIMEFRAMES.keys()),
            initial_api_key=os.environ.get("BINANCE_DEMO_API_KEY",""),
            initial_api_secret=os.environ.get("BINANCE_DEMO_API_SECRET",""),
        )
        self.executor=DemoExecutor(self.store)
        self._stop=threading.Event()
        self._thread=threading.Thread(target=self._loop,name="sltd-binance-demo",daemon=True)
        self._thread.start()
        self._recovery: dict[str,dict[str,Any]]={}

    def shutdown(self):
        self._stop.set()

    def connect(self, api_key: str, api_secret: str) -> dict:
        snapshot=self.session.connect_and_test(api_key,api_secret)
        adapter=self.session.adapter()
        recovery={}
        all_pass=True
        for symbol in DEFAULT_SYMBOLS:
            try:
                recovery[symbol]=self._reconcile_symbol(adapter,symbol)
            except Exception as exc:
                all_pass=False
                recovery[symbol]={"status":"BLOCKED","reason":str(exc)}
                self.store.set_runtime(symbol,run_state="RECOVERY_BLOCKED")
                self.store.audit("DEMO_RECONCILE_BLOCKED",symbol,str(exc))
            if recovery[symbol].get("status")!="PASS":
                all_pass=False
        summary={"status":"PASS" if all_pass else "BLOCKED","symbols":recovery}
        self._recovery=recovery
        self.session.set_recovery_status(summary,all_pass)
        self.store.audit("DEMO_RECONCILE_ALL",None,f"status={summary['status']}")
        return {"account":snapshot.__dict__,"recovery":summary}

    def disconnect(self):
        for symbol in DEFAULT_SYMBOLS:
            self.store.set_enabled(symbol,False)
            self.store.set_runtime(symbol,run_state="STOPPED")
        self.session.disconnect()
        self._recovery={}

    def _reconcile_symbol(self, adapter, symbol: str) -> dict:
        opens=adapter.open_orders(symbol)
        rows=opens if isinstance(opens,list) else ([opens] if opens else [])
        if rows:
            ids=[str(_first(x,"clientOrderId","client_order_id","orderId",default="?")) for x in rows if isinstance(x,dict)]
            raise RuntimeError("存在未成交订单："+",".join(ids[:3]))

        remote=float(adapter.position_amount(symbol))
        if remote<0:
            raise RuntimeError("检测到空头仓位；当前版本只允许做多")
        ledger=float(self.store.net_filled_qty(symbol))
        rules=adapter.symbol_rules(symbol)
        tol=float((rules.step_size or 0)/2)
        if abs(remote-ledger)>max(tol,1e-12):
            raise RuntimeError(f"本地订单账本仓位 {ledger} 与 Binance 仓位 {remote} 不一致")

        rt=self.store.runtimes()[symbol]
        fraction=float(rt.get("current_fraction") or 0)
        if remote>max(tol,1e-12) and fraction<=0:
            raise RuntimeError("Binance 有多头仓位，但本地策略仓位状态为空")
        if remote<=max(tol,1e-12) and fraction>1e-12:
            raise RuntimeError("本地策略记录有仓位，但 Binance 已经为空仓")
        return {"status":"PASS","remote_position":remote,"ledger_position":ledger,"fraction":fraction}

    def _connected(self) -> bool:
        return bool(self.session.public_status().get("connected"))

    def configure(self, symbol: str, *, strategy_id: str, timeframe: str, leverage: int, budget: float):
        symbol=symbol.upper().strip()
        if symbol not in DEFAULT_SYMBOLS: raise ValueError("不支持这个币种")
        if strategy_id not in EXECUTABLE_STRATEGIES: raise ValueError("缠论/顺势当前只允许观察，不允许自动下单")
        if timeframe not in TIMEFRAMES: raise ValueError("不支持这个 K 线周期")
        if not 1<=int(leverage)<=125: raise ValueError("杠杆必须在 1..125")
        if float(budget)<=0: raise ValueError("资金预算必须大于 0")

        cfg=self.store.configs()[symbol]; rt=self.store.runtimes()[symbol]
        if cfg["enabled"]: raise ValueError("请先停止该币种再修改策略")
        if float(rt.get("current_fraction") or 0)>1e-12:
            raise ValueError("当前币种仍有策略仓位，不能切换策略")
        if self._connected():
            adapter=self.session.adapter()
            if abs(float(adapter.position_amount(symbol)))>0:
                raise ValueError("Binance 当前币种仍有仓位，不能切换策略")
            opens=adapter.open_orders(symbol)
            if opens: raise ValueError("Binance 当前币种仍有挂单，不能切换策略")
        self.store.set_config(
            symbol,strategy_id=strategy_id,timeframe=timeframe,
            leverage=int(leverage),budget=float(budget),
        )
        self.store.set_runtime(symbol,state={},fraction=0.0,last_closed_open_time=None,run_state="STOPPED")
        self.store.audit("DEMO_CONFIG",symbol,f"strategy={strategy_id};tf={timeframe};lev={leverage};budget={budget}")

    def start(self, symbol: str) -> dict:
        symbol=symbol.upper().strip()
        if not self._connected(): raise ValueError("请先连接 Binance Demo")
        rec=self._recovery.get(symbol) or self._reconcile_symbol(self.session.adapter(),symbol)
        if rec.get("status")!="PASS": raise ValueError("该币种对账未通过")

        cfg=self.store.configs()[symbol]
        rt=self.store.runtimes()[symbol]
        completed,_forming,_meta=fetch_bars(symbol,cfg["timeframe"],force_refresh=True)
        if not completed: raise RuntimeError("没有已完成 K 线")
        latest=int(completed[-1].get("open_time"))

        old=rt.get("last_closed_open_time")
        fraction=float(rt.get("current_fraction") or 0)
        if fraction<=1e-12:
            self.store.set_runtime(symbol,fraction=0.0,state={},last_closed_open_time=latest,run_state="MONITORING")
        else:
            if old is None:
                raise ValueError("有仓位但缺少实时基线，已阻止恢复")
            times=[int(x.get("open_time")) for x in completed]
            if int(old) not in times:
                raise ValueError("有仓位且旧基线已超出行情窗口，已阻止恢复")
            gap=len(times)-1-times.index(int(old))
            if gap>1:
                raise ValueError(f"有仓位期间错过 {gap} 根已完成 K 线，不能自动补单")
            self.store.set_runtime(symbol,run_state="MONITORING")
        self.store.set_enabled(symbol,True)
        self.store.audit("DEMO_START",symbol,f"strategy={cfg['strategy_id']};baseline={latest}")
        return self.store.runtimes()[symbol]

    def stop(self, symbol: str):
        symbol=symbol.upper().strip()
        self.store.set_enabled(symbol,False)
        self.store.set_runtime(symbol,run_state="STOPPED")
        self.store.audit("DEMO_STOP",symbol,"manual stop")

    def emergency_flatten(self, symbol: str) -> dict:
        symbol=symbol.upper().strip()
        self.stop(symbol)
        adapter=self.session.adapter()
        amount=float(adapter.position_amount(symbol))
        if amount<0: raise RuntimeError("检测到空头仓位，拒绝自动处理")
        if amount==0:
            self.store.set_runtime(symbol,fraction=0.0,state={},last_order_id=None,run_state="STOPPED")
            return {"status":"ALREADY_FLAT"}
        rules=adapter.symbol_rules(symbol)
        from binance_demo_exchange import floor_to_step
        from decimal import Decimal
        qty=floor_to_step(Decimal(str(amount)),rules.step_size)
        if qty<=0: raise RuntimeError("当前仓位小于最小可平数量")
        cid=f"sv7-{symbol[:-4]}-{int(time.time())}-EMG"
        self.store.begin_order(symbol,cid,"EMERGENCY","SELL",float(qty),0.0)
        order=adapter.submit_market_sell_reduce_only(symbol,quantity=qty,client_order_id=cid)
        status=str(_first(order,"status",default="")).upper()
        self.store.finish_order(
            symbol,cid,order_id=str(_first(order,"orderId","order_id",default=cid)),
            status=status,qty=float(_first(order,"executedQty","executed_qty",default=qty)),
            price=float(_first(order,"avgPrice","avg_price",default=0) or 0),
        )
        if status!="FILLED": raise RuntimeError(f"紧急平仓未完成：{status}")
        self.store.set_runtime(symbol,fraction=0.0,state={},last_order_id=str(_first(order,"orderId",default=cid)),run_state="STOPPED")
        self.store.audit("DEMO_EMERGENCY_FLAT",symbol,f"qty={qty}")
        return {"status":"FILLED","order_id":_first(order,"orderId","order_id")}

    def _loop(self):
        while not self._stop.wait(2.0):
            if not self._connected():
                continue
            for symbol,cfg in self.store.configs().items():
                if not cfg["enabled"]:
                    continue
                try:
                    self._tick(symbol,cfg)
                except Exception as exc:
                    self.store.set_enabled(symbol,False)
                    self.store.set_runtime(symbol,run_state="EXECUTION_BLOCKED")
                    self.store.audit("DEMO_TICK_BLOCKED",symbol,f"{type(exc).__name__}:{exc}")

    def _tick(self, symbol: str, cfg: dict):
        rt=self.store.runtimes()[symbol]
        completed,forming,meta=fetch_bars(symbol,cfg["timeframe"],force_refresh=True)
        if not completed: return
        times=[int(x.get("open_time")) for x in completed]
        latest=times[-1]
        old=rt.get("last_closed_open_time")
        if old is None:
            self.store.set_runtime(symbol,last_closed_open_time=latest)
            return
        if latest==int(old):
            return
        if int(old) not in times:
            raise DemoExecutionBlocked("最后处理 K 线已超出窗口，禁止补历史单")
        gap=len(times)-1-times.index(int(old))
        if gap!=1:
            raise DemoExecutionBlocked(f"错过 {gap} 根已完成 K 线，禁止补历史单")

        plan=make_plan(
            cfg["strategy_id"],symbol,completed,cfg["timeframe"],meta,
            float(rt.get("current_fraction") or 0),dict(rt.get("state") or {}),
        )
        if int(plan.signal_open_time)!=latest:
            raise DemoExecutionBlocked("策略信号 K 线与最新已完成 K 线不一致")
        if plan.actions:
            ref=float((forming or completed[-1])["open"] if forming else completed[-1]["close"])
            self.executor.execute(symbol,plan,cfg,rt,self.session.adapter(),ref)
        self.store.set_runtime(symbol,state=plan.next_state,last_closed_open_time=latest,run_state="MONITORING")
        self.store.audit("DEMO_BAR_PROCESSED",symbol,f"open_time={latest};actions={len(plan.actions)}")

    def status(self) -> dict:
        public=self.session.public_status()
        account={}
        pnl={}
        if public.get("connected"):
            try:
                adapter=self.session.adapter()
                balances=adapter.balances()
                rows=balances if isinstance(balances,list) else [balances]
                usdt=next((x for x in rows if isinstance(x,dict) and str(_first(x,"asset",default="")).upper()=="USDT"),{})
                account={
                    "usdt_balance":float(_first(usdt,"balance",default=0) or 0),
                    "usdt_available":float(_first(usdt,"availableBalance","available_balance",default=0) or 0),
                    "one_way":bool(adapter.is_one_way()),
                }
                for symbol,rt in self.store.runtimes().items():
                    positions=adapter.positions(symbol)
                    prs=positions if isinstance(positions,list) else [positions]
                    row=next((x for x in prs if isinstance(x,dict) and str(_first(x,"symbol",default="")).upper()==symbol),{})
                    pnl[symbol]={
                        "position_amount":float(_first(row,"positionAmt","position_amt",default=0) or 0),
                        "unrealized_pnl":float(_first(row,"unRealizedProfit","unrealizedProfit","unrealized_profit",default=0) or 0),
                    }
            except Exception as exc:
                account={"error":str(exc)}
        return {
            "session":public,
            "account":account,
            "configs":self.store.configs(),
            "runtime":self.store.runtimes(),
            "pnl":pnl,
            "recovery":self._recovery,
            "audit":self.store.recent_audit(30),
            "executable_strategies":list(EXECUTABLE_STRATEGIES),
            "display_only_strategies":["chan","support_resistance"],
        }
