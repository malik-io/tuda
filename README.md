# TUDA — Textual Unified Digital Agent

Zero-cost, stealth-hosted email recon PDA with full metadata capture, forensic reporting, CUDA hooks, and agentic interface.

## Project Structure

```
TUDA/
├── README.md
├── main.py                  # Entry point — daemon or manual mode
├── email_parser.py          # Extracts raw metadata (IP, headers, auth, etc.)
├── intel_core.py            # Runs tagging, clustering, fingerprinting, NLP
├── logbook.sqlite           # SQLite DB to store parsed mail intel (auto-created)
├── config.json              # Runtime configuration (domain, port, plugins)
├── plugins/                 # Optional plugin modules
│   └── example.py
├── ui/
│   ├── server.py            # Flask-based report interface (optional)
│   └── templates/
│       └── index.html       # Web UI for metadata viewing
└── daemon/
    └── watcher.py           # Optional auto-run daemon
```

## Features

- Real-time email interception & parsing (via stdin or `.eml` drops)
- IP logging, HELO string capture, TLS negotiation hints
- Forensic fingerprinting engine
- NLP-style tagging via `intel_core.py`
- SQLite logbook for indexed reports
- Plugin system (header transforms, alerting, report filters)
- Flask web UI for stealth metadata browsing
- CUDA / PyTorch optional support

## How to Build & Run

```bash
# 1. Install dependencies
pip install flask

# 2. Start listener (pipe in a raw RFC822 email)
python TUDA/main.py < sample.eml

# 3. Parse a single file
python TUDA/main.py --sample sample.eml

# 4. Run web UI
python TUDA/ui/server.py

# 5. Background mode (watch .eml files)
python TUDA/daemon/watcher.py
```

## Plugins

Drop a plugin in `TUDA/plugins/` and register its path in `TUDA/config.json`.
Each plugin can provide a `process(metadata, intel)` hook to enrich results.

## Mission

> TUDA exists to make metadata visible, agentic, and sovereign.
> No more blind trust — we take our intel back.
