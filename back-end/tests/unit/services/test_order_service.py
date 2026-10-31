from datetime import date
from decimal import Decimal

import pytest

from app.domain.enums import OrderStatus
from app.domain.errors import MissingContactError, VerificationFailedError
from app.domain.models import Customer, Order
from app.services.order_service import OrderService

ORDER = Order(
    order_id=14,
    customer_id=1,
    order_date=date(2026, 3, 15),
    status=OrderStatus.PENDING,
    total_brl=Decimal("1749"),
    payment_method="debit",
)
CUSTOMER = Customer(
    customer_id=1, name="Alice", phone="(67) 99812-3456", email="Alice.Martins@Example.com"
)


class FakeOrderRepository:
    def get_by_id(self, order_id):
        return ORDER if order_id == ORDER.order_id else None


class FakeCustomerRepository:
    def get_by_id(self, customer_id):
        return CUSTOMER if customer_id == CUSTOMER.customer_id else None


@pytest.fixture
def service():
    return OrderService(FakeOrderRepository(), FakeCustomerRepository())


@pytest.mark.parametrize(
    ("email", "phone"),
    [
        ("alice.martins@example.com", None),
        ("  ALICE.MARTINS@EXAMPLE.COM ", None),
        (None, "(67) 99812-3456"),
        (None, "67998123456"),
        (None, "+55 67 99812-3456"),
        (None, "99812-3456"),
        ("wrong@example.com", "67 99812 3456"),
    ],
)
def test_matching_contact_returns_order(service, email, phone):
    assert service.get_verified_order(14, email=email, phone=phone).order_id == 14


@pytest.mark.parametrize(("email", "phone"), [(None, None), ("", "  ")])
def test_missing_contact_is_rejected(service, email, phone):
    with pytest.raises(MissingContactError):
        service.get_verified_order(14, email=email, phone=phone)


@pytest.mark.parametrize(
    ("order_id", "email", "phone"),
    [
        (14, "someone@example.com", None),
        (14, None, "3456"),
        (14, None, "(67) 99999-0000"),
        (999, "alice.martins@example.com", None),
    ],
)
def test_wrong_contact_and_unknown_order_fail_the_same_way(service, order_id, email, phone):
    with pytest.raises(VerificationFailedError) as error:
        service.get_verified_order(order_id, email=email, phone=phone)

    assert error.value.details == {}
