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

    @staticmethod
    def _columns(conn: sqlite3.Connection, table: str) -> set[str]:
        return {str(r[1]) for r in conn.execute(f"PRAGMA table_info({table})").fetchall()}

    def _ensure_column(self, conn: sqlite3.Connection, table: str, column: str, ddl: str) -> None:
        if column not in self._columns(conn, table):
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}")

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

                CREATE TABLE IF NOT EXISTS symbol_pnl (
                    symbol TEXT PRIMARY KEY,
                    realized_pnl REAL NOT NULL DEFAULT 0,
                    unrealized_pnl REAL NOT NULL DEFAULT 0,
                    funding_fee REAL NOT NULL DEFAULT 0,
                    trading_fee REAL NOT NULL DEFAULT 0,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    client_order_id TEXT NOT NULL,
                    binance_order_id TEXT,
                    side TEXT NOT NULL,
                    quantity REAL,
                    price REAL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(symbol, client_order_id)
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

            old_symbol_columns = self._columns(conn, "symbol_settings")
            old_runtime_columns = self._columns(conn, "runtime_state")
            self._ensure_column(conn, "symbol_settings", "capital_budget_usdt", "REAL NOT NULL DEFAULT 1000")
            self._ensure_column(conn, "symbol_settings", "timeframe", "TEXT NOT NULL DEFAULT '1d'")
            self._ensure_column(conn, "symbol_settings", "enabled", "INTEGER NOT NULL DEFAULT 0")
            self._ensure_column(conn, "runtime_state", "run_state", "TEXT NOT NULL DEFAULT 'STOPPED'")
            self._ensure_column(conn, "runtime_state", "entry_signal_open_time", "INTEGER")
            self._ensure_column(conn, "runtime_state", "entry_family", "TEXT")
            self._ensure_column(conn, "runtime_state", "accounting_start_time_ms", "INTEGER")

            if "capital_budget_usdt" not in old_symbol_columns:
                row = conn.execute("SELECT value FROM app_settings WHERE key='capital_budget_usdt'").fetchone()
                if row:
                    conn.execute("UPDATE symbol_settings SET capital_budget_usdt=?", (float(row[0]),))
            if "timeframe" not in old_symbol_columns:
                row = conn.execute("SELECT value FROM app_settings WHERE key='timeframe'").fetchone()
                if row:
                    conn.execute("UPDATE symbol_settings SET timeframe=?", (str(row[0]),))
            if "run_state" not in old_runtime_columns:
                conn.execute("UPDATE runtime_state SET run_state='STOPPED'")

    def seed(
        self,
        symbols: Iterable[str],
        default_leverage: int,
        default_budget: float,
        default_timeframe: str = "1d",
    ) -> None:
        with self._connect() as conn:
            for symbol in symbols:
                conn.execute(
                    """
                    INSERT OR IGNORE INTO symbol_settings(
                        symbol, requested_leverage, capital_budget_usdt, timeframe, enabled
                    ) VALUES(?, ?, ?, ?, 0)
                    """,
                    (symbol, default_leverage, default_budget, default_timeframe),
                )
                conn.execute(
                    "INSERT OR IGNORE INTO runtime_state(symbol, run_state) VALUES(?, 'STOPPED')",
                    (symbol,),
                )
                conn.execute("INSERT OR IGNORE INTO symbol_pnl(symbol) VALUES(?)", (symbol,))

    def get_symbol_configs(self) -> dict[str, dict[str, object]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT symbol, requested_leverage, capital_budget_usdt, timeframe, enabled
                FROM symbol_settings ORDER BY symbol
                """
            ).fetchall()
            return {
                str(r["symbol"]): {
                    "symbol": str(r["symbol"]),
                    "leverage": int(r["requested_leverage"]),
                    "capital_budget_usdt": float(r["capital_budget_usdt"]),
                    "timeframe": str(r["timeframe"]),
                    "enabled": bool(r["enabled"]),
                }
                for r in rows
            }

    def set_symbol_config(self, symbol: str, *, capital_budget_usdt: float, leverage: int, timeframe: str) -> None:
        with self._connect() as conn:
            cur = conn.execute(
                """
                UPDATE symbol_settings
                SET capital_budget_usdt=?, requested_leverage=?, timeframe=?, updated_at=CURRENT_TIMESTAMP
                WHERE symbol=?
                """,
                (float(capital_budget_usdt), int(leverage), timeframe, symbol),
            )
            if cur.rowcount != 1:
                raise KeyError(f"unknown symbol: {symbol}")
            conn.execute(
                "INSERT INTO audit_events(event_type, symbol, detail) VALUES('SET_SYMBOL_CONFIG', ?, ?)",
                (symbol, f"budget={capital_budget_usdt};leverage={leverage};timeframe={timeframe}"),
            )

    def set_symbol_enabled(self, symbol: str, enabled: bool) -> None:
        run_state = "ARMED" if enabled else "STOPPED"
        with self._connect() as conn:
            cur = conn.execute(
                "UPDATE symbol_settings SET enabled=?, updated_at=CURRENT_TIMESTAMP WHERE symbol=?",
                (1 if enabled else 0, symbol),
            )
            if cur.rowcount != 1:
                raise KeyError(f"unknown symbol: {symbol}")
            conn.execute(
                "UPDATE runtime_state SET run_state=?, updated_at=CURRENT_TIMESTAMP WHERE symbol=?",
                (run_state, symbol),
            )
            conn.execute(
                "INSERT INTO audit_events(event_type, symbol, detail) VALUES(?, ?, ?)",
                ("START_SYMBOL" if enabled else "STOP_SYMBOL", symbol, f"run_state={run_state}"),
            )

    def get_runtime_states(self) -> dict[str, dict[str, object]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT symbol, last_closed_bar_open_time, current_fraction, c_confirmed,
                       pending_action, last_signal, last_order_id, run_state,
                       entry_signal_open_time, entry_family, accounting_start_time_ms
                FROM runtime_state ORDER BY symbol
                """
            ).fetchall()
            return {str(r["symbol"]): dict(r) for r in rows}

    def set_run_state(self, symbol: str, run_state: str) -> None:
        with self._connect() as conn:
            cur = conn.execute(
                "UPDATE runtime_state SET run_state=?, updated_at=CURRENT_TIMESTAMP WHERE symbol=?",
                (str(run_state), symbol),
            )
            if cur.rowcount != 1:
                raise KeyError(f"unknown symbol: {symbol}")

    def baseline_closed_bar(self, symbol: str, bar_open_time: int) -> None:
        with self._connect() as conn:
            cur = conn.execute(
                """
                UPDATE runtime_state
                SET last_closed_bar_open_time=?, pending_action=NULL,
                    run_state='MONITORING', updated_at=CURRENT_TIMESTAMP
                WHERE symbol=?
                """,
                (int(bar_open_time), symbol),
            )
            if cur.rowcount != 1:
                raise KeyError(f"unknown symbol: {symbol}")
            conn.execute(
                "INSERT INTO audit_events(event_type, symbol, detail) VALUES('M3_BASELINE_BAR', ?, ?)",
                (symbol, f"bar_open_time={int(bar_open_time)}"),
            )

    def record_strategy_observation(
        self,
        symbol: str,
        *,
        bar_open_time: int,
        signal: str,
        pending_action: str | None,
        run_state: str | None = None,
    ) -> None:
        run_state = run_state or ("SIGNAL_READY" if pending_action else "MONITORING")
        with self._connect() as conn:
            cur = conn.execute(
                """
                UPDATE runtime_state
                SET last_closed_bar_open_time=?, last_signal=?, pending_action=?,
                    run_state=?, updated_at=CURRENT_TIMESTAMP
                WHERE symbol=?
                """,
                (int(bar_open_time), signal, pending_action, run_state, symbol),
            )
            if cur.rowcount != 1:
                raise KeyError(f"unknown symbol: {symbol}")
            conn.execute(
                "INSERT INTO audit_events(event_type, symbol, detail) VALUES('M3_SIGNAL_BAR', ?, ?)",
                (
                    symbol,
                    f"bar_open_time={int(bar_open_time)};signal={signal};pending={pending_action or 'NONE'}",
                ),
            )

    def set_execution_position_state(
        self,
        symbol: str,
        *,
        current_fraction: float,
        c_confirmed: bool,
        entry_signal_open_time: int | None,
        entry_family: str | None,
        last_order_id: str | None = None,
        run_state: str = "MONITORING",
    ) -> None:
        with self._connect() as conn:
            cur = conn.execute(
                """
                UPDATE runtime_state
                SET current_fraction=?, c_confirmed=?, entry_signal_open_time=?,
                    entry_family=?, last_order_id=?, pending_action=NULL,
                    run_state=?, updated_at=CURRENT_TIMESTAMP
                WHERE symbol=?
                """,
                (
                    float(current_fraction),
                    1 if c_confirmed else 0,
                    entry_signal_open_time,
                    entry_family,
                    last_order_id,
                    run_state,
                    symbol,
                ),
            )
            if cur.rowcount != 1:
                raise KeyError(f"unknown symbol: {symbol}")

    def append_audit(self, event_type: str, symbol: str | None, detail: str) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO audit_events(event_type, symbol, detail) VALUES(?, ?, ?)",
                (event_type, symbol, str(detail)),
            )

    def set_accounting_start_if_missing(self, symbol: str, start_time_ms: int) -> int:
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE runtime_state
                SET accounting_start_time_ms=COALESCE(accounting_start_time_ms, ?),
                    updated_at=CURRENT_TIMESTAMP
                WHERE symbol=?
                """,
                (int(start_time_ms), symbol),
            )
            row = conn.execute(
                "SELECT accounting_start_time_ms FROM runtime_state WHERE symbol=?",
                (symbol,),
            ).fetchone()
            if row is None:
                raise KeyError(f"unknown symbol: {symbol}")
            return int(row[0])

    def begin_order(self, symbol: str, client_order_id: str, *, side: str, quantity: float, price: float) -> bool:
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT OR IGNORE INTO orders(
                    symbol, client_order_id, side, quantity, price, status
                ) VALUES(?, ?, ?, ?, ?, 'PENDING')
                """,
                (symbol, client_order_id, side, float(quantity), float(price)),
            )
            return cur.rowcount == 1

    def get_order(self, symbol: str, client_order_id: str) -> dict[str, object] | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT symbol, client_order_id, binance_order_id, side, quantity, price, status
                FROM orders WHERE symbol=? AND client_order_id=?
                """,
                (symbol, client_order_id),
            ).fetchone()
            return dict(row) if row is not None else None

    def complete_order(
        self,
        symbol: str,
        client_order_id: str,
        *,
        binance_order_id: str,
        status: str,
        quantity: float,
        price: float,
    ) -> None:
        with self._connect() as conn:
            cur = conn.execute(
                """
                UPDATE orders
                SET binance_order_id=?, status=?, quantity=?, price=?, updated_at=CURRENT_TIMESTAMP
                WHERE symbol=? AND client_order_id=?
                """,
                (str(binance_order_id), str(status), float(quantity), float(price), symbol, client_order_id),
            )
            if cur.rowcount != 1:
                raise KeyError(f"unknown order: {symbol}/{client_order_id}")

    def get_pnl(self) -> dict[str, dict[str, float]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT symbol, realized_pnl, unrealized_pnl, funding_fee, trading_fee
                FROM symbol_pnl ORDER BY symbol
                """
            ).fetchall()
            out: dict[str, dict[str, float]] = {}
            for r in rows:
                realized = float(r["realized_pnl"])
                unrealized = float(r["unrealized_pnl"])
                funding = float(r["funding_fee"])
                trading = float(r["trading_fee"])
                out[str(r["symbol"])] = {
                    "realized_pnl": realized,
                    "unrealized_pnl": unrealized,
                    "funding_fee": funding,
                    "trading_fee": trading,
                    "total_pnl": realized + unrealized + funding - trading,
                }
            return out

    def set_pnl(
        self,
        symbol: str,
        *,
        realized_pnl: float,
        unrealized_pnl: float,
        funding_fee: float,
        trading_fee: float,
    ) -> None:
        with self._connect() as conn:
            cur = conn.execute(
                """
                UPDATE symbol_pnl
                SET realized_pnl=?, unrealized_pnl=?, funding_fee=?, trading_fee=?, updated_at=CURRENT_TIMESTAMP
                WHERE symbol=?
                """,
                (realized_pnl, unrealized_pnl, funding_fee, trading_fee, symbol),
            )
            if cur.rowcount != 1:
                raise KeyError(f"unknown symbol: {symbol}")

    def pnl_summary(self) -> dict[str, float]:
        pnl = self.get_pnl()
        return {
            "realized_pnl": sum(x["realized_pnl"] for x in pnl.values()),
            "unrealized_pnl": sum(x["unrealized_pnl"] for x in pnl.values()),
            "funding_fee": sum(x["funding_fee"] for x in pnl.values()),
            "trading_fee": sum(x["trading_fee"] for x in pnl.values()),
            "total_pnl": sum(x["total_pnl"] for x in pnl.values()),
        }

    # Legacy M1/M2 helpers retained temporarily. New code should use per-symbol methods.
    def get_budget(self) -> float:
        configs = self.get_symbol_configs()
        return float(next(iter(configs.values()))["capital_budget_usdt"]) if configs else 0.0

    def set_budget(self, value: float) -> None:
        with self._connect() as conn:
            conn.execute("UPDATE symbol_settings SET capital_budget_usdt=?, updated_at=CURRENT_TIMESTAMP", (float(value),))

    def get_timeframe(self, default: str = "1d") -> str:
        configs = self.get_symbol_configs()
        return str(next(iter(configs.values()))["timeframe"]) if configs else default

    def set_timeframe(self, timeframe: str) -> None:
        with self._connect() as conn:
            conn.execute("UPDATE symbol_settings SET timeframe=?, updated_at=CURRENT_TIMESTAMP", (timeframe,))

    def get_leverages(self) -> dict[str, int]:
        return {symbol: int(cfg["leverage"]) for symbol, cfg in self.get_symbol_configs().items()}

    def set_leverage(self, symbol: str, leverage: int) -> None:
        cfg = self.get_symbol_configs().get(symbol)
        if not cfg:
            raise KeyError(f"unknown symbol: {symbol}")
        self.set_symbol_config(
            symbol,
            capital_budget_usdt=float(cfg["capital_budget_usdt"]),
            leverage=int(leverage),
            timeframe=str(cfg["timeframe"]),
        )
