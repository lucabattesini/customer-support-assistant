from typing import Annotated

from app.domain.enums import ReturnReason
from app.tools.base import Payload, ToolContext, ToolSpec, enum_schema, without_none
from app.tools.get_order_status import OrderLookupInput


class CheckReturnEligibilityInput(OrderLookupInput):
    """Order lookup arguments plus the reason for the return or exchange."""

    reason: Annotated[ReturnReason, enum_schema(ReturnReason)]


def check_return_eligibility(
    context: ToolContext, arguments: CheckReturnEligibilityInput
) -> Payload:
    """Verify the order and evaluate return, exchange and warranty deadlines for today."""
    with context.services() as services:
        order = services.orders.get_verified_order(
            arguments.order_id, email=arguments.email, phone=arguments.phone
        )
        result = services.returns.check(order, arguments.reason, context.clock.today())
    return without_none(
        {
            "order_id": result.order_id,
            "reason": result.reason.value,
            "eligible": result.eligible,
            "blocking_status": result.blocking_status.value if result.blocking_status else None,
            "receipt_date_unknown": result.receipt_date_unknown or None,
            "deadline": result.deadline.isoformat() if result.deadline else None,
            "days_remaining": result.days_remaining,
            "days_exceeded": result.days_exceeded,
            "based_on_estimated_delivery": result.based_on_estimated_delivery,
            "legal_warranty_until": (
                result.legal_warranty_until.isoformat() if result.legal_warranty_until else None
            ),
            "legal_warranty_active": result.legal_warranty_active,
        }
    )


TOOL = ToolSpec(
    name="check_return_eligibility",
    input_model=CheckReturnEligibilityInput,
    handler=check_return_eligibility,
)
