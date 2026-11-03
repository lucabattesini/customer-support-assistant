import re

import pytest

from app.domain.enums import HandoffType, PolicySectionKey
from app.domain.errors import PolicySectionUnavailableError
from app.domain.models import Handoff, PolicySection
from app.services.handoff_service import HandoffService
from app.services.policy_service import PolicyService


class FakePolicyRepository:
    def __init__(self, sections):
        self._sections = {section.section: section for section in sections}

    def get_section(self, section):
        return self._sections.get(section)


class FakeHandoffRepository:
    def __init__(self):
        self.created = []

    def create(self, *, protocol, handoff_type, summary, contact, order_id, created_at):
        handoff = Handoff(
            handoff_id=len(self.created) + 1,
            protocol=protocol,
            type=handoff_type,
            summary=summary,
            contact=contact,
            order_id=order_id,
            created_at=created_at,
        )
        self.created.append(handoff)
        return handoff


def test_policy_service_returns_section():
    section = PolicySection(section=PolicySectionKey.PAYMENT, title="Payment", content="PIX")

    assert PolicyService(FakePolicyRepository([section])).get(PolicySectionKey.PAYMENT) == section


def test_policy_service_raises_when_section_missing():
    with pytest.raises(PolicySectionUnavailableError) as error:
        PolicyService(FakePolicyRepository([])).get(PolicySectionKey.PRIVACY)

    assert error.value.details == {"section": "privacy"}


def test_handoff_service_creates_protocol_and_normalizes_input(store_config, fixed_clock):
    repository = FakeHandoffRepository()
    service = HandoffService(repository, store_config.handoff)

    handoff = service.create(
        handoff_type=HandoffType.COMPLAINT,
        summary="  Late delivery  ",
        contact="   ",
        order_id=3,
        now=fixed_clock.now(),
    )

    assert re.fullmatch(r"HD-20260325-[0-9A-F]{8}", handoff.protocol)
    assert handoff.summary == "Late delivery"
    assert handoff.contact is None
    assert service.response_time_hours == 24


def test_handoff_protocols_are_unique(store_config, fixed_clock):
    service = HandoffService(FakeHandoffRepository(), store_config.handoff)

    protocols = {
        service.create(
            handoff_type=HandoffType.OTHER, summary="Case", now=fixed_clock.now()
        ).protocol
        for _ in range(50)
    }

    assert len(protocols) == 50
