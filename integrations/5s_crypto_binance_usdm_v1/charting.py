from __future__ import annotations

from typing import Any, Iterable


DISPLAY_KLINE_LIMIT = 1000


def normalize_chart_klines(rows: Iterable[Any]) -> list[dict[str, float | int]]:
    out: list[dict[str, float | int]] = []
    for row in rows:
        if not isinstance(row, (list, tuple)) or len(row) < 6:
            continue
        try:
            out.append(
                {
                    "open_time": int(row[0]),
                    "open": float(row[1]),
                    "high": float(row[2]),
                    "low": float(row[3]),
                    "close": float(row[4]),
                    "volume": float(row[5]),
                }
            )
        except (TypeError, ValueError):
            continue
    return out[-DISPLAY_KLINE_LIMIT:]
