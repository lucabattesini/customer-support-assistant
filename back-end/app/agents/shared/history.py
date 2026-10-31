from collections.abc import Callable

from langchain.agents.middleware import AgentMiddleware, ModelRequest, ModelResponse
from langchain_core.messages import AIMessage, AnyMessage, HumanMessage, ToolMessage


def trim_history(messages: list[AnyMessage], max_turns: int) -> list[AnyMessage]:
    """Reduce the conversation sent to the model.

    A turn starts at a customer message. Only the last `max_turns` turns are kept. The
    current turn is kept intact; earlier turns keep only the customer message and the
    final assistant answer, dropping tool calls and tool results. Because every kept turn
    starts with a customer message, a tool call is never separated from its result.

    Args:
        messages: Conversation without the system prompt.
        max_turns: Number of most recent turns to keep, including the current one.

    Returns:
        The trimmed conversation.
    """
    turns = _split_turns(messages)[-max_turns:]
    if not turns:
        return []
    *previous, current = turns
    return [message for turn in previous for message in _final_exchange(turn)] + current


def _split_turns(messages: list[AnyMessage]) -> list[list[AnyMessage]]:
    turns: list[list[AnyMessage]] = []
    for message in messages:
        if isinstance(message, HumanMessage):
            turns.append([message])
        elif turns:
            turns[-1].append(message)
    return turns


def _final_exchange(turn: list[AnyMessage]) -> list[AnyMessage]:
    return [
        message
        for message in turn
        if not isinstance(message, ToolMessage)
        and not (isinstance(message, AIMessage) and message.tool_calls)
    ]


class HistoryTrimmingMiddleware(AgentMiddleware):
    """Trims the messages sent to the model without changing the stored conversation."""

    def __init__(self, max_turns: int) -> None:
        super().__init__()
        self._max_turns = max_turns

    def wrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        """Call the model with the trimmed conversation."""
        return handler(request.override(messages=trim_history(request.messages, self._max_turns)))
