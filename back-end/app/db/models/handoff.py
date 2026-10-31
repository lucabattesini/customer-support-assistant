from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class HandoffModel(Base):
    """Case forwarded by the assistant to the human support team.

    `order_id` is intentionally not a foreign key: customers may mention order numbers
    that do not exist, and the case must still be recorded for the team.
    """

    __tablename__ = "handoffs"

    handoff_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    protocol: Mapped[str] = mapped_column(String(30), unique=True)
    type: Mapped[str] = mapped_column(String(30))
    summary: Mapped[str] = mapped_column(Text)
    contact: Mapped[str | None] = mapped_column(String(200))
    order_id: Mapped[int | None]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
