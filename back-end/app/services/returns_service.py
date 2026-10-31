from dataclasses import dataclass
from datetime import date, timedelta

from app.core.store_config import ReturnsConfig
from app.domain.enums import OrderStatus, ReturnReason
from app.domain.models import Order

NOT_RECEIVED_STATUSES = {OrderStatus.PENDING, OrderStatus.CONFIRMED, OrderStatus.SHIPPED}


@dataclass(frozen=True)
class ReturnEligibility:
    """Outcome of a return or exchange eligibility check.

    `blocking_status` is set when the order status alone prevents the request
    (cancelled or not received yet); in that case no deadline is computed.
    """

    order_id: int
    reason: ReturnReason
    eligible: bool
    blocking_status: OrderStatus | None = None
    deadline: date | None = None
    days_remaining: int | None = None
    days_exceeded: int | None = None
    based_on_estimated_delivery: bool = False
    legal_warranty_until: date | None = None


class ReturnsService:
    """Applies return, exchange and warranty deadlines to an order.

    Deadlines are inclusive: with a 7-day window starting on day D, day D+7 is still valid.
    Regret and preference count from receipt, defect counts from purchase. The receipt date
    is the order estimated delivery, since the data has no actual delivery date.
    """

    def __init__(self, rules: ReturnsConfig) -> None:
        self._rules = rules

    def check(self, order: Order, reason: ReturnReason, today: date) -> ReturnEligibility:
        """Check whether an order can be returned or exchanged for a reason on a date."""
        if order.status is OrderStatus.CANCELLED or order.status in NOT_RECEIVED_STATUSES:
            return ReturnEligibility(
                order_id=order.order_id,
                reason=reason,
                eligible=False,
                blocking_status=order.status,
            )

        received_on = order.estimated_delivery or order.order_date
        start, window_days = self._window(order, reason, received_on)
        deadline = start + timedelta(days=window_days)
        eligible = today <= deadline
        return ReturnEligibility(
            order_id=order.order_id,
            reason=reason,
            eligible=eligible,
            deadline=deadline,
            days_remaining=(deadline - today).days if eligible else None,
            days_exceeded=None if eligible else (today - deadline).days,
            based_on_estimated_delivery=order.estimated_delivery is not None,
            legal_warranty_until=received_on + timedelta(days=self._rules.legal_warranty_days),
        )

    def _window(self, order: Order, reason: ReturnReason, received_on: date) -> tuple[date, int]:
        if reason is ReturnReason.DEFECT:
            return order.order_date, self._rules.defect_days
        if reason is ReturnReason.PREFERENCE:
            return received_on, self._rules.preference_days
        return received_on, self._rules.regret_days
