import itertools

import httpx
import openai
import pytest
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage, ToolMessage

from app.agents.customer_support.agent import CustomerSupportAgent
from app.agents.shared.checkpointer import build_checkpointer
from app.agents.shared.errors import AgentStepLimitError, LLMUnavailableError
from app.agents.shared.prompt_builder import PromptBuilder
from app.core.settings import BASE_DIR
from app.tools.base import ToolContext
from app.tools.registry import build_tools


class ScriptedModel(GenericFakeChatModel):
    """Fake chat model that replays scripted messages and records what it receives."""

    received: list = []

    def bind_tools(self, tools, **kwargs):
        return self

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        self.received.append(list(messages))
        return super()._generate(messages, stop=stop, run_manager=run_manager, **kwargs)


class FailingModel(ScriptedModel):
    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        raise openai.APIConnectionError(request=httpx.Request("POST", "https://example.com"))


def tool_call(name, args, call_id="call_1"):
    return AIMessage(content="", tool_calls=[{"name": name, "args": args, "id": call_id}])


@pytest.fixture
def tools(session_factory, fixed_clock, store_config):
    context = ToolContext(
        session_factory=session_factory, clock=fixed_clock, store_config=store_config
    )
    return build_tools(context, PromptBuilder(BASE_DIR / "prompts").tool_description)


def build_agent(model, tools, max_turns=6, max_steps=10):
    return CustomerSupportAgent(
        model=model,
        tools=tools,
        system_prompt="You are a test assistant.",
        checkpointer=build_checkpointer(),
        max_turns=max_turns,
        max_steps=max_steps,
    )


def test_agent_runs_tool_and_returns_final_answer(tools):
    model = ScriptedModel(
        messages=iter(
            [
                tool_call("get_product_details", {"product": "northwind d-50"}),
                AIMessage(content="The D-50 costs R$ 2.199,00."),
            ]
        ),
        received=[],
    )
    agent = build_agent(model, tools)

    reply = agent.reply("thread-1", "How much is the D-50?")

    assert reply == "The D-50 costs R$ 2.199,00."
    tool_results = [m for m in model.received[1] if isinstance(m, ToolMessage)]
    assert '"list_price": "R$ 2.199,00"' in tool_results[0].content


def test_follow_up_sees_history_without_old_tool_results(tools):
    model = ScriptedModel(
        messages=iter(
            [
                tool_call("get_policy", {"section": "payment"}),
                AIMessage(content="We accept PIX."),
                AIMessage(content="Yes, up to 12 installments."),
            ]
        ),
        received=[],
    )
    agent = build_agent(model, tools)

    agent.reply("thread-1", "How can I pay?")
    agent.reply("thread-1", "Installments too?")

    follow_up_input = model.received[-1]
    assert [m.content for m in follow_up_input if m.type != "system"] == [
        "How can I pay?",
        "We accept PIX.",
        "Installments too?",
    ]


def test_threads_do_not_share_history(tools):
    model = ScriptedModel(
        messages=iter([AIMessage(content="Hi Alice"), AIMessage(content="Hi Bruno")]),
        received=[],
    )
    agent = build_agent(model, tools)

    agent.reply("alice", "Hello, I am Alice")
    agent.reply("bruno", "Hello, I am Bruno")

    assert [m.content for m in model.received[-1] if m.type == "human"] == ["Hello, I am Bruno"]


def test_step_limit_raises_domain_error(tools):
    endless_calls = (
        tool_call("get_policy", {"section": "payment"}, f"call_{i}") for i in itertools.count()
    )
    agent = build_agent(ScriptedModel(messages=endless_calls, received=[]), tools, max_steps=2)

    with pytest.raises(AgentStepLimitError):
        agent.reply("thread-1", "Loop forever")


def test_provider_failure_raises_unavailable_error(tools):
    agent = build_agent(FailingModel(messages=iter([]), received=[]), tools)

    with pytest.raises(LLMUnavailableError):
        agent.reply("thread-1", "Hello")
