import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.agents.shared.errors import AgentError, LLMNotConfiguredError
from app.api.dependencies import get_chat_controller
from app.api.schemas.chat_schemas import ChatRequest, ChatResponse
from app.controllers.chat_controller import ChatController, InvalidMessageError

logger = logging.getLogger(__name__)

router = APIRouter(tags=["chat"])


@router.post("/chat")
def chat(
    request: ChatRequest,
    controller: Annotated[ChatController, Depends(get_chat_controller)],
) -> ChatResponse:
    """Send a customer message and receive the assistant reply."""
    try:
        result = controller.handle(request.message, request.thread_id)
    except InvalidMessageError as error:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, str(error)) from error
    except LLMNotConfiguredError as error:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "The assistant is not configured: set OPENROUTER_API_KEY and LLM_MODEL",
        ) from error
    except AgentError as error:
        logger.warning("Agent failed to reply: %s", error)
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "The assistant could not answer right now, please try again",
        ) from error
    return ChatResponse(thread_id=result.thread_id, reply=result.reply)
