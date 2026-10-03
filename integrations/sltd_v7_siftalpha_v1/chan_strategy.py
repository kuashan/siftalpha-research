from __future__ import annotations

"""V7 Chan tab adapter powered by pinned Vespa314/chan.py upstream core.

The Chan calculation itself is NOT reimplemented here.  This module only:
1) adapts SiftAlpha completed OHLCV bars into upstream CKLine_Unit objects;
2) feeds them to upstream CChan through trigger_load one completed bar at a time;
3) converts upstream Bi / Segment / Zhongshu / BSP objects into the existing
   V7 web payload contract.

Upstream is bundled by CI/package at:
    vendor/chanpy
Pinned commit:
    429d6ed3043e27c93a003ba2b10e70a05575e1f5

Important display boundary:
upstream chan.py keeps sure and virtual current-frame structures.  A virtual
structure/BSP can change or disappear as later bars arrive.  The adapter does
not relabel a current-frame anchor as a historical first-observed confirmation.
"""

from datetime import datetime
from pathlib import Path
import sys
from typing import Iterable

CHAN_STRATEGY_ID = "chan"
CHANPY_UPSTREAM_SHA = "429d6ed3043e27c93a003ba2b10e70a05575e1f5"
CHAN_STRATEGY_VERSION = "缠论 · chan.py upstream 429d6ed"
CHAN_SOURCE = f"Vespa314/chan.py@{CHANPY_UPSTREAM_SHA}"
CHAN_MIN_BARS = 120

_VENDOR_ROOT = Path(__file__).resolve().parent / "vendor" / "chanpy"
if not (_VENDOR_ROOT / "Chan.py").exists():
    raise RuntimeError(
        "缺少 vendor/chanpy 上游核心；请使用 GitHub Actions 生成的 V7 SiftAlpha 安装包。"
    )
if str(_VENDOR_ROOT) not in sys.path:
    sys.path.insert(0, str(_VENDOR_ROOT))

from Chan import CChan  # noqa: E402
from ChanConfig import CChanConfig  # noqa: E402
from Common.CEnum import AUTYPE, DATA_FIELD, KL_TYPE  # noqa: E402
from Common.CTime import CTime  # noqa: E402
from KLine.KLine_Unit import CKLine_Unit  # noqa: E402


_TYPE_SUFFIX = {
    "1": "1",
    "1p": "1P",
    "2": "2",
    "2s": "2S",
    "3a": "3A",
    "3b": "3B",
}

CHAN_RULES = {
    "BUY": (
        "CHAN_B1",
        "CHAN_B1P",
        "CHAN_B2",
        "CHAN_B2S",
        "CHAN_B3A",
        "CHAN_B3B",
    ),
    "HOLD": (),
    "WAIT": (),
    "SELL": (
        "CHAN_S1",
        "CHAN_S1P",
        "CHAN_S2",
        "CHAN_S2S",
        "CHAN_S3A",
        "CHAN_S3B",
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
    "NONE": "无新买卖点",
}


def _validate_candles(candles: Iterable[dict]) -> list[dict]:
    out: list[dict] = []
    last = ""
    for raw in candles:
        date = str(raw.get("date") or "")
        if not date:
            raise ValueError("K 线日期不能为空")
        if last and date <= last:
            raise ValueError("K 线必须按时间严格递增排列")
        o = float(raw["open"])
        h = float(raw["high"])
        l = float(raw["low"])
        c = float(raw["close"])
        if h < max(o, l, c) or l > min(o, h, c):
            raise ValueError(f"{date}: OHLC 数据非法")
        out.append(
            {
                "date": date,
                "open": o,
                "high": h,
                "low": l,
                "close": c,
                "volume": float(raw.get("volume") or 0.0),
            }
        )
        last = date
    if len(out) < CHAN_MIN_BARS:
        raise ValueError(f"缠论至少需要 {CHAN_MIN_BARS} 根已结束 K 线")
    return out


def _ctime(value: str) -> CTime:
    text = str(value).strip()
    if len(text) <= 10:
        dt = datetime.strptime(text[:10], "%Y-%m-%d")
    else:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
    return CTime(
        dt.year,
        dt.month,
        dt.day,
        dt.hour,
        dt.minute,
        dt.second,
        auto=False,
    )


def _klu(row: dict) -> CKLine_Unit:
    return CKLine_Unit(
        {
            DATA_FIELD.FIELD_TIME: _ctime(row["date"]),
            DATA_FIELD.FIELD_OPEN: row["open"],
            DATA_FIELD.FIELD_HIGH: row["high"],
            DATA_FIELD.FIELD_LOW: row["low"],
            DATA_FIELD.FIELD_CLOSE: row["close"],
            DATA_FIELD.FIELD_VOLUME: row["volume"],
        }
    )


def _clip(index: int, start: int, end: int) -> int:
    return max(start, min(end, int(index)))


def _date(rows: list[dict], index: int) -> str:
    return rows[_clip(index, 0, len(rows) - 1)]["date"]


def _build_upstream(symbol: str, rows: list[dict]) -> object:
    config = CChanConfig({"trigger_step": True})
    chan = CChan(
        code=symbol,
        lv_list=[KL_TYPE.K_DAY],
        config=config,
        autype=AUTYPE.NONE,
    )
    for row in rows:
        chan.trigger_load({KL_TYPE.K_DAY: [_klu(row)]})
    return chan


def _line_overlay(
    line,
    rows: list[dict],
    visible_start: int,
    visible_end: int,
) -> dict | None:
    begin = line.get_begin_klu()
    end = line.get_end_klu()
    if end.idx < visible_start or begin.idx > visible_end:
        return None
    return {
        "direction": "up" if line.is_up() else "down",
        "start_date": _date(rows, _clip(begin.idx, visible_start, visible_end)),
        "start_price": (
            float(rows[visible_start]["close"])
            if begin.idx < visible_start
            else float(line.get_begin_val())
        ),
        "actual_start_date": _date(rows, begin.idx),
        "actual_start_price": float(line.get_begin_val()),
        "end_date": _date(rows, _clip(end.idx, visible_start, visible_end)),
        "end_price": (
            float(rows[visible_end]["close"])
            if end.idx > visible_end
            else float(line.get_end_val())
        ),
        "actual_end_date": _date(rows, end.idx),
        "actual_end_price": float(line.get_end_val()),
        "confirm_date": _date(rows, end.idx) if bool(line.is_sure) else None,
        "pending": not bool(line.is_sure),
    }


def _zs_overlay(
    zs,
    *,
    level: int,
    label: str,
    rows: list[dict],
    visible_start: int,
    visible_end: int,
) -> dict | None:
    start_index = int(zs.begin.idx)
    end_index = int(zs.end.idx)
    if end_index < visible_start or start_index > visible_end:
        return None
    return {
        "level": level,
        "level_label": label,
        "canonical": True,
        "start_date": _date(rows, _clip(start_index, visible_start, visible_end)),
        "end_date": _date(rows, _clip(end_index, visible_start, visible_end)),
        "actual_start_date": _date(rows, start_index),
        "actual_end_date": _date(rows, end_index),
        "confirm_date": _date(rows, end_index) if bool(zs.is_sure) else None,
        "ZG": float(zs.high),
        "ZD": float(zs.low),
        "GG": float(zs.peak_high),
        "DD": float(zs.peak_low),
        "count": int(zs.end_bi.idx - zs.begin_bi.idx + 1),
        "pending": not bool(zs.is_sure),
        "upgraded": level > 0,
    }


def _signal_rows(
    bsp_list,
    *,
    level: int,
    level_label: str,
    rows: list[dict],
) -> list[dict]:
    out: list[dict] = []
    for point in bsp_list.getSortedBspList():
        index = int(point.klu.idx)
        side = "B" if bool(point.is_buy) else "S"
        price = float(point.klu.low if point.is_buy else point.klu.high)
        sure = bool(point.bi.is_sure)
        for bsp_type in point.type:
            suffix = _TYPE_SUFFIX[str(bsp_type.value)]
            kind = f"{side}{suffix}"
            rule_id = f"CHAN_{kind}"
            out.append(
                {
                    "level": level,
                    "level_label": level_label,
                    "canonical_level": True,
                    "kind": kind,
                    "rule_id": rule_id,
                    "anchor_index": index,
                    "anchor_date": _date(rows, index),
                    "confirm_index": index if sure else None,
                    "confirm_date": _date(rows, index) if sure else None,
                    "price": price,
                    "status": "SURE" if sure else "VIRTUAL_CURRENT_FRAME",
                    "note": (
                        "chan.py 已确认结构买卖点"
                        if sure
                        else "chan.py 当前帧虚结构买卖点；后续 K 线可能调整或消失"
                    ),
                }
            )
    return out


def _dedupe_endpoints(kl, rows: list[dict], visible_start: int) -> list[dict]:
    points: dict[tuple[int, str], dict] = {}
    for bi in kl.bi_list:
        begin = bi.get_begin_klu()
        end = bi.get_end_klu()
        begin_type = "bottom" if bi.is_up() else "top"
        end_type = "top" if bi.is_up() else "bottom"
        for klu, kind, price in (
            (begin, begin_type, bi.get_begin_val()),
            (end, end_type, bi.get_end_val()),
        ):
            if int(klu.idx) < visible_start:
                continue
            points[(int(klu.idx), kind)] = {
                "type": kind,
                "anchor_date": _date(rows, klu.idx),
                "confirm_date": _date(rows, klu.idx) if bool(bi.is_sure) else None,
                "price": float(price),
                "sure": bool(bi.is_sure),
            }
    return [points[k] for k in sorted(points)]


def analyze_chan(
    symbol: str,
    candles: Iterable[dict],
    *,
    display_limit: int = 300,
    timeframe: str = "1d",
) -> dict:
    rows = _validate_candles(candles)
    chan = _build_upstream(symbol, rows)
    kl = chan[0]

    limit = max(80, min(int(display_limit), 500))
    visible_start = max(0, len(rows) - limit)
    visible_end = len(rows) - 1

    chart = [
        {
            **row,
            "state": "OTHER",
            "state_zh": "chan.py 当前帧",
            "position": 0.0,
            "risk_armed": False,
        }
        for row in rows[visible_start:]
    ]

    endpoints = _dedupe_endpoints(kl, rows, visible_start)

    bis_overlay = []
    for bi in kl.bi_list:
        item = _line_overlay(bi, rows, visible_start, visible_end)
        if item is not None:
            bis_overlay.append(item)

    segments_overlay = []
    for seg in kl.seg_list:
        item = _line_overlay(seg, rows, visible_start, visible_end)
        if item is not None:
            item["count"] = int(seg.cal_bi_cnt())
            segments_overlay.append(item)

    zhongshu_overlay = []
    for zs in kl.zs_list:
        item = _zs_overlay(
            zs,
            level=0,
            label="L0 笔级",
            rows=rows,
            visible_start=visible_start,
            visible_end=visible_end,
        )
        if item is not None:
            zhongshu_overlay.append(item)
    for zs in kl.segzs_list:
        item = _zs_overlay(
            zs,
            level=1,
            label="L1 线段级",
            rows=rows,
            visible_start=visible_start,
            visible_end=visible_end,
        )
        if item is not None:
            zhongshu_overlay.append(item)

    all_signals = _signal_rows(
        kl.bs_point_lst,
        level=0,
        level_label="L0 笔级",
        rows=rows,
    )
    all_signals += _signal_rows(
        kl.seg_bs_point_lst,
        level=1,
        level_label="L1 线段级",
        rows=rows,
    )
    all_signals.sort(
        key=lambda x: (
            int(x["anchor_index"]),
            int(x["level"]),
            str(x["kind"]),
        )
    )
    signal_overlay = [
        x for x in all_signals
        if int(x["anchor_index"]) >= visible_start
    ]

    events = []
    for signal in all_signals[-100:]:
        action = "BUY" if signal["kind"].startswith("B") else "SELL"
        events.append(
            {
                "date": signal["anchor_date"],
                "state": "OTHER",
                "state_zh": f"{signal['kind']} · {signal['level_label']}",
                "age": signal["status"],
                "origin": signal["level_label"],
                "action": action,
                "action_zh": ACTION_NAMES_ZH[action],
                "rule_ids": [signal["rule_id"]],
                "rule_names_zh": [
                    CHAN_RULE_NAMES_ZH.get(signal["rule_id"], signal["kind"])
                ],
                "execution_date": None,
                "execution_price": None,
                "position_after": None,
                "risk_after": signal["status"],
                "note": signal["note"],
            }
        )

    last_signal = all_signals[-1] if all_signals else None
    latest_signal = (
        last_signal
        if last_signal and int(last_signal["anchor_index"]) == visible_end
        else None
    )
    resolved_action = (
        "BUY"
        if latest_signal and latest_signal["kind"].startswith("B")
        else "SELL"
        if latest_signal and latest_signal["kind"].startswith("S")
        else "NONE"
    )

    last_bi = kl.bi_list[-1] if len(kl.bi_list) else None
    last_seg = kl.seg_list[-1] if len(kl.seg_list) else None
    last_zs = kl.zs_list[-1] if len(kl.zs_list) else None

    if last_seg is not None:
        current_structure = (
            ("向上线段" if last_seg.is_up() else "向下线段")
            + (" · 已确认" if last_seg.is_sure else " · 虚段")
        )
    elif last_bi is not None:
        current_structure = (
            ("向上笔" if last_bi.is_up() else "向下笔")
            + (" · 已确认" if last_bi.is_sure else " · 虚笔")
        )
    else:
        current_structure = "结构形成中"

    latest = rows[-1]
    sure_segments = sum(1 for x in kl.seg_list if x.is_sure)
    virtual_segments = len(kl.seg_list) - sure_segments

    return {
        "strategy": {
            "id": CHAN_STRATEGY_ID,
            "selector_label": "缠论",
            "version": CHAN_STRATEGY_VERSION,
            "source_commit": CHAN_SOURCE,
            "upstream_sha": CHANPY_UPSTREAM_SHA,
            "active_rule_count": sum(len(x) for x in CHAN_RULES.values()),
            "active_rules": CHAN_RULES,
            "active_rules_zh": {
                group: [CHAN_RULE_NAMES_ZH[x] for x in ids]
                for group, ids in CHAN_RULES.items()
            },
            "position_policy": "CHANPY_CURRENT_FRAME_SIGNAL_ONLY",
            "position_policy_zh": (
                "直接采用 Vespa314/chan.py 原版默认缠论核心；"
                "sure/virtual 结构均按上游当前帧语义显示"
            ),
            "hard_exit": "NONE",
            "hard_exit_zh": "无外部策略退出规则",
            "display_candles": limit,
            "timeframe": str(timeframe),
            "bar_close_contract": "CHANPY_TRIGGER_LOAD_COMPLETED_BAR_CURRENT_FRAME",
            "bar_close_contract_zh": (
                "仅喂入已结束 K 线；上游当前帧虚结构/买卖点可能随后续 K 线调整或消失"
            ),
            "rules_title_zh": "chan.py · 买卖点",
            "policy_title_zh": "Vespa314/chan.py 上游核心",
            "summary_state_label_zh": "当前缠论结构",
            "policy_steps_zh": [
                "① SiftAlpha 只提供已结束 OHLCV，不改上游缠论公式",
                "② 原版包含处理 / 分型 / 笔 / 线段 / 中枢",
                "③ 原版 1 / 1p / 2 / 2s / 3a / 3b 买卖点全部保留",
                "④ 同时保留 sure（已确认）与 virtual（当前虚结构）",
                "⑤ 图上 B/S 是 chan.py 当前帧输出；虚结构信号未来允许调整或消失",
                f"⑥ 上游固定 commit：{CHANPY_UPSTREAM_SHA[:12]}",
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
            "resolved_action": resolved_action,
            "resolved_action_zh": ACTION_NAMES_ZH[resolved_action],
            "rule_ids": [latest_signal["rule_id"]] if latest_signal else [],
            "rule_names_zh": (
                [CHAN_RULE_NAMES_ZH.get(latest_signal["rule_id"], latest_signal["kind"])]
                if latest_signal
                else []
            ),
            "position_fraction": 0.0,
            "risk_state": "NORMAL",
            "risk_state_zh": current_structure,
            "risk_sub_zh": "Vespa314/chan.py 原版默认配置 · 与 V7/E/5s/顺势隔离",
            "next_action": (
                f"当前最后一根出现 {latest_signal['kind']}；"
                f"状态为 {latest_signal['status']}。"
                if latest_signal
                else "等待 chan.py 当前帧产生新的买卖点。"
            ),
            "chan_bi": (
                (
                    "向上笔" if last_bi.is_up() else "向下笔"
                )
                + (" · 已确认" if last_bi.is_sure else " · 虚笔")
                if last_bi
                else "尚未形成"
            ),
            "chan_segment": (
                (
                    "向上线段" if last_seg.is_up() else "向下线段"
                )
                + (" · 已确认" if last_seg.is_sure else " · 虚段")
                if last_seg
                else "尚未形成"
            ),
            "chan_zhongshu": (
                f"L0 · ZG {float(last_zs.high):.3f} / ZD {float(last_zs.low):.3f}"
                if last_zs
                else "当前无中枢"
            ),
            "chan_last_signal": (
                f"{last_signal['kind']} · {last_signal['level_label']} · "
                f"{last_signal['anchor_date']} · {last_signal['status']}"
                if last_signal
                else "暂无"
            ),
        },
        "chart": chart,
        "markers": [],
        "events": events,
        "chan": {
            "engine": "Vespa314/chan.py",
            "upstream_sha": CHANPY_UPSTREAM_SHA,
            "endpoints": endpoints,
            "bis": bis_overlay,
            "segments": segments_overlay,
            "zhongshus": zhongshu_overlay,
            "trends": [],
            "signals": signal_overlay,
            "levels": [
                {
                    "level": 0,
                    "label": "L0 笔级",
                    "canonical": True,
                    "units": len(kl.bi_list),
                    "zhongshus": len(kl.zs_list),
                    "signals": len(kl.bs_point_lst),
                },
                {
                    "level": 1,
                    "label": "L1 线段级",
                    "canonical": True,
                    "units": len(kl.seg_list),
                    "zhongshus": len(kl.segzs_list),
                    "signals": len(kl.seg_bs_point_lst),
                },
            ],
            "counts": {
                "raw_bars_total": len(rows),
                "analysis_bars": len(rows),
                "bi_endpoints": len(endpoints),
                "bis": len(kl.bi_list),
                "sure_bis": sum(1 for x in kl.bi_list if x.is_sure),
                "segments": len(kl.seg_list),
                "sure_segments": sure_segments,
                "virtual_segments": virtual_segments,
                "zhongshus": len(kl.zs_list),
                "segment_zhongshus": len(kl.segzs_list),
                "bi_level_bsp": len(kl.bs_point_lst),
                "segment_level_bsp": len(kl.seg_bs_point_lst),
                "signal_type_memberships": len(all_signals),
            },
            "display_contract_zh": (
                "直接显示 chan.py 当前帧结构：实线/实结构为 sure，虚线/虚结构为 virtual；"
                "B/S 锚点来自上游 BSP，virtual 信号后续允许变化。"
            ),
        },
    }
