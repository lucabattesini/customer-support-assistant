from typing import Literal

from pydantic import BaseModel, Field

MAX_THREAD_ID_LENGTH = 100


class ChatRequest(BaseModel):
    """Customer message, optionally continuing an existing conversation."""

    message: str = Field(min_length=1)
    thread_id: str | None = Field(default=None, min_length=1, max_length=MAX_THREAD_ID_LENGTH)


class ChatResponse(BaseModel):
    """Assistant reply and the conversation id to send with the next message."""

    thread_id: str
    reply: str


class HealthResponse(BaseModel):
    """Service status."""

    status: Literal["ok"] = "ok"
    llm_configured: bool
