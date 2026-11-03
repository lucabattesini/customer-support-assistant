from decimal import Decimal

import pytest

from app.core.money import apply_discount, format_money, to_money
from app.core.store_config import LocaleConfig

BRL = LocaleConfig(
    timezone="America/Campo_Grande",
    currency_symbol="R$",
    decimal_separator=",",
    thousands_separator=".",
)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (2199, Decimal("2199.00")),
        (0.1 + 0.2, Decimal("0.30")),
        ("349.905", Decimal("349.91")),
        (Decimal("58.315"), Decimal("58.32")),
    ],
)
def test_to_money_rounds_half_up_to_cents(value, expected):
    assert to_money(value) == expected


def test_apply_discount_has_no_float_error():
    assert apply_discount(Decimal("2199"), 5) == Decimal("2089.05")


def test_apply_discount_rounds_to_cents():
    assert apply_discount(Decimal("349.90"), 18) == Decimal("286.92")


@pytest.mark.parametrize(
    ("amount", "expected"),
    [
        (Decimal("2089.05"), "R$ 2.089,05"),
        (Decimal("159.9"), "R$ 159,90"),
        (Decimal("19567"), "R$ 19.567,00"),
        (Decimal("1234567.891"), "R$ 1.234.567,89"),
    ],
)
def test_format_money_uses_locale_separators(amount, expected):
    assert format_money(amount, BRL) == expected
