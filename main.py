"""TUDA entry point.

Starts the email listener in either daemon or foreground mode.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sqlite3
import sys
from datetime import datetime, timezone

from email_parser import parse_email
from intel_core import enrich_intel


def load_config(path: pathlib.Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def init_db(db_path: pathlib.Path) -> None:
    connection = sqlite3.connect(db_path)
    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS logbook (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                received_at TEXT NOT NULL,
                source TEXT,
                subject TEXT,
                sender TEXT,
                recipients TEXT,
                helo TEXT,
                tls TEXT,
                tags TEXT,
                raw_headers TEXT
            )
            """
        )
        connection.commit()
    finally:
        connection.close()


def save_record(db_path: pathlib.Path, record: dict) -> None:
    connection = sqlite3.connect(db_path)
    try:
        connection.execute(
            """
            INSERT INTO logbook (
                received_at,
                source,
                subject,
                sender,
                recipients,
                helo,
                tls,
                tags,
                raw_headers
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record["received_at"],
                record.get("source"),
                record.get("subject"),
                record.get("sender"),
                ",".join(record.get("recipients", [])),
                record.get("helo"),
                record.get("tls"),
                ",".join(record.get("tags", [])),
                record.get("raw_headers"),
            ),
        )
        connection.commit()
    finally:
        connection.close()


def run_listener(config: dict) -> None:
    db_path = pathlib.Path(config["database_path"])
    init_db(db_path)

    print("TUDA listener ready. Paste a raw email followed by EOF (Ctrl-D):")
    raw_email = sys.stdin.read()
    if not raw_email.strip():
        print("No email data provided. Exiting.")
        return

    parsed = parse_email(raw_email)
    enriched = enrich_intel(parsed)
    enriched["received_at"] = datetime.now(timezone.utc).isoformat()
    save_record(db_path, enriched)
    print("Captured email metadata and saved to logbook.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="TUDA email recon agent")
    parser.add_argument(
        "--config",
        default="config.json",
        help="Path to config.json",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    config = load_config(pathlib.Path(args.config))
    run_listener(config)


if __name__ == "__main__":
    main()
