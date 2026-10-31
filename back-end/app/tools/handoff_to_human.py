from typing import Annotated

from pydantic import BaseModel, Field

from app.domain.enums import HandoffType
from app.tools.base import Payload, ToolContext, ToolSpec, enum_schema

MAX_SUMMARY_LENGTH = 500


class HandoffToHumanInput(BaseModel):
    """Arguments of `handoff_to_human`."""

    case_type: Annotated[HandoffType, enum_schema(HandoffType)]
    summary: str = Field(min_length=1, max_length=MAX_SUMMARY_LENGTH)
    contact: str | None = Field(default=None, max_length=200)
    order_id: int | None = Field(default=None, ge=1)


def handoff_to_human(context: ToolContext, arguments: HandoffToHumanInput) -> Payload:
    """Register the case and return the protocol and expected response time."""
    with context.services() as services:
        handoff = services.handoffs.create(
            handoff_type=arguments.case_type,
            summary=arguments.summary,
            contact=arguments.contact,
            order_id=arguments.order_id,
            now=context.clock.now(),
        )
        response_time_hours = services.handoffs.response_time_hours
    return {
        "protocol": handoff.protocol,
        "response_time_hours": response_time_hours,
        "created_at": handoff.created_at.isoformat(),
    }


TOOL = ToolSpec(name="handoff_to_human", input_model=HandoffToHumanInput, handler=handoff_to_human)
