"""Example plugin that enriches metadata tags."""

from __future__ import annotations


def process(metadata, intel):
    if metadata.get("subject") and "demo" in metadata["subject"].lower():
        intel.setdefault("tags", []).append("demo")
