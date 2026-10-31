from datetime import date
from pathlib import Path

from app.core.settings import BASE_DIR, Settings


def build_settings(**overrides: object) -> Settings:
    return Settings(_env_file=None, **overrides)


def test_empty_values_are_treated_as_unset():
    settings = build_settings(reference_date="", database_url="", openrouter_api_key=" ")

    assert settings.reference_date is None
    assert settings.database_url is None
    assert settings.openrouter_api_key is None


def test_reference_date_is_parsed():
    settings = build_settings(reference_date="2026-03-25")

    assert settings.reference_date == date(2026, 3, 25)


def test_default_database_url_is_absolute_sqlite_file():
    settings = build_settings()

    expected_path = (BASE_DIR / "data" / "app.db").as_posix()
    assert settings.resolved_database_url == f"sqlite:///{expected_path}"
    assert Path(expected_path).is_absolute()


def test_explicit_database_url_is_kept():
    settings = build_settings(database_url="sqlite://")

    assert settings.resolved_database_url == "sqlite://"


def test_paths_do_not_depend_on_working_directory():
    settings = build_settings()

    assert settings.store_config_path.is_absolute()
    assert settings.store_config_path.exists()
    assert settings.prompts_dir.is_absolute()


def test_llm_configured_requires_key_and_model():
    assert not build_settings(openrouter_api_key="key").llm_configured
    assert not build_settings(llm_model="model").llm_configured
    assert build_settings(openrouter_api_key="key", llm_model="model").llm_configured
