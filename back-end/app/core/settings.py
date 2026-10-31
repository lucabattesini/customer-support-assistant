from datetime import date
from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Application settings loaded from environment variables and the `.env` file."""

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openrouter_api_key: str | None = None
    llm_model: str | None = None
    llm_base_url: str | None = None
    llm_timeout_seconds: float = Field(default=30, gt=0)
    llm_max_retries: int = Field(default=2, ge=0)
    database_url: str
    reference_date: date | None = None
    history_max_turns: int = Field(default=6, ge=1)
    agent_max_steps: int = Field(default=10, ge=1)
    max_message_length: int = Field(default=2000, ge=1)
    log_level: str = "INFO"
    cors_origins: str = ""
    store_config_path: Path = BASE_DIR / "config" / "store.toml"
    prompts_dir: Path = BASE_DIR / "prompts"

    @field_validator(
        "openrouter_api_key",
        "llm_model",
        "llm_base_url",
        "database_url",
        "reference_date",
        mode="before",
    )
    @classmethod
    def empty_string_to_none(cls, value: Any) -> Any:
        """Treat empty environment values as unset."""
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @property
    def cors_origin_list(self) -> list[str]:
        """Origins allowed to call the API from a browser, from a comma-separated value.

        Empty by default, so no browser origin is allowed unless configured.
        """
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def llm_configured(self) -> bool:
        """Whether the LLM provider URL, credentials and model are all set."""
        return bool(self.llm_base_url and self.openrouter_api_key and self.llm_model)


@lru_cache
def get_settings() -> Settings:
    """Return the cached application settings."""
    return Settings()
