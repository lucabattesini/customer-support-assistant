from sqlalchemy.orm import Session

from app.db.models import CustomerModel
from app.domain.models import Customer


class CustomerRepository:
    """Read access to customers."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, customer_id: int) -> Customer | None:
        """Return a customer by id, or None when it does not exist."""
        model = self._session.get(CustomerModel, customer_id)
        return Customer.model_validate(model) if model else None
