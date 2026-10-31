from pydantic import BaseModel

from app.domain.enums import PolicySectionKey
from app.tools.base import Payload, ToolContext, ToolSpec


class GetPolicyInput(BaseModel):
    """Arguments of `get_policy`."""

    section: PolicySectionKey


def get_policy(context: ToolContext, arguments: GetPolicyInput) -> Payload:
    """Return the content of a store policy section."""
    with context.services() as services:
        policy = services.policies.get(arguments.section)
    return {"section": policy.section.value, "title": policy.title, "content": policy.content}


TOOL = ToolSpec(name="get_policy", input_model=GetPolicyInput, handler=get_policy)
