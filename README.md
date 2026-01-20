📁 **TUDA — Textual Unified Digital Agent**

> Zero-cost, stealth-hosted email recon PDA with full metadata capture, forensic reporting, CUDA hooks, and agentic interface.

---

## 📂 Project Structure

```bash
TUDA/
├── README.md
├── main.py                  # Entry point — daemon or manual mode
├── email_parser.py          # Extracts raw metadata (IP, headers, auth, etc.)
├── intel_core.py            # Runs tagging, clustering, fingerprinting, NLP
├── logbook.sqlite           # SQLite DB to store parsed mail intel
├── config.json              # Runtime configuration (domain, port, plugins)
├── plugins/                 # Optional plugin modules
│   └── ...
├── ui/
│   ├── server.py            # Flask-based report interface (optional)
│   └── templates/
│       └── index.html       # Web UI for metadata viewing
└── daemon/
    └── watcher.py           # Optional auto-run daemon
```

---

## 🧠 Features

- 📡 Real-time email interception & parsing
- 🧠 IP logging, HELO string capture, TLS negotiation
- 📦 Forensic fingerprinting engine
- 🧠 NLP tagging via `intel_core.py`
- 💾 SQLite logbook for indexed reports
- 🔌 Plugin system (header transforms, alerting, report filters)
- 🧵 Terminal PDA shell interface (TBA)
- 💻 Flask web UI for stealth metadata browsing
- 🧠 CUDA / PyTorch optional support
- 💰 Monetization: future ad-based dashboard or redirect capture

---

## 🛠️ How to Build & Run (For Codex / AI Agent)

```python
# 1. Clone or copy repo
mkdir TUDA && cd TUDA

# 2. Install dependencies
pip install flask sqlite3 torch

# 3. Start email listener
python main.py

# 4. (Optional) Run web UI
cd ui && python server.py

# 5. (Optional) Background mode
nohup python daemon/watcher.py &
```

---

## 🚧 Coming Soon

- `terminal_agent.py`: interactive PDA shell
- `api/v1/intel`: REST API for email events
- `report_builder.py`: generate PDF/HTML forensic reports
- `auto_response.py`: optional reply or forward system
- `plugin_market.json`: list of downloadable plugin logic

---

## 🤝 Contributing

This repo is modular — agents can inject or modify logic without breaking the base engine.  
To contribute:

1. Fork the project.
2. Add your plugin or module in `/plugins`
3. Register it in `config.json`
4. Submit a PR or send your `.py` to the PDA channel.

---

## 🧠 Mission
> TUDA exists to make metadata visible, agentic, and sovereign.  
No more blind trust — we take our intel back.

---

_Keep TUDA zero-cost, zero-trace, and fully agent-led._
