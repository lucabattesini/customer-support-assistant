import csv
import json
import tomllib
from datetime import date
from decimal import Decimal
from pathlib import Path

from sqlalchemy import delete, func, select
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

TITLE_PREFIX = "# "


def is_empty(session: Session) -> bool:
    """Whether the catalog has no products yet."""
    return session.scalar(select(func.count()).select_from(ProductModel)) == 0


def load_seed_data(session: Session, seed_dir: Path) -> None:
    """Replace all data with the store data found in a seed folder.

    The folder holds the CSV exports in `csv/`, one Markdown file per policy section in
    `policies/` and data corrections in `corrections.toml`. CSV values are only converted
    to their column types; corrections are applied on load so the CSVs stay as delivered.

    Args:
        session: Session used to write the data; the caller controls the transaction.
        seed_dir: Folder with the seed files.
    """
    corrections = _read_corrections(seed_dir / "corrections.toml")
    csv_dir = seed_dir / "csv"

    for model in reversed(ALL_MODELS):
        session.execute(delete(model))
    session.add_all(_categories(csv_dir / "categories.csv"))
    session.flush()
    session.add_all(_products(csv_dir / "products.csv", corrections))
    session.flush()
    session.add_all(_promotions(csv_dir / "promotions.csv"))
    session.add_all(_customers(csv_dir / "customers.csv"))
    session.flush()
    session.add_all(_orders(csv_dir / "orders.csv", csv_dir / "order_items.csv"))
    session.add_all(_policy_sections(seed_dir / "policies"))
    session.flush()


def _read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def _read_corrections(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("rb") as file:
        return tomllib.load(file)


def _optional(value: str) -> str | None:
    cleaned = value.strip()
    return cleaned or None


def _optional_date(value: str) -> date | None:
    cleaned = _optional(value)
    return date.fromisoformat(cleaned) if cleaned else None


def _categories(path: Path) -> list[CategoryModel]:
    return [
        CategoryModel(
            category_id=int(row["category_id"]),
            name=row["name"].strip(),
            description=_optional(row["description"]),
        )
        for row in _read_rows(path)
    ]


def _products(path: Path, corrections: dict) -> list[ProductModel]:
    drop_description = set(corrections.get("products", {}).get("drop_description", []))
    products = []
    for row in _read_rows(path):
        product_id = int(row["product_id"])
        products.append(
            ProductModel(
                product_id=product_id,
                price_brl=Decimal(row["price_brl"]),
                name=row["name"].strip(),
                category_id=int(row["category_id"]),
                description=(
                    None if product_id in drop_description else _optional(row["description"])
                ),
                stock_quantity=int(row["stock_quantity"]),
                status=row["status"].strip(),
                specs=json.loads(row["specs"]) if _optional(row["specs"]) else {},
                created_at=_optional_date(row["created_at"]),
            )
        )
    return products


def _promotions(path: Path) -> list[PromotionModel]:
    return [
        PromotionModel(
            promotion_id=int(row["promotion_id"]),
            product_id=int(row["product_id"]),
            discount_percent=int(row["discount_percent"]),
            description=row["description"].strip(),
            is_active=row["is_active"].strip() == "1",
        )
        for row in _read_rows(path)
    ]


def _customers(path: Path) -> list[CustomerModel]:
    return [
        CustomerModel(
            customer_id=int(row["customer_id"]),
            name=row["name"].strip(),
            phone=_optional(row["phone"]),
            email=_optional(row["email"]),
            city=_optional(row["city"]),
        )
        for row in _read_rows(path)
    ]


def _orders(orders_path: Path, items_path: Path) -> list[OrderModel]:
    items: dict[int, list[OrderItemModel]] = {}
    for row in _read_rows(items_path):
        items.setdefault(int(row["order_id"]), []).append(
            OrderItemModel(product_id=int(row["product_id"]), quantity=int(row["quantity"]))
        )
    return [
        OrderModel(
            order_id=int(row["order_id"]),
            customer_id=int(row["customer_id"]),
            order_date=date.fromisoformat(row["order_date"].strip()),
            status=row["status"].strip(),
            total_brl=Decimal(row["total_brl"]),
            payment_method=row["payment_method"].strip(),
            tracking_code=_optional(row["tracking_code"]),
            estimated_delivery=_optional_date(row["estimated_delivery"]),
            notes=_optional(row["notes"]),
            items=items.get(int(row["order_id"]), []),
        )
        for row in _read_rows(orders_path)
    ]


def _policy_sections(folder: Path) -> list[PolicySectionModel]:
    sections = []
    for path in sorted(folder.glob("*.md")):
        title_line, _, content = path.read_text(encoding="utf-8").partition("\n")
        if not title_line.startswith(TITLE_PREFIX):
            raise ValueError(f"Policy file {path.name} must start with a '# Title' line")
        sections.append(
            PolicySectionModel(
                section=path.stem,
                title=title_line.removeprefix(TITLE_PREFIX).strip(),
                content=content.strip(),
            )
        )
    return sections
