from dataclasses import dataclass
from decimal import Decimal

from rapidfuzz import fuzz

from app.core.text import compact_text, normalize_text
from app.domain.enums import ProductStatus
from app.domain.errors import (
    AmbiguousProductError,
    InvalidPriceRangeError,
    ProductNotFoundError,
    UnknownCategoryError,
)
from app.domain.models import Category, Product
from app.repositories.category_repository import CategoryRepository
from app.repositories.product_repository import ProductRepository

CATEGORY_MIN_SCORE = 90
SEARCH_MIN_SCORE = 60
MATCH_MIN_SCORE = 85
AMBIGUITY_MARGIN = 5
COMPACT_MATCH_MIN_LENGTH = 4
MAX_CANDIDATES = 5


@dataclass(frozen=True)
class SearchResult:
    """Page of products found by a catalog search."""

    products: list[Product]
    total_found: int


class CatalogService:
    """Product search, product identification and alternative suggestions."""

    def __init__(self, products: ProductRepository, categories: CategoryRepository) -> None:
        self._products = products
        self._categories = categories

    def search(
        self,
        *,
        query: str | None = None,
        category: str | None = None,
        min_price: Decimal | None = None,
        max_price: Decimal | None = None,
        only_available: bool = True,
        limit: int = 5,
    ) -> SearchResult:
        """Search the catalog by free text and filters.

        Without a text query results are ordered by price; with a query they are ordered by
        relevance and products below the relevance threshold are dropped.

        Args:
            query: Free text such as brand or model.
            category: Category name as written by the customer.
            min_price: Minimum list price, inclusive.
            max_price: Maximum list price, inclusive.
            only_available: Keep only active products with stock.
            limit: Maximum number of products returned.

        Returns:
            The first `limit` products and the total number of matches.

        Raises:
            InvalidPriceRangeError: When `min_price` is greater than `max_price`.
            UnknownCategoryError: When the category matches no catalog category.
        """
        if min_price is not None and max_price is not None and min_price > max_price:
            raise InvalidPriceRangeError({"min_price": str(min_price), "max_price": str(max_price)})

        candidates = self._products.list_by_filters(
            category_ids=self._resolve_category_ids(category) if category else None,
            min_price=min_price,
            max_price=max_price,
            statuses=[ProductStatus.ACTIVE] if only_available else None,
            in_stock=True if only_available else None,
        )
        if query and normalize_text(query):
            ranked = self._rank(query, candidates, SEARCH_MIN_SCORE)
            matches = [product for product, _ in ranked]
        else:
            matches = sorted(candidates, key=lambda product: (product.price_brl, product.name))
        return SearchResult(products=matches[:limit], total_found=len(matches))

    def find_product(self, reference: str) -> Product:
        """Identify a single product from an id or a name written by the customer.

        Args:
            reference: Product id or (partial) product name.

        Returns:
            The matching product.

        Raises:
            ProductNotFoundError: When nothing matches well enough.
            AmbiguousProductError: When several products match almost equally.
        """
        cleaned = reference.strip()
        if cleaned.isdigit():
            product = self._products.get_by_id(int(cleaned))
            if product is None:
                raise ProductNotFoundError({"reference": reference})
            return product

        ranked = self._rank(cleaned, self._products.list_all(), MATCH_MIN_SCORE)
        if not ranked:
            raise ProductNotFoundError({"reference": reference})
        best_product, best_score = ranked[0]
        close_matches = [
            product for product, score in ranked if best_score - score < AMBIGUITY_MARGIN
        ]
        if len(close_matches) > 1:
            raise AmbiguousProductError(
                {"candidates": [product for product, _ in ranked[:MAX_CANDIDATES]]}
            )
        return best_product

    def alternatives(self, product: Product, limit: int = 3) -> list[Product]:
        """Available products of the same category with the closest prices."""
        options = self._products.list_by_filters(
            category_ids=[product.category_id],
            statuses=[ProductStatus.ACTIVE],
            in_stock=True,
        )
        others = [option for option in options if option.product_id != product.product_id]
        others.sort(key=lambda option: (abs(option.price_brl - product.price_brl), option.name))
        return others[:limit]

    def _resolve_category_ids(self, category: str) -> list[int]:
        term = normalize_text(category)
        categories = self._categories.list_all()
        matches = [
            item.category_id
            for item in categories
            if term and fuzz.partial_ratio(term, normalize_text(item.name)) >= CATEGORY_MIN_SCORE
        ]
        if not matches:
            raise UnknownCategoryError(
                {"category": category, "available_categories": _names(categories)}
            )
        return matches

    def _rank(
        self, query: str, products: list[Product], min_score: float
    ) -> list[tuple[Product, float]]:
        scored = [(product, _relevance(query, product)) for product in products]
        relevant = [(product, score) for product, score in scored if score >= min_score]
        return sorted(relevant, key=lambda pair: (-pair[1], pair[0].product_id))


def _relevance(query: str, product: Product) -> float:
    searchable = f"{product.name} {product.category_name}"
    token_score = fuzz.token_set_ratio(normalize_text(query), normalize_text(searchable))
    compact_query = compact_text(query)
    if len(compact_query) < COMPACT_MATCH_MIN_LENGTH:
        return token_score
    return max(token_score, fuzz.partial_ratio(compact_query, compact_text(product.name)))


def _names(categories: list[Category]) -> list[str]:
    return [category.name for category in categories]
