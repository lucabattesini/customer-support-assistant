from collections.abc import Callable

from langchain.agents.middleware import AgentMiddleware, ModelRequest, ModelResponse
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI

from app.agents.shared.errors import LLMNotConfiguredError, LLMUnavailableError
from app.core.settings import Settings


def build_chat_model(settings: Settings) -> BaseChatModel:
    """Create the chat model served through the OpenRouter OpenAI-compatible API.

    Raises:
        LLMNotConfiguredError: When the provider URL, API key or model name is missing.
    """
    if not settings.llm_configured:
        raise LLMNotConfiguredError("LLM_BASE_URL, OPENROUTER_API_KEY and LLM_MODEL must be set")
    return ChatOpenAI(
        model=settings.llm_model,
        base_url=settings.llm_base_url,
        api_key=settings.openrouter_api_key,
        timeout=settings.llm_timeout_seconds,
        max_retries=settings.llm_max_retries,
    )


class ProviderErrorMiddleware(AgentMiddleware):
    """Turns any failure of the model call into `LLMUnavailableError`.

    Providers fail in several shapes: HTTP errors, timeouts, and error bodies returned with
    HTTP 200 that the client library surfaces as `ValueError` or `TypeError`. Only the model
    call is wrapped, so bugs in tools or in the graph are not disguised as provider outages.
    """

    def wrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        """Call the model, translating provider failures."""
        try:
            return handler(request)
        except Exception as error:
            raise LLMUnavailableError(f"{type(error).__name__}: {error}") from error
