"""Email parsing and metadata extraction utilities."""

from __future__ import annotations

import re
from email import policy
from email.parser import BytesParser
from typing import Any, Dict, List

IP_REGEX = re.compile(
    r"(?:(?:25[0-5]|2[0-4]\d|[01]?\d?\d)(?:\.|$)){4}"
)
TLS_HINTS = ("TLS", "SSL", "ESMTPS")


def _extract_ips(received_headers: List[str]) -> List[str]:
    ips: List[str] = []
    for header in received_headers:
        ips.extend(IP_REGEX.findall(header))
    return sorted(set(ips))


def _detect_tls(received_headers: List[str]) -> bool:
    for header in received_headers:
        if any(hint in header for hint in TLS_HINTS):
            return True
    return False


def parse_email(raw_email: bytes) -> Dict[str, Any]:
    """Parse raw email bytes into structured metadata."""
    message = BytesParser(policy=policy.default).parsebytes(raw_email)
    received_headers = message.get_all("Received", [])
    metadata = {
        "from": message.get("From"),
        "to": message.get("To"),
        "subject": message.get("Subject"),
        "date": message.get("Date"),
        "message_id": message.get("Message-ID"),
        "helo": message.get("Received", ""),
        "received_count": len(received_headers),
        "received_headers": received_headers,
        "ips": _extract_ips(received_headers),
        "tls": _detect_tls(received_headers),
        "headers": dict(message.items()),
        "body": message.get_body(preferencelist=("plain", "html")),
    }
    body_part = metadata["body"]
    metadata["body"] = body_part.get_content() if body_part else ""
    return metadata
