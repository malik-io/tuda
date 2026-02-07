from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="TUDA_", env_file=".env", extra="ignore")

    db_path: str = Field(default="messages.db")
    db_key: str = Field(default="change-me")

    gmail_token: str = Field(default="")
    gmail_refresh_token: str = Field(default="")
    gmail_client_id: str = Field(default="")
    gmail_client_secret: str = Field(default="")


@lru_cache
def get_settings() -> Settings:
    return Settings()
