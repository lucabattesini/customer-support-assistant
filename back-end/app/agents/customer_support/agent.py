from langchain.agents import create_agent
from langchain.agents.middleware import ModelCallLimitMiddleware
from langchain.agents.middleware.model_call_limit import ModelCallLimitExceededError
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.tools import BaseTool
from langgraph.types import Checkpointer

from app.agents.shared.errors import AgentStepLimitError, LLMUnavailableError
from app.agents.shared.history import HistoryTrimmingMiddleware
from app.agents.shared.llm import PROVIDER_ERRORS

AGENT_NAME = "customer_support"


class CustomerSupportAgent:
    """Single tool-calling agent that answers customers of the store."""

    def __init__(
        self,
        *,
        model: BaseChatModel,
        tools: list[BaseTool],
        system_prompt: str,
        checkpointer: Checkpointer,
        max_turns: int,
        max_steps: int,
    ) -> None:
        self._graph = create_agent(
            model=model,
            tools=tools,
            system_prompt=system_prompt,
            middleware=[
                HistoryTrimmingMiddleware(max_turns),
                ModelCallLimitMiddleware(run_limit=max_steps, exit_behavior="error"),
            ],
            checkpointer=checkpointer,
            name=AGENT_NAME,
        )

    def reply(self, thread_id: str, message: str) -> str:
        """Answer a customer message within a conversation thread.

        Args:
            thread_id: Conversation identifier; messages with the same id share history.
            message: Customer message.

        Returns:
            The assistant reply text.

        Raises:
            AgentStepLimitError: When the agent needs more model calls than allowed.
            LLMUnavailableError: When the LLM provider fails.
        """
        try:
            result = self._graph.invoke(
                {"messages": [HumanMessage(content=message)]},
                config={"configurable": {"thread_id": thread_id}},
            )
        except ModelCallLimitExceededError as error:
            raise AgentStepLimitError(str(error)) from error
        except PROVIDER_ERRORS as error:
            raise LLMUnavailableError(str(error)) from error
        return _last_answer(result["messages"])


def _last_answer(messages: list) -> str:
    answer = next(message for message in reversed(messages) if isinstance(message, AIMessage))
    return answer.text
