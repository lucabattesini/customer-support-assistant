import csv
from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import func, select

from app.core.settings import BASE_DIR
from app.db.models import (
    CategoryModel,
    CustomerModel,
    OrderItemModel,
    OrderModel,
    PolicySectionModel,
    ProductModel,
    PromotionModel,
)
from app.db.seed import is_empty, load_seed_data
from app.db.session import build_engine, build_session_factory, init_db, session_scope
from app.domain.enums import PolicySectionKey

SEED_DIR = BASE_DIR / "seed"


def _csv_rows(name):
    with (SEED_DIR / "csv" / f"{name}.csv").open(encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


@pytest.fixture
def seeded_session():
    engine = build_engine("sqlite://")
    init_db(engine)
    factory = build_session_factory(engine)
    with session_scope(factory) as session:
        load_seed_data(session, SEED_DIR)
    with session_scope(factory) as session:
        yield session
    engine.dispose()


def _count(session, model):
    return session.scalar(select(func.count()).select_from(model))


@pytest.mark.parametrize(
    ("model", "csv_name"),
    [
        (CategoryModel, "categories"),
        (ProductModel, "products"),
        (PromotionModel, "promotions"),
        (CustomerModel, "customers"),
        (OrderModel, "orders"),
        (OrderItemModel, "order_items"),
    ],
)
def test_every_csv_row_is_loaded(seeded_session, model, csv_name):
    assert _count(seeded_session, model) == len(_csv_rows(csv_name))


def test_every_policy_section_is_loaded(seeded_session):
    sections = set(seeded_session.scalars(select(PolicySectionModel.section)))

    assert sections == {key.value for key in PolicySectionKey}


def test_values_are_converted_to_column_types(seeded_session):
    product = seeded_session.get(ProductModel, 81)
    order = seeded_session.get(OrderModel, 9)
    promotion = seeded_session.get(PromotionModel, 12)

    assert product.price_brl == Decimal("599.90")
    assert product.specs["strings"] == "nylon"
    assert product.created_at == date(2021, 3, 15)
    assert order.tracking_code is None
    assert order.estimated_delivery is None
    assert order.notes is None
    assert promotion.is_active is True


def test_specs_with_irregular_spacing_are_parsed(seeded_session):
    assert seeded_session.get(ProductModel, 137).specs["strings"] == "4"


def test_contradicting_descriptions_are_dropped(seeded_session):
    assert seeded_session.get(ProductModel, 135).description is None
    assert seeded_session.get(ProductModel, 138).description is not None


def test_order_totals_are_kept_as_charged(seeded_session):
    assert seeded_session.get(OrderModel, 3).total_brl == Decimal("3450")


def test_policies_use_a_single_contact(seeded_session):
    contents = " ".join(seeded_session.scalars(select(PolicySectionModel.content)))

    assert "3321-4500" not in contents
    assert "contato@emporiodamusica.com.br" in contents
    assert "empóriodamusica" not in contents


def test_is_empty_reflects_the_catalog(seeded_session):
    assert not is_empty(seeded_session)


def test_loading_again_replaces_the_data(seeded_session):
    load_seed_data(seeded_session, SEED_DIR)

    assert _count(seeded_session, ProductModel) == len(_csv_rows("products"))
