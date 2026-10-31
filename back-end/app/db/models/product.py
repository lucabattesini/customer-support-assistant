from datetime import date
from decimal import Decimal
from typing import Any

from sqlalchemy import JSON, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.category import CategoryModel


class ProductModel(Base):
    """Catalog product."""

    __tablename__ = "products"

    product_id: Mapped[int] = mapped_column(primary_key=True)
    price_brl: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    name: Mapped[str] = mapped_column(String(200))
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.category_id"))
    description: Mapped[str | None] = mapped_column(Text)
    stock_quantity: Mapped[int]
    status: Mapped[str] = mapped_column(String(20))
    specs: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[date | None]

    category: Mapped[CategoryModel] = relationship()
