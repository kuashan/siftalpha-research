import sqlite3
import tempfile
import unittest
from pathlib import Path

from storage import StateStore


class StorageTests(unittest.TestCase):
    def test_independent_symbol_settings_survive_reopen(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "state.db"
            s = StateStore(path)
            s.seed(["BTCUSDT", "BNBUSDT"], 1, 1000, "1d")
            s.set_symbol_config("BTCUSDT", capital_budget_usdt=100, leverage=5, timeframe="4h")
            s.set_symbol_config("BNBUSDT", capital_budget_usdt=80, leverage=2, timeframe="1h")
            s.set_symbol_enabled("BTCUSDT", True)

            s2 = StateStore(path)
            cfg = s2.get_symbol_configs()
            self.assertEqual(cfg["BTCUSDT"]["capital_budget_usdt"], 100)
            self.assertEqual(cfg["BTCUSDT"]["leverage"], 5)
            self.assertEqual(cfg["BTCUSDT"]["timeframe"], "4h")
            self.assertTrue(cfg["BTCUSDT"]["enabled"])
            self.assertEqual(cfg["BNBUSDT"]["capital_budget_usdt"], 80)
            self.assertFalse(cfg["BNBUSDT"]["enabled"])

    def test_pnl_is_independent_and_has_total(self):
        with tempfile.TemporaryDirectory() as td:
            s = StateStore(Path(td) / "state.db")
            s.seed(["BTCUSDT", "BNBUSDT"], 1, 1000, "1d")
            s.set_pnl("BTCUSDT", realized_pnl=10, unrealized_pnl=2, funding_fee=-0.5, trading_fee=0.3)
            s.set_pnl("BNBUSDT", realized_pnl=-3, unrealized_pnl=1, funding_fee=0.2, trading_fee=0.1)
            pnl = s.get_pnl()
            self.assertAlmostEqual(pnl["BTCUSDT"]["total_pnl"], 11.2)
            self.assertAlmostEqual(pnl["BNBUSDT"]["total_pnl"], -1.9)
            self.assertAlmostEqual(s.pnl_summary()["total_pnl"], 9.3)

    def test_recent_audit_filters_and_returns_latest_first(self):
        with tempfile.TemporaryDirectory() as td:
            s = StateStore(Path(td) / "state.db")
            s.seed(["BTCUSDT"], 1, 1000, "1d")
            s.append_audit("SSSS_BAR_DECISION", "BTCUSDT", "decision=HOLD")
            s.append_audit("SCHEDULER_ERROR", "BTCUSDT", "RuntimeError:test failure")
            s.append_audit("SSSS_BAR_EXECUTION", "BTCUSDT", "status=ERROR")
            rows = s.recent_audit(
                "BTCUSDT",
                event_types=("SCHEDULER_ERROR", "SSSS_BAR_EXECUTION"),
                limit=10,
            )
            self.assertEqual([row["event_type"] for row in rows], [
                "SSSS_BAR_EXECUTION",
                "SCHEDULER_ERROR",
            ])
            self.assertIn("test failure", rows[1]["detail"])

    def test_legacy_global_values_migrate_to_existing_symbol(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "legacy.db"
            conn = sqlite3.connect(path)
            conn.executescript("""
            CREATE TABLE app_settings(key TEXT PRIMARY KEY, value TEXT NOT NULL);
            INSERT INTO app_settings VALUES('capital_budget_usdt','250');
            INSERT INTO app_settings VALUES('timeframe','6h');
            CREATE TABLE symbol_settings(symbol TEXT PRIMARY KEY, requested_leverage INTEGER NOT NULL, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
            INSERT INTO symbol_settings(symbol, requested_leverage) VALUES('BTCUSDT', 7);
            CREATE TABLE runtime_state(symbol TEXT PRIMARY KEY, last_closed_bar_open_time INTEGER, current_fraction REAL NOT NULL DEFAULT 0, c_confirmed INTEGER NOT NULL DEFAULT 0, pending_action TEXT, last_signal TEXT, last_order_id TEXT, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
            INSERT INTO runtime_state(symbol) VALUES('BTCUSDT');
            CREATE TABLE audit_events(id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, event_type TEXT NOT NULL, symbol TEXT, detail TEXT NOT NULL);
            """)
            conn.commit()
            conn.close()

            s = StateStore(path)
            s.seed(["BTCUSDT"], 1, 1000, "1d")
            cfg = s.get_symbol_configs()["BTCUSDT"]
            self.assertEqual(cfg["leverage"], 7)
            self.assertEqual(cfg["capital_budget_usdt"], 250)
            self.assertEqual(cfg["timeframe"], "6h")


if __name__ == "__main__":
    unittest.main()
