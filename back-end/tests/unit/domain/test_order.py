from datetime import date
from decimal import Decimal

import pytest

from app.domain.enums import OrderStatus
from app.domain.models import Order

ESTIMATED = date(2026, 3, 20)


def make_order(status, estimated_delivery=ESTIMATED):
    return Order(
        order_id=1,
        customer_id=1,
        order_date=date(2026, 3, 10),
        status=status,
        total_brl=Decimal("599.90"),
        payment_method="pix",
        estimated_delivery=estimated_delivery,
    )


@pytest.mark.parametrize(
    "status", [OrderStatus.PENDING, OrderStatus.CONFIRMED, OrderStatus.SHIPPED]
)
def test_order_in_progress_after_estimated_delivery_is_overdue(status):
    assert make_order(status).is_delivery_overdue(date(2026, 3, 21)) is True


@pytest.mark.parametrize("today", [date(2026, 3, 19), ESTIMATED])
def test_order_is_not_overdue_until_the_estimated_date_passes(today):
    assert make_order(OrderStatus.SHIPPED).is_delivery_overdue(today) is False


@pytest.mark.parametrize("status", [OrderStatus.DELIVERED, OrderStatus.CANCELLED])
def test_finished_orders_are_never_overdue(status):
    assert make_order(status).is_delivery_overdue(date(2026, 4, 30)) is False


def test_order_without_estimated_delivery_is_not_overdue():
    order = make_order(OrderStatus.CONFIRMED, estimated_delivery=None)

    assert order.is_delivery_overdue(date(2026, 4, 30)) is False
