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
    llm_base_url: str = "https://openrouter.ai/api/v1"
    llm_timeout_seconds: float = Field(default=30, gt=0)
    llm_max_retries: int = Field(default=2, ge=0)
    database_url: str | None = None
    reference_date: date | None = None
    history_max_turns: int = Field(default=6, ge=1)
    agent_max_steps: int = Field(default=10, ge=1)
    max_message_length: int = Field(default=2000, ge=1)
    log_level: str = "INFO"
    store_config_path: Path = BASE_DIR / "config" / "store.toml"
    prompts_dir: Path = BASE_DIR / "prompts"

    @field_validator(
        "openrouter_api_key", "llm_model", "database_url", "reference_date", mode="before"
    )
    @classmethod
    def empty_string_to_none(cls, value: Any) -> Any:
        """Treat empty environment values as unset."""
        if isinstance(value, str) and not value.strip():
            return None
        return value

    @property
    def resolved_database_url(self) -> str:
        """Database URL, defaulting to a SQLite file inside the project `data` folder."""
        if self.database_url:
            return self.database_url
        return f"sqlite:///{(BASE_DIR / 'data' / 'app.db').as_posix()}"

    @property
    def llm_configured(self) -> bool:
        """Whether the LLM provider credentials and model are set."""
        return bool(self.openrouter_api_key and self.llm_model)


@lru_cache
def get_settings() -> Settings:
    """Return the cached application settings."""
    return Settings()
