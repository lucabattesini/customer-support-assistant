from sqlalchemy.orm import Session

from app.core.store_config import StoreConfig
from app.repositories.category_repository import CategoryRepository
from app.repositories.customer_repository import CustomerRepository
from app.repositories.handoff_repository import HandoffRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.policy_repository import PolicyRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.promotion_repository import PromotionRepository
from app.services.catalog_service import CatalogService
from app.services.handoff_service import HandoffService
from app.services.order_service import OrderService
from app.services.policy_service import PolicyService
from app.services.pricing_service import PricingService
from app.services.returns_service import ReturnsService
from app.services.store_hours_service import StoreHoursService


class ServiceContainer:
    """Services wired to repositories that share a single database session."""

    def __init__(self, session: Session, config: StoreConfig) -> None:
        self.pricing = PricingService(PromotionRepository(session), config.pricing)
        self.catalog = CatalogService(
            ProductRepository(session), CategoryRepository(session), self.pricing
        )
        self.orders = OrderService(OrderRepository(session), CustomerRepository(session))
        self.returns = ReturnsService(config.returns)
        self.store_hours = StoreHoursService(config)
        self.policies = PolicyService(PolicyRepository(session))
        self.handoffs = HandoffService(HandoffRepository(session), config.handoff)
