import secrets
from datetime import datetime

from app.core.store_config import HandoffConfig
from app.domain.enums import HandoffType
from app.domain.models import Handoff
from app.repositories.handoff_repository import HandoffRepository

PROTOCOL_TOKEN_BYTES = 4


class HandoffService:
    """Registers cases that need the human support team."""

    def __init__(self, handoffs: HandoffRepository, config: HandoffConfig) -> None:
        self._handoffs = handoffs
        self._config = config

    @property
    def response_time_hours(self) -> int:
        """Business hours the team takes to answer a handoff."""
        return self._config.response_time_hours

    def create(
        self,
        *,
        handoff_type: HandoffType,
        summary: str,
        now: datetime,
        contact: str | None = None,
        order_id: int | None = None,
    ) -> Handoff:
        """Register a handoff with a unique protocol such as `HD-20260325-1A2B3C4D`."""
        return self._handoffs.create(
            protocol=_new_protocol(now),
            handoff_type=handoff_type,
            summary=summary.strip(),
            contact=contact.strip() if contact and contact.strip() else None,
            order_id=order_id,
            created_at=now,
        )


def _new_protocol(now: datetime) -> str:
    return f"HD-{now:%Y%m%d}-{secrets.token_hex(PROTOCOL_TOKEN_BYTES).upper()}"
