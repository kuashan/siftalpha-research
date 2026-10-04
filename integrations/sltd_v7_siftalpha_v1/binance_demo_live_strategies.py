from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import e_strategy
import five_s_signal_engine
import strategy as sltd


@dataclass(frozen=True)
class LiveAction:
    code: str
    rule_ids: tuple[str, ...]


@dataclass(frozen=True)
class LivePlan:
    strategy_id: str
    signal_open_time: int
    signal_date: str
    actions: tuple[LiveAction, ...]
    next_state: dict[str, Any]


def _open_time(row: dict, fallback: int) -> int:
    return int(row.get("open_time", row.get("openTime", fallback)))


def sltd_plan(symbol: str, bars: list[dict], fraction: float, state: dict) -> LivePlan:
    ledger=sltd.build_ledger(bars, symbol)
    row=ledger[-1]
    risk_armed=bool(state.get("risk_armed", False))
    actions: list[LiveAction]=[]
    next_state=dict(state)

    if fraction > 1e-12 and risk_armed and sltd.c2_condition(row):
        actions.append(LiveAction("SLTD_C2_EXIT", tuple(sltd._rule_ids(row))))
        next_state["risk_armed"]=False
    else:
        action=sltd.resolve_action(row)
        if action=="BUY":
            actions.append(LiveAction("SLTD_BUY25", tuple(sltd._rule_ids(row))))
            next_state["risk_armed"]=False
        elif action=="SELL" and fraction > 1e-12:
            actions.append(LiveAction("SLTD_SELL25_CURRENT", tuple(sltd._rule_ids(row))))
            next_state["risk_armed"]=True

    return LivePlan(
        "v7",
        _open_time(bars[-1], len(bars)-1),
        str(bars[-1]["date"]),
        tuple(actions),
        next_state,
    )


def e_plan(symbol: str, bars: list[dict], timeframe: str, market_meta: dict, fraction: float, state: dict) -> LivePlan:
    tf=str(timeframe).lower()
    primary=e_strategy._copy_validated(bars)
    higher_tf,higher_bars=e_strategy.build_higher_bars(primary, tf, market_meta)
    if len(higher_bars) < e_strategy.E_MIN_WARMUP_BARS:
        raise ValueError(f"{symbol}: E 大周期 {higher_tf} 预热不足")
    primary_ledger=e_strategy.build_ledger(primary, symbol)
    higher_ledger=e_strategy.build_ledger(higher_bars, f"{symbol}:{higher_tf}")

    i=len(primary)-1
    h=-1
    for j,row in enumerate(higher_bars):
        if int(row["_source_end_index"]) <= i:
            h=j
        else:
            break
    higher_row=higher_ledger[h] if h >= e_strategy.E_MIN_WARMUP_BARS-1 else None
    if i < e_strategy.E_MIN_WARMUP_BARS-1 or higher_row is None:
        raise ValueError(f"{symbol}: E 主/大周期共同预热不足")

    b1=bool(state.get("b1_used",False))
    b2=bool(state.get("b2_used",False))
    b3=bool(state.get("b3_used",False))
    sell_stage=int(state.get("sell_stage",0))
    row=primary_ledger[i]
    bar=primary[i]
    actions: list[LiveAction]=[]
    next_state={"b1_used":b1,"b2_used":b2,"b3_used":b3,"sell_stage":sell_stage}

    if fraction > 1e-12:
        inner_up=e_strategy._break_above_zk1(i, primary, primary_ledger)
        exit_active=sell_stage>0 or inner_up
        band=e_strategy._band_touch(bar,row)
        bs=row.get("BS")
        bs_hit=bs is not None and float(bar["high"]) >= float(bs)
        if exit_active and band:
            actions.append(LiveAction("E_EXIT",("E_SELL_3_TOUCH_GZB_BAND_FULL_EXIT",)))
            next_state={"b1_used":False,"b2_used":False,"b3_used":False,"sell_stage":0}
        elif sell_stage>0 and row.get("ZK1") is not None and float(bar["close"]) < float(row["ZK1"]):
            actions.append(LiveAction("E_EXIT",("E_SELL_4_CLOSE_BACK_BELOW_ZK1_FULL_EXIT",)))
            next_state={"b1_used":False,"b2_used":False,"b3_used":False,"sell_stage":0}
        elif exit_active and bs_hit:
            actions.append(LiveAction("E_SELL25PP",("E_SELL_2_TOUCH_BS_MINUS_25PP",)))
            next_state["sell_stage"]=max(sell_stage,2)
        elif sell_stage==0 and inner_up:
            actions.append(LiveAction("E_SELL50PP",("E_SELL_1_PRIMARY_CLOSE_BREAK_ABOVE_ZK1_MINUS_50PP",)))
            next_state["sell_stage"]=1

    if not actions and sell_stage==0:
        color=str(row.get("color") or "")
        inner_down=(
            not b1
            and color in {"BLUE","GRAY"}
            and e_strategy._break_below_zd1(i, primary, primary_ledger)
        )
        if inner_down:
            ids=["E_BUY_1_PRIMARY_CLOSE_BREAK_BELOW_ZD1"]
            code="E_BUY25"
            next_state["b1_used"]=True
            if (
                not b2
                and higher_row.get("ZD1") is not None
                and float(higher_row["close"]) < float(higher_row["ZD1"])
            ):
                ids.append("E_BUY_2_HIGHER_CLOSE_BELOW_ZD1")
                code="E_BUY50"
                next_state["b2_used"]=True
            actions.append(LiveAction(code,tuple(ids)))
        elif b1 and not b3 and e_strategy._band_touch(bar,row):
            actions.append(LiveAction("E_BUY25",("E_BUY_3_TOUCH_GZB_BAND",)))
            next_state["b3_used"]=True

    return LivePlan(
        "e",
        _open_time(bars[-1], i),
        str(bars[-1]["date"]),
        tuple(actions),
        next_state,
    )


def five_s_plan(bars: list[dict], fraction: float, state: dict) -> LivePlan:
    rows=[]
    for i,b in enumerate(bars):
        rows.append({
            "open_time":_open_time(b,i),
            "open":float(b["open"]),"high":float(b["high"]),"low":float(b["low"]),
            "close":float(b["close"]),"volume":float(b.get("volume") or 0),
        })
    evs=five_s_signal_engine.evaluate_candles(rows)
    ev=evs[-1]
    buy=tuple(ev.buy_onsets)
    sell=tuple(ev.sell_onsets)

    c_confirmed=bool(state.get("c_confirmed",False))
    entry_time=state.get("entry_signal_open_time")
    first_sell=set(state.get("first_sell_families") or [])
    actions: list[LiveAction]=[]
    next_state=dict(state)

    if fraction <= 1e-12:
        initial=[x for x in buy if x in ("A","B")]
        if initial and not sell:
            fam=initial[0]
            actions.append(LiveAction("5S_BUY60",(f"BUY_{fam}",)))
            next_state={
                "c_confirmed":False,
                "entry_signal_open_time":int(ev.open_time),
                "entry_family":fam,
                "first_sell_families":[],
            }
    else:
        entry_idx=None
        if entry_time is not None:
            for k,x in enumerate(evs):
                if int(x.open_time)==int(entry_time):
                    entry_idx=k
                    break
        if (
            not c_confirmed and entry_idx is not None
            and 1 <= ev.index-entry_idx <= 3
            and "C" in buy
        ):
            actions.append(LiveAction("5S_TOPUP40",("BUY_C",)))
            next_state["c_confirmed"]=True

        if sell:
            if not first_sell:
                new_first=set(sell)
                next_state["first_sell_families"]=sorted(new_first)
                if len(sell)>=2:
                    actions.append(LiveAction("5S_FULL_EXIT",("MULTI_SELL",)))
                elif "C" in sell:
                    actions.append(LiveAction("5S_FULL_EXIT",("SELL_C",)))
                else:
                    fam=sell[0]
                    actions.append(LiveAction("5S_HALF_EXIT",(f"SELL_{fam}",)))
            elif any(x not in first_sell for x in sell):
                actions.append(LiveAction(
                    "5S_FULL_EXIT",
                    tuple(["DISTINCT_SELL_FULL", *[f"SELL_{x}" for x in sell]])
                ))

        if any(a.code=="5S_FULL_EXIT" for a in actions):
            next_state={}

    return LivePlan(
        "5s_stocks",
        int(ev.open_time),
        str(bars[-1]["date"]),
        tuple(actions),
        next_state,
    )


def make_plan(strategy_id: str, symbol: str, bars: list[dict], timeframe: str,
              market_meta: dict, fraction: float, state: dict) -> LivePlan:
    if strategy_id=="v7":
        return sltd_plan(symbol,bars,fraction,state)
    if strategy_id=="e":
        return e_plan(symbol,bars,timeframe,market_meta,fraction,state)
    if strategy_id=="5s_stocks":
        return five_s_plan(bars,fraction,state)
    raise ValueError("该策略当前不允许自动下单")
