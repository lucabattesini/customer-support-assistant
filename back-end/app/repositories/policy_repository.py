from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import PolicySectionModel
from app.domain.enums import PolicySectionKey
from app.domain.models import PolicySection


class PolicyRepository:
    """Read access to the store policy sections."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_section(self, section: PolicySectionKey) -> PolicySection | None:
        """Return a policy section, or None when it has no content yet."""
        model = self._session.get(PolicySectionModel, section.value)
        return PolicySection.model_validate(model) if model else None

    def list_sections(self) -> list[PolicySection]:
        """Return all stored policy sections ordered by key."""
        models = self._session.scalars(
            select(PolicySectionModel).order_by(PolicySectionModel.section)
        )
        return [PolicySection.model_validate(model) for model in models]
