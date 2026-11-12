"""Input validation helpers."""


def validate_name(name):
    """A name is valid if it is not empty or only spaces."""
    return name.strip() != ""


def validate_marks(marks):
    """Marks must be between 0 and 100 (inclusive)."""
    return 0 <= marks <= 100
