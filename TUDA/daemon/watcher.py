"""Basic file watcher that ingests .eml files into the TUDA logbook."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(BASE_DIR))

from email_parser import parse_email
from intel_core import analyze
from main import init_db, store_entry

CONFIG_PATH = BASE_DIR / "config.json"


def load_config():
    with CONFIG_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> None:
    config = load_config()
    watch_dir = BASE_DIR / config.get("watch_dir", "inbox")
    watch_dir.mkdir(parents=True, exist_ok=True)
    db_path = BASE_DIR / config["logbook_path"]
    init_db(db_path)

    seen = set()
    print(f"Watching {watch_dir} for .eml files...")

    while True:
        for path in watch_dir.glob("*.eml"):
            if path in seen:
                continue
            raw_email = path.read_bytes()
            metadata = parse_email(raw_email)
            intel = analyze(metadata)
            store_entry(db_path, metadata, intel)
            seen.add(path)
            print(f"Ingested {path.name}")
        time.sleep(2)


if __name__ == "__main__":
    main()
