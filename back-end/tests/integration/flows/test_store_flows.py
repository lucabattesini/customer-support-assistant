import re

from sqlalchemy import delete

from app.db.models import PolicySectionModel
from app.db.session import session_scope
from app.repositories.handoff_repository import HandoffRepository


def test_policy_section_is_returned(call_tool):
    assert call_tool("get_policy", {"section": "returns_exchanges"}) == {
        "section": "returns_exchanges",
        "title": "Returns and exchanges",
        "content": "Regret within 7 days of receipt.",
    }


def test_missing_policy_section_suggests_handoff(call_tool, session_factory):
    with session_scope(session_factory) as session:
        session.execute(delete(PolicySectionModel).where(PolicySectionModel.section == "shipping"))

    assert call_tool("get_policy", {"section": "shipping"}) == {
        "error": "section_unavailable",
        "action": "offer_handoff",
        "section": "shipping",
    }


def test_current_datetime_uses_store_clock(call_tool):
    assert call_tool("get_current_datetime") == {
        "date": "2026-03-25",
        "time": "10:00",
        "weekday": "wednesday",
        "timezone": "America/Campo_Grande",
        "is_open": True,
        "today_hours": "09:00-18:00",
        "next_opening": None,
    }


def test_handoff_is_persisted_and_returns_protocol(call_tool, session_factory):
    payload = call_tool(
        "handoff_to_human",
        {
            "case_type": "complaint",
            "summary": "Order 3 arrived damaged",
            "contact": "bruno@example.com",
            "order_id": 3,
        },
    )

    assert re.fullmatch(r"HD-20260325-[0-9A-F]{8}", payload["protocol"])
    assert payload["response_time_hours"] == 24
    with session_scope(session_factory) as session:
        stored = HandoffRepository(session).get_by_protocol(payload["protocol"])
    assert stored.summary == "Order 3 arrived damaged"
    assert stored.order_id == 3
