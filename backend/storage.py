from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, Optional


class Storage:
    def __init__(self, db_path: str = "backend/state.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _conn(self) -> sqlite3.Connection:
        return sqlite3.connect(str(self.db_path))

    def _init_db(self) -> None:
        with self._conn() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS consciousness_state (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    state_json TEXT NOT NULL
                )
                """
            )

    def load_state(self) -> Optional[Dict[str, Any]]:
        with self._conn() as conn:
            row = conn.execute("SELECT state_json FROM consciousness_state WHERE id = 1").fetchone()
        if not row:
            return None
        return json.loads(row[0])

    def save_state(self, state: Dict[str, Any]) -> None:
        payload = json.dumps(state)
        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO consciousness_state (id, state_json)
                VALUES (1, ?)
                ON CONFLICT(id) DO UPDATE SET state_json=excluded.state_json
                """,
                (payload,),
            )
