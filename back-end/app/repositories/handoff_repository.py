from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import HandoffModel
from app.domain.enums import HandoffType
from app.domain.models import Handoff


class HandoffRepository:
    """Persistence of cases forwarded to the human team."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def create(
        self,
        *,
        protocol: str,
        handoff_type: HandoffType,
        summary: str,
        contact: str | None,
        order_id: int | None,
        created_at: datetime,
    ) -> Handoff:
        """Store a new handoff and return it with its generated id."""
        model = HandoffModel(
            protocol=protocol,
            type=handoff_type.value,
            summary=summary,
            contact=contact,
            order_id=order_id,
            created_at=created_at,
        )
        self._session.add(model)
        self._session.flush()
        return Handoff.model_validate(model)

    def get_by_protocol(self, protocol: str) -> Handoff | None:
        """Return a handoff by protocol, or None when it does not exist."""
        model = self._session.scalar(select(HandoffModel).where(HandoffModel.protocol == protocol))
        return Handoff.model_validate(model) if model else None
