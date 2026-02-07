"""Flask UI for browsing TUDA logbook entries."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from flask import Flask, render_template

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "logbook.sqlite"

app = Flask(__name__)


def fetch_entries():
    if not DB_PATH.exists():
        return []
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT id, timestamp, sender, recipient, subject, message_id, ips, tls, tags, fingerprint
            FROM logbook
            ORDER BY id DESC
            LIMIT 100
            """
        ).fetchall()
    entries = []
    for row in rows:
        entry = dict(row)
        entry["ips"] = entry.get("ips", "").split(",") if entry.get("ips") else []
        entry["tags"] = entry.get("tags", "").split(",") if entry.get("tags") else []
        entries.append(entry)
    return entries


@app.route("/")
def index():
    entries = fetch_entries()
    return render_template("index.html", entries=entries)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
