from app.db.models.category import CategoryModel
from app.db.models.customer import CustomerModel
from app.db.models.handoff import HandoffModel
from app.db.models.order import OrderItemModel, OrderModel
from app.db.models.policy_section import PolicySectionModel
from app.db.models.product import ProductModel
from app.db.models.promotion import PromotionModel

ALL_MODELS = (
    CategoryModel,
    ProductModel,
    PromotionModel,
    CustomerModel,
    OrderModel,
    OrderItemModel,
    PolicySectionModel,
    HandoffModel,
)

__all__ = [
    "ALL_MODELS",
    "CategoryModel",
    "CustomerModel",
    "HandoffModel",
    "OrderItemModel",
    "OrderModel",
    "PolicySectionModel",
    "ProductModel",
    "PromotionModel",
]
