from decimal import Decimal

import pytest

from app.domain.enums import ProductStatus
from app.domain.errors import (
    AmbiguousProductError,
    InvalidPriceRangeError,
    ProductNotFoundError,
    UnknownCategoryError,
)
from app.domain.models import Category, Product, Promotion
from app.services.catalog_service import CatalogService
from app.services.pricing_service import PricingService

CATEGORIES = [
    Category(category_id=1, name="Violões"),
    Category(category_id=2, name="Guitarras"),
    Category(category_id=3, name="Teclados e Pianos"),
]
CATEGORY_NAMES = {category.category_id: category.name for category in CATEGORIES}


def make_product(product_id, name, category_id, price, stock=5, status=ProductStatus.ACTIVE):
    return Product(
        product_id=product_id,
        name=name,
        category_id=category_id,
        category_name=CATEGORY_NAMES[category_id],
        price_brl=Decimal(price),
        stock_quantity=stock,
        status=status,
    )


PRODUCTS = [
    make_product(1, "Takamine GD20 Dreadnought Natural", 1, "2199"),
    make_product(2, "Takamine GC5CE Elétrico Nylon Natural", 1, "3299"),
    make_product(3, "Yamaha C40 Nylon Natural", 1, "599.90"),
    make_product(4, "Yamaha C70 Nylon Natural", 1, "849"),
    make_product(5, "Martin D-28 Dreadnought Natural", 1, "11499"),
    make_product(6, "Martin D-28E Elétrico Aço Natural", 1, "12000"),
    make_product(7, "Giannini GF-3D Dreadnought Sunburst", 1, "799.90", stock=0),
    make_product(8, "Shelby SN-7C 7 Cordas", 1, "749", stock=0, status=ProductStatus.DISCONTINUED),
    make_product(9, "Fender Telecaster Player Series", 2, "5400"),
    make_product(10, "Roland Stage Piano", 3, "4599"),
]


class FakeProductRepository:
    def __init__(self, products):
        self._products = products

    def get_by_id(self, product_id):
        return next((p for p in self._products if p.product_id == product_id), None)

    def list_all(self):
        return list(self._products)

    def list_by_filters(
        self, *, category_ids=None, min_price=None, max_price=None, statuses=None, in_stock=None
    ):
        return [
            p
            for p in self._products
            if (category_ids is None or p.category_id in category_ids)
            and (min_price is None or p.price_brl >= min_price)
            and (max_price is None or p.price_brl <= max_price)
            and (statuses is None or p.status in statuses)
            and (in_stock is None or (p.stock_quantity > 0) == in_stock)
        ]


class FakeCategoryRepository:
    def list_all(self):
        return list(CATEGORIES)


PROMOTIONS = [
    Promotion(promotion_id=1, product_id=1, discount_percent=60, description="Sale", is_active=True)
]


class FakePromotionRepository:
    def list_active(self, product_ids=None):
        return [p for p in PROMOTIONS if product_ids is None or p.product_id in product_ids]


@pytest.fixture
def catalog(store_config):
    pricing = PricingService(FakePromotionRepository(), store_config.pricing)
    return CatalogService(FakeProductRepository(PRODUCTS), FakeCategoryRepository(), pricing)


def ids(products):
    return [product.product_id for product in products]


def test_search_by_category_without_accent_and_max_price(catalog):
    result = catalog.search(category="violao", max_price=Decimal("850"))

    assert ids(result.products) == [3, 4]
    assert result.total_found == 2


def test_price_filter_uses_promotional_price(catalog):
    result = catalog.search(category="violao", max_price=Decimal("1000"))

    assert ids(result.products) == [3, 4, 1]
    assert result.quotes[1].final_price == Decimal("879.60")


def test_search_returns_quotes_only_for_returned_page(catalog):
    result = catalog.search(category="violoes", limit=2)

    assert set(result.quotes) == set(ids(result.products))


def test_search_without_query_is_ordered_by_price(catalog):
    result = catalog.search(category="violões", limit=10)

    prices = [result.quotes[product.product_id].final_price for product in result.products]
    assert prices == sorted(prices)


def test_search_excludes_unavailable_products_by_default(catalog):
    result = catalog.search(category="violoes", limit=20)

    assert 7 not in ids(result.products)
    assert 8 not in ids(result.products)


def test_search_can_include_unavailable_products(catalog):
    result = catalog.search(category="violoes", only_available=False, limit=20)

    assert {7, 8} <= set(ids(result.products))


def test_search_on_sale_keeps_only_products_with_active_promotion(catalog):
    result = catalog.search(on_sale=True, limit=10)

    assert ids(result.products) == [1]
    assert result.total_found == 1


def test_search_respects_limit_but_reports_total(catalog):
    result = catalog.search(category="violoes", limit=2)

    assert len(result.products) == 2
    assert result.total_found == 6


def test_search_by_query_ranks_relevant_products(catalog):
    result = catalog.search(query="telecaster")

    assert ids(result.products) == [9]


def test_search_partial_category_name(catalog):
    result = catalog.search(category="piano")

    assert ids(result.products) == [10]


def test_search_unknown_category_lists_available(catalog):
    with pytest.raises(UnknownCategoryError) as error:
        catalog.search(category="saxofone")

    assert error.value.details["available_categories"] == [
        "Violões",
        "Guitarras",
        "Teclados e Pianos",
    ]


def test_search_rejects_inverted_price_range(catalog):
    with pytest.raises(InvalidPriceRangeError):
        catalog.search(min_price=Decimal("1000"), max_price=Decimal("100"))


@pytest.mark.parametrize(
    ("reference", "expected_id"),
    [
        ("takamine gd20", 1),
        ("Takamine GD-20", 1),
        ("TAKAMINE GD20", 1),
        ("yamaha c40", 3),
        ("martin d-28 dreadnought", 5),
        ("telecaster", 9),
        ("10", 10),
    ],
)
def test_find_product_identifies_single_product(catalog, reference, expected_id):
    assert catalog.find_product(reference).product_id == expected_id


def test_find_product_returns_candidates_when_ambiguous(catalog):
    with pytest.raises(AmbiguousProductError) as error:
        catalog.find_product("martin d28")

    assert set(ids(error.value.details["candidates"])) >= {5, 6}


def test_find_product_brand_only_is_ambiguous(catalog):
    with pytest.raises(AmbiguousProductError):
        catalog.find_product("takamine")


@pytest.mark.parametrize("reference", ["saxofone soprano", "999", "xyz"])
def test_find_product_not_found(catalog, reference):
    with pytest.raises(ProductNotFoundError):
        catalog.find_product(reference)


def test_find_product_includes_discontinued_products(catalog):
    assert catalog.find_product("shelby sn-7c").product_id == 8


def test_alternatives_are_available_same_category_closest_price(catalog):
    out_of_stock = catalog.find_product("7")

    alternatives = catalog.alternatives(out_of_stock, limit=2)

    assert ids(alternatives) == [4, 3]
