from datetime import date

import pytest
from pydantic import ValidationError

from app.core.settings import Settings

LLM_SETTINGS = {
    "llm_base_url": "https://llm.example/api",
    "openrouter_api_key": "key",
    "llm_model": "model",
}


def build_settings(**overrides: object) -> Settings:
    values = {"database_url": "sqlite://", **overrides}
    return Settings(_env_file=None, **values)


def test_empty_values_are_treated_as_unset():
    settings = build_settings(reference_date="", openrouter_api_key=" ", llm_base_url="")

    assert settings.reference_date is None
    assert settings.openrouter_api_key is None
    assert settings.llm_base_url is None


def test_reference_date_is_parsed():
    settings = build_settings(reference_date="2026-03-25")

    assert settings.reference_date == date(2026, 3, 25)


@pytest.mark.parametrize("database_url", [None, ""])
def test_database_url_is_required(database_url):
    values = {} if database_url is None else {"database_url": database_url}

    with pytest.raises(ValidationError, match="database_url"):
        Settings(_env_file=None, **values)


def test_database_url_is_used_as_given():
    assert (
        build_settings(database_url="sqlite:///tmp/app.db").database_url == "sqlite:///tmp/app.db"
    )


def test_paths_do_not_depend_on_working_directory():
    settings = build_settings()

    assert settings.store_config_path.is_absolute()
    assert settings.store_config_path.exists()
    assert settings.prompts_dir.is_absolute()


@pytest.mark.parametrize("missing", ["llm_base_url", "openrouter_api_key", "llm_model"])
def test_llm_configured_requires_url_key_and_model(missing):
    values = {key: value for key, value in LLM_SETTINGS.items() if key != missing}

    assert not build_settings(**values).llm_configured


def test_llm_configured_when_everything_is_set():
    assert build_settings(**LLM_SETTINGS).llm_configured


def test_cors_allows_no_origin_by_default():
    assert build_settings().cors_origin_list == []


def test_cors_origins_are_split_and_trimmed():
    settings = build_settings(cors_origins=" http://a.test ,http://b.test,, ")

    assert settings.cors_origin_list == ["http://a.test", "http://b.test"]
