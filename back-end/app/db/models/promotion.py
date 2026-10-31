from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PromotionModel(Base):
    """Discount campaign applied to a single product."""

    __tablename__ = "promotions"

    promotion_id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.product_id"))
    discount_percent: Mapped[int]
    description: Mapped[str] = mapped_column(String(100))
    is_active: Mapped[bool]
