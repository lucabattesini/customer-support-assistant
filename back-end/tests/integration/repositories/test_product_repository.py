from decimal import Decimal

import pytest

from app.domain.enums import Availability, ProductStatus
from app.repositories.category_repository import CategoryRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.promotion_repository import PromotionRepository


@pytest.fixture
def products(session):
    return ProductRepository(session)


def test_get_by_id_maps_to_domain_with_category_name(products):
    product = products.get_by_id(101)

    assert product.name == "Acme AG-100 Nylon Natural"
    assert product.category_name == "Acoustic Guitars"
    assert product.price_brl == Decimal("599.90")
    assert product.status is ProductStatus.ACTIVE


def test_get_by_id_returns_none_when_missing(products):
    assert products.get_by_id(999) is None


@pytest.mark.parametrize(
    ("product_id", "availability"),
    [
        (101, Availability.AVAILABLE),
        (104, Availability.OUT_OF_STOCK),
        (105, Availability.DISCONTINUED),
        (106, Availability.COMING_SOON),
    ],
)
def test_availability_combines_status_and_stock(products, product_id, availability):
    assert products.get_by_id(product_id).availability is availability


def test_filters_by_category_price_status_and_stock(products):
    result = products.list_by_filters(
        category_ids=[1],
        max_price=Decimal("1000"),
        statuses=[ProductStatus.ACTIVE],
        in_stock=True,
    )

    assert [product.product_id for product in result] == [101, 102, 110]


def test_filters_by_min_price(products):
    result = products.list_by_filters(min_price=Decimal("3499.00"))

    assert [product.product_id for product in result] == [107, 109]


def test_list_all_is_ordered_by_id(products):
    ids = [product.product_id for product in products.list_all()]

    assert ids == sorted(ids)
    assert len(ids) == 10


def test_domain_objects_stay_usable_after_session_closes(session_factory):
    with session_factory() as session:
        product = ProductRepository(session).get_by_id(101)

    assert product.category_name == "Acoustic Guitars"


def test_category_repository_lists_all(session):
    names = [category.name for category in CategoryRepository(session).list_all()]

    assert names == ["Acoustic Guitars", "Electric Guitars", "Ukuleles", "Keyboards"]


def test_promotion_repository_lists_only_active(session):
    promotions = PromotionRepository(session).list_active()

    assert {promotion.promotion_id for promotion in promotions} == {1, 3, 4}


def test_promotion_repository_filters_active_by_product(session):
    promotions = PromotionRepository(session).list_active(product_ids=[107])

    assert sorted(promotion.discount_percent for promotion in promotions) == [10, 15]


def test_promotion_repository_lists_inactive_for_product(session):
    promotions = PromotionRepository(session).list_for_product(103)

    assert [(promotion.discount_percent, promotion.is_active) for promotion in promotions] == [
        (12, False)
    ]
