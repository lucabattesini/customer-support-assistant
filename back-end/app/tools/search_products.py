from decimal import Decimal

from pydantic import BaseModel, Field

from app.tools.base import Payload, ToolContext, ToolSpec
from app.tools.serializers import product_summary


class SearchProductsInput(BaseModel):
    """Arguments of `search_products`."""

    query: str | None = None
    category: str | None = None
    min_price: Decimal | None = Field(default=None, ge=0)
    max_price: Decimal | None = Field(default=None, ge=0)
    only_available: bool = True
    on_sale: bool = False
    limit: int = Field(default=5, ge=1, le=10)


def search_products(context: ToolContext, arguments: SearchProductsInput) -> Payload:
    """Search the catalog and return priced product summaries."""
    locale = context.store_config.locale
    with context.services() as services:
        result = services.catalog.search(
            query=arguments.query,
            category=arguments.category,
            min_price=arguments.min_price,
            max_price=arguments.max_price,
            only_available=arguments.only_available,
            on_sale=arguments.on_sale,
            limit=arguments.limit,
        )
    return {
        "products": [
            product_summary(product, result.quotes[product.product_id], locale)
            for product in result.products
        ],
        "total_found": result.total_found,
    }


TOOL = ToolSpec(name="search_products", input_model=SearchProductsInput, handler=search_products)
