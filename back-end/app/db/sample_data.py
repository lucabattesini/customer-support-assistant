from datetime import date
from decimal import Decimal

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.db.models import (
    ALL_MODELS,
    CategoryModel,
    CustomerModel,
    OrderItemModel,
    OrderModel,
    PolicySectionModel,
    ProductModel,
    PromotionModel,
)


def load_sample_data(session: Session) -> None:
    """Replace all data with a small synthetic dataset for development and tests.

    The dataset uses fictional brands and customers and covers the business cases the
    assistant must handle: active, expired and overlapping promotions, out-of-stock,
    discontinued and upcoming products, and orders in every status.

    Args:
        session: Session used to write the data; the caller controls the transaction.
    """
    for model in reversed(ALL_MODELS):
        session.execute(delete(model))
    session.add_all(_categories())
    session.flush()
    session.add_all(_products())
    session.flush()
    session.add_all(_promotions())
    session.add_all(_customers())
    session.flush()
    session.add_all(_orders())
    session.add_all(_policy_sections())
    session.flush()


def _categories() -> list[CategoryModel]:
    return [
        CategoryModel(category_id=1, name="Acoustic Guitars", description="Nylon and steel"),
        CategoryModel(category_id=2, name="Electric Guitars", description="Solid body guitars"),
        CategoryModel(category_id=3, name="Ukuleles", description="Soprano to baritone"),
        CategoryModel(category_id=4, name="Keyboards", description="Digital pianos and synths"),
    ]


def _product(
    product_id: int,
    name: str,
    category_id: int,
    price: str,
    stock: int,
    status: str = "active",
) -> ProductModel:
    return ProductModel(
        product_id=product_id,
        name=name,
        category_id=category_id,
        price_brl=Decimal(price),
        stock_quantity=stock,
        status=status,
        description=f"{name}, a sample product for development.",
        specs={"color": "Natural"},
        created_at=date(2025, 1, 15),
    )


def _products() -> list[ProductModel]:
    return [
        _product(101, "Acme AG-100 Nylon Natural", 1, "599.90", 12),
        _product(102, "Acme AG-200 Steel Sunburst", 1, "899.00", 5),
        _product(103, "Northwind D-50 Dreadnought", 1, "2199.00", 3),
        _product(104, "Northwind C-10 Classic", 1, "799.90", 0),
        _product(105, "Contoso S7 Seven String", 1, "749.00", 0, status="discontinued"),
        _product(106, "Contoso P-1 Parlor", 1, "1749.00", 2, status="coming_soon"),
        _product(107, "Acme E-300 Electric", 2, "3499.00", 4),
        _product(108, "Northwind U-1 Soprano Ukulele", 3, "199.90", 15),
        _product(109, "Contoso SP-88 Stage Piano", 4, "4599.00", 2),
        _product(110, "Acme F-20 Steel Folk", 1, "949.00", 7),
    ]


def _promotions() -> list[PromotionModel]:
    return [
        PromotionModel(
            promotion_id=1,
            product_id=102,
            discount_percent=20,
            description="Seasonal Sale",
            is_active=True,
        ),
        PromotionModel(
            promotion_id=2,
            product_id=103,
            discount_percent=12,
            description="Black Friday",
            is_active=False,
        ),
        PromotionModel(
            promotion_id=3,
            product_id=107,
            discount_percent=10,
            description="Special Offer",
            is_active=True,
        ),
        PromotionModel(
            promotion_id=4,
            product_id=107,
            discount_percent=15,
            description="Musician Week",
            is_active=True,
        ),
        PromotionModel(
            promotion_id=5,
            product_id=108,
            discount_percent=10,
            description="Spring Sale",
            is_active=False,
        ),
    ]


def _customers() -> list[CustomerModel]:
    return [
        CustomerModel(
            customer_id=1,
            name="Alice Martins",
            phone="(67) 99111-2222",
            email="alice@example.com",
            city="Springfield",
        ),
        CustomerModel(
            customer_id=2,
            name="Bruno Costa",
            phone="(67) 99333-4444",
            email="bruno@example.com",
            city="Shelbyville",
        ),
        CustomerModel(
            customer_id=3,
            name="Carla Dias",
            phone="(67) 99555-6666",
            email="carla@example.com",
            city="Springfield",
        ),
    ]


def _order(
    order_id: int,
    customer_id: int,
    order_date: date,
    status: str,
    total: str,
    payment_method: str,
    items: list[tuple[int, int]],
    tracking_code: str | None = None,
    estimated_delivery: date | None = None,
    notes: str | None = None,
) -> OrderModel:
    return OrderModel(
        order_id=order_id,
        customer_id=customer_id,
        order_date=order_date,
        status=status,
        total_brl=Decimal(total),
        payment_method=payment_method,
        tracking_code=tracking_code,
        estimated_delivery=estimated_delivery,
        notes=notes,
        items=[
            OrderItemModel(product_id=product_id, quantity=quantity)
            for product_id, quantity in items
        ],
    )


def _orders() -> list[OrderModel]:
    return [
        _order(
            1,
            1,
            date(2026, 3, 1),
            "delivered",
            "599.90",
            "pix",
            [(101, 1)],
            tracking_code="BRAA1234567BR",
            estimated_delivery=date(2026, 3, 10),
        ),
        _order(
            2,
            1,
            date(2026, 3, 15),
            "delivered",
            "949.00",
            "credit_6x",
            [(110, 1)],
            tracking_code="BRBB7654321BR",
            estimated_delivery=date(2026, 3, 20),
        ),
        _order(
            3,
            2,
            date(2026, 3, 20),
            "shipped",
            "199.90",
            "debit",
            [(108, 1)],
            tracking_code="BRCC1111111BR",
            estimated_delivery=date(2026, 3, 28),
        ),
        _order(
            4,
            2,
            date(2026, 3, 22),
            "confirmed",
            "3698.90",
            "credit_12x",
            [(107, 1), (108, 1)],
        ),
        _order(5, 3, date(2026, 3, 23), "pending", "4599.00", "boleto", [(109, 1)]),
        _order(
            6,
            3,
            date(2026, 3, 5),
            "cancelled",
            "749.00",
            "pix",
            [(105, 1)],
            notes="Cancelled by the customer before processing",
        ),
    ]


def _policy_sections() -> list[PolicySectionModel]:
    sections = {
        "about_contact": ("About and contact", "Sample store. Phone (00) 0000-0000."),
        "business_hours": ("Business hours", "Monday to Friday 9:00-18:00, Saturday 9:00-13:00."),
        "payment": ("Payment methods", "PIX with 5% discount, cards up to 12 installments."),
        "returns_exchanges": ("Returns and exchanges", "Regret within 7 days of receipt."),
        "shipping": ("Shipping", "Free local delivery above a minimum order value."),
        "promotions": ("Promotions", "Promotions are not cumulative."),
        "warranty": ("Warranty", "90-day legal warranty from receipt."),
        "privacy": ("Privacy", "Personal data is used only to process orders."),
        "service_scope": ("Service scope", "The store sells musical instruments only."),
    }
    return [
        PolicySectionModel(section=key, title=title, content=content)
        for key, (title, content) in sections.items()
    ]
