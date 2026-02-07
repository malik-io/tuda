"""TUDA entry point for parsing email metadata and storing intel."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List

from email_parser import parse_email
from intel_core import analyze

CONFIG_PATH = Path(__file__).resolve().parent / "config.json"


def load_config(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def init_db(db_path: Path) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS logbook (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                sender TEXT,
                recipient TEXT,
                subject TEXT,
                message_id TEXT,
                ips TEXT,
                tls INTEGER,
                tags TEXT,
                fingerprint TEXT,
                headers TEXT,
                body TEXT
            )
            """
        )


def store_entry(db_path: Path, metadata: Dict[str, Any], intel: Dict[str, Any]) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO logbook (
                sender, recipient, subject, message_id, ips, tls, tags, fingerprint, headers, body
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                metadata.get("from"),
                metadata.get("to"),
                metadata.get("subject"),
                metadata.get("message_id"),
                ",".join(metadata.get("ips", [])),
                int(bool(metadata.get("tls"))),
                ",".join(intel.get("tags", [])),
                intel.get("fingerprint"),
                json.dumps(metadata.get("headers", {}), ensure_ascii=False),
                metadata.get("body"),
            ),
        )


def load_plugins(plugin_paths: Iterable[str]) -> List[Any]:
    plugins = []
    for plugin_path in plugin_paths:
        path = Path(plugin_path)
        if not path.exists():
            continue
        spec = importlib.util.spec_from_file_location(path.stem, path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            plugins.append(module)
    return plugins


def apply_plugins(metadata: Dict[str, Any], intel: Dict[str, Any], plugins: List[Any]) -> None:
    for plugin in plugins:
        hook = getattr(plugin, "process", None)
        if callable(hook):
            hook(metadata, intel)


def process_email(raw_email: bytes, db_path: Path, plugins: List[Any]) -> Dict[str, Any]:
    metadata = parse_email(raw_email)
    intel = analyze(metadata)
    apply_plugins(metadata, intel, plugins)
    store_entry(db_path, metadata, intel)
    return {"metadata": metadata, "intel": intel}


def read_raw_email(path: Path | None) -> bytes:
    if path:
        return path.read_bytes()
    return sys.stdin.buffer.read()


def main() -> int:
    parser = argparse.ArgumentParser(description="TUDA email metadata capture")
    parser.add_argument("--config", type=Path, default=CONFIG_PATH)
    parser.add_argument("--sample", type=Path, help="Parse a single RFC822 message file")
    args = parser.parse_args()

    config = load_config(args.config)
    db_path = Path(args.config).resolve().parent / config["logbook_path"]
    init_db(db_path)
    plugins = load_plugins(config.get("plugins", []))

    raw_email = read_raw_email(args.sample)
    result = process_email(raw_email, db_path, plugins)
    metadata = result["metadata"]
    intel = result["intel"]
    print("Parsed email")
    print(f"From: {metadata.get('from')}")
    print(f"To: {metadata.get('to')}")
    print(f"Subject: {metadata.get('subject')}")
    print(f"IPs: {', '.join(metadata.get('ips', []))}")
    print(f"Tags: {', '.join(intel.get('tags', []))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
