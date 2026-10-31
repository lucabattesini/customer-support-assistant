from decimal import Decimal

import pytest

from app.domain.enums import ProductStatus
from app.domain.models import Product, Promotion
from app.services.pricing_service import PricingService


def make_product(product_id, price):
    return Product(
        product_id=product_id,
        name=f"Product {product_id}",
        category_id=1,
        category_name="Category",
        price_brl=Decimal(price),
        stock_quantity=1,
        status=ProductStatus.ACTIVE,
    )


def make_promotion(promotion_id, product_id, percent, label="Sale"):
    return Promotion(
        promotion_id=promotion_id,
        product_id=product_id,
        discount_percent=percent,
        description=label,
        is_active=True,
    )


class FakePromotionRepository:
    def __init__(self, promotions):
        self._promotions = promotions
        self.calls = 0

    def list_active(self, product_ids=None):
        self.calls += 1
        return [p for p in self._promotions if product_ids is None or p.product_id in product_ids]


@pytest.fixture
def make_service(store_config):
    def build(promotions=()):
        return PricingService(FakePromotionRepository(list(promotions)), store_config.pricing)

    return build


def test_without_promotion_offers_pix_price(make_service):
    quote = make_service().quote(make_product(1, "2199"))

    assert quote.list_price == Decimal("2199.00")
    assert quote.promotion is None
    assert quote.pix_price == Decimal("2089.05")
    assert quote.final_price == Decimal("2199.00")


def test_with_promotion_has_no_pix_price(make_service):
    quote = make_service([make_promotion(1, 1, 20, "Seasonal")]).quote(make_product(1, "899"))

    assert quote.promotion.price == Decimal("719.20")
    assert quote.promotion.discount_percent == 20
    assert quote.promotion.label == "Seasonal"
    assert quote.pix_price is None
    assert quote.final_price == Decimal("719.20")


def test_largest_active_promotion_wins(make_service):
    promotions = [make_promotion(1, 1, 10), make_promotion(2, 1, 15), make_promotion(3, 2, 50)]

    quote = make_service(promotions).quote(make_product(1, "3499"))

    assert quote.promotion.discount_percent == 15
    assert quote.promotion.price == Decimal("2974.15")


def test_installments_use_promotional_price(make_service):
    quote = make_service([make_promotion(1, 1, 20)]).quote(make_product(1, "1000"), installments=8)

    assert quote.installments.allowed
    assert quote.installments.installment_value == Decimal("100.00")


@pytest.mark.parametrize(
    ("price", "installments", "allowed", "value", "maximum"),
    [
        ("349.90", 6, False, None, 4),
        ("349.90", 3, True, Decimal("116.63"), 4),
        ("349.90", 4, True, Decimal("87.48"), 4),
        ("599.90", 6, True, Decimal("99.98"), 6),
        ("599.90", 7, False, None, 6),
        ("1200.00", 12, True, Decimal("100.00"), 12),
        ("1199.99", 12, False, None, 11),
        ("120.00", 3, False, None, 2),
        ("30.00", 1, True, Decimal("30.00"), 1),
        ("5000.00", 13, False, None, 12),
        ("5000.00", 0, False, None, 12),
    ],
)
def test_installment_rules_follow_tiers(make_service, price, installments, allowed, value, maximum):
    quote = make_service().quote(make_product(1, price), installments=installments)

    assert quote.installments.allowed is allowed
    assert quote.installments.installment_value == value
    assert quote.installments.max_installments == maximum


def test_quote_many_uses_a_single_lookup(store_config):
    repository = FakePromotionRepository([make_promotion(1, 2, 10)])
    service = PricingService(repository, store_config.pricing)

    quotes = service.quote_many([make_product(1, "100"), make_product(2, "200")])

    assert repository.calls == 1
    assert quotes[1].pix_price == Decimal("95.00")
    assert quotes[2].promotion.price == Decimal("180.00")
