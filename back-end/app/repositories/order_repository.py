from sqlalchemy import Select, select
from sqlalchemy.orm import Session, selectinload

from app.db.models import OrderItemModel, OrderModel
from app.domain.models import Order


class OrderRepository:
    """Read access to orders and their items."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, order_id: int) -> Order | None:
        """Return an order with its items, or None when it does not exist."""
        model = self._session.scalar(self._base_query().where(OrderModel.order_id == order_id))
        return Order.model_validate(model) if model else None

    def list_by_customer(self, customer_id: int) -> list[Order]:
        """Return the orders of a customer, newest first."""
        query = (
            self._base_query()
            .where(OrderModel.customer_id == customer_id)
            .order_by(OrderModel.order_date.desc(), OrderModel.order_id.desc())
        )
        return [Order.model_validate(model) for model in self._session.scalars(query)]

    def _base_query(self) -> Select[tuple[OrderModel]]:
        return select(OrderModel).options(
            selectinload(OrderModel.items).joinedload(OrderItemModel.product)
        )
