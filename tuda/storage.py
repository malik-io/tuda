from __future__ import annotations

from contextlib import contextmanager
from typing import Iterable

try:
    from pysqlcipher3 import dbapi2 as sqlite
except ImportError:  # pragma: no cover - fallback for environments without SQLCipher
    import sqlite3 as sqlite


class EncryptedDB:
    def __init__(self, db_path: str, key: str):
        self.db_path = db_path
        self.key = key

    @contextmanager
    def connect(self):
        conn = sqlite.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(f"PRAGMA key = '{self.key}'")
        except Exception:
            # sqlite3 fallback doesn't support SQLCipher pragma.
            pass
        try:
            yield conn
        finally:
            conn.close()

    def init_schema(self) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    subject TEXT,
                    sender TEXT,
                    snippet TEXT,
                    internal_date TEXT
                )
                """
            )
            conn.commit()

    def insert_messages(self, records: Iterable[tuple[str, str, str, str, str]]) -> None:
        with self.connect() as conn:
            conn.executemany(
                (
                    "INSERT OR REPLACE INTO messages "
                    "(id, subject, sender, snippet, internal_date) VALUES (?, ?, ?, ?, ?)"
                ),
                records,
            )
            conn.commit()

    def fetch_message(self, message_id: str) -> tuple[str, str, str, str] | None:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT subject, sender, snippet, internal_date FROM messages WHERE id = ?",
                (message_id,),
            ).fetchone()
        return row

    def list_messages(self, limit: int = 10) -> list[tuple[str, str, str, str, str]]:
        with self.connect() as conn:
            rows = conn.execute(
                (
                    "SELECT id, subject, sender, snippet, internal_date FROM messages "
                    "ORDER BY internal_date DESC LIMIT ?"
                ),
                (limit,),
            ).fetchall()
        return rows
