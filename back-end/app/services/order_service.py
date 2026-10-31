from app.core.text import digits_only
from app.domain.errors import MissingContactError, VerificationFailedError
from app.domain.models import Customer, Order
from app.repositories.customer_repository import CustomerRepository
from app.repositories.order_repository import OrderRepository

MIN_PHONE_DIGITS = 8


class OrderService:
    """Order lookup protected by customer identity verification."""

    def __init__(self, orders: OrderRepository, customers: CustomerRepository) -> None:
        self._orders = orders
        self._customers = customers

    def get_verified_order(
        self, order_id: int, email: str | None = None, phone: str | None = None
    ) -> Order:
        """Return an order only when a provided contact matches the order customer.

        Args:
            order_id: Order number informed by the customer.
            email: Email informed by the customer.
            phone: Phone informed by the customer, in any format.

        Returns:
            The verified order.

        Raises:
            MissingContactError: When neither email nor phone is provided.
            VerificationFailedError: When the order does not exist or no contact matches.
        """
        if not (email and email.strip()) and not (phone and phone.strip()):
            raise MissingContactError()
        order = self._orders.get_by_id(order_id)
        customer = self._customers.get_by_id(order.customer_id) if order else None
        if order is None or customer is None or not _contact_matches(customer, email, phone):
            raise VerificationFailedError()
        return order


def _contact_matches(customer: Customer, email: str | None, phone: str | None) -> bool:
    return _emails_match(customer.email, email) or _phones_match(customer.phone, phone)


def _emails_match(stored: str | None, informed: str | None) -> bool:
    if not stored or not informed:
        return False
    return stored.strip().lower() == informed.strip().lower()


def _phones_match(stored: str | None, informed: str | None) -> bool:
    """Compare phones by digits, accepting a missing country or area code prefix."""
    if not stored or not informed:
        return False
    stored_digits, informed_digits = digits_only(stored), digits_only(informed)
    shorter, longer = sorted((stored_digits, informed_digits), key=len)
    return len(shorter) >= MIN_PHONE_DIGITS and longer.endswith(shorter)
