import openai
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI

from app.agents.shared.errors import LLMNotConfiguredError
from app.core.settings import Settings

PROVIDER_ERRORS: tuple[type[Exception], ...] = (openai.OpenAIError,)


def build_chat_model(settings: Settings) -> BaseChatModel:
    """Create the chat model served through the OpenRouter OpenAI-compatible API.

    Raises:
        LLMNotConfiguredError: When the API key or the model name is missing.
    """
    if not settings.llm_configured:
        raise LLMNotConfiguredError("OPENROUTER_API_KEY and LLM_MODEL must be set")
    return ChatOpenAI(
        model=settings.llm_model,
        base_url=settings.llm_base_url,
        api_key=settings.openrouter_api_key,
        timeout=settings.llm_timeout_seconds,
        max_retries=settings.llm_max_retries,
    )
