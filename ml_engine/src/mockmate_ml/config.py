"""Centralized environment-based configuration."""

from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    environment: str = "development"
    log_level: str = "INFO"
    llm_provider: str = "none"
    gemini_api_key: SecretStr | None = None
    gemini_model: str = "gemini-2.5-flash"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
