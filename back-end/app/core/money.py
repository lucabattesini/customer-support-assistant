from decimal import ROUND_HALF_UP, Decimal

from app.core.store_config import LocaleConfig

CENT = Decimal("0.01")
HUNDRED = Decimal(100)


def to_money(value: Decimal | int | float | str) -> Decimal:
    """Convert a value to a Decimal rounded to cents (half up).

    Args:
        value: Amount to convert. Floats are converted through their string form.

    Returns:
        The amount quantized to two decimal places.
    """
    return Decimal(str(value)).quantize(CENT, rounding=ROUND_HALF_UP)


def apply_discount(amount: Decimal, percent: Decimal | int) -> Decimal:
    """Return the amount after a percentage discount, rounded to cents."""
    return to_money(Decimal(amount) * (HUNDRED - Decimal(percent)) / HUNDRED)


def format_money(amount: Decimal, locale: LocaleConfig) -> str:
    """Format an amount with the store currency conventions, e.g. `R$ 2.089,05`."""
    integer_part, fraction_part = f"{to_money(amount):,.2f}".split(".")
    integer_part = integer_part.replace(",", locale.thousands_separator)
    return f"{locale.currency_symbol} {integer_part}{locale.decimal_separator}{fraction_part}"
