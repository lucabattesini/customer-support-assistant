from pydantic import BaseModel

from app.services.store_hours_service import StoreHoursService
from app.tools.base import Payload, ToolContext, ToolSpec


class GetCurrentDatetimeInput(BaseModel):
    """`get_current_datetime` takes no arguments."""


def get_current_datetime(context: ToolContext, arguments: GetCurrentDatetimeInput) -> Payload:
    """Return the store-local date and time and the opening status."""
    status = StoreHoursService(context.store_config).status(context.clock.now())
    hours = status.today_hours
    return {
        "date": status.now.date().isoformat(),
        "time": status.now.strftime("%H:%M"),
        "weekday": status.weekday.value,
        "timezone": context.store_config.locale.timezone,
        "is_open": status.is_open,
        "today_hours": f"{hours.opens:%H:%M}-{hours.closes:%H:%M}" if hours else None,
        "next_opening": status.next_opening.isoformat() if status.next_opening else None,
    }


TOOL = ToolSpec(
    name="get_current_datetime", input_model=GetCurrentDatetimeInput, handler=get_current_datetime
)
