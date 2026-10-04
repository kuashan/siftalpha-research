from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from threading import RLock
from typing import Any


DEFAULT_SYMBOLS = ("BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT")
EXECUTABLE_STRATEGIES = ("v7", "e", "5s_stocks")


class DemoStore:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = RLock()
        self._init()

    def _conn(self):
        conn = sqlite3.connect(self.path, timeout=30, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init(self):
        with self._conn() as c:
            c.executescript(
                """
                CREATE TABLE IF NOT EXISTS symbol_config(
                    symbol TEXT PRIMARY KEY,
                    strategy_id TEXT NOT NULL,
                    timeframe TEXT NOT NULL,
                    leverage INTEGER NOT NULL,
                    capital_budget_usdt REAL NOT NULL,
                    enabled INTEGER NOT NULL DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS symbol_runtime(
                    symbol TEXT PRIMARY KEY,
                    strategy_id TEXT NOT NULL,
                    current_fraction REAL NOT NULL DEFAULT 0,
                    state_json TEXT NOT NULL DEFAULT '{}',
                    last_closed_open_time INTEGER,
                    last_order_id TEXT,
                    run_state TEXT NOT NULL DEFAULT 'STOPPED',
                    accounting_start_time_ms INTEGER
                );
                CREATE TABLE IF NOT EXISTS orders(
                    symbol TEXT NOT NULL,
                    client_order_id TEXT NOT NULL,
                    strategy_id TEXT NOT NULL,
                    side TEXT NOT NULL,
                    quantity REAL NOT NULL,
                    price REAL NOT NULL,
                    status TEXT NOT NULL,
                    binance_order_id TEXT,
                    PRIMARY KEY(symbol, client_order_id)
                );
                CREATE TABLE IF NOT EXISTS audit(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    kind TEXT NOT NULL,
                    symbol TEXT,
                    detail TEXT NOT NULL
                );
                """
            )
            for symbol in DEFAULT_SYMBOLS:
                c.execute(
                    """
                    INSERT OR IGNORE INTO symbol_config
                    (symbol,strategy_id,timeframe,leverage,capital_budget_usdt,enabled)
                    VALUES(?,?,?,?,?,0)
                    """,
                    (symbol, "v7", "1h", 1, 1000.0),
                )
                c.execute(
                    """
                    INSERT OR IGNORE INTO symbol_runtime
                    (symbol,strategy_id,current_fraction,state_json,run_state)
                    VALUES(?,?,?,?,?)
                    """,
                    (symbol, "v7", 0.0, "{}", "STOPPED"),
                )

    def configs(self) -> dict[str, dict[str, Any]]:
        with self._conn() as c:
            rows=c.execute("SELECT * FROM symbol_config ORDER BY symbol").fetchall()
        return {r["symbol"]: dict(r) | {"enabled": bool(r["enabled"])} for r in rows}

    def runtimes(self) -> dict[str, dict[str, Any]]:
        with self._conn() as c:
            rows=c.execute("SELECT * FROM symbol_runtime ORDER BY symbol").fetchall()
        out={}
        for r in rows:
            d=dict(r)
            try: d["state"]=json.loads(d.pop("state_json") or "{}")
            except Exception: d["state"]={}
            out[d["symbol"]]=d
        return out

    def set_config(self, symbol: str, *, strategy_id: str, timeframe: str, leverage: int, budget: float):
        if strategy_id not in EXECUTABLE_STRATEGIES:
            raise ValueError("该策略当前不允许自动下单")
        with self._lock, self._conn() as c:
            c.execute(
                """UPDATE symbol_config SET strategy_id=?,timeframe=?,leverage=?,capital_budget_usdt=?
                WHERE symbol=?""",
                (strategy_id,timeframe,int(leverage),float(budget),symbol),
            )
            c.execute("UPDATE symbol_runtime SET strategy_id=? WHERE symbol=?", (strategy_id,symbol))

    def set_enabled(self, symbol: str, enabled: bool):
        with self._lock, self._conn() as c:
            c.execute("UPDATE symbol_config SET enabled=? WHERE symbol=?", (1 if enabled else 0,symbol))

    def set_runtime(self, symbol: str, *, fraction: float | None=None, state: dict | None=None,
                    last_closed_open_time: int | None | object=..., last_order_id: str | None | object=...,
                    run_state: str | None=None, accounting_start_time_ms: int | None | object=...):
        fields=[]; vals=[]
        if fraction is not None: fields+=["current_fraction=?"]; vals+=[float(fraction)]
        if state is not None: fields+=["state_json=?"]; vals+=[json.dumps(state,separators=(",",":"))]
        if last_closed_open_time is not ...:
            fields+=["last_closed_open_time=?"]; vals+=[last_closed_open_time]
        if last_order_id is not ...:
            fields+=["last_order_id=?"]; vals+=[last_order_id]
        if run_state is not None: fields+=["run_state=?"]; vals+=[run_state]
        if accounting_start_time_ms is not ...:
            fields+=["accounting_start_time_ms=?"]; vals+=[accounting_start_time_ms]
        if not fields: return
        vals.append(symbol)
        with self._lock, self._conn() as c:
            c.execute("UPDATE symbol_runtime SET "+",".join(fields)+" WHERE symbol=?", vals)

    def baseline(self, symbol: str, strategy_id: str, open_time: int):
        self.set_runtime(
            symbol, fraction=0.0, state={}, last_closed_open_time=int(open_time),
            last_order_id=None, run_state="MONITORING",
        )

    def begin_order(self, symbol: str, client_id: str, strategy_id: str, side: str, qty: float, price: float) -> bool:
        with self._lock, self._conn() as c:
            cur=c.execute(
                """INSERT OR IGNORE INTO orders
                (symbol,client_order_id,strategy_id,side,quantity,price,status)
                VALUES(?,?,?,?,?,?,'PENDING')""",
                (symbol,client_id,strategy_id,side,float(qty),float(price)),
            )
            return cur.rowcount > 0

    def finish_order(self, symbol: str, client_id: str, *, order_id: str, status: str, qty: float, price: float):
        with self._lock, self._conn() as c:
            c.execute(
                """UPDATE orders SET binance_order_id=?,status=?,quantity=?,price=?
                WHERE symbol=? AND client_order_id=?""",
                (str(order_id),str(status),float(qty),float(price),symbol,client_id),
            )

    def order(self, symbol: str, client_id: str):
        with self._conn() as c:
            r=c.execute("SELECT * FROM orders WHERE symbol=? AND client_order_id=?", (symbol,client_id)).fetchone()
        return dict(r) if r else None

    def net_filled_qty(self, symbol: str) -> float:
        with self._conn() as c:
            rows=c.execute("SELECT side,quantity FROM orders WHERE symbol=? AND status='FILLED'", (symbol,)).fetchall()
        return sum((1 if r["side"]=="BUY" else -1)*float(r["quantity"]) for r in rows)

    def audit(self, kind: str, symbol: str | None, detail: str):
        with self._conn() as c:
            c.execute("INSERT INTO audit(kind,symbol,detail) VALUES(?,?,?)", (kind,symbol,str(detail)))

    def recent_audit(self, limit: int=100):
        with self._conn() as c:
            rows=c.execute("SELECT * FROM audit ORDER BY id DESC LIMIT ?", (int(limit),)).fetchall()
        return [dict(r) for r in rows]
