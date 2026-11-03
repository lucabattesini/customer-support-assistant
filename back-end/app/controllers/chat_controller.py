from dataclasses import dataclass
from typing import Protocol
from uuid import uuid4

from app.agents.shared.errors import LLMNotConfiguredError


class ChatAgent(Protocol):
    """Anything able to answer a message within a conversation thread."""

    def reply(self, thread_id: str, message: str) -> str:
        """Return the reply to a message."""
        ...


class InvalidMessageError(ValueError):
    """The customer message is blank or exceeds the configured maximum length."""


@dataclass(frozen=True)
class ChatResult:
    """Reply produced for a message and the conversation it belongs to."""

    thread_id: str
    reply: str


class ChatController:
    """Handles the chat use case independently of the HTTP layer."""

    def __init__(self, agent: ChatAgent | None, max_message_length: int) -> None:
        self._agent = agent
        self._max_message_length = max_message_length

    def handle(self, message: str, thread_id: str | None = None) -> ChatResult:
        """Answer a message, starting a new conversation when no thread id is given.

        Raises:
            InvalidMessageError: When the message is blank or longer than allowed.
            LLMNotConfiguredError: When no agent is available.
            AgentError: When the agent fails to produce a reply.
        """
        cleaned = message.strip()
        if not cleaned:
            raise InvalidMessageError("Message must not be blank")
        if len(cleaned) > self._max_message_length:
            raise InvalidMessageError(f"Message longer than {self._max_message_length} characters")
        if self._agent is None:
            raise LLMNotConfiguredError("The assistant is not configured")
        conversation_id = thread_id or uuid4().hex
        return ChatResult(
            thread_id=conversation_id, reply=self._agent.reply(conversation_id, cleaned)
        )
