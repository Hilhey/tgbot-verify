"""Military identity helper utilities."""

from one.name_generator import NameGenerator as BaseNameGenerator


class NameGenerator(BaseNameGenerator):
    """Reuse base English name generator."""


def generate_email(first_name: str, last_name: str, domain: str) -> str:
    """Generate a deterministic military email address."""
    local_part = f"{first_name}.{last_name}".lower()
    local_part = local_part.replace(" ", "").replace(".", "")
    return f"{local_part}@{domain}"


def generate_birth_date() -> str:
    """Return a fallback birth date when data is unavailable."""
    return "1970-01-01"


def generate_service_id(first_name: str, last_name: str, birth_date: str) -> str:
    """Generate a deterministic service ID."""
    initials = f"{first_name[:1]}{last_name[:1]}".upper()
    digits = "".join(char for char in birth_date if char.isdigit())[-6:]
    return f"{initials}-{digits or '000000'}"
