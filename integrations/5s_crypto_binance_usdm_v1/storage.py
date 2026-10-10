from __future__ import annotations

import json
import sqlite3
from decimal import Decimal
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

                CREATE TABLE IF NOT EXISTS reconciliation_baselines (
                    symbol TEXT NOT NULL,
                    strategy_id TEXT NOT NULL,
                    baseline_position REAL NOT NULL,
                    reason TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY(symbol, strategy_id)
                );

                CREATE TABLE IF NOT EXISTS ssss_signal_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    signal_bar_open_time INTEGER NOT NULL,
                    icon_id INTEGER NOT NULL,
                    first_detected_time TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    last_detected_time TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    detection_bar_open_time INTEGER,
                    status TEXT NOT NULL DEFAULT 'DETECTED',
                    execution_bar_open_time INTEGER,
                    execution_time TEXT,
                    binance_order_id TEXT,
                    result TEXT,
                    UNIQUE(symbol, timeframe, signal_bar_open_time, icon_id)
                );
                """
            )

            old_symbol_columns = self._columns(conn, "symbol_settings")
            old_runtime_columns = self._columns(conn, "runtime_state")
            self._ensure_column(conn, "symbol_settings", "capital_budget_usdt", "REAL NOT NULL DEFAULT 1000")
            self._ensure_column(conn, "symbol_settings", "timeframe", "TEXT NOT NULL DEFAULT '1d'")
            self._ensure_column(conn, "symbol_settings", "enabled", "INTEGER NOT NULL DEFAULT 0")
            self._ensure_column(conn, "symbol_settings", "strategy_id", "TEXT NOT NULL DEFAULT '5s_crypto_v1'")
            self._ensure_column(conn, "runtime_state", "run_state", "TEXT NOT NULL DEFAULT 'STOPPED'")
            self._ensure_column(conn, "runtime_state", "entry_signal_open_time", "INTEGER")
            self._ensure_column(conn, "runtime_state", "entry_family", "TEXT")
            self._ensure_column(conn, "runtime_state", "accounting_start_time_ms", "INTEGER")
            self._ensure_column(conn, "runtime_state", "strategy_state_json", "TEXT NOT NULL DEFAULT '{}'")
            self._ensure_column(conn, "orders", "strategy_id", "TEXT NOT NULL DEFAULT '5s_crypto_v1'")
            self._ensure_column(conn, "orders", "target_fraction_after", "REAL")
            self._ensure_column(conn, "orders", "strategy_state_after_json", "TEXT")
            self._ensure_column(conn, "orders", "signal_bar_open_time", "INTEGER")
            self._ensure_column(conn, "orders", "execution_bar_open_time", "INTEGER")
            self._ensure_column(conn, "orders", "marker_side", "TEXT")
            self._ensure_column(conn, "orders", "strategy_signal", "TEXT")

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
                SELECT symbol, requested_leverage, capital_budget_usdt, timeframe, enabled, strategy_id
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
                    "strategy_id": str(r["strategy_id"] or "5s_crypto_v1"),
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

    def set_symbol_strategy(self, symbol: str, strategy_id: str, timeframe: str) -> None:
        with self._connect() as conn:
            cur = conn.execute(
                """
                UPDATE symbol_settings
                SET strategy_id=?, timeframe=?, enabled=0, updated_at=CURRENT_TIMESTAMP
                WHERE symbol=?
                """,
                (str(strategy_id), str(timeframe), symbol),
            )
            if cur.rowcount != 1:
                raise KeyError(f"unknown symbol: {symbol}")
            conn.execute(
                """
                UPDATE runtime_state
                SET last_closed_bar_open_time=NULL, current_fraction=0, c_confirmed=0,
                    pending_action=NULL, last_signal=NULL, last_order_id=NULL,
                    run_state='STOPPED', entry_signal_open_time=NULL, entry_family=NULL,
                    accounting_start_time_ms=NULL, strategy_state_json='{}',
                    updated_at=CURRENT_TIMESTAMP
                WHERE symbol=?
                """,
                (symbol,),
            )
            conn.execute(
                """
                UPDATE symbol_pnl
                SET realized_pnl=0, unrealized_pnl=0, funding_fee=0, trading_fee=0,
                    updated_at=CURRENT_TIMESTAMP
                WHERE symbol=?
                """,
                (symbol,),
            )
            conn.execute(
                "INSERT INTO audit_events(event_type, symbol, detail) VALUES('SET_SYMBOL_STRATEGY', ?, ?)",
                (symbol, f"strategy={strategy_id};timeframe={timeframe}"),
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

    def get_reconciliation_baseline(self, symbol: str, strategy_id: str) -> Decimal:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT baseline_position
                FROM reconciliation_baselines
                WHERE symbol=? AND strategy_id=?
                """,
                (symbol, str(strategy_id)),
            ).fetchone()
            if row is None:
                return Decimal("0")
            return Decimal(str(row["baseline_position"]))

    def set_reconciliation_baseline(
        self,
        symbol: str,
        strategy_id: str,
        baseline_position: Decimal,
        *,
        reason: str,
    ) -> bool:
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT OR IGNORE INTO reconciliation_baselines(
                    symbol, strategy_id, baseline_position, reason
                ) VALUES(?, ?, ?, ?)
                """,
                (symbol, str(strategy_id), float(baseline_position), str(reason)),
            )
            return cur.rowcount == 1

    def get_runtime_states(self) -> dict[str, dict[str, object]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT symbol, last_closed_bar_open_time, current_fraction, c_confirmed,
                       pending_action, last_signal, last_order_id, run_state,
                       entry_signal_open_time, entry_family, accounting_start_time_ms,
                       strategy_state_json
                FROM runtime_state ORDER BY symbol
                """
            ).fetchall()
            out: dict[str, dict[str, object]] = {}
            for r in rows:
                item = dict(r)
                try:
                    item["strategy_state"] = json.loads(str(item.get("strategy_state_json") or "{}"))
                except Exception:
                    item["strategy_state"] = {}
                out[str(r["symbol"])] = item
            return out

    def set_run_state(self, symbol: str, run_state: str) -> None:
        with self._connect() as conn:
            cur = conn.execute(
                "UPDATE runtime_state SET run_state=?, updated_at=CURRENT_TIMESTAMP WHERE symbol=?",
                (str(run_state), symbol),
            )
            if cur.rowcount != 1:
                raise KeyError(f"unknown symbol: {symbol}")

    def baseline_closed_bar(
        self,
        symbol: str,
        bar_open_time: int,
        *,
        strategy_state: dict[str, object] | None = None,
    ) -> None:
        with self._connect() as conn:
            if strategy_state is None:
                cur = conn.execute(
                    """
                    UPDATE runtime_state
                    SET last_closed_bar_open_time=?, pending_action=NULL,
                        run_state='MONITORING', updated_at=CURRENT_TIMESTAMP
                    WHERE symbol=?
                    """,
                    (int(bar_open_time), symbol),
                )
            else:
                cur = conn.execute(
                    """
                    UPDATE runtime_state
                    SET last_closed_bar_open_time=?, pending_action=NULL,
                        strategy_state_json=?, run_state='MONITORING',
                        updated_at=CURRENT_TIMESTAMP
                    WHERE symbol=?
                    """,
                    (
                        int(bar_open_time),
                        json.dumps(dict(strategy_state), ensure_ascii=False, sort_keys=True),
                        symbol,
                    ),
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
        strategy_id: str = "5s_crypto_v1",
        strategy_state: dict[str, object] | None = None,
    ) -> None:
        run_state = run_state or ("SIGNAL_READY" if pending_action else "MONITORING")
        with self._connect() as conn:
            if strategy_state is None:
                cur = conn.execute(
                    """
                    UPDATE runtime_state
                    SET last_closed_bar_open_time=?, last_signal=?, pending_action=?,
                        run_state=?, updated_at=CURRENT_TIMESTAMP
                    WHERE symbol=?
                    """,
                    (int(bar_open_time), signal, pending_action, run_state, symbol),
                )
            else:
                cur = conn.execute(
                    """
                    UPDATE runtime_state
                    SET last_closed_bar_open_time=?, last_signal=?, pending_action=?,
                        strategy_state_json=?, run_state=?,
                        updated_at=CURRENT_TIMESTAMP
                    WHERE symbol=?
                    """,
                    (
                        int(bar_open_time),
                        signal,
                        pending_action,
                        json.dumps(dict(strategy_state), ensure_ascii=False, sort_keys=True),
                        run_state,
                        symbol,
                    ),
                )
            if cur.rowcount != 1:
                raise KeyError(f"unknown symbol: {symbol}")
            conn.execute(
                "INSERT INTO audit_events(event_type, symbol, detail) VALUES('M3_SIGNAL_BAR', ?, ?)",
                (
                    symbol,
                    f"bar_open_time={int(bar_open_time)};strategy={strategy_id};signal={signal};pending={pending_action or 'NONE'}",
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

    def set_strategy_execution_state(
        self,
        symbol: str,
        *,
        current_fraction: float,
        strategy_state: dict[str, object],
        last_order_id: str | None = None,
        run_state: str = "MONITORING",
    ) -> None:
        state = dict(strategy_state or {})
        c_confirmed = bool(state.get("c_confirmed", False))
        entry_signal = state.get("entry_signal_open_time")
        entry_family = state.get("entry_family")
        with self._connect() as conn:
            cur = conn.execute(
                """
                UPDATE runtime_state
                SET current_fraction=?, c_confirmed=?, entry_signal_open_time=?,
                    entry_family=?, strategy_state_json=?, last_order_id=?,
                    pending_action=NULL, run_state=?, updated_at=CURRENT_TIMESTAMP
                WHERE symbol=?
                """,
                (
                    float(current_fraction),
                    1 if c_confirmed else 0,
                    int(entry_signal) if entry_signal is not None else None,
                    str(entry_family) if entry_family is not None else None,
                    json.dumps(state, ensure_ascii=False, sort_keys=True),
                    last_order_id,
                    str(run_state),
                    symbol,
                ),
            )
            if cur.rowcount != 1:
                raise KeyError(f"unknown symbol: {symbol}")

    def set_recovery_strategy_state(
        self,
        symbol: str,
        *,
        current_fraction: float,
        strategy_state: dict[str, object],
        last_order_id: str | None,
        last_closed_bar_open_time: int | None,
        run_state: str,
    ) -> None:
        state = dict(strategy_state or {})
        c_confirmed = bool(state.get("c_confirmed", False))
        entry_signal = state.get("entry_signal_open_time")
        entry_family = state.get("entry_family")
        with self._connect() as conn:
            cur = conn.execute(
                """
                UPDATE runtime_state
                SET current_fraction=?, c_confirmed=?, entry_signal_open_time=?,
                    entry_family=?, strategy_state_json=?, last_order_id=?,
                    last_closed_bar_open_time=?, pending_action=NULL, run_state=?,
                    updated_at=CURRENT_TIMESTAMP
                WHERE symbol=?
                """,
                (
                    float(current_fraction),
                    1 if c_confirmed else 0,
                    int(entry_signal) if entry_signal is not None else None,
                    str(entry_family) if entry_family is not None else None,
                    json.dumps(state, ensure_ascii=False, sort_keys=True),
                    last_order_id,
                    last_closed_bar_open_time,
                    str(run_state),
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

    def recent_audit(
        self,
        symbol: str,
        *,
        event_types: tuple[str, ...] | None = None,
        limit: int = 20,
    ) -> list[dict[str, object]]:
        safe_limit = min(max(int(limit), 1), 200)
        with self._connect() as conn:
            if event_types:
                placeholders = ",".join("?" for _ in event_types)
                rows = conn.execute(
                    f"""
                    SELECT id, ts, event_type, symbol, detail
                    FROM audit_events
                    WHERE symbol=? AND event_type IN ({placeholders})
                    ORDER BY id DESC
                    LIMIT ?
                    """,
                    (symbol, *event_types, safe_limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT id, ts, event_type, symbol, detail
                    FROM audit_events
                    WHERE symbol=?
                    ORDER BY id DESC
                    LIMIT ?
                    """,
                    (symbol, safe_limit),
                ).fetchall()
            return [dict(row) for row in rows]

    def record_ssss_signal_detection(
        self,
        symbol: str,
        *,
        timeframe: str,
        signal_bar_open_time: int,
        icon_id: int,
        detection_bar_open_time: int,
        status: str = "DETECTED",
    ) -> dict[str, object]:
        """Persist first detection exactly once while refreshing last-seen metadata."""
        tf = str(timeframe).lower()
        icon = int(icon_id)
        if icon not in (9, 15):
            raise ValueError(f"unsupported SSSS icon: {icon}")
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT OR IGNORE INTO ssss_signal_events(
                    symbol, timeframe, signal_bar_open_time, icon_id,
                    detection_bar_open_time, status
                ) VALUES(?, ?, ?, ?, ?, ?)
                """,
                (
                    symbol, tf, int(signal_bar_open_time), icon,
                    int(detection_bar_open_time), str(status),
                ),
            )
            inserted = cur.rowcount == 1
            if not inserted:
                conn.execute(
                    """
                    UPDATE ssss_signal_events
                    SET last_detected_time=CURRENT_TIMESTAMP,
                        detection_bar_open_time=?
                    WHERE symbol=? AND timeframe=?
                      AND signal_bar_open_time=? AND icon_id=?
                    """,
                    (
                        int(detection_bar_open_time), symbol, tf,
                        int(signal_bar_open_time), icon,
                    ),
                )
            row = conn.execute(
                """
                SELECT id, symbol, timeframe, signal_bar_open_time, icon_id,
                       first_detected_time, last_detected_time,
                       detection_bar_open_time, status,
                       execution_bar_open_time, execution_time,
                       binance_order_id, result
                FROM ssss_signal_events
                WHERE symbol=? AND timeframe=?
                  AND signal_bar_open_time=? AND icon_id=?
                """,
                (symbol, tf, int(signal_bar_open_time), icon),
            ).fetchone()
            if row is None:
                raise RuntimeError("SSSS signal event persistence failed")
            item = dict(row)
            item["is_new"] = inserted
            return item

    def mark_ssss_signal_result(
        self,
        symbol: str,
        *,
        timeframe: str,
        signal_bar_open_time: int,
        icon_id: int,
        status: str,
        execution_bar_open_time: int | None = None,
        binance_order_id: str | None = None,
        result: str | None = None,
    ) -> None:
        with self._connect() as conn:
            cur = conn.execute(
                """
                UPDATE ssss_signal_events
                SET status=?,
                    execution_bar_open_time=?,
                    execution_time=CURRENT_TIMESTAMP,
                    binance_order_id=?,
                    result=?,
                    last_detected_time=CURRENT_TIMESTAMP
                WHERE symbol=? AND timeframe=?
                  AND signal_bar_open_time=? AND icon_id=?
                """,
                (
                    str(status),
                    int(execution_bar_open_time) if execution_bar_open_time is not None else None,
                    str(binance_order_id) if binance_order_id else None,
                    str(result) if result is not None else None,
                    symbol, str(timeframe).lower(),
                    int(signal_bar_open_time), int(icon_id),
                ),
            )
            if cur.rowcount != 1:
                raise KeyError(
                    f"unknown SSSS signal event: {symbol}/{timeframe}/{icon_id}/{signal_bar_open_time}"
                )

    def recent_ssss_signal_events(
        self,
        symbol: str,
        *,
        limit: int = 20,
    ) -> list[dict[str, object]]:
        safe_limit = min(max(int(limit), 1), 200)
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, symbol, timeframe, signal_bar_open_time, icon_id,
                       first_detected_time, last_detected_time,
                       detection_bar_open_time, status,
                       execution_bar_open_time, execution_time,
                       binance_order_id, result
                FROM ssss_signal_events
                WHERE symbol=?
                ORDER BY id DESC
                LIMIT ?
                """,
                (symbol, safe_limit),
            ).fetchall()
            return [dict(row) for row in rows]

    def chart_ssss_signal_events(
        self, symbol: str, *, timeframe: str, first_open_time: int,
        last_open_time: int,
    ) -> list[dict[str, object]]:
        """Immutable first-detection ledger survives XMA repaint and restarts.

        The most recent 1000 closed candles have at most 2000 icon slots.
        BASELINE icons are excluded because they predate activation.
        """
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT signal_bar_open_time, detection_bar_open_time,
                       icon_id, first_detected_time, status,
                       execution_bar_open_time, binance_order_id
                FROM ssss_signal_events
                WHERE symbol=? AND timeframe=?
                  AND signal_bar_open_time BETWEEN ? AND ?
                  AND status <> 'BASELINE'
                ORDER BY signal_bar_open_time ASC, icon_id ASC
                LIMIT 2000
                """,
                (
                    symbol, str(timeframe).lower(),
                    int(first_open_time), int(last_open_time),
                ),
            ).fetchall()
        return [dict(row) for row in rows]

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

    def begin_order(
        self,
        symbol: str,
        client_order_id: str,
        *,
        side: str,
        quantity: float,
        price: float,
        strategy_id: str = "5s_crypto_v1",
        target_fraction_after: float | None = None,
        strategy_state_after: dict[str, object] | None = None,
        signal_bar_open_time: int | None = None,
        execution_bar_open_time: int | None = None,
        marker_side: str | None = None,
        strategy_signal: str | None = None,
    ) -> bool:
        state_json = json.dumps(strategy_state_after or {}, ensure_ascii=False, sort_keys=True)
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT OR IGNORE INTO orders(
                    symbol, client_order_id, side, quantity, price, status,
                    strategy_id, target_fraction_after, strategy_state_after_json,
                    signal_bar_open_time, execution_bar_open_time, marker_side, strategy_signal
                ) VALUES(?, ?, ?, ?, ?, 'PENDING', ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    symbol, client_order_id, side, float(quantity), float(price),
                    str(strategy_id),
                    float(target_fraction_after) if target_fraction_after is not None else None,
                    state_json,
                    int(signal_bar_open_time) if signal_bar_open_time is not None else None,
                    int(execution_bar_open_time) if execution_bar_open_time is not None else None,
                    str(marker_side) if marker_side else None,
                    str(strategy_signal) if strategy_signal else None,
                ),
            )
            return cur.rowcount == 1

    def get_order(self, symbol: str, client_order_id: str) -> dict[str, object] | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT symbol, client_order_id, binance_order_id, side, quantity, price, status,
                       strategy_id, target_fraction_after, strategy_state_after_json,
                       signal_bar_open_time, execution_bar_open_time, marker_side, strategy_signal
                FROM orders WHERE symbol=? AND client_order_id=?
                """,
                (symbol, client_order_id),
            ).fetchone()
            return dict(row) if row is not None else None

    def list_orders(self, symbol: str) -> list[dict[str, object]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, symbol, client_order_id, binance_order_id, side,
                       quantity, price, status, strategy_id, target_fraction_after,
                       strategy_state_after_json, signal_bar_open_time,
                       execution_bar_open_time, marker_side, strategy_signal,
                       created_at, updated_at
                FROM orders WHERE symbol=? ORDER BY id ASC
                """,
                (symbol,),
            ).fetchall()
            return [dict(row) for row in rows]

    def mark_order_status(self, symbol: str, client_order_id: str, status: str) -> None:
        with self._connect() as conn:
            cur = conn.execute(
                """
                UPDATE orders SET status=?, updated_at=CURRENT_TIMESTAMP
                WHERE symbol=? AND client_order_id=?
                """,
                (str(status), symbol, client_order_id),
            )
            if cur.rowcount != 1:
                raise KeyError(f"unknown order: {symbol}/{client_order_id}")

    def set_recovery_runtime(
        self,
        symbol: str,
        *,
        current_fraction: float,
        c_confirmed: bool,
        entry_signal_open_time: int | None,
        entry_family: str | None,
        last_order_id: str | None,
        last_closed_bar_open_time: int | None,
        run_state: str,
    ) -> None:
        with self._connect() as conn:
            cur = conn.execute(
                """
                UPDATE runtime_state
                SET current_fraction=?, c_confirmed=?, entry_signal_open_time=?,
                    entry_family=?, last_order_id=?, last_closed_bar_open_time=?,
                    pending_action=NULL, run_state=?, updated_at=CURRENT_TIMESTAMP
                WHERE symbol=?
                """,
                (
                    float(current_fraction), 1 if c_confirmed else 0,
                    entry_signal_open_time, entry_family, last_order_id,
                    last_closed_bar_open_time, str(run_state), symbol,
                ),
            )
            if cur.rowcount != 1:
                raise KeyError(f"unknown symbol: {symbol}")

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

    def list_trade_markers(self, symbol: str, strategy_id: str = "5s_crypto_v1") -> list[dict[str, object]]:
        """Expose chart labels only for orders that actually reached FILLED."""
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, client_order_id, binance_order_id, side, price,
                       target_fraction_after, execution_bar_open_time,
                       marker_side, strategy_signal
                FROM orders
                WHERE symbol=? AND strategy_id=? AND status='FILLED'
                      AND execution_bar_open_time IS NOT NULL
                      AND marker_side IS NOT NULL
                ORDER BY id ASC
                """,
                (symbol, strategy_id),
            ).fetchall()

        markers: list[dict[str, object]] = []
        seen: set[tuple[int, str, str]] = set()
        for row in rows:
            open_time = int(row["execution_bar_open_time"])
            side = str(row["marker_side"] or "").upper()
            if side not in {"B", "S", "X"}:
                continue
            signal = str(row["strategy_signal"] or "")
            key = (open_time, side, str(row["client_order_id"]))
            if key in seen:
                continue
            seen.add(key)
            markers.append(
                {
                    "open_time": open_time,
                    "side": side,
                    "signal": signal,
                    "price": float(row["price"] or 0.0),
                    "client_order_id": str(row["client_order_id"]),
                    "binance_order_id": str(row["binance_order_id"] or ""),
                    "source": "FILLED_ORDER",
                }
            )
        return markers

    # Backward name retained for callers/tests while semantics are now FILLED-only.
    def list_signal_markers(self, symbol: str, strategy_id: str = "5s_crypto_v1") -> list[dict[str, object]]:
        return self.list_trade_markers(symbol, strategy_id)

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
