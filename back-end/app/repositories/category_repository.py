from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import CategoryModel
from app.domain.models import Category


class CategoryRepository:
    """Read access to product categories."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def list_all(self) -> list[Category]:
        """Return all categories ordered by id."""
        models = self._session.scalars(select(CategoryModel).order_by(CategoryModel.category_id))
        return [Category.model_validate(model) for model in models]
