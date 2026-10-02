from __future__ import annotations

from datetime import date, timedelta
import json
import math
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from strategy.frozen_signal_engine import evaluate_candles


def fixture_rows(count: int = 280):
    rows = []
    previous_close = 100.0
    start = date(2024, 1, 1)
    for i in range(count):
        trend = 0.10 * i if i < 115 else (11.5 - 0.055 * (i - 115) if i < 205 else 6.55 + 0.14 * (i - 205))
        wave = 7.5 * math.sin(i / 7.1) + 3.2 * math.sin(i / 2.65)
        close = max(8.0, 100.0 + trend + wave)
        open_price = previous_close * (1.0 + 0.008 * math.sin(i * 1.37))
        spread = 0.008 + 0.014 * abs(math.sin(i / 5.3))
        high = max(open_price, close) * (1.0 + spread)
        low = min(open_price, close) * (1.0 - spread * 0.92)
        volume = 1200.0 * (1.0 + 0.42 * math.sin(i / 4.7) + 0.22 * math.cos(i / 11.0))
        if i % 19 == 0:
            volume *= 2.7
        if i % 31 == 0:
            volume *= 0.42
        volume = max(50.0, volume)
        rows.append({
            "date": (start + timedelta(days=i)).isoformat(),
            "open_time": i,
            "open": open_price,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
        })
        previous_close = close
    return rows


class FrozenSignalParityTests(unittest.TestCase):
    def test_python_matches_frozen_javascript_bar_by_bar(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("node is required for frozen JS parity audit")

        rows = fixture_rows()
        here = Path(__file__).resolve().parent
        runner = here / "js_frozen_signal_parity_runner.js"

        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "fixture.csv"
            lines = ["Date,Open,High,Low,Close,Volume"]
            for r in rows:
                lines.append(
                    f"{r['date']},{r['open']:.12f},{r['high']:.12f},{r['low']:.12f},{r['close']:.12f},{r['volume']:.12f}"
                )
            csv_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

            # Parse the exact serialized numbers in Python too, eliminating
            # fixture formatting as a possible source of parity drift.
            normalized = []
            for i, line in enumerate(lines[1:]):
                d, o, h, l, c, v = line.split(",")
                normalized.append({
                    "open_time": i,
                    "open": float(o),
                    "high": float(h),
                    "low": float(l),
                    "close": float(c),
                    "volume": float(v),
                })

            proc = subprocess.run(
                [node, str(runner), str(csv_path)],
                check=True,
                capture_output=True,
                text=True,
            )
            js = json.loads(proc.stdout)

        py = evaluate_candles(normalized)
        self.assertEqual(len(js), len(py))

        signal_events = 0
        for expected, actual in zip(js, py):
            self.assertEqual(expected["states"], actual.states, f"state drift at {actual.index}")
            self.assertEqual(expected["buyActive"], list(actual.buy_active), f"BUY active drift at {actual.index}")
            self.assertEqual(expected["sellActive"], list(actual.sell_active), f"SELL active drift at {actual.index}")
            self.assertEqual(expected["buyOnsets"], list(actual.buy_onsets), f"BUY onset drift at {actual.index}")
            self.assertEqual(expected["sellOnsets"], list(actual.sell_onsets), f"SELL onset drift at {actual.index}")
            signal_events += len(actual.buy_onsets) + len(actual.sell_onsets)

        self.assertGreater(signal_events, 0, "fixture must exercise at least one frozen signal onset")


if __name__ == "__main__":
    unittest.main()
