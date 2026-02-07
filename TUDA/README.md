# TUDA — Textual Unified Digital Agent

TUDA is a modular email metadata capture system with a lightweight forensic pipeline. It ingests RFC822 messages, extracts headers and IP hints, and stores intel in a local SQLite logbook.

## Quick Start

```bash
pip install flask
python main.py --sample sample.eml
python ui/server.py
```

## Notes

- The SQLite logbook is created on first run.
- Drop `.eml` files into the `inbox/` directory when running the daemon watcher.
- Plugins can enrich tags or metadata via a `process(metadata, intel)` hook.
