#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
APP = ROOT / "integrations" / "sltd_v7_siftalpha_v1"
sys.path.insert(0, str(APP))

import data_provider
import strategy

OUT_JSON = Path(__file__).with_name("SLTD_V7_ABT_4H_SELL_AUDIT_v1.json")
OUT_MD = Path(__file__).with_name("SLTD_V7_ABT_4H_SELL_AUDIT_v1.md")


def deleted_sell_hits(row: dict) -> list[str]:
    hits = []
    if (
        row["color"] == "GRAY"
        and row.get("origin") == "BLUE"
        and int(row["run_age"]) <= 5
        and bool(row.get("light_resist"))
    ):
        hits.append("SELL_RECENT_BLUE_GRAY_LIGHT_RESIST")
    if (
        row["color"] == "GREEN"
        and 11 <= int(row["run_age"]) <= 20
        and bool(row.get("upper"))
        and row.get("upper_subtype") == "WICK_ONLY"
    ):
        hits.append("NEW_V5_D_GREEN_11_20_UPPER_WICK_ONLY")
    return hits


def row_summary(row: dict) -> dict:
    return {
        "date": row["date"],
        "close": row["close"],
        "state": row["color"],
        "run_age": row["run_age"],
        "origin": row.get("origin"),
        "upper": row.get("upper"),
        "upper_subtype": row.get("upper_subtype"),
        "lower": row.get("lower"),
        "lower_subtype": row.get("lower_subtype"),
        "light_resist": row.get("light_resist"),
        "light_support": row.get("light_support"),
        "active_BUY": list(row.get("BUY") or []),
        "active_HOLD": list(row.get("HOLD") or []),
        "active_WAIT": list(row.get("WAIT") or []),
        "active_SELL": list(row.get("SELL") or []),
        "deleted_sell_hits": deleted_sell_hits(row),
        "c2_condition": strategy.c2_condition(row),
    }


def main() -> None:
    bars, forming, meta = data_provider.fetch_bars("ABT", "4h", force_refresh=True)
    ledger = strategy.build_ledger(bars, "ABT")
    sim = strategy.simulate_policy(bars, ledger, friction_bps=5.0)

    markers = sim["markers"]
    last_buy = next((m for m in reversed(markers) if m["side"] == "B"), None)
    if last_buy is None:
        raise RuntimeError("ABT 4h has no executed BUY marker")

    date_to_index = {row["date"]: i for i, row in enumerate(ledger)}
    buy_signal_i = date_to_index[last_buy["signal_date"]]
    start_i = max(0, buy_signal_i - 80)
    window_rows = ledger[start_i : buy_signal_i + 1]

    ignored_resistance = []
    for row in window_rows:
        if row.get("SELL"):
            continue
        if row.get("upper") or row.get("light_resist"):
            ignored_resistance.append(row_summary(row))

    deleted_hits = []
    for row in window_rows:
        if deleted_sell_hits(row):
            deleted_hits.append(row_summary(row))

    active_sell_rows = [row_summary(r) for r in window_rows if r.get("SELL")]

    payload = {
        "symbol": "ABT",
        "timeframe": "4h",
        "market_meta": meta,
        "completed_bars": len(bars),
        "forming_bar": forming,
        "last_buy_marker": last_buy,
        "recent_markers": markers[-20:],
        "audit_window": {
            "start": window_rows[0]["date"],
            "end": window_rows[-1]["date"],
            "bars": len(window_rows),
        },
        "active_sell_rows_before_last_buy": active_sell_rows,
        "deleted_v6_sell_rule_hits_before_last_buy": deleted_hits,
        "ignored_upper_or_light_resist_before_last_buy": ignored_resistance,
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# SLTD V7 ABT 4小时卖出审计 v1",
        "",
        f"- 已完成4小时K线: {len(bars)}",
        f"- 审计窗口: {payload['audit_window']['start']} -> {payload['audit_window']['end']} ({payload['audit_window']['bars']} bars)",
        f"- 最后一次买入信号: {last_buy['signal_date']}",
        f"- 最后一次买入执行: {last_buy['execution_date']}",
        f"- 最后一次买入规则: {', '.join(last_buy['rule_names_zh'])}",
        f"- 买入后仓位: {last_buy['position_after']:.4f}",
        "",
        "## 该次买入前，当前V7有效SELL",
        f"- count: {len(active_sell_rows)}",
    ]
    for r in active_sell_rows:
        lines.append(f"- {r['date']} | {r['state']} age={r['run_age']} | {r['active_SELL']}")
    lines += [
        "",
        "## 该次买入前，被V7删除的V6卖出规则命中",
        f"- count: {len(deleted_hits)}",
    ]
    for r in deleted_hits:
        lines.append(f"- {r['date']} | {r['state']} age={r['run_age']} | {r['deleted_sell_hits']}")
    lines += [
        "",
        "## 该次买入前，上轨/轻阻力出现但当前V7没有SELL",
        f"- count: {len(ignored_resistance)}",
    ]
    for r in ignored_resistance[-20:]:
        lines.append(
            f"- {r['date']} | {r['state']} age={r['run_age']} | "
            f"upper={r['upper']} {r['upper_subtype']} | light_resist={r['light_resist']}"
        )
    lines += ["", "## 最近执行标记"]
    for m in markers[-20:]:
        lines.append(
            f"- {m['execution_date']} | {m['side']} | signal={m['signal_date']} | "
            f"rules={m['rule_names_zh']} | pos={m['position_after']:.4f} | risk={m['risk_after']}"
        )

    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(OUT_MD.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
