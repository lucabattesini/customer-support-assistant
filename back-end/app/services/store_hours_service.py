from dataclasses import dataclass
from datetime import datetime, timedelta

from app.core.store_config import DayHours, StoreConfig, Weekday

DAYS_IN_WEEK = 7


@dataclass(frozen=True)
class StoreStatus:
    """Opening status of the store at a given moment."""

    now: datetime
    weekday: Weekday
    is_open: bool
    today_hours: DayHours | None
    next_opening: datetime | None


class StoreHoursService:
    """Answers whether the store is open and when it opens next."""

    def __init__(self, config: StoreConfig) -> None:
        self._config = config

    def status(self, moment: datetime) -> StoreStatus:
        """Return the store status at a moment, converted to the store timezone."""
        now = moment.astimezone(self._config.locale.zone)
        weekday = Weekday.from_index(now.weekday())
        hours = self._config.hours_for(weekday)
        is_open = hours is not None and hours.opens <= now.time() < hours.closes
        return StoreStatus(
            now=now,
            weekday=weekday,
            is_open=is_open,
            today_hours=hours,
            next_opening=None if is_open else self._next_opening(now),
        )

    def _next_opening(self, now: datetime) -> datetime | None:
        for offset in range(DAYS_IN_WEEK + 1):
            day = now.date() + timedelta(days=offset)
            hours = self._config.hours_for(Weekday.from_index(day.weekday()))
            if hours is None:
                continue
            opening = datetime.combine(day, hours.opens, tzinfo=now.tzinfo)
            if opening > now:
                return opening
        return None
