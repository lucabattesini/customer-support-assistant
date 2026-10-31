import pytest

from app.core.text import compact_text, digits_only, normalize_text


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("Violões  Eletro-Acústicos", "violoes eletro acusticos"),
        ("  TAKAMINE GD20 ", "takamine gd20"),
        ("Ação/Ukulele!", "acao ukulele"),
        ("", ""),
    ],
)
def test_normalize_text(value, expected):
    assert normalize_text(value) == expected


def test_compact_text_ignores_separators():
    assert compact_text("GD-20") == compact_text("gd 20") == "gd20"


def test_digits_only():
    assert digits_only("+55 (67) 99812-3456") == "5567998123456"
