import tomllib
from datetime import time
from decimal import Decimal
from enum import StrEnum
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, Field, field_validator, model_validator


class Weekday(StrEnum):
    """Days of the week, ordered as in `datetime.weekday()`."""

    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"

    @classmethod
    def from_index(cls, index: int) -> Weekday:
        """Return the weekday matching a `datetime.weekday()` index."""
        return list(cls)[index]


class StoreInfo(BaseModel):
    """Public identity and contact data of the store."""

    name: str
    tagline: str
    address: str
    city: str
    phone: str
    email: str


class LocaleConfig(BaseModel):
    """Timezone and currency formatting used by the store."""

    timezone: str
    currency_symbol: str
    decimal_separator: str
    thousands_separator: str

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, value: str) -> str:
        """Ensure the timezone exists in the tz database."""
        try:
            ZoneInfo(value)
        except ZoneInfoNotFoundError as error:
            raise ValueError(f"Unknown timezone: {value}") from error
        return value

    @property
    def zone(self) -> ZoneInfo:
        """Timezone object for the configured timezone name."""
        return ZoneInfo(self.timezone)


class DayHours(BaseModel):
    """Opening and closing time of a single day."""

    opens: time
    closes: time

    @model_validator(mode="after")
    def validate_range(self) -> DayHours:
        """Ensure the store opens before it closes."""
        if self.opens >= self.closes:
            raise ValueError("Opening time must be earlier than closing time")
        return self


class InstallmentTier(BaseModel):
    """Upper bound of installments allowed for a minimum installment value."""

    max_installments: int = Field(ge=1)
    min_installment_value: Decimal = Field(ge=0)


class PricingConfig(BaseModel):
    """Discount and installment rules."""

    pix_discount_percent: Decimal = Field(ge=0, le=100)
    installment_tiers: list[InstallmentTier] = Field(min_length=1)

    @field_validator("installment_tiers")
    @classmethod
    def sort_tiers(cls, tiers: list[InstallmentTier]) -> list[InstallmentTier]:
        """Keep tiers ordered by their installment limit."""
        return sorted(tiers, key=lambda tier: tier.max_installments)

    @property
    def max_installments(self) -> int:
        """Highest number of installments allowed by any tier."""
        return self.installment_tiers[-1].max_installments


class ReturnsConfig(BaseModel):
    """Deadlines, in calendar days, for returns, exchanges and warranty."""

    regret_days: int = Field(ge=0)
    preference_days: int = Field(ge=0)
    defect_days: int = Field(ge=0)
    legal_warranty_days: int = Field(ge=0)


class CatalogConfig(BaseModel):
    """Catalog behavior settings."""

    similarity_specs: list[str] = Field(default_factory=list)
    """Product spec keys that define a similar product, in priority order."""


class HandoffConfig(BaseModel):
    """Human handoff settings."""

    response_time_hours: int = Field(ge=1)


class StoreConfig(BaseModel):
    """Store-specific configuration loaded from `store.toml`."""

    store: StoreInfo
    locale: LocaleConfig
    business_hours: dict[Weekday, DayHours]
    pricing: PricingConfig
    returns: ReturnsConfig
    handoff: HandoffConfig
    catalog: CatalogConfig = Field(default_factory=CatalogConfig)

    def hours_for(self, weekday: Weekday) -> DayHours | None:
        """Return the opening hours of a weekday, or None when the store is closed."""
        return self.business_hours.get(weekday)


def load_store_config(path: Path) -> StoreConfig:
    """Load and validate the store configuration from a TOML file.

    Args:
        path: Location of the TOML file.

    Returns:
        The validated store configuration.
    """
    with path.open("rb") as file:
        return StoreConfig.model_validate(tomllib.load(file))
