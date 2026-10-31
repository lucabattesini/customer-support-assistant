import json

import pytest
from pydantic import BaseModel

from app.agents.shared.prompt_builder import PromptBuilder
from app.core.settings import BASE_DIR
from app.domain.errors import UnknownCategoryError
from app.tools.base import ToolContext, ToolSpec, execute_tool
from app.tools.registry import TOOL_SPECS, build_tools


class EmptyInput(BaseModel):
    pass


@pytest.fixture
def context(store_config, fixed_clock):
    return ToolContext(session_factory=None, clock=fixed_clock, store_config=store_config)


@pytest.fixture
def prompts():
    return PromptBuilder(BASE_DIR / "prompts")


def run_handler(handler, context):
    spec = ToolSpec(name="demo", input_model=EmptyInput, handler=handler)
    return json.loads(execute_tool(spec, context, EmptyInput()))


def test_successful_payload_is_returned_as_json(context):
    assert run_handler(lambda ctx, args: {"price": "R$ 1,00", "name": "Violão"}, context) == {
        "price": "R$ 1,00",
        "name": "Violão",
    }


def test_domain_error_becomes_actionable_payload(context):
    def handler(ctx, args):
        raise UnknownCategoryError({"available_categories": ["Ukuleles"]})

    assert run_handler(handler, context) == {
        "error": "unknown_category",
        "action": "offer_available_categories",
        "available_categories": ["Ukuleles"],
    }


def test_unexpected_error_is_logged_and_hidden(context, caplog):
    def handler(ctx, args):
        raise RuntimeError("database exploded")

    payload = run_handler(handler, context)

    assert payload == {"error": "internal_error", "action": "apologize_and_offer_handoff"}
    assert "database exploded" in caplog.text


def test_registry_builds_every_tool_with_its_description(context, prompts):
    tools = build_tools(context, prompts.tool_description)

    assert [tool.name for tool in tools] == [spec.name for spec in TOOL_SPECS]
    assert all(tool.description == prompts.tool_description(tool.name) for tool in tools)


def test_registry_builds_a_subset(context, prompts):
    tools = build_tools(context, prompts.tool_description, names=["get_policy"])

    assert [tool.name for tool in tools] == ["get_policy"]


def test_registry_rejects_unknown_tool_names(context, prompts):
    with pytest.raises(ValueError, match="nope"):
        build_tools(context, prompts.tool_description, names=["nope"])


@pytest.mark.parametrize(
    ("tool_name", "arguments", "field"),
    [
        ("search_products", {"max_price": "R$1000"}, "max_price"),
        ("search_products", {"limit": 50}, "limit"),
        ("get_product_details", {"product": ""}, "product"),
        ("get_order_status", {"email": "a@b.com"}, "order_id"),
        ("check_return_eligibility", {"order_id": 1, "reason": "bored"}, "reason"),
        ("get_policy", {"section": "secret_recipes"}, "section"),
        ("handoff_to_human", {"case_type": "complaint", "summary": ""}, "summary"),
    ],
)
def test_invalid_arguments_return_error_instead_of_raising(
    context, prompts, tool_name, arguments, field
):
    tool = next(
        tool for tool in build_tools(context, prompts.tool_description) if tool.name == tool_name
    )

    payload = json.loads(tool.invoke(arguments))

    assert payload["error"] == "invalid_arguments"
    assert field in {item["field"] for item in payload["fields"]}
