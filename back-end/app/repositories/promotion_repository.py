from collections.abc import Collection

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import PromotionModel
from app.domain.models import Promotion


class PromotionRepository:
    """Read access to product promotions."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def list_active(self, product_ids: Collection[int] | None = None) -> list[Promotion]:
        """Return active promotions, optionally restricted to some products."""
        query = select(PromotionModel).where(PromotionModel.is_active.is_(True))
        if product_ids is not None:
            query = query.where(PromotionModel.product_id.in_(product_ids))
        models = self._session.scalars(query.order_by(PromotionModel.promotion_id))
        return [Promotion.model_validate(model) for model in models]

    def list_for_product(self, product_id: int) -> list[Promotion]:
        """Return every promotion of a product, active or not."""
        query = (
            select(PromotionModel)
            .where(PromotionModel.product_id == product_id)
            .order_by(PromotionModel.promotion_id)
        )
        return [Promotion.model_validate(model) for model in self._session.scalars(query)]
