from sqlalchemy.orm import Session, sessionmaker

from app.agents.customer_support.agent import AGENT_NAME, CustomerSupportAgent
from app.agents.shared.checkpointer import build_checkpointer
from app.agents.shared.llm import build_chat_model
from app.agents.shared.prompt_builder import PromptBuilder, store_prompt_values
from app.core.clock import SystemClock
from app.core.settings import Settings
from app.core.store_config import StoreConfig
from app.tools.base import ToolContext
from app.tools.registry import build_tools


def build_customer_support_agent(
    settings: Settings,
    store_config: StoreConfig,
    session_factory: sessionmaker[Session],
) -> CustomerSupportAgent:
    """Assemble the customer support agent from configuration.

    Raises:
        LLMNotConfiguredError: When the LLM provider is not configured.
    """
    prompts = PromptBuilder(settings.prompts_dir)
    context = ToolContext(
        session_factory=session_factory,
        clock=SystemClock(store_config.locale.zone, settings.reference_date),
        store_config=store_config,
    )
    return CustomerSupportAgent(
        model=build_chat_model(settings),
        tools=build_tools(context, prompts.tool_description),
        system_prompt=prompts.build_system_prompt(AGENT_NAME, store_prompt_values(store_config)),
        checkpointer=build_checkpointer(),
        max_turns=settings.history_max_turns,
        max_steps=settings.agent_max_steps,
    )
