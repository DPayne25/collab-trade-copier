from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, Optional

from config import APP_CONFIG


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(APP_CONFIG["db_path"])
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def db_cursor():
    conn = get_connection()
    cur = conn.cursor()
    try:
        yield cur
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with db_cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS trade_events (
                event_id TEXT PRIMARY KEY,
                source_ticket TEXT NOT NULL,
                action TEXT NOT NULL,
                symbol TEXT NOT NULL,
                side TEXT,
                volume REAL,
                stopPrice REAL,
                tp REAL,
                raw_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS trade_links (
                source_ticket TEXT NOT NULL,
                target_platform TEXT NOT NULL,
                target_order_id TEXT,
                target_position_id TEXT,
                status TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (source_ticket, target_platform)
            )
            """
        )


def insert_trade_event(event: Dict[str, Any]) -> None:
    with db_cursor() as cur:
        cur.execute(
            """
            INSERT INTO trade_events (
                event_id, source_ticket, action, symbol, side, volume, stopPrice, tp, raw_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event["event_id"],
                event["source_ticket"],
                event["action"],
                event["symbol"],
                event.get("side"),
                event.get("volume"),
                event.get("stopPrice"),
                event.get("tp"),
                json.dumps(event, default=str),
                datetime.utcnow().isoformat(),
            ),
        )


def upsert_trade_link(
    source_ticket: str,
    target_platform: str,
    target_order_id: Optional[str],
    target_position_id: Optional[str],
    status: str,
) -> None:
    with db_cursor() as cur:
        cur.execute(
            """
            INSERT INTO trade_links (
                source_ticket, target_platform, target_order_id, target_position_id, status, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(source_ticket, target_platform)
            DO UPDATE SET
                target_order_id=excluded.target_order_id,
                target_position_id=excluded.target_position_id,
                status=excluded.status,
                updated_at=excluded.updated_at
            """,
            (
                source_ticket,
                target_platform,
                target_order_id,
                target_position_id,
                status,
                datetime.utcnow().isoformat(),
            ),
        )


def event_exists(event_id: str) -> bool:
    with db_cursor() as cur:
        cur.execute("SELECT 1 FROM trade_events WHERE event_id = ? LIMIT 1", (event_id,))
        row = cur.fetchone()
        return row is not None


def get_trade_link(source_ticket: str, target_platform: str) -> Optional[Dict[str, Any]]:
    with db_cursor() as cur:
        cur.execute(
            """
            SELECT * FROM trade_links
            WHERE source_ticket = ? AND target_platform = ?
            LIMIT 1
            """,
            (source_ticket, target_platform),
        )
        row = cur.fetchone()
        return dict(row) if row else None