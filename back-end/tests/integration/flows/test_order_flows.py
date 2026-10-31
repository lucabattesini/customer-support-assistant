import pytest


def test_order_status_with_matching_email(call_tool):
    payload = call_tool("get_order_status", {"order_id": 3, "email": "BRUNO@example.com"})

    assert payload == {
        "order_id": 3,
        "status": "shipped",
        "order_date": "2026-03-20",
        "items": [{"name": "Northwind U-1 Soprano Ukulele", "quantity": 1}],
        "total": "R$ 199,90",
        "payment_method": "debit",
        "tracking_code": "BRCC1111111BR",
        "estimated_delivery": "2026-03-28",
    }


def test_cancelled_order_includes_reason(call_tool):
    payload = call_tool("get_order_status", {"order_id": 6, "phone": "67 99555-6666"})

    assert payload["status"] == "cancelled"
    assert payload["cancellation_reason"] == "Cancelled by the customer before processing"


def test_order_status_requires_contact(call_tool):
    assert call_tool("get_order_status", {"order_id": 3}) == {
        "error": "missing_contact",
        "action": "ask_customer_for_email_or_phone",
    }


@pytest.mark.parametrize(
    "arguments",
    [
        {"order_id": 3, "email": "alice@example.com"},
        {"order_id": 999, "email": "bruno@example.com"},
    ],
)
def test_wrong_contact_and_unknown_order_look_identical(call_tool, arguments):
    assert call_tool("get_order_status", arguments) == {
        "error": "verification_failed",
        "action": "ask_customer_to_check_order_number_and_contact",
    }


def test_regret_within_window_is_eligible(call_tool):
    payload = call_tool(
        "check_return_eligibility",
        {"order_id": 2, "email": "alice@example.com", "reason": "regret"},
    )

    assert payload == {
        "order_id": 2,
        "reason": "regret",
        "eligible": True,
        "deadline": "2026-03-27",
        "days_remaining": 2,
        "based_on_estimated_delivery": True,
        "legal_warranty_until": "2026-06-18",
    }


def test_regret_after_window_is_not_eligible_but_defect_is(call_tool):
    regret = call_tool(
        "check_return_eligibility",
        {"order_id": 1, "email": "alice@example.com", "reason": "regret"},
    )
    defect = call_tool(
        "check_return_eligibility",
        {"order_id": 1, "email": "alice@example.com", "reason": "defect"},
    )

    assert regret["eligible"] is False
    assert regret["days_exceeded"] == 8
    assert defect["eligible"] is True
    assert defect["deadline"] == "2026-03-31"


def test_return_of_order_not_delivered_is_blocked(call_tool):
    payload = call_tool(
        "check_return_eligibility",
        {"order_id": 4, "email": "bruno@example.com", "reason": "regret"},
    )

    assert payload["eligible"] is False
    assert payload["blocking_status"] == "confirmed"
    assert "deadline" not in payload


def test_return_check_requires_verification(call_tool):
    payload = call_tool(
        "check_return_eligibility",
        {"order_id": 1, "email": "bruno@example.com", "reason": "regret"},
    )

    assert payload["error"] == "verification_failed"
