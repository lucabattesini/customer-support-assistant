from pydantic import BaseModel, Field

from app.domain.enums import Availability
from app.domain.errors import AmbiguousProductError
from app.services.pricing_service import PriceQuote
from app.tools.base import Payload, ToolContext, ToolSpec, error_payload, without_none
from app.tools.serializers import money, product_summary

MAX_REQUESTED_INSTALLMENTS = 36


class GetProductDetailsInput(BaseModel):
    """Arguments of `get_product_details`."""

    product: str = Field(min_length=1)
    installments: int | None = Field(default=None, ge=1, le=MAX_REQUESTED_INSTALLMENTS)


def get_product_details(context: ToolContext, arguments: GetProductDetailsInput) -> Payload:
    """Return product details, pricing, expired promotions and alternatives when unavailable."""
    locale = context.store_config.locale
    with context.services() as services:
        try:
            product = services.catalog.find_product(arguments.product)
        except AmbiguousProductError as error:
            candidates = error.details["candidates"]
            quotes = services.pricing.quote_many(candidates)
            return {
                **error_payload(error),
                "candidates": [
                    product_summary(item, quotes[item.product_id], locale) for item in candidates
                ],
            }
        quote = services.pricing.quote(product, arguments.installments)
        expired = services.pricing.inactive_promotions(product)
        alternatives = []
        if product.availability is not Availability.AVAILABLE:
            options = services.catalog.alternatives(product)
            option_quotes = services.pricing.quote_many(options)
            alternatives = [
                product_summary(option, option_quotes[option.product_id], locale)
                for option in options
            ]

    return without_none(
        {
            "product_id": product.product_id,
            "name": product.name,
            "category": product.category_name,
            "description": product.description,
            "specs": product.specs or None,
            "availability": product.availability.value,
            "pricing": _pricing(quote, context),
            "expired_promotions": [
                {"label": promotion.description, "discount_percent": promotion.discount_percent}
                for promotion in expired
            ]
            or None,
            "alternatives": alternatives or None,
        }
    )


def _pricing(quote: PriceQuote, context: ToolContext) -> Payload:
    locale = context.store_config.locale
    promotion = quote.promotion
    installments = quote.installments
    return without_none(
        {
            "list_price": money(quote.list_price, locale),
            "promotion": {
                "label": promotion.label,
                "discount_percent": promotion.discount_percent,
                "price": money(promotion.price, locale),
            }
            if promotion
            else None,
            "pix_price": money(quote.pix_price, locale),
            "installments": without_none(
                {
                    "requested": installments.requested,
                    "allowed": installments.allowed,
                    "installment_value": money(installments.installment_value, locale),
                    "max_installments": installments.max_installments,
                }
            )
            if installments
            else None,
        }
    )


TOOL = ToolSpec(
    name="get_product_details", input_model=GetProductDetailsInput, handler=get_product_details
)
