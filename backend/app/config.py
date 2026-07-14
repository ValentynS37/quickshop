from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "BADS OS v2"
    app_env: str = "development"
    api_prefix: str = "/api/v1"
    bads_api_key: str = "dev-bads-key"
    database_url: str = "sqlite:///./bads_os.db"
    openai_api_key: str | None = None
    openai_model: str = "gpt-5-mini"
    openai_base_url: str = "https://api.openai.com/v1"
    agent_orchestration: Literal["sdk", "responses", "local"] = "sdk"
    agent_max_turns: int = Field(default=6, ge=2, le=20)
    agent_tracing_enabled: bool = False
    cors_origins: list[str] = ["http://localhost:8000", "http://localhost:5500"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    @field_validator("bads_api_key")
    @classmethod
    def validate_api_key(cls, value: str) -> str:
        if not value:
            raise ValueError("BADS_API_KEY cannot be empty")
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
