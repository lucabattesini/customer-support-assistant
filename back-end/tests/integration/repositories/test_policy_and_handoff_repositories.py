from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
from sqlalchemy import delete
from sqlalchemy.exc import IntegrityError

from app.db.models import PolicySectionModel
from app.db.session import session_scope
from app.domain.enums import HandoffType, PolicySectionKey
from app.repositories.handoff_repository import HandoffRepository
from app.repositories.policy_repository import PolicyRepository

CREATED_AT = datetime(2026, 3, 25, 10, 0, tzinfo=ZoneInfo("America/Campo_Grande"))


def create_handoff(repository, protocol="HD-1"):
    return repository.create(
        protocol=protocol,
        handoff_type=HandoffType.COMPLAINT,
        summary="Late delivery",
        contact="alice@example.com",
        order_id=3,
        created_at=CREATED_AT,
    )


def test_get_section_returns_policy(session):
    section = PolicyRepository(session).get_section(PolicySectionKey.RETURNS_EXCHANGES)

    assert section.section is PolicySectionKey.RETURNS_EXCHANGES
    assert section.title == "Returns and exchanges"


def test_list_sections_covers_every_key(session):
    keys = {section.section for section in PolicyRepository(session).list_sections()}

    assert keys == set(PolicySectionKey)


def test_get_section_returns_none_when_missing(session_factory):
    with session_scope(session_factory) as session:
        session.execute(delete(PolicySectionModel).where(PolicySectionModel.section == "privacy"))
    with session_scope(session_factory) as session:
        assert PolicyRepository(session).get_section(PolicySectionKey.PRIVACY) is None


def test_create_handoff_returns_generated_id(session):
    handoff = create_handoff(HandoffRepository(session))

    assert handoff.handoff_id > 0
    assert handoff.type is HandoffType.COMPLAINT


def test_get_by_protocol_finds_created_handoff(session_factory):
    with session_scope(session_factory) as session:
        create_handoff(HandoffRepository(session), protocol="HD-42")
    with session_scope(session_factory) as session:
        handoff = HandoffRepository(session).get_by_protocol("HD-42")

    assert handoff.summary == "Late delivery"
    assert handoff.order_id == 3


def test_protocol_is_unique(session_factory):
    with pytest.raises(IntegrityError), session_scope(session_factory) as session:
        repository = HandoffRepository(session)
        create_handoff(repository, protocol="HD-1")
        create_handoff(repository, protocol="HD-1")
