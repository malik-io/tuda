"""Flask UI for browsing TUDA logbook."""
from __future__ import annotations

import pathlib
import sqlite3

from flask import Flask, render_template

app = Flask(__name__)
DB_PATH = pathlib.Path(__file__).resolve().parents[1] / "logbook.sqlite"


def fetch_records() -> list[dict]:
    if not DB_PATH.exists():
        return []

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    try:
        rows = connection.execute(
            """
            SELECT id, received_at, subject, sender, recipients, tags
            FROM logbook
            ORDER BY id DESC
            LIMIT 100
            """
        ).fetchall()
    finally:
        connection.close()

    return [dict(row) for row in rows]


@app.route("/")
def index() -> str:
    records = fetch_records()
    return render_template("index.html", records=records)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
