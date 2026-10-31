from typing import Any


class DomainError(Exception):
    """Expected business failure that the assistant can explain or recover from.

    Attributes:
        code: Stable machine-readable error code exposed to the agent.
        action: Machine-readable hint of what the agent should do next.
        details: Extra structured data that helps the agent recover.
    """

    code = "domain_error"
    action = "apologize_and_offer_handoff"

    def __init__(self, details: dict[str, Any] | None = None) -> None:
        super().__init__(self.code)
        self.details = details or {}


class InvalidPriceRangeError(DomainError):
    """Minimum price is greater than maximum price."""

    code = "invalid_price_range"
    action = "ask_customer_to_confirm_price_range"


class UnknownCategoryError(DomainError):
    """Requested category does not match any catalog category."""

    code = "unknown_category"
    action = "offer_available_categories"


class ProductNotFoundError(DomainError):
    """No product matches the customer reference."""

    code = "product_not_found"
    action = "ask_customer_for_more_details_or_search"


class AmbiguousProductError(DomainError):
    """Several products match the customer reference equally well."""

    code = "ambiguous_product"
    action = "ask_customer_to_choose_candidate"


class MissingContactError(DomainError):
    """Order lookup requested without an email or phone to verify identity."""

    code = "missing_contact"
    action = "ask_customer_for_email_or_phone"


class VerificationFailedError(DomainError):
    """Order does not exist or the contact does not match its customer.

    Both cases share this error so the assistant never reveals whether an order exists.
    """

    code = "verification_failed"
    action = "ask_customer_to_check_order_number_and_contact"


class PolicySectionUnavailableError(DomainError):
    """Policy section has no content stored yet."""

    code = "section_unavailable"
    action = "offer_handoff"
