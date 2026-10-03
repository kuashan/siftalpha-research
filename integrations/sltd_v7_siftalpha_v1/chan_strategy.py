from __future__ import annotations

"""V7 Chan tab backed by the pinned upstream Vespa314/chan.py engine.

The upstream calculation core is vendored unchanged under vendor/chanpy and
pinned to commit 429d6ed3043e27c93a003ba2b10e70a05575e1f5.

This adapter only:
- converts SiftAlpha completed OHLCV bars to upstream CKLine_Unit objects;
- feeds them one bar at a time through CChan.trigger_load;
- translates upstream Bi / Segment / Zhongshu / BSP objects to the existing
  SiftAlpha V7 web payload.

No SLTD, XMA, E, 5s, or Shunshi signal is consumed by this adapter.
"""

import sys
from datetime import datetime, timezone
from math import isfinite
from pathlib import Path
from typing import Iterable

_VENDOR_ROOT = Path(__file__).resolve().parent / "vendor" / "chanpy"
if str(_VENDOR_ROOT) not in sys.path:
    sys.path.insert(0, str(_VENDOR_ROOT))

from Chan import CChan  # type: ignore  # noqa: E402
from ChanConfig import CChanConfig  # type: ignore  # noqa: E402
from Common.CEnum import AUTYPE, DATA_FIELD, KL_TYPE  # type: ignore  # noqa: E402
from Common.CTime import CTime  # type: ignore  # noqa: E402
from KLine.KLine_Unit import CKLine_Unit  # type: ignore  # noqa: E402


CHAN_STRATEGY_ID = "chan"
CHAN_UPSTREAM_REPOSITORY = "Vespa314/chan.py"
CHAN_UPSTREAM_COMMIT = "429d6ed3043e27c93a003ba2b10e70a05575e1f5"
CHAN_STRATEGY_VERSION = "缠论 · chan.py upstream 429d6ed"
CHAN_SOURCE = f"{CHAN_UPSTREAM_REPOSITORY}@{CHAN_UPSTREAM_COMMIT}"
CHAN_MIN_BARS = 20

CHAN_RULES = {
    "BUY": (
        "CHAN_B1", "CHAN_B1P", "CHAN_B2", "CHAN_B2S", "CHAN_B3A", "CHAN_B3B",
    ),
    "HOLD": (),
    "WAIT": (),
    "SELL": (
        "CHAN_S1", "CHAN_S1P", "CHAN_S2", "CHAN_S2S", "CHAN_S3A", "CHAN_S3B",
    ),
}

CHAN_RULE_NAMES_ZH = {
    "CHAN_B1": "一买",
    "CHAN_B1P": "盘整背驰类一买",
    "CHAN_B2": "二买",
    "CHAN_B2S": "类二买",
    "CHAN_B3A": "三买 A",
    "CHAN_B3B": "三买 B",
    "CHAN_S1": "一卖",
    "CHAN_S1P": "盘整背驰类一卖",
    "CHAN_S2": "二卖",
    "CHAN_S2S": "类二卖",
    "CHAN_S3A": "三卖 A",
    "CHAN_S3B": "三卖 B",
}

ACTION_NAMES_ZH = {
    "BUY": "买点",
    "SELL": "卖点",
    "NONE": "无新的当前执行信号",
}

_BSP_SUFFIX = {
    "1": "1",
    "1p": "1P",
    "2": "2",
    "2s": "2S",
    "3a": "3A",
    "3b": "3B",
}

_TIMEFRAME_LEVELS = {
    "1m": KL_TYPE.K_1M,
    "3m": KL_TYPE.K_3M,
    "5m": KL_TYPE.K_5M,
    "15m": KL_TYPE.K_15M,
    "30m": KL_TYPE.K_30M,
    "1h": KL_TYPE.K_60M,
    "2h": KL_TYPE.K_60M,
    "4h": KL_TYPE.K_60M,
    "1d": KL_TYPE.K_DAY,
    "5d": KL_TYPE.K_DAY,
}


def _validate_candles(candles: Iterable[dict]) -> list[dict]:
    out: list[dict] = []
    last_key: tuple[int, str] | None = None
    for raw in candles:
        date = str(raw.get("date") or "").strip()
        if not date:
            raise ValueError("K 线日期不能为空")
        o = float(raw["open"])
        h = float(raw["high"])
        l = float(raw["low"])
        c = float(raw["close"])
        v = float(raw.get("volume") or 0.0)
        if not all(isfinite(x) for x in (o, h, l, c, v)):
            raise ValueError(f"{date}: K 线字段不是有限数")
        if h < l or h < max(o, c) or l > min(o, c):
            raise ValueError(f"{date}: OHLC 高低关系非法")
        open_time = raw.get("open_time")
        key = (
            int(open_time) if open_time is not None else 0,
            date,
        )
        if last_key is not None and key <= last_key:
            raise ValueError("K 线必须按时间严格递增排列")
        last_key = key
        out.append(
            {
                "date": date,
                "open_time": int(open_time) if open_time is not None else None,
                "open": o,
                "high": h,
                "low": l,
                "close": c,
                "volume": v,
            }
        )
    if len(out) < CHAN_MIN_BARS:
        raise ValueError(f"缠论至少需要 {CHAN_MIN_BARS} 根已结束 K 线")
    return out


def _to_datetime(row: dict) -> datetime:
    if row.get("open_time") is not None:
        return datetime.fromtimestamp(int(row["open_time"]), tz=timezone.utc)
    raw = str(row["date"]).strip()
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return datetime.strptime(raw[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)


def _to_klu(row: dict) -> CKLine_Unit:
    dt = _to_datetime(row)
    return CKLine_Unit(
        {
            DATA_FIELD.FIELD_TIME: CTime(
                dt.year,
                dt.month,
                dt.day,
                dt.hour,
                dt.minute,
                dt.second,
                auto=False,
            ),
            DATA_FIELD.FIELD_OPEN: row["open"],
            DATA_FIELD.FIELD_HIGH: row["high"],
            DATA_FIELD.FIELD_LOW: row["low"],
            DATA_FIELD.FIELD_CLOSE: row["close"],
            DATA_FIELD.FIELD_VOLUME: row["volume"],
        }
    )


def _date_at(bars: list[dict], index: int) -> str:
    i = max(0, min(len(bars) - 1, int(index)))
    return str(bars[i]["date"])


def _direction(line) -> str:
    return "up" if line.is_up() else "down"


def _line_overlay(line, bars: list[dict], visible_start: int, visible_end: int) -> dict | None:
    start_idx = int(line.get_begin_klu().idx)
    end_idx = int(line.get_end_klu().idx)
    if end_idx < visible_start or start_idx > visible_end:
        return None
    clipped_start = max(visible_start, start_idx)
    clipped_end = min(visible_end, end_idx)
    return {
        "direction": _direction(line),
        "start_date": _date_at(bars, clipped_start),
        "start_price": (
            float(bars[clipped_start]["close"])
            if start_idx < visible_start
            else float(line.get_begin_val())
        ),
        "actual_start_date": _date_at(bars, start_idx),
        "actual_start_price": float(line.get_begin_val()),
        "end_date": _date_at(bars, clipped_end),
        "end_price": (
            float(bars[clipped_end]["close"])
            if end_idx > visible_end
            else float(line.get_end_val())
        ),
        "actual_end_date": _date_at(bars, end_idx),
        "actual_end_price": float(line.get_end_val()),
        "pending": not bool(line.is_sure),
        "count": (
            int(line.cal_bi_cnt())
            if hasattr(line, "cal_bi_cnt")
            else int(line.get_klu_cnt())
        ),
    }


def _endpoint_rows(kl, bars: list[dict], visible_start: int) -> list[dict]:
    points: dict[tuple[int, str], dict] = {}
    for bi in kl.bi_list:
        start = int(bi.get_begin_klu().idx)
        end = int(bi.get_end_klu().idx)
        if bi.is_up():
            pairs = (
                (start, "bottom", float(bi.get_begin_val())),
                (end, "top", float(bi.get_end_val())),
            )
        else:
            pairs = (
                (start, "top", float(bi.get_begin_val())),
                (end, "bottom", float(bi.get_end_val())),
            )
        for idx, kind, price in pairs:
            if idx < visible_start:
                continue
            points[(idx, kind)] = {
                "type": kind,
                "anchor_date": _date_at(bars, idx),
                "confirm_date": None,
                "price": price,
            }
    return [points[k] for k in sorted(points)]


def _zs_rows(zs_list, bars: list[dict], visible_start: int, visible_end: int, level: int, label: str) -> list[dict]:
    rows: list[dict] = []
    for zs in zs_list:
        start = int(zs.begin.idx)
        end = int(zs.end.idx)
        if end < visible_start or start > visible_end:
            continue
        rows.append(
            {
                "level": level,
                "level_label": label,
                "canonical": level >= 1,
                "start_date": _date_at(bars, max(start, visible_start)),
                "end_date": _date_at(bars, min(end, visible_end)),
                "actual_start_date": _date_at(bars, start),
                "actual_end_date": _date_at(bars, end),
                "confirm_date": None,
                "ZG": float(zs.high),
                "ZD": float(zs.low),
                "GG": float(zs.peak_high),
                "DD": float(zs.peak_low),
                "count": int(zs.end_bi.idx - zs.begin_bi.idx + 1),
                "pending": not bool(zs.is_sure),
                "upgraded": level >= 1,
            }
        )
    return rows


def _kind_for(point, bsp_type) -> str:
    side = "B" if bool(point.is_buy) else "S"
    return side + _BSP_SUFFIX[bsp_type.value]


def _signal_rows(points, bars: list[dict], *, level: int, level_label: str) -> list[dict]:
    rows: list[dict] = []
    for point in points:
        anchor = int(point.klu.idx)
        price = float(point.bi.get_end_val())
        for bsp_type in point.type:
            kind = _kind_for(point, bsp_type)
            rule_id = f"CHAN_{kind}"
            rows.append(
                {
                    "kind": kind,
                    "rule_id": rule_id,
                    "rule_name_zh": CHAN_RULE_NAMES_ZH.get(rule_id, kind),
                    "level": level,
                    "level_label": level_label,
                    "canonical_level": level >= 1,
                    "anchor_index": anchor,
                    "anchor_date": _date_at(bars, anchor),
                    "confirm_index": None,
                    "confirm_date": None,
                    "price": price,
                    "status": "UPSTREAM_CURRENT_FRAME",
                    "sure_structure": bool(point.bi.is_sure),
                    "note": "Vespa314/chan.py 当前帧形态学买卖点；后续 K 线可能修正或使该点消失。",
                }
            )
    rows.sort(key=lambda x: (x["anchor_index"], x["level"], x["kind"]))
    return rows


def _last_structure_text(kl) -> str:
    if len(kl.seg_list):
        seg = kl.seg_list[-1]
        return (
            ("向上线段" if seg.is_up() else "向下线段")
            + (" · 已确认" if seg.is_sure else " · 虚段")
        )
    if len(kl.bi_list):
        bi = kl.bi_list[-1]
        return (
            ("向上笔" if bi.is_up() else "向下笔")
            + (" · 已确认" if bi.is_sure else " · 虚笔")
        )
    return "结构形成中"


def analyze_chan(
    symbol: str,
    candles: Iterable[dict],
    *,
    display_limit: int = 300,
    timeframe: str = "1d",
) -> dict:
    bars = _validate_candles(candles)
    level = _TIMEFRAME_LEVELS.get(str(timeframe).lower(), KL_TYPE.K_DAY)
    config = CChanConfig({"trigger_step": True})
    chan = CChan(
        code=str(symbol),
        lv_list=[level],
        config=config,
        autype=AUTYPE.NONE,
    )
    for row in bars:
        chan.trigger_load({level: [_to_klu(row)]})

    kl = chan[0]
    limit = max(80, min(int(display_limit), 500))
    visible_start = max(0, len(bars) - limit)
    visible_end = len(bars) - 1

    chart = [
        {
            "date": x["date"],
            "open": x["open"],
            "high": x["high"],
            "low": x["low"],
            "close": x["close"],
            "volume": x["volume"],
            "state": "OTHER",
            "state_zh": "chan.py 当前帧",
            "position": 0.0,
            "risk_armed": False,
        }
        for x in bars[visible_start:]
    ]

    bis_overlay = [
        row
        for bi in kl.bi_list
        if (row := _line_overlay(bi, bars, visible_start, visible_end)) is not None
    ]
    segments_overlay = [
        row
        for seg in kl.seg_list
        if (row := _line_overlay(seg, bars, visible_start, visible_end)) is not None
    ]

    zhongshu_overlay = (
        _zs_rows(kl.zs_list, bars, visible_start, visible_end, 0, "L0 笔级")
        + _zs_rows(kl.segzs_list, bars, visible_start, visible_end, 1, "L1 线段级")
    )

    bi_points = kl.bs_point_lst.getSortedBspList()
    seg_points = kl.seg_bs_point_lst.getSortedBspList()
    all_signals = (
        _signal_rows(bi_points, bars, level=0, level_label="L0 笔级")
        + _signal_rows(seg_points, bars, level=1, level_label="L1 线段级")
    )
    all_signals.sort(key=lambda x: (x["anchor_index"], x["level"], x["kind"]))
    signal_overlay = [
        x for x in all_signals if int(x["anchor_index"]) >= visible_start
    ]

    latest_seen = all_signals[-1] if all_signals else None
    current_structure = _last_structure_text(kl)
    latest = bars[-1]

    last_bi = kl.bi_list[-1] if len(kl.bi_list) else None
    last_seg = kl.seg_list[-1] if len(kl.seg_list) else None
    last_zs = zhongshu_overlay[-1] if zhongshu_overlay else None

    events = []
    for signal in all_signals[-100:]:
        action = "BUY" if signal["kind"].startswith("B") else "SELL"
        events.append(
            {
                "date": signal["anchor_date"],
                "state": "OTHER",
                "state_zh": f"{signal['kind']} · {signal['level_label']}",
                "age": "chan.py 当前帧 BSP",
                "origin": signal["level_label"],
                "action": action,
                "action_zh": ACTION_NAMES_ZH[action],
                "rule_ids": [signal["rule_id"]],
                "rule_names_zh": [signal["rule_name_zh"]],
                "execution_date": None,
                "execution_price": None,
                "position_after": None,
                "risk_after": "结构信号，不直接执行",
                "note": signal["note"],
            }
        )

    return {
        "strategy": {
            "id": CHAN_STRATEGY_ID,
            "selector_label": "缠论",
            "version": CHAN_STRATEGY_VERSION,
            "source_commit": CHAN_SOURCE,
            "active_rule_count": sum(len(x) for x in CHAN_RULES.values()),
            "active_rules": CHAN_RULES,
            "active_rules_zh": {
                group: [CHAN_RULE_NAMES_ZH[x] for x in ids]
                for group, ids in CHAN_RULES.items()
            },
            "position_policy": "UPSTREAM_CHANPY_MORPHOLOGY_ONLY",
            "position_policy_zh": "直接采用 Vespa314/chan.py 原版开源缠论核心；V7 仅负责数据适配和显示",
            "hard_exit": "NONE",
            "hard_exit_zh": "无外部策略退出规则",
            "display_candles": limit,
            "timeframe": str(timeframe),
            "bar_close_contract": "UPSTREAM_CURRENT_FRAME_COMPLETED_BARS_ONLY",
            "bar_close_contract_zh": "仅输入已结束 K 线；BSP 为 chan.py 当前帧形态学结果，后续 K 线可能修正或使历史 BSP 消失",
            "rules_title_zh": "chan.py 原版买卖点",
            "policy_title_zh": "Vespa314/chan.py 原版核心",
            "summary_state_label_zh": "当前缠论结构",
            "policy_steps_zh": [
                "① SiftAlpha 只提供已结束 OHLCV K 线",
                "② 每根 K 线通过 CChan.trigger_load 逐根送入上游引擎",
                "③ 上游原版计算包含处理、分型、笔、虚笔/实笔",
                "④ 上游原版计算线段、虚段/实段、中枢和父级结构",
                "⑤ 原版 BSP 分类：1、1p、2、2s、3a、3b",
                "⑥ V7 不改写上游公式，只把原版结构和买卖点转换成网页显示",
                "⑦ 当前帧未确认结构允许被后续 K 线修正，这是上游原版语义",
            ],
        },
        "snapshot": {
            "symbol": symbol,
            "latest_date": latest["date"],
            "latest_close": latest["close"],
            "state": "OTHER",
            "state_zh": current_structure,
            "run_age": None,
            "age_bucket": "chan.py 当前帧",
            "origin": None,
            "resolved_action": "NONE",
            "resolved_action_zh": ACTION_NAMES_ZH["NONE"],
            "rule_ids": [],
            "rule_names_zh": [],
            "position_fraction": 0.0,
            "risk_state": "NORMAL",
            "risk_state_zh": current_structure,
            "risk_sub_zh": "Vespa314/chan.py 原版开源核心；与 V7/E/5s/顺势完全隔离",
            "next_action": "显示 chan.py 当前帧 BSP；这些结构点用于缠论观察，不自动转换成交易订单。",
            "chan_bi": (
                ("向上笔" if last_bi.is_up() else "向下笔")
                + (" · 已确认" if last_bi.is_sure else " · 虚笔")
                if last_bi else "尚未形成"
            ),
            "chan_segment": (
                ("向上线段" if last_seg.is_up() else "向下线段")
                + (" · 已确认" if last_seg.is_sure else " · 虚段")
                if last_seg else "尚未形成"
            ),
            "chan_zhongshu": (
                f"{last_zs['level_label']} · ZG {last_zs['ZG']:.3f} / ZD {last_zs['ZD']:.3f}"
                if last_zs else "当前可视区无中枢"
            ),
            "chan_last_signal": (
                f"{latest_seen['kind']} · {latest_seen['level_label']} · {latest_seen['anchor_date']}"
                if latest_seen else "暂无"
            ),
        },
        "chart": chart,
        "markers": [],
        "events": events,
        "chan": {
            "endpoints": _endpoint_rows(kl, bars, visible_start),
            "bis": bis_overlay,
            "segments": segments_overlay,
            "zhongshus": zhongshu_overlay,
            "trends": [],
            "signals": signal_overlay,
            "levels": [
                {
                    "level": 0,
                    "label": "L0 笔级",
                    "canonical": False,
                    "units": len(kl.bi_list),
                    "zhongshus": len(kl.zs_list),
                    "bsp_points": len(bi_points),
                },
                {
                    "level": 1,
                    "label": "L1 线段级",
                    "canonical": True,
                    "units": len(kl.seg_list),
                    "zhongshus": len(kl.segzs_list),
                    "bsp_points": len(seg_points),
                },
            ],
            "counts": {
                "raw_bars_total": len(bars),
                "merged": len(kl),
                "bi_endpoints": len(_endpoint_rows(kl, bars, 0)),
                "bis": len(kl.bi_list),
                "sure_bis": sum(1 for x in kl.bi_list if x.is_sure),
                "segments": len(kl.seg_list),
                "sure_segments": sum(1 for x in kl.seg_list if x.is_sure),
                "virtual_segments": sum(1 for x in kl.seg_list if not x.is_sure),
                "zhongshus": len(kl.zs_list),
                "segment_zhongshus": len(kl.segzs_list),
                "bsp_points": len(bi_points),
                "segment_bsp_points": len(seg_points),
                "bsp_type_memberships": len(all_signals),
            },
            "upstream_repository": CHAN_UPSTREAM_REPOSITORY,
            "upstream_commit": CHAN_UPSTREAM_COMMIT,
            "display_contract_zh": (
                "笔、线段、中枢与 1/1p/2/2s/3a/3b 买卖点均直接来自固定版本 chan.py；"
                "虚结构和当前帧 BSP 允许随后续 K 线修正。"
            ),
        },
    }
