from datetime import date
from decimal import Decimal

from app.domain.enums import OrderStatus
from app.repositories.customer_repository import CustomerRepository
from app.repositories.order_repository import OrderRepository


def test_get_by_id_includes_items_with_product_names(session):
    order = OrderRepository(session).get_by_id(4)

    assert order.status is OrderStatus.CONFIRMED
    assert order.total_brl == Decimal("3698.90")
    assert [(item.product_name, item.quantity) for item in order.items] == [
        ("Acme E-300 Electric", 1),
        ("Northwind U-1 Soprano Ukulele", 1),
    ]


def test_get_by_id_maps_optional_fields(session):
    order = OrderRepository(session).get_by_id(1)

    assert order.tracking_code == "BRAA1234567BR"
    assert order.estimated_delivery == date(2026, 3, 10)


def test_get_by_id_returns_none_when_missing(session):
    assert OrderRepository(session).get_by_id(999) is None


def test_list_by_customer_is_newest_first(session):
    orders = OrderRepository(session).list_by_customer(1)

    assert [order.order_id for order in orders] == [2, 1]


def test_order_items_stay_usable_after_session_closes(session_factory):
    with session_factory() as session:
        order = OrderRepository(session).get_by_id(4)

    assert order.items[0].product_name == "Acme E-300 Electric"


def test_customer_repository_gets_customer(session):
    customer = CustomerRepository(session).get_by_id(1)

    assert customer.email == "alice@example.com"
    assert CustomerRepository(session).get_by_id(999) is None
