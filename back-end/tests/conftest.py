from datetime import datetime, time
from decimal import Decimal

import pytest

from app.core.clock import FixedClock
from app.core.store_config import (
    DayHours,
    HandoffConfig,
    InstallmentTier,
    LocaleConfig,
    PricingConfig,
    ReturnsConfig,
    StoreConfig,
    StoreInfo,
    Weekday,
)
from app.db.sample_data import load_sample_data
from app.db.session import build_engine, build_session_factory, init_db, session_scope

WEEKDAY_HOURS = DayHours(opens=time(9), closes=time(18))


def build_test_store_config() -> StoreConfig:
    return StoreConfig(
        store=StoreInfo(
            name="Sample Music Store",
            tagline="Sample tagline.",
            address="1 Sample Street",
            city="Sample City",
            phone="(00) 0000-0000",
            email="contact@example.com",
        ),
        locale=LocaleConfig(
            timezone="America/Campo_Grande",
            currency_symbol="R$",
            decimal_separator=",",
            thousands_separator=".",
        ),
        business_hours={
            Weekday.MONDAY: WEEKDAY_HOURS,
            Weekday.TUESDAY: WEEKDAY_HOURS,
            Weekday.WEDNESDAY: WEEKDAY_HOURS,
            Weekday.THURSDAY: WEEKDAY_HOURS,
            Weekday.FRIDAY: WEEKDAY_HOURS,
            Weekday.SATURDAY: DayHours(opens=time(9), closes=time(13)),
        },
        pricing=PricingConfig(
            pix_discount_percent=Decimal(5),
            installment_tiers=[
                InstallmentTier(max_installments=3, min_installment_value=Decimal(50)),
                InstallmentTier(max_installments=6, min_installment_value=Decimal(80)),
                InstallmentTier(max_installments=12, min_installment_value=Decimal(100)),
            ],
        ),
        returns=ReturnsConfig(
            regret_days=7, preference_days=7, defect_days=30, legal_warranty_days=90
        ),
        handoff=HandoffConfig(response_time_hours=24),
    )


@pytest.fixture
def store_config() -> StoreConfig:
    return build_test_store_config()


@pytest.fixture
def fixed_clock(store_config):
    return FixedClock(datetime(2026, 3, 25, 10, 0, tzinfo=store_config.locale.zone))


@pytest.fixture
def engine():
    engine = build_engine("sqlite://")
    init_db(engine)
    with session_scope(build_session_factory(engine)) as session:
        load_sample_data(session)
    yield engine
    engine.dispose()


@pytest.fixture
def session_factory(engine):
    return build_session_factory(engine)


@pytest.fixture
def session(session_factory):
    with session_scope(session_factory) as session:
        yield session
