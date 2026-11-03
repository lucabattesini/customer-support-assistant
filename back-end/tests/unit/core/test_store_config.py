from datetime import time
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.core.settings import BASE_DIR
from app.core.store_config import DayHours, LocaleConfig, Weekday, load_store_config


@pytest.fixture
def config():
    return load_store_config(BASE_DIR / "config" / "store.toml")


def test_store_config_loads(config):
    assert config.store.name
    assert config.locale.zone.key == config.locale.timezone


def test_business_hours_parse_native_toml_times(config):
    monday = config.hours_for(Weekday.MONDAY)

    assert isinstance(monday.opens, time)
    assert monday.opens < monday.closes


def test_missing_weekday_means_closed(config):
    assert config.hours_for(Weekday.SUNDAY) is None


def test_installment_tiers_are_sorted(config):
    limits = [tier.max_installments for tier in config.pricing.installment_tiers]

    assert limits == sorted(limits)
    assert config.pricing.max_installments == limits[-1]


def test_pricing_values_are_decimal(config):
    assert isinstance(config.pricing.pix_discount_percent, Decimal)
    assert all(
        isinstance(tier.min_installment_value, Decimal) for tier in config.pricing.installment_tiers
    )


def test_weekday_from_index_matches_datetime_convention():
    assert Weekday.from_index(0) is Weekday.MONDAY
    assert Weekday.from_index(6) is Weekday.SUNDAY


def test_invalid_timezone_is_rejected():
    with pytest.raises(ValidationError):
        LocaleConfig(
            timezone="Mars/Olympus",
            currency_symbol="$",
            decimal_separator=".",
            thousands_separator=",",
        )


def test_day_hours_must_open_before_closing():
    with pytest.raises(ValidationError):
        DayHours(opens=time(18), closes=time(9))
