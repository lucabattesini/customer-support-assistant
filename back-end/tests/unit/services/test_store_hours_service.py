from datetime import UTC, datetime, time

import pytest

from app.core.store_config import Weekday
from app.services.store_hours_service import StoreHoursService


@pytest.fixture
def service(store_config):
    return StoreHoursService(store_config)


@pytest.fixture
def at(store_config):
    def build(year, month, day, hour, minute=0):
        return datetime(year, month, day, hour, minute, tzinfo=store_config.locale.zone)

    return build


def test_open_during_weekday_hours(service, at):
    status = service.status(at(2026, 3, 25, 10))

    assert status.is_open
    assert status.weekday is Weekday.WEDNESDAY
    assert status.next_opening is None


def test_closing_time_is_exclusive(service, at):
    assert not service.status(at(2026, 3, 25, 18)).is_open


def test_before_opening_next_opening_is_today(service, at):
    status = service.status(at(2026, 3, 25, 7, 30))

    assert not status.is_open
    assert status.next_opening == at(2026, 3, 25, 9)


def test_saturday_closes_earlier(service, at):
    status = service.status(at(2026, 3, 28, 13, 30))

    assert not status.is_open
    assert status.today_hours.closes == time(13)


def test_saturday_afternoon_next_opening_skips_sunday(service, at):
    assert service.status(at(2026, 3, 28, 14)).next_opening == at(2026, 3, 30, 9)


def test_sunday_is_closed(service, at):
    status = service.status(at(2026, 3, 29, 11))

    assert not status.is_open
    assert status.today_hours is None
    assert status.next_opening == at(2026, 3, 30, 9)


def test_friday_night_next_opening_is_saturday(service, at):
    assert service.status(at(2026, 3, 27, 20)).next_opening == at(2026, 3, 28, 9)


def test_moment_is_converted_to_store_timezone(service, at):
    status = service.status(datetime(2026, 3, 25, 13, 0, tzinfo=UTC))

    assert status.now == at(2026, 3, 25, 9)
    assert status.is_open
