import json

import pytest

from app.agents.shared.prompt_builder import PromptBuilder
from app.core.settings import BASE_DIR
from app.tools.base import ToolContext
from app.tools.registry import build_tools


@pytest.fixture
def tool_context(session_factory, fixed_clock, store_config):
    return ToolContext(
        session_factory=session_factory, clock=fixed_clock, store_config=store_config
    )


@pytest.fixture
def call_tool(tool_context):
    tools = {
        tool.name: tool
        for tool in build_tools(tool_context, PromptBuilder(BASE_DIR / "prompts").tool_description)
    }

    def call(name, arguments=None):
        raw = tools[name].invoke(arguments or {})
        assert isinstance(raw, str)
        return json.loads(raw)

    return call
