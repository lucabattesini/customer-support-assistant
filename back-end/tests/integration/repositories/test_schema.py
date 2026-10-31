from decimal import Decimal

import pytest
from sqlalchemy import func, inspect, select
from sqlalchemy.exc import IntegrityError

from app.db.models import (
    ALL_MODELS,
    OrderModel,
    PolicySectionModel,
    ProductModel,
    PromotionModel,
)
from app.db.sample_data import load_sample_data
from app.db.session import build_engine, build_session_factory, init_db, session_scope


def test_all_tables_are_created(engine):
    table_names = set(inspect(engine).get_table_names())

    assert {model.__tablename__ for model in ALL_MODELS} <= table_names


def test_foreign_keys_are_enforced(session_factory):
    with pytest.raises(IntegrityError), session_scope(session_factory) as session:
        session.add(
            PromotionModel(
                promotion_id=999,
                product_id=424242,
                discount_percent=5,
                description="Invalid",
                is_active=True,
            )
        )


def test_sample_data_is_loaded(session):
    assert session.scalar(select(func.count()).select_from(ProductModel)) == 10
    assert session.scalar(select(func.count()).select_from(OrderModel)) == 6
    assert session.scalar(select(func.count()).select_from(PolicySectionModel)) == 9


def test_money_columns_return_decimal(session):
    product = session.get(ProductModel, 101)

    assert product.price_brl == Decimal("599.90")
    assert isinstance(product.price_brl, Decimal)


def test_specs_are_stored_as_json(session):
    assert session.get(ProductModel, 101).specs == {"color": "Natural"}


def test_sample_data_load_is_idempotent(session_factory):
    with session_scope(session_factory) as session:
        load_sample_data(session)
    with session_scope(session_factory) as session:
        assert session.scalar(select(func.count()).select_from(ProductModel)) == 10


def test_file_database_creates_missing_folder(tmp_path):
    database_file = tmp_path / "nested" / "app.db"
    engine = build_engine(f"sqlite:///{database_file.as_posix()}")
    init_db(engine)
    with session_scope(build_session_factory(engine)) as session:
        load_sample_data(session)
    engine.dispose()

    assert database_file.exists()
