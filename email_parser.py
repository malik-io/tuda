"""Parse raw email data into metadata fields."""
from __future__ import annotations

from email import message_from_string
from email.message import Message


HEADER_FIELDS = {
    "from": "sender",
    "to": "recipients",
    "subject": "subject",
    "received": "received",
    "return-path": "return_path",
}


def _split_recipients(value: str | None) -> list[str]:
    if not value:
        return []
    return [addr.strip() for addr in value.split(",") if addr.strip()]


def parse_email(raw_email: str) -> dict:
    message: Message = message_from_string(raw_email)
    headers = dict(message.items())

    parsed = {
        "subject": headers.get("Subject"),
        "sender": headers.get("From"),
        "recipients": _split_recipients(headers.get("To")),
        "raw_headers": "\n".join(f"{k}: {v}" for k, v in headers.items()),
        "source": headers.get("Received"),
        "helo": headers.get("HELO"),
        "tls": headers.get("TLS"),
    }
    return parsed
