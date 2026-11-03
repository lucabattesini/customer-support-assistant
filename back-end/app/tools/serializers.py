from decimal import Decimal

from app.core.money import format_money
from app.core.store_config import LocaleConfig
from app.domain.models import Product
from app.services.pricing_service import PriceQuote
from app.tools.base import Payload, without_none


def money(amount: Decimal | None, locale: LocaleConfig) -> str | None:
    """Format an optional amount with the store currency conventions."""
    return None if amount is None else format_money(amount, locale)


def product_summary(product: Product, quote: PriceQuote, locale: LocaleConfig) -> Payload:
    """Short product representation used in lists."""
    promotion = quote.promotion
    return without_none(
        {
            "product_id": product.product_id,
            "name": product.name,
            "category": product.category_name,
            "price": money(quote.list_price, locale),
            "promotional_price": money(promotion.price, locale) if promotion else None,
            "discount_percent": promotion.discount_percent if promotion else None,
            "availability": product.availability.value,
        }
    )
