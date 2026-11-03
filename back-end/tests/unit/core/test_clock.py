from datetime import date, datetime
from zoneinfo import ZoneInfo

import pytest

from app.core.clock import FixedClock, SystemClock

ZONE = ZoneInfo("America/Campo_Grande")


def test_system_clock_is_timezone_aware():
    now = SystemClock(ZONE).now()

    assert now.tzinfo is not None
    assert now.utcoffset() == datetime.now(ZONE).utcoffset()


def test_system_clock_uses_reference_date():
    clock = SystemClock(ZONE, reference_date=date(2026, 3, 25))

    assert clock.today() == date(2026, 3, 25)
    assert clock.now().date() == date(2026, 3, 25)
    assert clock.now().tzinfo is not None


def test_fixed_clock_returns_frozen_moment():
    moment = datetime(2026, 3, 25, 10, 30, tzinfo=ZONE)
    clock = FixedClock(moment)

    assert clock.now() == moment
    assert clock.today() == date(2026, 3, 25)


def test_fixed_clock_rejects_naive_datetime():
    with pytest.raises(ValueError):
        FixedClock(datetime(2026, 3, 25, 10, 30))
