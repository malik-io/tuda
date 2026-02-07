"""Minimal daemon placeholder for TUDA."""
from __future__ import annotations

import time


def main() -> None:
    print("TUDA watcher running. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(5)
            print("Watcher heartbeat...")
    except KeyboardInterrupt:
        print("Watcher stopped.")


if __name__ == "__main__":
    main()
