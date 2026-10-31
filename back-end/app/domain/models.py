from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.domain.enums import (
    Availability,
    HandoffType,
    OrderStatus,
    PolicySectionKey,
    ProductStatus,
)


class DomainModel(BaseModel):
    """Immutable domain object that can be built from ORM instances."""

    model_config = ConfigDict(from_attributes=True, frozen=True)


class Category(DomainModel):
    """Product category."""

    category_id: int
    name: str
    description: str | None = None


class Product(DomainModel):
    """Catalog product."""

    product_id: int
    name: str
    category_id: int
    category_name: str
    price_brl: Decimal
    description: str | None = None
    stock_quantity: int
    status: ProductStatus
    specs: dict[str, Any] = {}
    created_at: date | None = None

    @property
    def availability(self) -> Availability:
        """Whether the product can be sold now, derived from status and stock."""
        if self.status is ProductStatus.DISCONTINUED:
            return Availability.DISCONTINUED
        if self.status is ProductStatus.COMING_SOON:
            return Availability.COMING_SOON
        if self.stock_quantity <= 0:
            return Availability.OUT_OF_STOCK
        return Availability.AVAILABLE


class Promotion(DomainModel):
    """Discount campaign for a product."""

    promotion_id: int
    product_id: int
    discount_percent: int
    description: str
    is_active: bool


class Customer(DomainModel):
    """Registered customer."""

    customer_id: int
    name: str
    phone: str | None = None
    email: str | None = None
    city: str | None = None


class OrderItem(DomainModel):
    """Product line of an order."""

    product_id: int
    product_name: str
    quantity: int


class Order(DomainModel):
    """Customer order with its items."""

    order_id: int
    customer_id: int
    order_date: date
    status: OrderStatus
    total_brl: Decimal
    payment_method: str
    tracking_code: str | None = None
    estimated_delivery: date | None = None
    notes: str | None = None
    items: list[OrderItem] = []


class PolicySection(DomainModel):
    """Section of the store policy manual."""

    section: PolicySectionKey
    title: str
    content: str


class Handoff(DomainModel):
    """Case forwarded to the human team."""

    handoff_id: int
    protocol: str
    type: HandoffType
    summary: str
    contact: str | None = None
    order_id: int | None = None
    created_at: datetime
