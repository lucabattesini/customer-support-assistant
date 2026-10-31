from collections.abc import Collection
from decimal import Decimal

from sqlalchemy import Select, select
from sqlalchemy.orm import Session, joinedload

from app.db.models import ProductModel
from app.domain.enums import ProductStatus
from app.domain.models import Product


class ProductRepository:
    """Read access to catalog products."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, product_id: int) -> Product | None:
        """Return a product by id, or None when it does not exist."""
        model = self._session.scalar(
            self._base_query().where(ProductModel.product_id == product_id)
        )
        return Product.model_validate(model) if model else None

    def list_all(self) -> list[Product]:
        """Return every product ordered by id."""
        return self._fetch(self._base_query())

    def list_by_filters(
        self,
        *,
        category_ids: Collection[int] | None = None,
        min_price: Decimal | None = None,
        max_price: Decimal | None = None,
        statuses: Collection[ProductStatus] | None = None,
        in_stock: bool | None = None,
    ) -> list[Product]:
        """Return products matching every filter that is provided.

        Args:
            category_ids: Restrict to these categories.
            min_price: Minimum list price, inclusive.
            max_price: Maximum list price, inclusive.
            statuses: Restrict to these catalog statuses.
            in_stock: When True only products with stock, when False only without stock.

        Returns:
            Matching products ordered by id.
        """
        query = self._base_query()
        if category_ids is not None:
            query = query.where(ProductModel.category_id.in_(category_ids))
        if min_price is not None:
            query = query.where(ProductModel.price_brl >= min_price)
        if max_price is not None:
            query = query.where(ProductModel.price_brl <= max_price)
        if statuses is not None:
            query = query.where(ProductModel.status.in_([status.value for status in statuses]))
        if in_stock is True:
            query = query.where(ProductModel.stock_quantity > 0)
        if in_stock is False:
            query = query.where(ProductModel.stock_quantity <= 0)
        return self._fetch(query)

    def _base_query(self) -> Select[tuple[ProductModel]]:
        return (
            select(ProductModel)
            .options(joinedload(ProductModel.category))
            .order_by(ProductModel.product_id)
        )

    def _fetch(self, query: Select[tuple[ProductModel]]) -> list[Product]:
        return [Product.model_validate(model) for model in self._session.scalars(query)]
