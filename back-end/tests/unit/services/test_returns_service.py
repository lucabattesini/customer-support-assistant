from datetime import date
from decimal import Decimal

import pytest

from app.domain.enums import OrderStatus, ReturnReason
from app.domain.models import Order
from app.services.returns_service import ReturnsService

PURCHASED = date(2026, 3, 1)
DELIVERED = date(2026, 3, 10)


def make_order(status=OrderStatus.DELIVERED, estimated_delivery=DELIVERED):
    return Order(
        order_id=1,
        customer_id=1,
        order_date=PURCHASED,
        status=status,
        total_brl=Decimal("599.90"),
        payment_method="pix",
        estimated_delivery=estimated_delivery,
    )


@pytest.fixture
def service(store_config):
    return ReturnsService(store_config.returns)


@pytest.mark.parametrize(
    ("reason", "today", "eligible", "deadline"),
    [
        (ReturnReason.REGRET, date(2026, 3, 17), True, date(2026, 3, 17)),
        (ReturnReason.REGRET, date(2026, 3, 18), False, date(2026, 3, 17)),
        (ReturnReason.PREFERENCE, date(2026, 3, 17), True, date(2026, 3, 17)),
        (ReturnReason.PREFERENCE, date(2026, 3, 18), False, date(2026, 3, 17)),
        (ReturnReason.DEFECT, date(2026, 3, 31), True, date(2026, 3, 31)),
        (ReturnReason.DEFECT, date(2026, 4, 1), False, date(2026, 3, 31)),
    ],
)
def test_deadlines_are_inclusive(service, reason, today, eligible, deadline):
    result = service.check(make_order(), reason, today)

    assert result.eligible is eligible
    assert result.deadline == deadline


def test_reports_days_remaining_when_eligible(service):
    result = service.check(make_order(), ReturnReason.REGRET, date(2026, 3, 15))

    assert result.days_remaining == 2
    assert result.days_exceeded is None


def test_reports_days_exceeded_when_not_eligible(service):
    result = service.check(make_order(), ReturnReason.REGRET, date(2026, 3, 25))

    assert result.days_exceeded == 8
    assert result.days_remaining is None


def test_receipt_is_based_on_estimated_delivery(service):
    result = service.check(make_order(), ReturnReason.REGRET, date(2026, 3, 15))

    assert result.based_on_estimated_delivery is True
    assert result.legal_warranty_until == date(2026, 6, 8)


@pytest.mark.parametrize(
    ("today", "active"),
    [(date(2026, 6, 8), True), (date(2026, 6, 9), False)],
)
def test_reports_whether_legal_warranty_is_still_active(service, today, active):
    result = service.check(make_order(), ReturnReason.REGRET, today)

    assert result.eligible is False
    assert result.legal_warranty_active is active


@pytest.mark.parametrize("reason", [ReturnReason.REGRET, ReturnReason.PREFERENCE])
def test_unknown_receipt_date_leaves_receipt_windows_undetermined(service, reason):
    result = service.check(make_order(estimated_delivery=None), reason, date(2026, 3, 5))

    assert result.eligible is None
    assert result.receipt_date_unknown is True
    assert result.deadline is None
    assert result.legal_warranty_until is None


def test_defect_window_does_not_need_receipt_date(service):
    result = service.check(
        make_order(estimated_delivery=None), ReturnReason.DEFECT, date(2026, 3, 5)
    )

    assert result.eligible is True
    assert result.deadline == date(2026, 3, 31)
    assert result.receipt_date_unknown is True
    assert result.based_on_estimated_delivery is False
    assert result.legal_warranty_until is None


@pytest.mark.parametrize(
    "status",
    [OrderStatus.PENDING, OrderStatus.CONFIRMED, OrderStatus.SHIPPED, OrderStatus.CANCELLED],
)
def test_orders_not_received_or_cancelled_are_blocked(service, status):
    result = service.check(make_order(status=status), ReturnReason.REGRET, date(2026, 3, 12))

    assert result.eligible is False
    assert result.blocking_status is status
    assert result.deadline is None
