from datetime import date, datetime
from typing import Protocol
from zoneinfo import ZoneInfo


class Clock(Protocol):
    """Source of the current date and time."""

    def now(self) -> datetime:
        """Return the current timezone-aware datetime."""
        ...

    def today(self) -> date:
        """Return the current date."""
        ...


class SystemClock:
    """Clock backed by the system time, optionally pinned to a reference date.

    When a reference date is set, the date is replaced while the current time of day is kept,
    so the application behaves as if it were running on that date.
    """

    def __init__(self, timezone: ZoneInfo, reference_date: date | None = None) -> None:
        self._timezone = timezone
        self._reference_date = reference_date

    def now(self) -> datetime:
        """Return the current datetime in the configured timezone."""
        current = datetime.now(self._timezone)
        if self._reference_date is None:
            return current
        return datetime.combine(self._reference_date, current.timetz())

    def today(self) -> date:
        """Return the current date in the configured timezone."""
        return self.now().date()


class FixedClock:
    """Clock frozen at a given moment."""

    def __init__(self, moment: datetime) -> None:
        if moment.tzinfo is None:
            raise ValueError("FixedClock requires a timezone-aware datetime")
        self._moment = moment

    def now(self) -> datetime:
        """Return the frozen moment."""
        return self._moment

    def today(self) -> date:
        """Return the date of the frozen moment."""
        return self._moment.date()
