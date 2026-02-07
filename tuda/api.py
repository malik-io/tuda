from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

from .config import Settings, get_settings
from .gmail_service import GmailService
from .plugins.manager import discover_plugins
from .storage import EncryptedDB

app = FastAPI(title="TUDA API")


class Message(BaseModel):
    id: str
    subject: str
    sender: str
    snippet: str
    internal_date: str


def get_db(settings: Settings = Depends(get_settings)) -> EncryptedDB:
    db = EncryptedDB(settings.db_path, settings.db_key)
    db.init_schema()
    return db


def get_gmail_service(settings: Settings = Depends(get_settings)) -> GmailService:
    return GmailService(
        token=settings.gmail_token,
        refresh_token=settings.gmail_refresh_token,
        client_id=settings.gmail_client_id,
        client_secret=settings.gmail_client_secret,
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/messages", response_model=list[Message])
def get_messages(
    limit: int = 10,
    message_id: str | None = None,
    db: EncryptedDB = Depends(get_db),
    service: GmailService = Depends(get_gmail_service),
):
    if message_id:
        row = db.fetch_message(message_id)
        if not row:
            raise HTTPException(status_code=404, detail="Message not found")
        return [
            Message(
                id=message_id,
                subject=row[0],
                sender=row[1],
                snippet=row[2],
                internal_date=row[3],
            )
        ]

    meta = service.list_messages(max_results=limit)
    records = [
        (
            m["id"],
            m["headers"].get("Subject", ""),
            m["headers"].get("From", ""),
            m.get("snippet", ""),
            m.get("internalDate", ""),
        )
        for m in meta
    ]
    if records:
        db.insert_messages(records)

    return [
        Message(
            id=record[0],
            subject=record[1],
            sender=record[2],
            snippet=record[3],
            internal_date=record[4],
        )
        for record in records
    ]


@app.get("/analysis/{message_id}")
def analyze_message(message_id: str, db: EncryptedDB = Depends(get_db)) -> dict[str, object]:
    row = db.fetch_message(message_id)
    if not row:
        raise HTTPException(status_code=404, detail="Message not found")

    message = {
        "id": message_id,
        "subject": row[0],
        "sender": row[1],
        "snippet": row[2],
        "internal_date": row[3],
    }

    results: dict[str, object] = {}
    for plugin in discover_plugins():
        results[plugin.name] = plugin.run(message)
    return {"message_id": message_id, "analysis": results}
