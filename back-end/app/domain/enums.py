from enum import StrEnum


class ProductStatus(StrEnum):
    """Catalog lifecycle status of a product."""

    ACTIVE = "active"
    DISCONTINUED = "discontinued"
    COMING_SOON = "coming_soon"


class Availability(StrEnum):
    """Whether a product can be sold right now."""

    AVAILABLE = "available"
    OUT_OF_STOCK = "out_of_stock"
    DISCONTINUED = "discontinued"
    COMING_SOON = "coming_soon"


class OrderStatus(StrEnum):
    """Processing status of an order."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class ReturnReason(StrEnum):
    """Reason a customer wants to return or exchange an order."""

    REGRET = "regret"
    DEFECT = "defect"
    PREFERENCE = "preference"


class HandoffType(StrEnum):
    """Category of a case forwarded to the human team."""

    COMPLAINT = "complaint"
    POLICY_QUESTION = "policy_question"
    HUMAN_REQUEST = "human_request"
    OTHER = "other"


class PolicySectionKey(StrEnum):
    """Stable identifiers of the store policy sections."""

    ABOUT_CONTACT = "about_contact"
    BUSINESS_HOURS = "business_hours"
    PAYMENT = "payment"
    RETURNS_EXCHANGES = "returns_exchanges"
    SHIPPING = "shipping"
    PROMOTIONS = "promotions"
    WARRANTY = "warranty"
    PRIVACY = "privacy"
    SERVICE_SCOPE = "service_scope"
