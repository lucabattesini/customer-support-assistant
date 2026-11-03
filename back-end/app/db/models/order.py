from datetime import date
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.product import ProductModel


class OrderItemModel(Base):
    """Product line of an order."""

    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.order_id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.product_id"))
    quantity: Mapped[int]

    product: Mapped[ProductModel] = relationship()

    @property
    def product_name(self) -> str:
        """Name of the ordered product."""
        return self.product.name


class OrderModel(Base):
    """Customer order."""

    __tablename__ = "orders"

    order_id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.customer_id"))
    order_date: Mapped[date]
    status: Mapped[str] = mapped_column(String(20))
    total_brl: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    payment_method: Mapped[str] = mapped_column(String(30))
    tracking_code: Mapped[str | None] = mapped_column(String(30))
    estimated_delivery: Mapped[date | None]
    notes: Mapped[str | None] = mapped_column(Text)

    items: Mapped[list[OrderItemModel]] = relationship(cascade="all, delete-orphan")
