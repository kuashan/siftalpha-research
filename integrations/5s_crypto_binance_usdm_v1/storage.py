from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable


class StateStore:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS app_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS symbol_settings (
                    symbol TEXT PRIMARY KEY,
                    requested_leverage INTEGER NOT NULL,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS runtime_state (
                    symbol TEXT PRIMARY KEY,
                    last_closed_bar_open_time INTEGER,
                    current_fraction REAL NOT NULL DEFAULT 0,
                    c_confirmed INTEGER NOT NULL DEFAULT 0,
                    pending_action TEXT,
                    last_signal TEXT,
                    last_order_id TEXT,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS audit_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    event_type TEXT NOT NULL,
                    symbol TEXT,
                    detail TEXT NOT NULL
                );
                """
            )

    def seed(self, symbols: Iterable[str], default_leverage: int, default_budget: float) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO app_settings(key, value) VALUES('capital_budget_usdt', ?)",
                (str(default_budget),),
            )
            for symbol in symbols:
                conn.execute(
                    "INSERT OR IGNORE INTO symbol_settings(symbol, requested_leverage) VALUES(?, ?)",
                    (symbol, default_leverage),
                )
                conn.execute(
                    "INSERT OR IGNORE INTO runtime_state(symbol) VALUES(?)",
                    (symbol,),
                )

    def get_budget(self) -> float:
        with self._connect() as conn:
            row = conn.execute("SELECT value FROM app_settings WHERE key='capital_budget_usdt'").fetchone()
            return float(row[0]) if row else 0.0

    def set_budget(self, value: float) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO app_settings(key, value) VALUES('capital_budget_usdt', ?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (str(value),),
            )
            conn.execute(
                "INSERT INTO audit_events(event_type, detail) VALUES('SET_BUDGET', ?)",
                (f"capital_budget_usdt={value}",),
            )

    def get_leverages(self) -> dict[str, int]:
        with self._connect() as conn:
            rows = conn.execute("SELECT symbol, requested_leverage FROM symbol_settings ORDER BY symbol").fetchall()
            return {str(r["symbol"]): int(r["requested_leverage"]) for r in rows}

    def set_leverage(self, symbol: str, leverage: int) -> None:
        with self._connect() as conn:
            conn.execute(
                "UPDATE symbol_settings SET requested_leverage=?, updated_at=CURRENT_TIMESTAMP WHERE symbol=?",
                (leverage, symbol),
            )
            conn.execute(
                "INSERT INTO audit_events(event_type, symbol, detail) VALUES('SET_LEVERAGE', ?, ?)",
                (symbol, f"requested_leverage={leverage}"),
            )
