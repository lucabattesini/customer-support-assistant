import re
import unicodedata

NON_ALPHANUMERIC = re.compile(r"[^0-9a-z]+")


def normalize_text(value: str) -> str:
    """Lowercase, strip accents and collapse punctuation and whitespace into single spaces.

    Example: `"Violões  Eletro-Acústicos"` becomes `"violoes eletro acusticos"`.
    """
    decomposed = unicodedata.normalize("NFKD", value.casefold())
    without_accents = "".join(char for char in decomposed if not unicodedata.combining(char))
    return NON_ALPHANUMERIC.sub(" ", without_accents).strip()


def compact_text(value: str) -> str:
    """Normalized text without spaces, so `"GD-20"` and `"gd20"` compare equal."""
    return normalize_text(value).replace(" ", "")


def digits_only(value: str) -> str:
    """Keep only the digits of a value, e.g. a phone number."""
    return "".join(char for char in value if char.isdigit())
