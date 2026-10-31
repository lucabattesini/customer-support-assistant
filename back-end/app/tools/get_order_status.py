from pydantic import BaseModel, Field

from app.domain.enums import OrderStatus
from app.domain.models import Order
from app.tools.base import Payload, ToolContext, ToolSpec, without_none
from app.tools.serializers import money


class OrderLookupInput(BaseModel):
    """Order number plus the contact used to verify the customer identity."""

    order_id: int = Field(ge=1)
    email: str | None = Field(default=None, max_length=200)
    phone: str | None = Field(default=None, max_length=30)


def get_order_status(context: ToolContext, arguments: OrderLookupInput) -> Payload:
    """Return the verified order status, items and delivery information."""
    with context.services() as services:
        order = services.orders.get_verified_order(
            arguments.order_id, email=arguments.email, phone=arguments.phone
        )
    return order_payload(order, context)


def order_payload(order: Order, context: ToolContext) -> Payload:
    """Customer-safe representation of an order."""
    cancelled = order.status is OrderStatus.CANCELLED
    return without_none(
        {
            "order_id": order.order_id,
            "status": order.status.value,
            "order_date": order.order_date.isoformat(),
            "items": [
                {"name": item.product_name, "quantity": item.quantity} for item in order.items
            ],
            "total": money(order.total_brl, context.store_config.locale),
            "payment_method": order.payment_method,
            "tracking_code": order.tracking_code,
            "estimated_delivery": (
                order.estimated_delivery.isoformat() if order.estimated_delivery else None
            ),
            "cancellation_reason": order.notes if cancelled else None,
        }
    )


TOOL = ToolSpec(name="get_order_status", input_model=OrderLookupInput, handler=get_order_status)
