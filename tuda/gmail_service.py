from __future__ import annotations

from typing import Any

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


class GmailService:
    def __init__(self, token: str, refresh_token: str, client_id: str, client_secret: str):
        self.creds = Credentials(
            token=token,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
        )
        self.service = build("gmail", "v1", credentials=self.creds)

    def list_messages(self, user_id: str = "me", max_results: int = 10) -> list[dict[str, Any]]:
        response = (
            self.service.users().messages().list(userId=user_id, maxResults=max_results).execute()
        )
        messages: list[dict[str, Any]] = []
        for msg in response.get("messages", []):
            meta = (
                self.service.users()
                .messages()
                .get(userId=user_id, id=msg["id"], format="metadata")
                .execute()
            )
            headers = {
                h.get("name", ""): h.get("value", "")
                for h in meta.get("payload", {}).get("headers", [])
            }
            messages.append(
                {
                    "id": meta["id"],
                    "snippet": meta.get("snippet", ""),
                    "internalDate": meta.get("internalDate", ""),
                    "headers": headers,
                }
            )
        return messages
