"""Lightweight enrichment for parsed email metadata."""
from __future__ import annotations

import re


SUSPICIOUS_KEYWORDS = {
    "urgent",
    "wire",
    "invoice",
    "password",
    "action required",
    "click",
}


def enrich_intel(parsed: dict) -> dict:
    subject = parsed.get("subject") or ""
    tags = set(parsed.get("tags", []))

    normalized = subject.lower()
    for keyword in SUSPICIOUS_KEYWORDS:
        if keyword in normalized:
            tags.add("suspicious-subject")
            break

    if parsed.get("sender") and re.search(r"@", parsed["sender"]):
        tags.add("has-sender")

    if parsed.get("recipients"):
        tags.add("has-recipient")

    parsed["tags"] = sorted(tags)
    return parsed
