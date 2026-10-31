from collections.abc import Collection
from typing import Any

from langchain_core.tools import BaseTool, StructuredTool
from pydantic import BaseModel

from app.agents.shared.prompt_builder import PromptBuilder
from app.tools import (
    check_return_eligibility,
    get_current_datetime,
    get_order_status,
    get_policy,
    get_product_details,
    handoff_to_human,
    search_products,
)
from app.tools.base import ToolContext, ToolSpec, execute_tool, validation_error_payload

TOOL_SPECS: tuple[ToolSpec[Any], ...] = (
    search_products.TOOL,
    get_product_details.TOOL,
    get_order_status.TOOL,
    check_return_eligibility.TOOL,
    get_policy.TOOL,
    get_current_datetime.TOOL,
    handoff_to_human.TOOL,
)


def build_tools(
    context: ToolContext, prompts: PromptBuilder, names: Collection[str] | None = None
) -> list[BaseTool]:
    """Build LangChain tools from the tool specs.

    Args:
        context: Dependencies shared by the tools.
        prompts: Source of the tool descriptions shown to the model.
        names: Optional subset of tools to build; all tools when omitted.

    Returns:
        The tools, in the order of `TOOL_SPECS`.
    """
    unknown = set(names or ()) - {spec.name for spec in TOOL_SPECS}
    if unknown:
        raise ValueError(f"Unknown tools: {sorted(unknown)}")
    return [
        _to_langchain_tool(spec, context, prompts)
        for spec in TOOL_SPECS
        if names is None or spec.name in names
    ]


def _to_langchain_tool[InputT: BaseModel](
    spec: ToolSpec[InputT], context: ToolContext, prompts: PromptBuilder
) -> BaseTool:
    def run(**arguments: Any) -> str:
        return execute_tool(spec, context, spec.input_model.model_validate(arguments))

    return StructuredTool.from_function(
        func=run,
        name=spec.name,
        description=prompts.tool_description(spec.name),
        args_schema=spec.input_model,
        handle_validation_error=validation_error_payload,
    )
