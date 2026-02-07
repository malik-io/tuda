from __future__ import annotations

from .base import PluginBase


class SpamDetector(PluginBase):
    @property
    def name(self) -> str:
        return "SpamDetector"

    def run(self, message: dict[str, str]) -> dict[str, bool]:
        text = (message.get("subject", "") + " " + message.get("snippet", "")).lower()
        spam_tokens = {"win", "lottery", "prize", "urgent", "bitcoin", "free"}
        return {"is_spam": any(token in text for token in spam_tokens)}
