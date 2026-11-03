from collections.abc import Iterable
from dataclasses import dataclass
from decimal import Decimal

from app.core.money import apply_discount, to_money
from app.core.store_config import PricingConfig
from app.domain.models import Product, Promotion
from app.repositories.promotion_repository import PromotionRepository


@dataclass(frozen=True)
class AppliedPromotion:
    """Active promotion chosen for a product."""

    discount_percent: int
    label: str
    price: Decimal


@dataclass(frozen=True)
class InstallmentQuote:
    """Result of an installment simulation."""

    requested: int
    allowed: bool
    installment_value: Decimal | None
    max_installments: int


@dataclass(frozen=True)
class PriceQuote:
    """Prices of a product under the store pricing rules."""

    list_price: Decimal
    promotion: AppliedPromotion | None
    pix_price: Decimal | None
    installments: InstallmentQuote | None

    @property
    def final_price(self) -> Decimal:
        """Price charged on card or boleto: promotional price when there is one."""
        return self.promotion.price if self.promotion else self.list_price


class PricingService:
    """Applies promotions, the PIX discount and installment rules.

    Promotions and the PIX discount are not cumulative: the PIX price is only offered for
    products without an active promotion. When several promotions are active at once the
    largest discount wins.
    """

    def __init__(self, promotions: PromotionRepository, pricing: PricingConfig) -> None:
        self._promotions = promotions
        self._pricing = pricing

    def quote(self, product: Product, installments: int | None = None) -> PriceQuote:
        """Price a single product, optionally simulating a number of installments."""
        promotions = self._promotions.list_active(product_ids=[product.product_id])
        return self._build_quote(product, promotions, installments)

    def quote_many(self, products: Iterable[Product]) -> dict[int, PriceQuote]:
        """Price several products with a single promotion lookup."""
        products = list(products)
        promotions = self._promotions.list_active(
            product_ids=[product.product_id for product in products]
        )
        return {
            product.product_id: self._build_quote(
                product,
                [item for item in promotions if item.product_id == product.product_id],
                None,
            )
            for product in products
        }

    def inactive_promotions(self, product: Product) -> list[Promotion]:
        """Promotions of a product that are no longer valid, to answer about expired offers."""
        return [
            promotion
            for promotion in self._promotions.list_for_product(product.product_id)
            if not promotion.is_active
        ]

    def max_installments(self, amount: Decimal) -> int:
        """Largest number of installments allowed for an amount (at least one)."""
        allowed = [
            count
            for count in range(1, self._pricing.max_installments + 1)
            if self._installments_allowed(amount, count)
        ]
        return allowed[-1]

    def _build_quote(
        self, product: Product, promotions: list[Promotion], installments: int | None
    ) -> PriceQuote:
        list_price = to_money(product.price_brl)
        promotion = _best_promotion(list_price, promotions)
        pix_price = (
            None if promotion else apply_discount(list_price, self._pricing.pix_discount_percent)
        )
        final_price = promotion.price if promotion else list_price
        return PriceQuote(
            list_price=list_price,
            promotion=promotion,
            pix_price=pix_price,
            installments=(
                self._simulate(final_price, installments) if installments is not None else None
            ),
        )

    def _simulate(self, amount: Decimal, requested: int) -> InstallmentQuote:
        allowed = self._installments_allowed(amount, requested)
        return InstallmentQuote(
            requested=requested,
            allowed=allowed,
            installment_value=to_money(amount / requested) if allowed else None,
            max_installments=self.max_installments(amount),
        )

    def _installments_allowed(self, amount: Decimal, count: int) -> bool:
        if count == 1:
            return True
        if count < 1 or count > self._pricing.max_installments:
            return False
        tier = next(
            tier for tier in self._pricing.installment_tiers if count <= tier.max_installments
        )
        return amount / count >= tier.min_installment_value


def _best_promotion(list_price: Decimal, promotions: list[Promotion]) -> AppliedPromotion | None:
    if not promotions:
        return None
    best = max(
        promotions, key=lambda promotion: (promotion.discount_percent, -promotion.promotion_id)
    )
    return AppliedPromotion(
        discount_percent=best.discount_percent,
        label=best.description,
        price=apply_discount(list_price, best.discount_percent),
    )
