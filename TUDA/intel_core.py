"""Lightweight intel processing for parsed email metadata."""

from __future__ import annotations

import hashlib
from typing import Any, Dict, List

TAG_KEYWORDS = {
    "invoice": "finance",
    "urgent": "priority",
    "password": "credential",
    "security": "security",
    "wire": "finance",
    "reset": "credential",
    "login": "credential",
}


def fingerprint(metadata: Dict[str, Any]) -> str:
    payload = "|".join(
        str(metadata.get(key, ""))
        for key in ("from", "to", "subject", "message_id")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def tag(metadata: Dict[str, Any]) -> List[str]:
    text = " ".join(
        str(metadata.get(key, ""))
        for key in ("subject", "body", "from")
    ).lower()
    tags = {label for keyword, label in TAG_KEYWORDS.items() if keyword in text}
    if metadata.get("tls"):
        tags.add("tls")
    if metadata.get("ips"):
        tags.add("ip-observed")
    return sorted(tags)


def analyze(metadata: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "fingerprint": fingerprint(metadata),
        "tags": tag(metadata),
    }
