import pytest
from langchain_openai import ChatOpenAI

from app.agents.shared.errors import LLMNotConfiguredError
from app.agents.shared.llm import build_chat_model
from app.core.settings import Settings


def test_build_chat_model_requires_configuration():
    with pytest.raises(LLMNotConfiguredError):
        build_chat_model(Settings(_env_file=None, database_url="sqlite://"))


def test_build_chat_model_points_to_configured_provider():
    settings = Settings(
        _env_file=None,
        database_url="sqlite://",
        llm_base_url="https://llm.example/api/v1",
        openrouter_api_key="test-key",
        llm_model="provider/model",
        llm_timeout_seconds=12,
        llm_max_retries=1,
    )

    model = build_chat_model(settings)

    assert isinstance(model, ChatOpenAI)
    assert model.model_name == "provider/model"
    assert model.openai_api_base == "https://llm.example/api/v1"
    assert model.request_timeout == 12
    assert model.max_retries == 1
