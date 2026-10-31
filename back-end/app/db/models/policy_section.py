from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PolicySectionModel(Base):
    """Section of the store policy manual, identified by a stable key."""

    __tablename__ = "policy_sections"

    section: Mapped[str] = mapped_column(String(50), primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text)
