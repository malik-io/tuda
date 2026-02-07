# TUDA Hybrid App

This repository now contains the TUDA Python backend scaffolding alongside the existing Android files.

## Backend quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
uvicorn tuda.api:app --reload
```

Environment variables (prefix `TUDA_`) can be used to configure Gmail and DB values:

- `TUDA_DB_PATH`
- `TUDA_DB_KEY`
- `TUDA_GMAIL_TOKEN`
- `TUDA_GMAIL_REFRESH_TOKEN`
- `TUDA_GMAIL_CLIENT_ID`
- `TUDA_GMAIL_CLIENT_SECRET`

## API endpoints

- `GET /health`
- `GET /messages?limit=20`
- `GET /messages?message_id=<id>`
- `GET /analysis/<message_id>`

## Testing and quality

```bash
ruff check .
black --check .
pytest
```

`pytest` enforces `--cov-fail-under=80` via `pyproject.toml`.
